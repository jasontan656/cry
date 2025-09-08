# 用户认证模块主入口文件
# 提供完整的认证功能统一入口点（注册、登录、OAuth）

from .register import (
    register_user,
    send_verification_code_to_email,
    verify_email_code,
    set_user_password_after_verification
)
from .login import login_user
from .oauth_google import get_google_auth_url, login_with_google
from .oauth_facebook import get_facebook_auth_url, login_with_facebook
from .schemas import (
    UserRegisterRequest, UserResponse,
    SendVerificationRequest, SendVerificationResponse,
    VerifyCodeRequest, VerifyCodeResponse,
    SetPasswordRequest, SetPasswordResponse
)
from .exceptions import UserAlreadyExistsError, InvalidInputError, InvalidCredentialsError

# 导出主要功能供外部使用
__all__ = [
    # 注册相关
    "register_user",
    "send_verification_code_to_email",
    "verify_email_code",
    "set_user_password_after_verification",

    # 登录相关
    "login_user",

    # OAuth相关
    "get_google_auth_url",
    "login_with_google",
    "get_facebook_auth_url",
    "login_with_facebook",

    # 数据模型
    "UserRegisterRequest",
    "UserResponse",
    "SendVerificationRequest",
    "SendVerificationResponse",
    "VerifyCodeRequest",
    "VerifyCodeResponse",
    "SetPasswordRequest",
    "SetPasswordResponse",

    # 异常类
    "UserAlreadyExistsError",
    "InvalidInputError",
    "InvalidCredentialsError"
]
