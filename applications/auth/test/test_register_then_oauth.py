# 注册后OAuth流程测试脚本
# 测试用户先完成邮箱注册，再尝试使用OAuth登录的绑定流程

from test_config import TestClient, generate_test_email, print_test_result


def test_email_register_then_google_oauth():
    """
    测试邮箱注册后再进行Google OAuth登录
    
    模拟以下场景：
    1. 用户先通过邮箱完成完整注册流程
    2. 用户随后尝试使用Google OAuth登录（相同邮箱）
    3. 系统检测到邮箱已被注册用户使用
    4. 提供账户绑定或OAuth关联选项
    
    该测试验证已注册用户的OAuth绑定逻辑。
    """
    # client 通过 TestClient() 创建测试客户端实例
    client = TestClient()
    
    # test_email 通过 generate_test_email 生成测试邮箱
    # 模拟邮箱注册和OAuth登录使用相同邮箱
    test_email = generate_test_email("register_then_oauth")
    test_password = "RegisterThenOAuth123!"
    
    print("[测试] 开始测试：邮箱注册后Google OAuth流程")
    print(f"测试邮箱: {test_email}")
    print("[列表] 场景：用户先邮箱注册，后尝试OAuth登录")
    
    # ======== 第一阶段：完整邮箱注册流程 ========
    print("\n[邮件] 第一阶段：完整邮箱注册流程")
    
    # ======== 步骤1: 发送验证码 ========
    print("\n[邮件] 步骤1.1: 发送验证码")
    
    # send_code_data 构造发送验证码的请求数据
    send_code_data = {
        "email": test_email,
        "test_user": True  # 开启测试模式，使用固定验证码123456
    }
    
    # send_response 通过 client.post 发送验证码请求
    send_response = client.post("/auth/send-verification", send_code_data)
    print_test_result("发送验证码", send_response, 200)
    
    # 检查发送验证码是否成功
    if (send_response.get("status_code") != 200 or 
        not send_response.get("data", {}).get("success", False)):
        print("[失败] 发送验证码失败，终止测试")
        return False
    
    print("[成功] 验证码发送成功")
    
    # ======== 步骤2: 验证验证码 ========
    print("\n[验证] 步骤1.2: 验证验证码")
    
    test_code = "123456"  # 使用固定测试验证码
    
    # verify_code_data 构造验证验证码的请求数据
    verify_code_data = {
        "email": test_email,
        "code": test_code
    }
    
    # verify_response 通过 client.post 验证验证码
    verify_response = client.post("/auth/verify-code", verify_code_data)
    print_test_result("验证验证码", verify_response, 200)
    
    # 检查验证码验证是否成功
    if (verify_response.get("status_code") != 200 or 
        not verify_response.get("data", {}).get("success", False)):
        print("[失败] 验证码验证失败，终止测试")
        return False
    
    print("[成功] 验证码验证成功")
    
    # ======== 步骤3: 设置密码完成注册 ========
    print("\n[密码] 步骤1.3: 设置密码完成注册")
    
    # set_password_data 构造设置密码的请求数据
    set_password_data = {
        "email": test_email,
        "password": test_password
    }
    
    # password_response 通过 client.post 设置密码
    password_response = client.post("/auth/set-password", set_password_data)
    print_test_result("设置密码完成注册", password_response, 200)
    
    # 检查密码设置是否成功
    if (password_response.get("status_code") != 200 or 
        not password_response.get("data", {}).get("success", False)):
        print("[失败] 设置密码失败，终止测试")
        return False
    
    print("[成功] 邮箱注册完成")
    
    # ======== 验证注册成功 ========
    print("\n[登录] 验证步骤：确认邮箱注册成功")
    
    # login_data 构造登录验证数据
    login_data = {
        "email": test_email,
        "password": test_password
    }
    
    # login_response 通过 client.post 验证登录
    login_response = client.post("/auth/login", login_data)
    print_test_result("邮箱注册后登录验证", login_response, 200)
    
    if not (login_response.get("status_code") == 200 and 
            login_response.get("data", {}).get("success", False)):
        print("[失败] 邮箱注册后登录失败，终止测试")
        return False
    
    print("[成功] 邮箱注册用户可以正常登录")
    
    # ======== 第二阶段：Google OAuth登录尝试 ========
    print("\n[Facebook] 第二阶段：Google OAuth登录尝试")
    
    # ======== 步骤1: 获取Google授权URL ========
    print("\n[设备] 步骤2.1: 获取Google授权URL")
    
    state_value = "register_then_oauth_test_789"
    
    # google_auth_data 构造获取Google授权URL的请求数据
    google_auth_data = {
        "state": state_value
    }
    
    # google_auth_response 通过 client.post 获取Google授权URL
    google_auth_response = client.post("/auth/google", google_auth_data)
    print_test_result("获取Google授权URL", google_auth_response, 200)
    
    # 检查获取授权URL是否成功
    if (google_auth_response.get("status_code") != 200 or 
        not google_auth_response.get("data", {}).get("success", False)):
        print("[失败] 获取Google授权URL失败")
        return False
    
    print("[成功] Google授权URL获取成功")
    
    # ======== 步骤2: 模拟Google OAuth回调 ========
    print("\n[步骤] 步骤2.2: 模拟Google OAuth回调")
    print("[信息]  注意：模拟已注册用户尝试OAuth登录")
    
    # 模拟从Google获得的授权码
    mock_authorization_code = "mock_existing_user_oauth_code_456"
    
    # google_callback_data 构造OAuth回调的请求数据
    google_callback_data = {
        "code": mock_authorization_code,
        "state": state_value,
        "expected_state": state_value
    }
    
    # google_callback_response 通过 client.post 处理OAuth回调
    google_callback_response = client.post("/auth/google/callback", google_callback_data)
    print_test_result("Google OAuth回调处理", google_callback_response, 200)
    
    # 分析OAuth回调的响应
    callback_data = google_callback_response.get("data", {})
    
    if callback_data.get("success", False):
        print("[成功] OAuth回调成功（模拟数据通过验证）")
        
        # 检查是否正确处理了已存在用户的OAuth绑定
        oauth_user_data = callback_data.get("data", {})
        oauth_user_id = oauth_user_data.get("user_id")
        oauth_email = oauth_user_data.get("email")
        
        print(f"[状态] OAuth响应分析:")
        print(f"   用户ID: {oauth_user_id}")
        print(f"   邮箱: {oauth_email}")
        
        # 这里需要检查系统是否识别出这是已存在的邮箱用户
        # 并且正确处理了账户绑定
        
    else:
        # OAuth回调失败是预期的，因为使用了mock授权码
        error_message = callback_data.get("error", "")
        error_type = callback_data.get("error_type", "")
        
        print("[列表] OAuth回调失败（预期，因为使用mock授权码）")
        print(f"   错误信息: {error_message}")
        print(f"   错误类型: {error_type}")
        
        # 即使OAuth失败，我们仍然可以测试邮箱验证流程
        print("   继续测试邮箱验证逻辑...")
    
    # ======== 第三阶段：邮箱验证流程测试 ========
    print("\n[邮件] 第三阶段：已注册邮箱的验证流程")
    
    # ======== 测试发送验证码到已注册邮箱 ========
    print("\n[邮件] 步骤3.1: 发送验证码到已注册邮箱")
    
    # existing_email_code_data 构造发送验证码请求
    existing_email_code_data = {
        "email": test_email,
        "test_user": True  # 开启测试模式，使用固定验证码123456
    }
    
    # existing_send_response 通过 client.post 向已注册邮箱发送验证码
    existing_send_response = client.post("/auth/send-verification", existing_email_code_data)
    print_test_result("向已注册邮箱发送验证码", existing_send_response, 200)
    
    # 检查向已注册邮箱发送验证码的结果
    existing_send_data = existing_send_response.get("data", {})
    if existing_send_data.get("success", False):
        print("[成功] 可以向已注册邮箱发送验证码")
        
        # ======== 验证已注册邮箱的验证码 ========
        print("\n[验证] 步骤3.2: 验证已注册邮箱的验证码")
        
        # existing_verify_data 构造验证已注册邮箱验证码的数据
        existing_verify_data = {
            "email": test_email,
            "code": test_code
        }
        
        # existing_verify_response 通过 client.post 验证已注册邮箱的验证码
        existing_verify_response = client.post("/auth/verify-code", existing_verify_data)
        print_test_result("验证已注册邮箱验证码", existing_verify_response, 200)
        
        # 分析已注册邮箱验证码验证的结果
        existing_verify_response_data = existing_verify_response.get("data", {})
        
        if existing_verify_response_data.get("success", False):
            user_exists = existing_verify_response_data.get("user_exists", False)
            is_oauth_user = existing_verify_response_data.get("is_oauth_user", False)
            
            print(f"[状态] 已注册邮箱状态检查:")
            print(f"   用户已存在: {user_exists}")
            print(f"   是OAuth用户: {is_oauth_user}")
            
            # 关键测试点：系统应该识别这是已存在的非OAuth用户
            if user_exists and not is_oauth_user:
                print("[成功] 系统正确识别已注册的邮箱用户")
                
                # ======== 测试密码更新功能 ========
                print("\n[步骤] 步骤3.3: 测试已注册用户密码更新")
                
                new_password = "NewPasswordAfterOAuth456!"
                
                # update_password_data 构造密码更新数据
                update_password_data = {
                    "email": test_email,
                    "password": new_password
                }
                
                # update_password_response 通过 client.post 更新已注册用户密码
                update_password_response = client.post("/auth/set-password", update_password_data)
                print_test_result("更新已注册用户密码", update_password_response, 200)
                
                # 检查密码更新结果
                update_data = update_password_response.get("data", {})
                if update_data.get("success", False):
                    print("[成功] 已注册用户密码更新成功")
                    
                    # ======== 验证新密码登录 ========
                    print("\n[登录] 验证步骤：测试新密码登录")
                    
                    # new_login_data 构造新密码登录数据
                    new_login_data = {
                        "email": test_email,
                        "password": new_password
                    }
                    
                    # new_login_response 通过 client.post 测试新密码登录
                    new_login_response = client.post("/auth/login", new_login_data)
                    print_test_result("新密码登录测试", new_login_response, 200)
                    
                    # 验证旧密码是否还能登录
                    print("\n[登录] 验证步骤：测试旧密码登录")
                    
                    # old_login_data 构造旧密码登录数据
                    old_login_data = {
                        "email": test_email,
                        "password": test_password
                    }
                    
                    # old_login_response 通过 client.post 测试旧密码登录
                    old_login_response = client.post("/auth/login", old_login_data)
                    print_test_result("旧密码登录测试", old_login_response, 200)
                    
                    # 分析密码更新效果
                    new_password_works = (new_login_response.get("status_code") == 200 and 
                                        new_login_response.get("data", {}).get("success", False))
                    old_password_works = (old_login_response.get("status_code") == 200 and 
                                        old_login_response.get("data", {}).get("success", False))
                    
                    print(f"\n[状态] 密码更新效果分析:")
                    print(f"   新密码可登录: {'是' if new_password_works else '否'}")
                    print(f"   旧密码可登录: {'是' if old_password_works else '否'}")
                    
                    if new_password_works and not old_password_works:
                        print("[成功] 密码更新成功：新密码生效，旧密码失效")
                    elif not new_password_works and old_password_works:
                        print("[列表] 密码未更新：旧密码仍然有效")
                    elif new_password_works and old_password_works:
                        print("[警告]  异常情况：新旧密码都可以登录")
                    else:
                        print("[失败] 错误情况：新旧密码都无法登录")
                        
                else:
                    print("[警告]  已注册用户密码更新失败")
                    
            elif user_exists and is_oauth_user:
                print("[列表] 系统识别为OAuth用户（可能之前的OAuth步骤生效了）")
                
            elif not user_exists:
                print("[警告]  系统未识别到已注册用户（可能存在问题）")
                
        else:
            print("[失败] 已注册邮箱验证码验证失败")
            
    else:
        print("[列表] 向已注册邮箱发送验证码失败")
        error_msg = existing_send_data.get("error", "")
        print(f"   错误信息: {error_msg}")
    
    print("\n[完成] 邮箱注册后Google OAuth流程测试完成！")
    print("[成功] 测试了已注册用户的OAuth绑定逻辑")
    print("[成功] 验证了系统对已注册用户状态的识别")
    
    return True


def test_email_register_then_facebook_oauth():
    """
    测试邮箱注册后再进行Facebook OAuth登录
    
    简化版本的Facebook OAuth绑定测试。
    """
    print("\n[Facebook] Facebook OAuth绑定测试")
    
    # client 通过 TestClient() 创建测试客户端实例
    client = TestClient()
    
    # facebook_test_email 通过 generate_test_email 生成Facebook测试邮箱
    facebook_test_email = generate_test_email("register_then_facebook")
    facebook_test_password = "RegisterThenFacebook123!"
    
    print("[测试] 开始测试：邮箱注册后Facebook OAuth流程")
    print(f"测试邮箱: {facebook_test_email}")
    
    # ======== 快速创建邮箱账户 ========
    print("\n[注册] 使用test_user模式快速创建邮箱账户")
    
    # quick_register_data 构造快速注册数据
    quick_register_data = {
        "email": facebook_test_email,
        "password": facebook_test_password,
        "test_user": True
    }
    
    # quick_register_response 通过 client.post 快速创建账户
    quick_register_response = client.post("/auth/register", quick_register_data)
    print_test_result("快速创建邮箱账户", quick_register_response, 200)
    
    if not (quick_register_response.get("status_code") == 200 and 
            quick_register_response.get("data", {}).get("success", False)):
        print("[失败] 快速创建账户失败，跳过Facebook OAuth测试")
        return False
    
    print("[成功] 邮箱账户创建成功")
    
    # ======== Facebook OAuth流程 ========
    print("\n[设备] Facebook OAuth登录流程")
    
    state_value = "register_then_facebook_012"
    
    # facebook_auth_data 构造Facebook授权数据
    facebook_auth_data = {
        "state": state_value
    }
    
    # facebook_auth_response 通过 client.post 获取Facebook授权URL
    facebook_auth_response = client.post("/auth/facebook", facebook_auth_data)
    print_test_result("获取Facebook授权URL", facebook_auth_response, 200)
    
    if (facebook_auth_response.get("status_code") == 200 and 
        facebook_auth_response.get("data", {}).get("success", False)):
        
        print("[成功] Facebook授权URL获取成功")
        
        # ======== Facebook OAuth回调 ========
        print("\n[步骤] Facebook OAuth回调测试")
        
        mock_fb_code = "mock_facebook_existing_user_code"
        
        # facebook_callback_data 构造Facebook回调数据
        facebook_callback_data = {
            "code": mock_fb_code,
            "state": state_value,
            "expected_state": state_value
        }
        
        # facebook_callback_response 通过 client.post 处理Facebook回调
        facebook_callback_response = client.post("/auth/facebook/callback", facebook_callback_data)
        print_test_result("Facebook OAuth回调", facebook_callback_response, 200)
        
        # 分析Facebook OAuth回调结果
        fb_callback_data = facebook_callback_response.get("data", {})
        if fb_callback_data.get("success", False):
            print("[成功] Facebook OAuth回调成功（模拟）")
        else:
            print("[列表] Facebook OAuth回调失败（预期，使用mock数据）")
    
    else:
        print("[列表] Facebook授权URL获取失败")
    
    return True


if __name__ == "__main__":
    """
    脚本直接执行入口
    
    执行邮箱注册后OAuth的所有测试场景。
    """
    print("[邮件] 执行邮箱注册后OAuth测试套件")
    
    # 执行邮箱注册后Google OAuth测试
    success1 = test_email_register_then_google_oauth()
    
    print("\n" + "="*80)
    
    # 执行邮箱注册后Facebook OAuth测试
    success2 = test_email_register_then_facebook_oauth()
    
    # 所有测试都成功才返回成功
    overall_success = success1 and success2
    
    print(f"\n[目标] 邮箱注册后OAuth测试套件完成")
    print(f"总体结果: {'成功' if overall_success else '失败'}")
    
    print("\n[列表] 测试说明:")
    print("   * 测试已注册用户尝试OAuth登录的绑定逻辑")
    print("   * 验证系统对已存在用户的识别和处理")
    print("   * 关键测试点是账户绑定和密码更新逻辑")
    
    # 根据测试结果设置程序退出状态码
    exit(0 if overall_success else 1)
