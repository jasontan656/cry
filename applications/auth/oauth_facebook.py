# Facebook OAuth 登录模块
# 实现 Facebook 第三方登录认证流程

import secrets
from config import oauth_settings
from .oauth_utils import construct_oauth_url, exchange_code_for_token, get_user_info, validate_oauth_state
from .tokens import generate_access_token
from .repository import check_user_exists, create_user
from .schemas import UserResponse


def get_facebook_auth_url(state: str = None) -> str:
    """
    生成 Facebook OAuth 授权 URL

    构造 Facebook OAuth 授权请求 URL，用户点击后跳转到 Facebook 登录页面。

    参数:
        state: 可选的随机状态字符串，用于防止 CSRF 攻击

    返回:
        str: Facebook OAuth 授权 URL 字符串
    """
    # 如果没有提供 state 参数，生成一个随机状态字符串
    if not state:
        state = secrets.token_urlsafe(32)

    # Facebook OAuth 授权端点 URL
    facebook_auth_endpoint = "https://www.facebook.com/v18.0/dialog/oauth"

    # 请求的权限范围：获取用户基本信息和邮箱
    scope = "email,public_profile"

    # 调用 construct_oauth_url 函数构造授权 URL
    # 传入 Facebook 授权端点 facebook_auth_endpoint、客户端 ID、回调 URI、权限范围 scope 和状态 state
    # 得到构造完成的授权 URL，赋值给 auth_url
    auth_url = construct_oauth_url(
        auth_endpoint=facebook_auth_endpoint,
        client_id=oauth_settings.facebook_client_id,
        redirect_uri=oauth_settings.oauth_redirect_uri,
        scope=scope,
        state=state
    )

    # 返回生成的授权 URL
    return auth_url


def login_with_facebook(code: str, state: str, expected_state: str = None) -> UserResponse:
    """
    使用 Facebook OAuth 授权码完成登录

    通过授权码交换访问令牌，获取用户信息，在系统中创建或更新用户记录。

    参数:
        code: 从 Facebook 回调获得的授权码
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

    # Facebook OAuth 令牌端点
    facebook_token_endpoint = "https://graph.facebook.com/v18.0/oauth/access_token"

    # 调用 exchange_code_for_token 函数交换授权码为访问令牌
    # 传入 Facebook 令牌端点 facebook_token_endpoint、客户端 ID、客户端密钥、授权码 code 和回调 URI
    # 得到令牌数据字典，赋值给 token_data
    token_data = exchange_code_for_token(
        token_endpoint=facebook_token_endpoint,
        client_id=oauth_settings.facebook_client_id,
        client_secret=oauth_settings.facebook_client_secret,
        code=code,
        redirect_uri=oauth_settings.oauth_redirect_uri
    )

    # 从令牌数据中提取访问令牌
    access_token = token_data.get("access_token")

    # Facebook 用户信息端点
    facebook_userinfo_endpoint = "https://graph.facebook.com/me"

    # 构建用户信息请求参数，指定需要的字段
    params = {
        "fields": "id,name,email",
        "access_token": access_token
    }

    # 调用 get_user_info 函数获取用户信息
    # 传入 Facebook 用户信息端点 facebook_userinfo_endpoint 和访问令牌 access_token
    # 注意：Facebook 需要在 URL 中传递参数，所以这里需要特殊处理
    user_info = get_user_info(f"{facebook_userinfo_endpoint}?fields=id,name,email", access_token)

    # 从用户信息中提取 Facebook 用户 ID、邮箱和姓名
    facebook_id = user_info.get("id")
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
    else:
        # 如果用户已存在，需要检查是否需要绑定OAuth账户
        from .repository import get_user_by_username, link_oauth_to_existing_email
        existing_user = get_user_by_username(username)
        user_id = existing_user["user_id"]

        # 尝试绑定Facebook OAuth账户到现有用户
        # 如果绑定失败（比如已经绑定过），忽略错误继续登录
        try:
            link_oauth_to_existing_email(email, "facebook", facebook_id)
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
