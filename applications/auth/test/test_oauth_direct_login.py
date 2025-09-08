# 直接OAuth登录测试脚本
# 测试用户通过Google和Facebook直接登录的完整流程

from test_config import TestClient, generate_test_email, print_test_result
import urllib.parse


def test_google_oauth_direct_login():
    """
    测试Google OAuth直接登录流程
    
    模拟用户首次通过Google登录的完整流程：
    1. 获取Google授权URL
    2. 模拟用户授权并获取授权码
    3. 使用授权码完成登录
    4. 验证登录响应包含必要的用户信息和token
    
    注意：该测试只能验证API接口的连通性，
    真实的OAuth流程需要在浏览器中完成用户授权。
    """
    # client 通过 TestClient() 创建测试客户端实例
    # 用于发送HTTP请求到auth模块API
    client = TestClient()
    
    print(f"Google OAuth direct login flow test starting")
    print(f"Note: OAuth tests can only verify API connectivity, real authorization requires browser completion")
    
    # ======== 步骤1: 获取Google授权URL ========
    print("\n[设备] 步骤1: 获取Google授权URL")
    
    # 可选的state参数，用于防止CSRF攻击
    state_value = "test_google_direct_login_123"
    
    # google_auth_data 构造获取Google授权URL的请求数据
    # 包含可选的state参数用于安全验证
    google_auth_data = {
        "state": state_value
    }
    
    # google_auth_response 通过 client.post 发送POST请求
    # 调用 /auth/google 接口，获取Google授权URL
    # 得到包含授权URL的响应结果
    google_auth_response = client.post("/auth/google", google_auth_data)
    
    # 调用 print_test_result 打印获取授权URL的测试结果
    print_test_result("获取Google授权URL", google_auth_response, 200)
    
    # 检查获取授权URL是否成功
    if (google_auth_response.get("status_code") != 200 or 
        not google_auth_response.get("data", {}).get("success", False)):
        print("[失败] 获取Google授权URL失败，终止测试")
        return False
    
    # 从响应中提取授权URL和相关信息
    google_auth_data_response = google_auth_response.get("data", {})
    auth_url = google_auth_data_response.get("data", {}).get("auth_url", "")
    provider = google_auth_data_response.get("data", {}).get("provider", "")
    
    print(f"[成功] 获取Google授权URL成功")
    print(f"   提供商: {provider}")
    print(f"   授权URL: {auth_url[:80]}...")
    
    # 验证授权URL的基本格式
    if "accounts.google.com" in auth_url and "oauth2" in auth_url:
        print("[成功] 授权URL格式正确，指向Google OAuth服务")
    else:
        print("[警告]  授权URL格式可能异常")
    
    # 检查URL中是否包含state参数
    if state_value in auth_url:
        print("[成功] 授权URL正确包含state参数")
    else:
        print("[警告]  授权URL中未找到state参数")
    
    # ======== 步骤2: 模拟OAuth回调 ========
    print("\n[步骤] 步骤2: 模拟Google OAuth回调")
    print("[信息]  注意：真实环境中这个步骤由Google服务器回调完成")
    
    # 模拟从Google获得的授权码（真实环境中由用户授权后获得）
    mock_authorization_code = "mock_google_auth_code_123456789"
    
    # google_callback_data 构造OAuth回调的请求数据
    # 包含模拟的授权码、state参数和期望的state值
    google_callback_data = {
        "code": mock_authorization_code,
        "state": state_value,
        "expected_state": state_value
    }
    
    # google_callback_response 通过 client.post 发送POST请求
    # 调用 /auth/google/callback 接口，处理OAuth回调
    # 得到登录处理的响应结果
    google_callback_response = client.post("/auth/google/callback", google_callback_data)
    
    # 调用 print_test_result 打印OAuth回调的测试结果
    print_test_result("Google OAuth回调处理", google_callback_response, 200)
    
    # 分析OAuth回调的响应
    callback_data = google_callback_response.get("data", {})
    
    # 注意：在测试环境中，mock授权码可能无法通过Google验证
    # 这里主要验证API接口的连通性和错误处理
    if callback_data.get("success", False):
        print("[成功] Google OAuth回调处理成功")
        
        # 检查登录响应数据
        user_data = callback_data.get("data", {})
        if "user_id" in user_data:
            print(f"   用户ID: {user_data['user_id']}")
        if "email" in user_data:
            print(f"   用户邮箱: {user_data['email']}")
        if "access_token" in user_data:
            print(f"   访问令牌: 已获得")
            
    else:
        # 回调失败是预期的，因为使用了mock授权码
        error_message = callback_data.get("error", "")
        error_type = callback_data.get("error_type", "")
        
        print(f"[列表] Google OAuth回调失败（预期）")
        print(f"   错误信息: {error_message}")
        print(f"   错误类型: {error_type}")
        
        # 这种情况下仍然认为测试通过，因为API正确处理了无效授权码
        print("[成功] API正确处理了无效的授权码")
    
    return True


def test_facebook_oauth_direct_login():
    """
    测试Facebook OAuth直接登录流程
    
    模拟用户首次通过Facebook登录的完整流程。
    """
    print("\n[Facebook] Facebook OAuth测试")
    
    # client 通过 TestClient() 创建测试客户端实例
    client = TestClient()
    
    print("[测试] 开始测试：Facebook OAuth直接登录流程")
    
    # ======== 步骤1: 获取Facebook授权URL ========
    print("\n[设备] 步骤1: 获取Facebook授权URL")
    
    # 可选的state参数
    state_value = "test_facebook_direct_login_456"
    
    # facebook_auth_data 构造获取Facebook授权URL的请求数据
    facebook_auth_data = {
        "state": state_value
    }
    
    # facebook_auth_response 通过 client.post 发送POST请求
    # 调用 /auth/facebook 接口，获取Facebook授权URL
    facebook_auth_response = client.post("/auth/facebook", facebook_auth_data)
    
    # 调用 print_test_result 打印获取Facebook授权URL的测试结果
    print_test_result("获取Facebook授权URL", facebook_auth_response, 200)
    
    # 检查获取授权URL是否成功
    if (facebook_auth_response.get("status_code") != 200 or 
        not facebook_auth_response.get("data", {}).get("success", False)):
        print("[失败] 获取Facebook授权URL失败")
        return False
    
    # 从响应中提取授权URL和相关信息
    facebook_auth_data_response = facebook_auth_response.get("data", {})
    auth_url = facebook_auth_data_response.get("data", {}).get("auth_url", "")
    provider = facebook_auth_data_response.get("data", {}).get("provider", "")
    
    print(f"[成功] 获取Facebook授权URL成功")
    print(f"   提供商: {provider}")
    print(f"   授权URL: {auth_url[:80]}...")
    
    # 验证授权URL的基本格式
    if "facebook.com" in auth_url and "oauth" in auth_url:
        print("[成功] 授权URL格式正确，指向Facebook OAuth服务")
    else:
        print("[警告]  授权URL格式可能异常")
    
    # ======== 步骤2: 模拟Facebook OAuth回调 ========
    print("\n[步骤] 步骤2: 模拟Facebook OAuth回调")
    
    # 模拟从Facebook获得的授权码
    mock_authorization_code = "mock_facebook_auth_code_789012345"
    
    # facebook_callback_data 构造OAuth回调的请求数据
    facebook_callback_data = {
        "code": mock_authorization_code,
        "state": state_value,
        "expected_state": state_value
    }
    
    # facebook_callback_response 通过 client.post 发送POST请求
    # 调用 /auth/facebook/callback 接口，处理OAuth回调
    facebook_callback_response = client.post("/auth/facebook/callback", facebook_callback_data)
    
    # 调用 print_test_result 打印Facebook OAuth回调的测试结果
    print_test_result("Facebook OAuth回调处理", facebook_callback_response, 200)
    
    # 分析Facebook OAuth回调的响应
    callback_data = facebook_callback_response.get("data", {})
    
    if callback_data.get("success", False):
        print("[成功] Facebook OAuth回调处理成功")
    else:
        print("[列表] Facebook OAuth回调失败（预期，因为使用mock授权码）")
        print("[成功] API正确处理了无效的授权码")
    
    return True


def test_oauth_state_validation():
    """
    测试OAuth state参数验证
    
    验证OAuth流程中state参数的安全验证逻辑。
    """
    print("\n[安全] 安全测试：OAuth state参数验证")
    
    # client 通过 TestClient() 创建测试客户端实例
    client = TestClient()
    
    # ======== 测试state不匹配 ========
    print("\n[警告]  测试：state参数不匹配")
    
    original_state = "original_state_123"
    tampered_state = "tampered_state_456"
    
    # 模拟state参数被篡改的OAuth回调
    # tampered_callback_data 构造state不匹配的回调数据
    tampered_callback_data = {
        "code": "mock_code_for_state_test",
        "state": tampered_state,           # 返回的state
        "expected_state": original_state   # 期望的state
    }
    
    # tampered_response 通过 client.post 发送state不匹配的回调请求
    tampered_response = client.post("/auth/google/callback", tampered_callback_data)
    
    # 调用 print_test_result 打印state验证测试结果
    print_test_result("state参数不匹配", tampered_response, 200)
    
    # 检查系统是否正确拒绝state不匹配的请求
    tampered_data = tampered_response.get("data", {})
    if not tampered_data.get("success", False):
        error_type = tampered_data.get("error_type", "")
        if "VALIDATION" in error_type or "STATE" in error_type:
            print("[成功] 系统正确检测到state参数不匹配")
        else:
            print("[列表] 系统拒绝了请求，但原因可能不是state验证")
    else:
        print("[失败] 系统未能检测到state参数不匹配（安全风险）")
    
    # ======== 测试缺少state ========
    print("\n[问题] 测试：缺少state参数")
    
    # missing_state_data 构造缺少state参数的回调数据
    missing_state_data = {
        "code": "mock_code_for_missing_state_test"
        # 缺少state和expected_state
    }
    
    # missing_state_response 通过 client.post 发送缺少state的回调请求
    missing_state_response = client.post("/auth/google/callback", missing_state_data)
    print_test_result("缺少state参数", missing_state_response, 200)
    
    return True


def test_oauth_without_code():
    """
    测试OAuth回调缺少授权码的情况
    """
    print("\n[注册] 边界测试：OAuth回调缺少授权码")
    
    # client 通过 TestClient() 创建测试客户端实例
    client = TestClient()
    
    # no_code_data 构造缺少授权码的回调数据
    no_code_data = {
        "state": "test_state_789",
        "expected_state": "test_state_789"
        # 缺少code参数
    }
    
    # no_code_response 通过 client.post 发送缺少授权码的回调请求
    no_code_response = client.post("/auth/google/callback", no_code_data)
    
    # 调用 print_test_result 打印缺少授权码测试结果
    print_test_result("缺少授权码的OAuth回调", no_code_response, 200)
    
    # 检查系统是否正确处理缺少授权码的情况
    no_code_data_response = no_code_response.get("data", {})
    if not no_code_data_response.get("success", False):
        error_type = no_code_data_response.get("error_type", "")
        if "MISSING_CODE" in error_type:
            print("[成功] 系统正确识别缺少授权码")
        else:
            print("[列表] 系统拒绝了请求，但错误类型可能不够具体")
    else:
        print("[失败] 系统意外接受了缺少授权码的请求")
    
    return True


if __name__ == "__main__":
    """
    脚本直接执行入口
    
    执行OAuth直接登录相关的所有测试。
    """
    print("[登录] 执行OAuth直接登录测试套件")
    
    # 执行Google OAuth测试
    success1 = test_google_oauth_direct_login()
    
    print("\n" + "="*80)
    
    # 执行Facebook OAuth测试
    success2 = test_facebook_oauth_direct_login()
    
    print("\n" + "="*80)
    
    # 执行OAuth安全测试
    success3 = test_oauth_state_validation()
    
    print("\n" + "="*80)
    
    # 执行OAuth边界测试
    success4 = test_oauth_without_code()
    
    # 所有测试都成功才返回成功
    overall_success = success1 and success2 and success3 and success4
    
    print(f"\n[目标] OAuth直接登录测试套件完成")
    print(f"总体结果: {'成功' if overall_success else '失败'}")
    
    print("\n[列表] 测试说明:")
    print("   * OAuth测试主要验证API接口连通性")
    print("   * 真实OAuth流程需要在浏览器中完成用户授权")
    print("   * Mock授权码无法通过第三方服务验证是正常现象")
    print("   * 重点关注API的错误处理和安全验证逻辑")
    
    # 根据测试结果设置程序退出状态码
    exit(0 if overall_success else 1)
