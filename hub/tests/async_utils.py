#!/usr/bin/env python3
# async_utils.py - Hub测试异步工具函数库
# 提供统一的异步HTTP请求处理、响应格式化和并发操作功能

import json
import time
import asyncio
import httpx
from typing import Dict, Any, List, Optional, Union
from contextlib import asynccontextmanager

# 系统基础URL配置 - 使用127.0.0.1避免DNS解析延迟
BASE_URL = "http://127.0.0.1:8000"

@asynccontextmanager
async def get_async_client(timeout: float = 30.0):
    """
    异步HTTP客户端上下文管理器 - 已弃用
    请使用 hub.tests.common.http_client.async_client_context() 替代
    
    Args:
        timeout: 请求超时时间（秒）
    """
    # 导入优化的客户端配置
    from .common.http_client import get_async_client as get_optimized_async_client
    
    client = get_optimized_async_client()
    try:
        yield client
    finally:
        # 不关闭，使用全局单例
        pass

async def async_http_request(
    method: str,
    url: str,
    client: httpx.AsyncClient,
    json_data: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    统一的异步HTTP请求函数

    Args:
        method: HTTP方法 ('GET', 'POST', etc.)
        url: 请求URL
        client: httpx.AsyncClient实例
        json_data: 请求JSON数据
        headers: 请求头

    Returns:
        标准化的响应字典
    """
    try:
        start_time = time.time()

        if method.upper() == 'GET':
            response = await client.get(url, headers=headers)
        elif method.upper() == 'POST':
            response = await client.post(url, json=json_data, headers=headers)
        else:
            response = await client.request(method, url, json=json_data, headers=headers)

        processing_time = time.time() - start_time

        # 尝试解析JSON响应
        try:
            response_data = response.json()
        except:
            response_data = {"raw_response": response.text[:500]}  # 限制响应大小

        return {
            "status_code": response.status_code,
            "success": response.status_code in [200, 201, 202],
            "error_handled": response.status_code >= 400,
            "raw_response": response_data,
            "processing_time": round(processing_time, 4),
            "response_size": len(str(response_data))
        }

    except Exception as e:
        return {
            "status_code": None,
            "success": False,
            "error_handled": False,
            "exception": str(e),
            "exception_type": type(e).__name__,
            "processing_time": None
        }

async def async_concurrent_requests(
    requests: List[Dict[str, Any]],
    max_workers: int = 8,
    timeout: float = 30.0
) -> Dict[str, Any]:
    """
    执行并发异步HTTP请求

    Args:
        requests: 请求列表，每个请求包含method, url, json_data等
        max_workers: 最大并发数
        timeout: 单个请求超时时间

    Returns:
        并发执行结果统计
    """
    start_time = time.time()
    results = []

    # 创建信号量限制并发数
    semaphore = asyncio.Semaphore(max_workers)

    async def execute_request(req_data: Dict[str, Any], req_id: int):
        async with semaphore:
            # 使用优化的异步客户端
            from .common.http_client import get_async_client as get_optimized_client
            client = get_optimized_client()
            result = await async_http_request(
                method=req_data.get("method", "POST"),
                url=req_data.get("url", f"{BASE_URL}/intent"),
                client=client,
                json_data=req_data.get("json_data")
            )
            result["request_id"] = req_data.get("request_id", f"req_{req_id}")
            result["intent"] = req_data.get("json_data", {}).get("intent", "unknown")
            return result

    # 执行所有并发请求
    tasks = [execute_request(req, i) for i, req in enumerate(requests)]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # 处理异常结果
    processed_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            processed_results.append({
                "request_id": f"req_{i}",
                "intent": requests[i].get("json_data", {}).get("intent", "unknown"),
                "success": False,
                "error_handled": False,
                "exception": str(result),
                "exception_type": type(result).__name__,
                "processing_time": None
            })
        else:
            processed_results.append(result)

    total_time = time.time() - start_time

    # 统计结果
    successful_requests = sum(1 for r in processed_results if r.get("success", False))
    error_handled_requests = sum(1 for r in processed_results if r.get("error_handled", False))

    return {
        "total_requests": len(requests),
        "total_processing_time": round(total_time, 3),
        "successful_requests": successful_requests,
        "error_handled_requests": error_handled_requests,
        "success_rate": round(successful_requests / len(requests) * 100, 2) if requests else 0,
        "requests_per_second": round(len(requests) / total_time, 2) if total_time > 0 else 0,
        "detailed_results": processed_results
    }

def format_test_output(title: str, request_data: Dict[str, Any], response_data: Dict[str, Any]):
    """
    统一的测试输出格式化函数

    Args:
        title: 测试标题
        request_data: 请求数据
        response_data: 响应数据
    """
    print(f"\n--- {title} ---")

    print("REQUEST DATA:")
    print(json.dumps(request_data, indent=2, ensure_ascii=False))

    print("RESPONSE DATA:")
    print(json.dumps(response_data, indent=2, ensure_ascii=False))

def format_performance_stats(title: str, stats: Dict[str, Any]):
    """
    统一的性能统计输出格式化函数

    Args:
        title: 统计标题
        stats: 统计数据
    """
    print(f"\n=== {title} ===")
    print(json.dumps(stats, indent=2, ensure_ascii=False))

def format_test_summary(test_name: str, results: List[Dict[str, Any]]):
    """
    统一的测试摘要输出格式化函数

    Args:
        test_name: 测试名称
        results: 测试结果列表
    """
    total_tests = len(results)
    successful_tests = sum(1 for r in results if r.get("success", False))
    error_handled_tests = sum(1 for r in results if r.get("error_handled", False))

    summary = {
        "test_name": test_name,
        "total_tests": total_tests,
        "successful_tests": successful_tests,
        "error_handled_tests": error_handled_tests,
        "success_rate": round(successful_tests / total_tests * 100, 2) if total_tests > 0 else 0,
        "error_handling_rate": round(error_handled_tests / total_tests * 100, 2) if total_tests > 0 else 0,
        "overall_status": "PASSED" if successful_tests == total_tests else "PARTIAL" if successful_tests > 0 else "FAILED"
    }

    print(f"\n{'='*60}")
    print(f"测试摘要: {test_name}")
    print(f"{'='*60}")
    print(json.dumps(summary, indent=2, ensure_ascii=False))

async def check_system_availability_async() -> bool:
    """
    异步系统可用性检查

    Returns:
        系统是否可用
    """
    print("=== 测试环境检查：验证系统可用性 ===")

    request_data = {
        "action": "check_system_availability",
        "target_url": BASE_URL
    }

    format_test_output("系统可用性检查", request_data, {})

    # 使用优化的异步客户端进行系统可用性检查
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), 'common'))
    from http_client import get_async_client as get_optimized_client
    client = get_optimized_client()
    result = await async_http_request("GET", f"{BASE_URL}/", client)

    response_data = {
        "status_code": result["status_code"],
        "system_available": result["status_code"] in [200, 404] if result["status_code"] else False,
        "response_time": result["processing_time"],
        "success": result["success"]
    }

    format_test_output("", {}, response_data)

    return response_data["system_available"]
