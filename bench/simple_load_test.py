#!/usr/bin/env python3
"""
简化的压力测试脚本
"""

import sys
import time
import json
import concurrent.futures
import requests
from statistics import mean, median
import threading
from collections import defaultdict

def send_request(url, payload, headers):
    """发送单个请求并记录时间"""
    start_time = time.time()
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        end_time = time.time()
        
        response_time = end_time - start_time
        status_code = response.status_code
        
        # 获取自定义响应头
        process_time = response.headers.get('X-Process-Time', 'N/A')
        
        return {
            'status_code': status_code,
            'response_time': response_time,
            'process_time': process_time,
            'success': True
        }
    except Exception as e:
        end_time = time.time()
        response_time = end_time - start_time
        return {
            'status_code': 0,
            'response_time': response_time, 
            'process_time': 'N/A',
            'success': False,
            'error': str(e)
        }

def run_load_test(payload_file, concurrency, total_requests, duration=0):
    """运行压力测试"""
    
    # 加载payload
    with open(payload_file, 'r') as f:
        payload = json.load(f)
    
    url = "http://127.0.0.1:8000/intent"
    headers = {'Content-Type': 'application/json'}
    
    print(f"=== 压测参数 ===")
    print(f"载荷文件: {payload_file}")
    print(f"并发数: {concurrency}")
    print(f"总请求数: {total_requests}")
    if duration > 0:
        print(f"持续时间: {duration}秒")
    print(f"目标URL: {url}")
    print()
    
    results = []
    start_time = time.time()
    
    if duration > 0:
        # 按时间运行
        print(f"开始持续时间测试... (持续 {duration} 秒)")
        
        def worker():
            while time.time() - start_time < duration:
                result = send_request(url, payload, headers)
                results.append(result)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = [executor.submit(worker) for _ in range(concurrency)]
            concurrent.futures.wait(futures)
    else:
        # 按请求数运行
        print(f"开始请求数测试... (总共 {total_requests} 请求)")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = [executor.submit(send_request, url, payload, headers) 
                      for _ in range(total_requests)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"压测完成! 总耗时: {total_time:.3f}秒")
    print()
    
    # 统计结果
    print("=== 结果统计 ===")
    
    total_requests_actual = len(results)
    successful_requests = len([r for r in results if r['success']])
    failed_requests = total_requests_actual - successful_requests
    
    print(f"实际完成请求数: {total_requests_actual}")
    print(f"成功请求数: {successful_requests}")
    print(f"失败请求数: {failed_requests}")
    
    if total_requests_actual == 0:
        print("错误: 没有任何请求")
        return
        
    # RPS计算
    rps = total_requests_actual / total_time if total_time > 0 else 0
    print(f"RPS (每秒请求数): {rps:.2f}")
    
    # 错误率
    error_rate = (failed_requests / total_requests_actual) * 100
    print(f"错误率: {error_rate:.2f}%")
    
    # 状态码分布
    status_codes = defaultdict(int)
    for result in results:
        status_codes[result['status_code']] += 1
    
    print("\n状态码分布:")
    for code, count in sorted(status_codes.items()):
        print(f"  {code}: {count}")
    
    # 响应时间统计
    response_times = [r['response_time'] for r in results if r['success']]
    
    if response_times:
        response_times.sort()
        n = len(response_times)
        
        avg_time = mean(response_times) * 1000  # 转换为毫秒
        min_time = min(response_times) * 1000
        max_time = max(response_times) * 1000
        median_time = median(response_times) * 1000
        
        # 百分位
        p50_time = response_times[int(n * 0.5)] * 1000
        p90_time = response_times[int(n * 0.9)] * 1000 
        p95_time = response_times[int(n * 0.95)] * 1000
        p99_time = response_times[int(n * 0.99)] * 1000
        
        print(f"\n响应时间统计 (毫秒):")
        print(f"  平均: {avg_time:.2f}ms")
        print(f"  中位数: {median_time:.2f}ms") 
        print(f"  最小: {min_time:.2f}ms")
        print(f"  最大: {max_time:.2f}ms")
        print(f"  P50: {p50_time:.2f}ms")
        print(f"  P90: {p90_time:.2f}ms")
        print(f"  P95: {p95_time:.2f}ms")
        print(f"  P99: {p99_time:.2f}ms")
        
        # X-Process-Time样例
        process_times = [r['process_time'] for r in results if r['process_time'] != 'N/A']
        if process_times:
            print(f"  X-Process-Time 样例: {process_times[0]}")
    
    # 返回汇总数据供后续使用
    return {
        'total_requests': total_requests_actual,
        'successful_requests': successful_requests,
        'failed_requests': failed_requests,
        'total_time': total_time,
        'rps': rps,
        'error_rate': error_rate,
        'status_codes': dict(status_codes),
        'response_times': {
            'avg': avg_time if response_times else 0,
            'min': min_time if response_times else 0,
            'max': max_time if response_times else 0,
            'p50': p50_time if response_times else 0,
            'p90': p90_time if response_times else 0,
            'p95': p95_time if response_times else 0,
            'p99': p99_time if response_times else 0,
        } if response_times else {}
    }

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("用法: python3 simple_load_test.py <payload_file> <concurrency> <total_requests> [duration]")
        sys.exit(1)
    
    payload_file = sys.argv[1]
    concurrency = int(sys.argv[2])
    total_requests = int(sys.argv[3])
    duration = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    
    run_load_test(payload_file, concurrency, total_requests, duration)
