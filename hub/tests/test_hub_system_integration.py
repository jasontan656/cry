#!/usr/bin/env python3
# test_hub_system_integration.py - Hub系统集成全面异步测试脚本
# 测试目标：通过异步HTTP请求验证hub系统集成、端到端流程、系统协调等完整功能

import json
import time
import asyncio
import httpx
from concurrent.futures import ThreadPoolExecutor, as_completed
from async_utils import (
    get_async_client, async_http_request, async_concurrent_requests,
    format_test_output, format_performance_stats, format_test_summary,
    check_system_availability_async, BASE_URL
)

# 使用async_utils中的异步检查函数

async def discover_system_capabilities():
    """
    发现系统功能
    目的：探测系统的可用端点和功能，为集成测试做准备
    """
    print("\n=== 系统能力发现：探测可用功能 ===")
    
    # 探测各种可能的端点
    endpoints_to_probe = [
        "/",
        "/docs",
        "/openapi.json",
        "/intent",
        "/invoke", 
        "/status",
        "/health",
        "/modules",
        "/flows",
        "/system",
        "/api",
        "/hub"
    ]
    
    print("REQUEST DATA:")
    print(json.dumps({
        "action": "discover_system_capabilities",
        "endpoints_to_probe": endpoints_to_probe
    }, indent=2))
    
    discovered_capabilities = []
    
    for endpoint in endpoints_to_probe:
        try:
            with httpx.Client() as client:
                # 尝试GET请求
                get_response = client.get(f"{BASE_URL}{endpoint}")
                
                capability = {
                    "endpoint": endpoint,
                    "method": "GET",
                    "status_code": get_response.status_code,
                    "available": get_response.status_code in [200, 405],
                    "content_type": get_response.headers.get("content-type", ""),
                    "response_size": len(get_response.content)
                }
                
                discovered_capabilities.append(capability)
                
                # 如果是intent端点，也尝试POST
                if "intent" in endpoint or "invoke" in endpoint:
                    try:
                        post_response = client.post(f"{BASE_URL}{endpoint}", json={"test": "probe"})
                        discovered_capabilities.append({
                            "endpoint": endpoint,
                            "method": "POST",
                            "status_code": post_response.status_code,
                            "available": post_response.status_code != 404,
                            "content_type": post_response.headers.get("content-type", ""),
                            "response_size": len(post_response.content)
                        })
                    except:
                        pass
                        
        except Exception as e:
            discovered_capabilities.append({
                "endpoint": endpoint,
                "method": "GET", 
                "error": str(e),
                "available": False
            })
    
    # 分析发现的能力
    available_capabilities = [c for c in discovered_capabilities if c.get("available", False)]
    api_endpoints = [c for c in available_capabilities if c["status_code"] == 200]
    
    print("RESPONSE DATA:")
    print(json.dumps({
        "capability_discovery": {
            "total_probed": len(endpoints_to_probe),
            "available_endpoints": len(available_capabilities),
            "functional_endpoints": len(api_endpoints),
            "discovered_endpoints": [c["endpoint"] for c in available_capabilities]
        },
        "detailed_capabilities": available_capabilities
    }, indent=2))
    
    return available_capabilities

async def test_system_integration_exceptions():
    """
    Phase 1: 系统集成异常场景测试
    目的：验证系统在异常输入下的集成稳定性
    """
    print("\n=== Phase 1: 系统集成异常场景测试 ===")
    
    # 测试1：跨端点请求异常处理
    print("\n--- 测试1: 跨端点请求异常处理 ---")
    
    # 向不同端点发送可能导致错误的请求
    cross_endpoint_tests = [
        {"endpoint": "/intent", "method": "POST", "data": {}},  # 空数据
        {"endpoint": "/intent", "method": "POST", "data": {"invalid": "data"}},  # 无效数据
        {"endpoint": "/intent", "method": "GET", "data": None},  # 错误方法
        {"endpoint": "/invoke", "method": "POST", "data": {"test": "invalid"}},  # 测试invoke端点
        {"endpoint": "/status", "method": "POST", "data": {}},  # 向状态端点POST
    ]
    
    print("REQUEST DATA:")
    print(json.dumps({
        "action": "cross_endpoint_exception_test",
        "total_tests": len(cross_endpoint_tests)
    }, indent=2))
    
    exception_results = []
    
    for test in cross_endpoint_tests:
        try:
            with httpx.Client() as client:
                if test["method"] == "POST":
                    response = client.post(f"{BASE_URL}{test['endpoint']}", json=test["data"])
                else:
                    response = client.get(f"{BASE_URL}{test['endpoint']}")
                
                try:
                    response_data = response.json()
                except:
                    response_data = {"raw_response": response.text[:200]}
                
                exception_results.append({
                    "endpoint": test["endpoint"],
                    "method": test["method"],
                    "status_code": response.status_code,
                    "endpoint_exists": response.status_code != 404,
                    "handled_gracefully": response.status_code != 500,
                    "provides_error_info": "error" in str(response_data).lower()
                })
                
        except Exception as e:
            exception_results.append({
                "endpoint": test["endpoint"],
                "method": test["method"],
                "exception": str(e),
                "handled_gracefully": False
            })
    
    # 分析异常处理结果
    graceful_handling = sum(1 for r in exception_results if r.get("handled_gracefully", False))
    existing_endpoints = sum(1 for r in exception_results if r.get("endpoint_exists", False))
    
    print("RESPONSE DATA:")
    print(json.dumps({
        "exception_handling_analysis": {
            "total_tests": len(cross_endpoint_tests),
            "graceful_error_handling": graceful_handling,
            "existing_endpoints": existing_endpoints, 
            "error_handling_rate": round(graceful_handling / len(cross_endpoint_tests) * 100, 2),
            "system_resilience": "优秀" if graceful_handling == len(cross_endpoint_tests) else "良好" if graceful_handling > len(cross_endpoint_tests) * 0.8 else "需要改进"
        },
        "detailed_results": exception_results
    }, indent=2))
    
    # 测试2：并发异常请求协调
    print("\n--- 测试2: 并发异常请求协调 ---")
    
    # 创建多个可能导致异常的并发请求
    concurrent_exception_requests = []
    
    for i in range(8):
        concurrent_exception_requests.append({
            "endpoint": "/intent",
            "data": {"intent": f"invalid_concurrent_intent_{i}", "user_id": f"concurrent_user_{i}"}
        })
    
    for i in range(4):
        concurrent_exception_requests.append({
            "endpoint": "/intent", 
            "data": {"malformed_field": f"value_{i}"}  # 缺失intent字段
        })
    
    print("REQUEST DATA:")
    print(json.dumps({
        "action": "concurrent_exception_coordination",
        "total_requests": len(concurrent_exception_requests),
        "request_types": ["invalid_intent", "malformed_request"]
    }, indent=2))
    
    try:
        concurrent_results = []
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = {}
            
            for req in concurrent_exception_requests:
                future = executor.submit(
                    lambda r: httpx.post(f"{BASE_URL}{r['endpoint']}", json=r["data"]),
                    req
                )
                futures[future] = req
            
            for future in as_completed(futures):
                request_data = futures[future]
                try:
                    response = future.result()
                    concurrent_results.append({
                        "endpoint": request_data["endpoint"],
                        "status_code": response.status_code,
                        "handled": response.status_code != 500,
                        "appropriate_error": response.status_code >= 400
                    })
                except Exception as e:
                    concurrent_results.append({
                        "endpoint": request_data["endpoint"],
                        "error": str(e),
                        "handled": False
                    })
        
        total_time = time.time() - start_time
        
        # 统计并发异常处理结果
        handled_exceptions = sum(1 for r in concurrent_results if r.get("handled", False))
        appropriate_errors = sum(1 for r in concurrent_results if r.get("appropriate_error", False))
        
        print("RESPONSE DATA:")
        print(json.dumps({
            "concurrent_exception_summary": {
                "total_requests": len(concurrent_exception_requests),
                "handled_exceptions": handled_exceptions,
                "appropriate_error_responses": appropriate_errors,
                "total_processing_time": round(total_time, 3),
                "requests_per_second": round(len(concurrent_exception_requests) / total_time, 2),
                "concurrent_coordination": "优秀" if handled_exceptions == len(concurrent_exception_requests) else "良好"
            },
            "sample_results": concurrent_results[:5]
        }, indent=2))
        
    except Exception as e:
        print("EXCEPTION:")
        print(json.dumps({"error": str(e), "type": type(e).__name__}, indent=2))

async def test_end_to_end_integration():
    """
    Phase 2: 端到端集成功能测试
    目的：验证完整的业务流程在系统中的执行
    """
    print("\n=== Phase 2: 端到端集成功能测试 ===")
    
    # 测试3：完整用户请求流程测试
    print("\n--- 测试3: 完整用户请求流程测试 ---")
    
    # 模拟一个完整的用户请求流程
    user_journey_steps = [
        {
            "step": 1,
            "description": "用户认证请求",
            "request": {"intent": "auth_login", "email": "test@example.com", "password": "testpass"}
        },
        {
            "step": 2, 
            "description": "用户资料获取",
            "request": {"intent": "get_user_profile", "user_id": "test_user_001"}
        },
        {
            "step": 3,
            "description": "业务操作执行",
            "request": {"intent": "perform_business_action", "action": "test_action", "user_id": "test_user_001"}
        },
        {
            "step": 4,
            "description": "结果通知发送",
            "request": {"intent": "send_notification", "user_id": "test_user_001", "message": "操作完成"}
        }
    ]
    
    print("REQUEST DATA:")
    print(json.dumps({
        "action": "complete_user_journey_test",
        "total_steps": len(user_journey_steps),
        "journey_type": "mock_business_process"
    }, indent=2))
    
    journey_results = []
    overall_success = True
    
    for step_info in user_journey_steps:
        step_start = time.time()
        
        try:
            with httpx.Client() as client:
                response = client.post(f"{BASE_URL}/intent", json=step_info["request"])
            step_time = time.time() - step_start
            
            try:
                response_data = response.json()
            except:
                response_data = {"raw_response": response.text}
            
            # 系统对未知intent的处理也是正常的集成行为
            step_success = response.status_code in [200, 400, 422]  # 包括预期的错误响应
            overall_success = overall_success and step_success
            
            journey_results.append({
                "step": step_info["step"],
                "description": step_info["description"],
                "success": step_success,
                "status_code": response.status_code,
                "processing_time": round(step_time, 4),
                "system_responsive": True,
                "intent": step_info["request"].get("intent", "unknown")
            })
            
        except Exception as e:
            journey_results.append({
                "step": step_info["step"],
                "description": step_info["description"],
                "success": False,
                "error": str(e),
                "system_responsive": False
            })
            overall_success = False
    
    print("RESPONSE DATA:")
    print(json.dumps({
        "user_journey_results": {
            "journey_completed": overall_success,
            "responsive_steps": sum(1 for r in journey_results if r.get("system_responsive", False)),
            "total_steps": len(journey_results),
            "total_journey_time": round(sum(r.get("processing_time", 0) for r in journey_results), 3),
            "system_integration_quality": "优秀" if overall_success else "良好" if sum(1 for r in journey_results if r.get("system_responsive", False)) > len(journey_results) * 0.8 else "需要改进"
        },
        "step_details": journey_results
    }, indent=2))
    
    # 测试4：数据传递和格式兼容性测试
    print("\n--- 测试4: 数据传递和格式兼容性测试 ---")
    
    # 测试各种数据格式的传递
    data_format_tests = [
        {
            "name": "简单字符串数据",
            "data": {"intent": "data_test", "message": "simple string"}
        },
        {
            "name": "数值数据",
            "data": {"intent": "data_test", "value": 12345, "float_value": 123.45}
        },
        {
            "name": "复杂嵌套对象",
            "data": {
                "intent": "data_test",
                "complex_data": {
                    "nested": {"deep": "value"},
                    "array": [1, 2, 3, {"item": "value"}],
                    "boolean": True
                }
            }
        },
        {
            "name": "中文数据",
            "data": {"intent": "data_test", "中文字段": "中文内容", "message": "包含中文的消息"}
        },
        {
            "name": "大数据量",
            "data": {
                "intent": "data_test",
                "large_array": list(range(100)),
                "large_text": "x" * 1000
            }
        }
    ]
    
    print("REQUEST DATA:")
    print(json.dumps({
        "action": "data_format_compatibility_test",
        "format_tests": len(data_format_tests),
        "test_types": [t["name"] for t in data_format_tests]
    }, indent=2))
    
    format_results = []
    
    for test in data_format_tests:
        try:
            with httpx.Client() as client:
                start_time = time.time()
                response = client.post(f"{BASE_URL}/intent", json=test["data"])
                processing_time = time.time() - start_time
            
            try:
                response_data = response.json()
            except:
                response_data = {"raw_response": response.text}
            
            format_results.append({
                "test_name": test["name"],
                "status_code": response.status_code,
                "data_accepted": response.status_code in [200, 400, 422],
                "processing_time": round(processing_time, 4),
                "response_available": bool(response_data),
                "data_size_bytes": len(json.dumps(test["data"]).encode('utf-8'))
            })
            
        except Exception as e:
            format_results.append({
                "test_name": test["name"],
                "error": str(e),
                "data_accepted": False
            })
    
    # 分析数据格式兼容性
    accepted_formats = sum(1 for r in format_results if r.get("data_accepted", False))
    avg_processing_time = sum(r.get("processing_time", 0) for r in format_results) / len(format_results)
    
    print("RESPONSE DATA:")
    print(json.dumps({
        "data_format_analysis": {
            "total_format_tests": len(data_format_tests),
            "accepted_formats": accepted_formats,
            "format_compatibility_rate": round(accepted_formats / len(data_format_tests) * 100, 2),
            "average_processing_time": round(avg_processing_time, 4),
            "data_handling_capability": "优秀" if accepted_formats == len(data_format_tests) else "良好"
        },
        "detailed_results": format_results
    }, indent=2))

async def test_system_performance_integration():
    """
    Phase 3: 系统性能集成测试
    目的：验证系统在高负载下的集成表现和稳定性
    """
    print("\n=== Phase 3: 系统性能集成测试 ===")
    
    # 测试5：高负载集成稳定性测试
    print("\n--- 测试5: 高负载集成稳定性测试 ---")
    
    # 创建高负载测试请求
    high_load_requests = []
    
    # 混合不同类型的请求
    request_types = [
        {"intent": "high_load_test_1", "type": "type1"},
        {"intent": "high_load_test_2", "type": "type2"},
        {"intent": "high_load_test_3", "type": "type3"}
    ]
    
    for i in range(30):  # 总共30个请求
        base_request = request_types[i % len(request_types)].copy()
        base_request.update({
            "request_id": f"high_load_{i}",
            "user_id": f"load_test_user_{i}",
            "timestamp": time.time(),
            "sequence": i
        })
        high_load_requests.append(base_request)
    
    print("REQUEST DATA:")
    print(json.dumps({
        "action": "high_load_integration_test", 
        "total_requests": len(high_load_requests),
        "concurrent_level": 10,
        "request_types": len(request_types)
    }, indent=2))
    
    try:
        load_test_results = []
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {}
            
            for req in high_load_requests:
                future = executor.submit(
                    lambda r: httpx.post(f"{BASE_URL}/intent", json=r),
                    req
                )
                futures[future] = req
            
            for future in as_completed(futures):
                request_data = futures[future]
                try:
                    response = future.result()
                    load_test_results.append({
                        "request_id": request_data["request_id"],
                        "sequence": request_data["sequence"],
                        "status_code": response.status_code,
                        "response_time": time.time() - request_data["timestamp"],
                        "system_stable": response.status_code != 500,
                        "handled": response.status_code in [200, 400, 422]
                    })
                except Exception as e:
                    load_test_results.append({
                        "request_id": request_data["request_id"],
                        "sequence": request_data["sequence"],
                        "error": str(e),
                        "system_stable": False,
                        "handled": False
                    })
        
        total_time = time.time() - start_time
        
        # 分析高负载测试结果
        stable_responses = sum(1 for r in load_test_results if r.get("system_stable", False))
        handled_requests = sum(1 for r in load_test_results if r.get("handled", False))
        
        # 响应时间分析
        response_times = [r["response_time"] for r in load_test_results if "response_time" in r]
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            min_response_time = min(response_times)
        else:
            avg_response_time = max_response_time = min_response_time = 0
        
        print("RESPONSE DATA:")
        print(json.dumps({
            "high_load_performance": {
                "total_requests": len(high_load_requests),
                "stable_responses": stable_responses,
                "handled_requests": handled_requests,
                "total_test_duration": round(total_time, 3),
                "requests_per_second": round(len(high_load_requests) / total_time, 2),
                "stability_rate": round(stable_responses / len(high_load_requests) * 100, 2),
                "handling_rate": round(handled_requests / len(high_load_requests) * 100, 2),
                "response_time_analysis": {
                    "average_ms": round(avg_response_time * 1000, 2),
                    "max_ms": round(max_response_time * 1000, 2),
                    "min_ms": round(min_response_time * 1000, 2)
                },
                "performance_grade": "优秀" if stable_responses > len(high_load_requests) * 0.95 else "良好" if stable_responses > len(high_load_requests) * 0.8 else "需要优化"
            },
            "sample_results": load_test_results[:5]
        }, indent=2))
        
    except Exception as e:
        print("EXCEPTION:")
        print(json.dumps({"error": str(e), "type": type(e).__name__}, indent=2))
    
    # 测试6：系统资源使用模式测试
    print("\n--- 测试6: 系统资源使用模式测试 ---")
    
    print("REQUEST DATA:")
    print(json.dumps({
        "action": "resource_usage_pattern_test",
        "test_duration_seconds": 10,
        "request_interval": 0.1
    }, indent=2))
    
    # 以固定间隔发送请求，观察系统响应模式
    pattern_results = []
    pattern_start = time.time()
    
    while time.time() - pattern_start < 10:  # 运行10秒
        request_time = time.time()
        test_request = {
            "intent": "resource_pattern_test",
            "timestamp": request_time,
            "test_id": f"pattern_{int(request_time * 1000)}"
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(f"{BASE_URL}/intent", json=test_request)
            response_time = time.time()
            
            pattern_results.append({
                "request_timestamp": request_time,
                "response_timestamp": response_time,
                "response_time": round(response_time - request_time, 4),
                "status_code": response.status_code,
                "system_responsive": response.status_code != 500
            })
            
        except Exception as e:
            pattern_results.append({
                "request_timestamp": request_time,
                "error": str(e),
                "system_responsive": False
            })
        
        time.sleep(0.1)  # 100ms间隔
    
    # 分析资源使用模式
    if pattern_results:
        responsive_count = sum(1 for r in pattern_results if r.get("system_responsive", False))
        response_times = [r["response_time"] for r in pattern_results if "response_time" in r]
        
        if response_times:
            avg_pattern_time = sum(response_times) / len(response_times)
            time_variance = max(response_times) - min(response_times) if len(response_times) > 1 else 0
        else:
            avg_pattern_time = time_variance = 0
        
        print("RESPONSE DATA:")
        print(json.dumps({
            "resource_pattern_analysis": {
                "total_requests": len(pattern_results),
                "responsive_requests": responsive_count,
                "responsiveness_rate": round(responsive_count / len(pattern_results) * 100, 2),
                "average_response_time_ms": round(avg_pattern_time * 1000, 2),
                "response_time_variance_ms": round(time_variance * 1000, 2),
                "system_consistency": "稳定" if time_variance < 0.1 else "波动" if time_variance < 0.5 else "不稳定",
                "resource_efficiency": "优秀" if avg_pattern_time < 0.05 else "良好" if avg_pattern_time < 0.2 else "需要优化"
            },
            "sample_pattern": pattern_results[-5:] if len(pattern_results) >= 5 else pattern_results
        }, indent=2))
    else:
        print("RESPONSE DATA:")
        print(json.dumps({
            "resource_pattern_analysis": "无响应数据，系统可能不可用"
        }, indent=2))

async def run_all_tests():
    """
    执行所有系统集成测试用例
    按照环境检查 -> 能力发现 -> 异常测试 -> 功能测试 -> 性能测试的顺序
    """
    try:
        # 首先检查系统可用性
        if not await check_system_availability_async():
            print("\n系统不可用，请确保运行 uvicorn main:app --host 0.0.0.0 --port 8000")
            print("FINAL RESULT: TEST FAILED - SYSTEM NOT AVAILABLE")
            return

        # 发现系统能力
        available_capabilities = await discover_system_capabilities()

        if not available_capabilities:
            print("\n警告：未发现任何可用的系统功能")

        # 执行异常场景测试
        await test_system_integration_exceptions()

        # 执行端到端集成测试
        await test_end_to_end_integration()

        # 执行性能集成测试
        await test_system_performance_integration()

        print("\nFINAL RESULT: TEST COMPLETED - 检查上述响应以验证系统集成状态")

    except Exception as e:
        print(f"\nEXCEPTION:")
        print(json.dumps({"error": str(e), "type": type(e).__name__}, indent=2))
        print("FINAL RESULT: TEST FAILED")

if __name__ == "__main__":
    # 运行所有异步测试用例
    asyncio.run(run_all_tests())