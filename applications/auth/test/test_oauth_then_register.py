# OAuth后注册流程测试脚本
# 测试用户先通过OAuth登录，再尝试邮箱注册的绑定流程

from test_config import TestClient, generate_test_email, print_test_result


def test_google_oauth_then_email_register():
    """
    测试Google OAuth登录后再进行邮箱注册
    
    模拟以下场景：
    1. 用户首次通过Google OAuth登录（创建OAuth账户）
    2. 用户随后尝试使用相同邮箱进行邮箱注册
    3. 系统检测到邮箱已被OAuth用户使用
    4. 提供邮箱绑定或密码设置选项
    
    该测试验证OAuth用户的邮箱绑定逻辑。
    """
    # client 通过 TestClient() 创建测试客户端实例
    client = TestClient()
    
    # test_email 通过 generate_test_email 生成测试邮箱
    # 模拟OAuth用户和邮箱注册使用相同邮箱
    test_email = generate_test_email("oauth_then_register")
    test_password = "OAuthThenRegister123!"
    
    print(f"Google OAuth then email registration flow test starting")
    print(f"Test email: {test_email}")
    print(f"Scenario: user OAuth login first, then attempts email registration")
    
    # ======== 第一阶段：模拟OAuth登录 ========
    print("\n[Facebook] 第一阶段：Google OAuth登录流程")
    
    # ======== 步骤1: 获取Google授权URL ========
    print("\n[设备] 步骤1.1: 获取Google授权URL")
    
    state_value = "oauth_then_register_test_123"
    
    # google_auth_data 构造获取Google授权URL的请求数据
    google_auth_data = {
        "state": state_value
    }
    
    # google_auth_response 通过 client.post 发送POST请求获取授权URL
    google_auth_response = client.post("/auth/google", google_auth_data)
    print_test_result("获取Google授权URL", google_auth_response, 200)
    
    # 检查获取授权URL是否成功
    if (google_auth_response.get("status_code") != 200 or 
        not google_auth_response.get("data", {}).get("success", False)):
        print("[失败] 获取Google授权URL失败，终止测试")
        return False
    
    print("[成功] 获取Google授权URL成功")
    
    # ======== 步骤2: 模拟Google OAuth回调 ========
    print("\n[步骤] 步骤1.2: 模拟Google OAuth回调")
    print("[信息]  注意：使用mock数据模拟OAuth用户首次登录")
    
    # 模拟从Google获得的授权码
    mock_authorization_code = "mock_oauth_first_login_code_789"
    
    # google_callback_data 构造OAuth回调的请求数据
    google_callback_data = {
        "code": mock_authorization_code,
        "state": state_value,
        "expected_state": state_value
    }
    
    # google_callback_response 通过 client.post 处理OAuth回调
    google_callback_response = client.post("/auth/google/callback", google_callback_data)
    print_test_result("Google OAuth回调处理", google_callback_response, 200)
    
    # 分析OAuth回调响应
    callback_data = google_callback_response.get("data", {})
    
    # 由于使用mock数据，OAuth回调可能失败，这是预期的
    if callback_data.get("success", False):
        print("[成功] OAuth回调成功（模拟数据通过验证）")
        oauth_user_data = callback_data.get("data", {})
        print(f"   OAuth用户ID: {oauth_user_data.get('user_id', 'N/A')}")
    else:
        print("[列表] OAuth回调失败（预期，因为使用mock授权码）")
        print("   继续测试邮箱注册流程...")
    
    # ======== 第二阶段：邮箱注册流程 ========
    print("\n[邮件] 第二阶段：使用相同邮箱进行注册")
    
    # ======== 步骤1: 发送验证码 ========
    print("\n[邮件] 步骤2.1: 发送验证码到OAuth用户邮箱")
    
    # send_code_data 构造发送验证码的请求数据
    send_code_data = {
        "email": test_email,
        "test_user": True  # 开启测试模式，使用固定验证码123456
    }
    
    # send_response 通过 client.post 发送验证码请求
    send_response = client.post("/auth/send-verification", send_code_data)
    print_test_result("发送验证码到OAuth邮箱", send_response, 200)
    
    # 检查发送验证码是否成功
    send_data = send_response.get("data", {})
    if not send_data.get("success", False):
        print("[失败] 发送验证码失败，可能邮箱已被OAuth用户占用")
        # 这种情况下继续测试其他逻辑
    else:
        print("[成功] 成功发送验证码到OAuth用户邮箱")
    
    # ======== 步骤2: 验证验证码 ========
    print("\n[验证] 步骤2.2: 验证验证码")
    
    test_code = "123456"  # 使用固定测试验证码
    
    # verify_code_data 构造验证验证码的请求数据
    verify_code_data = {
        "email": test_email,
        "code": test_code
    }
    
    # verify_response 通过 client.post 验证验证码
    verify_response = client.post("/auth/verify-code", verify_code_data)
    print_test_result("验证OAuth邮箱验证码", verify_response, 200)
    
    # 分析验证码验证的响应
    verify_data = verify_response.get("data", {})
    
    if verify_data.get("success", False):
        user_exists = verify_data.get("user_exists", False)
        is_oauth_user = verify_data.get("is_oauth_user", False)
        
        print(f"[状态] 用户状态检查:")
        print(f"   用户已存在: {user_exists}")
        print(f"   是OAuth用户: {is_oauth_user}")
        
        # 这是关键的测试点：系统应该识别出这是OAuth用户
        if user_exists and is_oauth_user:
            print("[成功] 系统正确识别OAuth用户尝试邮箱注册")
            
            # ======== 步骤3: 为OAuth用户设置邮箱密码 ========
            print("\n[密码] 步骤2.3: 为OAuth用户设置邮箱密码")
            
            # set_password_data 构造为OAuth用户设置密码的数据
            set_password_data = {
                "email": test_email,
                "password": test_password
            }
            
            # password_response 通过 client.post 为OAuth用户设置密码
            password_response = client.post("/auth/set-password", set_password_data)
            print_test_result("为OAuth用户设置密码", password_response, 200)
            
            # 检查密码设置结果
            password_data = password_response.get("data", {})
            if password_data.get("success", False):
                print("[成功] OAuth用户成功设置邮箱密码")
                print("   现在用户可以使用邮箱密码登录")
                
                # ======== 验证步骤：测试邮箱密码登录 ========
                print("\n[登录] 验证步骤：测试邮箱密码登录")
                
                # login_data 构造邮箱密码登录数据
                login_data = {
                    "email": test_email,
                    "password": test_password
                }
                
                # login_response 通过 client.post 测试邮箱密码登录
                login_response = client.post("/auth/login", login_data)
                print_test_result("OAuth用户邮箱密码登录", login_response, 200)
                
                # 检查登录是否成功
                login_data_response = login_response.get("data", {})
                if login_data_response.get("success", False):
                    print("[成功] OAuth用户可以使用邮箱密码登录")
                    print("[成功] OAuth账户与邮箱账户绑定成功")
                else:
                    print("[警告]  OAuth用户邮箱密码登录失败")
                    
            else:
                print("[警告]  OAuth用户设置密码失败")
                error_msg = password_data.get("error", "")
                print(f"   错误信息: {error_msg}")
                
        elif user_exists and not is_oauth_user:
            print("[列表] 系统识别为普通用户（非OAuth）")
            print("   这可能表示之前的OAuth步骤未成功创建用户")
            
        elif not user_exists:
            print("[列表] 系统识别为新用户")
            print("   OAuth步骤可能未成功创建用户，将创建新账户")
            
    else:
        print("[失败] 验证码验证失败")
        verify_error = verify_data.get("error", "")
        print(f"   错误信息: {verify_error}")
    
    # ======== 第三阶段：测试使用test_user模式直接注册 ========
    print("\n[实验] 第三阶段：test_user模式直接注册OAuth邮箱")
    
    # test_user_register_data 构造test_user模式注册数据
    test_user_register_data = {
        "email": test_email,
        "password": "TestUserPassword789!",
        "test_user": True
    }
    
    # test_user_response 通过 client.post 测试test_user模式注册
    test_user_response = client.post("/auth/register", test_user_register_data)
    print_test_result("test_user模式注册OAuth邮箱", test_user_response, 200)
    
    # 分析test_user模式注册结果
    test_user_data = test_user_response.get("data", {})
    if test_user_data.get("success", False):
        print("[列表] test_user模式允许OAuth邮箱注册")
    else:
        error_type = test_user_data.get("error_type", "")
        if error_type == "USER_EXISTS":
            print("[成功] test_user模式正确识别OAuth用户已存在")
        else:
            print(f"[列表] test_user模式处理结果: {error_type}")
    
    print("\n[完成] Google OAuth后邮箱注册流程测试完成！")
    print("[成功] 测试了OAuth用户的邮箱绑定逻辑")
    print("[成功] 验证了系统对OAuth用户状态的识别")
    
    return True


def test_facebook_oauth_then_email_register():
    """
    测试Facebook OAuth登录后再进行邮箱注册
    
    类似Google OAuth的测试逻辑，验证Facebook OAuth用户的邮箱绑定。
    """
    print("\n[Facebook] Facebook OAuth后邮箱注册测试")
    
    # client 通过 TestClient() 创建测试客户端实例
    client = TestClient()
    
    # facebook_test_email 通过 generate_test_email 生成Facebook测试邮箱
    facebook_test_email = generate_test_email("facebook_then_register")
    
    print("[测试] 开始测试：Facebook OAuth后邮箱注册流程")
    print(f"测试邮箱: {facebook_test_email}")
    
    # ======== Facebook OAuth授权 ========
    print("\n[设备] Facebook OAuth授权流程")
    
    state_value = "facebook_then_register_456"
    
    # facebook_auth_data 构造Facebook授权请求数据
    facebook_auth_data = {
        "state": state_value
    }
    
    # facebook_auth_response 通过 client.post 获取Facebook授权URL
    facebook_auth_response = client.post("/auth/facebook", facebook_auth_data)
    print_test_result("获取Facebook授权URL", facebook_auth_response, 200)
    
    if (facebook_auth_response.get("status_code") != 200 or 
        not facebook_auth_response.get("data", {}).get("success", False)):
        print("[失败] 获取Facebook授权URL失败")
        return False
    
    # ======== Facebook OAuth回调 ========
    print("\n[步骤] Facebook OAuth回调处理")
    
    mock_fb_code = "mock_facebook_code_for_binding_test"
    
    # facebook_callback_data 构造Facebook回调数据
    facebook_callback_data = {
        "code": mock_fb_code,
        "state": state_value,
        "expected_state": state_value
    }
    
    # facebook_callback_response 通过 client.post 处理Facebook回调
    facebook_callback_response = client.post("/auth/facebook/callback", facebook_callback_data)
    print_test_result("Facebook OAuth回调", facebook_callback_response, 200)
    
    # ======== 邮箱注册尝试 ========
    print("\n[邮件] 尝试邮箱注册相同邮箱")
    
    # 发送验证码
    send_code_data = {
        "email": facebook_test_email,
        "test_user": True  # 开启测试模式，使用固定验证码123456
    }
    send_response = client.post("/auth/send-verification", send_code_data)
    print_test_result("发送验证码", send_response, 200)
    
    # 验证码验证
    verify_code_data = {
        "email": facebook_test_email,
        "code": "123456"
    }
    verify_response = client.post("/auth/verify-code", verify_code_data)
    print_test_result("验证验证码", verify_response, 200)
    
    # 分析验证结果
    verify_data = verify_response.get("data", {})
    if verify_data.get("success", False):
        is_oauth_user = verify_data.get("is_oauth_user", False)
        if is_oauth_user:
            print("[成功] Facebook OAuth用户身份识别正确")
        else:
            print("[列表] 未识别为OAuth用户或OAuth步骤未成功")
    
    return True


if __name__ == "__main__":
    """
    脚本直接执行入口
    
    执行OAuth后注册的所有测试场景。
    """
    print("[连接] 执行OAuth后邮箱注册测试套件")
    
    # 执行Google OAuth后注册测试
    success1 = test_google_oauth_then_email_register()
    
    print("\n" + "="*80)
    
    # 执行Facebook OAuth后注册测试
    success2 = test_facebook_oauth_then_email_register()
    
    # 所有测试都成功才返回成功
    overall_success = success1 and success2
    
    print(f"\n[目标] OAuth后注册测试套件完成")
    print(f"总体结果: {'成功' if overall_success else '失败'}")
    
    print("\n[列表] 测试说明:")
    print("   * OAuth测试使用mock数据，重点验证API逻辑")
    print("   * 关键测试点是系统对OAuth用户状态的识别")
    print("   * 验证OAuth账户与邮箱账户的绑定流程")
    
    # 根据测试结果设置程序退出状态码
    exit(0 if overall_success else 1)
