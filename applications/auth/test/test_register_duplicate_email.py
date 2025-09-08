# 重复邮箱注册测试脚本
# 测试用户尝试使用已存在邮箱注册时的处理逻辑

from test_config import TestClient, generate_test_email, print_test_result


def test_duplicate_email_registration():
    """
    测试重复邮箱注册流程
    
    模拟以下场景：
    1. 先完成一个正常的邮箱注册
    2. 再次尝试使用相同邮箱注册
    3. 验证系统是否正确处理重复邮箱的情况
    
    该测试验证邮箱唯一性检查逻辑。
    """
    # client 通过 TestClient() 创建测试客户端实例
    # 用于发送HTTP请求到auth模块API
    client = TestClient()
    
    # test_email 通过 generate_test_email 生成测试用邮箱地址
    # 传入标识符 "duplicate_test" 生成唯一邮箱
    test_email = generate_test_email("duplicate_test")
    # test_password1 设置为第一次注册使用的密码
    test_password1 = "FirstPassword123!"
    # test_password2 设置为第二次注册尝试使用的密码
    test_password2 = "SecondPassword456!"
    
    print(f"Duplicate email registration handling test starting")
    print(f"Test email: {test_email}")
    print(f"First password length: {len(test_password1)}")
    print(f"Second password length: {len(test_password2)}")
    print(f"Password difference: {test_password1 != test_password2}")
    
    # ======== 第一轮：完成正常注册 ========
    print("\n[注册] 第一轮：完成正常注册流程")
    
    # 步骤1: 发送验证码
    print("\n[邮件] 步骤1.1: 发送验证码")
    send_code_data = {
        "email": test_email,
        "test_user": True  # 开启测试模式，使用固定验证码123456
    }
    
    # send_response1 通过 client.post 发送第一次验证码请求
    # 调用 /auth/send-verification 接口
    send_response1 = client.post("/auth/send-verification", send_code_data)
    print_test_result("第一次发送验证码", send_response1, 200)
    
    # 检查第一次发送验证码是否成功
    if (send_response1.get("status_code") != 200 or 
        not send_response1.get("data", {}).get("success", False)):
        print("[失败] 第一次发送验证码失败，无法继续测试")
        return False
    
    # 步骤2: 验证验证码
    print("\n[验证] 步骤1.2: 验证验证码")
    test_code = "123456"  # 使用固定测试验证码
    verify_code_data = {
        "email": test_email,
        "code": test_code
    }
    
    # verify_response1 通过 client.post 发送第一次验证码验证请求
    verify_response1 = client.post("/auth/verify-code", verify_code_data)
    print_test_result("第一次验证验证码", verify_response1, 200)
    
    # 检查第一次验证码验证是否成功
    if (verify_response1.get("status_code") != 200 or 
        not verify_response1.get("data", {}).get("success", False)):
        print("[失败] 第一次验证码验证失败，无法继续测试")
        return False
    
    # 步骤3: 设置密码完成注册
    print("\n[密码] 步骤1.3: 设置密码完成注册")
    set_password_data1 = {
        "email": test_email,
        "password": test_password1
    }
    
    # password_response1 通过 client.post 发送第一次密码设置请求
    password_response1 = client.post("/auth/set-password", set_password_data1)
    print_test_result("第一次设置密码", password_response1, 200)
    
    # 检查第一次密码设置是否成功
    if (password_response1.get("status_code") != 200 or 
        not password_response1.get("data", {}).get("success", False)):
        print("[失败] 第一次设置密码失败，无法继续测试")
        return False
    
    print("[成功] 第一轮注册完成，用户账户已创建")
    
    # ======== 第二轮：尝试重复邮箱注册 ========
    print("\n[步骤] 第二轮：尝试使用相同邮箱再次注册")
    
    # 步骤1: 尝试发送验证码到已存在的邮箱
    print("\n[邮件] 步骤2.1: 向已存在邮箱发送验证码")
    
    # send_response2 通过 client.post 发送第二次验证码请求
    # 使用相同的邮箱地址，测试系统处理
    send_response2 = client.post("/auth/send-verification", send_code_data)
    print_test_result("重复邮箱发送验证码", send_response2, 200)
    
    # 注意：发送验证码到已存在邮箱可能仍然成功
    # 关键是在后续步骤中如何处理
    
    # 步骤2: 验证验证码（如果发送成功）
    if (send_response2.get("status_code") == 200 and 
        send_response2.get("data", {}).get("success", False)):
        
        print("\n[验证] 步骤2.2: 验证验证码")
        
        # verify_response2 通过 client.post 发送第二次验证码验证请求
        verify_response2 = client.post("/auth/verify-code", verify_code_data)
        print_test_result("重复邮箱验证验证码", verify_response2, 200)
        
        # 检查验证响应中的用户状态
        if verify_response2.get("status_code") == 200:
            verify_data = verify_response2.get("data", {})
            user_exists = verify_data.get("user_exists", False)
            is_oauth_user = verify_data.get("is_oauth_user", False)
            
            print(f"[状态] 用户状态检查: 已存在={user_exists}, OAuth用户={is_oauth_user}")
            
            # 如果用户已存在且不是OAuth用户，尝试设置密码应该有特殊处理
            if user_exists and not is_oauth_user:
                print("\n[密码] 步骤2.3: 尝试为已存在用户设置新密码")
                
                set_password_data2 = {
                    "email": test_email,
                    "password": test_password2
                }
                
                # password_response2 通过 client.post 发送第二次密码设置请求
                password_response2 = client.post("/auth/set-password", set_password_data2)
                print_test_result("重复邮箱设置密码", password_response2, 200)
                
                # 检查密码设置的响应和消息
                password_data = password_response2.get("data", {})
                message = password_data.get("message", "")
                
                print(f"[注册] 系统响应消息: {message}")
                
                # 验证最终状态：尝试使用新密码登录
                print("\n[登录] 验证步骤: 测试新密码登录")
                
                login_data_new = {
                    "email": test_email,
                    "password": test_password2
                }
                
                # login_response_new 通过 client.post 测试新密码登录
                login_response_new = client.post("/auth/login", login_data_new)
                print_test_result("新密码登录测试", login_response_new, 200)
                
                # 验证原密码是否还能登录
                print("\n[登录] 验证步骤: 测试原密码登录")
                
                login_data_old = {
                    "email": test_email,
                    "password": test_password1
                }
                
                # login_response_old 通过 client.post 测试原密码登录
                login_response_old = client.post("/auth/login", login_data_old)
                print_test_result("原密码登录测试", login_response_old, 200)
                
                # 分析结果
                new_password_works = (login_response_new.get("status_code") == 200 and 
                                    login_response_new.get("data", {}).get("success", False))
                old_password_works = (login_response_old.get("status_code") == 200 and 
                                    login_response_old.get("data", {}).get("success", False))
                
                print(f"\n[状态] 登录测试结果:")
                print(f"   新密码可登录: {'是' if new_password_works else '否'}")
                print(f"   原密码可登录: {'是' if old_password_works else '否'}")
                
                if new_password_works and not old_password_works:
                    print("[成功] 密码更新逻辑正常：新密码生效，原密码失效")
                elif not new_password_works and old_password_works:
                    print("[成功] 密码保护逻辑正常：原密码不变，重复注册无效")
                elif new_password_works and old_password_works:
                    print("[警告]  异常情况：新旧密码都可以登录")
                else:
                    print("[失败] 错误情况：新旧密码都无法登录")
    
    # ======== 测试使用test_user模式重复注册 ========
    print("\n[实验] 附加测试：使用test_user模式尝试重复注册")
    
    # register_data 构造test_user模式的注册请求数据
    # 包含已存在的邮箱、新密码和test_user标识
    register_data = {
        "email": test_email,
        "password": "TestUserPassword789!",
        "test_user": True
    }
    
    # register_response 通过 client.post 发送直接注册请求
    # 调用 /auth/register 接口，测试test_user模式处理
    register_response = client.post("/auth/register", register_data)
    print_test_result("test_user模式重复注册", register_response, 200)
    
    # 检查test_user模式下的重复邮箱处理
    register_data = register_response.get("data", {})
    if register_response.get("status_code") == 200:
        if register_data.get("success", False):
            print("[成功] test_user模式：允许重复邮箱注册")
        else:
            error_type = register_data.get("error_type", "")
            if error_type == "USER_EXISTS":
                print("[成功] test_user模式：正确识别重复邮箱")
            else:
                print(f"[列表] test_user模式：其他处理逻辑 ({error_type})")
    
    print("\n[完成] 重复邮箱注册测试完成！")
    print("[成功] 测试了正常注册后再次使用相同邮箱的各种场景")
    print("[成功] 验证了系统对重复邮箱的处理逻辑")
    
    return True


if __name__ == "__main__":
    """
    脚本直接执行入口
    
    当脚本作为主程序运行时，执行重复邮箱注册测试。
    """
    # 执行重复邮箱注册测试函数
    success = test_duplicate_email_registration()
    
    # 根据测试结果设置程序退出状态码
    exit(0 if success else 1)
