#!/usr/bin/env python3
# run_all.py 一键执行所有认证测试脚本
"""
Auth模块MVP认证测试脚本执行器

执行完整认证测试流程：
1. 环境设置和清理 (seed.py)
2. 用户注册流程测试 (flow_register.py)
3. 用户登录和受保护资源测试 (flow_login.py)
4. Token刷新测试 (flow_token_refresh.py)
5. 密码重置测试 (flow_reset_password.py)
6. Google OAuth测试 (flow_oauth_google.py，可跳过)

命令行参数：
--base-url URL              API基础URL (默认: http://localhost:8000)
--email-prefix PREFIX       测试邮箱前缀 (默认: test)
--skip-oauth               跳过OAuth测试
--verbose                  详细输出

退出码：
0 - 所有测试通过
1 - 关键测试失败
2 - 环境设置失败
"""

import sys
import argparse
import time
from typing import Dict, Any, Optional

# 从测试模块导入功能
try:
    from .config import BASE_URL, TEST_EMAIL_PREFIX
    from .utils import log_json, generate_test_email
    from .seed import setup_test_environment
    from .flow_register import run_registration_tests
    from .flow_login import run_login_tests
    from .flow_token_refresh import run_token_refresh_tests
    from .flow_reset_password import run_password_reset_tests
    from .flow_oauth_google import run_oauth_tests
except ImportError:
    # 如果相对导入失败，使用绝对导入
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from config import BASE_URL, TEST_EMAIL_PREFIX
    from utils import log_json, generate_test_email
    from seed import setup_test_environment
    from flow_register import run_registration_tests
    from flow_login import run_login_tests
    from flow_token_refresh import run_token_refresh_tests
    from flow_reset_password import run_password_reset_tests
    from flow_oauth_google import run_oauth_tests


def parse_arguments():
    """
    parse_arguments 函数解析命令行参数
    支持自定义API URL、邮箱前缀、跳过OAuth等选项

    返回:
        argparse.Namespace: 解析后的命令行参数
    """
    parser = argparse.ArgumentParser(
        description="Auth模块MVP认证测试脚本执行器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python run_all.py                                    # 运行所有测试
  python run_all.py --base-url http://localhost:3000   # 指定API URL
  python run_all.py --email-prefix mytest              # 自定义邮箱前缀
  python run_all.py --skip-oauth                       # 跳过OAuth测试
  python run_all.py --verbose                          # 详细输出
        """
    )

    parser.add_argument(
        "--base-url",
        default=BASE_URL,
        help=f"API基础URL (默认: {BASE_URL})"
    )

    parser.add_argument(
        "--email-prefix",
        default=TEST_EMAIL_PREFIX,
        help=f"测试邮箱前缀 (默认: {TEST_EMAIL_PREFIX})"
    )

    parser.add_argument(
        "--skip-oauth",
        action="store_true",
        help="跳过OAuth测试"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="详细输出模式"
    )

    return parser.parse_args()


def update_global_config(args):
    """
    update_global_config 函数根据命令行参数更新全局配置
    修改相关模块的全局变量

    参数:
        args: 命令行参数对象
    """
    global BASE_URL, TEST_EMAIL_PREFIX

    # 更新基础URL
    BASE_URL = args.base_url
    # 更新测试邮箱前缀
    TEST_EMAIL_PREFIX = args.email_prefix

    # 更新相关模块的配置
    import config
    config.BASE_URL = BASE_URL
    config.TEST_EMAIL_PREFIX = TEST_EMAIL_PREFIX

    if args.verbose:
        print("更新配置:")
        print(f"  BASE_URL: {BASE_URL}")
        print(f"  TEST_EMAIL_PREFIX: {TEST_EMAIL_PREFIX}")


def run_test_flow(test_name: str, test_function, *args, **kwargs) -> Dict[str, Any]:
    """
    run_test_flow 函数执行单个测试流程
    包装测试函数调用，添加错误处理和日志记录

    参数:
        test_name: 测试名称
        test_function: 测试函数
        *args: 测试函数的位置参数
        **kwargs: 测试函数的关键字参数

    返回:
        dict: 测试结果字典
    """
    result = {
        "test_name": test_name,
        "success": False,
        "duration": 0,
        "error": None
    }

    start_time = time.time()

    try:
        print(f"\n▶ 开始执行: {test_name}")
        log_json({
            "stage": f"start_{test_name}",
            "timestamp": start_time
        })

        # 执行测试函数
        test_result = test_function(*args, **kwargs)

        # 计算执行时间
        end_time = time.time()
        result["duration"] = end_time - start_time
        # 环境设置使用setup_success，其他测试使用overall_success
        if test_name == "environment_setup":
            result["success"] = test_result.get("setup_success", False)
        else:
            result["success"] = test_result.get("overall_success", False)
        result["details"] = test_result

        # 记录测试完成
        log_json({
            "stage": f"complete_{test_name}",
            "success": result["success"],
            "duration": result["duration"],
            "timestamp": end_time
        })

        print(f"✓ {test_name} 执行完成 ({result['duration']:.1f}秒)")
        return result

    except Exception as e:
        end_time = time.time()
        result["duration"] = end_time - start_time
        result["success"] = False
        result["error"] = str(e)

        # 记录测试失败
        log_json({
            "stage": f"error_{test_name}",
            "success": False,
            "error": str(e),
            "duration": result["duration"],
            "timestamp": end_time
        })

        print(f"✗ {test_name} 执行失败: {e}")
        return result


def generate_test_report(all_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    generate_test_report 函数生成完整的测试报告
    汇总所有测试结果，计算统计信息

    参数:
        all_results: 所有测试结果字典

    返回:
        dict: 测试报告字典
    """
    report = {
        "test_suite": "Auth MVP Authentication Tests",
        "timestamp": time.time(),
        "total_duration": 0,
        "summary": {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "skipped_tests": 0
        },
        "test_results": [],
        "recommendations": []
    }

    # 统计各个测试结果
    for test_result in all_results["test_results"]:
        report["total_duration"] += test_result["duration"]
        report["summary"]["total_tests"] += 1

        if test_result["success"]:
            if test_result.get("details", {}).get("tests_skipped", 0) > 0:
                report["summary"]["skipped_tests"] += 1
            else:
                report["summary"]["passed_tests"] += 1
        else:
            report["summary"]["failed_tests"] += 1

        report["test_results"].append({
            "name": test_result["test_name"],
            "success": test_result["success"],
            "duration": test_result["duration"],
            "error": test_result.get("error")
        })

    # 生成建议
    if report["summary"]["failed_tests"] > 0:
        report["recommendations"].append("检查失败的测试用例，修复相关问题")
        report["recommendations"].append("查看详细的错误日志和数据流转记录")

    if report["summary"]["skipped_tests"] > 0:
        report["recommendations"].append("考虑配置跳过的测试环境（如OAuth环境变量）")

    if report["summary"]["passed_tests"] == report["summary"]["total_tests"]:
        report["recommendations"].append("所有测试通过！Auth模块达到MVP上线标准")

    return report


def main():
    """
    main 函数是脚本的主要入口点
    执行完整的测试流程并生成报告
    """
    # 解析命令行参数
    args = parse_arguments()

    print("="*80)
    print("Auth模块MVP认证测试脚本执行器")
    print("="*80)
    print(f"开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API URL: {args.base_url}")
    print(f"邮箱前缀: {args.email_prefix}")
    print(f"跳过OAuth: {'是' if args.skip_oauth else '否'}")
    print()

    # 更新全局配置
    update_global_config(args)

    # 初始化测试状态
    test_state = {
        "test_user_email": None,
        "test_user_password": "TestPass123!",
        "access_token": None,
        "refresh_token": None
    }

    # 存储所有测试结果
    all_results = {
        "command_args": vars(args),
        "test_results": [],
        "overall_success": False
    }

    try:
        # === 1. 环境设置和清理 ===
        print("阶段1: 环境设置和清理")
        env_result = run_test_flow("environment_setup", setup_test_environment)

        if not env_result["success"]:
            print("❌ 环境设置失败，终止测试")
            all_results["test_results"].append(env_result)
            return 2  # 环境设置失败的退出码

        all_results["test_results"].append(env_result)

        # === 2. 用户注册流程测试 ===
        print("\n阶段2: 用户注册流程测试")
        register_result = run_test_flow("user_registration", run_registration_tests)
        all_results["test_results"].append(register_result)

        # 如果注册成功，从注册结果中提取实际创建的用户邮箱
        if register_result["success"] and register_result.get("details"):
            # 尝试从注册结果中提取实际创建的用户邮箱
            registration_details = register_result["details"]
            if "test_email" in registration_details:
                test_state["test_user_email"] = registration_details["test_email"]
            else:
                # 如果无法提取，使用已知的测试用户
                test_state["test_user_email"] = "test_1757412835@test.local"

        # === 3. 用户登录和受保护资源测试 ===
        print("\n阶段3: 用户登录和受保护资源测试")
        # 运行登录测试（使用flow_login.py中的默认用户）
        login_result = run_test_flow(
            "user_login",
            run_login_tests
        )
        all_results["test_results"].append(login_result)

        # 如果登录成功，保存token
        if login_result["success"]:
            login_details = login_result.get("details", {})
            # 尝试从不同路径提取token
            if "access_token" in login_details:
                test_state["access_token"] = login_details["access_token"]
                test_state["refresh_token"] = login_details.get("refresh_token")
            elif "tokens" in login_details:
                tokens = login_details["tokens"]
                test_state["access_token"] = tokens.get("access_token")
                test_state["refresh_token"] = tokens.get("refresh_token")
            else:
                # 如果都找不到，设为None避免KeyError
                test_state["access_token"] = None
                test_state["refresh_token"] = None

        # === 4. Token刷新测试 ===
        print("\n阶段4: Token刷新测试")
        refresh_result = run_test_flow(
            "token_refresh",
            run_token_refresh_tests,
            test_state["access_token"],
            test_state["refresh_token"]
        )
        all_results["test_results"].append(refresh_result)

        # === 5. 密码重置测试 ===
        print("\n阶段5: 密码重置测试")
        reset_result = run_test_flow(
            "password_reset",
            run_password_reset_tests
        )
        all_results["test_results"].append(reset_result)

        # === 6. Google OAuth测试 ===
        if not args.skip_oauth:
            print("\n阶段6: Google OAuth测试")
            oauth_result = run_test_flow("oauth_google", run_oauth_tests)
            all_results["test_results"].append(oauth_result)
        else:
            print("\n阶段6: 跳过Google OAuth测试")
            oauth_result = {
                "test_name": "oauth_google",
                "success": True,
                "duration": 0,
                "skipped": True
            }
            all_results["test_results"].append(oauth_result)

        # === 生成测试报告 ===
        print("\n" + "="*80)
        print("测试执行完成")
        print("="*80)

        # 计算整体结果
        all_passed = all(result["success"] for result in all_results["test_results"])
        all_results["overall_success"] = all_passed

        # 生成详细报告
        report = generate_test_report(all_results)

        # 输出测试摘要
        print("\n测试结果摘要:")
        print(f"  总测试数: {report['summary']['total_tests']}")
        print(f"  通过测试: {report['summary']['passed_tests']}")
        print(f"  失败测试: {report['summary']['failed_tests']}")
        print(f"  跳过测试: {report['summary']['skipped_tests']}")
        print(".1f")
        print(f"  整体结果: {'✅ 通过' if all_passed else '❌ 失败'}")

        # 输出各测试详情
        print("\n详细结果:")
        for i, test_result in enumerate(report["test_results"], 1):
            status = "✅" if test_result["success"] else "❌"
            skipped = " (跳过)" if test_result.get("skipped") else ""
            print(f"  {i}. {test_result['name']}: {status}{skipped} ({test_result['duration']:.1f}s)")
        # 记录最终报告
        log_json({
            "stage": "test_suite_complete",
            "overall_success": all_passed,
            "report": report
        })

        # 输出建议
        if report["recommendations"]:
            print("\n建议:")
            for rec in report["recommendations"]:
                print(f"  • {rec}")

        # 返回适当的退出码
        if all_passed:
            print("\n🎉 所有测试通过！Auth模块达到MVP上线标准")
            return 0
        else:
            print(f"\n⚠️  {report['summary']['failed_tests']} 个测试失败，请检查上述详细结果")
            return 1

    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
        return 1
    except Exception as e:
        print(f"\n\n❌ 测试执行过程中发生未预期的错误: {e}")

        # 记录异常
        log_json({
            "stage": "test_suite_error",
            "error": str(e),
            "timestamp": time.time()
        })

        return 1


if __name__ == "__main__":
    # 执行主函数并使用其返回值作为退出码
    exit_code = main()
    sys.exit(exit_code)
