# 用户认证模块路由文件
# 定义用户认证相关的路由处理逻辑（注册、登录、OAuth）

from .register import (
    register_user,
    send_verification_code_to_email,
    verify_email_code,
    set_user_password_after_verification
)
from .login import login_user
from .oauth_google import get_google_auth_url, login_with_google
from .oauth_facebook import get_facebook_auth_url, login_with_facebook
from .reset_password import send_reset_code, verify_reset_code, reset_password
from .schemas import UserRegisterRequest, ForgotPasswordRequest, VerifyResetCodeRequest, ResetPasswordRequest
from .exceptions import UserAlreadyExistsError, InvalidInputError, InvalidCredentialsError, EmailAlreadyRegisteredError


def handle_register_request(request_data: dict) -> dict:
    """
    处理用户注册请求

    将HTTP请求数据转换为UserRegisterRequest对象，
    调用注册逻辑，并处理可能的异常情况。
    返回包含注册结果或错误信息的字典。

    参数:
        request_data: HTTP请求的数据字典，包含username、email、password

    返回:
        dict: 响应字典，包含success状态、data或error信息
    """
    try:
        # 将请求数据转换为UserRegisterRequest对象
        register_request = UserRegisterRequest(**request_data)

        # 调用注册函数执行用户注册
        result = register_user(register_request)

        # 返回成功响应
        return {
            "success": True,
            "data": result.model_dump()
        }

    except InvalidInputError as e:
        # 处理输入数据无效的异常
        return {
            "success": False,
            "error": str(e),
            "error_type": "INVALID_INPUT"
        }

    except UserAlreadyExistsError as e:
        # 处理用户已存在的异常
        return {
            "success": False,
            "error": str(e),
            "error_type": "USER_EXISTS"
        }

    except EmailAlreadyRegisteredError as e:
        # 处理邮箱已完整注册的异常
        return {
            "success": False,
            "error": str(e),
            "error_type": "EMAIL_ALREADY_REGISTERED"
        }

    except Exception as e:
        # 处理其他未预期的异常
        return {
            "success": False,
            "error": "注册过程中发生未知错误",
            "error_type": "UNKNOWN_ERROR"
        }


def handle_login_request(request_data: dict) -> dict:
    """
    处理用户登录请求

    将HTTP请求数据转换为登录参数，
    调用登录逻辑，并处理可能的异常情况。
    返回包含登录结果或错误信息的字典。

    参数:
        request_data: HTTP请求的数据字典，包含email、password

    返回:
        dict: 响应字典，包含success状态、data或error信息
    """
    try:
        # 从请求数据中提取邮箱和密码
        email = request_data.get("email")
        password = request_data.get("password")

        # 验证必要参数是否存在
        if not email or not password:
            return {
                "success": False,
                "error": "邮箱和密码都是必需的",
                "error_type": "MISSING_PARAMETERS"
            }

        # 调用登录函数执行用户登录
        result = login_user(email, password)

        # 返回成功响应
        return {
            "success": True,
            "data": result.model_dump(),
            "message": "登录成功"
        }

    except InvalidCredentialsError as e:
        # 处理登录凭证无效的异常
        return {
            "success": False,
            "error": str(e),
            "error_type": "INVALID_CREDENTIALS"
        }

    except Exception as e:
        # 处理其他未预期的异常
        return {
            "success": False,
            "error": "登录过程中发生未知错误",
            "error_type": "UNKNOWN_ERROR"
        }


def handle_google_auth(request_data: dict) -> dict:
    """
    处理Google OAuth授权请求

    生成Google OAuth授权URL，用于引导用户进行Google登录授权。

    参数:
        request_data: HTTP请求的数据字典，可选包含state参数

    返回:
        dict: 响应字典，包含success状态和授权URL
    """
    try:
        # 从请求数据中提取state参数
        state = request_data.get("state")

        # 调用Google OAuth函数生成授权URL
        auth_url = get_google_auth_url(state)

        # 返回成功响应，包含授权URL
        return {
            "success": True,
            "data": {
                "auth_url": auth_url,
                "provider": "google"
            },
            "message": "Google授权URL生成成功"
        }

    except Exception as e:
        # 处理生成授权URL过程中的异常
        return {
            "success": False,
            "error": "生成Google授权URL失败",
            "error_type": "OAUTH_URL_GENERATION_ERROR"
        }


def handle_google_callback(request_data: dict) -> dict:
    """
    处理Google OAuth回调请求

    处理Google OAuth授权后的回调，完成用户登录。

    参数:
        request_data: HTTP请求的数据字典，包含code、state等回调参数

    返回:
        dict: 响应字典，包含success状态和用户信息
    """
    try:
        # 从请求数据中提取回调参数
        code = request_data.get("code")
        state = request_data.get("state")
        expected_state = request_data.get("expected_state")

        # 验证必要参数是否存在
        if not code:
            return {
                "success": False,
                "error": "缺少授权码参数",
                "error_type": "MISSING_CODE"
            }

        # 调用Google OAuth回调函数完成登录
        result = login_with_google(code, state, expected_state)

        # 返回成功响应
        return {
            "success": True,
            "data": result.model_dump(),
            "message": "Google登录成功"
        }

    except ValueError as e:
        # 处理OAuth流程中的验证错误
        return {
            "success": False,
            "error": str(e),
            "error_type": "OAUTH_VALIDATION_ERROR"
        }

    except Exception as e:
        # 处理其他未预期的异常
        return {
            "success": False,
            "error": "Google OAuth回调处理失败",
            "error_type": "OAUTH_CALLBACK_ERROR"
        }


def handle_facebook_auth(request_data: dict) -> dict:
    """
    处理Facebook OAuth授权请求

    生成Facebook OAuth授权URL，用于引导用户进行Facebook登录授权。

    参数:
        request_data: HTTP请求的数据字典，可选包含state参数

    返回:
        dict: 响应字典，包含success状态和授权URL
    """
    try:
        # 从请求数据中提取state参数
        state = request_data.get("state")

        # 调用Facebook OAuth函数生成授权URL
        auth_url = get_facebook_auth_url(state)

        # 返回成功响应，包含授权URL
        return {
            "success": True,
            "data": {
                "auth_url": auth_url,
                "provider": "facebook"
            },
            "message": "Facebook授权URL生成成功"
        }

    except Exception as e:
        # 处理生成授权URL过程中的异常
        return {
            "success": False,
            "error": "生成Facebook授权URL失败",
            "error_type": "OAUTH_URL_GENERATION_ERROR"
        }


def handle_facebook_callback(request_data: dict) -> dict:
    """
    处理Facebook OAuth回调请求

    处理Facebook OAuth授权后的回调，完成用户登录。

    参数:
        request_data: HTTP请求的数据字典，包含code、state等回调参数

    返回:
        dict: 响应字典，包含success状态和用户信息
    """
    try:
        # 从请求数据中提取回调参数
        code = request_data.get("code")
        state = request_data.get("state")
        expected_state = request_data.get("expected_state")

        # 验证必要参数是否存在
        if not code:
            return {
                "success": False,
                "error": "缺少授权码参数",
                "error_type": "MISSING_CODE"
            }

        # 调用Facebook OAuth回调函数完成登录
        result = login_with_facebook(code, state, expected_state)

        # 返回成功响应
        return {
            "success": True,
            "data": result.model_dump(),
            "message": "Facebook登录成功"
        }

    except ValueError as e:
        # 处理OAuth流程中的验证错误
        return {
            "success": False,
            "error": str(e),
            "error_type": "OAUTH_VALIDATION_ERROR"
        }

    except Exception as e:
        # 处理其他未预期的异常
        return {
            "success": False,
            "error": "Facebook OAuth回调处理失败",
            "error_type": "OAUTH_CALLBACK_ERROR"
        }


async def handle_send_verification_code(request_data: dict) -> dict:
    """
    处理发送验证码请求

    向指定邮箱发送验证码，用于邮箱验证流程。

    参数:
        request_data: HTTP请求的数据字典，包含email

    返回:
        dict: 响应字典，包含success状态和消息
    """
    try:
        # 从请求数据中提取邮箱和测试用户标识
        email = request_data.get("email")
        test_user = request_data.get("test_user", False)  # 默认为False

        # 验证必要参数是否存在
        if not email:
            return {
                "success": False,
                "error": "邮箱参数是必需的",
                "error_type": "MISSING_EMAIL"
            }

        # 创建SendVerificationRequest对象，包含邮箱和测试用户标识
        from .schemas import SendVerificationRequest
        send_request = SendVerificationRequest(email=email, test_user=test_user)

        # 异步调用发送验证码函数
        result = await send_verification_code_to_email(send_request)

        # 返回响应
        return {
            "success": result.success,
            "message": result.message
        }

    except EmailAlreadyRegisteredError as e:
        # 处理邮箱已注册的异常
        return {
            "success": False,
            "error": str(e),
            "error_type": "EMAIL_ALREADY_REGISTERED"
        }

    except Exception as e:
        # 处理其他未预期的异常
        return {
            "success": False,
            "error": "发送验证码失败",
            "error_type": "SEND_CODE_ERROR"
        }


def handle_verify_code(request_data: dict) -> dict:
    """
    处理验证码验证请求

    验证用户输入的验证码，并返回用户状态信息。

    参数:
        request_data: HTTP请求的数据字典，包含email和code

    返回:
        dict: 响应字典，包含验证结果和用户状态
    """
    try:
        # 从请求数据中提取邮箱和验证码
        email = request_data.get("email")
        code = request_data.get("code")

        # 验证必要参数是否存在
        if not email or not code:
            return {
                "success": False,
                "error": "邮箱和验证码都是必需的",
                "error_type": "MISSING_PARAMETERS"
            }

        # 创建VerifyCodeRequest对象
        from .schemas import VerifyCodeRequest
        verify_request = VerifyCodeRequest(email=email, code=code)

        # 调用验证码验证函数
        result = verify_email_code(verify_request)

        # 返回响应
        return {
            "success": result.success,
            "message": result.message,
            "user_exists": result.user_exists,
            "is_oauth_user": result.is_oauth_user
        }

    except Exception as e:
        # 处理其他未预期的异常
        return {
            "success": False,
            "error": "验证码验证失败",
            "error_type": "VERIFY_CODE_ERROR"
        }


def handle_set_password(request_data: dict) -> dict:
    """
    处理设置密码请求

    为已验证邮箱的用户设置密码。

    参数:
        request_data: HTTP请求的数据字典，包含email和password

    返回:
        dict: 响应字典，包含密码设置结果
    """
    try:
        # 从请求数据中提取邮箱和密码
        email = request_data.get("email")
        password = request_data.get("password")

        # 验证必要参数是否存在
        if not email or not password:
            return {
                "success": False,
                "error": "邮箱和密码都是必需的",
                "error_type": "MISSING_PARAMETERS"
            }

        # 创建SetPasswordRequest对象
        from .schemas import SetPasswordRequest
        set_password_request = SetPasswordRequest(email=email, password=password)

        # 调用设置密码函数
        result = set_user_password_after_verification(set_password_request)

        # 返回响应
        response_data = {
            "success": result.success,
            "message": result.message
        }

        # 如果创建了新用户，包含user_id
        if result.user_id:
            response_data["user_id"] = result.user_id

        return response_data

    except Exception as e:
        # 处理其他未预期的异常
        return {
            "success": False,
            "error": "设置密码失败",
            "error_type": "SET_PASSWORD_ERROR"
        }


async def handle_forgot_password(request_data: dict) -> dict:
    """
    处理忘记密码请求

    向指定邮箱发送密码重置验证码，用于密码重置流程。
    支持测试模式，当test_user为True时生成固定验证码123456。

    参数:
        request_data: HTTP请求的数据字典，包含email和可选的test_user

    返回:
        dict: 响应字典，包含success状态和消息
    """
    try:
        # 从请求数据中提取邮箱和测试用户标识
        email = request_data.get("email")
        test_user = request_data.get("test_user", False)  # 默认为False

        # 验证必要参数是否存在
        if not email:
            return {
                "success": False,
                "error": "邮箱参数是必需的",
                "error_type": "MISSING_EMAIL"
            }

        # 创建 ForgotPasswordRequest 对象，包含邮箱和测试用户标识
        forgot_request = ForgotPasswordRequest(email=email, test_user=test_user)

        # 异步调用发送重置验证码函数
        # 传入邮箱地址和测试用户标识
        # 当 test_user 为 True 时生成固定验证码123456
        # 得到发送结果布尔值，赋值给 send_result
        send_result = await send_reset_code(forgot_request.email, is_test_user=forgot_request.test_user)

        # 根据发送结果返回相应响应
        if send_result:
            if test_user:
                return {
                    "success": True,
                    "message": "测试重置验证码已发送到您的邮箱，固定验证码：123456"
                }
            else:
                return {
                    "success": True,
                    "message": "密码重置验证码已发送到您的邮箱，请查收"
                }
        else:
            return {
                "success": False,
                "error": "邮箱不存在或验证码发送失败",
                "error_type": "SEND_RESET_CODE_ERROR"
            }

    except InvalidInputError as e:
        # 处理输入数据无效的异常
        return {
            "success": False,
            "error": str(e),
            "error_type": "INVALID_INPUT"
        }

    except Exception as e:
        # 处理其他未预期的异常
        return {
            "success": False,
            "error": "发送重置验证码失败",
            "error_type": "FORGOT_PASSWORD_ERROR"
        }


def handle_reset_password(request_data: dict) -> dict:
    """
    处理重置密码请求

    验证重置验证码并更新用户密码。

    参数:
        request_data: HTTP请求的数据字典，包含email、code、new_password

    返回:
        dict: 响应字典，包含重置结果
    """
    try:
        # 从请求数据中提取邮箱、验证码和新密码
        email = request_data.get("email")
        code = request_data.get("code")
        new_password = request_data.get("new_password")

        # 验证必要参数是否存在
        if not email or not code or not new_password:
            return {
                "success": False,
                "error": "邮箱、验证码和新密码都是必需的",
                "error_type": "MISSING_PARAMETERS"
            }

        # 创建 ResetPasswordRequest 对象
        reset_request = ResetPasswordRequest(
            email=email, 
            code=code, 
            new_password=new_password
        )

        # 调用 reset_password 函数执行密码重置
        # 传入邮箱、验证码和新密码，得到重置结果布尔值
        # 结果赋值给 reset_result
        reset_result = reset_password(
            reset_request.email, 
            reset_request.code, 
            reset_request.new_password
        )

        # 根据重置结果返回相应响应
        if reset_result:
            return {
                "success": True,
                "message": "密码重置成功！您可以使用新密码登录"
            }
        else:
            return {
                "success": False,
                "error": "密码重置失败，请检查验证码或重试",
                "error_type": "RESET_PASSWORD_FAILED"
            }

    except InvalidInputError as e:
        # 处理输入数据无效的异常
        return {
            "success": False,
            "error": str(e),
            "error_type": "INVALID_INPUT"
        }

    except Exception as e:
        # 处理其他未预期的异常
        return {
            "success": False,
            "error": "重置密码过程中发生错误",
            "error_type": "RESET_PASSWORD_ERROR"
        }


def handle_user_profile_request(request_data: dict) -> dict:
    """
    处理获取用户信息请求（受保护路由）

    这是一个包装函数，用于在传统路由系统中集成JWT认证中间件。
    实际的认证和处理逻辑在protected_routes模块中实现。

    参数:
        request_data: HTTP请求的数据字典

    返回:
        dict: 响应字典，包含success状态和用户信息或错误信息
    """
    try:
        # from .auth_middleware 通过 import 导入JWT认证依赖项
        from .auth_middleware import get_current_user, security
        # from .protected_routes 通过 import 导入受保护路由处理函数
        from .protected_routes import handle_get_user_profile

        # 从请求头中提取Authorization信息
        # request_data.get() 通过调用获取Authorization头部信息
        # 传入 "Authorization" 键名，返回认证头字符串或None
        # 赋值给 auth_header 变量存储认证头信息
        auth_header = request_data.get("Authorization")

        # if 条件判断检查认证头是否存在
        if not auth_header:
            # return 语句返回未认证错误响应
            return {
                "success": False,
                "error": "需要登录才能访问此接口",
                "error_type": "AUTHENTICATION_REQUIRED"
            }

        # 解析Bearer令牌格式
        # auth_header.startswith() 通过调用检查认证头是否以"Bearer "开头
        if not auth_header.startswith("Bearer "):
            # return 语句返回令牌格式错误响应
            return {
                "success": False,
                "error": "认证令牌格式错误",
                "error_type": "INVALID_TOKEN_FORMAT"
            }

        # auth_header[7:] 通过切片操作提取Bearer后面的令牌部分
        # 跳过"Bearer "前缀（7个字符），得到纯令牌字符串
        # 赋值给 token 变量存储JWT令牌
        token = auth_header[7:]

        # 手动验证JWT令牌并获取用户信息
        from .tokens import verify_access_token
        from .repository import get_user_by_username
        from .auth_middleware import AuthenticatedUser

        try:
            # verify_access_token() 通过调用验证JWT令牌有效性
            # 传入令牌字符串，返回解码后的载荷数据字典
            # 赋值给 payload 变量存储令牌载荷信息
            payload = verify_access_token(token)

            # payload.get() 通过调用提取用户ID字段
            # 传入 "user_id" 键名，返回用户ID字符串或None
            # 赋值给 user_id 变量存储用户标识符
            user_id = payload.get("user_id")
            
            # payload.get() 通过调用提取用户名字段
            # 传入 "username" 键名，返回用户名字符串或None
            # 赋值给 username 变量存储用户名
            username = payload.get("username")
            
            # payload.get() 通过调用提取令牌类型字段
            # 传入 "type" 键名，返回令牌类型字符串或None
            # 赋值给 token_type 变量存储令牌类型
            token_type = payload.get("type")

            # if 条件判断检查必要字段是否存在且令牌类型正确
            if not user_id or not username or token_type != "access_token":
                # return 语句返回令牌无效错误响应
                return {
                    "success": False,
                    "error": "认证令牌无效",
                    "error_type": "INVALID_TOKEN"
                }

            # get_user_by_username() 通过调用从数据库获取用户完整信息
            # 传入用户名，返回用户数据字典或空字典
            # 赋值给 user_data 变量存储用户数据
            user_data = get_user_by_username(username)
            
            # if 条件判断检查用户是否存在于数据库中
            if not user_data:
                # return 语句返回用户不存在错误响应
                return {
                    "success": False,
                    "error": "用户不存在",
                    "error_type": "USER_NOT_FOUND"
                }

            # user_data.get() 通过调用提取用户邮箱字段
            # 传入 "email" 键名和默认值用户名
            # 返回邮箱字符串，赋值给 email 变量存储用户邮箱地址
            email = user_data.get("email", username)

            # AuthenticatedUser() 通过调用创建认证用户对象
            # 传入用户ID、用户名和邮箱参数
            # 返回包含用户信息的认证对象，赋值给 current_user 变量
            current_user = AuthenticatedUser(
                user_id=user_id,
                username=username,
                email=email
            )

            # handle_get_user_profile() 通过调用处理获取用户信息的业务逻辑
            # 传入已认证的用户对象，返回处理结果字典
            # 赋值给 result 变量存储处理结果
            result = handle_get_user_profile(current_user)
            
            # return 语句返回处理结果
            return result

        except ValueError:
            # return 语句返回令牌验证失败错误响应
            return {
                "success": False,
                "error": "认证令牌已过期或无效",
                "error_type": "TOKEN_EXPIRED"
            }

    except Exception as e:
        # return 语句返回处理过程中发生的通用错误响应
        return {
            "success": False,
            "error": "获取用户信息失败",
            "error_type": "GET_PROFILE_ERROR"
        }


def handle_user_settings_request(request_data: dict) -> dict:
    """
    处理更新用户设置请求（受保护路由）

    这是一个包装函数，用于在传统路由系统中集成JWT认证中间件。
    实际的认证和处理逻辑在protected_routes模块中实现。

    参数:
        request_data: HTTP请求的数据字典，包含设置更新信息

    返回:
        dict: 响应字典，包含success状态和更新结果或错误信息
    """
    try:
        # from .auth_middleware 通过 import 导入JWT认证相关模块
        from .auth_middleware import AuthenticatedUser
        # from .protected_routes 通过 import 导入受保护路由处理函数
        from .protected_routes import handle_update_user_settings

        # 从请求头中提取Authorization信息
        # request_data.get() 通过调用获取Authorization头部信息
        # 传入 "Authorization" 键名，返回认证头字符串或None
        # 赋值给 auth_header 变量存储认证头信息
        auth_header = request_data.get("Authorization")

        # if 条件判断检查认证头是否存在
        if not auth_header:
            # return 语句返回未认证错误响应
            return {
                "success": False,
                "error": "需要登录才能访问此接口",
                "error_type": "AUTHENTICATION_REQUIRED"
            }

        # 解析Bearer令牌格式
        # auth_header.startswith() 通过调用检查认证头是否以"Bearer "开头
        if not auth_header.startswith("Bearer "):
            # return 语句返回令牌格式错误响应
            return {
                "success": False,
                "error": "认证令牌格式错误",
                "error_type": "INVALID_TOKEN_FORMAT"
            }

        # auth_header[7:] 通过切片操作提取Bearer后面的令牌部分
        # 跳过"Bearer "前缀（7个字符），得到纯令牌字符串
        # 赋值给 token 变量存储JWT令牌
        token = auth_header[7:]

        # 手动验证JWT令牌并获取用户信息
        from .tokens import verify_access_token
        from .repository import get_user_by_username

        try:
            # verify_access_token() 通过调用验证JWT令牌有效性
            # 传入令牌字符串，返回解码后的载荷数据字典
            # 赋值给 payload 变量存储令牌载荷信息
            payload = verify_access_token(token)

            # payload.get() 通过调用提取用户ID字段
            # 传入 "user_id" 键名，返回用户ID字符串或None
            # 赋值给 user_id 变量存储用户标识符
            user_id = payload.get("user_id")
            
            # payload.get() 通过调用提取用户名字段
            # 传入 "username" 键名，返回用户名字符串或None
            # 赋值给 username 变量存储用户名
            username = payload.get("username")
            
            # payload.get() 通过调用提取令牌类型字段
            # 传入 "type" 键名，返回令牌类型字符串或None
            # 赋值给 token_type 变量存储令牌类型
            token_type = payload.get("type")

            # if 条件判断检查必要字段是否存在且令牌类型正确
            if not user_id or not username or token_type != "access_token":
                # return 语句返回令牌无效错误响应
                return {
                    "success": False,
                    "error": "认证令牌无效",
                    "error_type": "INVALID_TOKEN"
                }

            # get_user_by_username() 通过调用从数据库获取用户完整信息
            # 传入用户名，返回用户数据字典或空字典
            # 赋值给 user_data 变量存储用户数据
            user_data = get_user_by_username(username)
            
            # if 条件判断检查用户是否存在于数据库中
            if not user_data:
                # return 语句返回用户不存在错误响应
                return {
                    "success": False,
                    "error": "用户不存在",
                    "error_type": "USER_NOT_FOUND"
                }

            # user_data.get() 通过调用提取用户邮箱字段
            # 传入 "email" 键名和默认值用户名
            # 返回邮箱字符串，赋值给 email 变量存储用户邮箱地址
            email = user_data.get("email", username)

            # AuthenticatedUser() 通过调用创建认证用户对象
            # 传入用户ID、用户名和邮箱参数
            # 返回包含用户信息的认证对象，赋值给 current_user 变量
            current_user = AuthenticatedUser(
                user_id=user_id,
                username=username,
                email=email
            )

            # handle_update_user_settings() 通过调用处理更新用户设置的业务逻辑
            # 传入请求数据和已认证的用户对象，返回处理结果字典
            # 赋值给 result 变量存储处理结果
            result = handle_update_user_settings(request_data, current_user)
            
            # return 语句返回处理结果
            return result

        except ValueError:
            # return 语句返回令牌验证失败错误响应
            return {
                "success": False,
                "error": "认证令牌已过期或无效",
                "error_type": "TOKEN_EXPIRED"
            }

    except Exception as e:
        # return 语句返回处理过程中发生的通用错误响应
        return {
            "success": False,
            "error": "更新用户设置失败",
            "error_type": "UPDATE_SETTINGS_ERROR"
        }


def handle_token_refresh_request(request_data: dict) -> dict:
    """
    处理刷新令牌请求

    这个路由不需要访问令牌认证，但需要有效的刷新令牌。
    用于在访问令牌过期时获取新的令牌对。

    参数:
        request_data: HTTP请求的数据字典，包含刷新令牌

    返回:
        dict: 响应字典，包含success状态和新的令牌对或错误信息
    """
    try:
        # from .protected_routes 通过 import 导入令牌刷新处理函数
        from .protected_routes import handle_refresh_token

        # handle_refresh_token() 通过调用处理令牌刷新的业务逻辑
        # 传入请求数据字典，返回处理结果字典
        # 赋值给 result 变量存储处理结果
        result = handle_refresh_token(request_data)
        
        # return 语句返回处理结果
        return result

    except Exception as e:
        # return 语句返回处理过程中发生的通用错误响应
        return {
            "success": False,
            "error": "令牌刷新失败",
            "error_type": "TOKEN_REFRESH_ERROR"
        }


def handle_logout_request(request_data: dict) -> dict:
    """
    处理用户登出请求（受保护路由）

    这是一个包装函数，用于在传统路由系统中集成JWT认证中间件。
    实际的认证和处理逻辑在protected_routes模块中实现。

    参数:
        request_data: HTTP请求的数据字典

    返回:
        dict: 响应字典，包含success状态和登出结果或错误信息
    """
    try:
        # from .auth_middleware 通过 import 导入JWT认证相关模块
        from .auth_middleware import AuthenticatedUser
        # from .protected_routes 通过 import 导入受保护路由处理函数
        from .protected_routes import handle_logout

        # 从请求头中提取Authorization信息
        # request_data.get() 通过调用获取Authorization头部信息
        # 传入 "Authorization" 键名，返回认证头字符串或None
        # 赋值给 auth_header 变量存储认证头信息
        auth_header = request_data.get("Authorization")

        # if 条件判断检查认证头是否存在
        if not auth_header:
            # return 语句返回未认证错误响应
            return {
                "success": False,
                "error": "需要登录才能执行登出操作",
                "error_type": "AUTHENTICATION_REQUIRED"
            }

        # 解析Bearer令牌格式
        # auth_header.startswith() 通过调用检查认证头是否以"Bearer "开头
        if not auth_header.startswith("Bearer "):
            # return 语句返回令牌格式错误响应
            return {
                "success": False,
                "error": "认证令牌格式错误",
                "error_type": "INVALID_TOKEN_FORMAT"
            }

        # auth_header[7:] 通过切片操作提取Bearer后面的令牌部分
        # 跳过"Bearer "前缀（7个字符），得到纯令牌字符串
        # 赋值给 token 变量存储JWT令牌
        token = auth_header[7:]

        # 手动验证JWT令牌并获取用户信息
        from .tokens import verify_access_token
        from .repository import get_user_by_username

        try:
            # verify_access_token() 通过调用验证JWT令牌有效性
            # 传入令牌字符串，返回解码后的载荷数据字典
            # 赋值给 payload 变量存储令牌载荷信息
            payload = verify_access_token(token)

            # payload.get() 通过调用提取用户ID字段
            # 传入 "user_id" 键名，返回用户ID字符串或None
            # 赋值给 user_id 变量存储用户标识符
            user_id = payload.get("user_id")
            
            # payload.get() 通过调用提取用户名字段
            # 传入 "username" 键名，返回用户名字符串或None
            # 赋值给 username 变量存储用户名
            username = payload.get("username")
            
            # payload.get() 通过调用提取令牌类型字段
            # 传入 "type" 键名，返回令牌类型字符串或None
            # 赋值给 token_type 变量存储令牌类型
            token_type = payload.get("type")

            # if 条件判断检查必要字段是否存在且令牌类型正确
            if not user_id or not username or token_type != "access_token":
                # return 语句返回令牌无效错误响应
                return {
                    "success": False,
                    "error": "认证令牌无效",
                    "error_type": "INVALID_TOKEN"
                }

            # get_user_by_username() 通过调用从数据库获取用户完整信息
            # 传入用户名，返回用户数据字典或空字典
            # 赋值给 user_data 变量存储用户数据
            user_data = get_user_by_username(username)
            
            # if 条件判断检查用户是否存在于数据库中
            if not user_data:
                # return 语句返回用户不存在错误响应
                return {
                    "success": False,
                    "error": "用户不存在",
                    "error_type": "USER_NOT_FOUND"
                }

            # user_data.get() 通过调用提取用户邮箱字段
            # 传入 "email" 键名和默认值用户名
            # 返回邮箱字符串，赋值给 email 变量存储用户邮箱地址
            email = user_data.get("email", username)

            # AuthenticatedUser() 通过调用创建认证用户对象
            # 传入用户ID、用户名和邮箱参数
            # 返回包含用户信息的认证对象，赋值给 current_user 变量
            current_user = AuthenticatedUser(
                user_id=user_id,
                username=username,
                email=email
            )

            # handle_logout() 通过调用处理用户登出的业务逻辑
            # 传入已认证的用户对象，返回处理结果字典
            # 赋值给 result 变量存储处理结果
            result = handle_logout(current_user)
            
            # return 语句返回处理结果
            return result

        except ValueError:
            # return 语句返回令牌验证失败错误响应
            return {
                "success": False,
                "error": "认证令牌已过期或无效",
                "error_type": "TOKEN_EXPIRED"
            }

    except Exception as e:
        # return 语句返回处理过程中发生的通用错误响应
        return {
            "success": False,
            "error": "登出操作失败",
            "error_type": "LOGOUT_ERROR"
        }


# 路由映射定义
# 定义URL路径到处理函数的映射关系
ROUTES = {
    # 传统注册和登录
    "/auth/register": handle_register_request,
    "/auth/login": handle_login_request,

    # 邮箱验证码流程
    "/auth/send-verification": handle_send_verification_code,
    "/auth/verify-code": handle_verify_code,
    "/auth/set-password": handle_set_password,

    # 忘记密码流程
    "/auth/forgot-password": handle_forgot_password,
    "/auth/reset-password": handle_reset_password,

    # OAuth登录
    "/auth/google": handle_google_auth,
    "/auth/google/callback": handle_google_callback,
    "/auth/facebook": handle_facebook_auth,
    "/auth/facebook/callback": handle_facebook_callback,

    # 受保护的用户路由（需要JWT认证）
    "/auth/user/profile": handle_user_profile_request,
    "/auth/user/settings": handle_user_settings_request,
    "/auth/user/logout": handle_logout_request,

    # 令牌管理路由
    "/auth/token/refresh": handle_token_refresh_request
}
