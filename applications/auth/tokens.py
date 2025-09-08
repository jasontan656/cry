# 登录令牌生成模块
# 使用 JWT 生成和管理用户登录后的访问令牌

import jwt
import os
from datetime import timedelta
from typing import Dict, Any
from utilities.time import Time


def generate_access_token(user_id: str, username: str, expires_minutes: int = 15) -> str:
    """
    生成用户访问令牌

    使用 JWT 标准创建用户登录后的访问令牌，包含用户基本信息和过期时间。
    令牌默认有效期为15分钟。

    参数:
        user_id: 用户唯一标识符字符串
        username: 用户名字符串
        expires_minutes: 令牌有效期分钟数，默认为15分钟

    返回:
        str: 生成的 JWT 访问令牌字符串
    """
    # os.getenv() 通过调用获取环境变量 JWT_SECRET_KEY 的值
    # 如果环境变量不存在则使用默认值 'your-secret-key-here'
    # 赋值给 secret_key 变量存储JWT密钥
    secret_key = os.getenv('JWT_SECRET_KEY', 'your-secret-key-here')

    # Time.now() 通过调用获取当前标准时间（UTC+8）
    # 使用系统统一的时间工具确保时区处理一致性
    # 赋值给 current_time 变量存储当前时间
    current_time = Time.now()
    
    # current_time + timedelta() 通过时间加法计算令牌过期时间
    # 传入 expires_minutes 参数创建分钟数时间差对象
    # 赋值给 expire 变量存储过期时间
    expire = current_time + timedelta(minutes=expires_minutes)

    # to_encode 通过字典创建令牌载荷数据
    # "user_id" 键赋值为用户ID字符串
    # "username" 键赋值为用户名字符串
    # "exp" 键通过 expire.timestamp() 获取过期时间戳
    # "iat" 键通过 current_time.timestamp() 获取签发时间戳
    # "type" 键赋值为 "access_token" 标识令牌类型
    to_encode = {
        "user_id": user_id,
        "username": username,
        "exp": expire.timestamp(),
        "iat": current_time.timestamp(),
        "type": "access_token"
    }

    # jwt.encode() 通过调用编码JWT令牌
    # 传入载荷数据 to_encode、密钥 secret_key 和算法 "HS256"
    # 得到编码后的令牌字符串，赋值给 encoded_jwt 变量
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm="HS256")

    # return 语句返回生成的JWT令牌字符串
    return encoded_jwt


def generate_refresh_token(user_id: str, username: str, expires_days: int = 7) -> str:
    """
    生成用户刷新令牌

    使用 JWT 标准创建用户的刷新令牌，用于获取新的访问令牌。
    令牌默认有效期为7天。

    参数:
        user_id: 用户唯一标识符字符串
        username: 用户名字符串
        expires_days: 令牌有效期天数，默认为7天

    返回:
        str: 生成的 JWT 刷新令牌字符串
    """
    # os.getenv() 通过调用获取环境变量 JWT_SECRET_KEY 的值
    # 如果环境变量不存在则使用默认值 'your-secret-key-here'
    # 赋值给 secret_key 变量存储JWT密钥
    secret_key = os.getenv('JWT_SECRET_KEY', 'your-secret-key-here')

    # Time.now() 通过调用获取当前标准时间（UTC+8）
    # 使用系统统一的时间工具确保时区处理一致性
    # 赋值给 current_time 变量存储当前时间
    current_time = Time.now()
    
    # current_time + timedelta() 通过时间加法计算令牌过期时间
    # 传入 expires_days 参数创建天数时间差对象
    # 赋值给 expire 变量存储过期时间
    expire = current_time + timedelta(days=expires_days)

    # to_encode 通过字典创建令牌载荷数据
    # "user_id" 键赋值为用户ID字符串
    # "username" 键赋值为用户名字符串
    # "exp" 键通过 expire.timestamp() 获取过期时间戳
    # "iat" 键通过 current_time.timestamp() 获取签发时间戳
    # "type" 键赋值为 "refresh_token" 标识令牌类型
    to_encode = {
        "user_id": user_id,
        "username": username,
        "exp": expire.timestamp(),
        "iat": current_time.timestamp(),
        "type": "refresh_token"
    }

    # jwt.encode() 通过调用编码JWT令牌
    # 传入载荷数据 to_encode、密钥 secret_key 和算法 "HS256"
    # 得到编码后的令牌字符串，赋值给 encoded_jwt 变量
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm="HS256")

    # return 语句返回生成的JWT刷新令牌字符串
    return encoded_jwt


def generate_token_pair(user_id: str, username: str) -> Dict[str, str]:
    """
    生成访问令牌和刷新令牌对

    同时生成访问令牌（15分钟）和刷新令牌（7天），
    用于完整的JWT认证流程。

    参数:
        user_id: 用户唯一标识符字符串
        username: 用户名字符串

    返回:
        dict: 包含access_token和refresh_token的字典
    """
    # generate_access_token() 通过调用生成15分钟有效的访问令牌
    # 传入用户ID和用户名，得到访问令牌字符串
    # 赋值给 access_token 变量存储访问令牌
    access_token = generate_access_token(user_id, username)
    
    # generate_refresh_token() 通过调用生成7天有效的刷新令牌
    # 传入用户ID和用户名，得到刷新令牌字符串
    # 赋值给 refresh_token 变量存储刷新令牌
    refresh_token = generate_refresh_token(user_id, username)
    
    # return 语句返回包含两种令牌的字典
    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }


def verify_access_token(token: str) -> Dict[str, Any]:
    """
    验证访问令牌

    验证 JWT 令牌的有效性，解码并返回令牌中的用户信息。
    如果令牌无效或过期，将抛出相应的异常。

    参数:
        token: 要验证的 JWT 令牌字符串

    返回:
        dict: 解码后的令牌载荷数据字典

    异常:
        jwt.ExpiredSignatureError: 令牌已过期
        jwt.InvalidTokenError: 令牌无效
    """
    # 获取 JWT 密钥，如果环境变量中没有设置，使用默认密钥
    secret_key = os.getenv('JWT_SECRET_KEY', 'your-secret-key-here')

    try:
        # 使用 jwt.decode() 方法解码令牌
        # 传入令牌字符串 token 和密钥 secret_key，使用 HS256 算法
        # 得到解码后的载荷数据字典，赋值给 payload
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])

        # 返回解码后的令牌载荷数据
        return payload

    except jwt.ExpiredSignatureError:
        # 令牌过期异常
        raise ValueError("Token has expired")

    except jwt.InvalidTokenError:
        # 令牌无效异常
        raise ValueError("Invalid token")


def refresh_access_token(refresh_token: str) -> Dict[str, str]:
    """
    使用刷新令牌生成新的访问令牌

    验证刷新令牌有效性后，生成新的访问令牌和刷新令牌对。
    用于在访问令牌过期时延长用户会话。

    参数:
        refresh_token: 刷新令牌字符串

    返回:
        dict: 包含新的access_token和refresh_token的字典

    异常:
        ValueError: 刷新令牌无效、已过期或类型错误
    """
    # verify_access_token() 通过调用验证刷新令牌有效性
    # 传入刷新令牌字符串，返回解码后的载荷数据字典
    # 赋值给 payload 变量存储令牌载荷
    payload = verify_access_token(refresh_token)
    
    # payload.get() 通过调用提取令牌类型字段
    # 传入 "type" 键名，返回令牌类型字符串
    # 赋值给 token_type 变量存储令牌类型
    token_type = payload.get("type")
    
    # if 条件判断检查令牌类型是否为刷新令牌
    if token_type != "refresh_token":
        # ValueError() 通过调用抛出值错误异常
        # 传入错误信息字符串，表示令牌类型错误
        raise ValueError("Token is not a refresh token")
    
    # payload.get() 通过调用提取用户ID字段
    # 传入 "user_id" 键名，返回用户ID字符串
    # 赋值给 user_id 变量存储用户标识符
    user_id = payload.get("user_id")
    
    # payload.get() 通过调用提取用户名字段
    # 传入 "username" 键名，返回用户名字符串
    # 赋值给 username 变量存储用户名
    username = payload.get("username")
    
    # generate_token_pair() 通过调用生成新的令牌对
    # 传入用户ID和用户名，返回包含两种令牌的字典
    # 赋值给 new_tokens 变量存储新令牌对
    new_tokens = generate_token_pair(user_id, username)
    
    # return 语句返回新生成的令牌对字典
    return new_tokens
