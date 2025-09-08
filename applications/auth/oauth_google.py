# Google OAuth 登录模块
# 实现 Google 第三方登录认证流程

import secrets
from config import oauth_settings
from .oauth_utils import construct_oauth_url, exchange_code_for_token, get_user_info, validate_oauth_state
from .tokens import generate_access_token
from .repository import check_user_exists, create_user
from .schemas import UserResponse


def get_google_auth_url(state: str = None) -> str:
    """
    生成 Google OAuth 授权 URL

    构造 Google OAuth 授权请求 URL，用户点击后跳转到 Google 登录页面。

    参数:
        state: 可选的随机状态字符串，用于防止 CSRF 攻击

    返回:
        str: Google OAuth 授权 URL 字符串
    """
    # 如果没有提供 state 参数，生成一个随机状态字符串
    if not state:
        state = secrets.token_urlsafe(32)

    # Google OAuth 端点 URL
    google_auth_endpoint = "https://accounts.google.com/o/oauth2/v2/auth"

    # 请求的权限范围：获取用户基本信息和邮箱
    scope = "openid email profile"

    # 调用 construct_oauth_url 函数构造授权 URL
    # 传入 Google 授权端点 google_auth_endpoint、客户端 ID、回调 URI、权限范围 scope 和状态 state
    # 得到构造完成的授权 URL，赋值给 auth_url
    auth_url = construct_oauth_url(
        auth_endpoint=google_auth_endpoint,
        client_id=oauth_settings.google_client_id,
        redirect_uri=oauth_settings.oauth_redirect_uri,
        scope=scope,
        state=state
    )

    # 返回生成的授权 URL
    return auth_url


def login_with_google(code: str, state: str, expected_state: str = None) -> UserResponse:
    """
    使用 Google OAuth 授权码完成登录

    通过授权码交换访问令牌，获取用户信息，在系统中创建或更新用户记录。

    参数:
        code: 从 Google 回调获得的授权码
        state: 从回调中接收到的 state 参数
        expected_state: 预期的 state 值，用于验证

    返回:
        UserResponse: 登录成功的用户信息对象

    异常:
        ValueError: state 验证失败或 OAuth 流程失败
    """
    # 如果提供了预期 state，进行验证
    if expected_state and not validate_oauth_state(expected_state, state):
        raise ValueError("Invalid state parameter")

    # Google OAuth 令牌端点
    google_token_endpoint = "https://oauth2.googleapis.com/token"

    # 调用 exchange_code_for_token 函数交换授权码为访问令牌
    # 传入 Google 令牌端点 google_token_endpoint、客户端 ID、客户端密钥、授权码 code 和回调 URI
    # 得到令牌数据字典，赋值给 token_data
    token_data = exchange_code_for_token(
        token_endpoint=google_token_endpoint,
        client_id=oauth_settings.google_client_id,
        client_secret=oauth_settings.google_client_secret,
        code=code,
        redirect_uri=oauth_settings.oauth_redirect_uri
    )

    # 从令牌数据中提取访问令牌
    access_token = token_data.get("access_token")

    # Google 用户信息端点
    google_userinfo_endpoint = "https://www.googleapis.com/oauth2/v2/userinfo"

    # 调用 get_user_info 函数获取用户信息
    # 传入 Google 用户信息端点 google_userinfo_endpoint 和访问令牌 access_token
    # 得到用户信息字典，赋值给 user_info
    user_info = get_user_info(google_userinfo_endpoint, access_token)

    # 从用户信息中提取 Google 用户 ID、邮箱和姓名
    google_id = user_info.get("id")
    email = user_info.get("email")
    name = user_info.get("name", "")

    # 使用邮箱作为用户名（这是新的设计）
    username = email

    # 检查用户是否已存在（通过邮箱检查）
    user_exists = check_user_exists(email)

    # 如果用户不存在，创建新用户（OAuth用户）
    if not user_exists:
        # 生成一个随机密码（第三方登录不需要实际密码）
        from .hashing import hash_password
        dummy_password = hash_password(secrets.token_urlsafe(32))

        # 创建新用户，传入用户名（邮箱）username、邮箱 email 和虚拟密码 dummy_password
        # 得到新创建用户的 user_id
        user_id = create_user(username, email, dummy_password)

        # 为新创建的OAuth用户绑定Google账户信息
        # Google ID存储到user_status集合中
        try:
            link_oauth_to_existing_email(email, "google", google_id)
        except ValueError:
            # 绑定失败，忽略错误继续登录
            pass
    else:
        # 如果用户已存在，需要检查是否需要绑定OAuth账户
        from .repository import get_user_by_username, link_oauth_to_existing_email
        existing_user = get_user_by_username(username)
        user_id = existing_user["user_id"]

        # 尝试绑定Google OAuth账户到现有用户
        # 如果绑定失败（比如已经绑定过），忽略错误继续登录
        try:
            link_oauth_to_existing_email(email, "google", google_id)
        except ValueError:
            # 绑定失败，可能是因为已经绑定过相同账户，忽略错误
            pass

    # 调用 generate_access_token 函数生成访问令牌
    # 传入用户ID user_id 和用户名（邮箱）username
    # 得到生成的令牌字符串，赋值给 jwt_token
    jwt_token = generate_access_token(user_id, username)

    # 创建 UserResponse 对象，包含登录成功后的用户信息
    return UserResponse(
        user_id=user_id,
        email=email
    )
