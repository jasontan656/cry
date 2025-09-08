# router.py 作为业务路由的核心模块
# 核心设计理念：纯路由转发，根据intent名称直接分发请求到对应的业务模块
# 负责基于意图名称的简单路由，不进行任何业务逻辑处理
#
# 路由架构：
# 1. 路由层：所有intent都直接路由到对应的模块处理
# 2. 注册层：所有intent都通过registry_center注册管理，支持模块自治
#
# 实现简单的intent到模块的映射，不进行编排或状态管理

# 导入标准库
import asyncio
from typing import Dict, Any, Optional, Union, List, Callable
import copy

# 从当前目录导入 registry_center 模块
# 用于获取模块注册信息和处理函数
from .registry_center import RegistryCenter


class Router:
    """
    Router 类作为中枢的简单意图路由器

    核心设计理念：纯路由转发，所有intent都直接路由到对应模块
    不再进行编排逻辑，让模块自主管理业务流程和状态

    设计原则：
    1. 模块自治：每个模块自己管理状态和流程逻辑
    2. 路由简化：只负责intent到模块的映射
    3. 状态驱动：模块通过数据库读取用户状态自主决策

    路由机制：
    - 路由层：所有intent都直接路由到对应模块处理
    - 注册层：所有intent通过registry_center统一注册管理

    基于 registry_center 提供的模块注册信息，实现简单的intent路由
    不进行业务逻辑处理，让模块完全自治
    """

    def __init__(self):
        # RegistryCenter 实例通过 RegistryCenter() 创建单例实例
        # 用于获取模块注册信息和意图处理函数
        self.registry = RegistryCenter()


    def get_registered_intents(self) -> List[str]:
        """
        get_registered_intents 方法获取所有已注册的意图列表
        返回当前系统支持的所有意图名称
        
        返回:
            意图名称字符串列表
        """
        # 通过 registry 的 intent_handlers 获取所有已注册意图
        # 返回意图名称列表
        return list(self.registry.intent_handlers.keys())

    async def route(self, intent: str, request_body: dict) -> Dict[str, Any]:
        """
        route 方法作为 Router 类的核心路由方法
        核心设计理念：纯路由转发，简单地将intent映射到对应模块

        路由逻辑：
        1. 根据intent名称查找对应的模块处理器
        2. 直接调用模块处理器，传入原始请求数据
        3. 返回模块的处理结果

        Intent处理逻辑：
        - 所有intent都直接路由到对应的模块处理
        - 不进行任何编排或状态检查逻辑
        - 模块完全自治，负责自己的业务逻辑

        参数:
            intent: 意图名称字符串
            request_body: 请求载荷数据字典，包含业务数据

        返回:
            处理结果字典，包含模块执行结果
        """
        # === 路由处理层 ===
        # 所有intent都直接路由到对应的模块处理
        # 不进行编排逻辑，只负责intent到模块的映射

        # 通过 registry 的 get_handler_for_intent 方法查找意图处理器
        # handler_func 接收对应意图的处理函数引用
        handler_func = self.registry.get_handler_for_intent(intent)

        # 如果未找到对应的意图处理器，返回错误响应
        if not handler_func:
            return {
                "error": f"No handler registered for intent: {intent}",
                "intent": intent,
                "status": "handler_not_found"
            }

        try:
            # 直接调用意图处理函数，传入原始请求数据
            # router只负责路由，不进行任何业务逻辑处理
            result = await handler_func(request_body)

            # 将执行结果包装为标准响应格式并返回
            return {
                "status": "success",
                "intent": intent,
                "result": result
            }

        except Exception as e:
            # 如果执行过程中发生异常，返回错误信息
            return {
                "error": f"Intent execution failed: {str(e)}",
                "intent": intent,
                "status": "execution_error"
            }


# router 通过 Router() 创建路由器实例
# 用于处理 orchestrate 的业务路由逻辑
router = Router()

# orchestrate_entry 函数作为 orchestrate 模块的外部代理入口
# 设计理念：薄代理层，专门委托 Router.route() 处理路由逻辑
# 职责清晰分离：外部接口只做参数转发，路由逻辑由 Router 类负责
async def orchestrate_entry(intent: str, request_body: dict) -> Dict[str, Any]:
    """
    orchestrate_entry 函数作为 orchestrate 模块的外部代理入口
    设计理念：作为薄代理层，委托 Router.route() 处理路由逻辑

    职责范围：
    - 接收外部请求参数
    - 将请求转发给 Router.route() 方法处理
    - 返回处理结果，不包含任何业务逻辑

    这是架构简化的体现：外部接口 → 路由器 → 模块处理器

    参数:
        intent: 意图名称字符串，直接传递给 Router.route() 方法
        request_body: 请求载荷数据字典，直接传递给 Router.route() 方法

    返回:
        Router.route() 方法的处理结果字典
    """
    # 通过 router.route 方法处理意图请求
    # 传入 intent 和 request_body 参数到路由器
    # await 等待异步执行完成后返回结果作为函数返回值
    return await router.route(intent, request_body)