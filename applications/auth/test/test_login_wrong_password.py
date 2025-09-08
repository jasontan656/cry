# 邮箱登录失败测试脚本
# 测试用户使用错误密码或不存在邮箱登录时的错误处理

from test_config import TestClient, generate_test_email, print_test_result


def test_login_with_wrong_password():
    """
    测试使用错误密码登录
    
    模拟用户输入错误密码的登录尝试：
    1. 先创建一个有效的测试账户
    2. 使用正确邮箱但错误密码尝试登录
    3. 验证系统正确拒绝登录并返回相应错误信息
    
    该测试验证密码验证逻辑的安全性。
    """
    # client 通过 TestClient() 创建测试客户端实例
    # 用于发送HTTP请求到auth模块API
    client = TestClient()
    
    # test_email 通过 generate_test_email 生成测试用邮箱地址
    # 传入标识符 "wrong_password" 生成唯一邮箱
    test_email = generate_test_email("wrong_password")
    # correct_password 设置为正确的测试密码
    correct_password = "CorrectPassword123!"
    # wrong_password 设置为错误的测试密码
    wrong_password = "WrongPassword456!"
    
    print(f"Wrong password login test starting with email: {test_email}")
    print(f"Correct password length: {len(correct_password)}")
    print(f"Wrong password length: {len(wrong_password)}")
    print(f"Password difference: {correct_password != wrong_password}")
    
    # ======== Preparation phase: Create test account ========
    print(f"\nTest account creation for email: {test_email}")
    
    # register_data 构造test_user模式的注册请求数据
    # 使用test_user=True快速创建账户，跳过验证码流程
    register_data = {
        "email": test_email,
        "password": correct_password,
        "test_user": True
    }
    
    # register_response 通过 client.post 发送注册请求
    # 调用 /auth/register 接口快速创建测试账户
    register_response = client.post("/auth/register", register_data)
    
    # 调用 print_test_result 打印注册结果
    print_test_result("创建测试账户", register_response, 200)
    
    # Check account creation success
    register_status = register_response.get("status_code")
    register_success = register_response.get("data", {}).get("success", False)
    
    print(f"Account creation results:")
    print(f"  - Status code: {register_status}")
    print(f"  - Success flag: {register_success}")
    
    if register_status != 200 or not register_success:
        print(f"Account creation failed - cannot proceed with login test")
        return False
    
    print(f"Test account successfully created")
    
    # ======== Main test: Wrong password login ========
    print(f"\nWrong password login attempt for: {test_email}")
    print(f"Using incorrect password: {wrong_password[:5]}...")
    
    # wrong_login_data 构造错误密码的登录请求数据
    # 包含正确的邮箱但错误的密码
    wrong_login_data = {
        "email": test_email,
        "password": wrong_password
    }
    
    # wrong_response 通过 client.post 发送POST请求
    # 调用 /auth/login 接口，传入错误密码的登录凭证
    # 得到登录尝试的响应结果
    wrong_response = client.post("/auth/login", wrong_login_data)
    
    # 调用 print_test_result 打印错误密码登录测试结果
    # 期望状态码可能是200（业务错误）或401（认证失败）
    print_test_result("错误密码登录", wrong_response, 200)
    
    # Analyze wrong password login response
    wrong_data = wrong_response.get("data", {})
    wrong_status = wrong_response.get("status_code")
    wrong_success = wrong_data.get("success", True)
    
    print(f"Wrong password attempt results:")
    print(f"  - Status code: {wrong_status}")
    print(f"  - Success flag: {wrong_success}")
    
    # Check login should fail
    if wrong_success == False:
        error_message = wrong_data.get("error", "")
        error_type = wrong_data.get("error_type", "")
        
        print(f"System correctly rejected wrong password login")
        print(f"  - Error message: {error_message}")
        print(f"  - Error type: {error_type}")
        
        # Validate error type expectation
        if error_type == "INVALID_CREDENTIALS":
            print(f"  - Error type validation: CORRECT (INVALID_CREDENTIALS)")
        else:
            print(f"  - Error type validation: NON_STANDARD ({error_type})")
        
        # Check for sensitive information leakage
        password_in_error = "password" in error_message.lower()
        print(f"  - Sensitive info leakage check: {'FAIL' if password_in_error else 'PASS'}")
        if password_in_error:
            print(f"  - Warning: error message may contain sensitive information")
    else:
        print(f"System unexpectedly allowed wrong password login - SECURITY ISSUE")
        return False
    
    # ======== Verify correct password still works ========
    print(f"\nCorrect password validation for: {test_email}")
    print(f"Using correct password after wrong attempt")
    
    # correct_login_data 构造正确密码的登录请求数据
    correct_login_data = {
        "email": test_email,
        "password": correct_password
    }
    
    # correct_response 通过 client.post 发送正确密码登录请求
    correct_response = client.post("/auth/login", correct_login_data)
    
    # 调用 print_test_result 打印正确密码验证结果
    print_test_result("正确密码验证", correct_response, 200)
    
    # Check correct password login success
    correct_status = correct_response.get("status_code")
    correct_success = correct_response.get("data", {}).get("success", False)
    
    print(f"Correct password validation results:")
    print(f"  - Status code: {correct_status}")
    print(f"  - Success flag: {correct_success}")
    
    if correct_status == 200 and correct_success:
        print(f"Correct password still works after wrong attempt - PASS")
    else:
        print(f"Correct password failed - possible system issue - FAIL")
        correct_error = correct_response.get("data", {})
        print(f"  - Error data: {correct_error}")
    
    return True


def test_login_with_nonexistent_email():
    """
    测试使用不存在的邮箱登录
    
    验证系统对不存在用户账户的处理逻辑。
    """
    print(f"\nNonexistent email login test")

    # client 通过 TestClient() 创建测试客户端实例
    client = TestClient()

    # nonexistent_email 通过 generate_test_email 生成不存在的邮箱
    # 使用特殊标识确保该邮箱未被注册
    nonexistent_email = generate_test_email("nonexistent_user_999999")
    test_password = "AnyPassword123!"

    print(f"Target nonexistent email: {nonexistent_email}")
    print(f"Email characteristics: domain={nonexistent_email.split('@')[1]}, length={len(nonexistent_email)}")
    
    # nonexistent_login_data 构造不存在邮箱的登录请求数据
    nonexistent_login_data = {
        "email": nonexistent_email,
        "password": test_password
    }
    
    # nonexistent_response 通过 client.post 发送不存在邮箱的登录请求
    nonexistent_response = client.post("/auth/login", nonexistent_login_data)
    
    # 调用 print_test_result 打印不存在邮箱登录测试结果
    print_test_result("不存在邮箱登录", nonexistent_response, 200)
    
    # Analyze nonexistent email login response
    nonexistent_data = nonexistent_response.get("data", {})
    nonexistent_status = nonexistent_response.get("status_code")
    nonexistent_success = nonexistent_data.get("success", True)
    
    print(f"Nonexistent email login results:")
    print(f"  - Status code: {nonexistent_status}")
    print(f"  - Success flag: {nonexistent_success}")
    
    # Check login should fail
    if nonexistent_success == False:
        error_message = nonexistent_data.get("error", "")
        error_type = nonexistent_data.get("error_type", "")
        
        print(f"System correctly rejected nonexistent email login")
        print(f"  - Error message: {error_message}")
        print(f"  - Error type: {error_type}")
        
        # Check error handling for user existence disclosure
        user_existence_disclosed = any(keyword in error_message for keyword in ["not exist", "not found", "does not exist"])
        print(f"  - User existence disclosure: {'YES' if user_existence_disclosed else 'NO'}")
        print(f"  - Security assessment: {'SECURITY_RISK' if user_existence_disclosed else 'SECURE'}")
    else:
        print(f"System unexpectedly allowed nonexistent email login - SECURITY ISSUE")
        return False
    
    return True


def test_login_with_empty_fields():
    """
    测试使用空字段登录
    
    验证系统对缺少必要参数的处理。
    """
    print(f"\nEmpty fields login validation test")

    # client 通过 TestClient() 创建测试客户端实例
    client = TestClient()

    test_email = generate_test_email("empty_field_test")
    test_password = "EmptyFieldTest123!"

    print(f"Test email for validation: {test_email}")
    print(f"Test password length: {len(test_password)}")
    
    # ======== Test empty email ========
    print(f"\nEmpty email field test:")
    
    # empty_email_data 构造空邮箱的登录请求数据
    empty_email_data = {
        "email": "",  # 空邮箱
        "password": test_password
    }
    
    # empty_email_response 通过 client.post 发送空邮箱登录请求
    empty_email_response = client.post("/auth/login", empty_email_data)
    print_test_result("空邮箱登录", empty_email_response, 200)
    
    # Check empty email handling
    empty_email_data_response = empty_email_response.get("data", {})
    empty_email_success = empty_email_data_response.get("success", False)
    empty_email_status = empty_email_response.get("status_code")
    
    print(f"  - Empty email status: {empty_email_status}")
    print(f"  - Empty email success flag: {empty_email_success}")
    print(f"  - Empty email validation: {'PASS' if not empty_email_success else 'FAIL'}")
    
    if empty_email_data_response.get("error"):
        print(f"  - Empty email error: {empty_email_data_response['error']}")
    
    # ======== Test empty password ========
    print(f"\nEmpty password field test:")
    
    # empty_password_data 构造空密码的登录请求数据
    empty_password_data = {
        "email": test_email,
        "password": ""  # 空密码
    }
    
    # empty_password_response 通过 client.post 发送空密码登录请求
    empty_password_response = client.post("/auth/login", empty_password_data)
    print_test_result("空密码登录", empty_password_response, 200)
    
    # Check empty password handling
    empty_password_data_response = empty_password_response.get("data", {})
    empty_password_success = empty_password_data_response.get("success", False)
    empty_password_status = empty_password_response.get("status_code")
    
    print(f"  - Empty password status: {empty_password_status}")
    print(f"  - Empty password success flag: {empty_password_success}")
    print(f"  - Empty password validation: {'PASS' if not empty_password_success else 'FAIL'}")
    
    if empty_password_data_response.get("error"):
        print(f"  - Empty password error: {empty_password_data_response['error']}")
    
    # ======== Test missing fields ========
    print(f"\nMissing fields validation test:")
    
    # missing_email_data 构造缺少邮箱字段的请求数据
    missing_email_data = {
        "password": test_password
        # 缺少email字段
    }
    
    # missing_email_response 通过 client.post 发送缺少邮箱字段的请求
    missing_email_response = client.post("/auth/login", missing_email_data)
    print_test_result("缺少邮箱字段", missing_email_response, 200)
    
    # missing_password_data 构造缺少密码字段的请求数据
    missing_password_data = {
        "email": test_email
        # 缺少password字段
    }
    
    # missing_password_response 通过 client.post 发送缺少密码字段的请求
    missing_password_response = client.post("/auth/login", missing_password_data)
    print_test_result("缺少密码字段", missing_password_response, 200)
    
    return True


def test_login_with_invalid_email_format():
    """
    测试使用无效邮箱格式登录
    
    验证系统对邮箱格式的验证逻辑。
    """
    print(f"\nInvalid email format login test")

    # client 通过 TestClient() 创建测试客户端实例
    client = TestClient()

    test_password = "InvalidFormatTest123!"

    print(f"Test password for invalid format attempts: {test_password}")
    print(f"Password length: {len(test_password)}")
    
    # Define various invalid email formats for testing
    invalid_emails = [
        "invalid-email",           # Missing @ and domain
        "@example.com",           # Missing username part
        "user@",                  # Missing domain part
        "user@@example.com",      # Double @ symbol
        "user@.com",              # Invalid domain format
        "user@example.",          # Missing domain suffix
        "user name@example.com",  # Contains space in username
        "user@exam ple.com",      # Contains space in domain
    ]
    
    print(f"Testing {len(invalid_emails)} invalid email formats:")
    
    # Test each invalid format
    invalid_results = []
    
    for i, invalid_email in enumerate(invalid_emails, 1):
        print(f"\n  Format {i}: '{invalid_email}'")
        
        invalid_login_data = {
            "email": invalid_email,
            "password": test_password
        }
        
        invalid_response = client.post("/auth/login", invalid_login_data)
        invalid_data = invalid_response.get("data", {})
        invalid_success = invalid_data.get("success", False)
        invalid_status = invalid_response.get("status_code")
        
        result = {
            "email": invalid_email,
            "status": invalid_status,
            "success": invalid_success,
            "validation": "PASS" if not invalid_success else "FAIL"
        }
        invalid_results.append(result)
        
        print(f"    - Status: {invalid_status}")
        print(f"    - Success: {invalid_success}")
        print(f"    - Validation: {result['validation']}")
    
    # Summary of invalid email format tests
    passed_count = sum(1 for r in invalid_results if r['validation'] == 'PASS')
    print(f"\nInvalid email format test summary:")
    print(f"  - Total formats tested: {len(invalid_results)}")
    print(f"  - Correctly rejected: {passed_count}")
    print(f"  - Incorrectly accepted: {len(invalid_results) - passed_count}")
    print(f"  - Overall validation rate: {(passed_count/len(invalid_results))*100:.1f}%")
    
    return True


if __name__ == "__main__":
    """
    脚本直接执行入口
    
    执行邮箱登录失败相关的所有测试。
    """
    print(f"Executing email login failure test suite")
    print(f"Suite components: wrong password, nonexistent email, empty fields, invalid formats")
    
    # 执行各项登录失败测试
    success1 = test_login_with_wrong_password()
    
    print("\n" + "="*60)
    success2 = test_login_with_nonexistent_email()
    
    print("\n" + "="*60)
    success3 = test_login_with_empty_fields()
    
    print("\n" + "="*60)
    success4 = test_login_with_invalid_email_format()
    
    # 所有测试都成功才返回成功
    overall_success = success1 and success2 and success3 and success4
    
    print(f"\nLogin failure test suite completion:")
    print(f"Test results summary:")
    print(f"  - Wrong password test: {'PASS' if success1 else 'FAIL'}")
    print(f"  - Nonexistent email test: {'PASS' if success2 else 'FAIL'}")
    print(f"  - Empty fields test: {'PASS' if success3 else 'FAIL'}")
    print(f"  - Invalid format test: {'PASS' if success4 else 'FAIL'}")
    print(f"Overall suite result: {'SUCCESS' if overall_success else 'FAILURE'}")
    print(f"Success rate: {((success1 + success2 + success3 + success4) / 4) * 100:.1f}%")
    
    # 根据测试结果设置程序退出状态码
    exit(0 if overall_success else 1)
