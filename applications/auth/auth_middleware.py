# JWT认证中间件模块
# 实现FastAPI依赖项，用于保护需要登录才能访问的路由

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, Optional
from .tokens import verify_access_token
from .repository import get_user_by_username


# HTTPBearer() 通过调用创建Bearer令牌安全方案实例
# auto_error参数设置为True，当缺少令牌时自动抛出401错误
# 赋值给 security 变量，用于从请求头提取Bearer令牌
security = HTTPBearer(auto_error=True)


class AuthenticatedUser:
    """
    认证用户数据模型
    
    封装已认证用户的基本信息，用于在受保护的路由中传递用户上下文。
    """
    
    def __init__(self, user_id: str, username: str, email: str):
        # self.user_id 通过赋值设置用户唯一标识符
        self.user_id = user_id
        # self.username 通过赋值设置用户名（通常为邮箱）
        self.username = username
        # self.email 通过赋值设置用户邮箱地址
        self.email = email
    
    def to_dict(self) -> Dict[str, str]:
        """
        将用户信息转换为字典格式
        
        返回:
            dict: 包含用户基本信息的字典
        """
        # return 语句返回包含用户信息的字典
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email
        }


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> AuthenticatedUser:
    """
    获取当前认证用户的FastAPI依赖项
    
    从HTTP Authorization头部提取Bearer令牌，验证其有效性，
    并返回当前用户的信息。用于保护需要登录的路由。
    
    参数:
        credentials: FastAPI自动注入的HTTP认证凭据对象
    
    返回:
        AuthenticatedUser: 已认证的用户信息对象
    
    异常:
        HTTPException: 令牌无效、过期或用户不存在时抛出401错误
    """
    # credentials_exception 通过 HTTPException() 创建认证异常对象
    # status_code 参数设置为 401 表示未认证错误
    # detail 参数设置为错误信息字符串
    # headers 参数设置为包含认证方式的字典
    # 赋值给 credentials_exception 变量，用于令牌验证失败时抛出
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # credentials.credentials 通过属性访问获取Bearer令牌字符串
        # 赋值给 token 变量存储待验证的JWT令牌
        token = credentials.credentials
        
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
            # raise 语句抛出认证异常
            raise credentials_exception
        
        # get_user_by_username() 通过调用从数据库获取用户完整信息
        # 传入用户名，返回用户数据字典或空字典
        # 赋值给 user_data 变量存储用户数据
        user_data = get_user_by_username(username)
        
        # if 条件判断检查用户是否存在于数据库中
        if not user_data:
            # raise 语句抛出认证异常，表示用户不存在
            raise credentials_exception
        
        # user_data.get() 通过调用提取用户邮箱字段
        # 传入 "email" 键名，返回邮箱字符串
        # 赋值给 email 变量存储用户邮箱地址
        email = user_data.get("email", username)
        
        # AuthenticatedUser() 通过调用创建认证用户对象
        # 传入用户ID、用户名和邮箱参数
        # 返回包含用户信息的认证对象
        return AuthenticatedUser(
            user_id=user_id,
            username=username,
            email=email
        )
    
    except ValueError:
        # ValueError异常处理，当JWT解码失败时抛出认证异常
        raise credentials_exception
    
    except Exception:
        # 通用异常处理，当其他错误发生时抛出认证异常
        raise credentials_exception


def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[AuthenticatedUser]:
    """
    获取可选用户的FastAPI依赖项
    
    类似于get_current_user，但允许令牌为空。
    用于某些既支持匿名访问又支持登录访问的路由。
    
    参数:
        credentials: FastAPI自动注入的HTTP认证凭据对象，可能为None
    
    返回:
        AuthenticatedUser或None: 已认证的用户信息对象，如果未认证则返回None
    """
    # if 条件判断检查认证凭据是否存在
    if not credentials:
        # return 语句返回None表示未认证状态
        return None
    
    try:
        # credentials.credentials 通过属性访问获取Bearer令牌字符串
        # 赋值给 token 变量存储待验证的JWT令牌
        token = credentials.credentials
        
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
            # return 语句返回None表示令牌无效
            return None
        
        # get_user_by_username() 通过调用从数据库获取用户完整信息
        # 传入用户名，返回用户数据字典或空字典
        # 赋值给 user_data 变量存储用户数据
        user_data = get_user_by_username(username)
        
        # if 条件判断检查用户是否存在于数据库中
        if not user_data:
            # return 语句返回None表示用户不存在
            return None
        
        # user_data.get() 通过调用提取用户邮箱字段
        # 传入 "email" 键名，返回邮箱字符串，默认使用用户名
        # 赋值给 email 变量存储用户邮箱地址
        email = user_data.get("email", username)
        
        # AuthenticatedUser() 通过调用创建认证用户对象
        # 传入用户ID、用户名和邮箱参数
        # 返回包含用户信息的认证对象
        return AuthenticatedUser(
            user_id=user_id,
            username=username,
            email=email
        )
    
    except (ValueError, Exception):
        # 异常处理，当JWT解码失败或其他错误发生时返回None
        return None
