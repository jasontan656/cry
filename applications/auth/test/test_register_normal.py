# 正常邮箱注册流程测试脚本
# 模拟用户完整的邮箱注册流程：发送验证码 -> 验证验证码 -> 设置密码

from test_config import TestClient, generate_test_email, print_test_result
import time
import json


def test_normal_email_registration():
    """
    测试正常的邮箱注册流程
    
    模拟用户使用邮箱进行完整注册的操作序列：
    1. 发送验证码到邮箱
    2. 验证输入的验证码
    3. 设置用户密码完成注册
    
    该测试验证整个注册流程的连通性和逻辑正确性。
    """
    # client 通过 TestClient() 创建测试客户端实例
    # 用于发送HTTP请求到auth模块API
    client = TestClient()
    
    # test_email 通过 generate_test_email 生成测试用邮箱地址
    # 传入标识符 "normal_register" 生成唯一邮箱
    test_email = generate_test_email("normal_register")
    # test_password 设置为测试用密码字符串
    test_password = "TestPassword123!"
    
    print(f"Email registration flow starting with email: {test_email}")
    print(f"Password length: {len(test_password)}")
    print(f"Email domain: {test_email.split('@')[1]}")
    print(f"Timestamp in email: {test_email.split('_')[-1].split('@')[0]}")
    
    # ======== Step 1: Send verification code ========
    print(f"\nStep 1 data flow - send_code_data construction:")
    
    # send_code_data 构造发送验证码的请求数据字典
    # 包含需要验证的邮箱地址和测试用户标识
    # test_user设为True时生成固定验证码123456，便于测试
    send_code_data = {
        "email": test_email,
        "test_user": True  # 开启测试模式，使用固定验证码123456
    }
    
    # Display request data flow
    print(f"API endpoint target: /auth/send-verification")
    print(f"Request payload keys: {list(send_code_data.keys())}")
    print(f"Test user mode enabled: {send_code_data.get('test_user', False)}")
    print(f"Request data structure: {json.dumps(send_code_data, indent=2, ensure_ascii=False)}")
    
    # send_response 通过 client.post 发送POST请求
    # 调用 /auth/send-verification 接口，传入邮箱数据
    # 得到发送验证码的响应结果
    send_response = client.post("/auth/send-verification", send_code_data)
    
    # Display raw response data flow
    print(f"Raw response keys: {list(send_response.keys()) if isinstance(send_response, dict) else 'N/A'}")
    print(f"Response status code: {send_response.get('status_code', 'N/A')}")
    if send_response.get('data'):
        print(f"Response data keys: {list(send_response['data'].keys()) if isinstance(send_response['data'], dict) else 'N/A'}")
    
    # 调用 print_test_result 打印步骤1的测试结果
    # 传入测试描述、响应数据、期望状态码200和请求数据
    print_test_result("发送验证码", send_response, 200, send_code_data)
    
    # Check verification code sending success
    status_code = send_response.get("status_code")
    success_flag = send_response.get("data", {}).get("success", False)
    print(f"Status code check: {status_code} (expected: 200)")
    print(f"Success flag value: {success_flag}")
    
    if status_code != 200 or not success_flag:
        error_data = send_response.get("data", {})
        print(f"Error detected - status: {status_code}, success: {success_flag}")
        print(f"Error response data: {error_data}")
        return False
    
    # ======== Step 2: Verify verification code ========
    print(f"\nStep 2 data flow - verification code validation:")
    
    # Test mode generates fixed verification code 123456
    test_code = "123456"
    print(f"Test mode verification code: {test_code}")
    print(f"Code validation target email: {test_email}")
    print(f"Code length for validation: {len(test_code)}")
    
    # Verification code data flow setup
    
    # verify_code_data 构造验证验证码的请求数据字典
    # 包含邮箱地址和用户输入的验证码
    verify_code_data = {
        "email": test_email,
        "code": test_code
    }
    
    # verify_response 通过 client.post 发送POST请求
    # 调用 /auth/verify-code 接口，传入验证数据
    # 得到验证码验证的响应结果
    verify_response = client.post("/auth/verify-code", verify_code_data)
    
    # 调用 print_test_result 打印步骤2的测试结果
    print_test_result("验证验证码", verify_response, 200)
    
    # Check verification code validation result
    verify_status = verify_response.get("status_code")
    verify_success = verify_response.get("data", {}).get("success", False)
    print(f"Verification status code: {verify_status}")
    print(f"Verification success flag: {verify_success}")
    
    if verify_status != 200 or not verify_success:
        verify_error_data = verify_response.get("data", {})
        print(f"Verification failed - status: {verify_status}, success: {verify_success}")
        print(f"Verification error data: {verify_error_data}")
        return False
    
    # Extract user status data from verification response
    verify_data = verify_response.get("data", {})
    user_exists = verify_data.get("user_exists", False)
    is_oauth_user = verify_data.get("is_oauth_user", False)
    
    print(f"User status data extraction:")
    print(f"  - user_exists flag: {user_exists}")
    print(f"  - is_oauth_user flag: {is_oauth_user}")
    print(f"  - verification response keys: {list(verify_data.keys())}")
    
    # ======== Step 3: Set password to complete registration ========
    print(f"\nStep 3 data flow - password setup for email: {test_email}")
    
    # set_password_data 构造设置密码的请求数据字典
    # 包含邮箱地址和用户设置的新密码
    set_password_data = {
        "email": test_email,
        "password": test_password
    }
    
    # password_response 通过 client.post 发送POST请求
    # 调用 /auth/set-password 接口，传入密码设置数据
    # 得到密码设置的响应结果
    password_response = client.post("/auth/set-password", set_password_data)
    
    # 调用 print_test_result 打印步骤3的测试结果
    print_test_result("设置密码", password_response, 200)
    
    # Check password setting result
    password_status = password_response.get("status_code")
    password_success = password_response.get("data", {}).get("success", False)
    print(f"Password setting status: {password_status}")
    print(f"Password setting success flag: {password_success}")
    
    if password_status != 200 or not password_success:
        password_error_data = password_response.get("data", {})
        print(f"Password setting failed - status: {password_status}, success: {password_success}")
        print(f"Password error response: {password_error_data}")
        return False
    
    # ======== Validation test: Login attempt ========
    print(f"\nLogin validation for registered account: {test_email}")
    print(f"Password length for login: {len(test_password)}")
    
    # login_data 构造登录测试的请求数据字典
    # 包含刚才注册的邮箱和设置的密码
    login_data = {
        "email": test_email,
        "password": test_password
    }
    
    # login_response 通过 client.post 发送POST请求
    # 调用 /auth/login 接口，传入登录凭证数据
    # 得到登录尝试的响应结果
    login_response = client.post("/auth/login", login_data)
    
    # 调用 print_test_result 打印登录验证的测试结果
    print_test_result("登录验证", login_response, 200)
    
    # Check login success to validate registration completeness
    login_status = login_response.get("status_code")
    login_success = login_response.get("data", {}).get("success", False)
    login_data = login_response.get("data", {})
    
    print(f"Login validation results:")
    print(f"  - Status code: {login_status}")
    print(f"  - Success flag: {login_success}")
    print(f"  - Response data keys: {list(login_data.keys()) if isinstance(login_data, dict) else 'N/A'}")
    
    if login_status != 200 or not login_success:
        print(f"Login validation failed - registration flow incomplete")
        print(f"Login error data: {login_data}")
        return False
    
    print(f"\nEmail registration flow completed successfully")
    print(f"Registration data validation: all steps passed")
    print(f"Final account status: active and loginable")
    print(f"Email registered: {test_email}")
    print(f"Total API calls made: 3 (send-verification, verify-code, set-password, login)")
    
    return True


if __name__ == "__main__":
    """
    脚本直接执行入口
    
    当脚本作为主程序运行时，执行正常邮箱注册流程测试。
    """
    # 执行正常邮箱注册流程测试函数
    success = test_normal_email_registration()
    
    # 根据测试结果设置程序退出状态码
    # 成功时退出码为0，失败时退出码为1
    exit(0 if success else 1)
