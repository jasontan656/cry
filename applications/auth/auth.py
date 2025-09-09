# 用户认证模块主入口文件
# 提供意图驱动架构下的认证功能统一导出点

# 导入响应格式工具
from .intent_handlers import (
    create_success_response,
    create_error_response,
    extract_auth_info_from_payload,
    extract_auth_info_from_context
)

# 导入流程注册功能
from .intent_registration import (
    auth_register_function,
    validate_flow_registration,
    get_flow_registration_info
)

# 导入流程定义功能  
from .flow_definitions import (
    register_auth_flows,
    get_all_auth_flows,
    validate_all_auth_flows
)

# 导入认证工具
from .auth_middleware import (
    AuthenticatedUser,
    extract_auth_info_from_token,
    create_authenticated_user,
    validate_user_authentication
)

# 导入数据模型（保留用于兼容）
from .schemas import (
    UserRegisterRequest,
    UserResponse,
    SendVerificationRequest,
    SendVerificationResponse, 
    VerifyCodeRequest,
    VerifyCodeResponse,
    SetPasswordRequest,
    SetPasswordResponse
)

# 导入异常类（保留用于兼容）
from .exceptions import (
    UserAlreadyExistsError,
    InvalidInputError,
    InvalidCredentialsError,
    EmailAlreadyRegisteredError
)

# 彻底重构：导出流程驱动架构组件
__all__ = [
    # 标准响应格式化工具
    "create_success_response",
    "create_error_response",
    
    # 认证信息提取工具
    "extract_auth_info_from_payload",
    "extract_auth_info_from_context", 
    "extract_auth_info_from_token",
    
    # 认证用户数据模型和工具
    "AuthenticatedUser",
    "create_authenticated_user",
    "validate_user_authentication",
    
    # 流程注册功能
    "auth_register_function", 
    "validate_flow_registration",
    "get_flow_registration_info",
    
    # 流程定义功能
    "register_auth_flows",
    "get_all_auth_flows",
    "validate_all_auth_flows",
    
    # 数据模型（保留兼容）
    "UserRegisterRequest",
    "UserResponse", 
    "SendVerificationRequest",
    "SendVerificationResponse",
    "VerifyCodeRequest",
    "VerifyCodeResponse",
    "SetPasswordRequest", 
    "SetPasswordResponse",
    
    # 异常类（保留兼容）
    "UserAlreadyExistsError",
    "InvalidInputError",
    "InvalidCredentialsError",
    "EmailAlreadyRegisteredError"
]
