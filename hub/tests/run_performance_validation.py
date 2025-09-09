#!/usr/bin/env python3
"""
性能验证脚本
用于验证修复后的测试框架性能是否达到预期目标

使用方法:
1. 启动服务: uvicorn main:app --host 0.0.0.0 --port 8000
2. 运行验证: python hub/tests/run_performance_validation.py
"""

import asyncio
import sys
import os
import time

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from hub.tests.common.http_client import BASE_URL, get_sync_client, get_async_client
from hub.tests.common.benchmark_utils import (
    warmup_connection, benchmark_invalid_intent_sync, 
    benchmark_invalid_intent_async, concurrent_benchmark
)
from hub.tests.common.report_generator import BenchmarkReportGenerator


def check_server_availability():
    """检查服务器是否可用"""
    print("🔍 检查服务器可用性...")
    
    client = get_sync_client()
    try:
        response = client.get("/")
        if response.status_code in [200, 404]:
            print("✅ 服务器可用")
            return True
        else:
            print(f"⚠️ 服务器响应异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 服务器不可用: {e}")
        print("请确保运行: uvicorn main:app --host 0.0.0.0 --port 8000")
        return False


async def run_performance_validation():
    """运行性能验证测试"""
    print("="*80)
    print("🚀 无效Intent性能修复验证")
    print("="*80)
    print(f"⏰ 测试开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 目标: 将无效Intent响应时间从~2s降低到≤300ms")
    print(f"🌐 测试端点: {BASE_URL}")
    print()
    
    # 检查服务器可用性
    if not check_server_availability():
        return False
    
    try:
        # 创建报告生成器
        report_generator = BenchmarkReportGenerator()
        
        print("📊 执行基准测试...")
        print()
        
        # 1. 同步基准测试
        print("1️⃣ 同步基准测试")
        sync_start = time.perf_counter()
        sync_result = benchmark_invalid_intent_sync(iterations=10)
        sync_duration = time.perf_counter() - sync_start
        
        # 2. 异步基准测试
        print("\n2️⃣ 异步基准测试")
        async_start = time.perf_counter()
        async_result = await benchmark_invalid_intent_async(iterations=10)
        async_duration = time.perf_counter() - async_start
        
        # 3. 并发基准测试
        print("\n3️⃣ 并发基准测试")
        concurrent_start = time.perf_counter()
        concurrent_result = await concurrent_benchmark(
            concurrent_workers=8,
            total_requests=40,
            batch_size=5
        )
        concurrent_duration = time.perf_counter() - concurrent_start
        
        # 生成详细报告
        print("\n📋 生成性能报告...")
        report_path = report_generator.generate_httpx_benchmark_report(
            sync_result=sync_result,
            async_result=async_result,
            concurrent_result=concurrent_result,
            curl_baseline_ms=210.0
        )
        
        # 验证结果
        print("\n" + "="*80)
        print("✅ 验证结果汇总")
        print("="*80)
        
        validation_passed = True
        
        # 检查同步性能
        print(f"📈 同步基准测试:")
        print(f"   • 平均响应时间: {sync_result.avg_time_ms}ms")
        print(f"   • P95响应时间: {sync_result.p95_ms}ms")
        print(f"   • 成功率: {sync_result.successful_requests}/{sync_result.total_requests}")
        print(f"   • 测试耗时: {sync_duration:.2f}s")
        
        sync_target_met = sync_result.avg_time_ms <= 300
        print(f"   • 目标达成: {'✅ 是' if sync_target_met else '❌ 否'} (≤300ms)")
        if not sync_target_met:
            validation_passed = False
        
        # 检查异步性能
        print(f"\n📈 异步基准测试:")
        print(f"   • 平均响应时间: {async_result.avg_time_ms}ms")
        print(f"   • P95响应时间: {async_result.p95_ms}ms")
        print(f"   • 成功率: {async_result.successful_requests}/{async_result.total_requests}")
        print(f"   • 测试耗时: {async_duration:.2f}s")
        
        async_target_met = async_result.avg_time_ms <= 300
        print(f"   • 目标达成: {'✅ 是' if async_target_met else '❌ 否'} (≤300ms)")
        if not async_target_met:
            validation_passed = False
        
        # 检查并发性能
        if concurrent_result.get('timing_stats'):
            timing_stats = concurrent_result['timing_stats']
            overall_stats = concurrent_result['overall_stats']
            
            print(f"\n📈 并发基准测试:")
            print(f"   • 平均响应时间: {timing_stats['avg_time_ms']}ms")
            print(f"   • P95响应时间: {timing_stats['p95_ms']}ms")
            print(f"   • 成功率: {overall_stats['success_rate']}%")
            print(f"   • 吞吐量: {overall_stats['requests_per_second']} req/s")
            print(f"   • 测试耗时: {concurrent_duration:.2f}s")
            
            concurrent_p95_met = timing_stats['p95_ms'] <= 450
            concurrent_stability_met = overall_stats['success_rate'] == 100
            print(f"   • P95目标达成: {'✅ 是' if concurrent_p95_met else '❌ 否'} (≤450ms)")
            print(f"   • 稳定性目标达成: {'✅ 是' if concurrent_stability_met else '❌ 否'} (100%)")
            
            if not (concurrent_p95_met and concurrent_stability_met):
                validation_passed = False
        else:
            print(f"\n📈 并发基准测试: ❌ 失败")
            validation_passed = False
        
        # 性能对比
        print(f"\n📊 性能改进对比:")
        original_time = 2050  # 原始问题时间
        if sync_result.avg_time_ms > 0:
            improvement = ((original_time - sync_result.avg_time_ms) / original_time) * 100
            speedup = original_time / sync_result.avg_time_ms
            print(f"   • 修复前: ~{original_time}ms")
            print(f"   • 修复后: {sync_result.avg_time_ms}ms")
            print(f"   • 性能提升: {improvement:.1f}%")
            print(f"   • 速度倍数: {speedup:.1f}x")
        
        # 最终结论
        print(f"\n🎯 最终结论:")
        if validation_passed:
            print("✅ 性能修复成功！所有验收标准均已达成")
            print("🎉 无效Intent处理时间已从~2s降低到预期范围内")
        else:
            print("⚠️ 部分验收标准未达成，需要进一步调优")
        
        print(f"\n📋 详细报告: {report_path}")
        print(f"⏰ 验证完成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        return validation_passed
        
    except Exception as e:
        print(f"❌ 验证过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # 清理连接
        from hub.tests.common.http_client import close_all_clients
        close_all_clients()


def main():
    """主函数"""
    success = asyncio.run(run_performance_validation())
    
    if success:
        print("\n🎊 验证完成：性能修复成功！")
        sys.exit(0)
    else:
        print("\n❌ 验证失败：需要进一步优化")
        sys.exit(1)


if __name__ == "__main__":
    main()
