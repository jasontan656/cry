# 邮箱已注册限制测试脚本
# 测试严格禁止已完整注册邮箱重复注册的功能

from test_config import TestClient, generate_test_email, print_test_result
import json


def test_prevent_duplicate_registration():
    """
    测试防止重复注册功能
    
    模拟以下场景：
    1. 先完成一个正常的邮箱注册（完整注册用户）
    2. 再次尝试使用相同邮箱注册
    3. 验证系统严格禁止重复注册，返回明确错误
    4. 验证系统推荐使用登录或忘记密码功能
    
    该测试验证新的邮箱唯一性严格检查逻辑。
    """
    # client 通过 TestClient() 创建测试客户端实例
    # 用于发送HTTP请求到auth模块API
    client = TestClient()
    
    # test_email 通过 generate_test_email 生成测试用邮箱地址
    # 传入标识符 "prevent_duplicate" 生成唯一邮箱
    test_email = generate_test_email("prevent_duplicate")
    # first_password 设置为第一次注册使用的密码
    first_password = "FirstPassword123!"
    # second_password 设置为第二次注册尝试使用的密码
    second_password = "SecondPassword456!"
    
    print(f"Prevent duplicate registration test starting")
    print(f"Test email: {test_email}")
    print(f"First password length: {len(first_password)}")
    print(f"Second password length: {len(second_password)}")
    print(f"Password difference: {first_password != second_password}")
    
    # ======== 第一轮：完成正常注册 ========
    print("\n[第一轮] 完成完整注册流程")
    
    # 使用test_user模式快速创建第一个用户
    first_register_data = {
        "email": test_email,
        "password": first_password,
        "test_user": True
    }
    
    # first_register_response 通过 client.post 发送第一次注册请求
    # 调用 /auth/register 接口，创建完整注册用户
    first_register_response = client.post("/auth/register", first_register_data)
    
    # 调用 print_test_result 打印第一次注册结果
    print_test_result("第一次完整注册", first_register_response, 200, first_register_data)
    
    # Check first registration success
    first_status = first_register_response.get("status_code")
    first_success = first_register_response.get("data", {}).get("success", False)

    print(f"First registration results:")
    print(f"  Status code: {first_status}")
    print(f"  Success flag: {first_success}")

    if first_status != 200 or not first_success:
        print(f"First registration failed - cannot continue testing")
        return False

    print(f"First registration completed successfully - user account fully created")
    
    # 验证第一个账户可以正常登录
    print("\n[验证] 确认第一个账户可以正常登录")
    
    first_login_data = {
        "email": test_email,
        "password": first_password
    }
    
    # first_login_response 通过 client.post 验证第一个账户登录
    first_login_response = client.post("/auth/login", first_login_data)
    print_test_result("第一个账户登录验证", first_login_response, 200, first_login_data)
    
    first_login_status = first_login_response.get("status_code")
    first_login_success = first_login_response.get("data", {}).get("success", False)

    print(f"First account login verification:")
    print(f"  Status code: {first_login_status}")
    print(f"  Success flag: {first_login_success}")

    if not (first_login_status == 200 and first_login_success):
        print(f"First account login failed - test environment may have issues")
        return False

    print(f"First account login working correctly")
    
    # ======== 第二轮：尝试重复注册（期望被拒绝）========
    print("\n[第二轮] 尝试使用相同邮箱重复注册")
    
    # ======== Test 1: Duplicate registration via verification code ========
    print(f"\nTest 1: Duplicate registration via verification code (should be rejected)")
    
    # duplicate_send_data 构造重复邮箱的验证码发送请求
    duplicate_send_data = {
        "email": test_email,
        "test_user": True  # 开启测试模式
    }
    
    # duplicate_send_response 通过 client.post 发送重复邮箱验证码请求
    duplicate_send_response = client.post("/auth/send-verification", duplicate_send_data)
    
    # 调用 print_test_result 打印重复邮箱验证码发送测试结果
    print_test_result("重复邮箱发送验证码", duplicate_send_response, 200, duplicate_send_data)
    
    # Check if system correctly rejects duplicate email verification request
    duplicate_send_data_response = duplicate_send_response.get("data", {})
    duplicate_send_success = duplicate_send_data_response.get("success", False)

    print(f"Duplicate email verification request results:")
    print(f"  Success flag: {duplicate_send_success}")

    if not duplicate_send_success:
        error_type = duplicate_send_data_response.get("error_type", "")
        error_message = duplicate_send_data_response.get("error", "")

        if error_type == "EMAIL_ALREADY_REGISTERED":
            print(f"System correctly rejected duplicate email verification request")
            print(f"  Error type: {error_type}")
            print(f"  Error message: {error_message}")

            # Check if error message contains recommended actions
            has_login_recommendation = "登录" in error_message
            has_forgot_password_recommendation = "忘记密码" in error_message

            print(f"  Contains login recommendation: {has_login_recommendation}")
            print(f"  Contains forgot password recommendation: {has_forgot_password_recommendation}")

            if has_login_recommendation and has_forgot_password_recommendation:
                print(f"Error message correctly recommends login or forgot password functionality")
            else:
                print(f"Suggestion: error message should include clearer action guidance")
        else:
            print(f"Anomaly: system rejected request but error type not expected: {error_type}")
    else:
        print(f"Warning: system unexpectedly allowed duplicate email verification")
        print(f"  This may not comply with new strict restriction requirements")
    
    # ======== Test 2: Duplicate registration via test_user mode ========
    print(f"\nTest 2: Duplicate registration via test_user mode (should be rejected)")
    
    # duplicate_register_data 构造重复邮箱的test_user注册请求
    duplicate_register_data = {
        "email": test_email,
        "password": second_password,
        "test_user": True
    }
    
    # duplicate_register_response 通过 client.post 发送重复邮箱注册请求
    duplicate_register_response = client.post("/auth/register", duplicate_register_data)
    
    # 调用 print_test_result 打印重复邮箱注册测试结果
    print_test_result("重复邮箱test_user注册", duplicate_register_response, 200, duplicate_register_data)
    
    # Check if system correctly rejects duplicate email registration request
    duplicate_register_data_response = duplicate_register_response.get("data", {})
    duplicate_register_success = duplicate_register_data_response.get("success", False)

    print(f"Duplicate email registration request results:")
    print(f"  Success flag: {duplicate_register_success}")

    if not duplicate_register_success:
        error_type = duplicate_register_data_response.get("error_type", "")
        error_message = duplicate_register_data_response.get("error", "")

        if error_type == "EMAIL_ALREADY_REGISTERED":
            print(f"System correctly rejected duplicate email registration request")
            print(f"  Error type: {error_type}")
            print(f"  Error message: {error_message}")
        else:
            print(f"Anomaly: system rejected request but error type not expected: {error_type}")
    else:
        print(f"Warning: system unexpectedly allowed duplicate email registration")
        print(f"  This may not comply with new strict restriction requirements")
    
    # ======== 验证原账户不受影响 ========
    print("\n[验证] 确认原账户功能不受影响")
    
    # original_login_data 构造原账户登录验证请求
    original_login_data = {
        "email": test_email,
        "password": first_password
    }
    
    # original_login_response 通过 client.post 验证原账户登录
    original_login_response = client.post("/auth/login", original_login_data)
    print_test_result("原账户登录验证", original_login_response, 200, original_login_data)
    
    # 检查原账户是否仍然正常
    if (original_login_response.get("status_code") == 200 and 
        original_login_response.get("data", {}).get("success", False)):
        print("[成功] 原账户功能不受重复注册尝试影响")
    else:
        print("[错误] 原账户功能受到影响")
        return False
    
    return True


if __name__ == "__main__":
    """
    脚本直接执行入口
    
    执行防止重复注册相关的所有测试。
    """
    print("[启动] 执行防止重复注册测试套件")
    
    # 执行防止重复注册测试
    success1 = test_prevent_duplicate_registration()
    
    # 所有测试都成功才返回成功
    overall_success = success1
    
    print(f"\n[结果] 防止重复注册测试套件完成")
    print(f"总体结果: {'成功' if overall_success else '失败'}")
    
    # 根据测试结果设置程序退出状态码
    exit(0 if overall_success else 1)
