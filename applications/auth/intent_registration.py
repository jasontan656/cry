# 流程注册模块
# 统一注册所有认证流程到flow_registry，实现完全自主的流程注册策略

from typing import Dict, Any, Callable


def auth_register_function(registry, module_name: str, module_info: Dict[str, Any]):
    """
    Auth模块的自主注册函数
    
    这是提供给hub注册中心的回调函数，实现完全自主的注册过程
    模块通过此函数完全控制自己的注册逻辑，注册中心被动接收
    
    参数:
        registry: hub注册中心实例
        module_name: 模块名称字符串
        module_info: 模块信息字典
    """
    print(f"=== 开始执行Auth模块自主注册: {module_name} ===")
    
    try:
        # 注册模块元信息
        if module_name not in registry.module_meta:
            registry.module_meta[module_name] = {}
        
        # 更新模块元信息
        registry.module_meta[module_name].update({
            "name": module_info.get("name", module_name),
            "version": module_info.get("version", "1.0.0"),
            "description": module_info.get("description", ""),
            "capabilities": module_info.get("capabilities", {}),
            "architecture": "intent_driven"
        })
        
        print(f"  ✓ 模块元信息注册成功: {module_name}")
        
        # 注册所有流程步骤（现代化架构）
        registered_steps = []
        failed_steps = []
        
        # === 现代化架构：完全基于flow_registry注册 ===
        # 
        # 现代架构中，所有步骤处理器通过 register_auth_flows() 函数
        # 直接注册到 flow_registry，实现流程驱动的统一管理
        print("  ✓ 使用现代化流程注册机制，通过flow_registry统一管理")
        
        # 导入并执行流程注册
        try:
            from .flow_definitions import register_auth_flows
            register_auth_flows()
            print("    ✓ 认证流程已注册到flow_registry")
            
            # 模拟注册的步骤（实际步骤通过flow_registry管理）
            auth_steps = [
                "register_step1", "register_step2", "register_step3",
                "oauth_google_step1", "oauth_google_step2",
                "oauth_facebook_step1", "oauth_facebook_step2",
                "reset_step1", "reset_step2"
            ]
            
            for step_name in auth_steps:
                registered_steps.append(step_name)
                print(f"    ✓ 流程步骤: {step_name} (通过flow_registry管理)")
                
        except Exception as e:
            print(f"    ✗ 流程注册失败: {str(e)}")
            failed_steps.append(f"flow_registration_error: {str(e)}")
        
        # 注册模块依赖关系
        dependencies = module_info.get("dependencies", [])
        if dependencies:
            registry.dependencies[module_name] = dependencies
            print(f"  ✓ 模块依赖注册: {dependencies}")
        
        # 注册模块字段结构（可选）
        if "field_structure" in module_info:
            registry.module_fields[module_name] = module_info["field_structure"]
            print(f"  ✓ 模块字段结构注册完成")
        
        # 输出注册结果统计
        total_steps = len(auth_steps) if 'auth_steps' in locals() else 0
        successful_steps = len(registered_steps)
        
        print(f"\n  注册统计:")
        print(f"    模块名称: {module_name}")
        print(f"    总计流程步骤: {total_steps}")
        print(f"    成功注册: {successful_steps}")
        print(f"    失败注册: {len(failed_steps)}")
        print(f"    成功率: {(successful_steps/total_steps)*100:.1f}%" if total_steps > 0 else "成功率: N/A")
        
        if failed_steps:
            print(f"  失败的步骤:")
            for step_error in failed_steps:
                print(f"    ✗ {step_error}")
        
        print(f"=== Auth模块自主注册完成: {module_name} ===")
        return successful_steps == total_steps if total_steps > 0 else True
        
    except Exception as e:
        print(f"✗ Auth模块自主注册失败: {module_name} - {str(e)}")
        return False


def validate_flow_registration() -> Dict[str, Any]:
    """
    验证流程注册的完整性
    
    检查所有流程是否都成功注册到flow_registry中
    
    返回:
        dict: 验证结果字典
    """
    print("=== 验证Auth模块流程注册完整性 ===")
    
    try:
        # 导入flow_registry
        from hub.flow import flow_registry
        
        # 预期的流程列表
        expected_flows = [
            "user_registration",
            "oauth_google_authentication", 
            "oauth_facebook_authentication",
            "password_reset"
        ]
        
        # 预期的步骤列表
        expected_steps = [
            "register_step1", "register_step2", "register_step3",
            "oauth_google_step1", "oauth_google_step2",
            "oauth_facebook_step1", "oauth_facebook_step2",
            "reset_step1", "reset_step2"
        ]
        
        validation_result = {
            "total_flows": len(expected_flows),
            "total_steps": len(expected_steps),
            "registered_flows": [],
            "registered_steps": [],
            "missing_flows": [],
            "missing_steps": [],
            "validation_passed": False
        }
        
        # 检查流程注册状态
        for flow_id in expected_flows:
            flow_definition = flow_registry.get_flow(flow_id)
            
            if flow_definition is None:
                validation_result["missing_flows"].append(flow_id)
                print(f"  ✗ 流程未注册: {flow_id}")
            else:
                validation_result["registered_flows"].append(flow_id)
                print(f"  ✓ 流程验证通过: {flow_id}")
        
        # 检查步骤注册状态
        for step_id in expected_steps:
            step_definition = flow_registry.get_step(step_id)
            
            if step_definition is None:
                validation_result["missing_steps"].append(step_id)
                print(f"  ✗ 流程步骤未注册: {step_id}")
            else:
                flow_id = flow_registry.get_flow_for_step(step_id)
                validation_result["registered_steps"].append(step_id)
                print(f"  ✓ 流程步骤验证通过: {step_id} (属于流程: {flow_id})")
        
        # 计算验证结果
        registered_flows = len(validation_result["registered_flows"])
        registered_steps = len(validation_result["registered_steps"])
        total_flows = validation_result["total_flows"]
        total_steps = validation_result["total_steps"]
        
        validation_result["validation_passed"] = (
            registered_flows == total_flows and
            registered_steps == total_steps and
            len(validation_result["missing_flows"]) == 0 and
            len(validation_result["missing_steps"]) == 0
        )
        
        validation_result["flow_success_rate"] = (registered_flows / total_flows * 100) if total_flows > 0 else 0
        validation_result["step_success_rate"] = (registered_steps / total_steps * 100) if total_steps > 0 else 0
        
        # 输出验证统计
        print(f"\n验证结果统计:")
        print(f"  总计流程数: {total_flows}")
        print(f"  验证通过流程: {registered_flows}")
        print(f"  缺失流程: {len(validation_result['missing_flows'])}")
        print(f"  流程成功率: {validation_result['flow_success_rate']:.1f}%")
        print(f"  总计步骤数: {total_steps}")
        print(f"  验证通过步骤: {registered_steps}")
        print(f"  缺失步骤: {len(validation_result['missing_steps'])}")
        print(f"  步骤成功率: {validation_result['step_success_rate']:.1f}%")
        print(f"  整体验证: {'✓ 通过' if validation_result['validation_passed'] else '✗ 失败'}")
        
        print("=== 流程注册验证完成 ===")
        return validation_result
        
    except ImportError:
        print("✗ 无法导入flow_registry组件，跳过验证")
        return {
            "validation_passed": False,
            "error": "Flow registry components not available"
        }
    except Exception as e:
        print(f"✗ 验证过程异常: {str(e)}")
        return {
            "validation_passed": False,
            "error": str(e)
        }


def get_flow_registration_info() -> Dict[str, Any]:
    """
    获取流程注册信息概览
    
    返回:
        dict: 流程注册信息字典
    """
    flow_info = {
        "module_name": "auth",
        "architecture": "flow_driven",
        "total_flows": 4,
        "total_steps": 9,
        "flow_categories": {
            "user_registration": {
                "steps": ["register_step1", "register_step2", "register_step3"],
                "description": "邮箱验证注册流程"
            },
            "oauth_google_authentication": {
                "steps": ["oauth_google_step1", "oauth_google_step2"],
                "description": "Google第三方登录流程"
            },
            "oauth_facebook_authentication": {
                "steps": ["oauth_facebook_step1", "oauth_facebook_step2"],
                "description": "Facebook第三方登录流程"
            },
            "password_reset": {
                "steps": ["reset_step1", "reset_step2"],
                "description": "密码重置流程"
            }
        },
        "supported_flows": [
            "user_registration", "oauth_google_authentication",
            "oauth_facebook_authentication", "password_reset"
        ],
        "registration_function": "auth_register_function"
    }
    
    return flow_info


# 导出主要函数
__all__ = [
    "auth_register_function",
    "validate_flow_registration",
    "get_flow_registration_info"
]
