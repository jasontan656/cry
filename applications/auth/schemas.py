# 用户注册相关数据模型定义
# 使用 pydantic.BaseModel 创建具有类型验证的数据结构

from pydantic import BaseModel


class UserRegisterRequest(BaseModel):
    """
    用户注册请求数据模型

    定义注册时客户端需要提供的字段：
    - email: 邮箱地址（同时作为用户名），字符串类型
    - password: 密码，字符串类型
    - test_user: 测试用户标识，布尔类型，默认为False（仅用于开发调试）
    """
    email: str
    password: str
    # test_user 字段通过布尔类型定义，默认赋值为False
    # 该字段仅供开发调试时跳过验证码验证流程使用
    # 生产环境应始终保持为False以确保安全性
    test_user: bool = False


class UserResponse(BaseModel):
    """
    用户认证响应数据模型

    定义登录或注册成功后返回给客户端的信息：
    - user_id: 用户唯一标识符，字符串类型
    - email: 邮箱地址（同时作为用户名），字符串类型
    - access_token: 访问令牌，字符串类型，有效期15分钟
    - refresh_token: 刷新令牌，字符串类型，有效期7天
    - token_type: 令牌类型，默认为"Bearer"
    """
    user_id: str
    email: str
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"


class UserData(BaseModel):
    """
    用户数据模型（内部使用）

    定义存储到user_profiles的用户静态画像信息结构：
    - user_id: 用户唯一标识符，字符串类型
    - username: 用户名（使用邮箱作为用户名），字符串类型
    - email: 邮箱地址，字符串类型
    
    注：动态状态字段（hashed_password、oauth_*_id等）现在存储在user_status集合中
    """
    user_id: str
    username: str  # 使用邮箱作为用户名
    email: str


class SendVerificationRequest(BaseModel):
    """
    发送验证码请求数据模型

    定义发送邮箱验证码时客户端需要提供的字段：
    - email: 需要验证的邮箱地址，字符串类型
    - test_user: 测试用户标识，布尔类型，默认为False（用于开发调试生成固定验证码）
    """
    email: str
    # test_user 字段通过布尔类型定义，默认赋值为False
    # 该字段为True时生成固定验证码123456，仅供开发调试时使用
    # 生产环境应始终保持为False以确保安全性
    test_user: bool = False


class VerifyCodeRequest(BaseModel):
    """
    验证验证码请求数据模型

    定义验证邮箱验证码时客户端需要提供的字段：
    - email: 邮箱地址，字符串类型
    - code: 用户输入的6位数字验证码，字符串类型
    """
    email: str
    code: str


class SetPasswordRequest(BaseModel):
    """
    设置密码请求数据模型

    定义为已验证邮箱设置密码时客户端需要提供的字段：
    - email: 邮箱地址，字符串类型
    - password: 新密码，字符串类型
    """
    email: str
    password: str


class SendVerificationResponse(BaseModel):
    """
    发送验证码响应数据模型

    定义发送验证码成功后返回给客户端的信息：
    - success: 是否发送成功，布尔类型
    - message: 响应消息，字符串类型
    """
    success: bool
    message: str


class VerifyCodeResponse(BaseModel):
    """
    验证验证码响应数据模型

    定义验证码验证结果返回给客户端的信息：
    - success: 是否验证成功，布尔类型
    - message: 响应消息，字符串类型
    - user_exists: 用户是否已存在，布尔类型（用于后续流程判断）
    - is_oauth_user: 是否为OAuth用户，布尔类型
    """
    success: bool
    message: str
    user_exists: bool
    is_oauth_user: bool


class SetPasswordResponse(BaseModel):
    """
    设置密码响应数据模型

    定义设置密码成功后返回给客户端的信息：
    - success: 是否设置成功，布尔类型
    - message: 响应消息，字符串类型
    - user_id: 用户ID（如果创建了新用户），可选字符串类型
    """
    success: bool
    message: str
    user_id: str = None


class ForgotPasswordRequest(BaseModel):
    """
    忘记密码请求数据模型

    定义忘记密码时客户端需要提供的字段：
    - email: 需要重置密码的邮箱地址，字符串类型
    - test_user: 测试用户标识，布尔类型，默认为False（用于开发调试生成固定验证码）
    """
    email: str
    # test_user 字段通过布尔类型定义，默认赋值为False
    # 该字段为True时生成固定重置验证码123456，仅供开发调试时使用
    # 生产环境应始终保持为False以确保安全性
    test_user: bool = False


class VerifyResetCodeRequest(BaseModel):
    """
    验证重置验证码请求数据模型

    定义验证忘记密码验证码时客户端需要提供的字段：
    - email: 邮箱地址，字符串类型
    - code: 用户输入的6位数字验证码，字符串类型
    """
    email: str
    code: str


class ResetPasswordRequest(BaseModel):
    """
    重置密码请求数据模型

    定义重置密码时客户端需要提供的字段：
    - email: 邮箱地址，字符串类型
    - code: 验证码，字符串类型（用于二次验证）
    - new_password: 新密码，字符串类型
    """
    email: str
    code: str
    new_password: str


class RefreshTokenRequest(BaseModel):
    """
    刷新令牌请求数据模型

    定义使用刷新令牌获取新访问令牌时客户端需要提供的字段：
    - refresh_token: 刷新令牌，字符串类型，有效期7天
    """
    refresh_token: str


class UserProfileResponse(BaseModel):
    """
    用户信息响应数据模型

    定义获取用户信息时返回给客户端的数据：
    - user_id: 用户唯一标识符，字符串类型
    - email: 邮箱地址，字符串类型
    - username: 用户名，字符串类型
    - created_at: 创建时间，字符串类型（可选）
    - updated_at: 更新时间，字符串类型（可选）
    """
    user_id: str
    email: str
    username: str
    created_at: str = None
    updated_at: str = None


class UserStatusData(BaseModel):
    """
    用户状态数据模型（内部使用）
    
    定义存储到user_status的用户动态状态信息结构：
    - user_id: 用户唯一标识符，字符串类型
    - hashed_password: 加密后的密码，字符串类型（可选）
    - oauth_google_id: Google OAuth绑定ID，字符串类型（可选）
    - oauth_facebook_id: Facebook OAuth绑定ID，字符串类型（可选）
    """
    user_id: str
    hashed_password: str = None
    oauth_google_id: str = None
    oauth_facebook_id: str = None


class UserSettingsUpdateRequest(BaseModel):
    """
    用户设置更新请求数据模型

    定义更新用户设置时客户端需要提供的字段：
    - email: 新邮箱地址，字符串类型（可选）
    - current_password: 当前密码，字符串类型（验证身份用）
    - new_password: 新密码，字符串类型（可选）
    """
    email: str = None
    current_password: str
    new_password: str = None


class LogoutResponse(BaseModel):
    """
    登出响应数据模型

    定义用户登出时返回给客户端的信息：
    - success: 是否登出成功，布尔类型
    - message: 响应消息，字符串类型
    """
    success: bool
    message: str
