# applications/mbti/flow_router.py - MBTI流程驱动路由器
# 基于flow_registry的纯流程驱动处理，不再依赖本地intent映射

import sys
import os
from typing import Dict, Any

# 添加上级目录到Python路径，以便导入hub模块
parent_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, parent_dir)

# 导入hub流程调度模块
from hub.flow import flow_registry
from hub.status import user_status_manager
from hub.registry_center import RegistryCenter

# 导入各步骤处理函数
from applications.mbti import step1, step2, step3, step4, step5


class FlowDrivenRouter:
    """
    FlowDrivenRouter 类实现流程驱动的路由处理器
    完全基于flow_registry进行步骤调度，不再维护本地映射
    """
    
    def __init__(self):
        # flow_id 设置为标准MBTI流程标识符
        self.flow_id = "mbti_personality_test"
    
    async def route_with_flow_context(self, intent: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        route_with_flow_context 方法通过流程上下文执行路由处理
        先检查流程状态，再调用对应的步骤处理器
        
        参数:
            intent: 意图标识字符串
            request: 请求数据字典
        
        返回:
            Dict[str, Any]: 处理结果字典，包含流程上下文
        """
        try:
            # user_id 从请求中获取用户标识符
            user_id = request.get("user_id")
            # flow_id 从请求中获取流程标识符，默认为标准MBTI流程
            flow_id = request.get("flow_id", self.flow_id)
            
            # === 获取用户流程状态快照 ===
            
            # user_status_manager.get_flow_snapshot 通过调用获取用户流程快照
            # 传入user_id和flow_id参数，返回完整的状态信息
            user_snapshot = await user_status_manager.get_flow_snapshot(user_id, flow_id)
            
            # === 验证流程跳转合法性 ===
            
            if user_snapshot.get("exists"):
                # current_step 从用户快照中获取当前步骤
                current_step = user_snapshot.get("current_step")
                
                # 如果当前步骤存在且与目标intent不同，验证跳转
                if current_step and current_step != intent:
                    # 这里可以添加流程跳转校验逻辑
                    print(f"Flow transition: {current_step} -> {intent}")
            
            # === 添加流程上下文到请求 ===
            
            # request 字典通过update方法添加流程上下文字段
            request.update({
                "flow_id": flow_id,
                "user_snapshot": user_snapshot
            })
            
            # === 通过flow_registry调用步骤处理器 ===
            
            # 从flow_registry获取步骤定义
            step_definition = flow_registry.get_step(intent)
            
            if step_definition and step_definition.handler_func:
                # 从flow_registry获取处理器函数
                handler = step_definition.handler_func
                # 调用处理器函数处理请求，传入添加了流程上下文的request参数
                result = await handler(request)
            else:
                # 步骤未在flow_registry中注册，返回错误响应
                result = {
                    "request_id": request.get("request_id", "unknown"),
                    "success": False,
                    "step": intent,
                    "error_message": f"流程步骤未在flow_registry中注册: {intent}",
                    "error_code": "STEP_NOT_REGISTERED"
                }
            
            # === 确保结果包含流程上下文 ===
            
            # 如果结果中没有flow_id，添加流程上下文
            if "flow_id" not in result:
                result["flow_id"] = flow_id
            
            # 返回包含流程上下文的处理结果
            return result
            
        except Exception as e:
            # 捕获处理过程中的异常，返回标准化错误响应
            return {
                "request_id": request.get("request_id", "unknown"),
                "user_id": request.get("user_id"),
                "flow_id": request.get("flow_id", self.flow_id),
                "success": False,
                "step": intent,
                "error_message": f"流程驱动路由处理异常: {str(e)}",
                "error_code": "FLOW_ROUTING_ERROR"
            }
    
    async def get_flow_progress(self, user_id: str, flow_id: str = None) -> Dict[str, Any]:
        """
        get_flow_progress 方法获取用户在流程中的进度信息
        集成flow_registry的进度计算功能
        
        参数:
            user_id: 用户标识符
            flow_id: 流程标识符，默认为标准MBTI流程
        
        返回:
            Dict[str, Any]: 流程进度信息字典
        """
        if not flow_id:
            flow_id = self.flow_id
            
        try:
            # user_status_manager.get_flow_snapshot 获取用户流程快照
            user_snapshot = await user_status_manager.get_flow_snapshot(user_id, flow_id)
            
            if not user_snapshot.get("exists"):
                return {
                    "error": "User flow state not found",
                    "progress": 0
                }
            
            # current_step 从快照中获取当前步骤
            current_step = user_snapshot.get("current_step")
            
            if current_step:
                # flow_registry.get_flow_progress 通过调用计算流程进度
                # 传入flow_id和current_step参数，获取进度信息
                progress_info = flow_registry.get_flow_progress(flow_id, current_step)
                return progress_info
            else:
                return {
                    "error": "Current step not found in user snapshot",
                    "progress": 0
                }
                
        except Exception as e:
            return {
                "error": f"Get flow progress failed: {str(e)}",
                "progress": 0
            }


# flow_router 通过FlowDrivenRouter()创建流程驱动路由器实例
# 用于整合传统路由与流程调度功能
flow_router = FlowDrivenRouter()


async def process_with_flow_context(intent: str, request: Dict[str, Any]) -> Dict[str, Any]:
    """
    process_with_flow_context 函数提供流程驱动的请求处理接口
    集成流程上下文和状态管理功能
    
    参数:
        intent: 意图标识字符串
        request: 请求数据字典
    
    返回:
        Dict[str, Any]: 处理结果字典，包含流程上下文
    """
    # flow_router.route_with_flow_context 通过调用流程驱动路由器
    # 传入intent和request参数，返回包含流程上下文的处理结果
    return await flow_router.route_with_flow_context(intent, request)
