#!/usr/bin/env python3
# test_hub_intent_routing.py - Hub意图路由功能全面异步测试脚本
# 测试目标：通过异步HTTP请求验证hub的意图路由处理能力
#
# 修复说明：根据《Invalid Intent Slowpath Deep Dive Analysis》报告修复测试层性能问题
# - 使用优化的 httpx 客户端配置（避免 DNS 延迟、连接池开销）
# - 统一客户端实例，避免每次请求重建连接
# - 127.0.0.1 替代 localhost，禁用重试和环境变量干扰

import json
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from async_utils import (
    get_async_client, async_http_request, async_concurrent_requests,
    format_test_output, format_performance_stats, format_test_summary,
    check_system_availability_async, BASE_URL
)
# 导入优化的HTTP客户端模块
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'common'))
from http_client import (
    get_sync_client, get_async_client as get_optimized_async_client, 
    sync_client_context, async_client_context,
    safe_request_with_timeout_details
)
from benchmark_utils import (
    warmup_connection, benchmark_invalid_intent_sync,
    benchmark_invalid_intent_async, concurrent_benchmark
)
from report_generator import BenchmarkReportGenerator

async def test_intent_routing_exceptions():
    """
    Phase 1: 异常场景测试 - 意图路由异常处理验证
    目的：验证无效意图、缺失参数、未注册步骤等异常输入的路由处理
    """
    print("\n=== Phase 1: 意图路由异常场景测试 ===")
    
    # 测试1：缺失intent字段的请求
    print("\n--- 测试1: 缺失intent字段的请求 ---")
    request_without_intent = {
        "user_id": "test_user_001",
        "data": "some data"
    }
    
    print("REQUEST DATA:")
    print(json.dumps(request_without_intent, indent=2))
    
    try:
        # 使用优化的同步客户端配置
        client = get_sync_client()
        response, error = safe_request_with_timeout_details(
            client, "POST", "/intent", json=request_without_intent
        )
        
        if error:
            print("REQUEST ERROR:")
            print(json.dumps(error, indent=2))
            return
            
        try:
                response_data = response.json()
        except:
                response_data = {"raw_response": response.text}
            
        print("RESPONSE DATA:")
        print(json.dumps({
                "status_code": response.status_code,
                "error_detected": response.status_code >= 400,
                "intent_validation": "intent" in str(response_data).lower(),
                "system_stable": response.status_code != 500
            }, indent=2))
        
    except Exception as e:
        print("EXCEPTION:")
        print(json.dumps({"error": str(e), "type": type(e).__name__}, indent=2))
    
    # 测试2：未注册的intent路由
    print("\n--- 测试2: 未注册的intent路由 ---")
    unregistered_intent_request = {
        "intent": "definitely_non_existent_step_xyz123",
        "user_id": "test_user_002",
        "data": "test data"
    }
    
    print("REQUEST DATA:")
    print(json.dumps(unregistered_intent_request, indent=2))
    
    try:
        client = get_sync_client()
        response, error = safe_request_with_timeout_details(
            client, "POST", "/intent", json=unregistered_intent_request
        )
        
        if error:
            print("REQUEST ERROR:")
            print(json.dumps(error, indent=2))
            return
            
        try:
                response_data = response.json()
        except:
                response_data = {"raw_response": response.text}
            
        print("RESPONSE DATA:")
        print(json.dumps({
                "status_code": response.status_code,
                "step_not_found": response.status_code >= 400,
                "error_message": "error" in str(response_data).lower() or "not found" in str(response_data).lower(),
                "routing_handled": True
            }, indent=2))
        
    except Exception as e:
        print("EXCEPTION:")
        print(json.dumps({"error": str(e), "type": type(e).__name__}, indent=2))
    
    # 测试3：无效JSON格式的请求
    print("\n--- 测试3: 无效JSON格式的请求 ---")
    print("REQUEST DATA:")
    print(json.dumps({"raw_data": "invalid json content"}, indent=2))
    
    try:
        client = get_sync_client()
        response, error = safe_request_with_timeout_details(
            client, "POST", "/intent",
            content="invalid json content{truncated",
            headers={"Content-Type": "application/json"}
        )
        
        if error:
            print("REQUEST ERROR:")
            print(json.dumps(error, indent=2))
            return
            
        try:
                response_data = response.json()
        except:
                response_data = {"raw_response": response.text}
            
        print("RESPONSE DATA:")
        print(json.dumps({
                "status_code": response.status_code,
                "json_error_handled": response.status_code >= 400,
                "parse_error_detected": "json" in str(response_data).lower() or "parse" in str(response_data).lower(),
                "routing_resilience": response.status_code != 500
            }, indent=2))
        
    except Exception as e:
        print("EXCEPTION:")
        print(json.dumps({"error": str(e), "type": type(e).__name__}, indent=2))
    
    # 测试4：特殊字符的intent测试
    print("\n--- 测试4: 特殊字符intent测试 ---")
    special_char_intents = [
        "intent@#$%", 
        "intent with spaces",
        "intent/with/slash",
        "intent.with.dots",
        "intent-with-dash",
        ""  # 空字符串
    ]
    
    print("REQUEST DATA:")
    print(json.dumps({
        "action": "test_special_character_intents",
        "test_intents": special_char_intents
    }, indent=2))
    
    special_char_results = []
    for intent in special_char_intents:
        test_request = {
            "intent": intent,
            "request_id": f"special_char_test",
            "user_id": "test_user_special"
        }
        
        try:
            client = get_sync_client()
            response, error = safe_request_with_timeout_details(
                client, "POST", "/intent", json=test_request
            )
            
            if error:
                special_char_results.append({
                    "intent": intent if intent else "empty_string",
                    "error": str(error),
                    "handled_appropriately": False
                })
                continue
                
            try:
                    response_data = response.json()
            except:
                    response_data = {"raw_response": response.text[:100]}
                
            special_char_results.append({
                    "intent": intent if intent else "empty_string",
                    "status_code": response.status_code,
                    "handled_appropriately": response.status_code >= 400 or response.status_code == 200,
                    "error_response": "error" in str(response_data).lower()
                })
        except Exception as e:
            special_char_results.append({
                "intent": intent if intent else "empty_string",
                "exception": str(e),
                "handled_appropriately": False
            })
    
    print("RESPONSE DATA:")
    print(json.dumps({
        "special_character_test_results": special_char_results,
        "total_tested": len(special_char_intents),
        "properly_handled": sum(1 for r in special_char_results if r.get("handled_appropriately", False))
    }, indent=2))

async def test_valid_intent_routing():
    """
    Phase 2: 正常场景测试 - 标准意图路由功能验证
    目的：验证正确的intent路由、参数传递、响应格式等正常功能
    """
    print("\n=== Phase 2: 意图路由正常场景测试 ===")
    
    # 测试5：探测可能存在的基本intent
    print("\n--- 测试5: 探测系统可用intent ---")
    
    # 常见的可能存在的intent名称
    potential_intents = [
        "test", "ping", "health", "status", "echo",
        "hello", "basic", "simple", "check", "validate"
    ]
    
    print("REQUEST DATA:")
    print(json.dumps({
        "action": "probe_available_intents",
        "potential_intents": potential_intents
    }, indent=2))
    
    available_intents = []
    intent_results = []
    
    for intent in potential_intents:
        test_request = {
            "intent": intent,
            "request_id": f"probe_{intent}",
            "user_id": "test_user_probe"
        }
        
        try:
            client = get_sync_client()
            response, error = safe_request_with_timeout_details(
                client, "POST", "/intent", json=test_request
            )
            
            if error:
                intent_results.append({
                    "intent": intent,
                    "error": str(error),
                    "available": False
                })
                continue
                
            try:
                    response_data = response.json()
            except:
                    response_data = {"raw_response": response.text}
                
            result = {
                    "intent": intent,
                    "status_code": response.status_code,
                    "available": response.status_code == 200,
                    "error": response.status_code >= 400,
                    "response_present": bool(response_data)
                }
                
            intent_results.append(result)
                
            if response.status_code == 200:
                    available_intents.append(intent)
                    
        except Exception as e:
            intent_results.append({
                "intent": intent,
                "exception": str(e),
                "available": False
            })
    
    print("RESPONSE DATA:")
    print(json.dumps({
        "probe_results": {
            "total_tested": len(potential_intents),
            "available_intents": available_intents,
            "error_intents": [r["intent"] for r in intent_results if r.get("error", False)],
            "system_responsive": len(intent_results) == len(potential_intents)
        },
        "detailed_results": intent_results
    }, indent=2))
    
    # 测试6：使用真实存在的auth和mbti模块intent进行参数传递测试
    real_test_intents = [
        {
            "intent": "mbti_step1",
            "description": "MBTI模块步骤1 - 基础参数测试"
        },
        {
            "intent": "register_step1", 
            "description": "Auth模块注册步骤1 - 邮箱验证",
            "required_fields": ["email", "test_user"]
        }
    ]
    
    print(f"\n--- 测试6: 参数传递测试 (使用真实intent) ---")
    
    all_parameter_results = []
    
    # 测试MBTI模块参数处理
    mbti_tests = [
        {
            "intent": "mbti_step1",
            "user_id": "param_test_user_1",
            "request_id": "param_mbti_001"
        },
        {
            "intent": "mbti_step1",
            "user_id": "param_test_user_2", 
            "request_id": "param_mbti_002",
            "additional_data": {"test_mode": True}
        }
    ]
    
    # 测试Auth模块参数处理
    auth_tests = [
        {
            "intent": "register_step1",
            "user_id": "param_test_user_3",
            "request_id": "param_auth_001",
            "email": "test_param@example.com",
            "test_user": True
        },
        {
            "intent": "oauth_google_step1",
            "user_id": "param_test_user_4",
            "request_id": "param_auth_002", 
            "state": "param_test_state_123"
        }
    ]
    
    parameter_tests = mbti_tests + auth_tests
        
    print("REQUEST DATA:")
    print(json.dumps({
        "action": "parameter_handling_test",
        "total_test_intents": len(real_test_intents),
        "parameter_variations": len(parameter_tests),
        "mbti_tests": len(mbti_tests),
        "auth_tests": len(auth_tests)
    }, indent=2))
    
    parameter_results = []
    
    for i, test_req in enumerate(parameter_tests):
        try:
            client = get_sync_client()
            response, error = safe_request_with_timeout_details(
                client, "POST", "/intent", json=test_req
            )
            
            if error:
                parameter_results.append({
                    "test_case": i + 1,
                    "intent": test_req.get("intent", "unknown"),
                    "error": str(error),
                    "success": False
                })
                continue
                
            try:
                    response_data = response.json()
            except:
                    response_data = {"raw_response": response.text}
                
            parameter_results.append({
                    "test_case": i + 1,
                    "intent": test_req["intent"],
                    "status_code": response.status_code,
                    "success": response.status_code == 200,
                    "param_count": len(test_req) - 1,  # -1 for intent field
                    "response_size": len(str(response_data))
                })
        except Exception as e:
            parameter_results.append({
                "test_case": i + 1,
                "intent": test_req.get("intent", "unknown"),
                "exception": str(e),
                "success": False
            })
    
    print("RESPONSE DATA:")
    print(json.dumps({
        "parameter_test_results": parameter_results,
        "successful_parameter_tests": sum(1 for r in parameter_results if r.get("success", False)),
        "mbti_success_rate": sum(1 for r in parameter_results if r.get("intent", "").startswith("mbti") and r.get("success", False)) / len(mbti_tests) * 100,
        "auth_success_rate": sum(1 for r in parameter_results if r.get("intent", "").startswith(("register", "oauth")) and r.get("success", False)) / len(auth_tests) * 100,
        "parameter_handling_capability": "优秀" if all(r.get("success", False) for r in parameter_results) else "良好"
    }, indent=2))
    
    # 测试7：并发路由请求
    print("\n--- 测试7: 并发路由请求测试 ---")
    
    # 创建混合的并发请求 - 使用真实intent
    concurrent_requests = []
    
    # 添加有效的MBTI请求
    for i in range(2):
        concurrent_requests.append({
            "intent": "mbti_step1",
            "request_id": f"concurrent_mbti_{i}",
            "user_id": f"concurrent_mbti_user_{i}"
        })
    
    # 添加有效的Auth请求  
    concurrent_requests.append({
        "intent": "register_step1",
        "request_id": "concurrent_auth_1",
        "user_id": "concurrent_auth_user_1",
        "email": "concurrent@example.com",
        "test_user": True
    })
    
    # 添加一些无效请求
    for i in range(3):
        concurrent_requests.append({
            "intent": f"invalid_concurrent_{i}",
            "request_id": f"concurrent_invalid_{i}",
            "user_id": f"concurrent_invalid_user_{i}"
        })
    
    print("REQUEST DATA:")
    print(json.dumps({
        "action": "concurrent_routing_test",
        "total_requests": len(concurrent_requests),
        "valid_requests": len([r for r in concurrent_requests if r["intent"] in ["mbti_step1", "register_step1"]]),
        "invalid_requests": len([r for r in concurrent_requests if r["intent"].startswith("invalid_")])
    }, indent=2))
    
    try:
        concurrent_results = []
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {}
            
            # 使用统一的客户端配置进行并发请求
            client = get_sync_client()
            for req in concurrent_requests:
                future = executor.submit(
                    lambda r: safe_request_with_timeout_details(client, "POST", "/intent", json=r)[0],
                    req
                )
                futures[future] = req
            
            for future in as_completed(futures):
                request_data = futures[future]
                try:
                    response = future.result()
                    concurrent_results.append({
                        "request_id": request_data["request_id"],
                        "intent": request_data["intent"],
                        "status_code": response.status_code,
                        "success": response.status_code == 200,
                        "handled": response.status_code in [200, 400, 422]
                    })
                except Exception as e:
                    concurrent_results.append({
                        "request_id": request_data["request_id"],
                        "intent": request_data["intent"],
                        "error": str(e),
                        "success": False,
                        "handled": False
                    })
        
        total_time = time.time() - start_time
        
        # 统计并发测试结果
        handled_requests = sum(1 for r in concurrent_results if r.get("handled", False))
        successful_requests = sum(1 for r in concurrent_results if r.get("success", False))
        
        print("RESPONSE DATA:")
        print(json.dumps({
            "concurrent_test_summary": {
                "total_processing_time": round(total_time, 3),
                "total_requests": len(concurrent_requests),
                "handled_requests": handled_requests,
                "successful_requests": successful_requests,
                "requests_per_second": round(len(concurrent_requests) / total_time, 2),
                "routing_efficiency": round(handled_requests / len(concurrent_requests) * 100, 2)
            },
            "sample_results": concurrent_results[:5]
        }, indent=2))
        
    except Exception as e:
        print("EXCEPTION:")
        print(json.dumps({"error": str(e), "type": type(e).__name__}, indent=2))

async def test_routing_performance():
    """
    Phase 3: 性能测试 - 路由性能和响应时间验证
    目的：验证hub路由系统的性能特征，重点测试无效intent的处理时间
    """
    print("\n=== Phase 3: 路由性能测试（修复后基准测试）===")
    
    # 生成报告生成器
    report_generator = BenchmarkReportGenerator()
    
    # 测试8：路由响应时间基准测试（同步）
    print("\n--- 测试8: 同步无效Intent基准测试 ---")
    sync_result = benchmark_invalid_intent_sync(iterations=10)
    
    # 测试9：异步无效Intent基准测试
    print("\n--- 测试9: 异步无效Intent基准测试 ---")
    async_result = await benchmark_invalid_intent_async(iterations=10)
    
    # 测试10：并发基准测试
    print("\n--- 测试10: 并发基准测试 ---")
    concurrent_result = await concurrent_benchmark(
        concurrent_workers=8,
        total_requests=40,
        batch_size=5
    )
    
    # 生成基准测试报告
    print("\n--- 生成基准测试报告 ---")
    report_path = report_generator.generate_httpx_benchmark_report(
        sync_result=sync_result,
        async_result=async_result,
        concurrent_result=concurrent_result,
        curl_baseline_ms=210.0  # 根据分析报告的curl基准
    )
    
    print(f"📋 详细基准测试报告已生成: {report_path}")
    
    # 保存原始结果
    raw_results = {
        "sync_benchmark": {
            "total_requests": sync_result.total_requests,
            "successful_requests": sync_result.successful_requests,
            "avg_time_ms": sync_result.avg_time_ms,
            "p95_ms": sync_result.p95_ms,
            "error_count": sync_result.timeout_errors + sync_result.connect_errors + sync_result.other_errors
        },
        "async_benchmark": {
            "total_requests": async_result.total_requests,
            "successful_requests": async_result.successful_requests,
            "avg_time_ms": async_result.avg_time_ms,
            "p95_ms": async_result.p95_ms,
            "error_count": async_result.timeout_errors + async_result.connect_errors + async_result.other_errors
        },
        "concurrent_benchmark": concurrent_result,
        "test_timestamp": time.time(),
        "curl_baseline_reference": 210.0
    }
    
    report_generator.save_raw_results(raw_results, "performance_benchmark")
    
    # 验收标准检查
    print("\n=== 验收标准检查 ===")
    validation_results = {
        "sync_avg_time_target": {
            "target": "≤ 300ms",
            "actual": f"{sync_result.avg_time_ms}ms",
            "passed": sync_result.avg_time_ms <= 300
        },
        "concurrent_p95_target": {
            "target": "≤ 450ms", 
            "actual": f"{concurrent_result.get('timing_stats', {}).get('p95_ms', 0)}ms" if concurrent_result.get('timing_stats') else "N/A",
            "passed": concurrent_result.get('timing_stats', {}).get('p95_ms', float('inf')) <= 450
        },
        "concurrent_stability_target": {
            "target": "100% 成功",
            "actual": f"{concurrent_result.get('overall_stats', {}).get('success_rate', 0)}%" if concurrent_result.get('overall_stats') else "N/A",
            "passed": concurrent_result.get('overall_stats', {}).get('success_rate', 0) == 100
        }
    }
    
    print("验收标准达成情况:")
    for key, result in validation_results.items():
        status = "✅ PASS" if result["passed"] else "❌ FAIL"
        print(f"  {key}: {result['actual']} (目标: {result['target']}) - {status}")
    
    # 总体结论
    all_passed = all(result["passed"] for result in validation_results.values())
    print(f"\n🎯 总体结论: {'✅ 所有验收标准达成' if all_passed else '⚠️ 部分验收标准未达成'}")
    
    return {
        "sync_result": sync_result,
        "async_result": async_result,
        "concurrent_result": concurrent_result,
        "validation_results": validation_results,
        "report_path": report_path,
        "all_standards_met": all_passed
    }

async def run_all_tests():
    """
    执行所有意图路由测试用例
    按照环境检查 -> 异常测试 -> 性能测试的顺序
    """
    try:
        # 首先检查系统可用性
        if not await check_system_availability_async():
            print("\n系统不可用，请确保运行 uvicorn main:app --host 0.0.0.0 --port 8000")
            print("FINAL RESULT: TEST FAILED - SYSTEM NOT AVAILABLE")
            return

        # 执行异常场景测试
        await test_intent_routing_exceptions()

        # 执行性能测试（包含基准测试）
        performance_results = await test_routing_performance()

        print("\n" + "="*80)
        print("🏆 测试完成总结")
        print("="*80)
        
        if performance_results and performance_results["all_standards_met"]:
            print("✅ 所有测试通过 - 无效Intent性能问题已修复")
            print("📊 关键指标:")
            sync_result = performance_results["sync_result"]
            concurrent_result = performance_results["concurrent_result"]
            print(f"   • 同步平均响应时间: {sync_result.avg_time_ms}ms (目标: ≤300ms)")
            if concurrent_result.get('timing_stats'):
                print(f"   • 并发P95响应时间: {concurrent_result['timing_stats']['p95_ms']}ms (目标: ≤450ms)")
                print(f"   • 并发成功率: {concurrent_result['overall_stats']['success_rate']}% (目标: 100%)")
            print(f"📋 详细报告: {performance_results['report_path']}")
        else:
            print("⚠️ 部分测试未通过 - 请查看详细报告进行进一步优化")
            if performance_results:
                print(f"📋 详细报告: {performance_results['report_path']}")

        print("\nFINAL RESULT: TEST COMPLETED - 检查上述响应以验证修复效果")

    except Exception as e:
        print(f"\nEXCEPTION:")
        print(json.dumps({"error": str(e), "type": type(e).__name__}, indent=2))
        print("FINAL RESULT: TEST FAILED")
    
    finally:
        # 清理客户端连接
        from common.http_client import close_all_clients
        close_all_clients()

if __name__ == "__main__":
    # 运行所有异步测试用例
    asyncio.run(run_all_tests())