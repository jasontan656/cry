"""
hub.py - Career Bot 系统现代化主入口文件
职责：接收各个模块和前端的请求，中转到现代化router流程调度器处理
新增：支持流程注册初始化钩子，确保系统启动时完成所有流程注册
"""

# 从当前目录导入现代化 router 模块的 hub_entry 函数
# 作为统一的请求处理入口，所有流程调度逻辑都在 router 中完成
from hub.router import hub_entry

# 导入流程管理模块，用于初始化阶段的流程注册支持
from hub.flow import flow_registry
from hub.registry_center import RegistryCenter

# 创建全局注册中心实例，用于模块注册管理
_hub_registry = RegistryCenter()


def register_module(module_info):
    """
    register_module 函数为外部模块提供注册入口
    现代化设计：支持模块通过 register_function 自主完成流程注册
    
    参数:
        module_info: 模块信息字典，包含 name、register_function 等
    
    返回:
        None
    """
    # _hub_registry.register_module 通过调用注册中心注册模块
    # 传入模块信息，触发模块的自主注册流程
    _hub_registry.register_module(module_info)


def get_flow_registry():
    """
    get_flow_registry 函数提供对全局流程注册中心的访问
    供外部模块在初始化时获取流程注册中心引用
    
    返回:
        FlowRegistry: 全局流程注册中心实例
    """
    # 返回全局 flow_registry 实例
    return flow_registry


def get_registry_center():
    """
    get_registry_center 函数提供对注册中心的访问
    供外部模块获取注册中心实例进行高级操作
    
    返回:
        RegistryCenter: 全局注册中心实例
    """
    # 返回全局 _hub_registry 实例
    return _hub_registry


def validate_system_integrity():
    """
    validate_system_integrity 函数提供系统完整性验证
    在系统启动或运维检查时调用，生成完整性报告
    
    返回:
        Dict[str, Any]: 系统完整性验证报告
    """
    # flow_registry.validate_all_flows_integrity 通过调用流程注册中心
    # 生成系统级流程完整性报告
    return flow_registry.validate_all_flows_integrity()


async def run(request):
    """
    模块统一入口函数，供外部系统调用
    现代化设计：中转职责，直接将请求转发给现代化流程调度器处理

    参数：
        request: 包含intent（现为step_id）和其他数据的请求字典

    返回：
        现代化响应结果字典，包含流程信息和执行状态
    """
    # 从 request 中提取 intent（现作为step_id）和其他数据
    intent = request.get("intent")
    
    # Fast Fail: invalid intent must not touch DB / status recovery
    # 如果没有找到 intent 字段，立即抛出预设异常避免动态构建
    if not intent:
        from hub.router import InvalidIntentError
        raise InvalidIntentError("missing", "Missing intent field in request")
    
    # 创建 request_body，移除 intent 字段，保留其他数据
    request_body = {k: v for k, v in request.items() if k != "intent"}
    
    # 通过现代化的 hub_entry 函数处理请求
    # 传入 intent（作为step_id）和 request_body 参数到现代化流程调度器
    # await 等待异步执行完成后返回结果作为函数返回值
    return await hub_entry(intent, request_body)
