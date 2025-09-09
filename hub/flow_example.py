# hub/flow_example.py - 流程调度系统使用示例
# 演示如何注册流程、步骤和使用流程调度功能

import asyncio
from typing import Dict, Any

# 导入流程调度相关类
from .flow import FlowDefinition, FlowStep, flow_registry
from .status import user_status_manager
from .registry_center import RegistryCenter
from .router import router


# ========== 示例：MBTI流程注册 ==========

async def register_mbti_flow_example():
    """
    register_mbti_flow_example 演示如何注册MBTI流程到流程调度系统
    包含完整的5步流程定义和步骤链接关系
    """
    print("=== 注册MBTI流程示例 ===")
    
    # === 1. 定义MBTI流程 ===
    
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
    
    # === 2. 注册流程定义 ===
    
    # flow_registry.register_flow 通过调用流程注册中心注册流程定义
    # 传入mbti_flow参数，建立flow_id到FlowDefinition的映射
    flow_registered = flow_registry.register_flow(mbti_flow)
    
    if flow_registered:
        print(f"✓ MBTI流程注册成功: {mbti_flow.flow_id}")
    else:
        print(f"✗ MBTI流程注册失败: {mbti_flow.flow_id}")
    
    # === 3. 定义并注册各个步骤 ===
    
    # 模拟的步骤处理函数（实际使用时应该是真实的模块处理函数）
    async def mock_step1_handler(request: Dict[str, Any]) -> Dict[str, Any]:
        return {"step": "mbti_step1", "message": "MBTI测试引导完成", "success": True}
    
    async def mock_step2_handler(request: Dict[str, Any]) -> Dict[str, Any]:
        return {"step": "mbti_step2", "mbti_type": "ENFP", "success": True}
    
    async def mock_step3_handler(request: Dict[str, Any]) -> Dict[str, Any]:
        return {"step": "mbti_step3", "reverse_questions": ["Q1", "Q2"], "success": True}
    
    async def mock_step4_handler(request: Dict[str, Any]) -> Dict[str, Any]:
        return {"step": "mbti_step4", "confirmed_type": "ENFP", "success": True}
    
    async def mock_step5_handler(request: Dict[str, Any]) -> Dict[str, Any]:
        return {"step": "mbti_step5", "final_report": "ENFP详细报告", "success": True}
    
    # 创建步骤定义列表
    mbti_steps = [
        FlowStep(
            step_id="mbti_step1",
            module_name="mbti",
            handler_func=mock_step1_handler,
            description="MBTI测试引导和问卷展示",
            next_step="mbti_step2",
            required_fields=["user_id", "request_id"],
            output_fields=["step", "message", "success"]
        ),
        FlowStep(
            step_id="mbti_step2", 
            module_name="mbti",
            handler_func=mock_step2_handler,
            description="MBTI类型初步计算",
            next_step="mbti_step3",
            previous_step="mbti_step1",
            required_fields=["user_id", "responses"],
            output_fields=["step", "mbti_type", "success"]
        ),
        FlowStep(
            step_id="mbti_step3",
            module_name="mbti", 
            handler_func=mock_step3_handler,
            description="反向问题生成",
            next_step="mbti_step4",
            previous_step="mbti_step2",
            required_fields=["user_id", "mbti_type"],
            output_fields=["step", "reverse_questions", "success"]
        ),
        FlowStep(
            step_id="mbti_step4",
            module_name="mbti",
            handler_func=mock_step4_handler, 
            description="反向问题计分和类型确认",
            next_step="mbti_step5",
            previous_step="mbti_step3",
            required_fields=["user_id", "reverse_responses"],
            output_fields=["step", "confirmed_type", "success"]
        ),
        FlowStep(
            step_id="mbti_step5",
            module_name="mbti",
            handler_func=mock_step5_handler,
            description="最终报告生成",
            previous_step="mbti_step4",
            required_fields=["user_id", "confirmed_type"],
            output_fields=["step", "final_report", "success"]
        )
    ]
    
    # 注册所有步骤
    for step in mbti_steps:
        # flow_registry.register_step 通过调用注册中心注册步骤定义
        # 传入step参数，建立step_id到FlowStep的映射
        step_registered = flow_registry.register_step(step)
        
        if step_registered:
            print(f"✓ 步骤注册成功: {step.step_id}")
        else:
            print(f"✗ 步骤注册失败: {step.step_id}")
    
    # === 4. 验证流程完整性 ===
    
    # flow_registry.validate_flow_integrity 通过调用验证流程的完整性
    # 传入flow_id参数，检查步骤链接和前后置条件
    validation_result = flow_registry.validate_flow_integrity("mbti_personality_test")
    
    print(f"\n流程完整性验证结果:")
    print(f"  有效: {validation_result['valid']}")
    print(f"  总步骤数: {validation_result['total_steps']}")
    
    if validation_result['errors']:
        print(f"  错误: {validation_result['errors']}")
    if validation_result['warnings']:
        print(f"  警告: {validation_result['warnings']}")
    
    print("=== MBTI流程注册完成 ===\n")


# ========== 示例：流程调度使用 ==========

async def demonstrate_flow_execution():
    """
    demonstrate_flow_execution 演示流程调度的完整执行过程
    包含用户状态管理、断点续传和跨步骤协调
    """
    print("=== 流程执行演示 ===")
    
    # === 1. 模拟用户开始MBTI流程 ===
    
    user_id = "test_user_12345"
    test_request = {
        "user_id": user_id,
        "request_id": "2024-12-19T10:30:00+0800_test-uuid-001"
    }
    
    print(f"用户 {user_id} 开始MBTI测试流程")
    
    # === 2. 执行第一步：mbti_step1 ===
    
    print("\n--- 执行 mbti_step1 ---")
    
    # router.route 通过调用增强的路由方法处理意图
    # 传入"mbti_step1"意图和test_request请求数据
    # 路由器会自动识别流程上下文、创建用户状态并执行步骤
    step1_result = await router.route("mbti_step1", test_request)
    
    print(f"步骤1结果: {step1_result}")
    
    # === 3. 查看用户流程状态 ===
    
    print("\n--- 查看用户流程状态 ---")
    
    # user_status_manager.get_flow_snapshot 通过调用获取用户流程快照
    # 传入user_id和flow_id参数，返回完整的状态信息
    user_snapshot = await user_status_manager.get_flow_snapshot(
        user_id, 
        "mbti_personality_test"
    )
    
    if user_snapshot.get("exists"):
        print(f"当前步骤: {user_snapshot['current_step']}")
        print(f"最后完成步骤: {user_snapshot['last_completed_step']}")
        print(f"步骤历史: {user_snapshot['step_history']}")
        print(f"流程状态: {user_snapshot['status']}")
    else:
        print(f"用户流程状态获取失败: {user_snapshot.get('error')}")
    
    # === 4. 继续执行第二步：mbti_step2 ===
    
    print("\n--- 执行 mbti_step2 ---")
    
    # 模拟用户提供答案数据
    step2_request = test_request.copy()
    step2_request.update({
        "responses": ["A1", "B2", "C1", "D2"]  # 模拟用户答案
    })
    
    # router.route 通过调用路由方法处理第二步
    # 路由器会自动恢复用户状态、识别当前步骤并执行
    step2_result = await router.route("mbti_step2", step2_request)
    
    print(f"步骤2结果: {step2_result}")
    
    # === 5. 模拟断点续传场景 ===
    
    print("\n--- 模拟断点续传 ---")
    
    # 获取恢复上下文
    # user_status_manager.restore_flow_context 通过调用恢复流程上下文
    # 传入user_id、flow_id和目标步骤，获取恢复所需的信息
    recovery_context = await user_status_manager.restore_flow_context(
        user_id,
        "mbti_personality_test",
        "mbti_step3"  # 恢复到第三步
    )
    
    if recovery_context.get("success"):
        print(f"恢复到步骤: {recovery_context['restore_to_step']}")
        print(f"前一步骤: {recovery_context['previous_step']}")
        print(f"可用输出: {recovery_context.get('available_output')}")
        print(f"步骤历史: {recovery_context['step_history']}")
    else:
        print(f"流程恢复失败: {recovery_context.get('error')}")
    
    # === 6. 获取流程进度信息 ===
    
    print("\n--- 流程进度信息 ---")
    
    # flow_registry.get_flow_progress 通过调用获取流程进度
    # 传入flow_id和当前步骤，计算完成百分比和剩余步骤
    progress_info = flow_registry.get_flow_progress(
        "mbti_personality_test", 
        "mbti_step2"
    )
    
    if "error" not in progress_info:
        print(f"流程进度: {progress_info['progress']}%")
        print(f"当前步骤位置: {progress_info['current_index'] + 1}/{progress_info['total_steps']}")
        print(f"已完成步骤: {progress_info['completed_steps']}")
        print(f"剩余步骤: {progress_info['remaining_steps']}")
        print(f"是否首步: {progress_info['is_first_step']}")
        print(f"是否末步: {progress_info['is_last_step']}")
    else:
        print(f"进度信息获取失败: {progress_info['error']}")
    
    print("=== 流程执行演示完成 ===\n")


# ========== 示例：注册中心集成 ==========

async def demonstrate_registry_integration():
    """
    demonstrate_registry_integration 演示注册中心的流程调度集成功能
    展示如何通过注册中心统一管理流程和步骤
    """
    print("=== 注册中心集成演示 ===")
    
    # === 1. 创建注册中心实例 ===
    
    # RegistryCenter() 通过构造函数创建注册中心实例
    # 包含原有的模块注册功能和新增的流程调度功能
    registry = RegistryCenter()
    
    # === 2. 通过注册中心注册流程 ===
    
    # 创建简单的认证流程示例
    auth_flow = FlowDefinition(
        flow_id="user_authentication",
        name="用户认证流程",
        description="包含注册和登录的用户认证流程",
        modules=["auth"],
        steps=["auth_register", "auth_login"],
        entry_step="auth_register",
        exit_steps=["auth_login"],
        flow_type="branched",  # 分支流程类型
        max_steps=2,
        timeout_seconds=600  # 10分钟超时
    )
    
    # registry.register_flow 通过调用注册中心的流程注册方法
    # 委托给flow_registry实现流程注册
    auth_flow_registered = registry.register_flow(auth_flow)
    
    print(f"认证流程注册结果: {'成功' if auth_flow_registered else '失败'}")
    
    # === 3. 查询流程和步骤信息 ===
    
    print("\n--- 查询流程信息 ---")
    
    # registry.get_flow_definition 通过调用获取流程定义
    retrieved_flow = registry.get_flow_definition("user_authentication")
    
    if retrieved_flow:
        print(f"流程名称: {retrieved_flow.name}")
        print(f"流程类型: {retrieved_flow.flow_type}")
        print(f"包含步骤: {retrieved_flow.steps}")
        print(f"参与模块: {retrieved_flow.modules}")
    else:
        print("流程查询失败")
    
    # === 4. 流程上下文识别 ===
    
    print("\n--- 流程上下文识别 ---")
    
    # registry.identify_flow_from_intent 通过调用识别意图对应的流程
    # 传入意图名称，返回所属的flow_id
    flow_for_mbti = registry.identify_flow_from_intent("mbti_step1")
    flow_for_auth = registry.identify_flow_from_intent("auth_register")
    
    print(f"mbti_step1 属于流程: {flow_for_mbti}")
    print(f"auth_register 属于流程: {flow_for_auth}")
    
    # === 5. 流程跳转验证 ===
    
    print("\n--- 流程跳转验证 ---")
    
    # registry.validate_flow_transition 通过调用验证步骤跳转
    # 传入用户ID、起始步骤和目标步骤，检查跳转有效性
    transition_result = registry.validate_flow_transition(
        "test_user_12345",
        "mbti_step1", 
        "mbti_step2"
    )
    
    print(f"mbti_step1 -> mbti_step2 跳转验证:")
    print(f"  有效: {transition_result['valid']}")
    print(f"  原因: {transition_result['reason']}")
    
    if 'transition_type' in transition_result:
        print(f"  跳转类型: {transition_result['transition_type']}")
    
    print("=== 注册中心集成演示完成 ===\n")


# ========== 主函数：运行所有示例 ==========

async def run_all_examples():
    """
    run_all_examples 运行所有流程调度示例
    展示完整的流程调度系统功能
    """
    print("========== 流程调度系统功能演示 ==========\n")
    
    try:
        # 1. 注册MBTI流程
        await register_mbti_flow_example()
        
        # 2. 演示流程执行
        await demonstrate_flow_execution()
        
        # 3. 演示注册中心集成
        await demonstrate_registry_integration()
        
        print("========== 所有示例执行完成 ==========")
        
    except Exception as e:
        print(f"示例执行失败: {str(e)}")
        import traceback
        traceback.print_exc()


# 如果直接运行此文件，执行所有示例
if __name__ == "__main__":
    # asyncio.run 通过调用运行异步主函数
    # 传入run_all_examples函数，执行完整的示例演示
    asyncio.run(run_all_examples())
