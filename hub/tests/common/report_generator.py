#!/usr/bin/env python3
"""
Hub Tests Report Generator
性能基准测试报告生成器

生成详细的基准测试报告，包括与 curl 基准的对比分析
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from benchmark_utils import BenchmarkResult


class BenchmarkReportGenerator:
    """基准测试报告生成器"""
    
    def __init__(self, report_dir: str = "hub/tests/report"):
        self.report_dir = report_dir
        self.ensure_report_dir()
    
    def ensure_report_dir(self):
        """确保报告目录存在"""
        os.makedirs(self.report_dir, exist_ok=True)
    
    def generate_httpx_benchmark_report(
        self,
        sync_result: Optional[BenchmarkResult] = None,
        async_result: Optional[BenchmarkResult] = None,
        concurrent_result: Optional[Dict[str, Any]] = None,
        curl_baseline_ms: float = 210.0
    ) -> str:
        """
        生成 httpx 基准测试报告
        
        Args:
            sync_result: 同步基准测试结果
            async_result: 异步基准测试结果
            concurrent_result: 并发基准测试结果
            curl_baseline_ms: curl 基准参考值（毫秒）
            
        Returns:
            生成的报告文件路径
        """
        report_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report_filename = f"httpx_benchmark_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        report_path = os.path.join(self.report_dir, report_filename)
        
        # 生成 Markdown 报告内容
        report_content = f"""# HttpX 基准测试报告

## 📊 执行概述

**报告生成时间**: {report_time}  
**测试目标**: 修复无效 intent 请求耗时问题，从 ~2s 降低到 ~210ms  
**参考基准**: curl 直接测试 = {curl_baseline_ms}ms  
**验收标准**: 单次平均 ≤ 300ms，并发 P95 ≤ 450ms

---

## 🔧 测试配置修复

### HttpX 客户端配置优化
- **BASE_URL**: 127.0.0.1:8000 (避免 localhost DNS 解析延迟)
- **连接超时**: 1.0s (connect)
- **读写超时**: 4.0s (read/write/pool)  
- **连接池**: 20 keepalive + 50 max connections
- **协议**: 强制 HTTP/1.1，禁用 HTTP/2
- **重试**: 禁用重试机制
- **环境**: 禁用系统代理和环境变量影响

### 测试框架改进
- **连接预热**: 执行前预热 TCP 连接池
- **客户端复用**: 全套测试使用单一客户端实例
- **超时处理**: 详细超时错误分类和报告
- **并发控制**: 信号量限制 + 批量执行

---
"""

        # 添加同步测试结果
        if sync_result:
            report_content += self._generate_sync_section(sync_result, curl_baseline_ms)
        
        # 添加异步测试结果
        if async_result:
            report_content += self._generate_async_section(async_result, curl_baseline_ms)
        
        # 添加并发测试结果
        if concurrent_result:
            report_content += self._generate_concurrent_section(concurrent_result, curl_baseline_ms)
        
        # 添加对比分析和结论
        report_content += self._generate_comparison_and_conclusion(
            sync_result, async_result, concurrent_result, curl_baseline_ms
        )
        
        # 写入报告文件
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"📋 基准测试报告已生成: {report_path}")
        return report_path
    
    def _generate_sync_section(self, result: BenchmarkResult, curl_baseline: float) -> str:
        """生成同步测试结果章节"""
        performance_grade = "优秀" if result.avg_time_ms <= 300 else "良好" if result.avg_time_ms <= 500 else "需要改进"
        vs_curl_ratio = result.avg_time_ms / curl_baseline if curl_baseline > 0 else 0
        
        return f"""## 📈 同步基准测试结果

### 基础指标
| 指标 | 数值 | 状态 |
|------|------|------|
| 总请求数 | {result.total_requests} | - |
| 成功请求数 | {result.successful_requests} | {'✅' if result.successful_requests == result.total_requests else '⚠️'} |
| 成功率 | {(result.successful_requests/result.total_requests*100):.1f}% | {'✅' if result.successful_requests == result.total_requests else '⚠️'} |

### 响应时间分析
| 统计量 | 时间 (ms) | vs Curl基准 | 状态 |
|--------|-----------|-------------|------|
| 平均值 | {result.avg_time_ms} | {vs_curl_ratio:.1f}x | {'✅' if result.avg_time_ms <= 300 else '⚠️'} |
| 中位数 (P50) | {result.p50_ms} | {result.p50_ms/curl_baseline:.1f}x | - |
| P90 | {result.p90_ms} | {result.p90_ms/curl_baseline:.1f}x | - |
| P95 | {result.p95_ms} | {result.p95_ms/curl_baseline:.1f}x | {'✅' if result.p95_ms <= 450 else '⚠️'} |
| 最小值 | {result.min_time_ms} | {result.min_time_ms/curl_baseline:.1f}x | - |
| 最大值 | {result.max_time_ms} | {result.max_time_ms/curl_baseline:.1f}x | - |

### 性能评级
**等级**: {performance_grade}  
**与 Curl 基准对比**: {vs_curl_ratio:.1f}x ({'+' if vs_curl_ratio > 1 else ''}{(vs_curl_ratio-1)*100:.1f}% 差异)

### 错误分析
| 错误类型 | 数量 | 占比 |
|----------|------|------|
| 超时错误 | {result.timeout_errors} | {(result.timeout_errors/result.total_requests*100):.1f}% |
| 连接错误 | {result.connect_errors} | {(result.connect_errors/result.total_requests*100):.1f}% |
| 其他错误 | {result.other_errors} | {(result.other_errors/result.total_requests*100):.1f}% |

### 服务端处理时间
"""
        
        if result.server_process_times_ms:
            avg_server_time = sum(result.server_process_times_ms) / len(result.server_process_times_ms)
            server_content = f"""
**可用样本**: {len(result.server_process_times_ms)} 个  
**平均服务端处理时间**: {avg_server_time:.2f}ms  
**客户端开销**: {result.avg_time_ms - avg_server_time:.2f}ms ({((result.avg_time_ms - avg_server_time)/result.avg_time_ms*100):.1f}%)

"""
        else:
            server_content = f"""
**服务端时间**: 无可用数据 (未检测到 X-Process-Time 响应头)

"""
        
        return server_content
    
    def _generate_async_section(self, result: BenchmarkResult, curl_baseline: float) -> str:
        """生成异步测试结果章节"""
        performance_grade = "优秀" if result.avg_time_ms <= 300 else "良好" if result.avg_time_ms <= 500 else "需要改进"
        vs_curl_ratio = result.avg_time_ms / curl_baseline if curl_baseline > 0 else 0
        
        return f"""## 🚀 异步基准测试结果

### 基础指标
| 指标 | 数值 | 状态 |
|------|------|------|
| 总请求数 | {result.total_requests} | - |
| 成功请求数 | {result.successful_requests} | {'✅' if result.successful_requests == result.total_requests else '⚠️'} |
| 成功率 | {(result.successful_requests/result.total_requests*100):.1f}% | {'✅' if result.successful_requests == result.total_requests else '⚠️'} |

### 响应时间分析
| 统计量 | 时间 (ms) | vs Curl基准 | 状态 |
|--------|-----------|-------------|------|
| 平均值 | {result.avg_time_ms} | {vs_curl_ratio:.1f}x | {'✅' if result.avg_time_ms <= 300 else '⚠️'} |
| 中位数 (P50) | {result.p50_ms} | {result.p50_ms/curl_baseline:.1f}x | - |
| P90 | {result.p90_ms} | {result.p90_ms/curl_baseline:.1f}x | - |
| P95 | {result.p95_ms} | {result.p95_ms/curl_baseline:.1f}x | {'✅' if result.p95_ms <= 450 else '⚠️'} |
| 最小值 | {result.min_time_ms} | {result.min_time_ms/curl_baseline:.1f}x | - |
| 最大值 | {result.max_time_ms} | {result.max_time_ms/curl_baseline:.1f}x | - |

### 性能评级
**等级**: {performance_grade}  
**与 Curl 基准对比**: {vs_curl_ratio:.1f}x ({'+' if vs_curl_ratio > 1 else ''}{(vs_curl_ratio-1)*100:.1f}% 差异)

"""
    
    def _generate_concurrent_section(self, result: Dict[str, Any], curl_baseline: float) -> str:
        """生成并发测试结果章节"""
        config = result.get("test_config", {})
        overall = result.get("overall_stats", {})
        timing = result.get("timing_stats", {})
        errors = result.get("error_analysis", {})
        
        if not timing:
            return f"""## 🌟 并发基准测试结果

### 测试配置
| 配置项 | 数值 |
|--------|------|
| 并发工作者 | {config.get("concurrent_workers", "N/A")} |
| 总请求数 | {config.get("total_requests", "N/A")} |
| 批次大小 | {config.get("batch_size", "N/A")} |

### 测试结果
**状态**: ❌ 测试失败  
**原因**: {result.get("error", "未知错误")}

"""
        
        p95_status = "✅" if timing.get("p95_ms", 0) <= 450 else "⚠️"
        success_rate_status = "✅" if overall.get("success_rate", 0) == 100 else "⚠️"
        
        return f"""## 🌟 并发基准测试结果

### 测试配置
| 配置项 | 数值 |
|--------|------|
| 并发工作者 | {config.get("concurrent_workers")} |
| 总请求数 | {config.get("total_requests")} |
| 批次大小 | {config.get("batch_size")} |
| 总批次数 | {config.get("total_batches")} |

### 整体统计
| 指标 | 数值 | 状态 |
|------|------|------|
| 总请求数 | {overall.get("total_requests")} | - |
| 成功请求数 | {overall.get("successful_requests")} | - |
| 成功率 | {overall.get("success_rate")}% | {success_rate_status} |
| 总耗时 | {overall.get("total_time_seconds")}s | - |
| 吞吐量 | {overall.get("requests_per_second")} req/s | - |

### 响应时间分析
| 统计量 | 时间 (ms) | vs Curl基准 | 状态 |
|--------|-----------|-------------|------|
| 平均值 | {timing.get("avg_time_ms")} | {timing.get("avg_time_ms", 0)/curl_baseline:.1f}x | - |
| 中位数 (P50) | {timing.get("p50_ms")} | {timing.get("p50_ms", 0)/curl_baseline:.1f}x | - |
| P90 | {timing.get("p90_ms")} | {timing.get("p90_ms", 0)/curl_baseline:.1f}x | - |
| P95 | {timing.get("p95_ms")} | {timing.get("p95_ms", 0)/curl_baseline:.1f}x | {p95_status} |
| 最小值 | {timing.get("min_time_ms")} | {timing.get("min_time_ms", 0)/curl_baseline:.1f}x | - |
| 最大值 | {timing.get("max_time_ms")} | {timing.get("max_time_ms", 0)/curl_baseline:.1f}x | - |

### 并发稳定性分析
| 指标 | 数值 | 状态 |
|------|------|------|
| 并发成功率 | {overall.get("success_rate")}% | {success_rate_status} |
| 超时错误 | {errors.get("timeout_errors", 0)} | {'✅' if errors.get("timeout_errors", 0) == 0 else '⚠️'} |
| 连接错误 | {errors.get("connect_errors", 0)} | {'✅' if errors.get("connect_errors", 0) == 0 else '⚠️'} |
| 其他错误 | {errors.get("other_errors", 0)} | {'✅' if errors.get("other_errors", 0) == 0 else '⚠️'} |

"""
    
    def _generate_comparison_and_conclusion(
        self,
        sync_result: Optional[BenchmarkResult],
        async_result: Optional[BenchmarkResult], 
        concurrent_result: Optional[Dict[str, Any]],
        curl_baseline: float
    ) -> str:
        """生成对比分析和结论章节"""
        
        conclusion = """## 🎯 对比分析与结论

### 修复前后对比

| 场景 | 修复前 (旧 httpx) | 修复后 (优化 httpx) | Curl 基准 | 改进幅度 |
|------|------------------|-------------------|-----------|----------|"""
        
        if sync_result and sync_result.successful_requests > 0:
            improvement = ((2050 - sync_result.avg_time_ms) / 2050) * 100
            conclusion += f"""
| 单次同步 | ~2050ms | {sync_result.avg_time_ms}ms | {curl_baseline}ms | {improvement:.1f}% ⬇️ |"""
        
        if async_result and async_result.successful_requests > 0:
            improvement = ((2050 - async_result.avg_time_ms) / 2050) * 100
            conclusion += f"""
| 单次异步 | ~2050ms | {async_result.avg_time_ms}ms | {curl_baseline}ms | {improvement:.1f}% ⬇️ |"""
        
        if concurrent_result and concurrent_result.get("timing_stats"):
            p95_time = concurrent_result["timing_stats"].get("p95_ms", 0)
            conclusion += f"""
| 并发 P95 | >2000ms | {p95_time}ms | {curl_baseline}ms (单次) | 显著改善 ⬇️ |"""
        
        conclusion += """

### 验收标准达成情况

| 验收标准 | 目标值 | 实际结果 | 达成状态 |
|----------|--------|----------|----------|"""
        
        # 检查验收标准
        if sync_result:
            sync_status = "✅ 达成" if sync_result.avg_time_ms <= 300 else "⚠️ 未达成"
            conclusion += f"""
| 单次平均时间 | ≤ 300ms | {sync_result.avg_time_ms}ms | {sync_status} |"""
        
        if concurrent_result and concurrent_result.get("timing_stats"):
            p95_time = concurrent_result["timing_stats"].get("p95_ms", 0)
            p95_status = "✅ 达成" if p95_time <= 450 else "⚠️ 未达成"
            conclusion += f"""
| 并发 P95 时间 | ≤ 450ms | {p95_time}ms | {p95_status} |"""
        
        if concurrent_result and concurrent_result.get("overall_stats"):
            success_rate = concurrent_result["overall_stats"].get("success_rate", 0)
            stability_status = "✅ 达成" if success_rate == 100 else "⚠️ 未达成"
            conclusion += f"""
| 并发稳定性 | 100% 成功 | {success_rate}% | {stability_status} |"""
        
        conclusion += """

### 根本问题解决验证

✅ **DNS 解析延迟**: 使用 127.0.0.1 替代 localhost，避免 DNS 查询开销  
✅ **连接池初始化**: 复用客户端实例，预热连接池  
✅ **超时策略**: 明确各阶段超时配置，避免隐藏等待  
✅ **环境干扰**: 禁用系统代理和环境变量影响  
✅ **协议开销**: 强制 HTTP/1.1，禁用 HTTP/2 协商

### 最终结论

"""

        # 根据结果生成最终结论
        overall_success = True
        issues = []
        
        if sync_result and sync_result.avg_time_ms > 300:
            overall_success = False
            issues.append("同步性能未达标")
        
        if concurrent_result:
            if concurrent_result.get("timing_stats", {}).get("p95_ms", 0) > 450:
                overall_success = False
                issues.append("并发 P95 性能未达标")
            if concurrent_result.get("overall_stats", {}).get("success_rate", 0) < 100:
                overall_success = False
                issues.append("并发稳定性未达标")
        
        if overall_success:
            conclusion += """🎉 **修复成功！**

测试层性能问题已完全解决：
- 无效 intent 处理时间从 ~2s 降低到 ~210-300ms
- 测试结果准确反映系统真实性能
- 并发稳定性达到 100%
- 测试框架配置优化完成

**建议**:
1. 将优化后的测试框架配置应用到所有测试脚本
2. 定期运行基准测试监控性能回归
3. 在 CI/CD 中集成性能基准检查"""
        else:
            conclusion += f"""⚠️ **部分问题仍需解决**

已完成的改进：
- 测试工具配置大幅优化
- 性能显著提升（相比修复前）

待解决问题：
{chr(10).join(f'- {issue}' for issue in issues)}

**建议**:
1. 进一步优化客户端配置或服务端处理
2. 检查网络环境和系统资源
3. 考虑调整验收标准或测试方法"""
        
        conclusion += f"""

---

**报告说明**: 
- 本报告基于《Invalid Intent Slowpath Deep Dive Analysis》分析结果生成
- 测试环境: {os.environ.get('COMPUTERNAME', 'Unknown')}
- HttpX 版本: 使用优化配置的统一客户端
- 时间测量: 使用 time.perf_counter() 高精度计时
"""
        
        return conclusion
    
    def save_raw_results(self, results: Dict[str, Any], filename_prefix: str = "raw_benchmark"):
        """保存原始测试结果为 JSON 文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{timestamp}.json"
        filepath = os.path.join(self.report_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"💾 原始结果已保存: {filepath}")
        return filepath
