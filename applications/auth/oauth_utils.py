# OAuth 通用工具函数模块
# 封装 OAuth2 认证流程中的通用工具函数

import requests
from typing import Dict, Any, Optional
from urllib.parse import urlencode


def construct_oauth_url(auth_endpoint: str, client_id: str, redirect_uri: str, scope: str, state: Optional[str] = None) -> str:
    """
    构造 OAuth 授权 URL

    根据 OAuth2 标准构造第三方平台的授权请求 URL。
    用于生成用户点击跳转到第三方平台的链接。

    参数:
        auth_endpoint: OAuth 授权端点 URL
        client_id: 客户端 ID
        redirect_uri: 回调 URI
        scope: 请求的权限范围
        state: 随机状态字符串，用于防止 CSRF 攻击

    返回:
        str: 构造完成的授权 URL 字符串
    """
    # 构建基础参数字典
    params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'scope': scope,
        'response_type': 'code',
        'access_type': 'offline'  # 请求离线访问以获取 refresh_token
    }

    # 如果提供了 state 参数，添加到参数字典中
    if state:
        params['state'] = state

    # 使用 urlencode() 对参数字典进行 URL 编码
    # 得到编码后的查询字符串，赋值给 query_string
    query_string = urlencode(params)

    # 将授权端点和查询字符串拼接成完整的 URL
    full_url = f"{auth_endpoint}?{query_string}"

    # 返回构造完成的授权 URL
    return full_url


def exchange_code_for_token(token_endpoint: str, client_id: str, client_secret: str, code: str, redirect_uri: str) -> Dict[str, Any]:
    """
    将授权码交换为访问令牌

    通过 OAuth2 授权码流程，将从第三方平台获得的授权码交换为访问令牌。
    发送 POST 请求到令牌端点，包含必要的认证信息。

    参数:
        token_endpoint: OAuth 令牌端点 URL
        client_id: 客户端 ID
        client_secret: 客户端密钥
        code: 从第三方平台获得的授权码
        redirect_uri: 回调 URI

    返回:
        dict: 令牌响应数据字典，包含 access_token, refresh_token 等

    异常:
        requests.HTTPError: HTTP 请求失败
    """
    # 构建令牌请求的数据
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
        'client_id': client_id,
        'client_secret': client_secret
    }

    # 构建请求头，指定内容类型为表单数据
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    # 发送 POST 请求到令牌端点
    # 传入令牌端点 URL token_endpoint、请求头 headers 和数据 data
    # 得到响应对象，赋值给 response
    response = requests.post(token_endpoint, headers=headers, data=data)

    # 检查响应状态码，如果不是 200 系列，抛出 HTTPError 异常
    response.raise_for_status()

    # 解析响应 JSON 数据
    token_data = response.json()

    # 返回令牌数据字典
    return token_data


def get_user_info(info_endpoint: str, access_token: str) -> Dict[str, Any]:
    """
    获取用户信息

    使用访问令牌从第三方平台的用户信息端点获取用户基本信息。
    通常在 OAuth 流程完成后调用，用于获取用户的公开信息。

    参数:
        info_endpoint: 用户信息端点 URL
        access_token: 访问令牌字符串

    返回:
        dict: 用户信息数据字典，包含用户的基本资料信息

    异常:
        requests.HTTPError: HTTP 请求失败
    """
    # 构建请求头，包含访问令牌的 Authorization 字段
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    # 发送 GET 请求到用户信息端点
    # 传入用户信息端点 URL info_endpoint 和请求头 headers
    # 得到响应对象，赋值给 response
    response = requests.get(info_endpoint, headers=headers)

    # 检查响应状态码，如果不是 200 系列，抛出 HTTPError 异常
    response.raise_for_status()

    # 解析响应 JSON 数据
    user_info = response.json()

    # 返回用户信息字典
    return user_info


def validate_oauth_state(expected_state: str, received_state: str) -> bool:
    """
    验证 OAuth 状态参数

    验证从第三方平台回调返回的 state 参数是否与预期值匹配。
    用于防止 CSRF 攻击，确保回调请求的合法性。

    参数:
        expected_state: 预期的 state 值
        received_state: 从回调中接收到的 state 值

    返回:
        bool: 状态验证结果，匹配返回 True，否则返回 False
    """
    # 比较预期状态和接收状态是否相等
    return expected_state == received_state
