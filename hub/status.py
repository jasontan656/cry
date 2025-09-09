# hub/status.py - 用户状态存储结构与流程恢复机制
# 实现用户状态读取、流程快照保存、断点续传和状态恢复功能

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import sys
import os

# 添加上级目录到Python路径，以便导入utilities模块
parent_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, parent_dir)

# Time 通过绝对导入路径utilities.time.Time获取，用于生成时间戳
from utilities.time import Time
# DatabaseOperations 通过绝对导入路径获取数据库操作实例
from utilities.mongodb_connector import DatabaseOperations


@dataclass
class UserFlowState:
    """
    UserFlowState 类定义用户在特定流程中的状态结构
    包含流程标识、当前步骤、执行历史和输出快照
    """
    # user_id 通过字符串标识用户唯一标识符
    user_id: str
    # flow_id 通过字符串标识用户当前执行的流程
    flow_id: str
    # current_step 通过字符串标识用户当前所在的流程步骤
    current_step: str
    # last_completed_step 通过字符串标识用户最后完成的步骤
    last_completed_step: str
    # created_at 通过字符串记录流程开始时间戳
    created_at: str
    # updated_at 通过字符串记录最后更新时间戳
    updated_at: str
    # status 通过字符串标识流程状态，如"ongoing"、"completed"、"paused"、"error"
    status: str = "ongoing"
    # step_history 通过字符串列表记录已执行的步骤历史
    step_history: List[str] = None
    # output_snapshot 通过字典保存每个步骤的输出结果快照
    output_snapshot: Dict[str, Any] = None
    # input_data 通过字典保存用户输入的原始数据
    input_data: Dict[str, Any] = None
    # error_info 通过可选字典记录执行过程中的错误信息
    error_info: Optional[Dict[str, Any]] = None
    # retry_count 通过整数记录重试次数
    retry_count: int = 0
    # max_retries 通过整数定义最大重试次数限制
    max_retries: int = 3
    
    # __post_init__ 方法在dataclass初始化后执行，设置默认空列表和字典
    def __post_init__(self):
        # step_history 若为None则初始化为空列表，避免可变默认参数问题
        if self.step_history is None:
            self.step_history = []
        # output_snapshot 若为None则初始化为空字典，避免可变默认参数问题
        if self.output_snapshot is None:
            self.output_snapshot = {}
        # input_data 若为None则初始化为空字典，避免可变默认参数问题
        if self.input_data is None:
            self.input_data = {}


@dataclass
class StepExecutionContext:
    """
    StepExecutionContext 类定义单个步骤的执行上下文
    包含步骤输入输出、执行时间和状态信息
    """
    # step_id 通过字符串标识执行的步骤
    step_id: str
    # request_id 通过字符串标识该次执行的请求标识符
    request_id: str
    # start_time 通过字符串记录步骤开始执行时间
    start_time: str
    # end_time 通过可选字符串记录步骤完成执行时间
    end_time: Optional[str] = None
    # input_data 通过字典保存步骤的输入数据
    input_data: Dict[str, Any] = None
    # output_data 通过字典保存步骤的输出结果
    output_data: Dict[str, Any] = None
    # execution_status 通过字符串标识执行状态，如"running"、"completed"、"failed"
    execution_status: str = "running"
    # error_message 通过可选字符串记录执行错误信息
    error_message: Optional[str] = None
    # duration_seconds 通过可选数值记录执行耗时
    duration_seconds: Optional[float] = None
    
    # __post_init__ 方法在dataclass初始化后执行，设置默认空字典
    def __post_init__(self):
        # input_data 若为None则初始化为空字典
        if self.input_data is None:
            self.input_data = {}
        # output_data 若为None则初始化为空字典
        if self.output_data is None:
            self.output_data = {}


class UserStatusManager:
    """
    UserStatusManager 类管理用户状态的读取、保存和恢复功能
    提供流程状态管理和断点续传的核心功能
    """

    # __init__ 方法初始化用户状态管理器
    def __init__(self):
        # DatabaseOperations() 通过无参构造创建数据库操作实例
        # 连接到默认的MongoDB实例和数据库
        self.db = DatabaseOperations()

    async def get_user_flow_state(self, user_id: str, flow_id: str = None) -> Optional[UserFlowState]:
        """
        get_user_flow_state 方法获取用户在指定流程中的状态
        支持按flow_id查询特定流程状态，或获取用户的活跃流程状态
        
        参数:
            user_id: 用户标识字符串
            flow_id: 可选的流程标识，None时获取用户当前活跃流程
        
        返回:
            Optional[UserFlowState]: 找到状态则返回UserFlowState实例，否则返回None
        """
        try:
            # 构建查询条件，始终包含user_id
            # filter_conditions 字典用于MongoDB查询过滤
            filter_conditions = {"user_id": user_id}
            
            # 如果指定了flow_id，添加到查询条件中
            if flow_id:
                filter_conditions["flow_id"] = flow_id
            
            # self.db.find 通过调用数据库操作实例的find方法
            # 传入集合名"user_status"和过滤条件，查询用户状态文档
            user_status_docs = self.db.find("user_status", filter_conditions)
            
            # 如果没有找到用户状态文档，返回None
            if not user_status_docs:
                return None
            
            # 获取第一个匹配的文档（假设每个用户每个流程只有一个活跃状态）
            # user_doc 赋值为查询结果列表的第一个文档字典
            user_doc = user_status_docs[0]
            
            # 将MongoDB文档转换为UserFlowState实例
            return self._doc_to_flow_state(user_doc)
            
        except Exception as e:
            # 捕获异常并打印错误信息
            print(f"获取用户流程状态失败: user_id={user_id}, flow_id={flow_id}, 错误: {str(e)}")
            return None

    async def save_user_flow_state(self, flow_state: UserFlowState) -> bool:
        """
        save_user_flow_state 方法保存或更新用户的流程状态
        支持新建状态和更新现有状态，使用update方法实现归档功能
        
        参数:
            flow_state: UserFlowState实例，包含完整的用户流程状态
        
        返回:
            bool: 保存成功返回True，失败返回False
        """
        try:
            # Time.timestamp() 生成当前时间戳，更新updated_at字段
            flow_state.updated_at = Time.timestamp()
            
            # asdict 函数将dataclass实例转换为字典格式，便于数据库存储
            state_dict = asdict(flow_state)
            
            # 构建查询条件，用于定位需要更新的文档
            filter_conditions = {
                "user_id": flow_state.user_id,
                "flow_id": flow_state.flow_id
            }
            
            # 检查是否已存在相同的流程状态记录
            existing_docs = self.db.find("user_status", filter_conditions)
            
            if existing_docs:
                # 如果记录已存在，使用update方法更新（带归档功能）
                # self.db.update 调用数据库更新操作，传入过滤条件和更新数据
                update_result = self.db.update("user_status", filter_conditions, state_dict)
                
                # 检查更新操作是否成功
                return update_result.acknowledged and (update_result.matched_count > 0 or update_result.modified_count > 0)
            else:
                # 如果记录不存在，使用insert方法新建
                # self.db.insert 调用数据库插入操作，传入集合名和状态字典
                insert_result = self.db.insert("user_status", state_dict)
                
                # 检查插入操作是否成功
                return insert_result.acknowledged and insert_result.inserted_id is not None
            
        except Exception as e:
            # 捕获异常并打印错误信息
            print(f"保存用户流程状态失败: {str(e)}")
            return False

    async def create_step_execution_context(self, user_id: str, step_id: str, 
                                          input_data: Dict[str, Any] = None) -> StepExecutionContext:
        """
        create_step_execution_context 方法创建步骤执行上下文
        为单个步骤的执行提供完整的上下文信息和追踪能力
        
        参数:
            user_id: 用户标识字符串
            step_id: 步骤标识字符串
            input_data: 可选的步骤输入数据字典
        
        返回:
            StepExecutionContext: 新创建的步骤执行上下文实例
        """
        # Time.timestamp() 生成唯一的request_id，用于追踪该次执行
        request_id = Time.timestamp()
        # Time.timestamp() 生成当前时间戳，记录步骤开始时间
        start_time = Time.timestamp()
        
        # 创建并返回StepExecutionContext实例
        return StepExecutionContext(
            step_id=step_id,
            request_id=request_id,
            start_time=start_time,
            input_data=input_data or {}
        )

    async def complete_step_execution(self, context: StepExecutionContext, 
                                    output_data: Dict[str, Any] = None, 
                                    error_message: str = None) -> StepExecutionContext:
        """
        complete_step_execution 方法完成步骤执行并记录结果
        更新执行上下文的完成状态、输出数据和执行时间
        
        参数:
            context: StepExecutionContext实例，要完成的执行上下文
            output_data: 可选的步骤输出数据字典
            error_message: 可选的错误消息字符串
        
        返回:
            StepExecutionContext: 更新后的执行上下文实例
        """
        # Time.timestamp() 生成当前时间戳，记录步骤完成时间
        context.end_time = Time.timestamp()
        
        # 根据是否有错误消息设置执行状态
        if error_message:
            context.execution_status = "failed"
            context.error_message = error_message
        else:
            context.execution_status = "completed"
            context.output_data = output_data or {}
        
        # 计算执行耗时（简化版本，实际应该解析时间戳差值）
        # 这里暂时设置为None，实际实现需要计算时间戳差值
        context.duration_seconds = None
        
        return context

    async def update_flow_progress(self, user_id: str, flow_id: str, 
                                 current_step: str, step_output: Dict[str, Any] = None) -> bool:
        """
        update_flow_progress 方法更新用户在流程中的进度
        记录当前步骤、更新输出快照和步骤历史
        
        参数:
            user_id: 用户标识字符串
            flow_id: 流程标识字符串
            current_step: 当前完成的步骤标识
            step_output: 可选的步骤输出数据
        
        返回:
            bool: 更新成功返回True，失败返回False
        """
        try:
            # 获取现有的用户流程状态
            flow_state = await self.get_user_flow_state(user_id, flow_id)
            
            if flow_state:
                # 更新现有状态
                flow_state.last_completed_step = flow_state.current_step
                flow_state.current_step = current_step
                
                # 添加到步骤历史（避免重复）
                if current_step not in flow_state.step_history:
                    flow_state.step_history.append(current_step)
                
                # 更新输出快照
                if step_output:
                    flow_state.output_snapshot[current_step] = step_output
                
                # 保存更新后的状态
                return await self.save_user_flow_state(flow_state)
            else:
                # 创建新的流程状态
                current_time = Time.timestamp()
                new_flow_state = UserFlowState(
                    user_id=user_id,
                    flow_id=flow_id,
                    current_step=current_step,
                    last_completed_step="none",
                    created_at=current_time,
                    updated_at=current_time,
                    step_history=[current_step] if current_step else [],
                    output_snapshot={current_step: step_output} if step_output else {}
                )
                
                return await self.save_user_flow_state(new_flow_state)
                
        except Exception as e:
            print(f"更新流程进度失败: {str(e)}")
            return False

    async def get_flow_snapshot(self, user_id: str, flow_id: str) -> Dict[str, Any]:
        """
        get_flow_snapshot 方法获取用户流程的完整快照
        包含当前状态、执行历史和所有步骤的输出数据
        
        参数:
            user_id: 用户标识字符串
            flow_id: 流程标识字符串
        
        返回:
            Dict[str, Any]: 流程快照字典，包含完整的状态信息
        """
        try:
            # 获取用户流程状态
            flow_state = await self.get_user_flow_state(user_id, flow_id)
            
            if not flow_state:
                return {
                    "exists": False,
                    "error": f"No flow state found for user {user_id} in flow {flow_id}"
                }
            
            # 构建完整的快照信息
            return {
                "exists": True,
                "user_id": flow_state.user_id,
                "flow_id": flow_state.flow_id,
                "current_step": flow_state.current_step,
                "last_completed_step": flow_state.last_completed_step,
                "status": flow_state.status,
                "created_at": flow_state.created_at,
                "updated_at": flow_state.updated_at,
                "step_history": flow_state.step_history.copy(),
                "output_snapshot": flow_state.output_snapshot.copy(),
                "input_data": flow_state.input_data.copy(),
                "retry_count": flow_state.retry_count,
                "error_info": flow_state.error_info
            }
            
        except Exception as e:
            return {
                "exists": False,
                "error": f"Failed to get flow snapshot: {str(e)}"
            }

    async def restore_flow_context(self, user_id: str, flow_id: str, target_step: str = None) -> Dict[str, Any]:
        """
        restore_flow_context 方法恢复用户流程到指定状态
        实现断点续传和流程恢复功能
        
        参数:
            user_id: 用户标识字符串
            flow_id: 流程标识字符串
            target_step: 可选的目标步骤，None时恢复到当前步骤
        
        返回:
            Dict[str, Any]: 恢复结果字典，包含恢复后的上下文信息
        """
        try:
            # 获取流程快照
            snapshot = await self.get_flow_snapshot(user_id, flow_id)
            
            if not snapshot["exists"]:
                return {
                    "success": False,
                    "error": "No flow state to restore",
                    "user_id": user_id,
                    "flow_id": flow_id
                }
            
            # 确定要恢复到的步骤
            restore_to_step = target_step or snapshot["current_step"]
            
            # 构建恢复上下文
            restore_context = {
                "success": True,
                "user_id": user_id,
                "flow_id": flow_id,
                "restore_to_step": restore_to_step,
                "previous_step": snapshot["last_completed_step"],
                "available_output": snapshot["output_snapshot"].get(snapshot["last_completed_step"]),
                "step_history": snapshot["step_history"],
                "original_input": snapshot["input_data"],
                "flow_status": snapshot["status"],
                "created_at": snapshot["created_at"],
                "last_updated": snapshot["updated_at"]
            }
            
            return restore_context
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to restore flow context: {str(e)}",
                "user_id": user_id,
                "flow_id": flow_id
            }

    def _doc_to_flow_state(self, doc: Dict[str, Any]) -> UserFlowState:
        """
        _doc_to_flow_state 方法将MongoDB文档转换为UserFlowState实例
        处理数据类型转换和字段映射
        
        参数:
            doc: MongoDB查询返回的文档字典
        
        返回:
            UserFlowState: 转换后的用户流程状态实例
        """
        # 提取必要字段，使用get方法提供默认值
        return UserFlowState(
            user_id=doc.get("user_id", ""),
            flow_id=doc.get("flow_id", ""),
            current_step=doc.get("current_step", ""),
            last_completed_step=doc.get("last_completed_step", "none"),
            created_at=doc.get("created_at", ""),
            updated_at=doc.get("updated_at", ""),
            status=doc.get("status", "ongoing"),
            step_history=doc.get("step_history", []),
            output_snapshot=doc.get("output_snapshot", {}),
            input_data=doc.get("input_data", {}),
            error_info=doc.get("error_info"),
            retry_count=doc.get("retry_count", 0),
            max_retries=doc.get("max_retries", 3)
        )


# user_status_manager 通过UserStatusManager()创建全局用户状态管理器实例
# 用于整个hub模块的用户状态管理和流程恢复功能
user_status_manager = UserStatusManager()
