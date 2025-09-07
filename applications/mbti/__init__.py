# __init__.py - MBTI模块热插拔接口定义
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

# from applications.mbti.mbti import run as execute
# 通过绝对导入路径applications.mbti.mbti获取run函数
# 并将其重命名为execute，用于统一模块执行入口
from applications.mbti.mbti import run as execute
# from applications.mbti.schemas import 导入多个字段定义相关函数和变量
# 包含FIELD_DEFINITIONS字典、schema_manager实例等多个导入项
from applications.mbti.schemas import (
    # FIELD_DEFINITIONS 导入字段定义规范字典
    FIELD_DEFINITIONS,
    # schema_manager 导入字段管理器SchemaManager实例
    schema_manager,
    # get_field_types 导入获取字段类型映射的函数
    get_field_types,
    # get_field_groups 导入获取字段分组映射的函数
    get_field_groups,
    # get_request_fields 导入获取请求字段列表的函数
    get_request_fields,
    # get_response_fields 导入获取响应字段列表的函数
    get_response_fields,
    # get_reverse_question_fields 导入获取反向问题字段列表的函数
    get_reverse_question_fields,
    # get_assessment_fields 导入获取评估字段列表的函数
    get_assessment_fields,
    # get_valid_steps 导入获取有效步骤列表的函数
    get_valid_steps,
    # get_all_field_definitions 导入获取所有字段定义的函数
    get_all_field_definitions,
    # inject_to_target_module 导入向目标模块注入字段的函数
    inject_to_target_module
)
# from applications.mbti.router import router, process_mbti_request
# 通过绝对导入路径applications.mbti.router获取router实例
# 和process_mbti_request函数，用于路由和请求处理
from applications.mbti.router import router, process_mbti_request

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
    动态生成模块元信息，通过调用schemas.py获取字段定义
    返回：完整的模块信息字典
    """
    # get_all_field_definitions() 通过调用获取所有字段定义信息
    # 不传入参数，返回包含字段类型、分组、元数据的完整字典
    # 赋值给all_field_definitions变量用于后续模块信息构建
    all_field_definitions = get_all_field_definitions()

    # return 语句返回构建的动态模块信息字典
    # 字典包含name、version、description等静态信息
    # 以及通过调用schemas函数动态获取的interface和capabilities信息
    return {
        # "name" 键赋值为字符串"mbti"，标识模块名称
        "name": "mbti",
        # "version" 键赋值为字符串"1.0.0"，标识模块版本
        "version": "1.0.0",
        # "description" 键赋值为模块功能描述字符串
        "description": "MBTI性格测试中心模块",
        "interface": {  # 对外暴露的接口字典
            # "execute" 键赋值为之前导入的execute函数引用
            "execute": execute,
            # "validate" 键赋值为None，表示验证接口暂未实现
            "validate": None,
            # "router" 键赋值为之前导入的router实例
            "router": router,
            # "process_mbti_request" 键赋值为之前导入的process_mbti_request函数
            "process_mbti_request": process_mbti_request,
            "schemas": {  # 数据结构定义字典，包含动态获取的字段信息
                # "field_definitions" 键赋值为FIELD_DEFINITIONS字典
                "field_definitions": FIELD_DEFINITIONS,
                # "all_field_definitions" 键赋值为all_field_definitions变量
                # 该变量通过get_all_field_definitions()调用获得
                "all_field_definitions": all_field_definitions,
                # "schema_manager" 键赋值为schema_manager实例
                "schema_manager": schema_manager,
                # "get_field_types" 键赋值为get_field_types函数引用
                "get_field_types": get_field_types,
                # "get_field_groups" 键赋值为get_field_groups函数引用
                "get_field_groups": get_field_groups,
                # "get_request_fields" 键赋值为get_request_fields函数引用
                "get_request_fields": get_request_fields,
                # "get_response_fields" 键赋值为get_response_fields函数引用
                "get_response_fields": get_response_fields,
                # "get_reverse_question_fields" 键赋值为get_reverse_question_fields函数引用
                "get_reverse_question_fields": get_reverse_question_fields,
                # "get_assessment_fields" 键赋值为get_assessment_fields函数引用
                "get_assessment_fields": get_assessment_fields,
                # "get_valid_steps" 键赋值为get_valid_steps函数引用
                "get_valid_steps": get_valid_steps
            }
        },
        "capabilities": {  # 模块能力声明字典
            "personality_test": {  # MBTI性格测试能力字典
                # "steps" 键通过get_valid_steps()调用获取有效步骤列表
                # 不传入参数，返回包含step1到step5的完整列表
                "steps": get_valid_steps(),
                # "description" 键赋值为详细的功能描述字符串
                # 说明完整的MBTI测试流程包括引导、计算、反向测试和报告生成
                "description": "完整的MBTI性格测试流程，包括初始测试、类型计算、反向验证和最终报告"
            },
            "mbti_analysis": {  # MBTI分析处理能力字典
                # "input_types" 键通过get_request_fields()调用获取请求字段列表
                # 不传入参数，返回包含request_id、user_id、responses等输入字段的列表
                "input_types": get_request_fields(),
                # "output_types" 键通过get_response_fields()调用获取响应字段列表
                # 不传入参数，返回包含success、step、mbti_type、final_report等输出字段的列表
                "output_types": get_response_fields()
            }
        },
        "orchestrate_info": {  # 编排信息字典
            # "supported_intents" 键赋值为具体的意图字符串列表
            # 包含mbti_step1到mbti_step5的完整意图标识，以及数据库查询和模块编排相关的intent，匹配router.py和step1.py中的实际处理逻辑
            "supported_intents": ["mbti_step1", "mbti_step2", "mbti_step3", "mbti_step4", "mbti_step5", "database_query", "orchestrate_next_module"],
            "step_flow": {  # 步骤流程定义字典
                # "step1" 键赋值为包含next和description的字典，表示初始MBTI测试引导
                "step1": {"next": "step2", "description": "初始MBTI测试引导"},
                # "step2" 键赋值为包含next和description的字典，表示MBTI类型计算
                "step2": {"next": "step3", "description": "MBTI类型计算"},
                # "step3" 键赋值为包含next和description的字典，表示反向问题生成
                "step3": {"next": "step4", "description": "反向问题生成"},
                # "step4" 键赋值为包含next和description的字典，表示反向问题计分
                "step4": {"next": "step5", "description": "反向问题计分"},
                # "step5" 键赋值为包含next和description的字典，表示最终报告生成
                "step5": {"next": None, "description": "最终报告生成"}
            },
            "data_flow": {  # 数据流转定义字典
                # "step_orchestrate" 键赋值为编排函数的完整路径字符串
                # 指向applications.mbti.router模块的process方法
                "step_orchestrate": "applications.mbti.router.process",
                # "result_storage" 键赋值为存储函数的完整路径字符串
                # 指向orchestrate模块的database存储功能
                "result_storage": "orchestrate.database.save_mbti_result"
            },
            "field_mappings": {  # 字段映射信息字典（动态获取）
                # "request_fields" 键通过get_request_fields()调用获取请求字段列表
                # 不传入参数，返回包含request_id、user_id等字段的列表
                "request_fields": get_request_fields(),
                # "response_fields" 键通过get_response_fields()调用获取响应字段列表
                # 不传入参数，返回包含request_id、success等字段的列表
                "response_fields": get_response_fields(),
                # "assessment_fields" 键通过get_assessment_fields()调用获取评估字段列表
                # 不传入参数，返回包含dimension_type、assessment_result等字段的列表
                "assessment_fields": get_assessment_fields()
            }
        },
        # "dependencies" 键赋值包含模块依赖关系的列表
        # 包含强依赖、间接强依赖和请求入口模块
        # time.py 作为强依赖，提供uuid+时间戳封包工具
        # orchestrate 作为强依赖，提供中枢路由和模块间通信能力
        # database 作为间接强依赖，提供用户状态读取和任务断点续传功能
        # frontend 和 entry 作为请求入口模块，提供intent请求的传入途径
        "dependencies": [
            # time.py 模块被列为强依赖项
            # 没有time.py时程序无法正确运行uuid+时间戳封包功能
            "time",
            # orchestrate 模块被列为强依赖项
            # 没有orchestrate中枢时模块无法激活使用和与其他模块通信
            "orchestrate",
            # database 模块被列为间接强依赖项
            # 没有database时无法读取用户状态进行断点续传
            # 会导致MBTI测试总是从第一步开始
            "database",
            # frontend 模块被列为请求入口依赖项
            # 前端模块负责触发intent请求的界面交互
            # 没有frontend时用户无法发起MBTI测试请求
            "frontend",
            # entry 模块被列为请求入口依赖项
            # entry模块作为intent白名单模块，负责读取orchestrate中注册的所有intent
            # 使用注册的intent作为白名单来验证和放行前端请求
            # 没有entry时前端请求无法通过intent验证，无法传递到MBTI模块
            "entry"
        ],
        "metadata": {  # 模块元数据字典
            # "author" 键赋值为开发团队字符串
            "author": "Career Bot Team",
            # "created" 键赋值为创建日期字符串
            "created": "2024-09-05",
            # "last_modified" 键赋值为最后修改日期字符串
            "last_modified": "2024-09-05",
            # "compatibility" 键赋值为兼容性要求字符串
            "compatibility": "orchestrate v1.0+",
            # "license" 键赋值为使用许可字符串
            "license": "Internal Use Only",
            # "field_count" 键通过len(get_field_types())调用计算字段总数
            # get_field_types()不传入参数，返回字段类型字典，然后len()计算其长度
            "field_count": len(get_field_types()),
            # "schema_version" 键赋值为字段定义版本字符串
            "schema_version": "2.0.0"
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
        # 不传入参数，返回包含通过schemas.py获取的所有字段定义的字典
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
    # 传入字符串消息"MBTI Agent模块初始化完成"
    logger.info("MBTI Agent模块初始化完成")

    # schema_manager 通过引用触发字段管理器初始化
    # 这会调用SchemaManager的__init__方法，加载JSON数据并注入字段
    schema_manager

    # return 语句返回包含初始化状态的字典
    return {
        # "status" 键赋值为字符串"initialized"表示初始化成功
        "status": "initialized",
        # "capabilities" 键赋值为MODULE_INFO["capabilities"]获取模块能力信息
        "capabilities": MODULE_INFO["capabilities"],
        # "orchestrate_info" 键赋值为MODULE_INFO["orchestrate_info"]获取编排信息
        "orchestrate_info": MODULE_INFO["orchestrate_info"]
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
    # 传入字符串消息"MBTI Agent模块清理完成"
    logger.info("MBTI Agent模块清理完成")
    # return 语句返回包含清理状态的字典
    return {"status": "cleaned"}

# def get_module_info() 定义获取模块完整信息的函数
# 函数不接收参数，返回包含动态字段定义的完整模块信息字典
def get_module_info():
    """
    获取模块完整信息（动态生成）
    返回：包含动态字段定义的完整模块信息字典
    """
    # _get_module_info() 通过调用获取动态生成的模块信息
    # 不传入参数，返回包含最新字段定义信息的完整字典
    # 每次调用都会确保获取最新的字段定义信息
    return _get_module_info()

# def get_capabilities() 定义获取模块能力列表的函数
# 函数不接收参数，返回包含动态字段信息的模块能力字典
def get_capabilities():
    """
    获取模块能力列表（动态生成）
    返回：包含动态字段信息的模块能力字典
    """
    # _get_module_info()["capabilities"] 通过调用动态获取模块能力信息
    # 不传入参数，返回包含通过schemas.py动态获取的字段信息的字典
    # 包含personality_test和mbti_analysis能力定义
    return _get_module_info()["capabilities"]

# def get_orchestrate_info() 定义获取编排信息的函数
# 函数不接收参数，返回包含动态字段映射的编排信息字典
def get_orchestrate_info():
    """
    获取编排信息（动态生成）
    返回：包含动态字段映射的编排信息字典
    """
    # _get_module_info()["orchestrate_info"] 通过调用动态获取编排信息
    # 不传入参数，返回包含通过schemas.py动态获取的字段映射信息的字典
    # 包含step_flow、data_flow和field_mappings等编排相关信息
    return _get_module_info()["orchestrate_info"]

# def mbti_register_function(registry, module_name, module_info) 定义MBTI模块的注册函数
# 函数接收注册中心实例、模块名和模块信息，实现自主注册逻辑
def mbti_register_function(registry, module_name, module_info):
    """
    MBTI模块的自主注册函数，向注册中心注册模块能力和处理器
    
    参数:
        registry: RegistryCenter实例，注册中心对象
        module_name: 模块名称字符串
        module_info: 模块信息字典
    """
    # 注册模块元信息到registry.module_meta
    registry.module_meta[module_name] = module_info
    
    # 注册模块字段信息到registry.module_fields
    if "interface" in module_info and "schemas" in module_info["interface"]:
        registry.module_fields[module_name] = module_info["interface"]["schemas"]
    
    # 注册模块依赖关系到registry.dependencies
    if "dependencies" in module_info:
        registry.dependencies[module_name] = module_info["dependencies"]
    
    # 注册意图处理器到registry.intent_handlers
    # 从模块信息中获取支持的意图列表
    supported_intents = module_info.get("orchestrate_info", {}).get("supported_intents", [])
    
    # 为每个支持的意图注册处理器
    for intent in supported_intents:
        if intent == "mbti_step1":
            # 导入step1处理器并注册（使用实际存在的process函数）
            from applications.mbti.step1 import process
            registry.intent_handlers[intent] = process
        elif intent == "mbti_step2":
            # 导入step2处理器并注册
            from applications.mbti.step2 import process
            registry.intent_handlers[intent] = process
        elif intent == "mbti_step3":
            # 导入step3处理器并注册
            from applications.mbti.step3 import process
            registry.intent_handlers[intent] = process
        elif intent == "mbti_step4":
            # 导入step4处理器并注册
            from applications.mbti.step4 import process
            registry.intent_handlers[intent] = process
        elif intent == "mbti_step5":
            # 导入step5处理器并注册
            from applications.mbti.step5 import process
            registry.intent_handlers[intent] = process

# def register_to_orchestrate() 定义主动注册到中枢的函数
# 函数不接收参数，执行MBTI模块向orchestrate注册中心的主动注册
def register_to_orchestrate():
    """
    MBTI模块主动向orchestrate注册中心注册
    实现模块自治的注册机制
    """
    # 检查orchestrate是否可用
    if not ORCHESTRATE_AVAILABLE:
        print("Warning: Orchestrate not available, skipping registration")
        return False
    
    try:
        # 使用router中的注册中心实例，确保注册到同一个registry
        registry = router.registry
        
        # 获取模块信息并添加注册函数
        module_info = get_module_info()
        module_info['register_function'] = mbti_register_function
        
        # 调用注册中心的register_module方法进行注册
        registry.register_module(module_info)
        
        print(f"MBTI模块成功注册到orchestrate注册中心")
        return True
        
    except Exception as e:
        print(f"MBTI模块注册失败: {str(e)}")
        return False

# 模块加载时自动注册到orchestrate
# 只有在orchestrate可用时才执行注册
if ORCHESTRATE_AVAILABLE:
    register_to_orchestrate()

# MODULE_READY 通过赋值True设置模块就绪状态标识
# 用于向外部系统表示该模块已准备就绪，可以正常使用
MODULE_READY = True
