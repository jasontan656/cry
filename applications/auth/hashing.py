# 密码加密逻辑封装
# 使用 bcrypt 库实现密码的不可逆加密存储

import bcrypt


def hash_password(password: str) -> str:
    """
    对密码进行加密处理

    使用 bcrypt.gensalt() 生成盐值，然后通过 bcrypt.hashpw() 对密码进行哈希处理。
    返回加密后的密码字符串，用于安全存储到数据库中。

    参数:
        password: 原始密码字符串

    返回:
        str: 加密后的密码哈希字符串
    """
    # 将密码字符串编码为字节串
    password_bytes = password.encode('utf-8')

    # 使用 bcrypt.gensalt() 生成随机盐值
    salt = bcrypt.gensalt()

    # 使用 bcrypt.hashpw() 对密码和盐值进行哈希处理
    hashed = bcrypt.hashpw(password_bytes, salt)

    # 将哈希结果解码为字符串并返回
    return hashed.decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """
    验证密码是否匹配

    将输入的密码与存储的哈希值进行比较验证。
    用于登录时验证用户输入的密码是否正确。

    参数:
        password: 用户输入的原始密码字符串
        hashed: 数据库中存储的哈希密码字符串

    返回:
        bool: 密码匹配返回True，否则返回False
    """
    # 将密码字符串编码为字节串
    password_bytes = password.encode('utf-8')

    # 将哈希密码字符串编码为字节串
    hashed_bytes = hashed.encode('utf-8')

    # 使用 bcrypt.checkpw() 验证密码是否匹配哈希值
    return bcrypt.checkpw(password_bytes, hashed_bytes)
