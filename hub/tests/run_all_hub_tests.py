#!/usr/bin/env python3
# run_all_hub_tests.py - Hub模块全面异步测试运行器
# 测试目标：统一运行所有hub异步测试脚本，生成汇总报告

import sys
import os
import json
import time
import asyncio
import subprocess
from typing import Dict, Any, List

# 将项目根目录添加到Python路径中，确保可以导入项目模块
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

async def run_single_test_async(test_script_path: str) -> Dict[str, Any]:
    """
    异步运行单个测试脚本并收集结果
    目的：执行指定的异步测试脚本并解析其输出结果

    参数:
        test_script_path: 测试脚本的文件路径

    返回:
        包含测试结果的字典
    """
    test_name = os.path.basename(test_script_path).replace(".py", "")

    print(f"\n{'='*60}")
    print(f"异步运行测试: {test_name}")
    print(f"{'='*60}")

    start_time = time.time()

    try:
        # 使用asyncio.subprocess异步执行测试脚本
        process = await asyncio.create_subprocess_exec(
            sys.executable, test_script_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=os.path.dirname(os.path.dirname(__file__))  # 在项目根目录运行
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=300.0  # 5分钟超时
            )
            execution_time = time.time() - start_time

            # 解析测试结果
            stdout_lines = stdout.decode().split('\n') if stdout else []
            stderr_lines = stderr.decode().split('\n') if stderr else []

            # 查找最终结果
            final_result = "UNKNOWN"
            for line in reversed(stdout_lines):
                if "FINAL RESULT:" in line:
                    final_result = line.split("FINAL RESULT:")[-1].strip()
                    break

            # 统计异常数量
            exception_count = sum(1 for line in stdout_lines if "EXCEPTION:" in line)

            # 统计测试阶段
            phase_count = sum(1 for line in stdout_lines if "Phase" in line and "===" in line)

            return {
                "test_name": test_name,
                "success": final_result == "TEST COMPLETED" and process.returncode == 0,
                "final_result": final_result,
                "return_code": process.returncode,
                "execution_time": round(execution_time, 2),
                "exception_count": exception_count,
                "phase_count": phase_count,
                "stdout_lines": len(stdout_lines),
                "stderr_lines": len(stderr_lines),
                "has_output": len(stdout_lines) > 0,
                "stdout_sample": stdout_lines[:3] if stdout_lines else [],
                "stderr_sample": stderr_lines[:3] if stderr_lines else [],
                "execution_mode": "async"
            }

        except asyncio.TimeoutError:
            execution_time = time.time() - start_time
            process.kill()
            return {
                "test_name": test_name,
                "success": False,
                "final_result": "TIMEOUT",
                "return_code": -1,
                "execution_time": round(execution_time, 2),
                "exception_count": 0,
                "phase_count": 0,
                "error": "Async test execution timeout (5 minutes)",
                "execution_mode": "async"
            }

    except Exception as e:
        execution_time = time.time() - start_time
        return {
            "test_name": test_name,
            "success": False,
            "final_result": "ERROR",
            "return_code": -1,
            "execution_time": round(execution_time, 2),
            "exception_count": 0,
            "phase_count": 0,
            "error": str(e)
        }

def generate_test_report(test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    生成测试汇总报告
    目的：基于所有测试结果生成详细的汇总分析
    
    参数:
        test_results: 所有测试的结果列表
    
    返回:
        汇总报告字典
    """
    total_tests = len(test_results)
    successful_tests = sum(1 for result in test_results if result.get("success", False))
    failed_tests = total_tests - successful_tests
    
    total_execution_time = sum(result.get("execution_time", 0) for result in test_results)
    total_exceptions = sum(result.get("exception_count", 0) for result in test_results)
    total_phases = sum(result.get("phase_count", 0) for result in test_results)
    
    # 分类测试结果
    passed_tests = [r for r in test_results if r.get("success", False)]
    failed_test_details = [r for r in test_results if not r.get("success", False)]
    
    # 性能分析
    avg_execution_time = total_execution_time / total_tests if total_tests > 0 else 0
    fastest_test = min(test_results, key=lambda x: x.get("execution_time", float('inf')))
    slowest_test = max(test_results, key=lambda x: x.get("execution_time", 0))
    
    return {
        "test_summary": {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": failed_tests,
            "success_rate": round(successful_tests / total_tests * 100, 2) if total_tests > 0 else 0
        },
        "execution_summary": {
            "total_execution_time": round(total_execution_time, 2),
            "average_execution_time": round(avg_execution_time, 2),
            "fastest_test": {
                "name": fastest_test.get("test_name", "unknown"),
                "time": fastest_test.get("execution_time", 0)
            },
            "slowest_test": {
                "name": slowest_test.get("test_name", "unknown"), 
                "time": slowest_test.get("execution_time", 0)
            }
        },
        "quality_metrics": {
            "total_exceptions_handled": total_exceptions,
            "total_test_phases": total_phases,
            "average_exceptions_per_test": round(total_exceptions / total_tests, 1) if total_tests > 0 else 0,
            "average_phases_per_test": round(total_phases / total_tests, 1) if total_tests > 0 else 0
        },
        "passed_tests": [
            {
                "name": test["test_name"],
                "time": test["execution_time"],
                "phases": test["phase_count"]
            }
            for test in passed_tests
        ],
        "failed_tests": [
            {
                "name": test["test_name"],
                "final_result": test.get("final_result", "UNKNOWN"),
                "error": test.get("error", "No specific error"),
                "execution_time": test.get("execution_time", 0)
            }
            for test in failed_test_details
        ],
        "recommendations": generate_recommendations(test_results)
    }

def generate_recommendations(test_results: List[Dict[str, Any]]) -> List[str]:
    """
    生成测试结果建议
    目的：基于测试结果生成改进建议
    
    参数:
        test_results: 所有测试结果列表
    
    返回:
        建议列表
    """
    recommendations = []
    
    total_tests = len(test_results)
    successful_tests = sum(1 for r in test_results if r.get("success", False))
    success_rate = successful_tests / total_tests if total_tests > 0 else 0
    
    # 成功率建议
    if success_rate == 1.0:
        recommendations.append("🎉 所有测试通过！Hub模块架构升级成功，系统稳定性优秀")
    elif success_rate >= 0.8:
        recommendations.append("✅ 大部分测试通过，系统基本稳定，需要修复少量问题")
    elif success_rate >= 0.6:
        recommendations.append("⚠️ 部分测试失败，需要重点关注失败的测试用例")
    else:
        recommendations.append("🚨 多个测试失败，建议全面检查Hub模块实现")
    
    # 性能建议
    avg_time = sum(r.get("execution_time", 0) for r in test_results) / total_tests
    if avg_time > 30:
        recommendations.append("⏱️ 测试执行时间较长，考虑优化性能或并行执行")
    elif avg_time < 5:
        recommendations.append("⚡ 测试执行速度优秀，系统响应快速")
    
    # 异常处理建议
    total_exceptions = sum(r.get("exception_count", 0) for r in test_results)
    if total_exceptions == 0:
        recommendations.append("🛡️ 异常处理完善，系统鲁棒性良好")
    elif total_exceptions > 20:
        recommendations.append("🔧 检测到大量异常，建议优化异常处理机制")
    
    # 失败测试具体建议
    failed_tests = [r for r in test_results if not r.get("success", False)]
    if failed_tests:
        recommendations.append(f"🔍 重点关注失败的测试：{', '.join(t['test_name'] for t in failed_tests)}")
    
    return recommendations

def main():
    """
    主函数：执行所有Hub测试并生成报告
    """
    print("🚀 开始执行Hub模块全面测试套件")
    print(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 定义所有测试脚本
    test_scripts = [
        "hub/test_hub_module_registration.py",
        "hub/test_hub_intent_routing.py", 
        "hub/test_hub_flow_integrity.py",
        "hub/test_hub_exception_handling.py",
        "hub/test_hub_system_integration.py"
    ]
    
    # 验证测试脚本是否存在
    existing_scripts = []
    for script in test_scripts:
        if os.path.exists(script):
            existing_scripts.append(script)
        else:
            print(f"⚠️ 警告：测试脚本不存在 - {script}")
    
    if not existing_scripts:
        print("❌ 错误：未找到任何测试脚本")
        return
    
    print(f"📝 找到 {len(existing_scripts)} 个测试脚本")
    print("REQUEST DATA:")
    print(json.dumps({
        "action": "run_all_hub_tests",
        "total_scripts": len(existing_scripts),
        "test_scripts": [os.path.basename(script) for script in existing_scripts]
    }, indent=2))
    
    # 执行所有测试
    all_test_results = []
    overall_start_time = time.time()
    
    for script_path in existing_scripts:
        # 使用异步测试运行器执行单个测试脚本
        test_result = asyncio.run(run_single_test_async(script_path))
        all_test_results.append(test_result)

        # 显示单个测试的简要结果
        status_icon = "✅" if test_result["success"] else "❌"
        print(f"{status_icon} {test_result['test_name']}: {test_result['final_result']} ({test_result['execution_time']}s)")
    
    overall_execution_time = time.time() - overall_start_time
    
    # 生成汇总报告
    # generate_test_report 通过调用生成详细的测试报告
    summary_report = generate_test_report(all_test_results)
    
    # 输出汇总报告
    print(f"\n{'='*80}")
    print("🏆 Hub模块测试汇总报告")
    print(f"{'='*80}")
    
    print("RESPONSE DATA:")
    print(json.dumps({
        "overall_execution_time": round(overall_execution_time, 2),
        "test_environment": {
            "python_version": sys.version.split()[0],
            "platform": sys.platform,
            "working_directory": os.getcwd()
        },
        "summary_report": summary_report
    }, indent=2))
    
    # 显示建议
    print(f"\n📋 测试建议:")
    for i, recommendation in enumerate(summary_report["recommendations"], 1):
        print(f"{i}. {recommendation}")
    
    # 确定最终结果
    success_rate = summary_report["test_summary"]["success_rate"]
    if success_rate == 100:
        print("\n🎉 FINAL RESULT: ALL TESTS PASSED")
        sys.exit(0)
    elif success_rate >= 80:
        print(f"\n⚠️ FINAL RESULT: MOSTLY PASSED ({success_rate}% success rate)")
        sys.exit(0)
    else:
        print(f"\n❌ FINAL RESULT: TESTS FAILED ({success_rate}% success rate)")
        sys.exit(1)

if __name__ == "__main__":
    main()
