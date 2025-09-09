# 认证流程定义模块
# 定义所有认证相关流程并注册到flow_registry

from typing import Dict, Any
from hub.flow import FlowDefinition, FlowStep, flow_registry
# 直接导入处理函数，不再依赖INTENT_HANDLERS映射
from .intent_handlers import (
    handle_auth_send_verification, handle_auth_verify_code, handle_auth_set_password,
    handle_auth_oauth_google_url, handle_auth_oauth_google_callback,
    handle_auth_oauth_facebook_url, handle_auth_oauth_facebook_callback,
    handle_auth_forgot_password, handle_auth_reset_password
)


def register_auth_flows():
    """
    注册所有认证相关流程到flow_registry
    
    包含用户注册流程、OAuth认证流程、密码重置流程等
    每个流程包含完整的步骤定义和链接关系
    """
    print("=== 开始注册Auth模块认证流程 ===")
    
    # 注册用户邮箱注册流程
    register_user_registration_flow()
    
    # 注册Google OAuth流程
    register_google_oauth_flow()
    
    # 注册Facebook OAuth流程
    register_facebook_oauth_flow()
    
    # 注册密码重置流程
    register_password_reset_flow()
    
    print("=== Auth模块所有认证流程注册完成 ===")


def register_user_registration_flow():
    """
    注册用户邮箱验证注册流程
    
    包含三个步骤：
    1. 发送验证码
    2. 验证验证码
    3. 设置密码完成注册
    """
    print("--- 注册用户邮箱注册流程 ---")
    
    # === 1. 定义用户注册流程 ===
    
    # FlowDefinition 通过构造函数创建用户注册流程定义
    registration_flow = FlowDefinition(
        flow_id="user_registration",
        name="用户邮箱验证注册流程",
        description="通过邮箱验证码完成用户注册的完整流程",
        modules=["auth"],  # 参与的模块列表
        steps=["register_step1", "register_step2", "register_step3"],  # 步骤顺序
        entry_step="register_step1",  # 入口步骤
        exit_steps=["register_step3"],  # 出口步骤列表
        flow_type="linear",  # 流程类型：线性
        max_steps=3,  # 最大步骤数
        timeout_seconds=900  # 流程超时时间：15分钟
    )
    
    # === 2. 注册流程定义 ===
    
    # flow_registry.register_flow 通过调用流程注册中心注册流程定义
    flow_registered = flow_registry.register_flow(registration_flow)
    
    if flow_registered:
        print(f"✓ 用户注册流程注册成功: {registration_flow.flow_id}")
    else:
        print(f"✗ 用户注册流程注册失败: {registration_flow.flow_id}")
    
    # === 3. 定义并注册步骤 ===
    
    # 创建步骤定义列表
    registration_steps = [
        FlowStep(
            step_id="register_step1",
            module_name="auth",
            handler_func=handle_auth_send_verification,
            description="发送邮箱验证码",
            next_step="register_step2",
            required_fields=["email", "test_user"],
            output_fields=["success", "message"]
        ),
        FlowStep(
            step_id="register_step2", 
            module_name="auth",
            handler_func=handle_auth_verify_code,
            description="验证邮箱验证码",
            next_step="register_step3",
            previous_step="register_step1",
            required_fields=["email", "code"],
            output_fields=["success", "message", "user_exists", "is_oauth_user"]
        ),
        FlowStep(
            step_id="register_step3",
            module_name="auth", 
            handler_func=handle_auth_set_password,
            description="设置密码完成注册",
            previous_step="register_step2",
            required_fields=["email", "password"],
            output_fields=["success", "message", "user_id"]
        )
    ]
    
    # 注册所有步骤
    for step in registration_steps:
        # flow_registry.register_step 通过调用注册中心注册步骤定义
        step_registered = flow_registry.register_step(step)
        
        if step_registered:
            print(f"  ✓ 步骤注册成功: {step.step_id}")
        else:
            print(f"  ✗ 步骤注册失败: {step.step_id}")
    
    # === 4. 验证流程完整性 ===
    
    # flow_registry.validate_flow_integrity 通过调用验证流程的完整性
    validation_result = flow_registry.validate_flow_integrity("user_registration")
    
    print(f"  流程完整性验证: {'✓ 通过' if validation_result['valid'] else '✗ 失败'}")
    if validation_result.get('errors'):
        print(f"  错误: {validation_result['errors']}")
    
    print("")


def register_google_oauth_flow():
    """
    注册Google OAuth认证流程
    
    包含两个步骤：
    1. 生成OAuth授权URL
    2. 处理OAuth回调完成登录
    """
    print("--- 注册Google OAuth认证流程 ---")
    
    # === 1. 定义Google OAuth流程 ===
    
    # FlowDefinition 通过构造函数创建Google OAuth流程定义
    google_oauth_flow = FlowDefinition(
        flow_id="oauth_google_authentication",
        name="Google OAuth认证流程",
        description="通过Google第三方登录完成用户认证的流程",
        modules=["auth"],  # 参与的模块列表
        steps=["oauth_google_step1", "oauth_google_step2"],  # 步骤顺序
        entry_step="oauth_google_step1",  # 入口步骤
        exit_steps=["oauth_google_step2"],  # 出口步骤列表
        flow_type="linear",  # 流程类型：线性
        max_steps=2,  # 最大步骤数
        timeout_seconds=300  # 流程超时时间：5分钟
    )
    
    # === 2. 注册流程定义 ===
    
    # flow_registry.register_flow 通过调用流程注册中心注册流程定义
    flow_registered = flow_registry.register_flow(google_oauth_flow)
    
    if flow_registered:
        print(f"✓ Google OAuth流程注册成功: {google_oauth_flow.flow_id}")
    else:
        print(f"✗ Google OAuth流程注册失败: {google_oauth_flow.flow_id}")
    
    # === 3. 定义并注册步骤 ===
    
    # 创建步骤定义列表
    google_oauth_steps = [
        FlowStep(
            step_id="oauth_google_step1",
            module_name="auth",
            handler_func=handle_auth_oauth_google_url,
            description="生成Google OAuth授权URL",
            next_step="oauth_google_step2",
            required_fields=["state"],  # state可选
            output_fields=["auth_url", "provider"]
        ),
        FlowStep(
            step_id="oauth_google_step2", 
            module_name="auth",
            handler_func=handle_auth_oauth_google_callback,
            description="处理Google OAuth回调完成登录",
            previous_step="oauth_google_step1",
            required_fields=["code", "state", "expected_state"],
            output_fields=["user_id", "email", "access_token", "refresh_token"]
        )
    ]
    
    # 注册所有步骤
    for step in google_oauth_steps:
        # flow_registry.register_step 通过调用注册中心注册步骤定义
        step_registered = flow_registry.register_step(step)
        
        if step_registered:
            print(f"  ✓ 步骤注册成功: {step.step_id}")
        else:
            print(f"  ✗ 步骤注册失败: {step.step_id}")
    
    # === 4. 验证流程完整性 ===
    
    # flow_registry.validate_flow_integrity 通过调用验证流程的完整性
    validation_result = flow_registry.validate_flow_integrity("oauth_google_authentication")
    
    print(f"  流程完整性验证: {'✓ 通过' if validation_result['valid'] else '✗ 失败'}")
    if validation_result.get('errors'):
        print(f"  错误: {validation_result['errors']}")
    
    print("")


def register_facebook_oauth_flow():
    """
    注册Facebook OAuth认证流程
    
    包含两个步骤：
    1. 生成OAuth授权URL
    2. 处理OAuth回调完成登录
    """
    print("--- 注册Facebook OAuth认证流程 ---")
    
    # === 1. 定义Facebook OAuth流程 ===
    
    # FlowDefinition 通过构造函数创建Facebook OAuth流程定义
    facebook_oauth_flow = FlowDefinition(
        flow_id="oauth_facebook_authentication",
        name="Facebook OAuth认证流程",
        description="通过Facebook第三方登录完成用户认证的流程",
        modules=["auth"],  # 参与的模块列表
        steps=["oauth_facebook_step1", "oauth_facebook_step2"],  # 步骤顺序
        entry_step="oauth_facebook_step1",  # 入口步骤
        exit_steps=["oauth_facebook_step2"],  # 出口步骤列表
        flow_type="linear",  # 流程类型：线性
        max_steps=2,  # 最大步骤数
        timeout_seconds=300  # 流程超时时间：5分钟
    )
    
    # === 2. 注册流程定义 ===
    
    # flow_registry.register_flow 通过调用流程注册中心注册流程定义
    flow_registered = flow_registry.register_flow(facebook_oauth_flow)
    
    if flow_registered:
        print(f"✓ Facebook OAuth流程注册成功: {facebook_oauth_flow.flow_id}")
    else:
        print(f"✗ Facebook OAuth流程注册失败: {facebook_oauth_flow.flow_id}")
    
    # === 3. 定义并注册步骤 ===
    
    # 创建步骤定义列表
    facebook_oauth_steps = [
        FlowStep(
            step_id="oauth_facebook_step1",
            module_name="auth",
            handler_func=handle_auth_oauth_facebook_url,
            description="生成Facebook OAuth授权URL",
            next_step="oauth_facebook_step2",
            required_fields=["state"],  # state可选
            output_fields=["auth_url", "provider"]
        ),
        FlowStep(
            step_id="oauth_facebook_step2", 
            module_name="auth",
            handler_func=handle_auth_oauth_facebook_callback,
            description="处理Facebook OAuth回调完成登录",
            previous_step="oauth_facebook_step1",
            required_fields=["code", "state", "expected_state"],
            output_fields=["user_id", "email", "access_token", "refresh_token"]
        )
    ]
    
    # 注册所有步骤
    for step in facebook_oauth_steps:
        # flow_registry.register_step 通过调用注册中心注册步骤定义
        step_registered = flow_registry.register_step(step)
        
        if step_registered:
            print(f"  ✓ 步骤注册成功: {step.step_id}")
        else:
            print(f"  ✗ 步骤注册失败: {step.step_id}")
    
    # === 4. 验证流程完整性 ===
    
    # flow_registry.validate_flow_integrity 通过调用验证流程的完整性
    validation_result = flow_registry.validate_flow_integrity("oauth_facebook_authentication")
    
    print(f"  流程完整性验证: {'✓ 通过' if validation_result['valid'] else '✗ 失败'}")
    if validation_result.get('errors'):
        print(f"  错误: {validation_result['errors']}")
    
    print("")


def register_password_reset_flow():
    """
    注册密码重置流程
    
    包含三个步骤：
    1. 发送重置验证码
    2. 验证重置验证码（可选单独验证步骤）
    3. 重置密码
    """
    print("--- 注册密码重置流程 ---")
    
    # === 1. 定义密码重置流程 ===
    
    # FlowDefinition 通过构造函数创建密码重置流程定义
    password_reset_flow = FlowDefinition(
        flow_id="password_reset",
        name="密码重置流程",
        description="通过邮箱验证码重置用户密码的完整流程",
        modules=["auth"],  # 参与的模块列表
        steps=["reset_step1", "reset_step2"],  # 步骤顺序（简化为两步）
        entry_step="reset_step1",  # 入口步骤
        exit_steps=["reset_step2"],  # 出口步骤列表
        flow_type="linear",  # 流程类型：线性
        max_steps=2,  # 最大步骤数
        timeout_seconds=600  # 流程超时时间：10分钟
    )
    
    # === 2. 注册流程定义 ===
    
    # flow_registry.register_flow 通过调用流程注册中心注册流程定义
    flow_registered = flow_registry.register_flow(password_reset_flow)
    
    if flow_registered:
        print(f"✓ 密码重置流程注册成功: {password_reset_flow.flow_id}")
    else:
        print(f"✗ 密码重置流程注册失败: {password_reset_flow.flow_id}")
    
    # === 3. 定义并注册步骤 ===
    
    # 创建步骤定义列表
    password_reset_steps = [
        FlowStep(
            step_id="reset_step1",
            module_name="auth",
            handler_func=handle_auth_forgot_password,
            description="发送密码重置验证码",
            next_step="reset_step2",
            required_fields=["email", "test_user"],
            output_fields=["success", "message"]
        ),
        FlowStep(
            step_id="reset_step2", 
            module_name="auth",
            handler_func=handle_auth_reset_password,
            description="验证验证码并重置密码",
            previous_step="reset_step1",
            required_fields=["email", "code", "new_password"],
            output_fields=["success", "message"]
        )
    ]
    
    # 注册所有步骤
    for step in password_reset_steps:
        # flow_registry.register_step 通过调用注册中心注册步骤定义
        step_registered = flow_registry.register_step(step)
        
        if step_registered:
            print(f"  ✓ 步骤注册成功: {step.step_id}")
        else:
            print(f"  ✗ 步骤注册失败: {step.step_id}")
    
    # === 4. 验证流程完整性 ===
    
    # flow_registry.validate_flow_integrity 通过调用验证流程的完整性
    validation_result = flow_registry.validate_flow_integrity("password_reset")
    
    print(f"  流程完整性验证: {'✓ 通过' if validation_result['valid'] else '✗ 失败'}")
    if validation_result.get('errors'):
        print(f"  错误: {validation_result['errors']}")
    
    print("")


def get_all_auth_flows() -> Dict[str, FlowDefinition]:
    """
    获取所有认证流程定义
    
    返回:
        dict: 流程ID到FlowDefinition的映射字典
    """
    return {
        "user_registration": flow_registry.get_flow_definition("user_registration"),
        "oauth_google_authentication": flow_registry.get_flow_definition("oauth_google_authentication"),
        "oauth_facebook_authentication": flow_registry.get_flow_definition("oauth_facebook_authentication"),
        "password_reset": flow_registry.get_flow_definition("password_reset")
    }


def validate_all_auth_flows() -> Dict[str, Dict[str, Any]]:
    """
    验证所有认证流程的完整性
    
    返回:
        dict: 每个流程的验证结果
    """
    flow_ids = [
        "user_registration",
        "oauth_google_authentication", 
        "oauth_facebook_authentication",
        "password_reset"
    ]
    
    validation_results = {}
    
    for flow_id in flow_ids:
        validation_results[flow_id] = flow_registry.validate_flow_integrity(flow_id)
    
    return validation_results


# 导出主要函数
__all__ = [
    "register_auth_flows",
    "register_user_registration_flow",
    "register_google_oauth_flow", 
    "register_facebook_oauth_flow",
    "register_password_reset_flow",
    "get_all_auth_flows",
    "validate_all_auth_flows"
]
