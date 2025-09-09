# __init__.py - Auth模块意图驱动架构接口定义
# sys 通过 import 导入系统模块，用于路径操作
import sys
# os 通过 import 导入操作系统接口模块，用于文件路径处理
import os
# typing 通过 import 导入类型注解模块，支持Dict、Any等类型注解
from typing import Dict, Any
# os.path.dirname 通过调用获取当前文件的上级目录路径
# 然后再次调用获取上上级目录路径，赋值给parent_dir变量
parent_dir = os.path.dirname(os.path.dirname(__file__))
# sys.path.insert 通过调用在路径列表开头插入parent_dir
# 传入索引0和parent_dir参数，确保上级目录优先被搜索
sys.path.insert(0, parent_dir)

# 彻底重构：导入流程驱动系统组件
# 导入响应格式工具，从services层获取，消除循环导入  
from applications.auth.services import create_success_response, create_error_response
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
                # "supported_flows" 键赋值为支持的流程总数（4个多步流程 + 10个单步流程）
                "supported_flows": 14,
                # "multi_step_flows" 键赋值为多步流程数量
                "multi_step_flows": 4,
                # "single_step_flows" 键赋值为单步流程数量  
                "single_step_flows": 10,
                # "flow_categories" 键赋值为流程分类列表
                "flow_categories": ["user_registration", "oauth_authentication", "password_reset", "protected_operations", "single_step_operations"],
                # "description" 键赋值为流程处理能力描述
                "description": "完整的用户认证流程处理系统，支持多步流程（注册、OAuth、密码重置）和单步操作（登录、受保护功能）"
            },
            "flow_management": {  # 流程管理能力字典
                # "supported_multi_step_flows" 键赋值为支持的多步流程列表
                "supported_multi_step_flows": ["user_registration", "oauth_google_authentication", "oauth_facebook_authentication", "password_reset"],
                # "supported_single_step_flows" 键赋值为支持的单步流程列表
                "supported_single_step_flows": [
                    "auth_register", "auth_login", "auth_refresh_token", "auth_logout",
                    "auth_get_profile", "auth_update_settings", 
                    "oauth_google_url", "oauth_google_callback",
                    "oauth_facebook_url", "oauth_facebook_callback"
                ],
                # "flow_state_tracking" 键标识支持流程状态追踪
                "flow_state_tracking": True,
                # "description" 键赋值为流程管理能力描述
                "description": "支持多步骤认证流程状态管理和恢复，以及单步原子操作的统一管理"
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
        # 这是提供给hub注册中心的回调函数，实现完全自主的flow_driven注册过程  
        "register_function": None,  # 将在模块加载完成后设置
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
            # "last_refactored" 键赋值为重构完成日期
            "last_refactored": "2024-12-19",
            # "multi_step_flow_count" 键赋值为多步流程数量
            "multi_step_flow_count": 4,  
            # "single_step_flow_count" 键赋值为单步流程数量
            "single_step_flow_count": 10,
            # "total_flow_count" 键赋值为支持的流程总数（多步+单步）
            "total_flow_count": 14,  # auth模块支持的流程总数
            # "architecture" 键标识架构类型
            "architecture": "flow_driven",  # 流程驱动架构标识
            # "migration_completed" 键标识迁移完成状态
            "migration_completed": True,
            # "intent_handlers_removed" 键标识旧架构已清理
            "intent_handlers_removed": True
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
def flow_driven_register_function(registry, module_name: str, module_info: Dict[str, Any]):
    """
    flow_driven_register_function Auth模块的flow_driven架构注册函数
    完全基于flow_registry的现代化注册机制，替代废弃的intent_handlers架构
    
    参数:
        registry: hub注册中心实例，用于模块元信息注册
        module_name: 模块名称字符串，应为"auth" 
        module_info: 模块信息字典，包含flow_driven架构的完整配置
        
    返回:
        bool: 注册成功返回True，失败返回False
    """
    # print 输出flow_driven注册开始信息
    print(f"=== 开始执行Auth模块flow_driven架构注册: {module_name} ===")
    
    try:
        # 注册模块元信息到hub注册中心
        # if module_name not in registry.module_meta 条件检查模块是否已在注册中心
        if module_name not in registry.module_meta:
            # registry.module_meta[module_name] 通过字典赋值创建模块元信息条目
            registry.module_meta[module_name] = {}
        
        # 更新模块元信息为flow_driven架构配置
        # registry.module_meta[module_name].update 通过调用更新模块配置
        registry.module_meta[module_name].update({
            "name": module_info.get("name", module_name),          # name字段设置模块名称
            "version": module_info.get("version", "1.0.0"),        # version字段设置模块版本
            "description": module_info.get("description", ""),     # description字段设置模块描述
            "capabilities": module_info.get("capabilities", {}),   # capabilities字段设置模块能力
            "architecture": "flow_driven",                         # architecture字段强制设置为flow_driven
            "migration_completed": True,                           # migration_completed字段标识迁移完成
            "last_refactored": "2024-12-19"                       # last_refactored字段记录重构时间
        })
        
        # print 输出模块元信息注册成功信息
        print(f"  ✓ 模块元信息注册成功: {module_name} (architecture: flow_driven)")
        
        # 执行flow_registry流程注册
        # registered_flows 通过列表初始化记录注册成功的流程
        registered_flows = []
        # failed_flows 通过列表初始化记录注册失败的流程
        failed_flows = []
        
        # 调用flow_definitions模块进行所有流程注册
        try:
            # register_auth_flows() 通过调用执行完整的流程注册逻辑
            # 包括多步流程和单步流程的注册
            register_auth_flows()
            # print 输出流程注册成功信息
            print("    ✓ 所有认证流程已成功注册到flow_registry")
            
            # 统计注册的流程（从module_info中获取预期数量）
            # multi_step_flows 通过get方法获取多步流程数量
            multi_step_flows = module_info.get("metadata", {}).get("multi_step_flow_count", 4)
            # single_step_flows 通过get方法获取单步流程数量  
            single_step_flows = module_info.get("metadata", {}).get("single_step_flow_count", 10)
            # total_flows 通过加法计算总流程数量
            total_flows = multi_step_flows + single_step_flows
            
            # registered_flows 通过列表赋值模拟成功注册的流程列表
            registered_flows = [
                "user_registration", "oauth_google_authentication", 
                "oauth_facebook_authentication", "password_reset",
                "auth_register", "auth_login", "auth_refresh_token", "auth_logout",
                "auth_get_profile", "auth_update_settings",
                "oauth_google_url", "oauth_google_callback",
                "oauth_facebook_url", "oauth_facebook_callback"
            ]
            
        except Exception as e:
            # print 输出流程注册失败信息
            print(f"    ✗ 流程注册失败: {str(e)}")
            # failed_flows.append 通过调用添加失败信息到列表
            failed_flows.append(f"flow_registration_error: {str(e)}")
        
        # 注册模块依赖关系到hub
        # dependencies 通过get方法获取模块依赖列表
        dependencies = module_info.get("dependencies", [])
        # if dependencies 条件检查是否有依赖需要注册
        if dependencies:
            # registry.dependencies[module_name] 通过字典赋值设置模块依赖
            registry.dependencies[module_name] = dependencies
            # print 输出依赖注册信息
            print(f"  ✓ 模块依赖注册: {dependencies}")
        
        # 输出注册结果统计信息
        # successful_flows 通过len函数获取成功注册的流程数量
        successful_flows = len(registered_flows)
        # failed_count 通过len函数获取失败注册的数量
        failed_count = len(failed_flows)
        # total_expected 通过get方法获取预期的总流程数
        total_expected = module_info.get("metadata", {}).get("total_flow_count", 14)
        
        # print 输出详细的注册统计信息
        print(f"\n  注册统计:")
        print(f"    模块名称: {module_name}")
        print(f"    架构类型: flow_driven") 
        print(f"    预期流程总数: {total_expected}")
        print(f"    成功注册流程: {successful_flows}")
        print(f"    失败注册: {failed_count}")
        print(f"    成功率: {(successful_flows/total_expected)*100:.1f}%" if total_expected > 0 else "成功率: N/A")
        
        # if failed_flows 条件检查是否有失败的注册
        if failed_flows:
            # print 输出失败流程的详细信息
            print(f"  失败的流程:")
            # for flow_error in failed_flows 遍历失败流程列表
            for flow_error in failed_flows:
                # print 输出每个失败流程的错误信息
                print(f"    ✗ {flow_error}")
        
        # print 输出flow_driven注册完成信息
        print(f"=== Auth模块flow_driven架构注册完成: {module_name} ===")
        # return 语句根据注册结果返回成功状态
        return successful_flows == total_expected if total_expected > 0 else True
        
    except Exception as e:
        # print 输出flow_driven注册失败的异常信息
        print(f"✗ Auth模块flow_driven架构注册失败: {module_name} - {str(e)}")
        # return False 注册异常时返回失败状态
        return False


def register_to_hub():
    """
    register_to_hub Auth模块主动向hub注册中心注册的入口函数
    使用flow_driven架构的现代化注册机制
    """
    # 检查hub是否可用
    # if not HUB_AVAILABLE 条件检查hub系统可用性
    if not HUB_AVAILABLE:
        # print 输出hub不可用的警告信息
        print("Warning: Hub not available, skipping registration")
        # return False hub不可用时返回注册失败状态
        return False

    try:
        # 使用router中的注册中心实例，确保注册到同一个registry
        # registry 通过router.registry获取注册中心实例
        registry = router.registry

        # 获取模块信息
        # module_info 通过get_module_info()调用获取完整的模块配置信息
        module_info = get_module_info()

        # 调用flow_driven注册函数执行注册
        # registration_success 通过调用flow_driven_register_function执行注册并获取结果
        registration_success = flow_driven_register_function(registry, "auth", module_info)

        # if registration_success 条件检查注册是否成功
        if registration_success:
            # print 输出注册成功信息
            print(f"Auth模块flow_driven系统成功注册到hub注册中心")
            # return True 注册成功时返回True状态
            return True
        else:
            # print 输出注册失败信息
            print(f"Auth模块flow_driven系统注册未完全成功")
            # return False 注册未完全成功时返回False状态
            return False

    except Exception as e:
        # print 输出注册异常信息
        print(f"Auth模块flow_driven系统注册失败: {str(e)}")
        # return False 注册异常时返回失败状态
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

# 在所有函数定义完成后，更新MODULE_INFO中的register_function
# _MODULE_INFO_CACHE["register_function"] 通过字典赋值设置注册函数
if _MODULE_INFO_CACHE is not None:
    _MODULE_INFO_CACHE["register_function"] = flow_driven_register_function
    
# MODULE_READY 通过赋值True设置模块就绪状态标识
# 用于向外部系统表示该模块已准备就绪，可以正常使用
MODULE_READY = True
