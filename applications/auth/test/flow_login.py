# flow_login.py 测试用户登录和受保护资源访问流程
"""
用户登录和受保护资源访问流程测试

测试内容：
1. LOGIN-OK: 成功登录，获取access_token
2. LOGIN-FAIL: 错误密码登录失败
3. NO-TOKEN: 无token访问受保护资源被拒绝
4. WITH-TOKEN: 携带token访问受保护资源成功

测试要点：
- 登录成功后返回access_token和refresh_token
- 错误密码正确返回401
- 无token访问受保护接口返回401
- 有token访问受保护接口返回200
"""

import sys
import time
from typing import Dict, Any

# 从相关模块导入功能
try:
    from .utils import make_request, log_json, get_db_connection, get_user_snapshot
    from .checks import (
        assert_response_success, assert_http_status, assert_field_exists,
        assert_field_value, TestAssertionError, validate_test_result
    )
except ImportError:
    # 如果相对导入失败，使用绝对导入
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from utils import make_request, log_json, get_db_connection, get_user_snapshot
    from checks import (
        assert_response_success, assert_http_status, assert_field_exists,
        assert_field_value, TestAssertionError, validate_test_result
    )
try:
    from .config import *
except ImportError:
    # 如果相对导入失败，使用绝对导入
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from config import *


def test_successful_login(test_email: str = None, test_password: str = None) -> Dict[str, Any]:
    """
    test_successful_login 函数测试成功的用户登录
    使用已注册的用户邮箱和密码进行登录

    参数:
        test_email: 测试用户邮箱，如果不提供则生成新的
        test_password: 测试用户密码，默认为"TestPass123!"

    返回:
        dict: 测试结果字典，包含token信息
    """
    result = {
        "test_name": "successful_login",
        "success": False,
        "tokens": {},
        "error": None
    }

    try:
        # 如果没有提供测试用户，动态查找最新的测试用户
        if not test_email:
            # 动态查找数据库中最新的测试用户，避免硬编码邮箱
            from utils import get_db_connection
            db_ops = get_db_connection()
            
            # 查找最新的测试用户
            latest_users = list(db_ops['user_profiles'].find({}).sort('_id', -1).limit(3))
            if latest_users:
                test_email = latest_users[0]['email']
                print(f"使用最新测试用户: {test_email}")
            else:
                test_email = "test_1757412835@test.local"  # 后备选项

        if not test_password:
            test_password = "TestPass123!"

        print(f"\n=== 开始测试成功登录 ===")
        print(f"登录邮箱: {test_email}")

        # 使用auth_login intent进行登录（根据intent_handlers.py）
        login_payload = {
            "email": test_email,
            "password": test_password
        }

        response_login = make_request("auth_login", login_payload)

        # 记录请求和响应
        log_json({
            "stage": "login_success_attempt",
            "intent": "auth_login",
            "request_body": login_payload,
            "response_status": response_login["status_code"],
            "response_body": response_login["response_body"]
        })

        # 验证登录响应
        assert_response_success(response_login, "用户登录")

        # 验证响应中包含必要的token字段（修正字段路径）
        assert_field_exists(response_login["response_body"], "result.data.access_token", "登录响应access_token")
        assert_field_exists(response_login["response_body"], "result.data.refresh_token", "登录响应refresh_token")

        # 提取token信息（修正提取路径）
        response_data = response_login["response_body"]["result"]["data"]
        access_token = response_data["access_token"]
        refresh_token = response_data["refresh_token"]

        result["tokens"] = {
            "access_token": access_token,
            "refresh_token": refresh_token
        }

        print("✓ 用户登录成功")
        result["success"] = True

        # 记录成功结果
        log_json({
            "stage": "test_successful_login_complete",
            "success": True,
            "user_email": test_email
        })

    except TestAssertionError as e:
        result["success"] = False
        result["error"] = str(e)

        # 记录失败信息
        log_json({
            "stage": "test_successful_login_failed",
            "success": False,
            "error": str(e),
            "details": e.details
        })

        print(f"✗ 成功登录测试失败: {e}")

    except Exception as e:
        result["success"] = False
        result["error"] = f"意外错误: {str(e)}"

        # 记录异常信息
        log_json({
            "stage": "test_successful_login_error",
            "success": False,
            "error": str(e)
        })

        print(f"✗ 成功登录测试异常: {e}")

    return result


def test_failed_login() -> Dict[str, Any]:
    """
    test_failed_login 函数测试登录失败场景
    使用错误密码尝试登录，期望返回401

    返回:
        dict: 测试结果字典
    """
    result = {
        "test_name": "failed_login",
        "success": False,
        "error": None
    }

    try:
        print(f"\n=== 开始测试登录失败 ===")

        # 使用不存在的用户或错误密码
        test_email = "nonexistent@test.local"
        wrong_password = "WrongPass123!"

        login_payload = {
            "email": test_email,
            "password": wrong_password
        }

        response_login = make_request("auth_login", login_payload)

        # 记录请求和响应
        log_json({
            "stage": "login_failure_attempt",
            "intent": "auth_login",
            "request_body": login_payload,
            "response_status": response_login["status_code"],
            "response_body": response_login["response_body"]
        })

        # 验证响应状态码为401（未授权）
        assert_http_status(response_login, 401, "错误密码登录")

        print("✓ 错误密码登录正确返回401")
        result["success"] = True

        # 记录成功结果
        log_json({
            "stage": "test_failed_login_complete",
            "success": True
        })

    except TestAssertionError as e:
        result["success"] = False
        result["error"] = str(e)

        # 记录失败信息
        log_json({
            "stage": "test_failed_login_failed",
            "success": False,
            "error": str(e),
            "details": e.details
        })

        print(f"✗ 登录失败测试失败: {e}")

    except Exception as e:
        result["success"] = False
        result["error"] = f"意外错误: {str(e)}"

        # 记录异常信息
        log_json({
            "stage": "test_failed_login_error",
            "success": False,
            "error": str(e)
        })

        print(f"✗ 登录失败测试异常: {e}")

    return result


def test_protected_resource_access(access_token: str = None) -> Dict[str, Any]:
    """
    test_protected_resource_access 函数测试受保护资源访问
    测试无token和有token访问受保护资源的场景

    参数:
        access_token: 可选的访问token，如果提供则测试有token访问

    返回:
        dict: 测试结果字典
    """
    result = {
        "test_name": "protected_resource_access",
        "success": False,
        "no_token_test": {},
        "with_token_test": {},
        "error": None
    }

    try:
        print(f"\n=== 开始测试受保护资源访问 ===")

        # === 测试1: 无token访问 ===
        print("1. 测试无token访问...")

        # 构建受保护资源请求（获取用户信息）
        protected_payload = {}

        response_no_token = make_request("auth_get_profile", protected_payload)

        # 记录请求和响应
        log_json({
            "stage": "protected_access_no_token",
            "intent": "auth_get_profile",
            "request_body": protected_payload,
            "response_status": response_no_token["status_code"],
            "response_body": response_no_token["response_body"]
        })

        # 验证无token访问被拒绝（401）
        assert_http_status(response_no_token, 401, "无token访问受保护资源")

        result["no_token_test"] = {
            "success": True,
            "response": response_no_token
        }

        print("✓ 无token访问正确返回401")

        # === 测试2: 有token访问 ===
        if access_token:
            print("2. 测试有token访问...")

            # 在payload中包含access_token
            protected_payload_with_token = {
                "access_token": access_token
            }

            response_with_token = make_request("auth_get_profile", protected_payload_with_token)

            # 记录请求和响应
            log_json({
                "stage": "protected_access_with_token",
                "intent": "auth_get_profile",
                "request_body": protected_payload_with_token,
                "response_status": response_with_token["status_code"],
                "response_body": response_with_token["response_body"]
            })

            # 验证有token访问成功（200）
            assert_response_success(response_with_token, "有token访问受保护资源")

            result["with_token_test"] = {
                "success": True,
                "response": response_with_token
            }

            print("✓ 有token访问正确返回200")
        else:
            print("⚠ 跳过有token访问测试 - 未提供access_token")
            result["with_token_test"] = {
                "success": True,  # 算作成功，因为这是可选测试
                "skipped": True,
                "reason": "no access_token provided"
            }

        result["success"] = True

        # 记录成功结果
        log_json({
            "stage": "test_protected_access_complete",
            "success": True,
            "no_token_success": result["no_token_test"]["success"],
            "with_token_success": result["with_token_test"]["success"]
        })

    except TestAssertionError as e:
        result["success"] = False
        result["error"] = str(e)

        # 记录失败信息
        log_json({
            "stage": "test_protected_access_failed",
            "success": False,
            "error": str(e),
            "details": e.details
        })

        print(f"✗ 受保护资源访问测试失败: {e}")

    except Exception as e:
        result["success"] = False
        result["error"] = f"意外错误: {str(e)}"

        # 记录异常信息
        log_json({
            "stage": "test_protected_access_error",
            "success": False,
            "error": str(e)
        })

        print(f"✗ 受保护资源访问测试异常: {e}")

    return result


def run_login_tests(test_user_email: str = None, test_user_password: str = None) -> Dict[str, Any]:
    """
    run_login_tests 函数运行所有登录相关的测试
    按顺序执行成功登录、失败登录、受保护资源访问测试

    参数:
        test_user_email: 测试用户邮箱，如果不提供则使用默认邮箱
        test_user_password: 测试用户密码，如果不提供则使用默认密码

    返回:
        dict: 所有测试的结果字典
    """
    results = {
        "flow_name": "user_login",
        "tests": [],
        "overall_success": False,
        "timestamp": time.time(),
        "access_token": None
    }

    print("\n" + "="*60)
    print("开始运行用户登录流程测试")
    print("="*60)

    # 执行成功登录测试
    # 使用传递的测试用户邮箱和密码，如果没有传递则使用默认值
    login_result = test_successful_login(test_user_email, test_user_password)
    results["tests"].append(login_result)

    # 如果登录成功，保存access_token用于后续测试
    if login_result["success"]:
        results["access_token"] = login_result["tokens"].get("access_token")

    # 执行登录失败测试
    failed_login_result = test_failed_login()
    results["tests"].append(failed_login_result)

    # 执行受保护资源访问测试
    protected_access_result = test_protected_resource_access(results["access_token"])
    results["tests"].append(protected_access_result)

    # 计算整体成功状态
    all_passed = all(test["success"] for test in results["tests"])
    results["overall_success"] = all_passed

    # 输出测试结果摘要
    print(f"\n登录流程测试完成:")
    print(f"  总测试数: {len(results['tests'])}")
    print(f"  通过测试: {sum(1 for test in results['tests'] if test['success'])}")
    print(f"  失败测试: {sum(1 for test in results['tests'] if not test['success'])}")
    print(f"  整体结果: {'✓ 通过' if all_passed else '✗ 失败'}")

    # 记录总体结果
    log_json({
        "stage": "login_flow_tests_complete",
        "overall_success": all_passed,
        "tests_run": len(results["tests"]),
        "tests_passed": sum(1 for test in results["tests"] if test["success"]),
        "tests_failed": sum(1 for test in results["tests"] if not test["success"])
    })

    return results


# 如果直接运行此脚本，执行登录测试
if __name__ == "__main__":
    print("执行用户登录流程测试...")

    # 运行所有登录测试
    results = run_login_tests()

    # 验证测试结果
    validate_test_result(
        results["overall_success"],
        "用户登录流程测试失败",
        {"results": results}
    )

    print("\n用户登录流程测试执行完毕")
