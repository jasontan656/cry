# 认证工具模块
# 提供意图驱动架构下的认证工具函数和用户数据模型

from typing import Dict, Any, Optional
from .tokens import verify_access_token
from .repository import get_user_by_username


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


def extract_auth_info_from_token(token: str) -> Optional[AuthenticatedUser]:
    """
    从JWT令牌中提取认证信息
    
    验证令牌有效性并返回认证用户对象，用于意图驱动架构下的认证检查。
    
    参数:
        token: JWT令牌字符串
    
    返回:
        AuthenticatedUser或None: 认证成功返回用户对象，否则返回None
    """
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
            return None
        
        # get_user_by_username() 通过调用从数据库获取用户完整信息
        # 传入用户名，返回用户数据字典或空字典
        # 赋值给 user_data 变量存储用户数据
        user_data = get_user_by_username(username)
        
        # if 条件判断检查用户是否存在于数据库中
        if not user_data:
            return None
        
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
    
    except (ValueError, Exception):
        # 异常处理，当JWT解码失败或其他错误发生时返回None
        return None


def extract_auth_info_from_payload(payload: Dict[str, Any]) -> Optional[AuthenticatedUser]:
    """
    从意图载荷中提取认证信息
    
    支持从payload的Authorization头部或access_token字段提取令牌并验证。
    
    参数:
        payload: 意图载荷字典，可能包含认证令牌
    
    返回:
        AuthenticatedUser对象或None: 认证成功返回用户对象，否则返回None
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
        
        # 调用令牌验证函数
        return extract_auth_info_from_token(token)
        
    except Exception:
        return None


def extract_auth_info_from_context(context: Dict[str, Any]) -> Optional[AuthenticatedUser]:
    """
    从意图上下文中提取认证信息
    
    支持从context中直接提取已验证的用户认证信息。
    
    参数:
        context: 意图上下文字典，可能包含用户认证信息
    
    返回:
        AuthenticatedUser对象或None: 认证信息存在返回用户对象，否则返回None
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


def create_authenticated_user(user_data: Dict[str, Any]) -> AuthenticatedUser:
    """
    从用户数据字典创建认证用户对象
    
    参数:
        user_data: 包含用户信息的字典
    
    返回:
        AuthenticatedUser: 认证用户对象
    
    异常:
        KeyError: 缺少必要的用户信息字段
    """
    # 从用户数据中提取必要字段
    user_id = user_data["user_id"]
    username = user_data.get("username") or user_data.get("email")
    email = user_data.get("email") or username
    
    # 创建并返回认证用户对象
    return AuthenticatedUser(
        user_id=user_id,
        username=username,
        email=email
    )


def validate_user_authentication(user: Optional[AuthenticatedUser]) -> bool:
    """
    验证用户认证状态
    
    参数:
        user: 可选的认证用户对象
    
    返回:
        bool: 用户已认证返回True，否则返回False
    """
    return user is not None and user.user_id and user.username


# 导出主要类和函数
__all__ = [
    # 认证用户数据模型
    "AuthenticatedUser",
    
    # 认证信息提取工具函数
    "extract_auth_info_from_token",
    "extract_auth_info_from_payload", 
    "extract_auth_info_from_context",
    
    # 认证用户创建和验证工具
    "create_authenticated_user",
    "validate_user_authentication"
]
