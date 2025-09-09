#!/usr/bin/env python3
"""
简化的性能测试脚本
用于快速验证修复效果
"""

import time
import statistics
import asyncio

# 尝试导入我们的优化模块
try:
    from common.http_client import get_sync_client, BASE_URL, safe_request_with_timeout_details
    from common.benchmark_utils import warmup_connection
    print("✅ 优化模块导入成功")
except Exception as e:
    print(f"❌ 优化模块导入失败: {e}")
    print("回退到标准 httpx")
    import httpx
    BASE_URL = "http://127.0.0.1:8000"
    
    def get_sync_client():
        return httpx.Client(base_url=BASE_URL, timeout=5.0)
    
    def safe_request_with_timeout_details(client, method, url, **kwargs):
        try:
            response = client.request(method, url, **kwargs)
            return response, None
        except Exception as e:
            return None, {"error": str(e)}
    
    def warmup_connection(rounds=2):
        print(f"简化预热 ({rounds} 轮)...")
        client = get_sync_client()
        for i in range(rounds):
            try:
                client.get("/")
                print(f"  预热轮次 {i+1} 完成")
            except:
                print(f"  预热轮次 {i+1} 失败")


def test_invalid_intent_performance():
    """测试无效intent的性能"""
    print("="*60)
    print("🚀 简化性能测试")
    print("="*60)
    
    # 检查服务器
    client = get_sync_client()
    try:
        response, error = safe_request_with_timeout_details(client, "GET", "/")
        if error or (response and response.status_code not in [200, 404]):
            print("❌ 服务器不可用，请启动服务器:")
            print("   uvicorn main:app --host 0.0.0.0 --port 8000")
            return False
        print("✅ 服务器可用")
    except Exception as e:
        print(f"❌ 服务器连接失败: {e}")
        return False
    
    # 预热连接
    print("\n🔥 预热连接...")
    try:
        warmup_connection(2)
        print("✅ 预热完成")
    except Exception as e:
        print(f"⚠️ 预热失败: {e}")
    
    # 测试无效intent性能
    print(f"\n📊 测试无效Intent性能 ({BASE_URL}/intent)...")
    
    test_request = {
        "intent": "benchmark_test_intent",
        "request_id": "perf_test_001",
        "user_id": "perf_test_user"
    }
    
    times = []
    success_count = 0
    iterations = 10
    
    print(f"执行 {iterations} 次测试...")
    
    for i in range(iterations):
        start_time = time.perf_counter()
        
        try:
            response, error = safe_request_with_timeout_details(
                client, "POST", "/intent", json=test_request
            )
            
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            times.append(elapsed_ms)
            
            if error:
                print(f"  第{i+1}次: 错误 - {error}")
            elif response:
                success_count += 1
                status_emoji = "✅" if response.status_code >= 400 else "⚠️"
                print(f"  第{i+1}次: {elapsed_ms:.1f}ms (状态:{response.status_code}) {status_emoji}")
            else:
                print(f"  第{i+1}次: 未知错误")
                
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            times.append(elapsed_ms)
            print(f"  第{i+1}次: 异常 - {e}")
    
    # 统计结果
    if times:
        avg_time = statistics.mean(times)
        min_time = min(times)
        max_time = max(times)
        
        # 计算分位数
        sorted_times = sorted(times)
        p95_idx = int(len(sorted_times) * 0.95)
        p95_time = sorted_times[p95_idx] if p95_idx < len(sorted_times) else sorted_times[-1]
        
        print(f"\n📈 性能统计:")
        print(f"  • 成功次数: {success_count}/{iterations}")
        print(f"  • 平均时间: {avg_time:.1f}ms")
        print(f"  • 最小时间: {min_time:.1f}ms")
        print(f"  • 最大时间: {max_time:.1f}ms")
        print(f"  • P95时间: {p95_time:.1f}ms")
        
        print(f"\n🎯 验收检查:")
        avg_pass = avg_time <= 300
        p95_pass = p95_time <= 450
        success_pass = success_count == iterations
        
        print(f"  • 平均时间 ≤ 300ms: {'✅ PASS' if avg_pass else '❌ FAIL'} ({avg_time:.1f}ms)")
        print(f"  • P95时间 ≤ 450ms: {'✅ PASS' if p95_pass else '❌ FAIL'} ({p95_time:.1f}ms)")
        print(f"  • 全部成功: {'✅ PASS' if success_pass else '❌ FAIL'} ({success_count}/{iterations})")
        
        # 对比修复前
        original_time = 2050
        if avg_time > 0:
            improvement = ((original_time - avg_time) / original_time) * 100
            speedup = original_time / avg_time
            print(f"\n🚀 修复效果:")
            print(f"  • 修复前: ~{original_time}ms")
            print(f"  • 修复后: {avg_time:.1f}ms")
            print(f"  • 性能提升: {improvement:.1f}%")
            print(f"  • 速度倍数: {speedup:.1f}x")
        
        all_pass = avg_pass and p95_pass and success_pass
        print(f"\n🏆 总体结论: {'✅ 修复成功' if all_pass else '⚠️ 需要优化'}")
        
        return all_pass
    else:
        print("❌ 没有有效的测试结果")
        return False


def main():
    """主函数"""
    success = test_invalid_intent_performance()
    
    if success:
        print("\n🎉 性能验证通过！无效Intent处理时间已优化到目标范围内")
        return 0
    else:
        print("\n⚠️ 性能验证未完全通过，但可能已有显著改善")
        return 1


if __name__ == "__main__":
    exit(main())
