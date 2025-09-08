# 忘记密码重置功能模块
# 独立实现密码重置的完整流程，包括验证码发送、验证、密码更新

import time
from typing import Dict, Tuple
from utilities.mail import send_email
from .validators import validate_email, validate_password
from .repository import check_user_exists, set_user_password_by_email
from .hashing import hash_password
from .exceptions import InvalidInputError
from .email_verification import generate_verification_code

# 密码重置验证码缓存存储
# 使用内存字典模拟缓存，键为邮箱，值为 (验证码, 时间戳) 元组
# 与注册验证码分离，避免混淆
_reset_codes: Dict[str, Tuple[str, float]] = {}

# 密码重置验证码有效期（秒）
RESET_CODE_EXPIRY = 600  # 10分钟，比注册验证码稍长


async def send_reset_code(email: str, is_test_user: bool = False) -> bool:
    """
    发送密码重置验证码

    生成6位数字验证码，组织重置密码邮件内容，
    通过异步调用send_email发送邮件。
    将验证码和时间戳存储到密码重置缓存中。
    支持测试模式，当is_test_user为True时生成固定验证码123456。

    参数:
        email: 需要重置密码的邮箱地址字符串
        is_test_user: 测试用户标识，为True时生成固定验证码，默认False

    返回:
        bool: 发送成功返回True，否则返回False
    """
    # 调用 validate_email 函数验证邮箱格式
    # 如果格式不正确，会抛出 InvalidInputError 异常
    validate_email(email)
    
    # 调用 check_user_exists 函数检查用户是否存在
    # 传入邮箱地址，得到用户存在性布尔值
    # 如果用户不存在，返回False
    if not check_user_exists(email):
        return False
    
    # 根据是否为测试用户决定验证码生成方式
    # is_test_user为True时使用固定验证码，仅用于开发调试
    # is_test_user为False时生成随机6位数字验证码
    if is_test_user is True:
        # 测试模式：使用固定验证码123456
        # 该逻辑仅用于开发调试，生产环境不应使用
        code = "123456"
    else:
        # 正常模式：调用 generate_verification_code() 生成6位数字验证码
        # 结果赋值给 code 变量，用于发送和缓存
        code = generate_verification_code()

    # 通过 time.time() 获取当前时间戳，用于验证码过期判断
    current_time = time.time()

    # 将验证码和时间戳存储到密码重置缓存字典中
    # 键为邮箱，值为(验证码, 时间戳)元组
    _reset_codes[email] = (code, current_time)

    # 组织密码重置邮件的主题和正文内容
    subject = "密码重置验证码 - 重置您的账户密码"
    # 测试模式下在邮件正文中提示这是测试验证码
    if is_test_user:
        body = f"您的密码重置验证码是：{code}\n\n这是测试重置验证码，验证码有效期为10分钟，请及时使用。\n注意：这是开发测试模式。\n如果您没有申请重置密码，请忽略此邮件。"
    else:
        body = f"您的密码重置验证码是：{code}\n\n验证码有效期为10分钟，请及时使用。\n如果您没有申请重置密码，请忽略此邮件。"

    try:
        # 在测试模式下跳过邮件发送，直接返回成功
        if is_test_user:
            return True

        # 异步调用 utilities.mail 模块的 send_email 函数
        # 传入邮箱地址、主题、正文内容，发送密码重置邮件
        # 返回发送结果布尔值
        return await send_email(
            to=email,
            subject=subject,
            body=body,
            content_type="plain"
        )
    except Exception:
        # 发送失败时从缓存中移除验证码
        if email in _reset_codes:
            del _reset_codes[email]
        return False


def verify_reset_code(email: str, code: str) -> bool:
    """
    验证密码重置验证码

    从密码重置缓存中获取存储的验证码，检查验证码是否正确且未过期。
    验证成功后保留验证码，供后续重置密码步骤使用。

    参数:
        email: 邮箱地址字符串
        code: 用户输入的验证码字符串

    返回:
        bool: 验证成功返回True，否则返回False
    """
    # 检查邮箱是否在密码重置验证码缓存中
    if email not in _reset_codes:
        return False

    # 从缓存中获取存储的验证码和时间戳
    stored_code, timestamp = _reset_codes[email]

    # 检查验证码是否过期（超过10分钟）
    current_time = time.time()
    if current_time - timestamp > RESET_CODE_EXPIRY:
        # 验证码过期，从缓存中移除
        del _reset_codes[email]
        return False

    # 检查用户输入的验证码是否与存储的验证码匹配
    if code != stored_code:
        return False

    # 验证成功，但不删除验证码
    # 保留验证码供后续重置密码步骤使用
    return True


def reset_password(email: str, code: str, new_password: str) -> bool:
    """
    重置用户密码

    一次性验证重置验证码并更新用户密码。
    验证成功后从缓存中清除验证码，完成密码重置流程。

    参数:
        email: 邮箱地址字符串
        code: 验证码字符串
        new_password: 新密码字符串

    返回:
        bool: 重置成功返回True，否则返回False

    异常:
        InvalidInputError: 邮箱格式或密码格式不正确
    """
    # 调用 validate_email 函数验证邮箱格式
    # 如果格式不正确，会抛出 InvalidInputError 异常
    validate_email(email)
    
    # 调用 validate_password 函数验证新密码格式
    # 如果格式不正确，会抛出 InvalidInputError 异常
    validate_password(new_password)

    # 验证重置验证码是否正确
    # 检查邮箱是否在密码重置验证码缓存中
    if email not in _reset_codes:
        return False

    # 从缓存中获取存储的验证码和时间戳
    stored_code, timestamp = _reset_codes[email]

    # 检查验证码是否过期（超过10分钟）
    current_time = time.time()
    if current_time - timestamp > RESET_CODE_EXPIRY:
        # 验证码过期，从缓存中移除
        del _reset_codes[email]
        return False

    # 检查用户输入的验证码是否与存储的验证码匹配
    if code != stored_code:
        return False

    # 验证码验证成功，开始更新密码
    # 调用 hash_password 函数对新密码进行加密处理
    # 传入原始新密码字符串，得到加密后的密码哈希
    # 结果赋值给 hashed_new_password 变量
    hashed_new_password = hash_password(new_password)

    try:
        # 调用 set_user_password_by_email 函数更新用户密码
        # 传入邮箱地址和加密后的新密码
        # 得到用户ID或None，用于确认操作成功
        user_id = set_user_password_by_email(email, hashed_new_password)

        # 检查密码更新是否成功
        if user_id:
            # 密码重置成功，从缓存中移除验证码
            del _reset_codes[email]
            return True
        else:
            return False

    except Exception:
        return False


def cleanup_expired_reset_codes() -> None:
    """
    清理过期的密码重置验证码

    遍历密码重置验证码缓存，移除所有已过期的验证码条目。
    用于定期清理内存中的过期数据。
    """
    # 获取当前时间戳
    current_time = time.time()

    # 创建需要删除的邮箱列表
    expired_emails = []

    # 遍历密码重置验证码缓存字典
    for email, (code, timestamp) in _reset_codes.items():
        # 检查验证码是否过期
        if current_time - timestamp > RESET_CODE_EXPIRY:
            expired_emails.append(email)

    # 从缓存中移除所有过期的验证码
    for email in expired_emails:
        del _reset_codes[email]
