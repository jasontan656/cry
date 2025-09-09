# hub/flow.py - 现代化流程调度与跨模块流程支持模块
# FlowRegistry 作为系统唯一的"步骤标识→处理函数"注册中心
# 完全替代传统的 intent_handlers 映射机制，实现现代化流程驱动架构

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass


@dataclass
class FlowStep:
    """
    FlowStep 类定义流程中单个步骤的标准化结构
    包含步骤标识、处理函数、前置/后置逻辑和流程跳转信息
    """
    # step_id 通过字符串标识流程中的具体步骤，如"mbti_step1"
    step_id: str
    # module_name 通过字符串标识处理该步骤的模块名称
    module_name: str
    # handler_func 通过Callable类型引用具体的步骤处理函数
    handler_func: Callable
    # description 通过字符串描述该步骤的功能说明
    description: str
    # next_step 通过可选字符串指定下一个步骤标识，None表示流程结束
    next_step: Optional[str] = None
    # previous_step 通过可选字符串指定前一个步骤标识，用于回退和校验
    previous_step: Optional[str] = None
    # preconditions 通过字符串列表定义执行该步骤的前置条件
    preconditions: List[str] = None
    # postconditions 通过字符串列表定义执行该步骤后的后置条件
    postconditions: List[str] = None
    # required_fields 通过字符串列表定义执行该步骤所需的输入字段
    required_fields: List[str] = None
    # output_fields 通过字符串列表定义该步骤产生的输出字段
    output_fields: List[str] = None
    
    # __post_init__ 方法在dataclass初始化后执行，设置默认空列表
    def __post_init__(self):
        # preconditions 若为None则初始化为空列表，避免可变默认参数问题
        if self.preconditions is None:
            self.preconditions = []
        # postconditions 若为None则初始化为空列表，避免可变默认参数问题
        if self.postconditions is None:
            self.postconditions = []
        # required_fields 若为None则初始化为空列表，避免可变默认参数问题
        if self.required_fields is None:
            self.required_fields = []
        # output_fields 若为None则初始化为空列表，避免可变默认参数问题
        if self.output_fields is None:
            self.output_fields = []


@dataclass
class FlowDefinition:
    """
    FlowDefinition 类定义完整流程的标准化结构
    包含流程标识、参与模块、步骤序列和流程元数据
    """
    # flow_id 通过字符串标识完整流程，如"mbti_personality_test"
    flow_id: str
    # name 通过字符串定义流程的显示名称
    name: str
    # description 通过字符串描述流程的整体功能和目标
    description: str
    # modules 通过字符串列表标识参与该流程的所有模块
    modules: List[str]
    # steps 通过字符串列表定义流程中所有步骤的执行顺序
    steps: List[str]
    # entry_step 通过字符串标识流程的入口步骤
    entry_step: str
    # exit_steps 通过字符串列表标识可能的流程出口步骤
    exit_steps: List[str]
    # flow_type 通过字符串定义流程类型，如"linear"、"branched"、"conditional"
    flow_type: str = "linear"
    # max_steps 通过整数定义流程允许的最大步骤数，用于防止无限循环
    max_steps: int = 20
    # timeout_seconds 通过整数定义流程超时时间，单位为秒
    timeout_seconds: int = 3600


class FlowRegistry:
    """
    FlowRegistry 类作为流程注册中心
    负责管理流程定义、步骤映射和跨模块流程协调
    """

    # __init__ 方法初始化FlowRegistry实例的核心数据结构
    def __init__(self):
        # flows 初始化为空字典，存储flow_id到FlowDefinition的映射
        self.flows: Dict[str, FlowDefinition] = {}
        # steps 初始化为空字典，存储step_id到FlowStep的映射
        self.steps: Dict[str, FlowStep] = {}
        # flow_steps_mapping 初始化为空字典，存储flow_id到步骤列表的映射
        self.flow_steps_mapping: Dict[str, List[str]] = {}
        # step_to_flow_mapping 初始化为空字典，存储step_id到flow_id的反向映射
        self.step_to_flow_mapping: Dict[str, str] = {}

    def register_flow(self, flow_definition: FlowDefinition) -> bool:
        """
        register_flow 方法注册完整的流程定义到注册中心
        建立flow_id到FlowDefinition的映射和相关索引结构
        
        参数:
            flow_definition: FlowDefinition实例，包含完整的流程定义
        
        返回:
            bool: 注册成功返回True，失败返回False
        """
        try:
            # flow_definition.flow_id 通过访问flow_id属性获取流程标识
            # 作为字典键存储到flows中，值为完整的flow_definition实例
            self.flows[flow_definition.flow_id] = flow_definition
            
            # flow_definition.steps 通过访问steps属性获取步骤列表
            # 存储到flow_steps_mapping中，建立flow_id到步骤列表的映射
            self.flow_steps_mapping[flow_definition.flow_id] = flow_definition.steps.copy()
            
            # 遍历flow_definition.steps列表中的每个步骤标识
            for step_id in flow_definition.steps:
                # step_id 作为键，flow_definition.flow_id作为值
                # 存储到step_to_flow_mapping中，建立步骤到流程的反向映射
                self.step_to_flow_mapping[step_id] = flow_definition.flow_id
            
            # 注册成功返回True
            return True
            
        except Exception as e:
            # 捕获异常并打印错误信息，返回False表示注册失败
            print(f"流程注册失败: {flow_definition.flow_id}, 错误: {str(e)}")
            return False

    def register_step(self, step_definition: FlowStep) -> bool:
        """
        register_step 方法注册单个流程步骤到注册中心
        建立step_id到FlowStep的映射，供流程执行时查找
        
        参数:
            step_definition: FlowStep实例，包含步骤的完整定义
        
        返回:
            bool: 注册成功返回True，失败返回False
        """
        try:
            # step_definition.step_id 通过访问step_id属性获取步骤标识
            # 作为字典键存储到steps中，值为完整的step_definition实例
            self.steps[step_definition.step_id] = step_definition
            
            # 注册成功返回True
            return True
            
        except Exception as e:
            # 捕获异常并打印错误信息，返回False表示注册失败
            print(f"步骤注册失败: {step_definition.step_id}, 错误: {str(e)}")
            return False

    def get_flow(self, flow_id: str) -> Optional[FlowDefinition]:
        """
        get_flow 方法根据flow_id获取完整的流程定义
        供Dispatcher调用以了解流程结构和执行顺序
        
        参数:
            flow_id: 流程标识字符串
        
        返回:
            Optional[FlowDefinition]: 找到则返回FlowDefinition实例，否则返回None
        """
        # flows.get 通过字典get方法查找flow_id对应的FlowDefinition
        # 如果不存在则返回None
        return self.flows.get(flow_id)

    def get_step(self, step_id: str) -> Optional[FlowStep]:
        """
        get_step 方法根据step_id获取步骤的完整定义
        供Dispatcher调用以获取步骤处理函数和执行要求
        
        参数:
            step_id: 步骤标识字符串
        
        返回:
            Optional[FlowStep]: 找到则返回FlowStep实例，否则返回None
        """
        # steps.get 通过字典get方法查找step_id对应的FlowStep
        # 如果不存在则返回None
        return self.steps.get(step_id)

    def get_flow_for_step(self, step_id: str) -> Optional[str]:
        """
        get_flow_for_step 方法根据step_id获取所属的flow_id
        用于确定当前步骤属于哪个流程，实现流程上下文识别
        
        参数:
            step_id: 步骤标识字符串
        
        返回:
            Optional[str]: 找到则返回flow_id字符串，否则返回None
        """
        # step_to_flow_mapping.get 通过字典get方法查找step_id对应的flow_id
        # 如果不存在则返回None
        return self.step_to_flow_mapping.get(step_id)

    def get_next_step(self, current_step_id: str) -> Optional[str]:
        """
        get_next_step 方法根据当前步骤获取下一个步骤标识
        用于实现流程的自动推进和步骤跳转逻辑
        
        参数:
            current_step_id: 当前步骤标识字符串
        
        返回:
            Optional[str]: 找到则返回下一步骤标识，否则返回None
        """
        # get_step 方法通过current_step_id获取当前步骤的FlowStep实例
        current_step = self.get_step(current_step_id)
        
        # 如果当前步骤存在，返回其next_step属性
        # 否则返回None表示没有下一步骤或流程结束
        if current_step:
            return current_step.next_step
        return None

    def get_previous_step(self, current_step_id: str) -> Optional[str]:
        """
        get_previous_step 方法根据当前步骤获取前一个步骤标识
        用于实现流程的回退和错误恢复机制
        
        参数:
            current_step_id: 当前步骤标识字符串
        
        返回:
            Optional[str]: 找到则返回前一步骤标识，否则返回None
        """
        # get_step 方法通过current_step_id获取当前步骤的FlowStep实例
        current_step = self.get_step(current_step_id)
        
        # 如果当前步骤存在，返回其previous_step属性
        # 否则返回None表示没有前一步骤或已是流程起点
        if current_step:
            return current_step.previous_step
        return None

    def validate_flow_integrity(self, flow_id: str) -> Dict[str, Any]:
        """
        validate_flow_integrity 方法强化版流程完整性验证
        现代化设计：全面检查步骤链接、处理函数、模块依赖和流程逻辑
        明确识别并报告哪些流程未注册完整步骤
        
        参数:
            flow_id: 需要验证的流程标识字符串
        
        返回:
            Dict[str, Any]: 详细的验证结果字典，包含错误、警告和建议
        """
        # get_flow 方法通过flow_id获取流程定义
        flow = self.get_flow(flow_id)
        
        # 如果流程不存在，返回验证失败结果
        if not flow:
            return {
                "valid": False,
                "errors": [f"Flow not found: {flow_id}"],
                "missing_registration": [flow_id],
                "suggestion": f"Please register flow '{flow_id}' via flow_registry.register_flow()"
            }
        
        # 初始化验证结果收集器
        errors = []
        warnings = []
        missing_steps = []
        invalid_handlers = []
        broken_links = []
        module_issues = []
        
        # === 基础结构验证 ===
        # 验证entry_step是否在步骤列表中
        if flow.entry_step not in flow.steps:
            errors.append(f"Entry step {flow.entry_step} not in flow steps")
        
        # 验证所有exit_steps是否在步骤列表中
        for exit_step in flow.exit_steps:
            if exit_step not in flow.steps:
                errors.append(f"Exit step {exit_step} not in flow steps")
        
        # === 步骤完整性验证（强化版）===
        registered_steps = []
        unregistered_steps = []
        
        for step_id in flow.steps:
            # get_step 方法检查步骤是否已注册到steps字典中
            step = self.get_step(step_id)
            
            if not step:
                errors.append(f"Step {step_id} not registered")
                missing_steps.append(step_id)
                unregistered_steps.append(step_id)
                continue
            
            registered_steps.append(step_id)
            
            # === 处理函数验证 ===
            # 验证处理函数是否有效且可调用
            if not step.handler_func:
                errors.append(f"Step {step_id} missing handler function")
                invalid_handlers.append(step_id)
            elif not callable(step.handler_func):
                errors.append(f"Step {step_id} handler_func is not callable")
                invalid_handlers.append(step_id)
            
            # === 模块验证 ===
            # 验证步骤所属模块是否明确
            if not step.module_name:
                warnings.append(f"Step {step_id} missing module_name")
                module_issues.append(step_id)
            
            # === 步骤链接验证 ===
            # 验证next_step链接的有效性
            if step.next_step and step.next_step not in flow.steps:
                errors.append(f"Step {step_id} next_step {step.next_step} not in flow")
                broken_links.append(f"{step_id} -> {step.next_step}")
            
            # 验证previous_step链接的有效性
            if step.previous_step and step.previous_step not in flow.steps:
                errors.append(f"Step {step_id} previous_step {step.previous_step} not in flow")
                broken_links.append(f"{step.previous_step} <- {step_id}")
            
            # === 字段依赖验证 ===
            # 检查必需字段是否定义
            if not step.required_fields and not step.output_fields:
                warnings.append(f"Step {step_id} has no field definitions (input/output)")
        
        # === 流程逻辑验证 ===
        # 检查流程是否存在孤立步骤（无法到达）
        reachable_steps = set([flow.entry_step])
        to_visit = [flow.entry_step]
        
        while to_visit:
            current = to_visit.pop(0)
            current_step = self.get_step(current)
            if current_step and current_step.next_step:
                if current_step.next_step not in reachable_steps:
                    reachable_steps.add(current_step.next_step)
                    to_visit.append(current_step.next_step)
        
        unreachable_steps = set(flow.steps) - reachable_steps
        for unreachable in unreachable_steps:
            warnings.append(f"Step {unreachable} is unreachable from entry point")
        
        # === 构建强化版验证结果 ===
        is_valid = len(errors) == 0
        
        result = {
            "valid": is_valid,
            "flow_id": flow_id,
            "total_steps": len(flow.steps),
            "registered_steps": len(registered_steps),
            "unregistered_steps": len(unregistered_steps),
            
            # 错误和警告
            "errors": errors,
            "warnings": warnings,
            
            # 详细问题分类
            "missing_steps": missing_steps,
            "invalid_handlers": invalid_handlers,
            "broken_links": broken_links,
            "module_issues": module_issues,
            "unreachable_steps": list(unreachable_steps),
            
            # 完整性指标
            "completion_rate": round(len(registered_steps) / len(flow.steps) * 100, 2) if flow.steps else 0,
            "handler_coverage": round((len(registered_steps) - len(invalid_handlers)) / len(flow.steps) * 100, 2) if flow.steps else 0,
            
            # 建议和修复指导
            "suggestions": self._generate_integrity_suggestions(
                missing_steps, invalid_handlers, broken_links, module_issues
            )
        }
        
        return result
    
    def _generate_integrity_suggestions(self, missing_steps: List[str], invalid_handlers: List[str], 
                                      broken_links: List[str], module_issues: List[str]) -> List[str]:
        """
        _generate_integrity_suggestions 方法生成流程完整性修复建议
        
        参数:
            missing_steps: 缺失的步骤列表
            invalid_handlers: 无效处理函数的步骤列表
            broken_links: 断开的链接列表
            module_issues: 模块问题步骤列表
        
        返回:
            List[str]: 修复建议列表
        """
        suggestions = []
        
        if missing_steps:
            suggestions.append(f"Register missing steps via flow_registry.register_step(): {', '.join(missing_steps)}")
        
        if invalid_handlers:
            suggestions.append(f"Fix handler functions for steps: {', '.join(invalid_handlers)}")
        
        if broken_links:
            suggestions.append(f"Fix broken step links: {', '.join(broken_links)}")
        
        if module_issues:
            suggestions.append(f"Specify module_name for steps: {', '.join(module_issues)}")
        
        if not suggestions:
            suggestions.append("Flow integrity is complete - no issues found")
        
        return suggestions

    def validate_all_flows_integrity(self) -> Dict[str, Any]:
        """
        validate_all_flows_integrity 方法验证所有注册流程的完整性
        系统级验证：生成全局流程健康报告，识别系统架构问题
        
        返回:
            Dict[str, Any]: 系统级流程完整性报告
        """
        # 获取所有已注册的流程
        all_flows = self.get_all_flows()
        
        if not all_flows:
            return {
                "system_valid": False,
                "total_flows": 0,
                "error": "No flows registered in system",
                "suggestion": "Please register flows via flow_registry.register_flow()"
            }
        
        # 系统级验证结果收集
        flow_reports = {}
        valid_flows = 0
        total_steps = 0
        total_registered_steps = 0
        total_missing_steps = 0
        critical_issues = []
        
        # 验证每个流程
        for flow_id in all_flows.keys():
            report = self.validate_flow_integrity(flow_id)
            flow_reports[flow_id] = report
            
            if report["valid"]:
                valid_flows += 1
            
            total_steps += report["total_steps"]
            total_registered_steps += report["registered_steps"]
            total_missing_steps += report["unregistered_steps"]
            
            # 收集关键问题
            if report["unregistered_steps"] > 0:
                critical_issues.append(f"Flow '{flow_id}' has {report['unregistered_steps']} unregistered steps")
            
            if report["invalid_handlers"]:
                critical_issues.append(f"Flow '{flow_id}' has invalid handlers: {', '.join(report['invalid_handlers'])}")
        
        # 计算系统级指标
        system_completion_rate = round(total_registered_steps / total_steps * 100, 2) if total_steps else 0
        flow_completion_rate = round(valid_flows / len(all_flows) * 100, 2) if all_flows else 0
        
        # 构建系统级报告
        system_report = {
            "system_valid": len(critical_issues) == 0,
            "validation_timestamp": f"System validated with {len(all_flows)} flows",
            
            # 统计概览
            "total_flows": len(all_flows),
            "valid_flows": valid_flows,
            "invalid_flows": len(all_flows) - valid_flows,
            "total_steps": total_steps,
            "registered_steps": total_registered_steps,
            "missing_steps": total_missing_steps,
            
            # 完整性指标
            "system_completion_rate": system_completion_rate,
            "flow_completion_rate": flow_completion_rate,
            
            # 关键问题
            "critical_issues": critical_issues,
            
            # 详细报告
            "flow_reports": flow_reports,
            
            # 系统建议
            "system_recommendations": self._generate_system_recommendations(
                valid_flows, len(all_flows), total_missing_steps, critical_issues
            )
        }
        
        return system_report
    
    def _generate_system_recommendations(self, valid_flows: int, total_flows: int, 
                                       missing_steps: int, critical_issues: List[str]) -> List[str]:
        """
        _generate_system_recommendations 方法生成系统级修复建议
        
        参数:
            valid_flows: 有效流程数量
            total_flows: 总流程数量
            missing_steps: 缺失步骤总数
            critical_issues: 关键问题列表
        
        返回:
            List[str]: 系统级建议列表
        """
        recommendations = []
        
        if missing_steps > 0:
            recommendations.append(f"System has {missing_steps} unregistered steps - register via flow_registry.register_step()")
        
        if valid_flows < total_flows:
            invalid_count = total_flows - valid_flows
            recommendations.append(f"System has {invalid_count} invalid flows - fix integrity issues")
        
        if len(critical_issues) > 3:
            recommendations.append("System has multiple critical issues - consider comprehensive flow audit")
        
        if valid_flows == total_flows and missing_steps == 0:
            recommendations.append("System flow integrity is excellent - all flows properly registered")
        
        return recommendations
    
    def get_all_flows(self) -> Dict[str, FlowDefinition]:
        """
        get_all_flows 方法获取所有已注册的流程定义
        用于系统管理和流程总览功能
        
        返回:
            Dict[str, FlowDefinition]: 所有流程定义的字典副本
        """
        # flows.copy 通过字典copy方法返回浅拷贝
        # 避免外部代码直接修改内部数据结构
        return self.flows.copy()

    def get_flow_progress(self, flow_id: str, current_step_id: str) -> Dict[str, Any]:
        """
        get_flow_progress 方法计算流程的执行进度信息
        根据当前步骤在流程中的位置计算完成百分比
        
        参数:
            flow_id: 流程标识字符串
            current_step_id: 当前执行步骤标识
        
        返回:
            Dict[str, Any]: 包含进度信息的字典
        """
        # get_flow 方法获取流程定义
        flow = self.get_flow(flow_id)
        
        # 如果流程不存在，返回错误信息
        if not flow:
            return {
                "error": f"Flow not found: {flow_id}",
                "progress": 0
            }
        
        try:
            # flow.steps.index 方法查找current_step_id在步骤列表中的索引位置
            current_index = flow.steps.index(current_step_id)
            # len(flow.steps) 计算流程总步骤数
            total_steps = len(flow.steps)
            # 计算进度百分比：(当前位置+1)/总步骤数*100，向上取整
            progress = round(((current_index + 1) / total_steps) * 100, 2)
            
            # 返回详细的进度信息字典
            return {
                "flow_id": flow_id,
                "current_step": current_step_id,
                "current_index": current_index,
                "total_steps": total_steps,
                "progress": progress,
                "remaining_steps": total_steps - current_index - 1,
                "completed_steps": current_index,
                "is_first_step": current_index == 0,
                "is_last_step": current_index == total_steps - 1
            }
            
        except ValueError:
            # current_step_id不在流程步骤列表中，返回错误信息
            return {
                "error": f"Step {current_step_id} not found in flow {flow_id}",
                "progress": 0
            }


# flow_registry 通过FlowRegistry()创建全局流程注册中心实例
# 用于整个hub模块的流程管理和步骤协调
flow_registry = FlowRegistry()
