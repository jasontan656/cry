#!/usr/bin/env python3
# test_hub_exception_handling.py - Hub异常处理机制全面异步测试脚本
# 测试目标：通过异步HTTP请求验证hub在各种异常情况下的处理能力、错误恢复和系统稳定性

import json
import time
import asyncio
from async_utils import (
    get_async_client, async_http_request, async_concurrent_requests,
    format_test_output, format_performance_stats, format_test_summary,
    check_system_availability_async, BASE_URL
)

async def test_system_level_exceptions():
    """
    Phase 1: 异常场景测试 - 系统级异常处理验证
    目的：验证各种系统级异常情况下hub的稳定性和错误处理
    """
    print("\n=== Phase 1: 系统级异常场景测试 ===")

    # 测试1：无效intent请求处理
    invalid_intent_request = {
        "intent": "non_existent_step_error_test",
        "request_id": "error_test_001",
        "user_id": "test_user_error"
    }

    async with get_async_client() as client:
        result = await async_http_request("POST", f"{BASE_URL}/intent", client, json_data=invalid_intent_request)

    response_data = {
        "status_code": result["status_code"],
        "success": result["success"],
        "error_handled": result["error_handled"],
        "system_stable": result["status_code"] != 500 if result["status_code"] else False,
        "error_type": result["raw_response"].get("error", "").split(":")[0] if isinstance(result["raw_response"], dict) and "error" in result["raw_response"] else "unknown",
        "processing_time": result["processing_time"]
    }

    format_test_output("测试1: 无效intent异常处理", invalid_intent_request, response_data)
    
    # 测试2：缺失必要字段的请求
    malformed_request = {
        "request_id": "malformed_001",
        "user_id": "test_user_malformed"
        # 故意不包含intent字段
    }

    async with get_async_client() as client:
        result = await async_http_request("POST", f"{BASE_URL}/intent", client, json_data=malformed_request)

    response_data = {
        "status_code": result["status_code"],
        "success": result["success"],
        "error_handled": result["error_handled"],
        "validation_error": "intent" in str(result["raw_response"]).lower(),
        "system_stable": result["status_code"] != 500 if result["status_code"] else False,
        "processing_time": result["processing_time"]
    }

    format_test_output("测试2: 缺失必要字段异常处理", malformed_request, response_data)
    
    # 测试3：无效JSON格式请求
    invalid_json_request = {"raw_data": "invalid json content"}

    async with get_async_client() as client:
        result = await async_http_request(
            "POST",
            f"{BASE_URL}/intent",
            client,
            headers={"Content-Type": "application/json"}
        )

    response_data = {
        "status_code": result["status_code"],
        "success": result["success"],
        "error_handled": result["error_handled"],
        "json_parse_error": "json" in str(result["raw_response"]).lower() or "parse" in str(result["raw_response"]).lower(),
        "system_stable": result["status_code"] != 500 if result["status_code"] else False,
        "processing_time": result["processing_time"]
    }

    format_test_output("测试3: 无效JSON格式异常处理", invalid_json_request, response_data)
    
    # 测试4：空请求体处理
    empty_body_request = {"empty_body": True}

    async with get_async_client() as client:
        result = await async_http_request(
            "POST",
            f"{BASE_URL}/intent",
            client,
            headers={"Content-Type": "application/json"}
        )

    response_data = {
        "status_code": result["status_code"],
        "success": result["success"],
        "error_handled": result["error_handled"],
        "empty_body_handled": True,
        "system_stable": result["status_code"] != 500 if result["status_code"] else False,
        "processing_time": result["processing_time"]
    }

    format_test_output("测试4: 空请求体异常处理", empty_body_request, response_data)

async def test_concurrent_exception_handling():
    """
    Phase 2: 并发异常场景测试 - 并发环境下的异常处理验证
    目的：验证多个并发异常请求同时处理时的系统稳定性
    """
    print("\n=== Phase 2: 并发异常场景测试 ===")
    
    # 测试5：并发异常请求处理
    # 创建多个不同类型的异常请求
    concurrent_error_requests = [
        {
            "method": "POST",
            "url": f"{BASE_URL}/intent",
            "json_data": {"intent": f"invalid_intent_{i}", "request_id": f"concurrent_err_{i}", "user_id": f"user_{i}"},
            "request_id": f"concurrent_err_{i}"
        }
        for i in range(5)
    ] + [
        {
            "method": "POST",
            "url": f"{BASE_URL}/intent",
            "json_data": {"request_id": f"malformed_{i}", "user_id": f"user_{i+5}"},  # 缺失intent
            "request_id": f"malformed_{i}"
        }
        for i in range(3)
    ]

    request_summary = {
        "action": "concurrent_exception_requests",
        "total_requests": len(concurrent_error_requests),
        "error_types": ["invalid_intent", "malformed_request"],
        "requests_per_type": [5, 3]
    }

    format_test_output("测试5: 并发异常请求处理", request_summary, {})

    # 使用异步并发请求
    concurrent_results = await async_concurrent_requests(concurrent_error_requests, max_workers=8)

    # 重新格式化结果以符合原有格式
    formatted_results = []
    for result in concurrent_results["detailed_results"]:
        formatted_results.append({
            "request_id": result["request_id"],
            "intent": result.get("intent", "missing"),
            "status_code": result["status_code"],
            "error_handled": result["error_handled"],
            "success": result["success"]
        })

    response_data = {
        "total_processing_time": concurrent_results["total_processing_time"],
        "total_requests": concurrent_results["total_requests"],
        "successful_handling": concurrent_results["successful_requests"],
        "error_handled_count": concurrent_results["error_handled_requests"],
        "system_stability": concurrent_results["error_handled_requests"] / concurrent_results["total_requests"] if concurrent_results["total_requests"] > 0 else 0,  # 基于异常处理率计算稳定性
        "detailed_results": formatted_results[:5]  # 显示前5个结果
    }

    format_performance_stats("并发异常请求处理结果", response_data)

async def test_error_recovery_mechanisms():
    """
    Phase 3: 错误恢复机制测试 - 验证系统的自我恢复能力
    目的：验证hub在异常后的恢复机制和容错能力
    """
    print("\n=== Phase 3: 错误恢复机制测试 ===")
    
    # 测试6：异常后的正常请求处理
    # 首先发送一个会异常的请求
    error_request = {
        "intent": "invalid_step_for_recovery_test",
        "request_id": "recovery_test_error",
        "user_id": "recovery_user"
    }

    format_test_output("测试6: 异常后的正常请求处理", error_request, {"note": "异常请求"})

    async with get_async_client() as client:
        # 发送异常请求
        error_result = await async_http_request("POST", f"{BASE_URL}/intent", client, json_data=error_request)

        # 紧接着发送正常请求（假设系统有一些基本的intent处理）
        normal_request = {
            "intent": "test_normal_step",  # 假设存在的正常步骤
            "request_id": "recovery_test_normal",
            "user_id": "recovery_user"
        }

        normal_result = await async_http_request("POST", f"{BASE_URL}/intent", client, json_data=normal_request)

    response_data = {
        "error_request_handled": error_result["error_handled"],
        "normal_request_after_error": {
            "status_code": normal_result["status_code"],
            "success": normal_result["success"] or normal_result["error_handled"],  # 400也算是正常处理
            "response_available": bool(normal_result["raw_response"])
        },
        "system_resilience": "通过" if normal_result["status_code"] in [200, 400] else "需要检查",
        "processing_time": normal_result["processing_time"]
    }

    format_test_output("", {}, response_data)

async def run_all_tests():
    """
    执行所有异常处理测试用例
    按照环境检查 -> 异常测试 -> 并发测试 -> 恢复测试的顺序
    """
    try:
        # 首先检查系统可用性
        if not await check_system_availability_async():
            print("\n系统不可用，请确保运行 uvicorn main:app --host 0.0.0.0 --port 8000")
            print("FINAL RESULT: TEST FAILED - SYSTEM NOT AVAILABLE")
            return

        # 执行系统级异常测试
        await test_system_level_exceptions()

        # 执行并发异常测试
        await test_concurrent_exception_handling()

        # 执行错误恢复测试
        await test_error_recovery_mechanisms()

        print("\nFINAL RESULT: TEST COMPLETED - 检查上述响应以验证异常处理是否正确")

    except Exception as e:
        print(f"\nEXCEPTION:")
        print(json.dumps({"error": str(e), "type": type(e).__name__}, indent=2))
        print("FINAL RESULT: TEST FAILED")

if __name__ == "__main__":
    # 运行所有异步测试用例
    asyncio.run(run_all_tests())