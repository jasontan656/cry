# config.py 通过字典定义测试配置常量
import os
# 加载.env环境变量
try:
    from dotenv import load_dotenv
    # 查找项目根目录的.env文件
    env_path = os.path.join(os.path.dirname(__file__), '../../../.env')
    load_dotenv(env_path)
except ImportError:
    print("Warning: python-dotenv not available, using system environment variables only")

# BASE_URL 设置为本地开发服务器地址，端口8000
BASE_URL = "http://localhost:8000"

# REQUEST_TIMEOUT 设置为30秒，防止测试因网络延迟失败
REQUEST_TIMEOUT = 30

# TEST_EMAIL_PREFIX 设置为测试邮箱前缀，用于生成唯一测试邮箱
TEST_EMAIL_PREFIX = "test"

# TEST_USER_FLAG 设置为True，启用测试模式特殊处理
TEST_USER_FLAG = True

# FIXED_VERIFICATION_CODE 设置为123456，测试模式下的固定验证码
FIXED_VERIFICATION_CODE = "123456"

# FIXED_RESET_CODE 设置为123456，测试模式下的固定重置验证码
FIXED_RESET_CODE = "123456"

# MONGODB_CONNECTION_STRING 设置为本地MongoDB默认连接字符串
MONGODB_CONNECTION_STRING = "mongodb://localhost:27017/"

# MONGODB_DATABASE_NAME 设置为careerbot_mongodb，项目使用的数据库名
MONGODB_DATABASE_NAME = "careerbot_mongodb"

# COLLECTIONS 定义需要测试的MongoDB集合列表
COLLECTIONS = [
    "user_profiles",    # 用户个人资料集合
    "user_status",      # 用户状态信息集合
    "user_archive"      # 用户数据归档集合
]

# OAUTH_SKIP_IF_MISSING 设置为True，OAuth环境变量缺失时自动跳过测试
OAUTH_SKIP_IF_MISSING = True

# GOOGLE_OAUTH_CLIENT_ID 从环境变量获取Google OAuth客户端ID
GOOGLE_OAUTH_CLIENT_ID = None  # 测试脚本会检查环境变量

# GOOGLE_OAUTH_CLIENT_SECRET 从环境变量获取Google OAuth客户端密钥
GOOGLE_OAUTH_CLIENT_SECRET = None  # 测试脚本会检查环境变量

# LOG_LEVEL 设置为INFO级别，控制测试日志输出详细程度
LOG_LEVEL = "INFO"
