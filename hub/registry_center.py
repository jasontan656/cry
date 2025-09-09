from typing import Dict, Any, Optional, Callable, List
import asyncio
import inspect
import concurrent.futures

# 导入新增的流程和状态管理模块
from .flow import FlowDefinition, FlowStep, flow_registry
from .status import UserFlowState, user_status_manager


class RegistryCenter:
    """
    RegistryCenter 类作为模块注册中心的共享底座
    专注于模块元信息、字段结构和依赖关系的统一管理
    移除历史意图驱动逻辑，避免与现代 flow_registry 冲突
    """

    # __init__ 方法初始化 RegistryCenter 类的实例
    # 创建核心数据结构用于存储模块注册信息（移除意图相关字段）
    def __init__(self):
        # module_meta 初始化为空字典，用于记录模块元信息
        # 键为模块名，值为包含 name、version、capabilities 等信息的字典
        self.module_meta: Dict[str, Dict[str, Any]] = {}

        # module_fields 初始化为空字典，用于存储模块名称到字段结构的映射
        # 键为模块名，值为包含 field_types 和 field_groups 的字段结构字典
        self.module_fields: Dict[str, Dict[str, Any]] = {}

        # dependencies 初始化为空字典，用于存储模块名称到依赖模块列表的映射
        # 键为模块名，值为该模块声明的依赖模块名称列表
        self.dependencies: Dict[str, list] = {}

    def register_module(self, module_info: Dict[str, Any]) -> None:
        """
        register_module 方法采用完全自主注册策略，专注于模块元信息管理
        模块通过register_function完全自主控制注册过程，中枢被动接收注册信息
        移除意图映射逻辑，所有流程注册统一由 flow_registry 处理
        """
        # 从 module_info 中提取模块名称，作为存储键
        module_name = module_info.get('name')

        # 只有当模块名称存在时才继续处理注册
        if module_name:
            # 存储模块元信息到 module_meta 字典中
            self.module_meta[module_name] = module_info
            
            # 检查模块是否提供了自主注册函数
            if 'register_function' in module_info:
                # 通过 _register_via_function 方法执行模块提供的自主注册函数
                # 传入 module_name 和 module_info 参数，让模块完全自主控制注册过程
                self._register_via_function(module_name, module_info)

                # 现代架构：所有流程和步骤注册统一由模块的 register_function 
                # 直接调用 flow_registry.register_flow() 和 flow_registry.register_step()
                # 不再在此处处理意图映射，避免与 flow_registry 冲突

    def _register_via_function(self, module_name: str, module_info: Dict[str, Any]) -> None:
        """
        _register_via_function 方法通过模块提供的自主注册函数进行注册
        这是最纯粹的照单全收方式，模块完全自主控制注册过程，中枢被动接收
        支持同步和异步注册函数
        """
        # 从 module_info 中获取模块提供的注册函数
        register_func = module_info.get('register_function')

        # 检查注册函数是否有效且可调用
        if register_func and callable(register_func):
            # 检查是否为异步协程函数
            if inspect.iscoroutinefunction(register_func):
                # 处理异步注册函数
                self._handle_async_registration(register_func, module_name, module_info)
            else:
                # 处理同步注册函数
                register_func(self, module_name, module_info)

    def _handle_async_registration(self, register_func: Callable, module_name: str, module_info: Dict[str, Any]) -> None:
        """
        _handle_async_registration 方法处理异步注册函数
        使用线程池执行器来确保异步函数能够完全执行完成
        """
        def run_async_in_thread():
            """在新线程中运行异步函数"""
            try:
                # 在新的线程中创建新的事件循环
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    # 在新事件循环中运行异步注册函数
                    loop.run_until_complete(register_func(self, module_name, module_info))
                finally:
                    loop.close()
            except Exception as e:
                print(f"警告：异步注册函数在线程中执行失败 {module_name}: {str(e)}")

        try:
            # 检查当前是否有正在运行的事件循环
            loop = asyncio.get_running_loop()
            # 如果有运行的事件循环，使用线程池执行器
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_async_in_thread)
                # 等待异步注册完成（设置超时以防止无限等待）
                future.result(timeout=30)  # 30秒超时
        except RuntimeError:
            # 没有运行的事件循环，直接使用 asyncio.run
            try:
                asyncio.run(register_func(self, module_name, module_info))
            except Exception as e:
                print(f"警告：异步注册函数执行失败 {module_name}: {str(e)}")
        except concurrent.futures.TimeoutError:
            print(f"警告：异步注册函数执行超时 {module_name}")
        except Exception as e:
            print(f"警告：异步注册处理失败 {module_name}: {str(e)}")


    # === 已移除的历史意图驱动方法 ===
    # 以下方法已被移除，避免与现代 flow_registry 架构冲突：
    # - get_handler_for_intent(intent) -> 已由 flow_registry.get_step(intent) 替代
    # - get_module_for_intent(intent) -> 已由 flow_registry.get_flow_for_step(intent) 替代
    # 
    # 现代架构中，所有意图到处理器的映射统一由 flow_registry 管理
    # RegistryCenter 专注于模块元信息、字段结构和依赖关系管理

    def get_registered_modules(self) -> List[str]:
        """
        get_registered_modules 方法获取所有已注册的模块名称列表
        用于系统管理和模块总览功能
        
        返回:
            List[str]: 所有已注册模块的名称列表
        """
        # module_meta.keys 获取所有已注册模块的名称
        # 转换为列表返回
        return list(self.module_meta.keys())

    def get_module_info(self, module_name: str) -> Dict[str, Any]:
        """
        get_module_info 方法获取指定模块的完整元信息
        用于查看特定模块的详细配置和能力
        
        参数:
            module_name: 模块名称字符串
            
        返回:
            Dict[str, Any]: 模块信息字典，如果模块不存在则返回空字典
        """
        # module_meta.get 通过模块名获取对应的模块信息
        # 如果不存在则返回空字典
        return self.module_meta.get(module_name, {})

    def get_module_fields(self, module_name: str) -> Dict[str, Any]:
        """
        get_module_fields 方法获取某个模块的字段结构定义
        用于查看特定模块的输入输出字段配置

        通过 module_name 参数传入模块名称字符串
        从 module_fields 字典中查找对应的字段结构
        如果找到则返回字段结构字典，否则返回空字典
        """
        # 使用 module_name 作为键从 module_fields 字典中获取字段结构
        # 如果模块不存在则返回空字典
        return self.module_fields.get(module_name, {})

    def get_dependencies(self, module_name: str) -> list:
        """
        get_dependencies 方法获取某个模块声明的依赖模块列表
        用于分析模块间的依赖关系和执行顺序

        通过 module_name 参数传入模块名称字符串
        从 dependencies 字典中查找对应的依赖列表
        如果找到则返回依赖模块列表，否则返回空列表
        """
        # 使用 module_name 作为键从 dependencies 字典中获取依赖列表
        # 如果模块不存在则返回空列表
        return self.dependencies.get(module_name, [])

    def get_all_fields(self) -> Dict[str, Dict[str, Any]]:
        """
        get_all_fields 方法返回所有模块的字段结构总览
        用于中枢系统获取完整的字段信息索引

        不需要传入参数，直接返回 module_fields 字典的副本
        防止外部直接修改内部数据结构
        """
        # 返回 module_fields 字典的浅拷贝
        # 避免外部代码直接修改内部的字段数据
        return self.module_fields.copy()

    # ============ 流程调度扩展方法 ============

    def register_flow(self, flow_definition: FlowDefinition) -> bool:
        """
        register_flow 方法将流程定义注册到流程注册中心
        通过委托给flow_registry实现流程的统一管理
        
        参数:
            flow_definition: FlowDefinition实例，包含完整的流程定义
        
        返回:
            bool: 注册成功返回True，失败返回False
        """
        # flow_registry.register_flow 通过调用流程注册中心的注册方法
        # 传入flow_definition参数，委托给专业的流程管理模块
        # 返回注册结果布尔值
        return flow_registry.register_flow(flow_definition)

    def register_flow_step(self, step_definition: FlowStep) -> bool:
        """
        register_flow_step 方法将单个步骤定义注册到流程注册中心
        通过委托给flow_registry实现步骤的统一管理
        
        参数:
            step_definition: FlowStep实例，包含步骤的完整定义
        
        返回:
            bool: 注册成功返回True，失败返回False
        """
        # flow_registry.register_step 通过调用流程注册中心的步骤注册方法
        # 传入step_definition参数，委托给专业的流程管理模块
        # 返回注册结果布尔值
        return flow_registry.register_step(step_definition)

    def get_flow_definition(self, flow_id: str) -> Optional[FlowDefinition]:
        """
        get_flow_definition 方法根据flow_id获取完整的流程定义
        通过委托给flow_registry实现流程查询
        
        参数:
            flow_id: 流程标识字符串
        
        返回:
            Optional[FlowDefinition]: 找到则返回FlowDefinition实例，否则返回None
        """
        # flow_registry.get_flow 通过调用流程注册中心的查询方法
        # 传入flow_id参数，返回对应的FlowDefinition实例或None
        return flow_registry.get_flow(flow_id)

    def get_flow_step(self, step_id: str) -> Optional[FlowStep]:
        """
        get_flow_step 方法根据step_id获取步骤的完整定义
        通过委托给flow_registry实现步骤查询
        
        参数:
            step_id: 步骤标识字符串
        
        返回:
            Optional[FlowStep]: 找到则返回FlowStep实例，否则返回None
        """
        # flow_registry.get_step 通过调用流程注册中心的步骤查询方法
        # 传入step_id参数，返回对应的FlowStep实例或None
        return flow_registry.get_step(step_id)

    def get_flow_for_step(self, step_id: str) -> Optional[str]:
        """
        get_flow_for_step 方法根据step_id获取所属的flow_id
        通过委托给flow_registry实现步骤到流程的映射查询
        
        参数:
            step_id: 步骤标识字符串
        
        返回:
            Optional[str]: 找到则返回flow_id字符串，否则返回None
        """
        # flow_registry.get_flow_for_step 通过调用流程注册中心的映射查询方法
        # 传入step_id参数，返回对应的flow_id或None
        return flow_registry.get_flow_for_step(step_id)

    def get_next_step_in_flow(self, current_step_id: str) -> Optional[str]:
        """
        get_next_step_in_flow 方法获取流程中当前步骤的下一个步骤
        用于实现流程的自动推进逻辑
        
        参数:
            current_step_id: 当前步骤标识字符串
        
        返回:
            Optional[str]: 下一步骤标识字符串，None表示流程结束
        """
        # flow_registry.get_next_step 通过调用流程注册中心的下一步查询方法
        # 传入current_step_id参数，返回下一步骤标识或None
        return flow_registry.get_next_step(current_step_id)

    def get_flow_progress(self, flow_id: str, current_step_id: str) -> Dict[str, Any]:
        """
        get_flow_progress 方法获取流程的执行进度信息
        通过委托给flow_registry计算流程完成百分比和剩余步骤
        
        参数:
            flow_id: 流程标识字符串
            current_step_id: 当前执行步骤标识
        
        返回:
            Dict[str, Any]: 包含进度信息的字典
        """
        # flow_registry.get_flow_progress 通过调用流程注册中心的进度计算方法
        # 传入flow_id和current_step_id参数，返回详细的进度信息字典
        return flow_registry.get_flow_progress(flow_id, current_step_id)

    # ============ 用户状态管理扩展方法 ============

    async def get_user_snapshot(self, user_id: str, flow_id: str = None) -> Dict[str, Any]:
        """
        get_user_snapshot 方法获取用户在指定流程中的完整快照
        通过委托给user_status_manager实现用户状态查询
        
        参数:
            user_id: 用户标识字符串
            flow_id: 可选的流程标识，None时获取用户活跃流程
        
        返回:
            Dict[str, Any]: 用户流程快照字典，包含完整的状态信息
        """
        # user_status_manager.get_flow_snapshot 通过调用用户状态管理器的快照获取方法
        # 传入user_id和flow_id参数，返回完整的流程快照字典
        return await user_status_manager.get_flow_snapshot(user_id, flow_id)

    async def get_user_flow_state(self, user_id: str, flow_id: str = None) -> Optional[UserFlowState]:
        """
        get_user_flow_state 方法获取用户的流程状态对象
        通过委托给user_status_manager实现状态对象查询
        
        参数:
            user_id: 用户标识字符串
            flow_id: 可选的流程标识，None时获取用户活跃流程
        
        返回:
            Optional[UserFlowState]: 找到则返回UserFlowState实例，否则返回None
        """
        # user_status_manager.get_user_flow_state 通过调用用户状态管理器的状态查询方法
        # 传入user_id和flow_id参数，返回UserFlowState实例或None
        return await user_status_manager.get_user_flow_state(user_id, flow_id)

    async def update_user_flow_progress(self, user_id: str, flow_id: str, 
                                       current_step: str, step_output: Dict[str, Any] = None) -> bool:
        """
        update_user_flow_progress 方法更新用户的流程进度
        通过委托给user_status_manager实现进度更新和快照保存
        
        参数:
            user_id: 用户标识字符串
            flow_id: 流程标识字符串
            current_step: 当前完成的步骤标识
            step_output: 可选的步骤输出数据
        
        返回:
            bool: 更新成功返回True，失败返回False
        """
        # user_status_manager.update_flow_progress 通过调用用户状态管理器的进度更新方法
        # 传入user_id、flow_id、current_step和step_output参数
        # 返回更新操作的结果布尔值
        return await user_status_manager.update_flow_progress(user_id, flow_id, current_step, step_output)

    async def restore_user_flow_context(self, user_id: str, flow_id: str, target_step: str = None) -> Dict[str, Any]:
        """
        restore_user_flow_context 方法恢复用户流程到指定状态
        通过委托给user_status_manager实现断点续传和流程恢复
        
        参数:
            user_id: 用户标识字符串
            flow_id: 流程标识字符串
            target_step: 可选的目标步骤，None时恢复到当前步骤
        
        返回:
            Dict[str, Any]: 恢复结果字典，包含恢复后的上下文信息
        """
        # user_status_manager.restore_flow_context 通过调用用户状态管理器的恢复方法
        # 传入user_id、flow_id和target_step参数，返回恢复上下文字典
        return await user_status_manager.restore_flow_context(user_id, flow_id, target_step)

    # ============ 流程调度辅助方法 ============

    def identify_flow_from_step(self, step_id: str) -> Optional[str]:
        """
        identify_flow_from_step 方法根据步骤标识识别所属流程
        现代化方法：直接委托给 flow_registry 处理流程识别
        
        参数:
            step_id: 步骤标识字符串
        
        返回:
            Optional[str]: 找到则返回flow_id字符串，否则返回None
        """
        # flow_registry.get_flow_for_step 通过调用流程注册中心的方法
        # 直接获取步骤所属的流程，现代架构的标准做法
        return flow_registry.get_flow_for_step(step_id)

    def get_flow_context_for_request(self, step_id: str, user_id: str) -> Dict[str, Any]:
        """
        get_flow_context_for_request 方法为请求构建现代化流程上下文信息
        现代化设计：基于 flow_registry，为 Router 提供流程识别支持
        
        参数:
            step_id: 步骤标识字符串（原意图名称）
            user_id: 用户标识字符串
        
        返回:
            Dict[str, Any]: 现代化流程上下文字典，包含流程信息和执行建议
        """
        # 通过现代化方法识别步骤对应的流程
        flow_id = self.identify_flow_from_step(step_id)
        
        if not flow_id:
            # 如果无法识别流程，返回基本信息
            return {
                "has_flow": False,
                "step_id": step_id,
                "user_id": user_id,
                "error": f"No flow found for step: {step_id}",
                "suggestion": "Please ensure the step is registered via flow_registry.register_step()"
            }
        
        # 获取流程定义和步骤定义
        flow_def = flow_registry.get_flow(flow_id)
        step_def = flow_registry.get_step(step_id)
        
        # 构建现代化的流程上下文
        context = {
            "has_flow": True,
            "flow_id": flow_id,
            "flow_name": flow_def.name if flow_def else "Unknown",
            "current_step": step_id,
            "step_module": step_def.module_name if step_def else "Unknown",
            "user_id": user_id,
            "flow_type": flow_def.flow_type if flow_def else "linear"
        }
        
        # 添加现代化的流程管理提示
        context["flow_registry_managed"] = True
        context["async_state_methods"] = [
            "user_status_manager.get_user_flow_state",
            "user_status_manager.get_flow_snapshot"
        ]
        
        return context

    def validate_flow_transition(self, user_id: str, from_step: str, to_step: str) -> Dict[str, Any]:
        """
        validate_flow_transition 方法验证流程步骤跳转的有效性
        现代化设计：委托给 flow_registry 进行步骤链接和前置条件检查
        
        参数:
            user_id: 用户标识字符串
            from_step: 起始步骤标识
            to_step: 目标步骤标识
        
        返回:
            Dict[str, Any]: 验证结果字典，包含是否允许跳转和原因
        """
        # 通过 flow_registry 获取起始步骤和目标步骤的定义
        from_step_def = flow_registry.get_step(from_step)
        to_step_def = flow_registry.get_step(to_step)
        
        # 基本存在性检查
        if not from_step_def:
            return {
                "valid": False,
                "reason": f"Source step not found: {from_step}",
                "suggestion": "Please register the step via flow_registry.register_step()"
            }
        
        if not to_step_def:
            return {
                "valid": False,
                "reason": f"Target step not found: {to_step}",
                "suggestion": "Please register the step via flow_registry.register_step()"
            }
        
        # 检查步骤是否属于同一流程（现代化方法）
        from_flow = flow_registry.get_flow_for_step(from_step)
        to_flow = flow_registry.get_flow_for_step(to_step)
        
        if from_flow != to_flow:
            return {
                "valid": False,
                "reason": f"Steps belong to different flows: {from_flow} -> {to_flow}"
            }
        
        # 检查直接跳转是否允许
        if from_step_def.next_step == to_step:
            return {
                "valid": True,
                "reason": "Direct next step transition",
                "transition_type": "forward"
            }
        
        # 检查回退是否允许
        if to_step_def.next_step == from_step:
            return {
                "valid": True,
                "reason": "Backward step transition",
                "transition_type": "backward"
            }
        
        # 其他跳转需要进一步验证逻辑
        return {
            "valid": False,
            "reason": f"Invalid transition: {from_step} -> {to_step}",
            "suggested_next": from_step_def.next_step
        }
