#!/usr/bin/env python3
"""
Auth模块重构运行门禁验证脚本
验证flow_registry架构迁移后的系统功能完整性
"""

import asyncio
import json
import sys
import os
from typing import Dict, Any, List
from datetime import datetime

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, project_root)

class RuntimeGateValidator:
    """运行门禁验证器，检查重构后的系统功能完整性"""
    
    def __init__(self):
        # test_results 通过列表初始化存储所有测试结果
        self.test_results = []
        # start_time 通过datetime.now获取验证开始时间
        self.start_time = datetime.now()
        
    def log_test_result(self, test_name: str, success: bool, message: str, data: Any = None):
        """
        log_test_result 记录单个测试结果的方法
        用于统一收集和格式化测试结果信息
        
        参数:
            test_name: 测试名称字符串，用于标识具体的测试项目
            success: 布尔值标识测试是否成功通过
            message: 测试结果描述信息字符串
            data: 可选的测试数据，用于详细分析
        """
        # test_result 通过字典构建单个测试结果记录
        test_result = {
            "test_name": test_name,         # test_name字段记录测试名称
            "success": success,             # success字段记录测试通过状态
            "message": message,             # message字段记录结果描述
            "timestamp": datetime.now().isoformat(),  # timestamp字段记录测试时间
            "data": data                    # data字段记录额外的测试数据
        }
        # self.test_results.append 通过调用添加测试结果到列表
        self.test_results.append(test_result)
        
        # 输出测试结果到控制台
        # status_symbol 通过三元运算符根据success状态选择显示符号
        status_symbol = "✅" if success else "❌"
        # print 输出格式化的测试结果信息
        print(f"{status_symbol} {test_name}: {message}")
        
        # if data 条件检查是否有额外数据需要显示
        if data:
            # print 输出缩进的数据信息，使用JSON格式化
            print(f"   Data: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    async def validate_flow_registry_integrity(self) -> bool:
        """
        validate_flow_registry_integrity 验证flow_registry完整性的异步方法
        检查所有预期的流程和步骤是否成功注册到flow_registry中
        
        返回:
            bool: 所有流程注册验证通过返回True，否则返回False
        """
        try:
            # 首先确保模块已注册，触发流程注册
            # import applications.auth 导入模块触发自注册机制
            import applications.auth
            # from applications.auth.flow_definitions import register_auth_flows 导入流程注册函数
            from applications.auth.flow_definitions import register_auth_flows
            
            # 手动触发流程注册以确保flow_registry中有内容
            # register_auth_flows() 通过调用确保所有流程都注册到flow_registry
            register_auth_flows()
            
            # 导入flow_registry模块进行验证
            # from hub.flow import flow_registry 导入流程注册中心
            from hub.flow import flow_registry
            
            # expected_multi_step_flows 通过列表定义预期的多步流程标识
            expected_multi_step_flows = [
                "user_registration",                # 用户注册多步流程
                "oauth_google_authentication",      # Google OAuth多步流程
                "oauth_facebook_authentication",    # Facebook OAuth多步流程  
                "password_reset"                    # 密码重置多步流程
            ]
            
            # expected_single_step_flows 通过列表定义预期的单步流程标识
            expected_single_step_flows = [
                "auth_register", "auth_login", "auth_refresh_token", "auth_logout",
                "auth_get_profile", "auth_update_settings",
                "oauth_google_url", "oauth_google_callback",
                "oauth_facebook_url", "oauth_facebook_callback"
            ]
            
            # 验证多步流程注册状态
            # missing_multi_flows 通过列表初始化存储缺失的多步流程
            missing_multi_flows = []
            # for flow_id in expected_multi_step_flows 遍历所有预期多步流程
            for flow_id in expected_multi_step_flows:
                # flow_definition 通过flow_registry.get_flow检查流程是否存在
                flow_definition = flow_registry.get_flow(flow_id)
                # if not flow_definition 条件检查流程是否缺失
                if not flow_definition:
                    # missing_multi_flows.append 添加缺失流程到列表
                    missing_multi_flows.append(flow_id)
            
            # 验证单步流程注册状态  
            # missing_single_flows 通过列表初始化存储缺失的单步流程
            missing_single_flows = []
            # for step_id in expected_single_step_flows 遍历所有预期单步流程
            for step_id in expected_single_step_flows:
                # step_definition 通过flow_registry.get_step检查步骤是否存在
                step_definition = flow_registry.get_step(step_id)
                # if not step_definition 条件检查步骤是否缺失
                if not step_definition:
                    # missing_single_flows.append 添加缺失步骤到列表
                    missing_single_flows.append(step_id)
            
            # 统计验证结果
            # total_expected 通过加法计算预期流程总数
            total_expected = len(expected_multi_step_flows) + len(expected_single_step_flows)
            # total_missing 通过加法计算缺失流程总数
            total_missing = len(missing_multi_flows) + len(missing_single_flows)
            # success_rate 通过计算得出成功注册率
            success_rate = ((total_expected - total_missing) / total_expected * 100) if total_expected > 0 else 0
            
            # 构建验证结果数据
            # integrity_data 通过字典构建完整性检查结果
            integrity_data = {
                "total_expected_flows": total_expected,              # 预期流程总数
                "missing_multi_step_flows": missing_multi_flows,    # 缺失的多步流程列表
                "missing_single_step_flows": missing_single_flows,  # 缺失的单步流程列表
                "success_rate": f"{success_rate:.1f}%",             # 成功注册率
                "multi_step_success": len(expected_multi_step_flows) - len(missing_multi_flows),  # 多步流程成功数
                "single_step_success": len(expected_single_step_flows) - len(missing_single_flows) # 单步流程成功数
            }
            
            # 判定验证结果
            # validation_success 通过布尔运算检查是否所有流程都已注册
            validation_success = total_missing == 0
            
            # message 通过条件运算符构建结果消息
            message = f"Flow registry完整性验证{'通过' if validation_success else '失败'}: {success_rate}%成功率"
            
            # self.log_test_result 记录完整性验证结果
            self.log_test_result(
                "Flow Registry 完整性验证",
                validation_success,
                message,
                integrity_data
            )
            
            # return 返回验证是否成功的布尔值
            return validation_success
            
        except Exception as e:
            # 异常处理：记录验证失败信息
            self.log_test_result(
                "Flow Registry 完整性验证",
                False,
                f"验证过程异常: {str(e)}"
            )
            # return False 异常时返回验证失败
            return False
    
    async def validate_services_layer_functions(self) -> bool:
        """
        validate_services_layer_functions 验证services层函数可导入性的异步方法
        确保所有业务逻辑函数已成功迁移到services.py并可正常导入
        
        返回:
            bool: 所有services函数导入成功返回True，否则返回False
        """
        try:
            # 尝试导入所有services层函数
            # from applications.auth.services import ... 导入所有迁移的业务服务函数
            from applications.auth.services import (
                # 响应格式化工具函数
                create_success_response, create_error_response,
                # 认证信息提取函数
                extract_auth_info_from_payload, extract_auth_info_from_context,
                # 注册相关服务函数
                register_service, send_verification_service,
                verify_code_service, set_password_service,
                # 登录相关服务函数
                login_service,
                # OAuth相关服务函数
                oauth_google_url_service, oauth_google_callback_service,
                oauth_facebook_url_service, oauth_facebook_callback_service,
                # 密码重置相关服务函数
                forgot_password_service, reset_password_service,
                # 受保护功能服务函数
                get_profile_service, update_settings_service,
                refresh_token_service, logout_service
            )
            
            # 验证函数可调用性
            # service_functions 通过列表存储所有导入的服务函数
            service_functions = [
                create_success_response, create_error_response,
                extract_auth_info_from_payload, extract_auth_info_from_context,
                register_service, send_verification_service,
                verify_code_service, set_password_service,
                login_service,
                oauth_google_url_service, oauth_google_callback_service,
                oauth_facebook_url_service, oauth_facebook_callback_service,
                forgot_password_service, reset_password_service,
                get_profile_service, update_settings_service,
                refresh_token_service, logout_service
            ]
            
            # 检查所有函数是否可调用
            # callable_functions 通过列表推导式筛选可调用函数
            callable_functions = [func for func in service_functions if callable(func)]
            
            # success 通过比较长度判断是否所有函数都可调用
            success = len(callable_functions) == len(service_functions)
            
            # services_data 通过字典构建服务层验证结果
            services_data = {
                "total_functions": len(service_functions),      # 总函数数量
                "callable_functions": len(callable_functions), # 可调用函数数量  
                "import_success": True,                        # 导入成功状态
                "function_categories": {                       # 函数分类统计
                    "response_formatters": 2,    # 响应格式化函数数量
                    "auth_extractors": 2,        # 认证提取函数数量
                    "business_services": 13      # 业务服务函数数量
                }
            }
            
            # message 构建验证结果消息
            message = f"Services层函数验证{'通过' if success else '失败'}: {len(callable_functions)}/{len(service_functions)}个函数可用"
            
            # self.log_test_result 记录services层验证结果
            self.log_test_result(
                "Services层函数验证",
                success,
                message,
                services_data
            )
            
            # return 返回验证是否成功
            return success
            
        except ImportError as e:
            # 导入异常处理
            self.log_test_result(
                "Services层函数验证",
                False,
                f"Services层导入失败: {str(e)}"
            )
            return False
        except Exception as e:
            # 其他异常处理
            self.log_test_result(
                "Services层函数验证", 
                False,
                f"Services层验证异常: {str(e)}"
            )
            return False
    
    async def validate_architecture_metadata(self) -> bool:
        """
        validate_architecture_metadata 验证架构元数据正确性的异步方法
        检查模块元数据中的architecture字段是否正确设置为flow_driven
        
        返回:
            bool: 架构元数据验证通过返回True，否则返回False
        """
        try:
            # 导入模块信息获取函数
            # from applications.auth import get_module_info 导入模块信息获取函数
            from applications.auth import get_module_info
            
            # module_info 通过调用get_module_info获取完整模块信息
            module_info = get_module_info()
            
            # 检查架构标识
            # metadata 通过get方法获取元数据部分
            metadata = module_info.get("metadata", {})
            # architecture 通过get方法获取架构标识
            architecture = metadata.get("architecture")
            # migration_completed 通过get方法获取迁移完成状态
            migration_completed = metadata.get("migration_completed", False)
            # intent_handlers_removed 通过get方法获取旧架构清理状态
            intent_handlers_removed = metadata.get("intent_handlers_removed", False)
            
            # 检查接口架构类型
            # interface 通过get方法获取接口信息
            interface = module_info.get("interface", {})
            # architecture_type 通过get方法获取接口架构类型
            architecture_type = interface.get("architecture_type")
            
            # 验证架构一致性
            # architecture_consistent 通过布尔运算检查架构标识一致性
            architecture_consistent = (
                architecture == "flow_driven" and 
                architecture_type == "flow_driven"
            )
            
            # migration_flags_correct 通过布尔运算检查迁移标识正确性
            migration_flags_correct = migration_completed and intent_handlers_removed
            
            # success 通过布尔运算综合判定验证成功状态
            success = architecture_consistent and migration_flags_correct
            
            # metadata_data 通过字典构建元数据验证结果
            metadata_data = {
                "architecture": architecture,                          # 架构标识
                "architecture_type": architecture_type,                # 接口架构类型
                "migration_completed": migration_completed,            # 迁移完成状态
                "intent_handlers_removed": intent_handlers_removed,    # 旧架构清理状态
                "architecture_consistent": architecture_consistent,    # 架构一致性状态
                "migration_flags_correct": migration_flags_correct,    # 迁移标识正确性
                "total_flow_count": metadata.get("total_flow_count", 0) # 总流程数量
            }
            
            # message 构建验证结果消息
            message = f"架构元数据验证{'通过' if success else '失败'}: architecture={architecture}, migrated={migration_completed}"
            
            # self.log_test_result 记录架构元数据验证结果
            self.log_test_result(
                "架构元数据验证",
                success,
                message,
                metadata_data
            )
            
            # return 返回验证是否成功
            return success
            
        except Exception as e:
            # 异常处理：记录验证失败信息
            self.log_test_result(
                "架构元数据验证",
                False,
                f"元数据验证异常: {str(e)}"
            )
            return False
    
    async def validate_circular_import_resolution(self) -> bool:
        """
        validate_circular_import_resolution 验证循环导入问题解决的异步方法  
        检查flow_definitions是否能正确导入services而不产生循环导入
        
        返回:
            bool: 循环导入问题已解决返回True，否则返回False
        """
        try:
            # 测试关键导入路径是否无循环导入问题
            # from applications.auth.flow_definitions import register_auth_flows 测试流程定义导入
            from applications.auth.flow_definitions import register_auth_flows
            # from applications.auth.services import login_service 测试services层导入
            from applications.auth.services import login_service
            # from applications.auth import get_module_info 测试模块主入口导入
            from applications.auth import get_module_info
            
            # 验证导入的函数是否可调用
            # imports_callable 通过all函数和callable检查所有导入是否可调用
            imports_callable = all([
                callable(register_auth_flows),    # 流程注册函数可调用检查
                callable(login_service),          # 登录服务函数可调用检查
                callable(get_module_info)         # 模块信息函数可调用检查
            ])
            
            # circular_import_data 通过字典构建循环导入验证结果
            circular_import_data = {
                "flow_definitions_import": "成功",     # 流程定义导入状态
                "services_import": "成功",             # services层导入状态
                "module_init_import": "成功",          # 模块初始化导入状态
                "all_imports_callable": imports_callable, # 所有导入可调用状态
                "import_path_resolved": True           # 导入路径解决状态
            }
            
            # message 构建验证结果消息
            message = f"循环导入问题验证通过: 所有关键导入路径正常"
            
            # self.log_test_result 记录循环导入验证结果
            self.log_test_result(
                "循环导入解决验证",
                True,  # 成功导入表示循环导入问题已解决
                message,
                circular_import_data
            )
            
            # return True 所有导入成功表示循环导入问题已解决
            return True
            
        except ImportError as e:
            # 导入异常处理：可能仍有循环导入问题
            self.log_test_result(
                "循环导入解决验证",
                False,
                f"导入失败，可能存在循环导入: {str(e)}"
            )
            return False
        except Exception as e:
            # 其他异常处理
            self.log_test_result(
                "循环导入解决验证",
                False,
                f"循环导入验证异常: {str(e)}"
            )
            return False
    
    async def run_all_gates(self) -> Dict[str, Any]:
        """
        run_all_gates 执行所有运行门禁检查的主方法
        按顺序运行各个验证门禁，收集并汇总验证结果
        
        返回:
            Dict[str, Any]: 包含所有门禁结果的汇总报告
        """
        # print 输出运行门禁开始信息
        print("="*60)
        print("🚀 Auth模块重构运行门禁验证开始")
        print("="*60)
        
        # 执行各个验证门禁
        # gate_results 通过列表存储各个门禁的执行结果
        gate_results = []
        
        # 1. Flow Registry完整性验证门禁
        # registry_result 通过异步调用执行流程注册中心完整性验证
        registry_result = await self.validate_flow_registry_integrity()
        gate_results.append(registry_result)
        
        # 2. Services层函数验证门禁
        # services_result 通过异步调用执行services层函数验证
        services_result = await self.validate_services_layer_functions()
        gate_results.append(services_result)
        
        # 3. 架构元数据验证门禁
        # metadata_result 通过异步调用执行架构元数据验证
        metadata_result = await self.validate_architecture_metadata()
        gate_results.append(metadata_result)
        
        # 4. 循环导入解决验证门禁
        # circular_import_result 通过异步调用执行循环导入问题验证
        circular_import_result = await self.validate_circular_import_resolution()
        gate_results.append(circular_import_result)
        
        # 计算总体验证结果
        # total_gates 通过len函数获取总门禁数量
        total_gates = len(gate_results)
        # passed_gates 通过sum函数统计通过的门禁数量
        passed_gates = sum(gate_results)
        # success_rate 通过计算得出门禁通过率
        success_rate = (passed_gates / total_gates * 100) if total_gates > 0 else 0
        # all_gates_passed 通过布尔运算判断是否所有门禁都通过
        all_gates_passed = passed_gates == total_gates
        
        # end_time 通过datetime.now获取验证结束时间
        end_time = datetime.now()
        # duration 通过时间差计算验证总耗时
        duration = (end_time - self.start_time).total_seconds()
        
        # 构建最终验证报告
        # final_report 通过字典构建完整的验证报告
        final_report = {
            "overall_status": "PASSED" if all_gates_passed else "FAILED",  # 总体验证状态
            "total_gates": total_gates,                                     # 总门禁数量
            "passed_gates": passed_gates,                                   # 通过门禁数量
            "failed_gates": total_gates - passed_gates,                     # 失败门禁数量
            "success_rate": f"{success_rate:.1f}%",                         # 成功率
            "duration_seconds": duration,                                   # 验证总耗时
            "start_time": self.start_time.isoformat(),                      # 开始时间
            "end_time": end_time.isoformat(),                               # 结束时间
            "detailed_results": self.test_results                          # 详细测试结果列表
        }
        
        # 输出最终验证结果
        print("="*60)
        status_emoji = "✅" if all_gates_passed else "❌"
        print(f"{status_emoji} 运行门禁验证结果: {final_report['overall_status']}")
        print(f"📊 通过率: {success_rate:.1f}% ({passed_gates}/{total_gates})")
        print(f"⏱️  总耗时: {duration:.2f}秒")
        print("="*60)
        
        # return 返回完整的验证报告
        return final_report


async def main():
    """
    main 主执行函数，创建验证器实例并运行所有门禁检查
    将验证结果输出到文件以供后续分析
    """
    # validator 通过RuntimeGateValidator构造函数创建验证器实例
    validator = RuntimeGateValidator()
    
    try:
        # 运行所有运行门禁检查
        # report 通过异步调用执行所有验证门禁并获取报告
        report = await validator.run_all_gates()
        
        # 将验证报告写入文件
        # report_path 通过拼接构建报告文件路径
        report_path = os.path.join(os.path.dirname(__file__), "gates_runtime_report.json")
        
        # with open 使用文件上下文管理器写入JSON报告
        with open(report_path, 'w', encoding='utf-8') as f:
            # json.dump 将报告字典序列化写入JSON文件
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # print 输出报告文件保存信息
        print(f"📝 详细验证报告已保存到: {report_path}")
        
        # 根据验证结果设置退出码
        # exit_code 通过条件运算符根据验证结果设置程序退出码
        exit_code = 0 if report["overall_status"] == "PASSED" else 1
        # sys.exit 通过调用设置程序退出码
        sys.exit(exit_code)
        
    except Exception as e:
        # 异常处理：输出运行门禁执行失败信息
        print(f"❌ 运行门禁执行失败: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    # 运行主执行函数
    # asyncio.run 通过调用运行异步主函数
    asyncio.run(main())
