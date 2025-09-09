# 认证流程定义模块
# 定义所有认证相关流程并注册到flow_registry

from typing import Dict, Any
from hub.flow import FlowDefinition, FlowStep, flow_registry
# 导入业务服务层函数，消除循环导入依赖
# 从services.py导入纯业务逻辑函数，不再依赖intent_handlers
from .services import (
    # 多步流程服务函数
    send_verification_service, verify_code_service, set_password_service,
    oauth_google_url_service, oauth_google_callback_service,
    oauth_facebook_url_service, oauth_facebook_callback_service,
    forgot_password_service, reset_password_service,
    # 单步流程服务函数
    register_service, login_service, refresh_token_service, logout_service,
    get_profile_service, update_settings_service
)


def register_auth_flows():
    """
    register_auth_flows 注册所有认证相关流程到flow_registry的主函数
    包含多步流程（用户注册、OAuth认证、密码重置）和单步流程（登录、受保护功能等）
    实现完整的flow_driven架构，彻底替代旧的intent_handlers映射机制
    
    流程分类:
    - 多步流程: 需要多个步骤协调完成的复杂业务流程  
    - 单步流程: 可以独立完成的原子业务操作
    """
    # print 输出注册开始信息，便于系统启动时追踪注册进度
    print("=== 开始注册Auth模块认证流程 ===")
    
    # 注册多步流程 - 复杂业务流程注册
    # register_user_registration_flow 通过调用注册用户邮箱验证注册的三步流程
    register_user_registration_flow()
    
    # register_google_oauth_flow 通过调用注册Google OAuth认证的两步流程  
    register_google_oauth_flow()
    
    # register_facebook_oauth_flow 通过调用注册Facebook OAuth认证的两步流程
    register_facebook_oauth_flow()
    
    # register_password_reset_flow 通过调用注册密码重置的两步流程
    register_password_reset_flow()
    
    # 注册单步流程 - 原子业务操作注册
    # register_single_step_flows 通过调用注册所有单步认证流程
    register_single_step_flows()
    
    # print 输出注册完成信息，标记Auth模块流程注册全部完成
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
            handler_func=send_verification_service,  # 使用services层函数，消除循环导入
            description="发送邮箱验证码",
            next_step="register_step2",
            required_fields=["email", "test_user"],
            output_fields=["success", "message"]
        ),
        FlowStep(
            step_id="register_step2", 
            module_name="auth",
            handler_func=verify_code_service,  # 使用services层函数，消除循环导入
            description="验证邮箱验证码",
            next_step="register_step3",
            previous_step="register_step1",
            required_fields=["email", "code"],
            output_fields=["success", "message", "user_exists", "is_oauth_user"]
        ),
        FlowStep(
            step_id="register_step3",
            module_name="auth", 
            handler_func=set_password_service,  # 使用services层函数，消除循环导入
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
            handler_func=oauth_google_url_service,  # 使用services层函数，消除循环导入
            description="生成Google OAuth授权URL",
            next_step="oauth_google_step2",
            required_fields=["state"],  # state可选
            output_fields=["auth_url", "provider"]
        ),
        FlowStep(
            step_id="oauth_google_step2", 
            module_name="auth",
            handler_func=oauth_google_callback_service,  # 使用services层函数，消除循环导入
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
            handler_func=oauth_facebook_url_service,  # 使用services层函数，消除循环导入
            description="生成Facebook OAuth授权URL",
            next_step="oauth_facebook_step2",
            required_fields=["state"],  # state可选
            output_fields=["auth_url", "provider"]
        ),
        FlowStep(
            step_id="oauth_facebook_step2", 
            module_name="auth",
            handler_func=oauth_facebook_callback_service,  # 使用services层函数，消除循环导入
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
            handler_func=forgot_password_service,  # 使用services层函数，消除循环导入
            description="发送密码重置验证码",
            next_step="reset_step2",
            required_fields=["email", "test_user"],
            output_fields=["success", "message"]
        ),
        FlowStep(
            step_id="reset_step2", 
            module_name="auth",
            handler_func=reset_password_service,  # 使用services层函数，消除循环导入
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


def register_single_step_flows():
    """
    register_single_step_flows 注册所有单步认证流程到flow_registry
    单步流程是指可以独立完成的原子业务操作，不依赖前置步骤
    
    包含的单步流程:
    - auth_register: 直接用户注册（不走多步验证流程）
    - auth_login: 用户登录认证
    - auth_refresh_token: 刷新访问令牌
    - auth_logout: 用户登出
    - auth_get_profile: 获取用户资料（需认证）
    - auth_update_settings: 更新用户设置（需认证）
    - oauth_google_url: 生成Google OAuth授权URL
    - oauth_google_callback: 处理Google OAuth回调
    - oauth_facebook_url: 生成Facebook OAuth授权URL
    - oauth_facebook_callback: 处理Facebook OAuth回调
    """
    # print 输出单步流程注册开始信息
    print("--- 注册单步认证流程 ---")
    
    # 定义所有单步流程的步骤定义列表
    # single_step_definitions 通过列表字面量创建单步流程定义集合
    single_step_definitions = [
        # auth_register 单步流程 - 直接用户注册
        FlowStep(
            step_id="auth_register",                    # step_id字段设置为统一的认证注册标识
            module_name="auth",                         # module_name字段标识为auth模块
            handler_func=register_service,              # handler_func字段使用services层的注册服务函数
            description="直接用户注册单步流程",            # description字段描述流程功能
            required_fields=["email", "password", "test_user"],  # required_fields列表定义必需的输入字段
            output_fields=["user_id", "success", "message"]      # output_fields列表定义输出字段
        ),
        
        # auth_login 单步流程 - 用户登录认证
        FlowStep(
            step_id="auth_login",                       # step_id字段设置为统一的认证登录标识
            module_name="auth",                         # module_name字段标识为auth模块
            handler_func=login_service,                 # handler_func字段使用services层的登录服务函数
            description="用户登录认证单步流程",            # description字段描述登录功能
            required_fields=["email", "password"],      # required_fields列表定义登录必需字段
            output_fields=["access_token", "refresh_token", "user_id", "success", "message"]  # output_fields列表定义登录输出
        ),
        
        # auth_refresh_token 单步流程 - 刷新访问令牌
        FlowStep(
            step_id="auth_refresh_token",               # step_id字段设置为统一的token刷新标识
            module_name="auth",                         # module_name字段标识为auth模块
            handler_func=refresh_token_service,         # handler_func字段使用services层的token刷新服务函数
            description="刷新访问令牌单步流程",            # description字段描述token刷新功能
            required_fields=["refresh_token"],          # required_fields列表定义刷新token必需字段
            output_fields=["access_token", "refresh_token", "success", "message"]  # output_fields列表定义刷新输出
        ),
        
        # auth_logout 单步流程 - 用户登出
        FlowStep(
            step_id="auth_logout",                      # step_id字段设置为统一的登出标识
            module_name="auth",                         # module_name字段标识为auth模块
            handler_func=logout_service,                # handler_func字段使用services层的登出服务函数
            description="用户登出单步流程",               # description字段描述登出功能
            required_fields=["Authorization"],          # required_fields列表定义登出认证必需字段
            output_fields=["success", "message"]        # output_fields列表定义登出输出结果
        ),
        
        # auth_get_profile 单步流程 - 获取用户资料（需认证）
        FlowStep(
            step_id="auth_get_profile",                 # step_id字段设置为统一的获取资料标识
            module_name="auth",                         # module_name字段标识为auth模块
            handler_func=get_profile_service,           # handler_func字段使用services层的获取资料服务函数
            description="获取用户资料单步流程（需认证）",   # description字段描述获取资料功能
            required_fields=["Authorization"],          # required_fields列表定义获取资料认证必需字段
            output_fields=["user_profile", "success", "message"]  # output_fields列表定义资料输出
        ),
        
        # auth_update_settings 单步流程 - 更新用户设置（需认证）
        FlowStep(
            step_id="auth_update_settings",             # step_id字段设置为统一的更新设置标识
            module_name="auth",                         # module_name字段标识为auth模块
            handler_func=update_settings_service,       # handler_func字段使用services层的更新设置服务函数
            description="更新用户设置单步流程（需认证）",   # description字段描述更新设置功能
            required_fields=["Authorization"],          # required_fields列表定义更新设置认证必需字段
            output_fields=["updated_settings", "success", "message"]  # output_fields列表定义更新输出
        ),
        
        # oauth_google_url 单步流程 - 生成Google OAuth授权URL
        FlowStep(
            step_id="oauth_google_url",                 # step_id字段设置为统一的Google OAuth URL标识
            module_name="auth",                         # module_name字段标识为auth模块
            handler_func=oauth_google_url_service,      # handler_func字段使用services层的Google URL服务函数
            description="生成Google OAuth授权URL单步流程",  # description字段描述Google URL生成功能
            required_fields=[],                         # required_fields列表为空，state字段可选
            output_fields=["auth_url", "provider", "success", "message"]  # output_fields列表定义URL输出
        ),
        
        # oauth_google_callback 单步流程 - 处理Google OAuth回调
        FlowStep(
            step_id="oauth_google_callback",            # step_id字段设置为统一的Google OAuth回调标识
            module_name="auth",                         # module_name字段标识为auth模块
            handler_func=oauth_google_callback_service, # handler_func字段使用services层的Google回调服务函数
            description="处理Google OAuth回调单步流程",   # description字段描述Google回调处理功能
            required_fields=["code"],                   # required_fields列表定义回调必需的授权码字段
            output_fields=["access_token", "refresh_token", "user_id", "success", "message"]  # output_fields列表定义回调输出
        ),
        
        # oauth_facebook_url 单步流程 - 生成Facebook OAuth授权URL
        FlowStep(
            step_id="oauth_facebook_url",               # step_id字段设置为统一的Facebook OAuth URL标识
            module_name="auth",                         # module_name字段标识为auth模块
            handler_func=oauth_facebook_url_service,    # handler_func字段使用services层的Facebook URL服务函数
            description="生成Facebook OAuth授权URL单步流程",  # description字段描述Facebook URL生成功能
            required_fields=[],                         # required_fields列表为空，state字段可选
            output_fields=["auth_url", "provider", "success", "message"]  # output_fields列表定义URL输出
        ),
        
        # oauth_facebook_callback 单步流程 - 处理Facebook OAuth回调
        FlowStep(
            step_id="oauth_facebook_callback",          # step_id字段设置为统一的Facebook OAuth回调标识
            module_name="auth",                         # module_name字段标识为auth模块
            handler_func=oauth_facebook_callback_service,  # handler_func字段使用services层的Facebook回调服务函数
            description="处理Facebook OAuth回调单步流程",   # description字段描述Facebook回调处理功能
            required_fields=["code"],                   # required_fields列表定义回调必需的授权码字段
            output_fields=["access_token", "refresh_token", "user_id", "success", "message"]  # output_fields列表定义回调输出
        ),
        
        # auth_forgot_password 单步流程 - 发送密码重置验证码
        FlowStep(
            step_id="auth_forgot_password",             # step_id字段设置为统一的忘记密码标识
            module_name="auth",                         # module_name字段标识为auth模块
            handler_func=forgot_password_service,       # handler_func字段使用services层的忘记密码服务函数
            description="发送密码重置验证码单步流程",       # description字段描述忘记密码功能
            required_fields=["email"],                  # required_fields列表定义必需的邮箱字段
            output_fields=["success", "message"]        # output_fields列表定义输出字段
        ),
        
        # auth_reset_password 单步流程 - 验证码重置密码
        FlowStep(
            step_id="auth_reset_password",              # step_id字段设置为统一的重置密码标识
            module_name="auth",                         # module_name字段标识为auth模块
            handler_func=reset_password_service,        # handler_func字段使用services层的重置密码服务函数
            description="验证码重置密码单步流程",           # description字段描述重置密码功能
            required_fields=["email", "code", "new_password"],  # required_fields列表定义重置密码必需字段
            output_fields=["success", "message"]        # output_fields列表定义重置输出
        )
    ]
    
    # 批量注册所有单步流程定义到flow_registry
    # for step_definition in single_step_definitions 遍历所有单步流程定义
    for step_definition in single_step_definitions:
        # flow_registry.register_step 通过调用流程注册中心注册每个单步流程
        step_registered = flow_registry.register_step(step_definition)
        
        # if step_registered 条件检查单步流程注册是否成功
        if step_registered:
            # print 输出单步流程注册成功信息，包含步骤标识
            print(f"  ✓ 单步流程注册成功: {step_definition.step_id}")
        else:
            # print 输出单步流程注册失败信息，包含步骤标识
            print(f"  ✗ 单步流程注册失败: {step_definition.step_id}")
    
    # print 输出单步流程注册完成信息
    print("  单步认证流程注册完成")
    print("")


def validate_all_auth_flows() -> Dict[str, Dict[str, Any]]:
    """
    validate_all_auth_flows 验证所有认证流程的完整性
    检查多步流程和单步流程是否都成功注册到flow_registry中
    
    返回:
        dict: 每个流程的验证结果，包含多步流程和单步流程的验证状态
    """
    # flow_ids 通过列表定义需要验证的多步流程标识
    flow_ids = [
        "user_registration",                # 用户注册多步流程
        "oauth_google_authentication",      # Google OAuth多步流程 
        "oauth_facebook_authentication",    # Facebook OAuth多步流程
        "password_reset"                    # 密码重置多步流程
    ]
    
    # single_step_ids 通过列表定义需要验证的单步流程标识
    single_step_ids = [
        "auth_register", "auth_login", "auth_refresh_token", "auth_logout",
        "auth_get_profile", "auth_update_settings",
        "oauth_google_url", "oauth_google_callback",
        "oauth_facebook_url", "oauth_facebook_callback",
        "auth_forgot_password", "auth_reset_password"
    ]
    
    # validation_results 通过字典初始化验证结果存储结构
    validation_results = {}
    
    # 验证多步流程完整性
    # for flow_id in flow_ids 遍历所有多步流程标识
    for flow_id in flow_ids:
        # flow_registry.validate_flow_integrity 通过调用验证指定流程的完整性
        validation_results[flow_id] = flow_registry.validate_flow_integrity(flow_id)
    
    # 验证单步流程注册状态
    # for step_id in single_step_ids 遍历所有单步流程标识
    for step_id in single_step_ids:
        # flow_registry.get_step 通过调用检查单步流程是否已注册
        step_definition = flow_registry.get_step(step_id)
        # validation_results[step_id] 通过字典赋值记录单步流程验证结果
        validation_results[step_id] = {
            "valid": step_definition is not None,      # valid字段标识流程是否有效注册
            "type": "single_step",                     # type字段标识为单步流程类型
            "registered": step_definition is not None  # registered字段标识是否已注册
        }
    
    # return 语句返回包含所有流程验证结果的字典
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
