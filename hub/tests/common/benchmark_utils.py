#!/usr/bin/env python3
"""
Hub Tests Benchmark Utilities
连接预热和性能基准测试工具

根据《Invalid Intent Slowpath Deep Dive Analysis》报告修复：
- 连接预热：解决首次请求连接建立开销
- 性能基准：提供标准化的性能测试和报告
- 时间测量：高精度计时和分位数统计
- 对照测试：与 curl 基准对比分析
"""

import time
import asyncio
import statistics
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from http_client import (
    get_sync_client, get_async_client, 
    safe_request_with_timeout_details,
    safe_async_request_with_timeout_details,
    BASE_URL
)


@dataclass
class BenchmarkResult:
    """基准测试结果数据类"""
    total_requests: int
    successful_requests: int
    failed_requests: int
    error_requests: int
    
    # 时间统计（毫秒）
    total_time_ms: float
    avg_time_ms: float
    min_time_ms: float
    max_time_ms: float
    p50_ms: float
    p90_ms: float
    p95_ms: float
    
    # 连接统计
    connect_times_ms: List[float]
    process_times_ms: List[float]
    
    # 错误详情
    timeout_errors: int
    connect_errors: int
    other_errors: int
    error_details: List[Dict[str, Any]]
    
    # 服务端处理时间（来自响应头）
    server_process_times_ms: List[float]


def warmup_connection(rounds: int = 2) -> Dict[str, Any]:
    """
    连接预热函数
    
    在性能测试前调用，预热 TCP 连接和连接池，忽略结果
    
    Args:
        rounds: 预热轮数，默认 2 轮
        
    Returns:
        预热结果统计
    """
    print(f"🔥 开始连接预热 ({rounds} 轮)...")
    
    warmup_results = []
    client = get_sync_client()
    
    # 预热 GET 根路径
    for i in range(rounds):
        start_time = time.perf_counter()
        response, error = safe_request_with_timeout_details(client, "GET", "/")
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        
        warmup_results.append({
            "round": i + 1,
            "endpoint": "GET /",
            "success": response is not None,
            "time_ms": round(elapsed_ms, 2),
            "status_code": response.status_code if response else None,
            "error": error
        })
    
    # 预热 POST 无效 intent 端点
    for i in range(rounds):
        start_time = time.perf_counter()
        response, error = safe_request_with_timeout_details(
            client, "POST", "/dev/raise_invalid_intent", json={}
        )
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        
        warmup_results.append({
            "round": i + 1,
            "endpoint": "POST /dev/raise_invalid_intent",
            "success": response is not None,
            "time_ms": round(elapsed_ms, 2),
            "status_code": response.status_code if response else None,
            "error": error
        })
    
    successful_warmups = sum(1 for r in warmup_results if r["success"])
    avg_warmup_time = statistics.mean([r["time_ms"] for r in warmup_results if r["success"]])
    
    result = {
        "total_warmup_requests": len(warmup_results),
        "successful_warmups": successful_warmups,
        "avg_warmup_time_ms": round(avg_warmup_time, 2),
        "warmup_success_rate": round(successful_warmups / len(warmup_results) * 100, 2),
        "detailed_results": warmup_results
    }
    
    print(f"✅ 连接预热完成: {successful_warmups}/{len(warmup_results)} 成功, 平均 {result['avg_warmup_time_ms']}ms")
    return result


async def async_warmup_connection(rounds: int = 2) -> Dict[str, Any]:
    """异步连接预热函数"""
    print(f"🔥 开始异步连接预热 ({rounds} 轮)...")
    
    warmup_results = []
    client = get_async_client()
    
    # 预热 GET 根路径
    for i in range(rounds):
        start_time = time.perf_counter()
        response, error = await safe_async_request_with_timeout_details(client, "GET", "/")
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        
        warmup_results.append({
            "round": i + 1,
            "endpoint": "GET /",
            "success": response is not None,
            "time_ms": round(elapsed_ms, 2),
            "status_code": response.status_code if response else None,
            "error": error
        })
    
    # 预热 POST 无效 intent 端点
    for i in range(rounds):
        start_time = time.perf_counter()
        response, error = await safe_async_request_with_timeout_details(
            client, "POST", "/dev/raise_invalid_intent", json={}
        )
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        
        warmup_results.append({
            "round": i + 1,
            "endpoint": "POST /dev/raise_invalid_intent",
            "success": response is not None,
            "time_ms": round(elapsed_ms, 2),
            "status_code": response.status_code if response else None,
            "error": error
        })
    
    successful_warmups = sum(1 for r in warmup_results if r["success"])
    avg_warmup_time = statistics.mean([r["time_ms"] for r in warmup_results if r["success"]])
    
    result = {
        "total_warmup_requests": len(warmup_results),
        "successful_warmups": successful_warmups,
        "avg_warmup_time_ms": round(avg_warmup_time, 2),
        "warmup_success_rate": round(successful_warmups / len(warmup_results) * 100, 2),
        "detailed_results": warmup_results
    }
    
    print(f"✅ 异步连接预热完成: {successful_warmups}/{len(warmup_results)} 成功, 平均 {result['avg_warmup_time_ms']}ms")
    return result


def benchmark_invalid_intent_sync(iterations: int = 10) -> BenchmarkResult:
    """
    同步无效 intent 基准测试
    
    测试 /intent 端点处理无效 intent 的性能
    
    Args:
        iterations: 测试迭代次数
        
    Returns:
        BenchmarkResult: 详细的基准测试结果
    """
    print(f"📊 开始同步无效 intent 基准测试 ({iterations} 次迭代)...")
    
    # 先进行预热
    warmup_connection(2)
    
    client = get_sync_client()
    test_request = {
        "intent": "benchmark_test_intent",
        "request_id": "benchmark_sync_001",
        "user_id": "benchmark_user"
    }
    
    results = []
    error_details = []
    
    for i in range(iterations):
        start_time = time.perf_counter()
        response, error = safe_request_with_timeout_details(
            client, "POST", "/intent", json=test_request
        )
        total_time_ms = (time.perf_counter() - start_time) * 1000
        
        if response:
            # 提取服务端处理时间（如果存在 X-Process-Time 头）
            server_time_ms = None
            if "X-Process-Time" in response.headers:
                try:
                    server_time_ms = float(response.headers["X-Process-Time"]) * 1000
                except:
                    pass
            
            results.append({
                "iteration": i + 1,
                "total_time_ms": round(total_time_ms, 2),
                "server_time_ms": round(server_time_ms, 2) if server_time_ms else None,
                "status_code": response.status_code,
                "success": True,
                "error": False
            })
        else:
            results.append({
                "iteration": i + 1,
                "total_time_ms": round(total_time_ms, 2),
                "server_time_ms": None,
                "status_code": None,
                "success": False,
                "error": True
            })
            error_details.append(error)
    
    # 统计分析
    successful_results = [r for r in results if r["success"]]
    failed_results = [r for r in results if not r["success"]]
    
    if successful_results:
        times_ms = [r["total_time_ms"] for r in successful_results]
        server_times_ms = [r["server_time_ms"] for r in successful_results if r["server_time_ms"]]
        
        # 计算分位数
        times_ms_sorted = sorted(times_ms)
        p50_idx = int(len(times_ms_sorted) * 0.5)
        p90_idx = int(len(times_ms_sorted) * 0.9)
        p95_idx = int(len(times_ms_sorted) * 0.95)
        
        benchmark_result = BenchmarkResult(
            total_requests=iterations,
            successful_requests=len(successful_results),
            failed_requests=len(failed_results),
            error_requests=len([r for r in results if r.get("error", False)]),
            
            total_time_ms=round(sum(times_ms), 2),
            avg_time_ms=round(statistics.mean(times_ms), 2),
            min_time_ms=round(min(times_ms), 2),
            max_time_ms=round(max(times_ms), 2),
            p50_ms=round(times_ms_sorted[p50_idx], 2),
            p90_ms=round(times_ms_sorted[p90_idx], 2),
            p95_ms=round(times_ms_sorted[p95_idx], 2),
            
            connect_times_ms=[],  # 暂时无法单独测量连接时间
            process_times_ms=times_ms,
            
            timeout_errors=len([e for e in error_details if e and e.get("error_type") == "timeout"]),
            connect_errors=len([e for e in error_details if e and e.get("error_type") == "connect"]),
            other_errors=len([e for e in error_details if e and e.get("error_type") not in ["timeout", "connect"]]),
            error_details=error_details,
            
            server_process_times_ms=server_times_ms
        )
        
        print(f"✅ 同步基准测试完成: 平均 {benchmark_result.avg_time_ms}ms, P95 {benchmark_result.p95_ms}ms")
        return benchmark_result
    else:
        print("❌ 所有请求均失败，无法生成基准结果")
        return BenchmarkResult(
            total_requests=iterations,
            successful_requests=0,
            failed_requests=iterations,
            error_requests=iterations,
            total_time_ms=0, avg_time_ms=0, min_time_ms=0, max_time_ms=0,
            p50_ms=0, p90_ms=0, p95_ms=0,
            connect_times_ms=[], process_times_ms=[],
            timeout_errors=len([e for e in error_details if e and e.get("error_type") == "timeout"]),
            connect_errors=len([e for e in error_details if e and e.get("error_type") == "connect"]),
            other_errors=len([e for e in error_details if e and e.get("error_type") not in ["timeout", "connect"]]),
            error_details=error_details,
            server_process_times_ms=[]
        )


async def benchmark_invalid_intent_async(iterations: int = 10) -> BenchmarkResult:
    """异步无效 intent 基准测试"""
    print(f"📊 开始异步无效 intent 基准测试 ({iterations} 次迭代)...")
    
    # 先进行预热
    await async_warmup_connection(2)
    
    client = get_async_client()
    test_request = {
        "intent": "benchmark_test_intent",
        "request_id": "benchmark_async_001", 
        "user_id": "benchmark_user"
    }
    
    results = []
    error_details = []
    
    for i in range(iterations):
        start_time = time.perf_counter()
        response, error = await safe_async_request_with_timeout_details(
            client, "POST", "/intent", json=test_request
        )
        total_time_ms = (time.perf_counter() - start_time) * 1000
        
        if response:
            # 提取服务端处理时间
            server_time_ms = None
            if "X-Process-Time" in response.headers:
                try:
                    server_time_ms = float(response.headers["X-Process-Time"]) * 1000
                except:
                    pass
            
            results.append({
                "iteration": i + 1,
                "total_time_ms": round(total_time_ms, 2),
                "server_time_ms": round(server_time_ms, 2) if server_time_ms else None,
                "status_code": response.status_code,
                "success": True,
                "error": False
            })
        else:
            results.append({
                "iteration": i + 1,
                "total_time_ms": round(total_time_ms, 2),
                "server_time_ms": None,
                "status_code": None,
                "success": False,
                "error": True
            })
            error_details.append(error)
    
    # 统计分析（同步版本逻辑）
    successful_results = [r for r in results if r["success"]]
    failed_results = [r for r in results if not r["success"]]
    
    if successful_results:
        times_ms = [r["total_time_ms"] for r in successful_results]
        server_times_ms = [r["server_time_ms"] for r in successful_results if r["server_time_ms"]]
        
        times_ms_sorted = sorted(times_ms)
        p50_idx = int(len(times_ms_sorted) * 0.5)
        p90_idx = int(len(times_ms_sorted) * 0.9)
        p95_idx = int(len(times_ms_sorted) * 0.95)
        
        benchmark_result = BenchmarkResult(
            total_requests=iterations,
            successful_requests=len(successful_results),
            failed_requests=len(failed_results),
            error_requests=len([r for r in results if r.get("error", False)]),
            
            total_time_ms=round(sum(times_ms), 2),
            avg_time_ms=round(statistics.mean(times_ms), 2),
            min_time_ms=round(min(times_ms), 2),
            max_time_ms=round(max(times_ms), 2),
            p50_ms=round(times_ms_sorted[p50_idx], 2),
            p90_ms=round(times_ms_sorted[p90_idx], 2),
            p95_ms=round(times_ms_sorted[p95_idx], 2),
            
            connect_times_ms=[],
            process_times_ms=times_ms,
            
            timeout_errors=len([e for e in error_details if e and e.get("error_type") == "timeout"]),
            connect_errors=len([e for e in error_details if e and e.get("error_type") == "connect"]),
            other_errors=len([e for e in error_details if e and e.get("error_type") not in ["timeout", "connect"]]),
            error_details=error_details,
            
            server_process_times_ms=server_times_ms
        )
        
        print(f"✅ 异步基准测试完成: 平均 {benchmark_result.avg_time_ms}ms, P95 {benchmark_result.p95_ms}ms")
        return benchmark_result
    else:
        print("❌ 所有异步请求均失败，无法生成基准结果")
        return BenchmarkResult(
            total_requests=iterations,
            successful_requests=0,
            failed_requests=iterations,
            error_requests=iterations,
            total_time_ms=0, avg_time_ms=0, min_time_ms=0, max_time_ms=0,
            p50_ms=0, p90_ms=0, p95_ms=0,
            connect_times_ms=[], process_times_ms=[],
            timeout_errors=len([e for e in error_details if e and e.get("error_type") == "timeout"]),
            connect_errors=len([e for e in error_details if e and e.get("error_type") == "connect"]),
            other_errors=len([e for e in error_details if e and e.get("error_type") not in ["timeout", "connect"]]),
            error_details=error_details,
            server_process_times_ms=[]
        )


async def concurrent_benchmark(
    concurrent_workers: int = 8,
    total_requests: int = 40,
    batch_size: int = 5
) -> Dict[str, Any]:
    """
    并发基准测试
    
    Args:
        concurrent_workers: 并发工作者数量
        total_requests: 总请求数
        batch_size: 每批请求数
        
    Returns:
        并发测试结果字典
    """
    print(f"🚀 开始并发基准测试: {concurrent_workers} 并发 × {total_requests} 请求 (批量 {batch_size})")
    
    # 预热
    await async_warmup_connection(2)
    
    client = get_async_client()
    
    # 分批执行
    batches = []
    for i in range(0, total_requests, batch_size):
        batch_requests = []
        for j in range(min(batch_size, total_requests - i)):
            req_id = i + j + 1
            batch_requests.append({
                "intent": "benchmark_test_intent",
                "request_id": f"concurrent_bench_{req_id}",
                "user_id": f"concurrent_user_{req_id}"
            })
        batches.append(batch_requests)
    
    all_results = []
    total_start_time = time.perf_counter()
    
    for batch_idx, batch_requests in enumerate(batches):
        print(f"🔄 执行批次 {batch_idx + 1}/{len(batches)} ({len(batch_requests)} 请求)")
        
        # 创建信号量限制并发数
        semaphore = asyncio.Semaphore(concurrent_workers)
        
        async def execute_request(request_data: Dict[str, Any]) -> Dict[str, Any]:
            async with semaphore:
                start_time = time.perf_counter()
                response, error = await safe_async_request_with_timeout_details(
                    client, "POST", "/intent", json=request_data
                )
                total_time_ms = (time.perf_counter() - start_time) * 1000
                
                if response:
                    server_time_ms = None
                    if "X-Process-Time" in response.headers:
                        try:
                            server_time_ms = float(response.headers["X-Process-Time"]) * 1000
                        except:
                            pass
                    
                    return {
                        "request_id": request_data["request_id"],
                        "total_time_ms": round(total_time_ms, 2),
                        "server_time_ms": round(server_time_ms, 2) if server_time_ms else None,
                        "status_code": response.status_code,
                        "success": True,
                        "error": None
                    }
                else:
                    return {
                        "request_id": request_data["request_id"],
                        "total_time_ms": round(total_time_ms, 2),
                        "server_time_ms": None,
                        "status_code": None,
                        "success": False,
                        "error": error
                    }
        
        # 执行当前批次的并发请求
        batch_tasks = [execute_request(req) for req in batch_requests]
        batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
        
        # 处理异常结果
        for i, result in enumerate(batch_results):
            if isinstance(result, Exception):
                all_results.append({
                    "request_id": batch_requests[i]["request_id"],
                    "total_time_ms": 0,
                    "server_time_ms": None,
                    "status_code": None,
                    "success": False,
                    "error": {"error_type": "exception", "message": str(result)}
                })
            else:
                all_results.append(result)
    
    total_time_seconds = time.perf_counter() - total_start_time
    
    # 统计分析
    successful_results = [r for r in all_results if r["success"]]
    failed_results = [r for r in all_results if not r["success"]]
    
    if successful_results:
        times_ms = [r["total_time_ms"] for r in successful_results]
        server_times_ms = [r["server_time_ms"] for r in successful_results if r["server_time_ms"]]
        
        times_ms_sorted = sorted(times_ms)
        p50_idx = int(len(times_ms_sorted) * 0.5)
        p90_idx = int(len(times_ms_sorted) * 0.9)
        p95_idx = int(len(times_ms_sorted) * 0.95)
        
        result = {
            "test_config": {
                "concurrent_workers": concurrent_workers,
                "total_requests": total_requests,
                "batch_size": batch_size,
                "total_batches": len(batches)
            },
            "overall_stats": {
                "total_requests": len(all_results),
                "successful_requests": len(successful_results),
                "failed_requests": len(failed_results),
                "success_rate": round(len(successful_results) / len(all_results) * 100, 2),
                "total_time_seconds": round(total_time_seconds, 3),
                "requests_per_second": round(len(all_results) / total_time_seconds, 2)
            },
            "timing_stats": {
                "avg_time_ms": round(statistics.mean(times_ms), 2),
                "min_time_ms": round(min(times_ms), 2),
                "max_time_ms": round(max(times_ms), 2),
                "p50_ms": round(times_ms_sorted[p50_idx], 2),
                "p90_ms": round(times_ms_sorted[p90_idx], 2),
                "p95_ms": round(times_ms_sorted[p95_idx], 2)
            },
            "server_timing": {
                "server_times_available": len(server_times_ms),
                "avg_server_time_ms": round(statistics.mean(server_times_ms), 2) if server_times_ms else None
            },
            "error_analysis": {
                "timeout_errors": len([r for r in all_results if r.get("error") and r["error"].get("error_type") == "timeout"]),
                "connect_errors": len([r for r in all_results if r.get("error") and r["error"].get("error_type") == "connect"]),
                "other_errors": len([r for r in all_results if r.get("error") and r["error"].get("error_type") not in ["timeout", "connect"]])
            }
        }
        
        print(f"✅ 并发基准测试完成: {result['overall_stats']['success_rate']}% 成功, P95 {result['timing_stats']['p95_ms']}ms")
        return result
    else:
        print("❌ 所有并发请求均失败")
        return {
            "test_config": {
                "concurrent_workers": concurrent_workers,
                "total_requests": total_requests,
                "batch_size": batch_size
            },
            "overall_stats": {
                "total_requests": len(all_results),
                "successful_requests": 0,
                "failed_requests": len(all_results),
                "success_rate": 0,
                "total_time_seconds": round(total_time_seconds, 3)
            },
            "error": "所有请求均失败"
        }
