# router.py - 严格控制的流程调度器
# 核心设计理念：基于严格intent验证的流程驱动路由
# 负责严格intent验证、限定状态恢复、拒绝fallback处理
#
# 严格架构：
# 1. intent白名单验证：只允许已注册的intent执行
# 2. 限定状态管理：仅特定intent可触发用户状态恢复
# 3. 异常强制抛出：任何无效intent都抛出结构化异常
#
# 完全移除fallback容错机制，实现报错即停的开发模式

# 导入标准库
from typing import Dict, Any, List

# 从当前目录导入 registry_center 模块，仅用于流程上下文支持
from .registry_center import RegistryCenter

# 创建全局共享的RegistryCenter实例，仅用于流程管理相关功能
_shared_registry = RegistryCenter()

# 从当前目录导入流程和状态管理模块 - 严格架构的核心
from .flow import FlowDefinition, FlowStep, flow_registry
from .status import StepExecutionContext, user_status_manager

# 从当前目录导入预设错误常量 - Fast Fail优化
from .error_presets import INVALID_INTENT, MISSING_INTENT, PROCESSING_ERROR


# ============ 严格Intent控制常量 ============

# STATEFUL_INTENT_WHITELIST 通过frozenset定义允许状态恢复的intent白名单
# 只有这些intent可以触发user_status_manager.get_user_flow_state()等恢复逻辑
STATEFUL_INTENT_WHITELIST = frozenset([
    'login',           # 登录intent允许状态恢复
    'restore_session', # 会话恢复intent允许状态恢复 
    'auto_resume',     # 自动恢复intent允许状态恢复
    'continue_flow',   # 继续流程intent允许状态恢复
    'recover_progress' # 进度恢复intent允许状态恢复
])


# ============ 严格Intent控制异常类 ============

class InvalidIntentError(Exception):
    """
    InvalidIntentError 异常类用于处理无效intent的严格控制
    当intent未在flow_registry中注册时抛出此异常，禁止fallback处理
    """
    
    # __init__ 方法初始化InvalidIntentError异常实例
    # intent 参数接收无效的intent字符串
    # message 参数接收可选的自定义错误信息
    def __init__(self, intent: str, message: str = None):
        # intent 通过参数传入赋值给实例属性
        self.intent = intent
        # default_message 通过f字符串格式化生成默认错误信息
        default_message = f"Invalid intent '{intent}' - not registered in flow_registry"
        # message 通过逻辑运算符选择自定义信息或默认信息
        self.message = message or default_message
        # super().__init__ 通过调用父类构造函数初始化异常
        super().__init__(self.message)
    
    # to_dict 方法将异常转换为结构化字典，用于API错误响应
    # Fast Fail: 使用预设错误字典，避免动态拼装异常报文
    def to_dict(self) -> Dict[str, Any]:
        # INVALID_INTENT.copy() 通过浅复制预设错误字典获取基础错误信息
        # 避免动态f-string构建，使用预构建常量提升性能
        error_dict = INVALID_INTENT.copy()
        # error_dict["intent"] 通过字典赋值添加具体的intent信息
        error_dict["intent"] = self.intent
        # return 语句返回基于预设的标准化错误字典
        return error_dict


class Router:
    """
    Router 类作为现代化流程调度器

    核心设计理念：基于 Dispatcher + Flow 的流程驱动架构
    完全摒弃传统的 intent_handlers 映射，全面拥抱流程化执行

    现代设计原则：
    1. 流程驱动：所有请求通过 flow_registry.get_step(intent) 获取执行函数
    2. 状态管理：用 user_status_manager 管理用户状态推进
    3. 上下文恢复：支持流程断点续传和状态恢复
    4. 跨模块协调：支持流程在不同模块间的串联执行

    调度机制：
    - 流程识别：根据 intent 从 flow_registry 获取对应的 FlowStep
    - 状态恢复：通过 user_status_manager 恢复用户流程上下文
    - 执行调度：调用 FlowStep.handler_func 执行业务逻辑
    - 进度更新：执行完成后更新用户流程状态

    不再依赖 registry_center 的 intent_handlers，完全基于 flow 架构
    """

    def __init__(self):
        # RegistryCenter 实例仅用于流程相关的辅助功能
        # 主要的路由逻辑通过 flow_registry 实现
        self.registry = _shared_registry


    def get_registered_steps(self) -> List[str]:
        """
        get_registered_steps 方法获取所有已注册的流程步骤列表
        返回当前系统支持的所有步骤名称（替代原有的意图列表）
        
        返回:
            步骤名称字符串列表
        """
        # 通过 flow_registry.steps 获取所有已注册的流程步骤
        # 返回步骤标识列表
        return list(flow_registry.steps.keys())

    async def route(self, intent: str, request_body: dict) -> Dict[str, Any]:
        """
        route 方法作为严格控制的流程调度器的核心方法
        基于Fast Fail原则实现快速intent验证和异常处理

        Fast Fail优化路由逻辑：
        1. 立即intent验证：函数开始即验证intent，无效则立即抛出异常
        2. 禁止无效intent触发状态恢复：只有有效intent才进入状态管理分支
        3. 避免数据库访问：无效intent绝不触发user_status_manager调用
        4. 快速异常响应：使用预设错误字典，避免动态构建

        参数:
            intent: 步骤标识字符串，必须已在flow_registry中注册
            request_body: 请求载荷数据字典，包含业务数据

        返回:
            处理结果字典，仅在成功情况下返回，失败则抛出异常
        
        异常:
            InvalidIntentError: 当intent未注册时抛出
        """
        # === Fast Fail: 立即intent验证层 ===
        # Fast Fail: invalid intent must not touch DB / status recovery
        # flow_registry.get_step 通过调用流程注册中心查询intent对应的FlowStep
        # 传入intent参数，获取FlowStep实例或None
        step_definition = flow_registry.get_step(intent)
        
        # Fast Fail: 如果intent未注册，立即抛出异常，禁止任何后续处理
        if not step_definition:
            # InvalidIntentError 通过构造函数创建异常实例
            # 传入intent参数，立即抛出异常，绕过所有状态恢复和数据库操作
            raise InvalidIntentError(intent)
        
        # === 有效intent的状态恢复层（仅在验证通过后执行）===
        # request_body.get 从请求体中获取user_id，用于白名单intent的状态管理
        user_id = request_body.get("user_id")
        
        # flow_registry.get_flow_for_step 通过调用获取步骤所属流程的方法
        # 传入已验证的intent参数，返回对应的flow_id
        flow_id = flow_registry.get_flow_for_step(intent)
        
        # 初始化状态恢复相关变量为None，仅白名单intent可赋值
        user_flow_state = None
        flow_recovery_context = None
        step_context = None
        
        # 严格限制：只有白名单中的intent才允许执行状态恢复逻辑
        if intent in STATEFUL_INTENT_WHITELIST and flow_id and user_id:
            try:
                # user_status_manager.get_user_flow_state 通过调用用户状态管理器
                # 仅对白名单intent传入user_id和flow_id参数，获取用户流程状态
                user_flow_state = await user_status_manager.get_user_flow_state(user_id, flow_id)
                
                # 如果存在用户流程状态，获取恢复上下文
                if user_flow_state:
                    # user_status_manager.restore_flow_context 通过调用状态管理器恢复方法
                    # 仅对白名单intent传入user_id、flow_id和当前步骤，获取恢复上下文
                    flow_recovery_context = await user_status_manager.restore_flow_context(
                        user_id, flow_id, intent
                    )
                    
            except Exception as e:
                # 白名单intent状态恢复失败时，抛出异常而非继续执行
                raise RuntimeError(f"Stateful intent '{intent}' recovery failed: {str(e)}")
        
        # === 强制步骤执行层 ===
        # step_definition.handler_func 获取已验证FlowStep的处理函数引用
        # 此处handler_func必须存在且可调用，否则抛出异常
        handler_func = step_definition.handler_func

        # 强制验证处理函数有效性，无效则抛出异常，禁止返回错误响应
        if not handler_func or not callable(handler_func):
            # RuntimeError 通过构造函数创建运行时异常
            # 传入错误信息，强制中断执行而非返回fallback响应
            raise RuntimeError(f"Invalid handler function for intent '{intent}' in module '{step_definition.module_name}'")

        try:
            # === 严格请求数据准备 ===
            # enhanced_request_body 通过copy方法创建请求体副本，避免修改原始数据
            enhanced_request_body = request_body.copy()
            
            # 仅为已验证的流程添加上下文信息
            if flow_id:
                # flow_registry.get_flow 通过调用获取完整流程定义
                flow_definition = flow_registry.get_flow(flow_id)
                # _flow_context 通过字典赋值添加流程上下文信息
                enhanced_request_body["_flow_context"] = {
                    "flow_id": flow_id,
                    "flow_name": flow_definition.name if flow_definition else "Unknown",
                    "current_step": intent,
                    "step_module": step_definition.module_name,
                    "stateful_intent": intent in STATEFUL_INTENT_WHITELIST
                }
            
            # 仅为白名单intent添加状态恢复信息
            if intent in STATEFUL_INTENT_WHITELIST and flow_recovery_context and flow_recovery_context.get("success"):
                # _recovery_context 通过字典赋值添加恢复上下文信息
                enhanced_request_body["_recovery_context"] = {
                    "restore_to_step": flow_recovery_context.get("restore_to_step"),
                    "previous_step": flow_recovery_context.get("previous_step"),
                    "available_output": flow_recovery_context.get("available_output"),
                    "step_history": flow_recovery_context.get("step_history")
                }
            
            # === 限定执行上下文创建 ===
            # 仅白名单intent且满足条件时创建步骤执行上下文
            if intent in STATEFUL_INTENT_WHITELIST and user_id and flow_id:
                # user_status_manager.create_step_execution_context 通过调用创建执行上下文
                # 仅对白名单intent传入user_id、intent和enhanced_request_body参数
                step_context = await user_status_manager.create_step_execution_context(
                    user_id, 
                    intent, 
                    enhanced_request_body
                )
            
            # === 强制步骤执行 ===
            # handler_func 通过await异步调用执行已验证的FlowStep处理函数
            # 传入enhanced_request_body参数，获取业务逻辑执行结果
            result = await handler_func(enhanced_request_body)

            # === 限定流程进度更新 ===
            # 仅白名单intent且存在执行上下文时更新流程进度
            if intent in STATEFUL_INTENT_WHITELIST and step_context and user_id and flow_id:
                # user_status_manager.complete_step_execution 通过调用完成白名单intent的步骤执行
                # 传入step_context和result参数，更新白名单intent的执行状态
                await user_status_manager.complete_step_execution(step_context, result)
                
                # user_status_manager.update_flow_progress 通过调用更新白名单intent的流程进度
                # 传入user_id、flow_id、intent和result参数，更新流程状态
                await user_status_manager.update_flow_progress(user_id, flow_id, intent, result)
                
                # flow_registry.get_next_step 通过调用获取下一步骤标识
                next_step = flow_registry.get_next_step(intent)
                
                # 为白名单intent添加流程建议信息
                if next_step and isinstance(result, dict):
                    # _flow_suggestion 通过字典赋值添加下一步骤建议
                    result["_flow_suggestion"] = {
                        "next_step": next_step,
                        "flow_id": flow_id
                    }

            # === 严格响应构建 ===
            # response 通过字典创建严格的成功响应结构，不包含兜底字段
            response = {
                "success": True,
                "intent": intent,
                "module": step_definition.module_name,
                "result": result,
                "stateful": intent in STATEFUL_INTENT_WHITELIST
            }
            
            # 仅为流程相关的intent添加流程信息
            if flow_id:
                # flow_registry.get_flow 通过调用获取流程定义
                flow_definition = flow_registry.get_flow(flow_id)
                # flow_info 通过字典赋值添加流程信息到响应中
                response["flow_info"] = {
                    "flow_id": flow_id,
                    "flow_name": flow_definition.name if flow_definition else "Unknown",
                    "current_step": intent,
                    "module": step_definition.module_name
                }
                
                # 仅为白名单intent且有用户ID时添加进度信息
                if intent in STATEFUL_INTENT_WHITELIST and user_id:
                    # flow_registry.get_flow_progress 通过调用获取流程进度信息
                    progress_info = flow_registry.get_flow_progress(flow_id, intent)
                    # progress 通过字典赋值添加进度信息
                    response["flow_info"]["progress"] = progress_info
            
            # return 语句返回严格的成功响应，不包含任何兜底结构
            return response

        except Exception as e:
            # === 严格异常处理层 ===
            # 执行异常时进行必要清理后重新抛出异常，禁止返回错误响应
            
            # 仅对白名单intent清理步骤执行上下文
            if intent in STATEFUL_INTENT_WHITELIST and step_context:
                try:
                    # user_status_manager.complete_step_execution 通过调用清理白名单intent的执行上下文
                    # 传入step_context、None结果和错误消息，标记执行失败
                    await user_status_manager.complete_step_execution(step_context, None, str(e))
                except Exception as cleanup_error:
                    # 清理失败时抛出复合异常，包含原始异常和清理异常信息
                    raise RuntimeError(f"Intent '{intent}' execution failed: {str(e)}. Cleanup also failed: {str(cleanup_error)}")
            
            # 严格模式：重新抛出原始异常，禁止返回fallback错误响应
            # 让上层HTTP处理器将异常转换为合适的4xx/5xx状态码
            raise RuntimeError(f"Intent '{intent}' execution failed in module '{step_definition.module_name}': {str(e)}")


# router 通过 Router() 创建路由器实例
# 用于处理 hub 的业务路由逻辑
router = Router()

# hub_entry 函数作为 hub 模块的外部代理入口
# 设计理念：薄代理层，专门委托现代化 Router.route() 处理流程调度
# 职责清晰分离：外部接口只做参数转发，流程调度逻辑由 Router 类负责
async def hub_entry(intent: str, request_body: dict) -> Dict[str, Any]:
    """
    hub_entry 函数作为现代化 hub 模块的外部代理入口
    设计理念：作为薄代理层，委托现代化 Router.route() 处理流程调度

    现代化职责范围：
    - 接收外部请求参数（intent 现在作为 step_id）
    - 将请求转发给基于 Dispatcher + Flow 的 Router.route() 方法处理
    - 返回流程执行结果，不包含任何业务逻辑

    这是现代架构的体现：外部接口 → 流程调度器 → FlowStep.handler_func

    参数:
        intent: 步骤标识字符串（原意图名称），直接传递给 Router.route() 方法
        request_body: 请求载荷数据字典，直接传递给 Router.route() 方法

    返回:
        Router.route() 方法的现代化处理结果字典，包含流程信息和执行状态
    """
    # 通过现代化的 router.route 方法处理步骤请求
    # 传入 intent（作为step_id）和 request_body 参数到流程调度器
    # await 等待异步执行完成后返回结果作为函数返回值
    return await router.route(intent, request_body)