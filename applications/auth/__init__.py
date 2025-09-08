# __init__.py - Auth模块热插拔接口定义
# sys 通过 import 导入系统模块，用于路径操作
import sys
# os 通过 import 导入操作系统接口模块，用于文件路径处理
import os
# os.path.dirname 通过调用获取当前文件的上级目录路径
# 然后再次调用获取上上级目录路径，赋值给parent_dir变量
parent_dir = os.path.dirname(os.path.dirname(__file__))
# sys.path.insert 通过调用在路径列表开头插入parent_dir
# 传入索引0和parent_dir参数，确保上级目录优先被搜索
sys.path.insert(0, parent_dir)

# from applications.auth.register import 导入注册相关函数
from applications.auth.register import register_user
# from applications.auth.login import login_user 导入用户登录函数
from applications.auth.login import login_user
# from applications.auth.schemas import 导入核心数据模型
from applications.auth.schemas import UserRegisterRequest, UserResponse
# from applications.auth.router import ROUTES 导入路由映射
from applications.auth.router import ROUTES
# from applications.auth.exceptions import 导入核心异常类
from applications.auth.exceptions import UserAlreadyExistsError, InvalidCredentialsError

# 导入orchestrate注册中心，用于模块主动注册
try:
    from orchestrate.router import router
    ORCHESTRATE_AVAILABLE = True
except ImportError:
    ORCHESTRATE_AVAILABLE = False

# def _get_dynamic_module_info() 定义动态生成模块元信息的函数
# 函数不接收参数，返回包含动态字段信息的模块信息字典
def _get_dynamic_module_info():
    """
    动态生成模块元信息
    返回：完整的模块信息字典
    """
    # return 语句返回构建的动态模块信息字典
    return {
        # "name" 键赋值为字符串"auth"，标识模块名称
        "name": "auth",
        # "version" 键赋值为字符串"1.0.0"，标识模块版本
        "version": "1.0.0",
        # "description" 键赋值为模块功能描述字符串
        "description": "用户认证中心模块，支持邮箱注册登录、第三方OAuth、邮箱验证码验证",
        "interface": {  # 对外暴露的接口字典
            # "register_user" 键赋值为之前导入的register_user函数引用
            "register_user": register_user,
            # "login_user" 键赋值为之前导入的login_user函数引用
            "login_user": login_user,
            # "router" 键赋值为之前导入的ROUTES路由映射字典
            "router": ROUTES
        },
        "capabilities": {  # 模块能力声明字典
            "email_authentication": {  # 邮箱认证能力字典
                # "methods" 键赋值为支持的认证方法列表
                "methods": ["register", "login", "email_verification"],
                # "description" 键赋值为详细的功能描述字符串
                "description": "完整的邮箱认证流程，包括注册、登录、验证码验证"
            },
            "oauth_integration": {  # OAuth集成能力字典
                # "providers" 键赋值为支持的OAuth提供商列表
                "providers": ["google", "facebook"],
                # "description" 键赋值为OAuth集成功能描述字符串
                "description": "支持Google和Facebook第三方OAuth登录"
            }
        },
        "orchestrate_info": {  # 编排信息字典
            # "supported_intents" 键赋值为具体的意图字符串列表
            "supported_intents": ["auth_register", "auth_login"],
            "route_mappings": {  # 路由映射定义字典
                # "/auth/register" 键赋值为注册路由处理函数
                "/auth/register": "handle_register_request",
                # "/auth/login" 键赋值为登录路由处理函数
                "/auth/login": "handle_login_request"
            }
        },
        # "dependencies" 键赋值包含模块依赖关系的列表
        "dependencies": [
            # database 模块被列为强依赖项
            # 没有database时无法存储和查询用户信息
            "database",
            # mail 模块被列为强依赖项
            # 没有mail时无法发送邮箱验证码
            "mail"
        ],
        "metadata": {  # 模块元数据字典
            # "author" 键赋值为开发团队字符串
            "author": "Career Bot Team",
            # "created" 键赋值为创建日期字符串
            "created": "2024-12-19",
            # "route_count" 键通过len(ROUTES)调用计算路由总数
            "route_count": len(ROUTES)
        }
    }


# _MODULE_INFO_CACHE 通过赋值None初始化全局缓存变量
# 用于存储计算过的模块信息，避免重复调用动态生成函数
_MODULE_INFO_CACHE = None

# def _get_module_info() 定义获取模块信息的内部函数
# 函数不接收参数，返回包含完整模块信息的字典
def _get_module_info():
    """
    获取模块信息，带缓存机制避免重复计算
    返回：模块信息字典
    """
    # global _MODULE_INFO_CACHE 声明使用全局变量_MODULE_INFO_CACHE
    global _MODULE_INFO_CACHE
    # if 条件判断检查_MODULE_INFO_CACHE是否为None
    if _MODULE_INFO_CACHE is None:
        # _get_dynamic_module_info() 通过调用动态生成完整的模块信息
        # 不传入参数，返回包含最新配置的字典
        # 赋值给_MODULE_INFO_CACHE变量进行缓存
        _MODULE_INFO_CACHE = _get_dynamic_module_info()
    # return 语句返回缓存的模块信息字典
    return _MODULE_INFO_CACHE

# MODULE_INFO 通过_get_module_info()调用获取动态生成的模块信息
# 赋值给全局变量MODULE_INFO，用于向后兼容现有代码
MODULE_INFO = _get_module_info()

# def initialize_module(config: dict = None) 定义模块初始化钩子函数
# 函数接收可选的config字典参数，默认为None，返回初始化状态字典
def initialize_module(config: dict = None):
    """模块初始化钩子"""
    # import logging 导入日志模块用于记录初始化信息
    import logging
    # logging.getLogger 通过调用获取当前模块的日志记录器实例
    # 传入__name__参数，返回logger对象赋值给logger变量
    logger = logging.getLogger(__name__)
    # logger.info 通过调用记录信息级别的日志消息
    # 传入字符串消息"Auth模块初始化完成"
    logger.info("Auth模块初始化完成")

    # return 语句返回包含初始化状态的字典
    return {
        # "status" 键赋值为字符串"initialized"表示初始化成功
        "status": "initialized",
        # "capabilities" 键赋值为MODULE_INFO["capabilities"]获取模块能力信息
        "capabilities": MODULE_INFO["capabilities"]
    }

# def cleanup_module() 定义模块清理钩子函数
# 函数不接收参数，返回清理状态字典
def cleanup_module():
    """模块清理钩子"""
    # import logging 导入日志模块用于记录清理信息
    import logging
    # logging.getLogger 通过调用获取当前模块的日志记录器实例
    # 传入__name__参数，返回logger对象赋值给logger变量
    logger = logging.getLogger(__name__)
    # logger.info 通过调用记录信息级别的日志消息
    # 传入字符串消息"Auth模块清理完成"
    logger.info("Auth模块清理完成")
    # return 语句返回包含清理状态的字典
    return {"status": "cleaned"}

# def get_module_info() 定义获取模块完整信息的函数
# 函数不接收参数，返回包含完整模块信息的字典
def get_module_info():
    """
    获取模块完整信息（动态生成）
    返回：包含完整模块信息的字典
    """
    # _get_module_info() 通过调用获取动态生成的模块信息
    # 不传入参数，返回包含最新配置的完整字典
    return _get_module_info()

# def get_capabilities() 定义获取模块能力列表的函数
# 函数不接收参数，返回包含模块能力的字典
def get_capabilities():
    """
    获取模块能力列表（动态生成）
    返回：包含模块能力的字典
    """
    # _get_module_info()["capabilities"] 通过调用动态获取模块能力信息
    # 不传入参数，返回包含认证和OAuth能力的字典
    return _get_module_info()["capabilities"]

# def register_to_orchestrate() 定义主动注册到中枢的函数
# 函数不接收参数，执行Auth模块向orchestrate注册中心的主动注册
def register_to_orchestrate():
    """
    Auth模块主动向orchestrate注册中心注册
    实现模块自治的注册机制
    """
    # 检查orchestrate是否可用
    if not ORCHESTRATE_AVAILABLE:
        print("Warning: Orchestrate not available, skipping registration")
        return False

    try:
        # 使用router中的注册中心实例，确保注册到同一个registry
        registry = router.registry

        # 获取模块信息
        module_info = get_module_info()

        # 调用注册中心的register_module方法进行注册
        registry.register_module(module_info)

        print(f"Auth模块成功注册到orchestrate注册中心")
        return True

    except Exception as e:
        print(f"Auth模块注册失败: {str(e)}")
        return False

# 模块加载时自动注册到orchestrate
# 只有在orchestrate可用时才执行注册
if ORCHESTRATE_AVAILABLE:
    register_to_orchestrate()

# MODULE_READY 通过赋值True设置模块就绪状态标识
# 用于向外部系统表示该模块已准备就绪，可以正常使用
MODULE_READY = True
