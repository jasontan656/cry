# Auth模块业务服务层
# 承载从intent_handlers迁移的纯业务逻辑函数
# 不包含路由/注册副作用，专注业务逻辑实现

import asyncio
from typing import Dict, Any, Optional

# 业务逻辑模块导入 - 不导入路由相关模块
from .register import (
    register_user, send_verification_code_to_email,
    verify_email_code, set_user_password_after_verification
)
from .login import login_user
from .oauth_google import get_google_auth_url, login_with_google
from .oauth_facebook import get_facebook_auth_url, login_with_facebook
from .reset_password import send_reset_code, verify_reset_code, reset_password
from .protected_routes import (
    handle_get_user_profile, handle_update_user_settings,
    handle_refresh_token, handle_logout
)
from .schemas import (
    UserRegisterRequest, SendVerificationRequest, VerifyCodeRequest,
    SetPasswordRequest, ForgotPasswordRequest, ResetPasswordRequest
)
from .exceptions import (
    UserAlreadyExistsError, InvalidInputError, InvalidCredentialsError,
    EmailAlreadyRegisteredError
)
from .auth_middleware import AuthenticatedUser
from .tokens import verify_access_token
from .repository import get_user_by_username


# ============ 响应格式化工具函数 ============

def create_success_response(data: Any = None, message: str = "操作成功") -> Dict[str, Any]:
    """
    create_success_response 通过构建字典创建标准成功响应格式
    用于统一所有业务服务的成功响应结构
    
    参数:
        data: 响应数据，可以是任何可序列化的对象
        message: 成功消息字符串，默认为"操作成功"
    
    返回:
        dict: 标准成功响应格式字典，包含success、message和可选的data字段
    """
    # response 通过字典字面量创建基础响应结构
    response = {
        "success": True,     # success字段标记响应成功状态
        "message": message   # message字段包含操作成功描述
    }
    
    # if data is not None 条件检查是否有响应数据需要包含
    if data is not None:
        # response["data"] 通过字典赋值添加响应数据到结果中
        response["data"] = data
    
    # return 语句返回构建完成的成功响应字典
    return response


def create_error_response(error: str, error_type: str = "UNKNOWN_ERROR", details: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    create_error_response 通过构建字典创建标准错误响应格式
    用于统一所有业务服务的错误响应结构
    
    参数:
        error: 错误信息字符串，描述具体的错误内容
        error_type: 错误类型标识字符串，用于客户端分类处理
        details: 额外的错误详情字典，包含调试或上下文信息
    
    返回:
        dict: 标准错误响应格式字典，包含success、error、error_type和可选details字段
    """
    # response 通过字典字面量创建基础错误响应结构
    response = {
        "success": False,        # success字段标记响应失败状态
        "error": error,          # error字段包含错误信息描述
        "error_type": error_type # error_type字段标识错误类型分类
    }
    
    # if details is not None 条件检查是否有错误详情需要包含
    if details is not None:
        # response["details"] 通过字典赋值添加错误详情到结果中
        response["details"] = details
    
    # return 语句返回构建完成的错误响应字典
    return response


def extract_auth_info_from_payload(payload: Dict[str, Any]) -> Optional[AuthenticatedUser]:
    """
    extract_auth_info_from_payload 从载荷中提取认证信息并验证token有效性
    解析Authorization头或access_token字段，验证JWT并返回用户对象
    
    参数:
        payload: 意图载荷字典，可能包含认证令牌信息
    
    返回:
        AuthenticatedUser对象或None: 认证成功返回用户对象，失败返回None
    """
    try:
        # 支持嵌套payload格式的认证信息提取
        # 检查是否是hub传递的格式（包含payload字段）
        if "payload" in payload and isinstance(payload["payload"], dict):
            actual_payload = payload["payload"]
        else:
            actual_payload = payload
            
        # 同时检查两个层级的认证信息
        # auth_header 优先从actual_payload中提取，然后从顶层payload提取
        auth_header = (actual_payload.get("Authorization") or actual_payload.get("access_token") or 
                      payload.get("Authorization") or payload.get("access_token"))
        
        # if not auth_header 条件检查认证头部是否存在
        if not auth_header:
            # return None 当无认证头部时直接返回None表示未认证
            return None
            
        # 处理Bearer令牌格式的认证头部
        # if auth_header.startswith("Bearer ") 条件检查是否为Bearer格式
        if auth_header.startswith("Bearer "):
            # token 通过切片操作跳过"Bearer "前缀获取真实token
            token = auth_header[7:]  # 跳过"Bearer "前缀
        else:
            # token 直接使用auth_header作为token内容
            token = auth_header
        
        # payload_data 通过verify_access_token函数验证JWT令牌有效性
        payload_data = verify_access_token(token)
        
        # 从验证后的载荷中提取用户身份信息
        # user_id 通过get方法提取用户ID字段
        user_id = payload_data.get("user_id")
        # username 通过get方法提取用户名字段  
        username = payload_data.get("username")
        # token_type 通过get方法提取token类型字段
        token_type = payload_data.get("type")
        
        # 验证token载荷中的必要字段和类型
        # if not user_id or not username or token_type != "access_token" 综合条件检查
        if not user_id or not username or token_type != "access_token":
            # return None 当关键字段缺失或token类型不匹配时返回None
            return None
        
        # user_data 通过get_user_by_username函数从数据库获取用户完整信息
        user_data = get_user_by_username(username)
        
        # if not user_data 条件检查用户数据是否存在
        if not user_data:
            # return None 当用户不存在时返回None
            return None
        
        # email 通过get方法提取用户邮箱，默认使用username
        email = user_data.get("email", username)
        # return AuthenticatedUser 创建并返回认证用户对象
        return AuthenticatedUser(
            user_id=user_id,     # user_id字段设置为从token中提取的用户ID
            username=username,   # username字段设置为从token中提取的用户名
            email=email          # email字段设置为从数据库获取的邮箱地址
        )
        
    except (ValueError, Exception):
        # except 捕获所有验证异常，返回None表示认证失败
        return None


def extract_auth_info_from_context(context: Dict[str, Any]) -> Optional[AuthenticatedUser]:
    """
    extract_auth_info_from_context 从上下文字典中提取认证信息
    检查context中的认证标识并构建用户对象
    
    参数:
        context: 意图上下文字典，可能包含用户认证信息
    
    返回:
        AuthenticatedUser对象或None: 认证信息存在时返回用户对象，否则返回None
    """
    try:
        # if not context.get("authenticated", False) 条件检查上下文中的认证状态标识
        if not context.get("authenticated", False):
            # return None 当上下文未标记为已认证时直接返回None
            return None
        
        # 从上下文中提取用户身份信息字段
        # user_id 通过get方法提取用户ID字段
        user_id = context.get("user_id")
        # username 通过get方法提取用户名字段
        username = context.get("username") 
        # email 通过get方法提取邮箱字段
        email = context.get("email")
        
        # 验证必要字段是否完整
        # if not user_id or not username 条件检查关键身份字段
        if not user_id or not username:
            # return None 当关键身份字段缺失时返回None
            return None
        
        # return AuthenticatedUser 创建并返回认证用户对象
        return AuthenticatedUser(
            user_id=user_id,                # user_id字段设置为从上下文提取的用户ID
            username=username,              # username字段设置为从上下文提取的用户名
            email=email or username         # email字段设置为提取的邮箱或使用用户名作为默认值
        )
        
    except Exception:
        # except 捕获所有提取异常，返回None表示提取失败
        return None


# ============ 注册相关业务服务函数 ============

async def register_service(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    register_service 处理用户注册业务逻辑的服务函数
    从handle_auth_register迁移而来，包含邮箱密码验证和用户创建逻辑
    
    参数:
        payload: 包含注册信息的载荷字典，需包含email、password、test_user字段
    
    返回:
        dict: 标准服务响应格式，成功时包含用户注册结果数据
    """
    try:
        # 从载荷中提取注册必要信息字段
        # email 通过get方法提取邮箱地址字段
        email = payload.get("email")
        # password 通过get方法提取密码字段
        password = payload.get("password")
        # test_user 通过get方法提取测试用户标识，默认False
        test_user = payload.get("test_user", False)
        
        # 验证注册请求的必要参数完整性
        # if not email or not password 条件检查必须字段
        if not email or not password:
            # return create_error_response 当必要参数缺失时返回错误响应
            return create_error_response(
                "邮箱和密码都是必需的",         # error参数设置错误信息
                "MISSING_PARAMETERS"         # error_type参数设置错误类型
            )
        
        # register_request 通过UserRegisterRequest构造函数创建注册请求对象
        register_request = UserRegisterRequest(
            email=email,         # email字段设置为提取的邮箱地址
            password=password,   # password字段设置为提取的密码
            test_user=test_user  # test_user字段设置为测试用户标识
        )
        
        # result 通过register_user函数执行用户注册业务逻辑
        result = register_user(register_request)
        
        # return create_success_response 注册成功时返回成功响应
        return create_success_response(
            data=result.model_dump(),        # data参数设置为注册结果的字典形式
            message="注册成功"                # message参数设置为成功消息
        )
        
    except InvalidInputError as e:
        # except InvalidInputError 捕获输入验证异常
        return create_error_response(str(e), "INVALID_INPUT")
    except UserAlreadyExistsError as e:
        # except UserAlreadyExistsError 捕获用户已存在异常
        return create_error_response(str(e), "USER_EXISTS")
    except EmailAlreadyRegisteredError as e:
        # except EmailAlreadyRegisteredError 捕获邮箱已注册异常
        return create_error_response(str(e), "EMAIL_ALREADY_REGISTERED")
    except Exception as e:
        # except Exception 捕获所有其他异常
        return create_error_response(
            "注册过程中发生未知错误",           # error参数设置通用错误信息
            "UNKNOWN_ERROR"                # error_type参数设置为未知错误类型
        )


async def send_verification_service(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    send_verification_service 处理发送验证码业务逻辑的服务函数
    从handle_auth_send_verification迁移而来，负责邮箱验证码的生成和发送
    
    参数:
        payload: 包含邮箱信息的载荷字典，需包含email、test_user字段
    
    返回:
        dict: 标准服务响应格式，包含验证码发送结果信息
    """
    try:
        # 从载荷中提取验证码发送所需信息字段，支持嵌套payload格式
        # 检查是否是hub传递的格式（包含payload字段）
        if "payload" in payload and isinstance(payload["payload"], dict):
            actual_payload = payload["payload"]
        else:
            actual_payload = payload
            
        # email 通过get方法从actual_payload中提取目标邮箱地址字段
        email = actual_payload.get("email")
        # test_user 通过get方法提取测试用户标识，默认False
        test_user = actual_payload.get("test_user", False)
        
        # 验证发送验证码请求的必要参数
        # if not email 条件检查邮箱字段是否存在
        if not email:
            # raise InvalidInputError 当邮箱参数缺失时抛出输入错误异常
            raise InvalidInputError("邮箱参数是必需的")
        
        # send_request 通过SendVerificationRequest构造函数创建发送请求对象
        send_request = SendVerificationRequest(email=email, test_user=test_user)
        
        # result 通过异步调用send_verification_code_to_email函数发送验证码
        result = await send_verification_code_to_email(send_request)
        
        # return create_success_response 发送成功时返回成功响应
        return create_success_response(
            data={"success": result.success, "message": result.message},  # data参数包含发送结果
            message=result.message                                        # message参数使用返回的消息
        )
        
    except EmailAlreadyRegisteredError as e:
        # EmailAlreadyRegisteredError 直接重新抛出邮箱已注册异常
        raise e
    except Exception as e:
        # Exception 对于其他异常，包装为系统错误重新抛出
        raise RuntimeError(f"发送验证码失败: {str(e)}")


async def verify_code_service(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    verify_code_service 处理验证码验证业务逻辑的服务函数
    从handle_auth_verify_code迁移而来，负责验证用户输入的邮箱验证码
    
    参数:
        payload: 包含验证码信息的载荷字典，需包含email、code字段
    
    返回:
        dict: 标准服务响应格式，包含验证结果和用户状态信息
    """
    try:
        # 从载荷中提取验证码验证所需信息字段，支持嵌套payload格式
        # 检查是否是hub传递的格式（包含payload字段）
        if "payload" in payload and isinstance(payload["payload"], dict):
            actual_payload = payload["payload"]
        else:
            actual_payload = payload
            
        # email 通过get方法从actual_payload中提取邮箱地址字段
        email = actual_payload.get("email")
        # code 通过get方法提取验证码字段
        code = actual_payload.get("code")
        
        # 验证验证码验证请求的必要参数
        # if not email or not code 条件检查必要字段是否完整
        if not email or not code:
            # return create_error_response 当必要参数缺失时返回错误响应
            return create_error_response(
                "邮箱和验证码都是必需的",           # error参数设置错误信息
                "MISSING_PARAMETERS"            # error_type参数设置错误类型
            )
        
        # verify_request 通过VerifyCodeRequest构造函数创建验证请求对象
        verify_request = VerifyCodeRequest(email=email, code=code)
        
        # result 通过verify_email_code函数执行验证码验证逻辑
        result = verify_email_code(verify_request)
        
        # return create_success_response 验证成功时返回成功响应
        return create_success_response(
            data={
                "success": result.success,              # success字段包含验证结果状态
                "message": result.message,              # message字段包含验证结果消息
                "user_exists": result.user_exists,      # user_exists字段标识用户是否已存在
                "is_oauth_user": result.is_oauth_user   # is_oauth_user字段标识是否为OAuth用户
            },
            message=result.message                      # message参数使用验证结果消息
        )
        
    except Exception as e:
        # except Exception 捕获所有验证失败异常
        return create_error_response(
            "验证码验证失败",                      # error参数设置错误信息
            "VERIFY_CODE_ERROR"                # error_type参数设置错误类型
        )


async def set_password_service(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    set_password_service 处理设置密码业务逻辑的服务函数
    从handle_auth_set_password迁移而来，负责为已验证邮箱的用户设置密码
    
    参数:
        payload: 包含密码信息的载荷字典，需包含email、password字段
    
    返回:
        dict: 标准服务响应格式，包含密码设置结果和用户ID信息
    """
    try:
        # 从载荷中提取密码设置所需信息字段，支持嵌套payload格式
        # 检查是否是hub传递的格式（包含payload字段）
        if "payload" in payload and isinstance(payload["payload"], dict):
            actual_payload = payload["payload"]
        else:
            actual_payload = payload
            
        # email 通过get方法从actual_payload中提取邮箱地址字段
        email = actual_payload.get("email")
        # password 通过get方法提取新密码字段
        password = actual_payload.get("password")
        
        # 验证密码设置请求的必要参数
        # if not email or not password 条件检查必要字段是否完整
        if not email or not password:
            # return create_error_response 当必要参数缺失时返回错误响应
            return create_error_response(
                "邮箱和密码都是必需的",             # error参数设置错误信息
                "MISSING_PARAMETERS"            # error_type参数设置错误类型
            )
        
        # set_password_request 通过SetPasswordRequest构造函数创建设置密码请求对象
        set_password_request = SetPasswordRequest(email=email, password=password)
        
        # result 通过set_user_password_after_verification函数执行密码设置逻辑
        result = set_user_password_after_verification(set_password_request)
        
        # response_data 通过字典构建响应数据结构
        response_data = {
            "success": result.success,              # success字段包含设置结果状态
            "message": result.message               # message字段包含设置结果消息
        }
        
        # 如果创建了新用户，包含用户ID到响应数据中
        # if result.user_id 条件检查是否有用户ID返回
        if result.user_id:
            # response_data["user_id"] 通过字典赋值添加用户ID字段
            response_data["user_id"] = result.user_id
        
        # return create_success_response 设置成功时返回成功响应
        return create_success_response(
            data=response_data,                     # data参数包含响应数据
            message=result.message                  # message参数使用设置结果消息
        )
        
    except Exception as e:
        # except Exception 捕获所有密码设置失败异常
        return create_error_response(
            "设置密码失败",                        # error参数设置错误信息
            "SET_PASSWORD_ERROR"                # error_type参数设置错误类型
        )


# ============ 登录相关业务服务函数 ============

async def login_service(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    login_service 处理用户登录业务逻辑的服务函数
    从handle_auth_login迁移而来，负责邮箱密码验证和token生成
    
    参数:
        payload: 包含登录信息的载荷字典，需包含email、password字段
    
    返回:
        dict: 标准服务响应格式，成功时包含access_token和refresh_token
    """
    try:
        # 从载荷中提取登录认证所需信息字段，支持嵌套payload格式
        # 检查是否是hub传递的格式（包含payload字段）
        if "payload" in payload and isinstance(payload["payload"], dict):
            actual_payload = payload["payload"]
        else:
            actual_payload = payload
            
        # email 通过get方法从actual_payload中提取邮箱地址字段
        email = actual_payload.get("email")
        # password 通过get方法提取密码字段
        password = actual_payload.get("password")
        
        # 验证登录请求的必要参数
        # if not email or not password 条件检查必要字段是否完整
        if not email or not password:
            # raise InvalidInputError 当必要参数缺失时抛出输入错误异常
            raise InvalidInputError("邮箱和密码都是必需的")
        
        # result 通过login_user函数执行登录认证业务逻辑
        result = login_user(email, password)
        
        # return create_success_response 登录成功时返回成功响应
        return create_success_response(
            data=result.model_dump(),               # data参数设置为登录结果的字典形式
            message="登录成功"                       # message参数设置为成功消息
        )
        
    except InvalidCredentialsError as e:
        # InvalidCredentialsError 直接重新抛出登录凭据无效异常
        raise e
    except Exception as e:
        # Exception 对于其他异常，包装为系统错误重新抛出
        raise RuntimeError(f"登录过程中发生未知错误: {str(e)}")


# ============ OAuth相关业务服务函数 ============

async def oauth_google_url_service(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    oauth_google_url_service 处理Google OAuth授权URL生成业务逻辑的服务函数
    从handle_auth_oauth_google_url迁移而来，负责生成Google OAuth认证链接
    
    参数:
        payload: 包含OAuth参数的载荷字典，可选包含state字段
    
    返回:
        dict: 标准服务响应格式，包含生成的Google授权URL和提供商信息
    """
    try:
        # state 通过get方法提取状态参数字段（用于OAuth安全验证）
        state = payload.get("state")
        
        # auth_url 通过get_google_auth_url函数生成Google OAuth授权URL
        auth_url = get_google_auth_url(state)
        
        # return create_success_response OAuth URL生成成功时返回成功响应
        return create_success_response(
            data={
                "auth_url": auth_url,               # auth_url字段包含生成的授权链接
                "provider": "google"                # provider字段标识OAuth提供商为Google
            },
            message="Google授权URL生成成功"          # message参数设置为成功消息
        )
        
    except Exception as e:
        # except Exception 捕获所有URL生成失败异常
        return create_error_response(
            "生成Google授权URL失败",                # error参数设置错误信息
            "OAUTH_URL_GENERATION_ERROR"        # error_type参数设置错误类型
        )


async def oauth_google_callback_service(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    oauth_google_callback_service 处理Google OAuth回调业务逻辑的服务函数
    从handle_auth_oauth_google_callback迁移而来，负责处理Google OAuth认证回调
    
    参数:
        payload: 包含OAuth回调参数的载荷字典，需包含code字段，可选state、expected_state
    
    返回:
        dict: 标准服务响应格式，成功时包含用户信息和认证token
    """
    try:
        # 从载荷中提取OAuth回调所需参数字段
        # code 通过get方法提取授权码字段
        code = payload.get("code")
        # state 通过get方法提取状态参数字段
        state = payload.get("state")
        # expected_state 通过get方法提取预期状态参数字段
        expected_state = payload.get("expected_state")
        
        # 验证OAuth回调的必要参数
        # if not code 条件检查授权码字段是否存在
        if not code:
            # return create_error_response 当授权码缺失时返回错误响应
            return create_error_response(
                "缺少授权码参数",                     # error参数设置错误信息
                "MISSING_CODE"                   # error_type参数设置错误类型
            )
        
        # result 通过login_with_google函数执行Google OAuth登录业务逻辑
        result = login_with_google(code, state, expected_state)
        
        # return create_success_response Google登录成功时返回成功响应
        return create_success_response(
            data=result.model_dump(),               # data参数设置为登录结果的字典形式
            message="Google登录成功"                 # message参数设置为成功消息
        )
        
    except ValueError as e:
        # except ValueError 捕获OAuth参数验证异常
        return create_error_response(str(e), "OAUTH_VALIDATION_ERROR")
    except Exception as e:
        # except Exception 捕获所有其他OAuth回调处理失败异常
        return create_error_response(
            "Google OAuth回调处理失败",              # error参数设置错误信息
            "OAUTH_CALLBACK_ERROR"               # error_type参数设置错误类型
        )


async def oauth_facebook_url_service(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    oauth_facebook_url_service 处理Facebook OAuth授权URL生成业务逻辑的服务函数
    从handle_auth_oauth_facebook_url迁移而来，负责生成Facebook OAuth认证链接
    
    参数:
        payload: 包含OAuth参数的载荷字典，可选包含state字段
    
    返回:
        dict: 标准服务响应格式，包含生成的Facebook授权URL和提供商信息
    """
    try:
        # state 通过get方法提取状态参数字段（用于OAuth安全验证）
        state = payload.get("state")
        
        # auth_url 通过get_facebook_auth_url函数生成Facebook OAuth授权URL
        auth_url = get_facebook_auth_url(state)
        
        # return create_success_response OAuth URL生成成功时返回成功响应
        return create_success_response(
            data={
                "auth_url": auth_url,               # auth_url字段包含生成的授权链接
                "provider": "facebook"              # provider字段标识OAuth提供商为Facebook
            },
            message="Facebook授权URL生成成功"        # message参数设置为成功消息
        )
        
    except Exception as e:
        # except Exception 捕获所有URL生成失败异常
        return create_error_response(
            "生成Facebook授权URL失败",              # error参数设置错误信息
            "OAUTH_URL_GENERATION_ERROR"        # error_type参数设置错误类型
        )


async def oauth_facebook_callback_service(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    oauth_facebook_callback_service 处理Facebook OAuth回调业务逻辑的服务函数
    从handle_auth_oauth_facebook_callback迁移而来，负责处理Facebook OAuth认证回调
    
    参数:
        payload: 包含OAuth回调参数的载荷字典，需包含code字段，可选state、expected_state
    
    返回:
        dict: 标准服务响应格式，成功时包含用户信息和认证token
    """
    try:
        # 从载荷中提取OAuth回调所需参数字段
        # code 通过get方法提取授权码字段
        code = payload.get("code")
        # state 通过get方法提取状态参数字段
        state = payload.get("state")
        # expected_state 通过get方法提取预期状态参数字段
        expected_state = payload.get("expected_state")
        
        # 验证OAuth回调的必要参数
        # if not code 条件检查授权码字段是否存在
        if not code:
            # return create_error_response 当授权码缺失时返回错误响应
            return create_error_response(
                "缺少授权码参数",                     # error参数设置错误信息
                "MISSING_CODE"                   # error_type参数设置错误类型
            )
        
        # result 通过login_with_facebook函数执行Facebook OAuth登录业务逻辑
        result = login_with_facebook(code, state, expected_state)
        
        # return create_success_response Facebook登录成功时返回成功响应
        return create_success_response(
            data=result.model_dump(),               # data参数设置为登录结果的字典形式
            message="Facebook登录成功"               # message参数设置为成功消息
        )
        
    except ValueError as e:
        # except ValueError 捕获OAuth参数验证异常
        return create_error_response(str(e), "OAUTH_VALIDATION_ERROR")
    except Exception as e:
        # except Exception 捕获所有其他OAuth回调处理失败异常
        return create_error_response(
            "Facebook OAuth回调处理失败",            # error参数设置错误信息
            "OAUTH_CALLBACK_ERROR"               # error_type参数设置错误类型
        )


# ============ 密码重置相关业务服务函数 ============

async def forgot_password_service(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    forgot_password_service 处理忘记密码业务逻辑的服务函数
    从handle_auth_forgot_password迁移而来，负责发送密码重置验证码
    
    参数:
        payload: 包含邮箱信息的载荷字典，需包含email字段，可选test_user
    
    返回:
        dict: 标准服务响应格式，包含密码重置验证码发送结果
    """
    try:
        # 从载荷中提取密码重置所需信息字段，支持嵌套payload格式
        # 检查是否是hub传递的格式（包含payload字段）
        if "payload" in payload and isinstance(payload["payload"], dict):
            actual_payload = payload["payload"]
        else:
            actual_payload = payload
            
        # email 通过get方法从actual_payload中提取邮箱地址字段
        email = actual_payload.get("email")
        # test_user 通过get方法提取测试用户标识，默认False
        test_user = actual_payload.get("test_user", False)
        
        # 验证忘记密码请求的必要参数
        # if not email 条件检查邮箱字段是否存在
        if not email:
            # return create_error_response 当邮箱参数缺失时返回错误响应
            return create_error_response(
                "邮箱参数是必需的",                   # error参数设置错误信息
                "MISSING_EMAIL"                  # error_type参数设置错误类型
            )
        
        # forgot_request 通过ForgotPasswordRequest构造函数创建忘记密码请求对象
        forgot_request = ForgotPasswordRequest(email=email, test_user=test_user)
        
        # send_result 通过异步调用send_reset_code函数发送重置验证码
        send_result = await send_reset_code(forgot_request.email, is_test_user=forgot_request.test_user)
        
        # 根据发送结果返回相应响应
        # if send_result 条件检查发送是否成功
        if send_result:
            # if test_user 条件检查是否为测试用户
            if test_user:
                # return create_success_response 测试用户发送成功时返回包含固定验证码的响应
                return create_success_response(
                    message="测试重置验证码已发送到您的邮箱，固定验证码：123456"  # message包含测试验证码信息
                )
            else:
                # return create_success_response 正常用户发送成功时返回标准成功响应
                return create_success_response(
                    message="密码重置验证码已发送到您的邮箱，请查收"        # message包含标准发送成功信息
                )
        else:
            # return create_error_response 发送失败时返回错误响应
            return create_error_response(
                "邮箱不存在或验证码发送失败",               # error参数设置错误信息
                "SEND_RESET_CODE_ERROR"              # error_type参数设置错误类型
            )
        
    except InvalidInputError as e:
        # except InvalidInputError 捕获输入验证异常
        return create_error_response(str(e), "INVALID_INPUT")
    except Exception as e:
        # except Exception 捕获所有其他发送失败异常
        return create_error_response(
            "发送重置验证码失败",                       # error参数设置错误信息
            "FORGOT_PASSWORD_ERROR"                # error_type参数设置错误类型
        )


async def reset_password_service(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    reset_password_service 处理重置密码业务逻辑的服务函数
    从handle_auth_reset_password迁移而来，负责验证验证码并重置用户密码
    
    参数:
        payload: 包含重置信息的载荷字典，需包含email、code、new_password字段
    
    返回:
        dict: 标准服务响应格式，包含密码重置结果信息
    """
    try:
        # 从载荷中提取密码重置所需信息字段，支持嵌套payload格式
        # 检查是否是hub传递的格式（包含payload字段）
        if "payload" in payload and isinstance(payload["payload"], dict):
            actual_payload = payload["payload"]
        else:
            actual_payload = payload
            
        # email 通过get方法从actual_payload中提取邮箱地址字段
        email = actual_payload.get("email")
        # code 通过get方法提取重置验证码字段
        code = actual_payload.get("code")
        # new_password 通过get方法提取新密码字段
        new_password = actual_payload.get("new_password")
        
        # 验证重置密码请求的必要参数
        # if not email or not code or not new_password 条件检查必要字段是否完整
        if not email or not code or not new_password:
            # return create_error_response 当必要参数缺失时返回错误响应
            return create_error_response(
                "邮箱、验证码和新密码都是必需的",           # error参数设置错误信息
                "MISSING_PARAMETERS"               # error_type参数设置错误类型
            )
        
        # reset_request 通过ResetPasswordRequest构造函数创建重置密码请求对象
        reset_request = ResetPasswordRequest(
            email=email,                           # email字段设置为提取的邮箱地址
            code=code,                             # code字段设置为提取的验证码
            new_password=new_password              # new_password字段设置为提取的新密码
        )
        
        # reset_result 通过reset_password函数执行密码重置业务逻辑
        reset_result = reset_password(
            reset_request.email,                   # email参数传入邮箱地址
            reset_request.code,                    # code参数传入验证码
            reset_request.new_password             # new_password参数传入新密码
        )
        
        # 根据重置结果返回相应响应
        # if reset_result 条件检查重置是否成功
        if reset_result:
            # return create_success_response 重置成功时返回成功响应
            return create_success_response(
                message="密码重置成功！您可以使用新密码登录"      # message参数设置为成功消息
            )
        else:
            # return create_error_response 重置失败时返回错误响应
            return create_error_response(
                "密码重置失败，请检查验证码或重试",            # error参数设置错误信息
                "RESET_PASSWORD_FAILED"                # error_type参数设置错误类型
            )
        
    except InvalidInputError as e:
        # except InvalidInputError 捕获输入验证异常
        return create_error_response(str(e), "INVALID_INPUT")
    except Exception as e:
        # except Exception 捕获所有其他重置失败异常
        return create_error_response(
            "重置密码过程中发生错误",                     # error参数设置错误信息
            "RESET_PASSWORD_ERROR"                   # error_type参数设置错误类型
        )


# ============ 受保护功能相关业务服务函数 ============

async def get_profile_service(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    get_profile_service 处理获取用户信息业务逻辑的服务函数
    从handle_auth_get_profile迁移而来，需要认证后才能访问用户资料信息
    
    参数:
        payload: 包含认证信息的载荷字典，需包含有效的认证token或上下文
    
    返回:
        dict: 标准服务响应格式，成功时包含用户资料信息
    """
    try:
        # current_user 通过extract_auth_info_from_payload或extract_auth_info_from_context提取认证信息
        # 使用 or 逻辑运算符尝试从载荷和上下文中提取认证用户信息
        current_user = extract_auth_info_from_payload(payload) or extract_auth_info_from_context(payload)
        
        # if not current_user 条件检查认证信息是否成功提取
        if not current_user:
            # raise InvalidCredentialsError 当认证信息无效时抛出认证错误异常
            raise InvalidCredentialsError("需要登录才能访问此接口")
        
        # result 通过handle_get_user_profile函数调用受保护的用户资料获取逻辑
        result = handle_get_user_profile(current_user)
        
        # return result 直接返回处理结果（已经是标准格式）
        return result
        
    except InvalidCredentialsError as e:
        # InvalidCredentialsError 直接重新抛出认证错误异常，保持异常类型
        raise e
    except Exception as e:
        # Exception 对于其他异常，包装为系统错误重新抛出
        raise RuntimeError(f"获取用户信息失败: {str(e)}")


async def update_settings_service(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    update_settings_service 处理更新用户设置业务逻辑的服务函数
    从handle_auth_update_settings迁移而来，需要认证后才能修改用户设置信息
    
    参数:
        payload: 包含认证信息和设置数据的载荷字典，需包含有效认证和设置字段
    
    返回:
        dict: 标准服务响应格式，成功时包含更新结果信息
    """
    try:
        # current_user 通过extract_auth_info_from_payload或extract_auth_info_from_context提取认证信息
        # 使用 or 逻辑运算符尝试从载荷和上下文中提取认证用户信息
        current_user = extract_auth_info_from_payload(payload) or extract_auth_info_from_context(payload)
        
        # if not current_user 条件检查认证信息是否成功提取
        if not current_user:
            # return create_error_response 当认证信息无效时返回错误响应
            return create_error_response(
                "需要登录才能访问此接口",                 # error参数设置错误信息
                "AUTHENTICATION_REQUIRED"           # error_type参数设置错误类型
            )
        
        # result 通过handle_update_user_settings函数调用受保护的用户设置更新逻辑
        result = handle_update_user_settings(payload, current_user)
        
        # return result 直接返回处理结果（已经是标准格式）
        return result
        
    except Exception as e:
        # except Exception 捕获所有更新设置失败异常
        return create_error_response(
            "更新用户设置失败",                        # error参数设置错误信息
            "UPDATE_SETTINGS_ERROR"                # error_type参数设置错误类型
        )


async def refresh_token_service(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    refresh_token_service 处理刷新令牌业务逻辑的服务函数
    从handle_auth_refresh_token迁移而来，负责验证refresh_token并生成新的access_token
    
    参数:
        payload: 包含刷新令牌的载荷字典，需包含refresh_token字段
    
    返回:
        dict: 标准服务响应格式，成功时包含新的access_token和refresh_token
    """
    try:
        # result 通过handle_refresh_token函数调用token刷新业务逻辑
        # 直接传入载荷，由业务逻辑函数处理refresh_token提取和验证
        result = handle_refresh_token(payload)
        
        # return result 直接返回处理结果（已经是标准格式）
        return result
        
    except Exception as e:
        # Exception 根据异常类型决定是否抛出业务异常
        error_msg = str(e)
        if "无效" in error_msg or "过期" in error_msg or "invalid" in error_msg.lower():
            # token相关的业务异常，抛出认证错误
            raise InvalidCredentialsError(f"令牌刷新失败: {error_msg}")
        else:
            # 其他系统异常包装为RuntimeError
            raise RuntimeError(f"令牌刷新失败: {error_msg}")


async def logout_service(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    logout_service 处理用户登出业务逻辑的服务函数
    从handle_auth_logout迁移而来，需要认证后才能执行登出操作
    
    参数:
        payload: 包含认证信息的载荷字典，需包含有效的认证token或上下文
    
    返回:
        dict: 标准服务响应格式，成功时包含登出结果信息
    """
    try:
        # current_user 通过extract_auth_info_from_payload或extract_auth_info_from_context提取认证信息
        # 使用 or 逻辑运算符尝试从载荷和上下文中提取认证用户信息
        current_user = extract_auth_info_from_payload(payload) or extract_auth_info_from_context(payload)
        
        # if not current_user 条件检查认证信息是否成功提取
        if not current_user:
            # return create_error_response 当认证信息无效时返回错误响应
            return create_error_response(
                "需要登录才能执行登出操作",                 # error参数设置错误信息
                "AUTHENTICATION_REQUIRED"           # error_type参数设置错误类型
            )
        
        # result 通过handle_logout函数调用受保护的用户登出业务逻辑
        result = handle_logout(current_user)
        
        # return result 直接返回处理结果（已经是标准格式）
        return result
        
    except Exception as e:
        # except Exception 捕获所有登出操作失败异常
        return create_error_response(
            "登出操作失败",                          # error参数设置错误信息
            "LOGOUT_ERROR"                       # error_type参数设置错误类型
        )


# ============ 导出所有业务服务函数 ============

__all__ = [
    # 响应格式化工具函数
    "create_success_response", "create_error_response",
    "extract_auth_info_from_payload", "extract_auth_info_from_context",
    
    # 注册相关业务服务函数  
    "register_service", "send_verification_service",
    "verify_code_service", "set_password_service",
    
    # 登录相关业务服务函数
    "login_service",
    
    # OAuth相关业务服务函数
    "oauth_google_url_service", "oauth_google_callback_service",
    "oauth_facebook_url_service", "oauth_facebook_callback_service",
    
    # 密码重置相关业务服务函数
    "forgot_password_service", "reset_password_service",
    
    # 受保护功能业务服务函数
    "get_profile_service", "update_settings_service",
    "refresh_token_service", "logout_service"
]
