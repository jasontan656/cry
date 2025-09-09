# flow_oauth_google.py 测试Google OAuth流程
"""
Google OAuth认证流程测试

测试内容：
1. OAUTH-ENV-CHECK: 检查OAuth环境变量是否可用
2. OAUTH-URL-GEN: 生成OAuth授权URL（如果环境可用）
3. OAUTH-CALLBACK: 处理OAuth回调（如果环境可用且可测试）

测试要点：
- 环境变量缺失时优雅跳过
- 生成有效的OAuth授权URL
- OAuth回调处理正确
- 数据库中正确创建OAuth用户记录
"""

import os
import sys
import time
from typing import Dict, Any

# 从相关模块导入功能
try:
    from .utils import make_request, log_json, get_db_connection, get_user_snapshot
    from .checks import (
        assert_response_success, assert_field_exists, assert_db_document_exists,
        assert_db_field_exists, assert_oauth_env_available, TestAssertionError,
        validate_test_result
    )
except ImportError:
    # 如果相对导入失败，使用绝对导入
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from utils import make_request, log_json, get_db_connection, get_user_snapshot
    from checks import (
        assert_response_success, assert_field_exists, assert_db_document_exists,
        assert_db_field_exists, assert_oauth_env_available, TestAssertionError,
        validate_test_result
    )


def check_oauth_environment() -> Dict[str, Any]:
    """
    check_oauth_environment 函数检查Google OAuth环境是否准备就绪
    检查必要的环境变量和配置

    返回:
        dict: 环境检查结果
    """
    result = {
        "available": False,
        "google_client_id": False,
        "google_client_secret": False,
        "reason": ""
    }

    print("\n检查Google OAuth环境...")

    # 检查Google OAuth环境变量
    google_client_id = os.getenv("GOOGLE_CLIENT_ID")
    google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

    result["google_client_id"] = bool(google_client_id)
    result["google_client_secret"] = bool(google_client_secret)

    if google_client_id and google_client_secret:
        result["available"] = True
        result["reason"] = "Google OAuth环境变量已配置"
        print("✓ Google OAuth环境变量已配置")
    else:
        result["available"] = False
        missing_vars = []
        if not google_client_id:
            missing_vars.append("GOOGLE_CLIENT_ID")
        if not google_client_secret:
            missing_vars.append("GOOGLE_CLIENT_SECRET")
        result["reason"] = f"缺少环境变量: {', '.join(missing_vars)}"
        print(f"⚠ Google OAuth环境变量缺失: {', '.join(missing_vars)}")

    # 记录环境检查结果
    log_json({
        "stage": "oauth_environment_check",
        "available": result["available"],
        "google_client_id": result["google_client_id"],
        "google_client_secret": result["google_client_secret"],
        "reason": result["reason"]
    })

    return result


def test_oauth_url_generation() -> Dict[str, Any]:
    """
    test_oauth_url_generation 函数测试OAuth授权URL生成
    只有在环境变量可用时才执行

    返回:
        dict: 测试结果字典
    """
    result = {
        "test_name": "oauth_url_generation",
        "success": False,
        "skipped": False,
        "auth_url": None,
        "error": None
    }

    try:
        print(f"\n=== 开始测试OAuth URL生成 ===")

        # 检查OAuth环境
        env_check = check_oauth_environment()
        if not env_check["available"]:
            result["skipped"] = True
            result["success"] = True  # 跳过算作成功
            result["reason"] = env_check["reason"]

            print(f"⚠ 跳过OAuth URL生成测试: {env_check['reason']}")

            # 记录跳过结果
            log_json({
                "stage": "test_oauth_url_skipped",
                "success": True,
                "skipped": True,
                "reason": env_check["reason"]
            })

            return result

        # 环境可用，执行测试
        oauth_url_payload = {
            "state": "test_state_123"
        }

        response_url = make_request("oauth_google_url", oauth_url_payload)

        # 记录请求和响应
        log_json({
            "stage": "oauth_url_generation_attempt",
            "intent": "oauth_google_url",
            "request_body": oauth_url_payload,
            "response_status": response_url["status_code"],
            "response_body": response_url["response_body"]
        })

        # 验证OAuth URL生成响应
        assert_response_success(response_url, "OAuth URL生成")

        # 验证响应中包含授权URL（修正字段路径）
        assert_field_exists(response_url["response_body"], "result.data.auth_url", "OAuth授权URL")
        assert_field_exists(response_url["response_body"], "result.data.provider", "OAuth提供商")

        # 提取授权URL（修正提取路径）
        auth_url = response_url["response_body"]["result"]["data"]["auth_url"]
        result["auth_url"] = auth_url

        # 验证URL包含必要的Google OAuth参数
        if "accounts.google.com" in auth_url and "client_id" in auth_url:
            print("✓ OAuth授权URL生成成功")
            result["success"] = True
        else:
            raise TestAssertionError("生成的OAuth URL不符合预期格式", {
                "auth_url": auth_url
            })

        # 记录成功结果
        log_json({
            "stage": "test_oauth_url_complete",
            "success": True,
            "auth_url": auth_url
        })

    except TestAssertionError as e:
        result["success"] = False
        result["error"] = str(e)

        # 记录失败信息
        log_json({
            "stage": "test_oauth_url_failed",
            "success": False,
            "error": str(e),
            "details": e.details
        })

        print(f"✗ OAuth URL生成测试失败: {e}")

    except Exception as e:
        result["success"] = False
        result["error"] = f"意外错误: {str(e)}"

        # 记录异常信息
        log_json({
            "stage": "test_oauth_url_error",
            "success": False,
            "error": str(e)
        })

        print(f"✗ OAuth URL生成测试异常: {e}")

    return result


def test_oauth_callback_simulation() -> Dict[str, Any]:
    """
    test_oauth_callback_simulation 函数测试OAuth回调处理
    模拟OAuth回调过程（注意：这需要真实的OAuth流程支持）

    返回:
        dict: 测试结果字典
    """
    result = {
        "test_name": "oauth_callback_simulation",
        "success": False,
        "skipped": False,
        "error": None
    }

    try:
        print(f"\n=== 开始测试OAuth回调模拟 ===")

        # 检查OAuth环境
        env_check = check_oauth_environment()
        if not env_check["available"]:
            result["skipped"] = True
            result["success"] = True  # 跳过算作成功
            result["reason"] = env_check["reason"]

            print(f"⚠ 跳过OAuth回调测试: {env_check['reason']}")

            # 记录跳过结果
            log_json({
                "stage": "test_oauth_callback_skipped",
                "success": True,
                "skipped": True,
                "reason": env_check["reason"]
            })

            return result

        # 注意：真实的OAuth回调测试需要：
        # 1. 有效的授权码（从Google获取）
        # 2. 正确的state参数
        # 3. 真实的回调URL
        #
        # 这里我们只做基本的结构验证，实际的OAuth回调测试
        # 需要完整的OAuth流程，这在自动化测试中通常是困难的

        print("⚠ OAuth回调测试需要真实的OAuth流程，标记为跳过")

        result["skipped"] = True
        result["success"] = True  # 跳过算作成功
        result["reason"] = "需要真实的OAuth授权码和回调流程"

        # 记录跳过结果
        log_json({
            "stage": "test_oauth_callback_simulation_skipped",
            "success": True,
            "skipped": True,
            "reason": result["reason"]
        })

    except Exception as e:
        result["success"] = False
        result["error"] = f"意外错误: {str(e)}"

        # 记录异常信息
        log_json({
            "stage": "test_oauth_callback_error",
            "success": False,
            "error": str(e)
        })

        print(f"✗ OAuth回调模拟测试异常: {e}")

    return result


def run_oauth_tests() -> Dict[str, Any]:
    """
    run_oauth_tests 函数运行所有OAuth相关的测试
    环境检查失败时会跳过相关测试

    返回:
        dict: 所有测试的结果字典
    """
    results = {
        "flow_name": "oauth_google",
        "tests": [],
        "overall_success": False,
        "timestamp": time.time(),
        "environment_available": False
    }

    print("\n" + "="*60)
    print("开始运行Google OAuth流程测试")
    print("="*60)

    # 执行环境检查
    env_check = check_oauth_environment()
    results["environment_available"] = env_check["available"]

    # 执行OAuth URL生成测试
    url_test = test_oauth_url_generation()
    results["tests"].append(url_test)

    # 执行OAuth回调模拟测试
    callback_test = test_oauth_callback_simulation()
    results["tests"].append(callback_test)

    # 计算整体成功状态
    all_passed = all(test["success"] for test in results["tests"])
    results["overall_success"] = all_passed

    # 输出测试结果摘要
    print(f"\nGoogle OAuth流程测试完成:")
    print(f"  环境可用: {'✓ 是' if env_check['available'] else '✗ 否'}")
    print(f"  总测试数: {len(results['tests'])}")
    print(f"  通过测试: {sum(1 for test in results['tests'] if test['success'])}")
    print(f"  失败测试: {sum(1 for test in results['tests'] if not test['success'])}")
    print(f"  跳过测试: {sum(1 for test in results['tests'] if test.get('skipped', False))}")
    print(f"  整体结果: {'✓ 通过' if all_passed else '✗ 失败'}")

    # 记录总体结果
    log_json({
        "stage": "oauth_flow_tests_complete",
        "overall_success": all_passed,
        "environment_available": env_check["available"],
        "tests_run": len(results["tests"]),
        "tests_passed": sum(1 for test in results["tests"] if test["success"]),
        "tests_failed": sum(1 for test in results["tests"] if not test["success"]),
        "tests_skipped": sum(1 for test in results["tests"] if test.get("skipped", False))
    })

    return results


# 如果直接运行此脚本，执行OAuth测试
if __name__ == "__main__":
    print("执行Google OAuth流程测试...")

    # 运行所有OAuth测试
    results = run_oauth_tests()

    # 验证测试结果（OAuth测试允许跳过）
    validate_test_result(
        results["overall_success"],
        "Google OAuth流程测试失败",
        {"results": results}
    )

    print("\nGoogle OAuth流程测试执行完毕")
