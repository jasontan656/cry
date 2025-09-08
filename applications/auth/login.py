# 标准登录模块
# 实现用户名/密码登录逻辑

from .repository import get_user_by_username
from .hashing import verify_password
from .tokens import generate_token_pair
from .exceptions import InvalidCredentialsError
from .schemas import UserResponse


def login_user(email: str, password: str) -> UserResponse:
    """
    执行用户标准登录流程

    通过邮箱获取用户信息，验证密码正确性，生成访问令牌。
    如果邮箱不存在或密码错误，抛出InvalidCredentialsError异常。

    参数:
        email: 邮箱字符串（同时作为用户名）
        password: 密码字符串

    返回:
        UserResponse: 登录成功的用户信息对象

    异常:
        InvalidCredentialsError: 邮箱或密码错误
    """
    # 使用邮箱作为用户名来查询用户
    username = email

    # 调用 get_user_by_username 函数获取用户信息
    # 传入用户名（邮箱）username，得到用户信息字典
    # 结果赋值给 user_data 变量
    user_data = get_user_by_username(username)

    # 检查用户是否存在，如果用户数据为空字典，表示用户不存在
    if not user_data:
        raise InvalidCredentialsError("邮箱或密码错误")

    # 从用户数据中提取加密密码哈希
    stored_hashed_password = user_data.get("hashed_password")

    # 调用 verify_password 函数验证输入密码是否匹配存储的哈希密码
    # 传入输入密码 password 和存储的哈希密码 stored_hashed_password
    # 得到验证结果布尔值，赋值给 is_password_valid
    is_password_valid = verify_password(password, stored_hashed_password)

    # 如果密码验证失败，抛出 InvalidCredentialsError 异常
    if not is_password_valid:
        raise InvalidCredentialsError("邮箱或密码错误")

    # user_data["user_id"] 通过字典取值获取用户ID字段
    # 赋值给 user_id 变量存储用户唯一标识符
    user_id = user_data["user_id"]
    
    # user_data["email"] 通过字典取值获取用户邮箱字段
    # 赋值给 user_email 变量存储用户邮箱地址
    user_email = user_data["email"]

    # generate_token_pair() 通过调用生成访问令牌和刷新令牌对
    # 传入用户ID user_id 和用户名（邮箱）username
    # 得到包含两种令牌的字典，赋值给 tokens 变量
    tokens = generate_token_pair(user_id, username)

    # UserResponse() 通过调用创建用户响应对象，包含登录成功后的完整信息
    # user_id 参数传入用户ID
    # email 参数传入用户邮箱
    # access_token 参数从 tokens 字典提取访问令牌
    # refresh_token 参数从 tokens 字典提取刷新令牌
    # token_type 参数默认为 "Bearer"
    # 返回包含完整认证信息的用户响应对象
    return UserResponse(
        user_id=user_id,
        email=user_email,
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type="Bearer"
    )
