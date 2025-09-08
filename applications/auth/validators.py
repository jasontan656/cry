# 输入数据校验逻辑封装
# 提供用户名、密码、邮箱等字段的格式验证功能

import re
from .exceptions import InvalidInputError


def validate_email(email: str) -> None:
    """
    验证邮箱格式

    使用正则表达式检查邮箱的基本格式要求，同时作为用户名使用。
    如果校验失败，抛出 InvalidInputError 异常。

    参数:
        email: 要验证的邮箱字符串（同时作为用户名）
    """
    # 定义邮箱格式的正则表达式
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    # 使用正则表达式验证邮箱格式
    if not re.match(email_pattern, email):
        raise InvalidInputError("邮箱格式不正确")

    # 检查邮箱长度是否合理
    if len(email) > 254:  # RFC 5321 限制
        raise InvalidInputError("邮箱地址过长")


def validate_password(password: str) -> None:
    """
    验证密码强度

    检查密码长度是否至少为8个字符。
    如果校验失败，抛出 InvalidInputError 异常。

    参数:
        password: 要验证的密码字符串
    """
    # 检查密码长度是否至少为8个字符
    if len(password) < 8:
        raise InvalidInputError("密码长度至少为8个字符")


def validate_registration_data(email: str, password: str) -> None:
    """
    验证用户注册数据的完整性

    依次调用各个字段的验证函数，确保所有输入数据都符合要求。
    如果任一字段校验失败，将抛出对应的异常。

    参数:
        email: 邮箱字符串（同时作为用户名）
        password: 密码字符串
    """
    # 依次验证邮箱和密码
    validate_email(email)
    validate_password(password)
