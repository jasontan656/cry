#!/usr/bin/env python3
# test_hub_flow_integrity.py - Hub流程完整性验证全面异步测试脚本
# 测试目标：通过异步HTTP请求验证hub的流程完整性检查、系统健康监控等功能

import json
import time
import asyncio
from async_utils import (
    get_async_client, async_http_request, async_concurrent_requests,
    format_test_output, format_performance_stats, format_test_summary,
    check_system_availability_async, BASE_URL
)

async def test_flow_integrity_exceptions():
    """
    Phase 1: 异常场景测试 - 流程完整性验证异常处理
    目的：验证不存在流程、无效参数等异常情况的完整性检查
    """
    print("\n=== Phase 1: 流程完整性异常场景测试 ===")
    
    # 测试1：验证不存在的流程步骤
    non_existent_step_request = {
        "intent": "non_existent_flow_step_xyz",
        "request_id": "integrity_test_001",
        "user_id": "test_user_integrity"
    }

    async with get_async_client() as client:
        result = await async_http_request("POST", f"{BASE_URL}/intent", client, json_data=non_existent_step_request)

    response_data = {
        "status_code": result["status_code"],
        "success": result["success"],
        "step_not_found": result["error_handled"],
        "error_message_present": "error" in str(result["raw_response"]).lower(),
        "system_integrity_maintained": result["status_code"] != 500 if result["status_code"] else False,
        "processing_time": result["processing_time"]
    }

    format_test_output("测试1: 验证不存在的流程步骤", non_existent_step_request, response_data)
    
    # 测试2：验证空流程步骤ID
    empty_intent_request = {
        "intent": "",
        "request_id": "integrity_test_002",
        "user_id": "test_user_empty"
    }

    async with get_async_client() as client:
        result = await async_http_request("POST", f"{BASE_URL}/intent", client, json_data=empty_intent_request)

    response_data = {
        "status_code": result["status_code"],
        "success": result["success"],
        "empty_intent_handled": result["error_handled"],
        "validation_error": "intent" in str(result["raw_response"]).lower() or "empty" in str(result["raw_response"]).lower(),
        "system_stable": result["status_code"] != 500 if result["status_code"] else False,
        "processing_time": result["processing_time"]
    }

    format_test_output("测试2: 验证空流程步骤ID", empty_intent_request, response_data)
    
    # 测试3：测试系统在没有有效流程时的响应
    request_summary = {"action": "check_system_flow_state"}

    # 尝试访问可能存在的系统状态端点
    endpoints_to_check = ["/health", "/status", "/system", "/flows"]
    endpoint_found = False

    async with get_async_client() as client:
        for endpoint in endpoints_to_check:
            try:
                result = await async_http_request("GET", f"{BASE_URL}{endpoint}", client)
                if result["success"]:
                    response_data = {
                        "endpoint": endpoint,
                        "status_code": result["status_code"],
                        "success": result["success"],
                        "system_info_available": result["success"],
                        "data_present": bool(result["raw_response"]),
                        "sample_data": result["raw_response"] if len(str(result["raw_response"])) < 500 else "数据过大，已截断",
                        "processing_time": result["processing_time"]
                    }
                    format_test_output("测试3: 系统流程状态检查", request_summary, response_data)
                    endpoint_found = True
                    break
            except:
                continue

    if not endpoint_found:
        response_data = {
            "system_status_endpoints": "未找到标准状态端点",
            "attempted_endpoints": endpoints_to_check,
            "system_integrity": "无法直接验证，需要通过功能测试"
        }
        format_test_output("测试3: 系统流程状态检查", request_summary, response_data)

async def test_valid_flow_integrity():
    """
    Phase 2: 正常场景测试 - 标准流程完整性验证功能
    目的：验证系统对有效请求的处理能力和流程完整性
    """
    print("\n=== Phase 2: 流程完整性正常场景测试 ===")
    
    # 测试4：测试系统的基本响应能力
    # 使用真实存在的auth和mbti模块intent
    real_intents = [
        # Auth模块真实intent
        "register_step1",
        "oauth_google_step1", 
        "reset_step1",
        # MBTI模块真实intent
        "mbti_step1",
        "mbti_step2"
    ]

    request_summary = {
        "action": "test_real_intents", 
        "intents_to_test": real_intents
    }

    # 创建并发请求 - 为不同intent补充必需字段
    concurrent_requests = []
    
    for intent in real_intents:
        base_data = {
            "intent": intent,
            "request_id": f"integrity_test_{intent}",
            "user_id": "test_user_integrity"
        }
        
        # 根据intent类型补充必需字段
        if intent == "register_step1":
            base_data.update({
                "email": "test@example.com",
                "test_user": True
            })
        elif intent == "oauth_google_step1":
            base_data.update({
                "state": "test_state_12345"
            })
        elif intent == "reset_step1":
            base_data.update({
                "email": "test@example.com", 
                "test_user": True
            })
        # mbti模块不需要额外字段，已经包含user_id和request_id
        
        concurrent_requests.append({
            "method": "POST",
            "url": f"{BASE_URL}/intent",
            "json_data": base_data,
            "request_id": f"integrity_test_{intent}"
        })

    # 执行并发请求
    concurrent_results = await async_concurrent_requests(concurrent_requests, max_workers=5)

    # 重新格式化结果
    results = []
    for result in concurrent_results["detailed_results"]:
        results.append({
            "intent": result["intent"],
            "status_code": result["status_code"],
            "success": result["success"],
            "error": result["error_handled"],
            "response_available": bool(result["raw_response"])
        })

    # 统计结果
    successful_intents = [r for r in results if r.get("success", False)]
    handled_errors = [r for r in results if r.get("error", False)]

    response_data = {
        "total_intents_tested": len(real_intents),
        "successful_intents": len(successful_intents),
        "handled_errors": len(handled_errors),
        "system_responsiveness": concurrent_results["success_rate"] / 100,
        "detailed_results": results,
        "integrity_assessment": "良好" if len(successful_intents) > 0 or len(handled_errors) > 0 else "需要检查",
        "total_processing_time": concurrent_results["total_processing_time"],
        "requests_per_second": concurrent_results["requests_per_second"]
    }

    format_performance_stats("测试4: 系统基本响应能力测试", response_data)
    
    # 测试5：流程处理时间一致性测试
    # 如果找到了成功的intent，测试其处理时间一致性
    if successful_intents:
        test_intent = successful_intents[0]["intent"]

        request_summary = {
            "action": "timing_consistency_test",
            "test_intent": test_intent,
            "test_count": 5
        }

        # 创建5个相同的并发请求来测试时间一致性
        timing_requests = [
            {
                "method": "POST",
                "url": f"{BASE_URL}/intent",
                "json_data": {
                    "intent": test_intent,
                    "request_id": f"timing_test_{i}",
                    "user_id": f"timing_user_{i}"
                },
                "request_id": f"timing_test_{i}"
            }
            for i in range(5)
        ]

        # 执行并发请求
        timing_concurrent_results = await async_concurrent_requests(timing_requests, max_workers=5)

        # 重新格式化结果
        timing_results = []
        for i, result in enumerate(timing_concurrent_results["detailed_results"]):
            timing_results.append({
                "test_run": i + 1,
                "processing_time": result["processing_time"],
                "status_code": result["status_code"],
                "success": result["success"]
            })

        # 分析时间一致性
        successful_times = [r["processing_time"] for r in timing_results if r.get("processing_time")]
        if successful_times:
            avg_time = sum(successful_times) / len(successful_times)
            max_time = max(successful_times)
            min_time = min(successful_times)

            response_data = {
                "timing_analysis": {
                    "successful_requests": len(successful_times),
                    "average_processing_time": round(avg_time, 4),
                    "min_processing_time": round(min_time, 4),
                    "max_processing_time": round(max_time, 4),
                    "time_variance": round(max_time - min_time, 4),
                    "consistency": "良好" if (max_time - min_time) < 0.5 else "需要优化",
                    "total_test_time": timing_concurrent_results["total_processing_time"]
                },
                "detailed_results": timing_results
            }
        else:
            response_data = {
                "timing_analysis": "无成功请求，无法分析时间一致性",
                "detailed_results": timing_results
            }

        format_performance_stats("测试5: 流程处理时间一致性测试", response_data)
    else:
        response_data = {
            "timing_test": "跳过 - 未找到可用的成功intent进行测试"
        }
        format_performance_stats("测试5: 流程处理时间一致性测试", response_data)
    
    # 测试6：系统负载下的完整性验证
    request_summary = {
        "action": "load_test_integrity",
        "concurrent_requests": 10,
        "request_type": "mixed"
    }

    # 创建混合类型的请求进行负载测试
    load_test_requests = []

    # 添加有效请求（如果有的话）
    if successful_intents:
        valid_intent = successful_intents[0]["intent"]
        for i in range(5):
            load_test_requests.append({
                "method": "POST",
                "url": f"{BASE_URL}/intent",
                "json_data": {
                    "intent": valid_intent,
                    "request_id": f"load_valid_{i}",
                    "user_id": f"load_user_{i}"
                },
                "request_id": f"load_valid_{i}"
            })

    # 添加无效请求
    for i in range(5):
        load_test_requests.append({
            "method": "POST",
            "url": f"{BASE_URL}/intent",
            "json_data": {
                "intent": f"invalid_load_test_{i}",
                "request_id": f"load_invalid_{i}",
                "user_id": f"load_user_invalid_{i}"
            },
            "request_id": f"load_invalid_{i}"
        })

    # 执行并发负载测试
    load_concurrent_results = await async_concurrent_requests(load_test_requests, max_workers=5)

    # 重新格式化结果
    load_results = []
    for result in load_concurrent_results["detailed_results"]:
        load_results.append({
            "request_id": result["request_id"],
            "intent": result["intent"],
            "status_code": result["status_code"],
            "handled": result["status_code"] is not None,
            "success": result["success"] or result["error_handled"]
        })

    # 统计负载测试结果
    handled_requests = sum(1 for r in load_results if r.get("handled", False))
    successful_requests = sum(1 for r in load_results if r.get("success", False))

    response_data = {
        "load_test_summary": {
            "total_requests": len(load_test_requests),
            "handled_requests": handled_requests,
            "successful_requests": successful_requests,
            "total_processing_time": load_concurrent_results["total_processing_time"],
            "requests_per_second": load_concurrent_results["requests_per_second"],
            "system_integrity_under_load": "良好" if handled_requests / len(load_test_requests) > 0.8 else "需要优化"
        },
        "sample_results": load_results[:5]
    }

    format_performance_stats("测试6: 系统负载下的完整性验证", response_data)

async def run_all_tests():
    """
    执行所有流程完整性测试用例
    按照环境检查 -> 异常测试 -> 正常场景测试的顺序
    """
    try:
        # 首先检查系统可用性
        if not await check_system_availability_async():
            print("\n系统不可用，请确保运行 uvicorn main:app --host 0.0.0.0 --port 8000")
            print("FINAL RESULT: TEST FAILED - SYSTEM NOT AVAILABLE")
            return

        # 执行异常场景测试
        await test_flow_integrity_exceptions()

        # 执行正常场景测试
        await test_valid_flow_integrity()

        print("\nFINAL RESULT: TEST COMPLETED - 检查上述响应以验证流程完整性")

    except Exception as e:
        print(f"\nEXCEPTION:")
        print(json.dumps({"error": str(e), "type": type(e).__name__}, indent=2))
        print("FINAL RESULT: TEST FAILED")

if __name__ == "__main__":
    # 运行所有异步测试用例
    asyncio.run(run_all_tests())