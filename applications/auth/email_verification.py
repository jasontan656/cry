# 邮箱验证码管理模块
# 负责验证码生成、发送、缓存、验证的完整流程

import asyncio
import random
import time
from typing import Dict, Tuple
from utilities.mail import send_email


# 验证码缓存存储
# 使用内存字典模拟缓存，键为邮箱，值为 (验证码, 时间戳) 元组
_verification_codes: Dict[str, Tuple[str, float]] = {}

# 验证码有效期（秒）
VERIFICATION_CODE_EXPIRY = 300  # 5分钟


def generate_verification_code() -> str:
    """
    生成6位数字验证码

    使用random模块生成6位随机数字字符串。
    返回生成的验证码字符串，用于发送给用户。

    返回:
        str: 6位数字验证码字符串
    """
    # 使用random.randint()生成6位数字
    # 通过循环生成每一位数字，最后拼接成字符串
    code = ''.join(str(random.randint(0, 9)) for _ in range(6))
    return code


async def send_verification_code(email: str, is_test_user: bool = False) -> bool:
    """
    向指定邮箱发送验证码

    生成6位数字验证码，组织邮件内容，通过异步调用send_email发送邮件。
    同时将验证码和时间戳存储到内存缓存中。
    支持测试模式，当is_test_user为True时生成固定验证码123456。

    参数:
        email: 接收验证码的邮箱地址字符串
        is_test_user: 测试用户标识，为True时生成固定验证码，默认False

    返回:
        bool: 发送成功返回True，否则返回False
    """
    # 根据是否为测试用户决定验证码生成方式
    # is_test_user为True时使用固定验证码，仅用于开发调试
    # is_test_user为False时生成随机6位数字验证码
    if is_test_user is True:
        # 测试模式：使用固定验证码123456
        # 该逻辑仅用于开发调试，生产环境不应使用
        code = "123456"
    else:
        # 正常模式：调用generate_verification_code()生成6位数字验证码
        # 结果赋值给code变量，用于发送和缓存
        code = generate_verification_code()

    # 获取当前时间戳，用于验证码过期判断
    current_time = time.time()

    # 将验证码和时间戳存储到全局缓存字典中
    # 键为邮箱，值为(验证码, 时间戳)元组
    _verification_codes[email] = (code, current_time)

    # 组织邮件主题和正文内容
    subject = "邮箱验证码 - 验证您的身份"
    # 测试模式下在邮件正文中提示这是测试验证码
    if is_test_user:
        body = f"您的验证码是：{code}\n\n这是测试验证码，验证码有效期为5分钟，请及时使用。\n注意：这是开发测试模式。"
    else:
        body = f"您的验证码是：{code}\n\n验证码有效期为5分钟，请及时使用。"

    try:
        # 异步调用utilities.mail模块的send_email函数
        # 传入邮箱地址、主题、正文内容，发送验证码邮件
        # 返回发送结果布尔值
        return await send_email(
            to=email,
            subject=subject,
            body=body,
            content_type="plain"
        )
    except Exception:
        # 发送失败时从缓存中移除验证码
        if email in _verification_codes:
            del _verification_codes[email]
        return False


def verify_code(email: str, code: str) -> bool:
    """
    验证邮箱验证码

    从内存缓存中获取存储的验证码，检查验证码是否正确且未过期。
    验证成功后立即从缓存中清除验证码。

    参数:
        email: 邮箱地址字符串
        code: 用户输入的验证码字符串

    返回:
        bool: 验证成功返回True，否则返回False
    """
    # 检查邮箱是否在验证码缓存中
    if email not in _verification_codes:
        return False

    # 从缓存中获取存储的验证码和时间戳
    stored_code, timestamp = _verification_codes[email]

    # 检查验证码是否过期（超过5分钟）
    current_time = time.time()
    if current_time - timestamp > VERIFICATION_CODE_EXPIRY:
        # 验证码过期，从缓存中移除
        del _verification_codes[email]
        return False

    # 检查用户输入的验证码是否与存储的验证码匹配
    if code != stored_code:
        return False

    # 验证成功，从缓存中移除验证码
    del _verification_codes[email]
    return True


def cleanup_expired_codes() -> None:
    """
    清理过期的验证码

    遍历验证码缓存，移除所有已过期的验证码条目。
    用于定期清理内存中的过期数据。
    """
    # 获取当前时间戳
    current_time = time.time()

    # 创建需要删除的邮箱列表
    expired_emails = []

    # 遍历验证码缓存字典
    for email, (code, timestamp) in _verification_codes.items():
        # 检查验证码是否过期
        if current_time - timestamp > VERIFICATION_CODE_EXPIRY:
            expired_emails.append(email)

    # 从缓存中移除所有过期的验证码
    for email in expired_emails:
        del _verification_codes[email]
