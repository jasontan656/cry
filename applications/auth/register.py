# 用户注册主逻辑实现
# 整合验证码验证和密码设置的完整注册流程

import asyncio
from .schemas import (
    SendVerificationRequest, SendVerificationResponse,
    VerifyCodeRequest, VerifyCodeResponse,
    SetPasswordRequest, SetPasswordResponse,
    UserRegisterRequest, UserResponse
)
from .validators import validate_email, validate_password
from .hashing import hash_password
from .repository import create_user, get_user_by_id, check_user_exists, check_user_is_oauth_only, set_user_password_by_email
from .exceptions import UserAlreadyExistsError, InvalidInputError, EmailAlreadyRegisteredError
from .email_verification import send_verification_code, verify_code


async def send_verification_code_to_email(request: SendVerificationRequest) -> SendVerificationResponse:
    """
    向指定邮箱发送验证码

    生成6位数字验证码并发送到用户邮箱，用于邮箱验证流程。
    支持测试模式，当test_user为True时生成固定验证码123456。
    严格检查邮箱注册状态，禁止已完整注册用户重复注册。

    参数:
        request: SendVerificationRequest 对象，包含需要验证的邮箱和test_user标识

    返回:
        SendVerificationResponse: 发送结果响应对象

    异常:
        InvalidInputError: 邮箱格式不正确
        EmailAlreadyRegisteredError: 邮箱已完整注册，禁止重复注册
    """
    # 从请求对象中提取邮箱地址和测试用户标识
    email = request.email
    test_user = request.test_user

    # 调用 validate_email 函数验证邮箱格式
    # 如果格式不正确，会抛出 InvalidInputError 异常
    validate_email(email)

    # 检查邮箱是否已存在，实施严格的重复注册控制
    # 调用 check_user_exists 函数检查用户是否已存在
    user_exists = check_user_exists(email)
    
    if user_exists:
        # 调用 check_user_is_oauth_only 函数检查是否为OAuth用户
        # 传入邮箱地址，得到OAuth用户状态布尔值
        is_oauth_only = check_user_is_oauth_only(email)
        
        # 如果用户已存在且不是OAuth用户，则为已完整注册用户
        # 根据用户要求，严格禁止重复注册
        if not is_oauth_only:
            # 抛出 EmailAlreadyRegisteredError 异常
            # 提示用户邮箱已注册，应使用登录或忘记密码功能
            raise EmailAlreadyRegisteredError("邮箱已注册，请直接登录或使用忘记密码")

    # 异步调用 send_verification_code 函数发送验证码
    # 传入邮箱地址 email 和测试用户标识 test_user
    # 当 test_user 为 True 时生成固定验证码123456
    # 得到发送结果布尔值，赋值给 send_result
    send_result = await send_verification_code(email, is_test_user=test_user)

    # 根据发送结果创建响应对象
    if send_result:
        if test_user:
            return SendVerificationResponse(
                success=True,
                message="测试验证码已发送到您的邮箱，固定验证码：123456"
            )
        else:
            return SendVerificationResponse(
                success=True,
                message="验证码已发送到您的邮箱，请查收"
            )
    else:
        return SendVerificationResponse(
            success=False,
            message="验证码发送失败，请稍后重试"
        )


def verify_email_code(request: VerifyCodeRequest) -> VerifyCodeResponse:
    """
    验证邮箱验证码

    检查用户输入的验证码是否正确，并返回用户的状态信息。

    参数:
        request: VerifyCodeRequest 对象，包含邮箱和验证码

    返回:
        VerifyCodeResponse: 验证结果响应对象，包含用户状态信息

    异常:
        InvalidInputError: 邮箱格式不正确
    """
    # 从请求对象中提取邮箱和验证码
    email = request.email
    code = request.code

    # 调用 validate_email 函数验证邮箱格式
    # 如果格式不正确，会抛出 InvalidInputError 异常
    validate_email(email)

    # 调用 verify_code 函数验证验证码
    # 传入邮箱 email 和验证码 code，得到验证结果布尔值
    # 结果赋值给 verification_result
    verification_result = verify_code(email, code)

    # 如果验证码验证失败，返回失败响应
    if not verification_result:
        return VerifyCodeResponse(
            success=False,
            message="验证码错误或已过期",
            user_exists=False,
            is_oauth_user=False
        )

    # 验证码验证成功，检查用户是否存在
    user_exists = check_user_exists(email)

    # 如果用户不存在，返回新用户状态
    if not user_exists:
        return VerifyCodeResponse(
            success=True,
            message="邮箱验证成功，您可以设置密码完成注册",
            user_exists=False,
            is_oauth_user=False
        )

    # 用户已存在，检查是否为纯OAuth用户
    is_oauth_only = check_user_is_oauth_only(email)

    if is_oauth_only:
        return VerifyCodeResponse(
            success=True,
            message="您已通过第三方登录注册，请设置密码以启用邮箱密码登录",
            user_exists=True,
            is_oauth_user=True
        )
    else:
        return VerifyCodeResponse(
            success=True,
            message="邮箱验证成功，您的账户已完整注册",
            user_exists=True,
            is_oauth_user=False
        )


def set_user_password_after_verification(request: SetPasswordRequest) -> SetPasswordResponse:
    """
    为已验证邮箱设置密码

    用于新用户完成注册，或OAuth用户设置密码以启用邮箱密码登录。

    参数:
        request: SetPasswordRequest 对象，包含邮箱和密码

    返回:
        SetPasswordResponse: 密码设置结果响应对象

    异常:
        InvalidInputError: 邮箱或密码格式不正确
        ValueError: 邮箱不存在
    """
    # 从请求对象中提取邮箱和密码
    email = request.email
    password = request.password

    # 调用 validate_email 和 validate_password 函数验证输入
    # 如果格式不正确，会抛出 InvalidInputError 异常
    validate_email(email)
    validate_password(password)

    # 调用 hash_password 函数对密码进行加密处理
    # 传入原始密码字符串，得到加密后的密码哈希
    # 结果赋值给 hashed_password 变量
    hashed_password = hash_password(password)

    # 检查用户是否存在
    user_exists = check_user_exists(email)

    # 如果用户不存在，先创建新用户
    if not user_exists:
        # 使用邮箱作为用户名
        username = email

        # 调用 create_user 函数创建新用户记录
        # 传入用户名 username、邮箱 email 和加密后的密码 hashed_password
        # 得到新创建用户的user_id，赋值给 user_id
        user_id = create_user(username, email, hashed_password)

        return SetPasswordResponse(
            success=True,
            message="注册成功！您可以使用邮箱和密码登录",
            user_id=user_id
        )

    # 用户已存在，检查是否为OAuth用户
    is_oauth_only = check_user_is_oauth_only(email)

    if is_oauth_only:
        # 为OAuth用户设置密码，启用邮箱密码登录
        user_id = set_user_password_by_email(email, hashed_password)

        return SetPasswordResponse(
            success=True,
            message="密码设置成功！现在您可以使用邮箱密码登录",
            user_id=user_id
        )
    else:
        # 用户已设置密码，更新密码
        user_id = set_user_password_by_email(email, hashed_password)

        return SetPasswordResponse(
            success=True,
            message="密码更新成功",
            user_id=user_id
        )


def register_user(request: UserRegisterRequest) -> UserResponse:
    """
    用户注册流程（支持测试模式）

    根据test_user字段决定是否跳过验证码验证。
    支持开发调试时快速验证注册主流程逻辑。
    严格禁止已完整注册用户重复注册，允许OAuth用户补设密码。

    参数:
        request: UserRegisterRequest 对象，包含邮箱、密码、test_user标识

    返回:
        UserResponse: 注册成功后的用户信息对象

    异常:
        InvalidInputError: 输入数据格式不正确
        EmailAlreadyRegisteredError: 邮箱已完整注册，禁止重复注册
    """
    # 从请求对象中提取邮箱、密码和测试用户标识
    email = request.email
    password = request.password
    test_user = request.test_user

    # 使用邮箱作为用户名
    username = email

    # 调用 validate_registration_data 函数验证输入数据的完整性
    # 传入邮箱和密码进行格式校验
    # 如果校验失败，会抛出 InvalidInputError 异常
    from .validators import validate_registration_data
    validate_registration_data(email, password)

    # 严格的邮箱重复检查逻辑，在注册逻辑最前面执行
    # 调用 check_user_exists 函数检查邮箱是否已存在
    user_exists = check_user_exists(email)
    
    if user_exists:
        # 调用 check_user_is_oauth_only 函数检查用户类型
        # 传入邮箱地址，得到是否为OAuth用户的布尔值
        is_oauth_only = check_user_is_oauth_only(email)
        
        # 如果用户已存在且不是OAuth用户，则为已完整注册用户
        # 严格禁止重复注册，抛出异常
        if not is_oauth_only:
            # 抛出 EmailAlreadyRegisteredError 异常
            # 提示用户邮箱已注册，应使用登录或忘记密码功能
            raise EmailAlreadyRegisteredError("邮箱已注册，请直接登录或使用忘记密码")

    # 检查是否为测试用户，决定是否跳过验证码验证流程
    # test_user 字段为True时跳过验证码验证，仅用于开发调试
    # test_user 字段为False时执行完整的验证码验证流程
    if test_user is True:
        # 测试模式：跳过验证码验证，直接进入密码设置流程
        # 不调用 email_verification 模块的任何验证函数
        # 不发送验证码邮件，视为验证码验证通过
        # 该逻辑仅用于开发调试，生产环境不应使用

        # 调用 hash_password 函数对密码进行加密处理
        # 传入原始密码字符串，得到加密后的密码哈希
        # 结果赋值给 hashed_password 变量
        hashed_password = hash_password(password)

        # 检查用户是否已存在
        user_exists = check_user_exists(email)

        # 如果用户不存在，创建新用户
        if not user_exists:
            # 调用 create_user 函数在数据库中创建用户记录
            # 传入用户名（邮箱）、邮箱和加密后的密码
            # 得到新创建用户的user_id，赋值给 user_id
            user_id = create_user(username, email, hashed_password)
        else:
            # 用户已存在，检查是否为OAuth用户
            is_oauth_only = check_user_is_oauth_only(email)

            if is_oauth_only:
                # 为OAuth用户设置密码，启用邮箱密码登录
                user_id = set_user_password_by_email(email, hashed_password)
            else:
                # 用户已设置密码，抛出邮箱已存在异常
                raise UserAlreadyExistsError("邮箱已存在")

        # 调用 get_user_by_id 函数获取用户信息
        # 传入 user_id，得到用户信息字典
        # 结果赋值给 user_data 变量
        user_data = get_user_by_id(user_id)

        # 为新注册用户生成访问令牌和刷新令牌
        from .tokens import generate_token_pair

        # 创建令牌对（包含访问令牌和刷新令牌）
        token_pair = generate_token_pair(user_data["user_id"], user_data["email"])

        # 提取访问令牌和刷新令牌
        access_token = token_pair["access_token"]
        refresh_token = token_pair["refresh_token"]

        # 创建 UserResponse 对象，使用获取到的用户信息和生成的令牌
        # 传入 user_id、email、access_token、refresh_token 创建响应对象
        # 返回给调用方表示注册成功
        return UserResponse(
            user_id=user_data["user_id"],
            email=user_data["email"],
            access_token=access_token,
            refresh_token=refresh_token
        )

    else:
        # 正常模式：执行完整的验证码验证流程
        # 该模式需要用户先发送验证码、验证验证码，再设置密码
        # 这里抛出异常提示需要先进行验证码验证
        raise InvalidInputError("请先通过验证码验证流程完成注册")
