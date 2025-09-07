# router.py 作为业务编排的核心模块
# 核心设计理念：区分编排intent和普通路由intent，不一视同仁处理所有intent
# 负责基于意图名称动态分发请求到具体的业务模块
#
# Intent处理分层架构：
# 1. 编排层：只有 orchestrate_next_module 等明确请求编排的intent才进行编排
# 2. 路由层：其他所有intent（模块步骤、业务处理等）都走正常路由处理
# 3. 注册层：所有intent都通过registry_center注册管理，支持模块自治
#
# 实现基于模板的模块编排，支持异步嵌套的业务场景，但不主动干预普通路由

# 导入标准库
import asyncio
from typing import Dict, Any, Optional, Union, List, Callable
import copy

# 从当前目录导入 registry_center 模块
# 用于获取模块注册信息和处理函数
from .registry_center import RegistryCenter


class Router:
    """
    Router 类作为中枢的动态意图调度器

    核心设计理念：区分编排intent和普通路由intent，实现精准的任务分发

    设计原则：
    1. 反对强耦合流水线，转而支持模块独立性和灵活编排
    2. 模块应该是独立可复用的，而不是强制顺序依赖
    3. 支持异步嵌套编排：公司层面和职位层面分离管理
    4. 一个公司可发布多个职位，每个职位独立处理
    5. 只对明确请求编排的intent进行编排，其他intent走正常路由

    Intent处理分层：
    - 编排层：orchestrate_next_module 等明确请求编排的intent
    - 路由层：mbti_step1, company_identity_process 等普通业务intent
    - 注册层：所有intent通过registry_center统一注册管理

    基于 registry_center 提供的模块注册信息，实现意图驱动的智能路由分发
    支持模块依赖注入、上下文构建和基于模板的灵活编排，但不主动干预普通路由
    """

    def __init__(self):
        # RegistryCenter 实例通过 RegistryCenter() 创建单例实例
        # 用于获取模块注册信息和意图处理函数
        self.registry = RegistryCenter()

    def get_hardcoded_next_module(self, current_module: str) -> Optional[str]:
        """
        get_hardcoded_next_module 方法显式硬编码业务规则
        支持链式检查机制：用户点击一次，后台自动检查流程进度

        设计理念：
        - 每个模块的step1都有检查机制，检查用户是否已完成该步骤
        - 如果已完成，模块会请求中枢找下一个模块继续检查
        - 防循环机制：用户完成全流程后会被打上jobfindingregistrycomplate标记
        - mbti_step1检测到该标记时直接拒绝服务，避免无限循环

        参数:
            current_module: 当前正在执行的模块名称

        返回:
            下一个模块名称，如果已是流程末尾则返回 None
        """
        # 硬编码找工作流程规则：mbti -> ninetest -> final_analysis_output -> resume -> final_analysis_output -> taggings
        if current_module == "mbti":
            return "ninetest"
        elif current_module == "ninetest":
            return "final_analysis_output"
        elif current_module == "final_analysis_output":
            # 需要根据上下文判断是第一次还是第二次调用final_analysis_output
            # 这里简化为直接返回resume，实际可能需要更复杂的状态判断
            return "resume"
        elif current_module == "resume":
            return "final_analysis_output"  # 第二次调用final_analysis_output
        elif current_module == "taggings":
            return None  # 找工作流程结束，用户将被打上jobfindingregistrycomplate标记

        # 硬编码企业流程规则
        elif current_module == "company_identity":
            return "taggings"
        elif current_module == "jobpost":
            return "taggings"

        # 未知模块返回 None
        return None

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
        route 方法作为 Router 类的核心路由和编排处理方法
        核心设计理念：支持链式检查机制，用户点击一次，后台自动检查流程进度

        业务流程设计：
        1. 用户始终从 mbti_step1 触发流程
        2. 每个模块的step1都有检查机制：检查用户是否已完成该步骤
        3. 如果已完成，模块请求中枢找下一个模块继续检查
        4. 如果未完成，模块正常处理业务逻辑
        5. 防循环机制：完成全流程的用户被打上jobfindingregistrycomplate标记

        Intent处理分层逻辑：
        1. 编排相关intent（orchestrate_next_module）：返回下一个模块信息
        2. 模块步骤intent（如 mbti_step1）：路由到模块，模块内部决定是处理还是继续检查
        3. 其他注册intent：正常路由处理

        参数:
            intent: 意图名称字符串
            request_body: 请求载荷数据字典，包含业务数据

        返回:
            处理结果字典，包含模块执行结果或下一个模块信息
        """
        # === 编排相关intent处理层 ===
        # 只有明确请求编排下一个模块的intent才进行编排处理
        if intent == "orchestrate_next_module":
            # 从 request_body 中提取 current_module 参数
            current_module = request_body.get("current_module")

            # 检查必需参数是否存在
            if not current_module:
                return {
                    "error": "Missing required parameter: current_module",
                    "intent": intent,
                    "status": "invalid_request"
                }

            # 显式硬编码业务规则：根据当前模块确定下一个模块
            # 保持业务逻辑集中管理，避免各模块重复实现
            next_module = self.get_hardcoded_next_module(current_module)

            if not next_module:
                # 当前模块已是流程末尾，返回流程完成状态
                return {
                    "status": "flow_completed",
                    "current_module": current_module,
                    "message": "业务流程已完成"
                }

            # 返回下一个模块信息，让调用方决定是否继续链式检查
            # 设计理念：支持链式检查机制，防止无限循环
            # 调用方可以继续调用下一个模块的step1进行检查
            return {
                "status": "next_module_found", 
                "current_module": current_module,
                "next_module": next_module,
                "next_intent": f"{next_module}_step1"
            }

        # === 普通路由intent处理层 ===
        # 其他所有intent（包括模块步骤intent）都走正常的路由处理
        # 不进行主动编排，只是根据registry路由到对应模块

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
            # router只负责路由，不负责数据验证和上下文构建
            result = await handler_func(request_body)

            # 将执行结果包装为标准响应格式并返回
            # 注意：这里不进行主动编排，只是完成路由功能
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
# 设计理念：薄代理层，专门委托 Router.route() 处理所有业务逻辑
# 职责清晰分离：外部接口只做参数转发，核心逻辑由 Router 类负责
async def orchestrate_entry(intent: str, request_body: dict) -> Dict[str, Any]:
    """
    orchestrate_entry 函数作为 orchestrate 模块的外部代理入口
    设计理念：作为薄代理层，委托 Router.route() 处理所有业务逻辑

    职责范围：
    - 接收外部请求参数
    - 将请求转发给 Router.route() 方法处理
    - 返回处理结果，不包含任何业务逻辑

    这是架构分层的体现：外部接口 → 路由器代理 → 核心业务逻辑

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