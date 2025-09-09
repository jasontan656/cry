#!/usr/bin/env python3
# test_hub_module_registration.py - Hub模块注册功能全面异步测试脚本
# 测试目标：通过异步HTTP请求验证hub模块注册机制和系统状态检查功能

import json
import time
import asyncio
import httpx
from async_utils import (
    get_async_client, async_http_request, async_concurrent_requests,
    format_test_output, format_performance_stats, format_test_summary,
    check_system_availability_async, BASE_URL
)

# 使用async_utils中的异步检查函数

async def test_module_registration_endpoints():
    """
    Phase 1: 模块注册端点测试 - 验证模块注册相关端点的可用性
    目的：验证系统是否提供模块注册和状态查询的HTTP端点
    """
    print("\n=== Phase 1: 模块注册端点测试 ===")
    
    # 测试1：探测可能的模块注册端点
    print("\n--- 测试1: 探测模块注册相关端点 ---")
    
    # 常见的可能存在的模块相关端点
    potential_endpoints = [
        "/modules",
        "/register",
        "/registration",
        "/module/register", 
        "/hub/modules",
        "/hub/register",
        "/system/modules",
        "/api/modules",
        "/status",
        "/health",
        "/info"
    ]
    
    print("REQUEST DATA:")
    print(json.dumps({
        "action": "probe_module_endpoints",
        "endpoints_to_test": potential_endpoints
    }, indent=2))
    
    endpoint_results = []
    
    for endpoint in potential_endpoints:
        try:
            with httpx.Client() as client:
                # 尝试GET请求
                get_response = client.get(f"{BASE_URL}{endpoint}")
                
                try:
                    get_data = get_response.json()
                except:
                    get_data = {"raw_response": get_response.text[:100]}
                
                result = {
                    "endpoint": endpoint,
                    "method": "GET",
                    "status_code": get_response.status_code,
                    "available": get_response.status_code in [200, 405],  # 405表示方法不允许，但端点存在
                    "response_size": len(get_response.text)
                }
                
                endpoint_results.append(result)
                
                # 如果GET返回405，尝试POST
                if get_response.status_code == 405:
                    try:
                        post_response = client.post(f"{BASE_URL}{endpoint}", json={})
                        endpoint_results.append({
                            "endpoint": endpoint,
                            "method": "POST",
                            "status_code": post_response.status_code,
                            "available": post_response.status_code != 404,
                            "response_size": len(post_response.text)
                        })
                    except:
                        pass
                        
        except Exception as e:
            endpoint_results.append({
                "endpoint": endpoint,
                "method": "GET",
                "error": str(e),
                "available": False
            })
    
    # 筛选可用的端点
    available_endpoints = [r for r in endpoint_results if r.get("available", False)]
    
    print("RESPONSE DATA:")
    print(json.dumps({
        "endpoint_discovery": {
            "total_tested": len(potential_endpoints),
            "available_endpoints": len(available_endpoints),
            "discovered_endpoints": [r["endpoint"] for r in available_endpoints]
        },
        "detailed_results": endpoint_results
    }, indent=2))
    
    return available_endpoints

async def test_module_registration_exceptions():
    """
    Phase 2: 模块注册异常测试 - 验证模块注册的异常处理
    目的：验证无效模块信息、错误请求等异常输入的处理
    """
    print("\n=== Phase 2: 模块注册异常场景测试 ===")
    
    # 测试2：尝试向可能的注册端点发送无效数据
    print("\n--- 测试2: 无效模块注册数据测试 ---")
    
    # 可能的注册端点
    registration_endpoints = ["/register", "/modules", "/module/register"]
    
    # 各种无效的注册请求
    invalid_registration_requests = [
        {},  # 空对象
        {"name": ""},  # 空名称
        {"invalid_field": "test"},  # 无效字段
        {"name": "test_module"},  # 缺失其他必要字段
        {"name": "test", "version": ""},  # 空版本
    ]
    
    print("REQUEST DATA:")
    print(json.dumps({
        "action": "test_invalid_module_registration",
        "registration_endpoints": registration_endpoints,
        "invalid_requests_count": len(invalid_registration_requests)
    }, indent=2))
    
    registration_results = []
    
    for endpoint in registration_endpoints:
        for i, invalid_req in enumerate(invalid_registration_requests):
            try:
                with httpx.Client() as client:
                    response = client.post(f"{BASE_URL}{endpoint}", json=invalid_req)
                    
                    try:
                        response_data = response.json()
                    except:
                        response_data = {"raw_response": response.text[:200]}
                    
                    registration_results.append({
                        "endpoint": endpoint,
                        "test_case": i + 1,
                        "request": invalid_req,
                        "status_code": response.status_code,
                        "endpoint_exists": response.status_code != 404,
                        "validation_error": response.status_code in [400, 422],
                        "server_stable": response.status_code != 500
                    })
                    
            except Exception as e:
                registration_results.append({
                    "endpoint": endpoint,
                    "test_case": i + 1,
                    "request": invalid_req,
                    "error": str(e),
                    "endpoint_exists": False
                })
    
    # 分析结果
    existing_endpoints = [r for r in registration_results if r.get("endpoint_exists", False)]
    validated_requests = [r for r in registration_results if r.get("validation_error", False)]
    
    print("RESPONSE DATA:")
    print(json.dumps({
        "registration_test_summary": {
            "total_tests": len(registration_results),
            "existing_endpoints": len(set(r["endpoint"] for r in existing_endpoints)),
            "validation_responses": len(validated_requests),
            "system_stability": sum(1 for r in registration_results if r.get("server_stable", True))
        },
        "sample_results": registration_results[:5]
    }, indent=2))

async def test_system_status_and_health():
    """
    Phase 3: 系统状态和健康检查测试 - 验证系统状态检查功能
    目的：验证系统能够提供状态信息和健康检查
    """
    print("\n=== Phase 3: 系统状态和健康检查测试 ===")
    
    # 测试3：系统状态端点测试
    print("\n--- 测试3: 系统状态端点测试 ---")
    
    status_endpoints = ["/status", "/health", "/info", "/system", "/system/status"]
    
    print("REQUEST DATA:")
    print(json.dumps({
        "action": "test_system_status_endpoints",
        "endpoints_to_test": status_endpoints
    }, indent=2))
    
    status_results = []
    
    for endpoint in status_endpoints:
        try:
            with httpx.Client() as client:
                response = client.get(f"{BASE_URL}{endpoint}")
                
                try:
                    response_data = response.json()
                    data_type = "json"
                except:
                    response_data = response.text[:300] if response.text else ""
                    data_type = "text"
                
                status_results.append({
                    "endpoint": endpoint,
                    "status_code": response.status_code,
                    "available": response.status_code == 200,
                    "data_type": data_type,
                    "data_size": len(str(response_data)),
                    "has_system_info": "system" in str(response_data).lower() or 
                                     "status" in str(response_data).lower() or
                                     "health" in str(response_data).lower(),
                    "sample_data": response_data if len(str(response_data)) < 200 else str(response_data)[:200] + "..."
                })
                
        except Exception as e:
            status_results.append({
                "endpoint": endpoint,
                "error": str(e),
                "available": False
            })
    
    # 筛选可用的状态端点
    available_status_endpoints = [r for r in status_results if r.get("available", False)]
    
    print("RESPONSE DATA:")
    print(json.dumps({
        "status_endpoint_summary": {
            "total_tested": len(status_endpoints),
            "available_endpoints": len(available_status_endpoints),
            "endpoints_with_system_info": len([r for r in available_status_endpoints if r.get("has_system_info", False)])
        },
        "detailed_results": status_results
    }, indent=2))
    
    # 测试4：系统完整性验证（如果有可用的状态端点）
    if available_status_endpoints:
        print("\n--- 测试4: 系统完整性状态验证 ---")
        
        best_endpoint = available_status_endpoints[0]["endpoint"]
        
        print("REQUEST DATA:")
        print(json.dumps({
            "action": "system_integrity_check",
            "selected_endpoint": best_endpoint
        }, indent=2))
        
        try:
            with httpx.Client() as client:
                response = client.get(f"{BASE_URL}{best_endpoint}")
                
                try:
                    system_data = response.json()
                    
                    # 分析系统数据结构
                    integrity_analysis = {
                        "response_structure": "json",
                        "top_level_keys": list(system_data.keys()) if isinstance(system_data, dict) else [],
                        "data_completeness": len(str(system_data)),
                        "contains_version_info": any(key in str(system_data).lower() for key in ["version", "build", "release"]),
                        "contains_module_info": any(key in str(system_data).lower() for key in ["module", "component", "service"]),
                        "contains_status_info": any(key in str(system_data).lower() for key in ["status", "state", "health"])
                    }
                    
                except:
                    system_data = response.text
                    integrity_analysis = {
                        "response_structure": "text",
                        "data_completeness": len(system_data),
                        "contains_system_keywords": any(keyword in system_data.lower() for keyword in 
                                                       ["system", "status", "health", "running", "module"])
                    }
                
                print("RESPONSE DATA:")
                print(json.dumps({
                    "system_integrity_analysis": integrity_analysis,
                    "endpoint_used": best_endpoint,
                    "response_successful": response.status_code == 200,
                    "sample_system_data": str(system_data)[:300] + "..." if len(str(system_data)) > 300 else str(system_data)
                }, indent=2))
                
        except Exception as e:
            print("EXCEPTION:")
            print(json.dumps({"error": str(e), "type": type(e).__name__}, indent=2))
    else:
        print("\n--- 测试4: 系统完整性状态验证 ---")
        print("RESPONSE DATA:")
        print(json.dumps({
            "system_integrity_check": "跳过 - 未找到可用的系统状态端点"
        }, indent=2))

async def test_module_functionality_verification():
    """
    Phase 4: 模块功能验证测试 - 通过现有功能验证模块系统的工作状态
    目的：通过测试现有的intent处理来验证模块注册系统的有效性
    """
    print("\n=== Phase 4: 模块功能验证测试 ===")
    
    # 测试5：通过intent测试验证模块系统状态
    print("\n--- 测试5: 通过功能测试验证模块系统 ---")
    
    # 尝试各种intent来测试模块系统的响应性
    test_intents = [
        "test",
        "hello", 
        "ping",
        "echo",
        "status"
    ]
    
    print("REQUEST DATA:")
    print(json.dumps({
        "action": "module_system_functionality_test",
        "test_intents": test_intents,
        "purpose": "验证模块注册系统通过intent处理的工作状态"
    }, indent=2))
    
    functionality_results = []
    
    for intent in test_intents:
        test_request = {
            "intent": intent,
            "request_id": f"module_test_{intent}",
            "user_id": "module_system_test_user"
        }
        
        try:
            start_time = time.time()
            with httpx.Client() as client:
                response = client.post(f"{BASE_URL}/intent", json=test_request)
            processing_time = time.time() - start_time
            
            try:
                response_data = response.json()
            except:
                response_data = {"raw_response": response.text}
            
            functionality_results.append({
                "intent": intent,
                "status_code": response.status_code,
                "processing_time": round(processing_time, 4),
                "module_processed": response.status_code == 200,
                "system_responsive": response.status_code in [200, 400, 422],
                "response_indicates_module_system": any(keyword in str(response_data).lower() 
                                                       for keyword in ["module", "step", "flow", "handler"])
            })
            
        except Exception as e:
            functionality_results.append({
                "intent": intent,
                "error": str(e),
                "module_processed": False,
                "system_responsive": False
            })
    
    # 分析模块系统功能状态
    responsive_tests = [r for r in functionality_results if r.get("system_responsive", False)]
    successful_processes = [r for r in functionality_results if r.get("module_processed", False)]
    module_system_indicators = [r for r in functionality_results if r.get("response_indicates_module_system", False)]
    
    print("RESPONSE DATA:")
    print(json.dumps({
        "module_system_analysis": {
            "total_tests": len(test_intents),
            "system_responsive_tests": len(responsive_tests),
            "successful_module_processes": len(successful_processes),
            "module_system_indicators": len(module_system_indicators),
            "system_responsiveness_rate": round(len(responsive_tests) / len(test_intents) * 100, 2),
            "module_processing_capability": "有效" if len(successful_processes) > 0 else "基本" if len(responsive_tests) > 0 else "需要检查",
            "average_processing_time": round(
                sum(r.get("processing_time", 0) for r in functionality_results if "processing_time" in r) / 
                len([r for r in functionality_results if "processing_time" in r]), 4
            ) if any("processing_time" in r for r in functionality_results) else 0
        },
        "detailed_results": functionality_results
    }, indent=2))
    
    # 测试6：模块系统压力测试
    print("\n--- 测试6: 模块系统压力测试 ---")
    
    if successful_processes:
        # 使用找到的有效intent进行压力测试
        working_intent = successful_processes[0]["intent"]
        
        print("REQUEST DATA:")
        print(json.dumps({
            "action": "module_system_stress_test",
            "test_intent": working_intent,
            "concurrent_requests": 5,
            "total_requests": 15
        }, indent=2))
        
        try:
            import concurrent.futures
            
            stress_requests = []
            for i in range(15):
                stress_requests.append({
                    "intent": working_intent,
                    "request_id": f"stress_test_{i}",
                    "user_id": f"stress_user_{i}",
                    "timestamp": time.time()
                })
            
            stress_results = []
            start_time = time.time()
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = {}
                
                for req in stress_requests:
                    future = executor.submit(
                        lambda r: httpx.post(f"{BASE_URL}/intent", json=r),
                        req
                    )
                    futures[future] = req
                
                for future in concurrent.futures.as_completed(futures):
                    request_data = futures[future]
                    try:
                        response = future.result()
                        stress_results.append({
                            "request_id": request_data["request_id"],
                            "processing_time": time.time() - request_data["timestamp"],
                            "status_code": response.status_code,
                            "success": response.status_code == 200,
                            "system_stable": response.status_code != 500
                        })
                    except Exception as e:
                        stress_results.append({
                            "request_id": request_data["request_id"],
                            "error": str(e),
                            "success": False,
                            "system_stable": False
                        })
            
            total_stress_time = time.time() - start_time
            
            # 分析压力测试结果
            successful_stress = sum(1 for r in stress_results if r.get("success", False))
            stable_responses = sum(1 for r in stress_results if r.get("system_stable", False))
            avg_stress_time = sum(r.get("processing_time", 0) for r in stress_results if "processing_time" in r) / len(stress_results)
            
            print("RESPONSE DATA:")
            print(json.dumps({
                "stress_test_results": {
                    "total_requests": len(stress_requests),
                    "successful_requests": successful_stress,
                    "stable_responses": stable_responses,
                    "total_test_time": round(total_stress_time, 3),
                    "average_request_time": round(avg_stress_time, 4),
                    "requests_per_second": round(len(stress_requests) / total_stress_time, 2),
                    "success_rate": round(successful_stress / len(stress_requests) * 100, 2),
                    "system_stability_under_load": "优秀" if stable_responses == len(stress_requests) else "良好" if stable_responses > len(stress_requests) * 0.8 else "需要改进"
                },
                "sample_results": stress_results[:3]
            }, indent=2))
            
        except Exception as e:
            print("EXCEPTION:")
            print(json.dumps({"error": str(e), "type": type(e).__name__}, indent=2))
    else:
        print("RESPONSE DATA:")
        print(json.dumps({
            "stress_test": "跳过 - 未找到可用的成功处理intent进行压力测试"
        }, indent=2))

async def run_all_tests():
    """
    执行所有模块注册测试用例
    按照环境检查 -> 端点探测 -> 异常测试 -> 状态测试 -> 功能验证的顺序
    """
    try:
        # 首先检查系统可用性
        if not await check_system_availability_async():
            print("\n系统不可用，请确保运行 uvicorn main:app --host 0.0.0.0 --port 8000")
            print("FINAL RESULT: TEST FAILED - SYSTEM NOT AVAILABLE")
            return

        # 探测模块注册端点
        available_endpoints = await test_module_registration_endpoints()

        # 执行异常场景测试
        await test_module_registration_exceptions()

        # 执行系统状态测试
        await test_system_status_and_health()

        # 执行功能验证测试
        await test_module_functionality_verification()

        print("\nFINAL RESULT: TEST COMPLETED - 检查上述响应以验证模块注册系统状态")

    except Exception as e:
        print(f"\nEXCEPTION:")
        print(json.dumps({"error": str(e), "type": type(e).__name__}, indent=2))
        print("FINAL RESULT: TEST FAILED")

if __name__ == "__main__":
    # 运行所有异步测试用例
    asyncio.run(run_all_tests())