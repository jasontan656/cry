# __init__.py - Auth模块意图驱动架构接口定义
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

# 彻底重构：导入流程驱动系统组件
# 导入响应格式工具，保持兼容性
from applications.auth.intent_handlers import create_success_response, create_error_response
# 导入流程注册函数，用于向Hub系统自主注册
from applications.auth.intent_registration import auth_register_function
# 导入流程注册函数，用于向flow_registry注册认证流程
from applications.auth.flow_definitions import register_auth_flows

# 导入hub注册中心，用于模块主动注册
try:
    from hub.router import router
    HUB_AVAILABLE = True
except ImportError:
    HUB_AVAILABLE = False

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
        "interface": {  # 流程驱动架构接口字典
            # 现代化架构：完全基于流程注册机制
            # "response_formatters" 键赋值为标准响应格式化工具
            "response_formatters": {
                "create_success_response": create_success_response,
                "create_error_response": create_error_response
            },
            # "architecture_type" 键标识流程驱动架构
            "architecture_type": "flow_driven"
        },
        "capabilities": {  # 流程驱动能力声明字典
            "flow_processing": {  # 流程处理能力字典
                # "supported_flows" 键赋值为支持的流程总数
                "supported_flows": 4,
                # "flow_categories" 键赋值为流程分类列表
                "flow_categories": ["user_registration", "oauth_authentication", "password_reset", "protected_operations"],
                # "description" 键赋值为流程处理能力描述
                "description": "完整的用户认证流程处理系统，支持注册、OAuth、密码重置和受保护功能流程"
            },
            "flow_management": {  # 流程管理能力字典
                # "supported_flows" 键赋值为支持的流程列表
                "supported_flows": ["user_registration", "oauth_authentication", "password_reset"],
                # "flow_state_tracking" 键标识支持流程状态追踪
                "flow_state_tracking": True,
                # "description" 键赋值为流程管理能力描述
                "description": "支持多步骤认证流程状态管理和恢复"
            }
        },
        "hub_info": {  # 流程驱动编排信息字典
            # "supported_flows" 键赋值为完整的流程字符串列表
            "supported_flows": [
                "user_registration", "oauth_google_authentication", 
                "oauth_facebook_authentication", "password_reset"
            ],
            "flow_definitions": {  # 流程定义字典，描述各个流程的步骤
                # 用户注册流程
                "user_registration": {
                    "steps": ["register_step1", "register_step2", "register_step3"],
                    "description": "邮箱验证注册流程"
                },
                # Google OAuth流程
                "oauth_google_authentication": {
                    "steps": ["oauth_google_step1", "oauth_google_step2"],
                    "description": "Google第三方登录流程"
                },
                # Facebook OAuth流程
                "oauth_facebook_authentication": {
                    "steps": ["oauth_facebook_step1", "oauth_facebook_step2"],
                    "description": "Facebook第三方登录流程"
                },
                # 密码重置流程
                "password_reset": {
                    "steps": ["reset_step1", "reset_step2"],
                    "description": "密码重置流程"
                }
            }
        },
        # "register_function" 键赋值为模块自主注册函数
        # 这是提供给hub注册中心的回调函数，实现完全自主的注册过程
        "register_function": auth_register_function,
        # "dependencies" 键赋值包含意图驱动系统依赖关系的列表
        "dependencies": [
            # hub 模块被列为核心依赖项
            # 意图驱动架构需要hub进行意图路由和流程管理
            "hub",
            # mongodb_connector 模块被列为数据层依赖项
            # 意图处理器需要数据存储支持
            "mongodb_connector",
            # mail 模块被列为通讯依赖项  
            # 验证码发送意图需要邮件服务支持
            "mail"
        ],
        "metadata": {  # 模块元数据字典
            # "author" 键赋值为开发团队字符串
            "author": "Career Bot Team",
            # "created" 键赋值为创建日期字符串
            "created": "2024-12-19",
            # "flow_count" 键赋值为支持的流程总数
            "flow_count": 4,  # auth模块支持的流程数量
            # "architecture" 键标识架构类型
            "architecture": "flow_driven"  # 流程驱动架构标识
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
    # 传入字符串消息表明流程驱动架构初始化完成
    logger.info("Auth模块流程驱动系统初始化完成")

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
    # 传入字符串消息表明流程驱动系统清理完成
    logger.info("Auth模块流程驱动系统清理完成")
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

# def register_to_hub() 定义主动注册到中枢的函数
# 函数不接收参数，执行Auth模块向hub注册中心的主动注册
def register_to_hub():
    """
    Auth模块主动向hub注册中心注册
    实现模块自治的注册机制
    """
    # 检查hub是否可用
    if not HUB_AVAILABLE:
        print("Warning: Hub not available, skipping registration")
        return False

    try:
        # 使用router中的注册中心实例，确保注册到同一个registry
        registry = router.registry

        # 获取模块信息
        module_info = get_module_info()

        # 调用注册中心的register_module方法进行注册
        registry.register_module(module_info)

        print(f"Auth模块流程驱动系统成功注册到hub注册中心")
        return True

    except Exception as e:
        print(f"Auth模块流程驱动系统注册失败: {str(e)}")
        return False

# 模块加载时自动注册到hub并注册流程
# 只有在hub可用时才执行注册
if HUB_AVAILABLE:
    # 注册模块到hub
    register_to_hub()
    
    # 注册所有认证流程到flow_registry
    try:
        register_auth_flows()
        print("Auth模块所有流程注册成功")
    except Exception as e:
        print(f"Auth模块流程注册失败: {str(e)}")

# MODULE_READY 通过赋值True设置模块就绪状态标识
# 用于向外部系统表示该模块已准备就绪，可以正常使用
MODULE_READY = True
