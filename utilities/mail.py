# 导入标准库模块
from typing import Optional, List, Union

# 导入第三方库模块
from pydantic_settings import BaseSettings
from aiosmtplib import send
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os


class MailSettings(BaseSettings):
    """
    邮件配置类

    管理邮件服务器相关的环境变量配置。
    通过 pydantic.BaseSettings 自动从 .env 文件加载配置。
    """

    # 邮件服务器配置
    mail_host: str
    mail_port: int
    mail_username: str
    mail_password: str
    mail_encryption: str
    mail_from_address: str
    mail_from_name: str

    class Config:
        """
        Pydantic 配置类

        指定环境变量加载的配置文件路径。
        """
        # 使用绝对路径确保能找到.env文件
        env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
        extra = "ignore"  # 忽略.env文件中的额外字段


# 创建全局邮件配置实例
# 通过 MailSettings() 自动从 .env 文件加载配置
# 结果赋值给 mail_settings 变量，提供给其他模块使用
mail_settings = MailSettings()


class EmailMessage:
    """
    邮件消息类

    用于构建邮件消息，包含主题、收件人、正文等信息。
    """

    def __init__(self,
                 to: Union[str, List[str]],
                 subject: str,
                 body: str,
                 content_type: str = 'plain'):
        """
        初始化邮件消息

        参数:
            to (Union[str, List[str]]): 收件人邮箱地址，可以是单个字符串或列表
            subject (str): 邮件主题
            body (str): 邮件正文内容
            content_type (str): 内容类型，默认为 'plain'，也可以是 'html'
        """
        # 将单个收件人转换为列表格式
        # 结果赋值给 self.to 变量
        self.to = [to] if isinstance(to, str) else to

        # 邮件主题赋值给 self.subject 变量
        self.subject = subject

        # 邮件正文赋值给 self.body 变量
        self.body = body

        # 内容类型赋值给 self.content_type 变量
        self.content_type = content_type

        # 初始化附件列表为空列表
        self.attachments = []


class MailSender:
    """
    邮件发送器类

    提供发送邮件的核心功能，支持自定义邮件内容和附件。
    """

    def __init__(self):
        """
        初始化邮件发送器

        使用全局邮件配置实例 mail_settings
        """
        # 使用全局配置实例赋值给 self.settings
        self.settings = mail_settings

    def _create_message(self, email_msg: EmailMessage) -> MIMEMultipart:
        """
        创建邮件消息对象

        参数:
            email_msg (EmailMessage): 邮件消息实例

        返回值:
            MIMEMultipart: 构建好的邮件消息对象
        """
        # 创建 MIMEMultipart 对象作为邮件主体
        # 设置邮件的 From、To、Subject 字段
        msg = MIMEMultipart()
        msg['From'] = f"{self.settings.mail_from_name} <{self.settings.mail_from_address}>"
        msg['To'] = ', '.join(email_msg.to)
        msg['Subject'] = email_msg.subject

        # 创建 MIMEText 对象作为邮件正文
        # 根据 content_type 设置内容类型
        body_part = MIMEText(email_msg.body, email_msg.content_type, 'utf-8')
        msg.attach(body_part)

        # 如果有附件，添加附件到邮件中
        for attachment in email_msg.attachments:
            msg.attach(attachment)

        return msg

    async def send_email(self, email_msg: EmailMessage) -> bool:
        """
        发送邮件

        参数:
            email_msg (EmailMessage): 要发送的邮件消息实例

        返回值:
            bool: 邮件发送成功返回 True，失败返回 False
        """
        try:
            # 先通过 _create_message() 创建邮件消息对象
            # 结果赋值给 msg 变量
            msg = self._create_message(email_msg)

            # 然后通过 aiosmtplib.send 发送邮件
            # 传入邮件服务器配置参数和邮件内容
            # message 作为位置参数传递
            # 端口587使用STARTTLS，端口465使用直接TLS
            if self.settings.mail_port == 587:
                # 使用STARTTLS (端口587)
                await send(
                    msg,  # message 作为第一个位置参数
                    hostname=self.settings.mail_host,
                    port=self.settings.mail_port,
                    username=self.settings.mail_username,
                    password=self.settings.mail_password,
                    start_tls=True
                )
            else:
                # 使用直接TLS (端口465)
                await send(
                    msg,  # message 作为第一个位置参数
                    hostname=self.settings.mail_host,
                    port=self.settings.mail_port,
                    username=self.settings.mail_username,
                    password=self.settings.mail_password,
                    use_tls=True if self.settings.mail_encryption.upper() == 'TLS' else False
                )

            return True

        except Exception as e:
            # 发送失败时打印错误信息
            print(f"邮件发送失败: {e}")
            return False


# 创建全局邮件发送器实例
# 提供给其他模块直接使用
mail_sender = MailSender()


async def send_email(to: Union[str, List[str]],
                    subject: str,
                    body: str,
                    content_type: str = 'plain') -> bool:
    """
    发送邮件的便捷函数

    参数:
        to (Union[str, List[str]]): 收件人邮箱地址
        subject (str): 邮件主题
        body (str): 邮件正文内容
        content_type (str): 内容类型，默认为 'plain'

    返回值:
        bool: 发送成功返回 True，失败返回 False
    """
    # 创建 EmailMessage 实例
    # 传入所有参数构建邮件消息
    email_msg = EmailMessage(
        to=to,
        subject=subject,
        body=body,
        content_type=content_type
    )

    # 使用全局邮件发送器发送邮件
    # 返回发送结果
    return await mail_sender.send_email(email_msg)
