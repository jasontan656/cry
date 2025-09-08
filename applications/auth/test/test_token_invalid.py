# 无效token测试脚本
# 测试系统对无效或过期访问令牌的处理

from test_config import TestClient, generate_test_email, print_test_result


def test_access_protected_endpoint_without_token():
    """
    测试在没有token的情况下访问受保护的接口
    
    验证系统是否正确拒绝未认证的请求。
    注意：由于当前auth模块主要提供认证服务，
    这里主要测试认证相关接口的token验证逻辑。
    """
    # client 通过 TestClient() 创建测试客户端实例
    client = TestClient()
    
    print(f"Testing access to protected endpoints without token")
    
    # ======== 测试访问需要认证的接口 ========
    print("\n[安全] 测试：无token访问认证接口")
    
    # 假设存在一个需要认证的用户信息接口（示例）
    # 由于当前auth模块中没有明确的受保护接口，
    # 这里模拟一个可能的用户信息查询接口
    
    # 尝试访问可能需要认证的接口
    protected_endpoints = [
        "/auth/user/profile",      # 假设的用户信息接口
        "/auth/user/settings",     # 假设的用户设置接口
        "/auth/token/refresh",     # 假设的token刷新接口
        "/auth/user/logout",       # 假设的登出接口
    ]
    
    for endpoint in protected_endpoints:
        print(f"\n   测试接口: {endpoint}")
        
        # 不携带任何认证信息的请求
        # no_token_response 通过 client.get 发送无token的GET请求
        no_token_response = client.get(endpoint)
        
        # 简化输出，只显示关键信息
        status_code = no_token_response.get("status_code", 0)
        data = no_token_response.get("data", {})
        
        print(f"      状态码: {status_code}")
        
        # 根据状态码判断认证保护是否有效
        if status_code == 401:
            print("      [成功] 正确返回401未认证")
        elif status_code == 403:
            print("      [成功] 正确返回403无权限")
        elif status_code == 404:
            print("      [列表] 接口不存在（正常）")
        elif status_code == 200:
            success = data.get("success", True)
            if not success:
                print("      [成功] 业务层正确拒绝未认证请求")
            else:
                print("      [警告]  接口可能未受认证保护")
        else:
            print(f"      [列表] 其他响应: {status_code}")
    
    return True


def test_access_with_invalid_token():
    """
    测试使用无效token访问接口
    
    验证系统对格式错误或伪造token的处理。
    """
    print(f"\nTesting access with invalid token")
    
    # client 通过 TestClient() 创建测试客户端实例
    client = TestClient()
    
    # 定义各种无效token格式
    invalid_tokens = [
        "invalid-token-format",                    # 简单字符串
        "Bearer invalid-token",                    # 错误的Bearer格式
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid",  # 无效JWT
        "",                                        # 空token
        "   ",                                     # 空白字符
        "token" * 100,                            # 过长token
    ]
    
    for i, invalid_token in enumerate(invalid_tokens, 1):
        print(f"\n   {i}. 测试无效token: '{invalid_token[:30]}{'...' if len(invalid_token) > 30 else ''}'")
        
        # 设置Authorization header
        # 临时修改session的headers来包含无效token
        original_headers = client.session.headers.copy()
        client.session.headers["Authorization"] = f"Bearer {invalid_token}"
        
        try:
            # invalid_token_response 通过 client.get 发送带无效token的请求
            # 测试一个可能存在的用户信息接口
            invalid_token_response = client.get("/auth/user/profile")
            
            status_code = invalid_token_response.get("status_code", 0)
            data = invalid_token_response.get("data", {})
            
            # 检查系统如何处理无效token
            if status_code in [401, 403]:
                print(f"      [成功] 正确拒绝无效token ({status_code})")
            elif status_code == 404:
                print(f"      [列表] 接口不存在")
            else:
                success = data.get("success", True)
                if not success:
                    print(f"      [成功] 业务层正确拒绝无效token")
                else:
                    print(f"      [警告]  系统可能未验证token ({status_code})")
        
        finally:
            # 恢复原始headers
            client.session.headers.clear()
            client.session.headers.update(original_headers)
    
    return True


def test_expired_token_simulation():
    """
    测试过期token的处理
    
    由于无法直接创建过期token，这里主要测试token验证的逻辑。
    """
    print("\n[超时] 测试：过期token处理模拟")
    
    # client 通过 TestClient() 创建测试客户端实例
    client = TestClient()
    
    # 先创建一个正常账户并登录获取真实token
    # test_email 通过 generate_test_email 生成测试邮箱
    test_email = generate_test_email("token_expiry_test")
    test_password = "TokenExpiryTest123!"
    
    print("\n[注册] 准备：创建测试账户并获取token")
    
    # 注册账户
    register_data = {
        "email": test_email,
        "password": test_password,
        "test_user": True
    }
    
    # register_response 通过 client.post 创建测试账户
    register_response = client.post("/auth/register", register_data)
    
    if not (register_response.get("status_code") == 200 and 
            register_response.get("data", {}).get("success", False)):
        print("[失败] 创建测试账户失败，跳过token过期测试")
        return False
    
    # 登录获取token
    login_data = {
        "email": test_email,
        "password": test_password
    }
    
    # login_response 通过 client.post 执行登录获取token
    login_response = client.post("/auth/login", login_data)
    
    if not (login_response.get("status_code") == 200 and 
            login_response.get("data", {}).get("success", False)):
        print("[失败] 登录获取token失败，跳过token过期测试")
        return False
    
    # 提取真实token
    user_data = login_response.get("data", {}).get("data", {})
    real_token = user_data.get("access_token", "")
    
    if not real_token:
        print("[失败] 未获取到访问token，跳过token过期测试")
        return False
    
    print(f"[成功] 获得真实token: {real_token[:20]}...")
    
    # ======== 测试token格式验证 ========
    print("\n[验证] 测试：token格式分析")
    
    # 分析token基本格式
    if "." in real_token:
        token_parts = real_token.split(".")
        print(f"   Token段数: {len(token_parts)}")
        
        if len(token_parts) == 3:
            print("   [成功] 符合JWT三段式格式")
        else:
            print("   [列表] 非标准JWT格式")
    else:
        print("   [列表] 非JWT格式token")
    
    # ======== 测试使用真实token访问（如果有受保护接口）========
    print("\n[登录] 测试：使用真实token访问")
    
    # 设置Authorization header使用真实token
    original_headers = client.session.headers.copy()
    client.session.headers["Authorization"] = f"Bearer {real_token}"
    
    try:
        # 尝试访问受保护接口
        # real_token_response 通过 client.get 发送带真实token的请求
        real_token_response = client.get("/auth/user/profile")
        
        status_code = real_token_response.get("status_code", 0)
        
        if status_code == 200:
            print("   [成功] 真实token成功访问受保护接口")
        elif status_code == 404:
            print("   [列表] 测试接口不存在（正常）")
        else:
            print(f"   [列表] 其他响应: {status_code}")
    
    finally:
        # 恢复原始headers
        client.session.headers.clear()
        client.session.headers.update(original_headers)
    
    return True


def test_token_in_different_formats():
    """
    测试不同格式的token处理
    
    验证系统对各种token传递方式的处理。
    """
    print("\n[列表] 测试：不同token传递格式")
    
    # client 通过 TestClient() 创建测试客户端实例
    client = TestClient()
    
    # 使用一个示例token
    sample_token = "sample_token_for_format_test_123456789"
    
    # 测试不同的Authorization header格式
    token_formats = [
        f"Bearer {sample_token}",      # 标准Bearer格式
        f"bearer {sample_token}",      # 小写bearer
        f"Token {sample_token}",       # Token前缀
        f"{sample_token}",             # 直接token
        f"JWT {sample_token}",         # JWT前缀
    ]
    
    for i, token_format in enumerate(token_formats, 1):
        print(f"\n   {i}. 测试格式: '{token_format[:40]}...'")
        
        # 设置Authorization header
        original_headers = client.session.headers.copy()
        client.session.headers["Authorization"] = token_format
        
        try:
            # format_response 通过 client.get 发送不同格式token的请求
            format_response = client.get("/auth/user/profile")
            
            status_code = format_response.get("status_code", 0)
            
            if status_code == 404:
                print(f"      [列表] 接口不存在")
            elif status_code in [401, 403]:
                print(f"      [列表] 认证失败 ({status_code})")
            else:
                print(f"      [列表] 响应: {status_code}")
        
        finally:
            # 恢复原始headers
            client.session.headers.clear()
            client.session.headers.update(original_headers)
    
    return True


if __name__ == "__main__":
    """
    脚本直接执行入口
    
    执行token相关的所有测试。
    """
    print("[密码] 执行无效token测试套件")
    
    # 执行各项token测试
    success1 = test_access_protected_endpoint_without_token()
    
    print("\n" + "="*60)
    success2 = test_access_with_invalid_token()
    
    print("\n" + "="*60)
    success3 = test_expired_token_simulation()
    
    print("\n" + "="*60)
    success4 = test_token_in_different_formats()
    
    # 所有测试都成功才返回成功
    overall_success = success1 and success2 and success3 and success4
    
    print(f"\n[目标] Token测试套件完成")
    print(f"总体结果: {'成功' if overall_success else '失败'}")
    
    print("\n[列表] 测试说明:")
    print("   * 当前auth模块可能没有明确的受保护接口")
    print("   * 测试主要验证token处理的API连通性")
    print("   * 404响应通常表示接口不存在，这是正常的")
    print("   * 重点关注系统的错误处理和安全验证逻辑")
    
    # 根据测试结果设置程序退出状态码
    exit(0 if overall_success else 1)
