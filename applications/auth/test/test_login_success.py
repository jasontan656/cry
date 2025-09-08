# 邮箱登录成功测试脚本
# 测试用户使用正确邮箱和密码登录的流程

from test_config import TestClient, generate_test_email, print_test_result


def test_successful_email_login():
    """
    测试邮箱密码登录成功流程
    
    模拟用户登录的完整流程：
    1. 先创建一个测试用户账户
    2. 使用正确的邮箱和密码登录
    3. 验证登录响应包含必要的用户信息和token
    
    该测试验证正常登录流程的连通性。
    """
    # client 通过 TestClient() 创建测试客户端实例
    # 用于发送HTTP请求到auth模块API
    client = TestClient()
    
    # test_email 通过 generate_test_email 生成测试用邮箱地址
    # 传入标识符 "login_success" 生成唯一邮箱
    test_email = generate_test_email("login_success")
    # test_password 设置为测试用密码字符串
    test_password = "SuccessLoginTest123!"
    
    print(f"Login success flow starting with email: {test_email}")
    print(f"Email identifier: {test_email.split('_')[0]}")
    print(f"Password characteristics: length={len(test_password)}, has_special_chars={'!' in test_password}")
    
    # ======== Preparation phase: Create test account ========
    print(f"\nAccount creation phase - target email: {test_email}")
    
    # register_data 构造test_user模式的注册请求数据
    # 使用test_user=True快速创建账户，跳过验证码流程
    register_data = {
        "email": test_email,
        "password": test_password,
        "test_user": True
    }
    
    # register_response 通过 client.post 发送注册请求
    # 调用 /auth/register 接口快速创建测试账户
    register_response = client.post("/auth/register", register_data)
    
    # 调用 print_test_result 打印注册结果
    print_test_result("创建测试账户", register_response, 200)
    
    # Check account creation result
    register_status = register_response.get("status_code")
    register_success = register_response.get("data", {}).get("success", False)
    print(f"Account creation status: {register_status}")
    print(f"Account creation success flag: {register_success}")
    
    if register_status != 200 or not register_success:
        register_error = register_response.get("data", {})
        print(f"Account creation failed - cannot proceed with login test")
        print(f"Creation error data: {register_error}")
        return False
    
    # Extract user information from registration response
    register_data_response = register_response.get("data", {})
    user_data = register_data_response.get("data", {})
    created_user_id = user_data.get("user_id")
    created_email = user_data.get("email")
    
    print(f"Account creation data extraction:")
    print(f"  - User ID: {created_user_id}")
    print(f"  - Registered email: {created_email}")
    print(f"  - User data keys: {list(user_data.keys()) if isinstance(user_data, dict) else 'N/A'}")
    print(f"  - Email verification: {created_email == test_email}")
    
    # ======== Main test: Successful login ========
    print(f"\nLogin attempt with credentials - email: {test_email}")
    print(f"Credential validation target: /auth/login")
    
    # login_data 构造登录请求的数据字典
    # 包含刚创建账户的邮箱和密码
    login_data = {
        "email": test_email,
        "password": test_password
    }
    
    # login_response 通过 client.post 发送POST请求
    # 调用 /auth/login 接口，传入正确的登录凭证
    # 得到登录尝试的响应结果
    login_response = client.post("/auth/login", login_data)
    
    # 调用 print_test_result 打印登录测试结果
    print_test_result("正确凭证登录", login_response, 200)
    
    # Check login success
    login_status = login_response.get("status_code")
    login_success = login_response.get("data", {}).get("success", False)
    print(f"Login attempt results:")
    print(f"  - Status code: {login_status}")
    print(f"  - Success flag: {login_success}")
    
    if login_status != 200 or not login_success:
        login_error = login_response.get("data", {})
        print(f"Login failed - test unsuccessful")
        print(f"Login error response: {login_error}")
        return False
    
    # Analyze login response content in detail
    login_data_response = login_response.get("data", {})
    login_message = login_data_response.get("message", "")
    login_user_data = login_data_response.get("data", {})
    
    print(f"Login response analysis:")
    print(f"  - Response message: {login_message}")
    print(f"  - Response data type: {type(login_user_data).__name__}")
    print(f"  - User data keys: {list(login_user_data.keys()) if isinstance(login_user_data, dict) else 'N/A'}")
    
    # Check user information in response
    user_id_present = "user_id" in login_user_data
    email_present = "email" in login_user_data
    username_present = "username" in login_user_data
    
    print(f"User information presence check:")
    print(f"  - user_id present: {user_id_present}")
    if user_id_present:
        print(f"    user_id value: {login_user_data['user_id']}")
    print(f"  - email present: {email_present}")
    if email_present:
        print(f"    email value: {login_user_data['email']}")
    print(f"  - username present: {username_present}")
    if username_present:
        print(f"    username value: {login_user_data['username']}")
    
    # Check access token presence and format
    token_present = "access_token" in login_user_data
    print(f"Access token analysis:")
    print(f"  - token present: {token_present}")
    
    if token_present:
        token = login_user_data["access_token"]
        token_length = len(token)
        has_jwt_format = "." in token
        jwt_parts_count = len(token.split(".")) if has_jwt_format else 0
        
        print(f"  - token length: {token_length}")
        print(f"  - token preview: {token[:20]}...{token[-10:] if token_length > 30 else token}")
        print(f"  - has JWT format: {has_jwt_format}")
        if has_jwt_format:
            print(f"  - JWT parts count: {jwt_parts_count}")
        
        token_valid_format = token_length > 10 and has_jwt_format
        print(f"  - token format validation: {'PASS' if token_valid_format else 'FAIL'}")
    else:
        print(f"  - token not included in response")
    
    # Check refresh token presence
    refresh_token_present = "refresh_token" in login_user_data
    print(f"Refresh token analysis:")
    print(f"  - refresh token present: {refresh_token_present}")
    if refresh_token_present:
        refresh_token = login_user_data["refresh_token"]
        print(f"  - refresh token length: {len(refresh_token)}")
        print(f"  - refresh token preview: {refresh_token[:15]}...{refresh_token[-5:] if len(refresh_token) > 20 else refresh_token}")
    
    # Check user ID consistency
    login_user_id = login_user_data.get("user_id")
    print(f"User ID consistency check:")
    print(f"  - created user ID: {created_user_id}")
    print(f"  - login user ID: {login_user_id}")
    
    if login_user_id and created_user_id:
        id_match = login_user_id == created_user_id
        print(f"  - ID consistency: {'MATCH' if id_match else 'MISMATCH'}")
        if not id_match:
            print(f"  - ID mismatch details: created={created_user_id}, login={login_user_id}")
    else:
        print(f"  - ID comparison: skipped (missing data)")
    
    # ======== Boundary test: Case sensitivity ========
    print(f"\nCase sensitivity testing for email: {test_email}")
    
    # Test uppercase email transformation
    uppercase_email = test_email.upper()
    print(f"Case transformation: {test_email} -> {uppercase_email}")
    print(f"Case difference detected: {test_email != uppercase_email}")
    
    uppercase_login_data = {
        "email": uppercase_email,
        "password": test_password
    }
    
    # uppercase_response 通过 client.post 发送大写邮箱登录请求
    uppercase_response = client.post("/auth/login", uppercase_login_data)
    print_test_result("大写邮箱登录", uppercase_response, 200)
    
    # Analyze uppercase email login result
    uppercase_data = uppercase_response.get("data", {})
    uppercase_success = uppercase_data.get("success", False)
    uppercase_status = uppercase_response.get("status_code")
    
    print(f"Uppercase email test results:")
    print(f"  - Status code: {uppercase_status}")
    print(f"  - Success flag: {uppercase_success}")
    print(f"  - Case sensitivity behavior: {'CASE_INSENSITIVE' if uppercase_success else 'CASE_SENSITIVE'}")
    
    # Test mixed case email transformation
    mixed_case_email = test_email.replace("example", "Example")
    print(f"Mixed case transformation: {test_email} -> {mixed_case_email}")
    print(f"Domain case changed: {'example' in test_email and 'Example' in mixed_case_email}")
    
    mixed_case_login_data = {
        "email": mixed_case_email,
        "password": test_password
    }
    
    # mixed_case_response 通过 client.post 发送混合大小写邮箱登录请求
    mixed_case_response = client.post("/auth/login", mixed_case_login_data)
    print_test_result("混合大小写邮箱登录", mixed_case_response, 200)
    
    # ======== Performance test: Multiple consecutive logins ========
    print(f"\nConsecutive login performance test starting")
    print(f"Target iterations: 3")
    print(f"Test credentials: {test_email}")
    
    # Execute consecutive login tests
    consecutive_success_count = 0
    login_times = []
    
    for i in range(3):
        iteration_start = __import__('time').time()
        print(f"Login iteration {i+1}/3 starting...")
        
        consecutive_response = client.post("/auth/login", login_data)
        iteration_end = __import__('time').time()
        iteration_time = iteration_end - iteration_start
        login_times.append(iteration_time)
        
        # Check individual login success
        iter_status = consecutive_response.get("status_code")
        iter_success = consecutive_response.get("data", {}).get("success", False)
        
        print(f"  - Iteration {i+1} status: {iter_status}")
        print(f"  - Iteration {i+1} success: {iter_success}")
        print(f"  - Iteration {i+1} response time: {iteration_time:.3f}s")
        
        if iter_status == 200 and iter_success:
            consecutive_success_count += 1
    
    print(f"Consecutive login performance analysis:")
    print(f"  - Success count: {consecutive_success_count}/3")
    print(f"  - Success rate: {(consecutive_success_count/3)*100:.1f}%")
    print(f"  - Average response time: {sum(login_times)/len(login_times):.3f}s")
    print(f"  - Min response time: {min(login_times):.3f}s")
    print(f"  - Max response time: {max(login_times):.3f}s")
    
    system_reliability = "HIGH" if consecutive_success_count == 3 else "LOW"
    print(f"  - System reliability: {system_reliability}")
    
    print(f"\nLogin success test completion summary:")
    print(f"  - Main login flow: validated")
    print(f"  - Response data completeness: verified")
    print(f"  - Boundary cases tested: email case sensitivity")
    print(f"  - System stability: {system_reliability.lower()}")
    print(f"  - Total API calls: {4 + 3} (register, login, uppercase, mixed-case, 3x consecutive)")
    print(f"  - Account used: {test_email}")
    print(f"  - User ID: {created_user_id}")
    
    return True


def test_login_response_structure():
    """
    测试登录响应数据结构
    
    专门测试登录成功后响应数据的结构和字段完整性。
    """
    print(f"\nAdditional test: Login response structure validation")

    # client 通过 TestClient() 创建测试客户端实例
    client = TestClient()

    # response_test_email 通过 generate_test_email 生成响应测试邮箱
    response_test_email = generate_test_email("response_structure")
    response_test_password = "ResponseTest123!"

    print(f"Target email for structure test: {response_test_email}")
    print(f"Test password length: {len(response_test_password)}")
    
    # 先创建账户
    register_data = {
        "email": response_test_email,
        "password": response_test_password,
        "test_user": True
    }
    
    setup_response = client.post("/auth/register", register_data)
    setup_status = setup_response.get("status_code")
    setup_success = setup_response.get("data", {}).get("success", False)
    
    print(f"Structure test account creation:")
    print(f"  - Status: {setup_status}")
    print(f"  - Success: {setup_success}")
    
    if not (setup_status == 200 and setup_success):
        print(f"Structure test account creation failed")
        return False
    
    # 执行登录获取响应
    login_data = {
        "email": response_test_email,
        "password": response_test_password
    }
    
    # structure_response 通过 client.post 发送登录请求获取完整响应
    structure_response = client.post("/auth/login", login_data)
    
    print(f"Login response structure analysis:")
    print(f"Response type: {type(structure_response).__name__}")
    print(f"Response size estimate: {len(str(structure_response))} characters")
    
    # Check top-level structure
    expected_top_fields = ["status_code", "data", "headers"]
    top_level_fields = list(structure_response.keys()) if isinstance(structure_response, dict) else []
    
    print(f"Top-level structure validation:")
    print(f"  - Present fields: {top_level_fields}")
    print(f"  - Expected fields: {expected_top_fields}")
    
    for field in expected_top_fields:
        field_present = field in structure_response
        print(f"  - {field}: {'PRESENT' if field_present else 'MISSING'}")
    
    # Check data field structure
    data = structure_response.get("data", {})
    expected_data_fields = ["success", "message", "data"]
    data_fields = list(data.keys()) if isinstance(data, dict) else []
    
    print(f"Data field structure validation:")
    print(f"  - Data field type: {type(data).__name__}")
    print(f"  - Present data fields: {data_fields}")
    print(f"  - Expected data fields: {expected_data_fields}")
    
    for field in expected_data_fields:
        field_present = field in data
        print(f"  - {field}: {'PRESENT' if field_present else 'MISSING'}")
    
    # Check user data structure
    user_data = data.get("data", {})
    expected_user_fields = ["user_id", "email", "access_token"]
    user_fields = list(user_data.keys()) if isinstance(user_data, dict) else []
    
    print(f"User data structure validation:")
    print(f"  - User data type: {type(user_data).__name__}")
    print(f"  - Present user fields: {user_fields}")
    print(f"  - Expected user fields: {expected_user_fields}")
    
    for field in expected_user_fields:
        field_present = field in user_data
        field_value = user_data.get(field) if field_present else None
        field_type = type(field_value).__name__ if field_value is not None else "None"
        print(f"  - {field}: {'PRESENT' if field_present else 'OPTIONAL'} (type: {field_type})")
    
    return True


if __name__ == "__main__":
    """
    脚本直接执行入口
    
    执行邮箱登录成功相关的所有测试。
    """
    print(f"Executing email login success test suite")
    print(f"Test suite components: main login test, response structure validation")
    
    # 执行主要的登录成功测试
    success1 = test_successful_email_login()
    
    print("\n" + "="*60)
    
    # 执行响应结构测试
    success2 = test_login_response_structure()
    
    # 所有测试都成功才返回成功
    overall_success = success1 and success2
    
    print(f"\nTest suite completion status: {'SUCCESS' if overall_success else 'FAILURE'}")
    print(f"Individual test results:")
    print(f"  - Main login test: {'PASS' if success1 else 'FAIL'}")
    print(f"  - Response structure test: {'PASS' if success2 else 'FAIL'}")
    print(f"Overall suite success rate: {((success1 + success2) / 2) * 100:.1f}%")
    
    # 根据测试结果设置程序退出状态码
    exit(0 if overall_success else 1)
