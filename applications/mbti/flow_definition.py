# applications/mbti/flow_definition.py - MBTI流程标准化定义模块
# 按照hub/flow_example.py标准实现FlowDefinition和FlowStep注册

import sys
import os

# 添加上级目录到Python路径，以便导入hub模块
parent_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, parent_dir)

# 导入流程调度相关类
from hub.flow import FlowDefinition, FlowStep, flow_registry
from hub.status import UserFlowState, user_status_manager

# 导入各步骤处理函数
from applications.mbti import step1, step2, step3, step4, step5


def create_mbti_flow_definition():
    """
    create_mbti_flow_definition 函数创建MBTI流程的完整定义
    按照hub/flow_example.py标准实现流程结构
    
    返回:
        FlowDefinition: 完整的MBTI流程定义对象
    """
    # FlowDefinition 通过构造函数创建MBTI流程定义
    # 包含flow_id、名称、描述、参与模块、步骤序列等完整信息
    mbti_flow = FlowDefinition(
        flow_id="mbti_personality_test",
        name="MBTI性格测试完整流程",
        description="包含初始测试、类型计算、反向验证和最终报告的完整MBTI测试流程",
        modules=["mbti"],  # 参与的模块列表
        steps=["mbti_step1", "mbti_step2", "mbti_step3", "mbti_step4", "mbti_step5"],  # 步骤顺序
        entry_step="mbti_step1",  # 入口步骤
        exit_steps=["mbti_step5"],  # 出口步骤列表
        flow_type="linear",  # 流程类型：线性
        max_steps=5,  # 最大步骤数
        timeout_seconds=1800  # 流程超时时间：30分钟
    )
    
    # 返回构建完成的流程定义对象
    return mbti_flow


def create_mbti_flow_steps():
    """
    create_mbti_flow_steps 函数创建所有MBTI步骤的FlowStep定义
    按照hub/flow_example.py标准定义步骤结构和前后置关系
    
    返回:
        List[FlowStep]: 包含所有步骤定义的列表
    """
    # mbti_steps 通过列表初始化，包含所有FlowStep对象定义
    mbti_steps = [
        FlowStep(
            step_id="mbti_step1",
            module_name="mbti",
            handler_func=step1.process,
            description="MBTI测试引导和问卷展示",
            next_step="mbti_step2",
            required_fields=["user_id", "request_id"],
            output_fields=["step", "message", "success", "next_step", "flow_id", "current_mbti_step"]
        ),
        FlowStep(
            step_id="mbti_step2", 
            module_name="mbti",
            handler_func=step2.process,
            description="MBTI类型初步计算",
            next_step="mbti_step3",
            previous_step="mbti_step1",
            required_fields=["user_id", "request_id", "responses"],
            output_fields=["step", "mbti_result", "analysis", "success", "flow_id"]
        ),
        FlowStep(
            step_id="mbti_step3",
            module_name="mbti", 
            handler_func=step3.process,
            description="反向问题生成",
            next_step="mbti_step4",
            previous_step="mbti_step2",
            required_fields=["user_id", "request_id", "mbti_result"],
            output_fields=["step", "reverse_questions", "success", "flow_id"]
        ),
        FlowStep(
            step_id="mbti_step4",
            module_name="mbti",
            handler_func=step4.process, 
            description="反向问题计分和类型确认",
            next_step="mbti_step5",
            previous_step="mbti_step3",
            required_fields=["user_id", "request_id", "reverse_responses"],
            output_fields=["step", "confirmed_type", "success", "flow_id"]
        ),
        FlowStep(
            step_id="mbti_step5",
            module_name="mbti",
            handler_func=step5.process,
            description="最终报告生成",
            previous_step="mbti_step4",
            required_fields=["user_id", "request_id", "confirmed_type"],
            output_fields=["step", "final_report", "success", "flow_id"]
        )
    ]
    
    # 返回所有步骤定义的列表
    return mbti_steps


async def register_mbti_flow():
    """
    register_mbti_flow 异步函数注册MBTI流程到流程调度系统
    包含完整的流程定义和步骤链接关系注册
    
    返回:
        bool: 注册成功返回True，失败返回False
    """
    print("=== 开始注册MBTI流程到流程调度系统 ===")
    
    try:
        # === 1. 创建并注册流程定义 ===
        
        # create_mbti_flow_definition 通过调用创建MBTI流程定义
        # 不传入参数，返回包含完整流程信息的FlowDefinition对象
        mbti_flow = create_mbti_flow_definition()
        
        # flow_registry.register_flow 通过调用流程注册中心注册流程定义
        # 传入mbti_flow参数，建立flow_id到FlowDefinition的映射
        flow_registered = flow_registry.register_flow(mbti_flow)
        
        if flow_registered:
            print(f"✓ MBTI流程注册成功: {mbti_flow.flow_id}")
        else:
            print(f"✗ MBTI流程注册失败: {mbti_flow.flow_id}")
            return False
        
        # === 2. 创建并注册所有步骤定义 ===
        
        # create_mbti_flow_steps 通过调用创建所有步骤定义
        # 不传入参数，返回包含所有FlowStep对象的列表
        mbti_steps = create_mbti_flow_steps()
        
        # 遍历mbti_steps列表中的每个FlowStep对象
        for step in mbti_steps:
            # flow_registry.register_step 通过调用注册中心注册步骤定义
            # 传入step参数，建立step_id到FlowStep的映射
            step_registered = flow_registry.register_step(step)
            
            if step_registered:
                print(f"✓ 步骤注册成功: {step.step_id}")
            else:
                print(f"✗ 步骤注册失败: {step.step_id}")
                return False
        
        # === 3. 验证流程完整性 ===
        
        # flow_registry.validate_flow_integrity 通过调用验证流程的完整性
        # 传入flow_id参数，检查步骤链接和前后置条件
        validation_result = flow_registry.validate_flow_integrity("mbti_personality_test")
        
        print(f"\n流程完整性验证结果:")
        print(f"  有效: {validation_result['valid']}")
        print(f"  总步骤数: {validation_result['total_steps']}")
        
        if validation_result['errors']:
            print(f"  错误: {validation_result['errors']}")
            return False
        
        if validation_result['warnings']:
            print(f"  警告: {validation_result['warnings']}")
        
        print("=== MBTI流程注册完成 ===\n")
        return True
        
    except Exception as e:
        print(f"MBTI流程注册失败: {str(e)}")
        return False


def get_mbti_flow_definition():
    """
    get_mbti_flow_definition 函数获取已创建的MBTI流程定义
    供外部模块调用获取流程结构信息
    
    返回:
        FlowDefinition: MBTI流程定义对象
    """
    # create_mbti_flow_definition 通过调用创建并返回流程定义
    return create_mbti_flow_definition()


def get_mbti_flow_steps():
    """
    get_mbti_flow_steps 函数获取已创建的MBTI步骤定义列表
    供外部模块调用获取步骤结构信息
    
    返回:
        List[FlowStep]: MBTI步骤定义列表
    """
    # create_mbti_flow_steps 通过调用创建并返回步骤定义列表
    return create_mbti_flow_steps()
