# 意图处理器工厂模块
# 实现符合双层意图驱动架构的所有认证意图处理函数

import asyncio
from typing import Dict, Any, Optional
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


# 意图处理器通用工具函数

def create_success_response(data: Any = None, message: str = "操作成功") -> Dict[str, Any]:
    """
    创建标准成功响应格式
    
    参数:
        data: 响应数据，可以是任何可序列化的对象
        message: 成功消息字符串
    
    返回:
        dict: 标准成功响应格式字典
    """
    # 构建标准成功响应结构
    response = {
        "success": True,
        "message": message
    }
    
    # 如果有数据，添加到响应中
    if data is not None:
        response["data"] = data
    
    return response


def create_error_response(error: str, error_type: str = "UNKNOWN_ERROR", details: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    创建标准错误响应格式
    
    参数:
        error: 错误信息字符串
        error_type: 错误类型标识字符串
        details: 额外的错误详情字典
    
    返回:
        dict: 标准错误响应格式字典
    """
    # 构建标准错误响应结构
    response = {
        "success": False,
        "error": error,
        "error_type": error_type
    }
    
    # 如果有详情，添加到响应中
    if details is not None:
        response["details"] = details
    
    return response


def extract_auth_info_from_payload(payload: Dict[str, Any]) -> Optional[AuthenticatedUser]:
    """
    从payload中提取认证信息
    
    参数:
        payload: 意图载荷字典，可能包含认证令牌
    
    返回:
        AuthenticatedUser对象或None: 如果认证成功返回用户对象，否则返回None
    """
    try:
        # 从payload中提取Authorization头部或access_token字段
        auth_header = payload.get("Authorization") or payload.get("access_token")
        
        if not auth_header:
            return None
            
        # 处理Bearer令牌格式
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]  # 跳过"Bearer "前缀
        else:
            token = auth_header
        
        # 验证JWT令牌
        payload_data = verify_access_token(token)
        
        # 提取用户信息
        user_id = payload_data.get("user_id")
        username = payload_data.get("username")
        token_type = payload_data.get("type")
        
        # 验证令牌类型和必要字段
        if not user_id or not username or token_type != "access_token":
            return None
        
        # 从数据库获取用户完整信息
        user_data = get_user_by_username(username)
        
        if not user_data:
            return None
        
        # 创建认证用户对象
        email = user_data.get("email", username)
        return AuthenticatedUser(
            user_id=user_id,
            username=username,
            email=email
        )
        
    except (ValueError, Exception):
        return None


def extract_auth_info_from_context(context: Dict[str, Any]) -> Optional[AuthenticatedUser]:
    """
    从context中提取认证信息
    
    参数:
        context: 意图上下文字典，可能包含用户认证信息
    
    返回:
        AuthenticatedUser对象或None: 如果认证信息存在返回用户对象，否则返回None
    """
    try:
        # 检查context中是否有认证标识
        if not context.get("authenticated", False):
            return None
        
        # 从context中提取用户信息
        user_id = context.get("user_id")
        username = context.get("username")
        email = context.get("email")
        
        # 验证必要字段
        if not user_id or not username:
            return None
        
        # 创建认证用户对象
        return AuthenticatedUser(
            user_id=user_id,
            username=username,
            email=email or username
        )
        
    except Exception:
        return None


# 注册相关意图处理器

async def handle_auth_register(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    处理用户注册意图
    
    参数:
        payload: 包含注册信息的载荷字典 (email, password, test_user)
        context: 意图上下文字典
    
    返回:
        dict: 标准意图响应格式
    """
    try:
        # 从payload中提取注册信息
        email = payload.get("email")
        password = payload.get("password")
        test_user = payload.get("test_user", False)
        
        # 验证必要参数
        if not email or not password:
            return create_error_response(
                "邮箱和密码都是必需的",
                "MISSING_PARAMETERS"
            )
        
        # 创建注册请求对象
        register_request = UserRegisterRequest(
            email=email,
            password=password,
            test_user=test_user
        )
        
        # 调用注册函数
        result = register_user(register_request)
        
        # 返回成功响应
        return create_success_response(
            data=result.model_dump(),
            message="注册成功"
        )
        
    except InvalidInputError as e:
        return create_error_response(str(e), "INVALID_INPUT")
    except UserAlreadyExistsError as e:
        return create_error_response(str(e), "USER_EXISTS")
    except EmailAlreadyRegisteredError as e:
        return create_error_response(str(e), "EMAIL_ALREADY_REGISTERED")
    except Exception as e:
        return create_error_response(
            "注册过程中发生未知错误",
            "UNKNOWN_ERROR"
        )


async def handle_auth_send_verification(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    处理发送验证码意图
    
    参数:
        payload: 包含邮箱信息的载荷字典 (email, test_user)
        context: 意图上下文字典
    
    返回:
        dict: 标准意图响应格式
    """
    try:
        # 从payload中提取邮箱和测试用户标识
        email = payload.get("email")
        test_user = payload.get("test_user", False)
        
        # 验证必要参数
        if not email:
            return create_error_response(
                "邮箱参数是必需的",
                "MISSING_EMAIL"
            )
        
        # 创建发送验证码请求对象
        send_request = SendVerificationRequest(email=email, test_user=test_user)
        
        # 异步调用发送验证码函数
        result = await send_verification_code_to_email(send_request)
        
        # 返回响应
        return create_success_response(
            data={"success": result.success, "message": result.message},
            message=result.message
        )
        
    except EmailAlreadyRegisteredError as e:
        return create_error_response(str(e), "EMAIL_ALREADY_REGISTERED")
    except Exception as e:
        return create_error_response(
            "发送验证码失败",
            "SEND_CODE_ERROR"
        )


async def handle_auth_verify_code(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    处理验证码验证意图
    
    参数:
        payload: 包含验证码信息的载荷字典 (email, code)
        context: 意图上下文字典
    
    返回:
        dict: 标准意图响应格式
    """
    try:
        # 从payload中提取邮箱和验证码
        email = payload.get("email")
        code = payload.get("code")
        
        # 验证必要参数
        if not email or not code:
            return create_error_response(
                "邮箱和验证码都是必需的",
                "MISSING_PARAMETERS"
            )
        
        # 创建验证码验证请求对象
        verify_request = VerifyCodeRequest(email=email, code=code)
        
        # 调用验证码验证函数
        result = verify_email_code(verify_request)
        
        # 返回响应
        return create_success_response(
            data={
                "success": result.success,
                "message": result.message,
                "user_exists": result.user_exists,
                "is_oauth_user": result.is_oauth_user
            },
            message=result.message
        )
        
    except Exception as e:
        return create_error_response(
            "验证码验证失败",
            "VERIFY_CODE_ERROR"
        )


async def handle_auth_set_password(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    处理设置密码意图
    
    参数:
        payload: 包含密码信息的载荷字典 (email, password)
        context: 意图上下文字典
    
    返回:
        dict: 标准意图响应格式
    """
    try:
        # 从payload中提取邮箱和密码
        email = payload.get("email")
        password = payload.get("password")
        
        # 验证必要参数
        if not email or not password:
            return create_error_response(
                "邮箱和密码都是必需的",
                "MISSING_PARAMETERS"
            )
        
        # 创建设置密码请求对象
        set_password_request = SetPasswordRequest(email=email, password=password)
        
        # 调用设置密码函数
        result = set_user_password_after_verification(set_password_request)
        
        # 构建响应数据
        response_data = {
            "success": result.success,
            "message": result.message
        }
        
        # 如果创建了新用户，包含user_id
        if result.user_id:
            response_data["user_id"] = result.user_id
        
        return create_success_response(
            data=response_data,
            message=result.message
        )
        
    except Exception as e:
        return create_error_response(
            "设置密码失败",
            "SET_PASSWORD_ERROR"
        )


# 登录相关意图处理器

async def handle_auth_login(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    处理用户登录意图
    
    参数:
        payload: 包含登录信息的载荷字典 (email, password)
        context: 意图上下文字典
    
    返回:
        dict: 标准意图响应格式
    """
    try:
        # 从payload中提取邮箱和密码
        email = payload.get("email")
        password = payload.get("password")
        
        # 验证必要参数
        if not email or not password:
            return create_error_response(
                "邮箱和密码都是必需的",
                "MISSING_PARAMETERS"
            )
        
        # 调用登录函数
        result = login_user(email, password)
        
        # 返回成功响应
        return create_success_response(
            data=result.model_dump(),
            message="登录成功"
        )
        
    except InvalidCredentialsError as e:
        return create_error_response(str(e), "INVALID_CREDENTIALS")
    except Exception as e:
        return create_error_response(
            "登录过程中发生未知错误",
            "UNKNOWN_ERROR"
        )


# OAuth相关意图处理器

async def handle_auth_oauth_google_url(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    处理Google OAuth授权URL生成意图
    
    参数:
        payload: 包含OAuth参数的载荷字典 (state)
        context: 意图上下文字典
    
    返回:
        dict: 标准意图响应格式
    """
    try:
        # 从payload中提取state参数
        state = payload.get("state")
        
        # 调用Google OAuth函数生成授权URL
        auth_url = get_google_auth_url(state)
        
        # 返回成功响应
        return create_success_response(
            data={
                "auth_url": auth_url,
                "provider": "google"
            },
            message="Google授权URL生成成功"
        )
        
    except Exception as e:
        return create_error_response(
            "生成Google授权URL失败",
            "OAUTH_URL_GENERATION_ERROR"
        )


async def handle_auth_oauth_google_callback(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    处理Google OAuth回调意图
    
    参数:
        payload: 包含OAuth回调参数的载荷字典 (code, state, expected_state)
        context: 意图上下文字典
    
    返回:
        dict: 标准意图响应格式
    """
    try:
        # 从payload中提取回调参数
        code = payload.get("code")
        state = payload.get("state")
        expected_state = payload.get("expected_state")
        
        # 验证必要参数
        if not code:
            return create_error_response(
                "缺少授权码参数",
                "MISSING_CODE"
            )
        
        # 调用Google OAuth回调函数完成登录
        result = login_with_google(code, state, expected_state)
        
        # 返回成功响应
        return create_success_response(
            data=result.model_dump(),
            message="Google登录成功"
        )
        
    except ValueError as e:
        return create_error_response(str(e), "OAUTH_VALIDATION_ERROR")
    except Exception as e:
        return create_error_response(
            "Google OAuth回调处理失败",
            "OAUTH_CALLBACK_ERROR"
        )


async def handle_auth_oauth_facebook_url(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    处理Facebook OAuth授权URL生成意图
    
    参数:
        payload: 包含OAuth参数的载荷字典 (state)
        context: 意图上下文字典
    
    返回:
        dict: 标准意图响应格式
    """
    try:
        # 从payload中提取state参数
        state = payload.get("state")
        
        # 调用Facebook OAuth函数生成授权URL
        auth_url = get_facebook_auth_url(state)
        
        # 返回成功响应
        return create_success_response(
            data={
                "auth_url": auth_url,
                "provider": "facebook"
            },
            message="Facebook授权URL生成成功"
        )
        
    except Exception as e:
        return create_error_response(
            "生成Facebook授权URL失败",
            "OAUTH_URL_GENERATION_ERROR"
        )


async def handle_auth_oauth_facebook_callback(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    处理Facebook OAuth回调意图
    
    参数:
        payload: 包含OAuth回调参数的载荷字典 (code, state, expected_state)
        context: 意图上下文字典
    
    返回:
        dict: 标准意图响应格式
    """
    try:
        # 从payload中提取回调参数
        code = payload.get("code")
        state = payload.get("state")
        expected_state = payload.get("expected_state")
        
        # 验证必要参数
        if not code:
            return create_error_response(
                "缺少授权码参数",
                "MISSING_CODE"
            )
        
        # 调用Facebook OAuth回调函数完成登录
        result = login_with_facebook(code, state, expected_state)
        
        # 返回成功响应
        return create_success_response(
            data=result.model_dump(),
            message="Facebook登录成功"
        )
        
    except ValueError as e:
        return create_error_response(str(e), "OAUTH_VALIDATION_ERROR")
    except Exception as e:
        return create_error_response(
            "Facebook OAuth回调处理失败",
            "OAUTH_CALLBACK_ERROR"
        )


# 密码重置相关意图处理器

async def handle_auth_forgot_password(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    处理忘记密码意图
    
    参数:
        payload: 包含邮箱信息的载荷字典 (email, test_user)
        context: 意图上下文字典
    
    返回:
        dict: 标准意图响应格式
    """
    try:
        # 从payload中提取邮箱和测试用户标识
        email = payload.get("email")
        test_user = payload.get("test_user", False)
        
        # 验证必要参数
        if not email:
            return create_error_response(
                "邮箱参数是必需的",
                "MISSING_EMAIL"
            )
        
        # 创建忘记密码请求对象
        forgot_request = ForgotPasswordRequest(email=email, test_user=test_user)
        
        # 异步调用发送重置验证码函数
        send_result = await send_reset_code(forgot_request.email, is_test_user=forgot_request.test_user)
        
        # 根据发送结果返回相应响应
        if send_result:
            if test_user:
                return create_success_response(
                    message="测试重置验证码已发送到您的邮箱，固定验证码：123456"
                )
            else:
                return create_success_response(
                    message="密码重置验证码已发送到您的邮箱，请查收"
                )
        else:
            return create_error_response(
                "邮箱不存在或验证码发送失败",
                "SEND_RESET_CODE_ERROR"
            )
        
    except InvalidInputError as e:
        return create_error_response(str(e), "INVALID_INPUT")
    except Exception as e:
        return create_error_response(
            "发送重置验证码失败",
            "FORGOT_PASSWORD_ERROR"
        )


async def handle_auth_reset_password(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    处理重置密码意图
    
    参数:
        payload: 包含重置信息的载荷字典 (email, code, new_password)
        context: 意图上下文字典
    
    返回:
        dict: 标准意图响应格式
    """
    try:
        # 从payload中提取邮箱、验证码和新密码
        email = payload.get("email")
        code = payload.get("code")
        new_password = payload.get("new_password")
        
        # 验证必要参数
        if not email or not code or not new_password:
            return create_error_response(
                "邮箱、验证码和新密码都是必需的",
                "MISSING_PARAMETERS"
            )
        
        # 创建重置密码请求对象
        reset_request = ResetPasswordRequest(
            email=email,
            code=code,
            new_password=new_password
        )
        
        # 调用重置密码函数
        reset_result = reset_password(
            reset_request.email,
            reset_request.code,
            reset_request.new_password
        )
        
        # 根据重置结果返回相应响应
        if reset_result:
            return create_success_response(
                message="密码重置成功！您可以使用新密码登录"
            )
        else:
            return create_error_response(
                "密码重置失败，请检查验证码或重试",
                "RESET_PASSWORD_FAILED"
            )
        
    except InvalidInputError as e:
        return create_error_response(str(e), "INVALID_INPUT")
    except Exception as e:
        return create_error_response(
            "重置密码过程中发生错误",
            "RESET_PASSWORD_ERROR"
        )


# 受保护功能相关意图处理器

async def handle_auth_get_profile(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    处理获取用户信息意图（需要认证）
    
    参数:
        payload: 包含认证信息的载荷字典
        context: 意图上下文字典
    
    返回:
        dict: 标准意图响应格式
    """
    try:
        # 从payload或context中提取认证信息
        current_user = extract_auth_info_from_payload(payload) or extract_auth_info_from_context(context)
        
        if not current_user:
            return create_error_response(
                "需要登录才能访问此接口",
                "AUTHENTICATION_REQUIRED"
            )
        
        # 调用受保护路由处理函数
        result = handle_get_user_profile(current_user)
        
        # 直接返回处理结果（已经是标准格式）
        return result
        
    except Exception as e:
        return create_error_response(
            "获取用户信息失败",
            "GET_PROFILE_ERROR"
        )


async def handle_auth_update_settings(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    处理更新用户设置意图（需要认证）
    
    参数:
        payload: 包含认证信息和设置数据的载荷字典
        context: 意图上下文字典
    
    返回:
        dict: 标准意图响应格式
    """
    try:
        # 从payload或context中提取认证信息
        current_user = extract_auth_info_from_payload(payload) or extract_auth_info_from_context(context)
        
        if not current_user:
            return create_error_response(
                "需要登录才能访问此接口",
                "AUTHENTICATION_REQUIRED"
            )
        
        # 调用受保护路由处理函数
        result = handle_update_user_settings(payload, current_user)
        
        # 直接返回处理结果（已经是标准格式）
        return result
        
    except Exception as e:
        return create_error_response(
            "更新用户设置失败",
            "UPDATE_SETTINGS_ERROR"
        )


async def handle_auth_refresh_token(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    处理刷新令牌意图
    
    参数:
        payload: 包含刷新令牌的载荷字典 (refresh_token)
        context: 意图上下文字典
    
    返回:
        dict: 标准意图响应格式
    """
    try:
        # 调用受保护路由处理函数
        result = handle_refresh_token(payload)
        
        # 直接返回处理结果（已经是标准格式）
        return result
        
    except Exception as e:
        return create_error_response(
            "令牌刷新失败",
            "TOKEN_REFRESH_ERROR"
        )


async def handle_auth_logout(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    处理用户登出意图（需要认证）
    
    参数:
        payload: 包含认证信息的载荷字典
        context: 意图上下文字典
    
    返回:
        dict: 标准意图响应格式
    """
    try:
        # 从payload或context中提取认证信息
        current_user = extract_auth_info_from_payload(payload) or extract_auth_info_from_context(context)
        
        if not current_user:
            return create_error_response(
                "需要登录才能执行登出操作",
                "AUTHENTICATION_REQUIRED"
            )
        
        # 调用受保护路由处理函数
        result = handle_logout(current_user)
        
        # 直接返回处理结果（已经是标准格式）
        return result
        
    except Exception as e:
        return create_error_response(
            "登出操作失败",
            "LOGOUT_ERROR"
        )


# ============ 旧架构清理完成 ============
# 
# 注意：INTENT_HANDLERS字典已删除，完成flow_registry架构迁移
# 
# 迁移说明：
# - 所有业务逻辑函数已迁移到services.py
# - 所有流程注册已转移到flow_definitions.py  
# - 旧的意图映射机制已被flow_registry替代
# 
# 如需使用认证功能，请通过以下方式：
# - 单步流程: 使用auth_login、auth_logout等新的意图标识
# - 多步流程: 使用register_step1/2/3、reset_step1/2等流程标识
# - 业务逻辑: 导入applications.auth.services中的对应函数
# 
# ============ 旧架构清理完成 ============


# 导出所有意图处理器函数
__all__ = [
    # 工具函数
    "create_success_response", "create_error_response",
    "extract_auth_info_from_payload", "extract_auth_info_from_context",
    
    # 注册相关意图处理器
    "handle_auth_register", "handle_auth_send_verification",
    "handle_auth_verify_code", "handle_auth_set_password",
    
    # 登录相关意图处理器
    "handle_auth_login",
    
    # OAuth相关意图处理器
    "handle_auth_oauth_google_url", "handle_auth_oauth_google_callback",
    "handle_auth_oauth_facebook_url", "handle_auth_oauth_facebook_callback",
    
    # 密码重置相关意图处理器
    "handle_auth_forgot_password", "handle_auth_reset_password",
    
    # 受保护功能意图处理器
    "handle_auth_get_profile", "handle_auth_update_settings",
    "handle_auth_refresh_token", "handle_auth_logout"
    
    # 注意：INTENT_HANDLERS映射已删除，请使用services.py中的对应函数
]
