# __init__.py - MBTI模块热插拔接口定义
# sys 通过 import 导入系统模块，用于路径操作
import sys
# os 通过 import 导入操作系统接口模块，用于文件路径处理
import os
# 导入类型提示模块，用于流程跳转校验函数的类型定义
from typing import Dict, Any
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
    get_all_field_definitions
)
# from applications.mbti.flow_router import flow_router, process_with_flow_context
# 通过绝对导入路径applications.mbti.flow_router获取flow_router实例
# 和process_with_flow_context函数，用于流程驱动路由和请求处理
from applications.mbti.flow_router import flow_router, process_with_flow_context

# 导入流程定义模块，用于流程驱动架构支持
from applications.mbti.flow_definition import register_mbti_flow, get_mbti_flow_definition, get_mbti_flow_steps

# 导入hub注册中心和流程管理模块，用于模块主动注册
try:
    from hub.router import router as hub_router
    from hub.flow import flow_registry
    from hub.status import user_status_manager
    from hub.registry_center import RegistryCenter
    HUB_AVAILABLE = True
except ImportError:
    HUB_AVAILABLE = False

# def get_user_flow_snapshot(user_id, flow_id) 定义获取用户流程状态快照的函数
# 函数接收用户ID和流程ID参数，返回用户在指定流程中的状态信息
def get_user_flow_snapshot(user_id: str, flow_id: str = "mbti_personality_test"):
    """
    获取用户流程状态快照
    通过user_status_manager获取用户在指定流程中的完整状态信息
    
    参数:
        user_id: 用户标识符字符串
        flow_id: 流程标识符字符串，默认为MBTI流程
    
    返回:
        Dict: 包含用户流程状态的字典
    """
    # 检查hub是否可用
    if not HUB_AVAILABLE:
        return {"error": "Hub not available", "exists": False}
    
    try:
        # import asyncio 导入异步执行模块，用于运行异步函数
        import asyncio
        # 检查当前是否在事件循环中运行
        try:
            loop = asyncio.get_running_loop()
            # 如果在事件循环中，使用concurrent.futures来执行
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, user_status_manager.get_flow_snapshot(user_id, flow_id))
                return future.result(timeout=10)
        except RuntimeError:
            # 如果没有运行的事件循环，使用asyncio.run
            return asyncio.run(user_status_manager.get_flow_snapshot(user_id, flow_id))
    except Exception as e:
        # 捕获异常并返回错误信息字典
        return {"error": f"Get flow snapshot failed: {str(e)}", "exists": False}

# def restore_user_flow_context(user_id, flow_id, target_step) 定义恢复用户流程上下文的函数
# 函数接收用户ID、流程ID和目标步骤参数，返回恢复操作的结果
def restore_user_flow_context(user_id: str, flow_id: str, target_step: str):
    """
    恢复用户流程上下文到指定步骤
    通过user_status_manager恢复用户在流程中的执行上下文
    
    参数:
        user_id: 用户标识符字符串
        flow_id: 流程标识符字符串
        target_step: 目标步骤标识符字符串
    
    返回:
        Dict: 包含恢复操作结果的字典
    """
    # 检查hub是否可用
    if not HUB_AVAILABLE:
        return {"success": False, "error": "Hub not available"}
    
    try:
        # import asyncio 导入异步执行模块，用于运行异步函数
        import asyncio
        # 检查当前是否在事件循环中运行
        try:
            loop = asyncio.get_running_loop()
            # 如果在事件循环中，使用concurrent.futures来执行
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, user_status_manager.restore_flow_context(user_id, flow_id, target_step))
                return future.result(timeout=10)
        except RuntimeError:
            # 如果没有运行的事件循环，使用asyncio.run
            return asyncio.run(user_status_manager.restore_flow_context(user_id, flow_id, target_step))
    except Exception as e:
        # 捕获异常并返回错误信息字典
        return {"success": False, "error": f"Restore flow context failed: {str(e)}"}

# def get_flow_progress_info(user_id, flow_id) 定义获取流程进度信息的函数
# 函数接收用户ID和流程ID参数，返回用户在流程中的进度信息
def get_flow_progress_info(user_id: str, flow_id: str = "mbti_personality_test"):
    """
    获取用户流程进度信息
    结合用户状态快照和流程注册信息计算进度百分比
    
    参数:
        user_id: 用户标识符字符串
        flow_id: 流程标识符字符串，默认为MBTI流程
    
    返回:
        Dict: 包含流程进度信息的字典
    """
    # 检查hub是否可用
    if not HUB_AVAILABLE:
        return {"error": "Hub not available", "progress": 0}
    
    try:
        # get_user_flow_snapshot 通过调用获取用户流程状态快照
        # 传入user_id和flow_id参数，获取当前流程状态
        user_snapshot = get_user_flow_snapshot(user_id, flow_id)
        
        # 如果快照不存在或获取失败，返回错误信息
        if not user_snapshot.get("exists"):
            return {"error": "User flow state not found", "progress": 0}
        
        # current_step 从快照中获取当前步骤标识符
        current_step = user_snapshot.get("current_step")
        
        if current_step:
            # flow_registry.get_flow_progress 通过调用获取流程进度信息
            # 传入flow_id和current_step参数，计算进度百分比和剩余步骤
            return flow_registry.get_flow_progress(flow_id, current_step)
        else:
            return {"error": "Current step not found", "progress": 0}
            
    except Exception as e:
        # 捕获异常并返回错误信息字典
        return {"error": f"Get flow progress failed: {str(e)}", "progress": 0}

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
            # "router" 键赋值为之前导入的flow_router实例
            "router": flow_router,
            # "process_mbti_request" 键赋值为之前导入的process_with_flow_context函数
            "process_mbti_request": process_with_flow_context,
            "flow": {  # 流程相关接口字典，提供流程定义和状态管理功能
                # "get_mbti_flow_definition" 键赋值为get_mbti_flow_definition函数引用
                # 用于获取MBTI流程的完整定义结构
                "get_mbti_flow_definition": get_mbti_flow_definition,
                # "get_mbti_flow_steps" 键赋值为get_mbti_flow_steps函数引用
                # 用于获取MBTI流程的所有步骤定义列表
                "get_mbti_flow_steps": get_mbti_flow_steps,
                # "get_user_flow_snapshot" 键赋值为get_user_flow_snapshot函数引用
                # 用于获取用户在流程中的状态快照
                "get_user_flow_snapshot": get_user_flow_snapshot,
                # "restore_user_flow_context" 键赋值为restore_user_flow_context函数引用
                # 用于恢复用户流程上下文到指定步骤
                "restore_user_flow_context": restore_user_flow_context,
                # "get_flow_progress_info" 键赋值为get_flow_progress_info函数引用
                # 用于获取用户在流程中的进度信息
                "get_flow_progress_info": get_flow_progress_info
            },
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
        "hub_info": {  # 编排信息字典
            # "supported_intents" 键赋值为具体的意图字符串列表
            # 包含mbti_step1到mbti_step5的完整意图标识，以及数据库查询和模块编排相关的intent，匹配flow_router.py和step1.py中的实际处理逻辑
            "supported_intents": ["mbti_step1", "mbti_step2", "mbti_step3", "mbti_step4", "mbti_step5", "mongodb_connector_query", "hub_next_module"],
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
                # "step_hub" 键赋值为编排函数的完整路径字符串
                # 指向applications.mbti.flow_router模块的process_with_flow_context方法
                "step_hub": "applications.mbti.flow_router.process_with_flow_context",
                # "result_storage" 键赋值为存储函数的完整路径字符串
                # 指向hub模块的mongodb_connector存储功能
                "result_storage": "hub.mongodb_connector.save_mbti_result"
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
        # hub 作为强依赖，提供中枢路由和模块间通信能力
        # mongodb_connector 作为间接强依赖，提供用户状态读取和任务断点续传功能
        # frontend 和 entry 作为请求入口模块，提供intent请求的传入途径
        "dependencies": [
            # time.py 模块被列为强依赖项
            # 没有time.py时程序无法正确运行uuid+时间戳封包功能
            "time",
            # hub 模块被列为强依赖项
            # 没有hub中枢时模块无法激活使用和与其他模块通信
            "hub",
            # mongodb_connector 模块被列为间接强依赖项
            # 没有mongodb_connector时无法读取用户状态进行断点续传
            # 会导致MBTI测试总是从第一步开始
            "mongodb_connector",
            # frontend 模块被列为请求入口依赖项
            # 前端模块负责触发intent请求的界面交互
            # 没有frontend时用户无法发起MBTI测试请求
            "frontend",
            # entry 模块被列为请求入口依赖项
            # entry模块作为intent白名单模块，负责读取hub中注册的所有intent
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
            "compatibility": "hub v1.0+",
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
        # "hub_info" 键赋值为MODULE_INFO["hub_info"]获取编排信息
        "hub_info": MODULE_INFO["hub_info"]
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

# def get_hub_info() 定义获取编排信息的函数
# 函数不接收参数，返回包含动态字段映射的编排信息字典
def get_hub_info():
    """
    获取编排信息（动态生成）
    返回：包含动态字段映射的编排信息字典
    """
    # _get_module_info()["hub_info"] 通过调用动态获取编排信息
    # 不传入参数，返回包含通过schemas.py动态获取的字段映射信息的字典
    # 包含step_flow、data_flow和field_mappings等编排相关信息
    return _get_module_info()["hub_info"]

# def mbti_register_function(registry, module_name, module_info) 定义MBTI模块的注册函数（流程驱动版本）
# 函数接收注册中心实例、模块名和模块信息，实现自主注册逻辑，并整合流程定义和步骤注册
async def mbti_register_function(registry, module_name, module_info):
    """
    MBTI模块的自主注册函数（流程驱动版本），向注册中心注册模块能力、处理器和流程定义
    符合hub/flow_example.py标准的完整流程驱动架构
    
    参数:
        registry: RegistryCenter实例，注册中心对象
        module_name: 模块名称字符串
        module_info: 模块信息字典
    """
    print(f"=== 开始注册MBTI模块到流程驱动架构 ===")
    
    # === 1. 注册模块基础信息 ===
    
    # 注册模块元信息到registry.module_meta
    registry.module_meta[module_name] = module_info
    
    # 注册模块字段信息到registry.module_fields
    if "interface" in module_info and "schemas" in module_info["interface"]:
        registry.module_fields[module_name] = module_info["interface"]["schemas"]
    
    # 注册模块依赖关系到registry.dependencies
    if "dependencies" in module_info:
        registry.dependencies[module_name] = module_info["dependencies"]
    
    # === 2. 现代化架构：跳过旧的intent_handlers注册 ===
    # 
    # 注意：移除传统的 intent_handlers 注册机制
    # 现代架构中，所有步骤处理器通过 register_mbti_flow() 函数
    # 直接注册到 flow_registry，实现流程驱动的统一管理
    print("✓ 跳过传统intent_handlers注册，使用现代化流程注册机制")
    
    # === 3. 注册MBTI流程定义和步骤 ===
    
    try:
        # register_mbti_flow 通过await调用异步注册MBTI流程到流程调度系统
        # 包含完整的流程定义和步骤链接关系注册
        flow_registered = await register_mbti_flow()
        
        if flow_registered:
            print(f"✓ MBTI流程注册到流程调度系统成功")
        else:
            print(f"✗ MBTI流程注册到流程调度系统失败")
            
    except Exception as e:
        print(f"MBTI流程注册异常: {str(e)}")
    
    # === 4. 添加流程跳转校验支持 ===
    
    # 为registry添加流程跳转校验方法（如果不存在）
    if not hasattr(registry, 'validate_flow_transition'):
        registry.validate_flow_transition = _create_flow_transition_validator(registry)
    
    print(f"=== MBTI模块注册到流程驱动架构完成 ===\n")


def _create_flow_transition_validator(registry):
    """
    _create_flow_transition_validator 函数创建流程跳转校验器
    为RegistryCenter添加流程跳转校验能力，集成flow_registry功能
    
    参数:
        registry: RegistryCenter实例
        
    返回:
        Callable: 流程跳转校验函数
    """
    def validate_flow_transition(user_id: str, from_step: str, to_step: str) -> Dict[str, Any]:
        """
        validate_flow_transition 方法验证流程步骤跳转的合法性
        集成flow_registry的跳转校验逻辑
        
        参数:
            user_id: 用户ID字符串
            from_step: 起始步骤标识
            to_step: 目标步骤标识
        
        返回:
            Dict[str, Any]: 校验结果字典
        """
        try:
            # 获取起始步骤和目标步骤的定义
            from_step_def = flow_registry.get_step(from_step)
            to_step_def = flow_registry.get_step(to_step)
            
            if not from_step_def or not to_step_def:
                return {
                    "valid": False,
                    "reason": f"步骤定义不存在: {from_step if not from_step_def else to_step}",
                    "transition_type": "invalid"
                }
            
            # 检查是否为合法的下一步骤跳转
            if from_step_def.next_step == to_step:
                return {
                    "valid": True,
                    "reason": "正常步骤跳转",
                    "transition_type": "forward"
                }
            
            # 检查是否为合法的回退跳转
            if to_step_def.next_step == from_step:
                return {
                    "valid": True,
                    "reason": "步骤回退",
                    "transition_type": "backward"
                }
            
            # 非法跳转
            return {
                "valid": False,
                "reason": f"不允许从 {from_step} 跳转到 {to_step}",
                "transition_type": "illegal"
            }
            
        except Exception as e:
            return {
                "valid": False,
                "reason": f"跳转校验异常: {str(e)}",
                "transition_type": "error"
            }
    
    return validate_flow_transition

# def register_to_hub() 定义主动注册到中枢的函数（流程驱动版本）
# 函数不接收参数，执行MBTI模块向hub注册中心的主动注册，包含流程和步骤注册
async def register_to_hub():
    """
    MBTI模块主动向hub注册中心注册（流程驱动版本）
    实现模块自治的注册机制，包含完整的流程驱动架构支持
    """
    # 检查hub是否可用
    if not HUB_AVAILABLE:
        print("Warning: Hub not available, skipping registration")
        return False
    
    try:
        # 使用hub_router中的注册中心实例，确保注册到同一个registry
        registry = hub_router.registry if hasattr(hub_router, 'registry') else RegistryCenter()
        
        # 获取模块信息并添加注册函数
        module_info = get_module_info()
        module_info['register_function'] = mbti_register_function
        
        # 调用注册中心的register_module方法进行注册（需要异步支持）
        if hasattr(registry, 'register_module'):
            # 如果register_module是同步方法
            registry.register_module(module_info)
        else:
            # 直接调用异步注册函数
            await mbti_register_function(registry, module_info.get('name'), module_info)
        
        print(f"MBTI模块成功注册到hub注册中心（流程驱动架构）")
        return True
        
    except Exception as e:
        print(f"MBTI模块注册失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

# 模块加载时自动注册到hub（流程驱动版本）
# 只有在hub可用时才执行注册，使用异步执行方式
if HUB_AVAILABLE:
    import asyncio
    
    # _register_mbti_module 通过异步方式执行模块注册到流程驱动架构
    async def _register_mbti_module():
        """异步执行MBTI模块注册到hub流程驱动架构"""
        try:
            # await register_to_hub() 异步调用注册函数
            success = await register_to_hub()
            if success:
                print("MBTI模块已成功集成到流程驱动架构")
            else:
                print("MBTI模块集成到流程驱动架构失败")
        except Exception as e:
            print(f"MBTI模块异步注册异常: {str(e)}")
    
    # 尝试在事件循环中执行异步注册
    try:
        # asyncio.get_event_loop() 获取当前事件循环，并运行异步注册函数
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # 如果事件循环正在运行，创建任务
            asyncio.create_task(_register_mbti_module())
        else:
            # 如果事件循环未运行，直接运行
            loop.run_until_complete(_register_mbti_module())
    except RuntimeError:
        # 如果没有事件循环，创建新的事件循环
        try:
            asyncio.run(_register_mbti_module())
        except Exception as e:
            print(f"无法执行异步注册: {str(e)}，跳过流程驱动架构集成")

# MODULE_READY 通过赋值True设置模块就绪状态标识
# 用于向外部系统表示该模块已准备就绪，可以正常使用
MODULE_READY = True
