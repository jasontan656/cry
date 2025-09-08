# 项目配置管理模块
# 使用 pydantic.BaseSettings 管理环境变量配置

import os
from pydantic_settings import BaseSettings


class OAuthSettings(BaseSettings):
    """
    OAuth 配置类

    管理 Google 和 Facebook OAuth 认证相关的环境变量配置。
    通过 pydantic.BaseSettings 自动从 .env 文件加载配置。
    """

    # Google OAuth 配置
    google_client_id: str
    google_client_secret: str

    # Facebook OAuth 配置
    facebook_client_id: str
    facebook_client_secret: str

    # OAuth 通用配置
    oauth_redirect_uri: str = "http://localhost:8000/auth/oauth/callback"

    class Config:
        """
        Pydantic 配置类

        指定环境变量加载的配置文件路径。
        """
        # 使用绝对路径确保能找到.env文件
        env_file = os.path.join(os.path.dirname(__file__), ".env")
        env_prefix = ""  # 不使用前缀，直接映射环境变量名
        extra = "ignore"  # 忽略.env文件中的额外字段


# 创建全局配置实例
# 通过 OAuthSettings() 自动从 .env 文件加载配置
# 结果赋值给 oauth_settings 变量，提供给其他模块使用
oauth_settings = OAuthSettings()
