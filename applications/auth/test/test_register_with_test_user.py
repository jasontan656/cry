# test_user模式注册测试脚本
# 测试跳过验证码验证的快速注册流程

from test_config import TestClient, generate_test_email, print_test_result


def test_register_with_test_user_mode():
    """
    测试test_user模式注册流程
    
    模拟开发调试环境下的快速注册流程：
    1. 使用test_user=True参数直接注册
    2. 跳过验证码验证步骤
    3. 验证注册成功后可以正常登录
    
    该测试验证开发模式下的简化注册流程。
    """
    # client 通过 TestClient() 创建测试客户端实例
    # 用于发送HTTP请求到auth模块API
    client = TestClient()
    
    # test_email 通过 generate_test_email 生成测试用邮箱地址
    # 传入标识符 "testuser_mode" 生成唯一邮箱
    test_email = generate_test_email("testuser_mode")
    # test_password 设置为测试用密码字符串
    test_password = "TestUserPassword123!"
    
    print(f"test_user mode registration flow test starting")
    print(f"Test email: {test_email}")
    print(f"Test password length: {len(test_password)}")
    print(f"Note: this mode is for development debugging only, skips verification code validation")
    
    # ======== 直接注册测试 ========
    print("\n[注册] test_user模式：直接注册")
    
    # register_data 构造test_user模式的注册请求数据
    # 包含邮箱、密码和test_user标识设为True
    register_data = {
        "email": test_email,
        "password": test_password,
        "test_user": True
    }
    
    # register_response 通过 client.post 发送注册请求
    # 调用 /auth/register 接口，传入包含test_user标识的注册数据
    # 得到直接注册的响应结果
    register_response = client.post("/auth/register", register_data)
    
    # 调用 print_test_result 打印注册测试结果
    # 传入测试描述、响应数据、期望状态码200
    print_test_result("test_user模式直接注册", register_response, 200)
    
    # 检查注册是否成功
    if (register_response.get("status_code") != 200 or 
        not register_response.get("data", {}).get("success", False)):
        print("[失败] test_user模式注册失败，终止测试")
        return False
    
    # 从注册响应中获取用户信息
    register_data_response = register_response.get("data", {})
    user_data = register_data_response.get("data", {})
    user_id = user_data.get("user_id")
    email = user_data.get("email")
    
    print(f"[成功] 注册成功")
    print(f"   用户ID: {user_id}")
    print(f"   邮箱: {email}")
    
    # ======== 登录验证测试 ========
    print("\n[登录] 验证步骤: 使用注册账户登录")
    
    # login_data 构造登录测试的请求数据字典
    # 包含刚才注册的邮箱和密码
    login_data = {
        "email": test_email,
        "password": test_password
    }
    
    # login_response 通过 client.post 发送POST请求
    # 调用 /auth/login 接口，传入登录凭证数据
    # 得到登录尝试的响应结果
    login_response = client.post("/auth/login", login_data)
    
    # 调用 print_test_result 打印登录验证的测试结果
    print_test_result("test_user账户登录", login_response, 200)
    
    # 检查登录是否成功
    if (login_response.get("status_code") != 200 or 
        not login_response.get("data", {}).get("success", False)):
        print("[失败] 登录验证失败，test_user注册可能不完整")
        return False
    
    # 从登录响应中获取token或用户信息
    login_data_response = login_response.get("data", {})
    login_user_data = login_data_response.get("data", {})
    
    print("[成功] 登录成功，账户状态正常")
    if "access_token" in login_user_data:
        print(f"   获得访问令牌: {login_user_data['access_token'][:20]}...")
    
    # ======== 对比测试：普通模式注册 ========
    print("\n[步骤] 对比测试：普通模式注册（预期失败）")
    
    # 生成另一个测试邮箱用于对比
    # compare_email 通过 generate_test_email 生成对比用邮箱地址
    compare_email = generate_test_email("normal_mode_compare")
    
    # normal_register_data 构造普通模式的注册请求数据
    # 包含邮箱、密码，test_user默认为False或不设置
    normal_register_data = {
        "email": compare_email,
        "password": test_password
        # 不设置test_user或设置为False
    }
    
    # normal_register_response 通过 client.post 发送普通注册请求
    # 调用 /auth/register 接口，测试默认模式下的行为
    normal_register_response = client.post("/auth/register", normal_register_data)
    
    # 调用 print_test_result 打印对比测试结果
    # 普通模式下直接注册应该失败，要求先验证码流程
    print_test_result("普通模式直接注册（预期失败）", normal_register_response, 200)
    
    # 检查普通模式注册的响应
    normal_data = normal_register_response.get("data", {})
    if not normal_data.get("success", False):
        error_message = normal_data.get("error", "")
        print(f"[成功] 普通模式正确拒绝直接注册: {error_message}")
    else:
        print("[警告]  普通模式意外允许直接注册")
    
    # ======== 边界测试：test_user=False ========
    print("\n[实验] 边界测试：显式设置test_user=False")
    
    # 生成第三个测试邮箱
    # explicit_false_email 通过 generate_test_email 生成边界测试邮箱
    explicit_false_email = generate_test_email("explicit_false")
    
    # explicit_false_data 构造显式设置test_user为False的注册数据
    explicit_false_data = {
        "email": explicit_false_email,
        "password": test_password,
        "test_user": False
    }
    
    # explicit_false_response 通过 client.post 发送注册请求
    explicit_false_response = client.post("/auth/register", explicit_false_data)
    
    # 调用 print_test_result 打印边界测试结果
    print_test_result("显式test_user=False注册", explicit_false_response, 200)
    
    # 检查显式False的响应
    explicit_data = explicit_false_response.get("data", {})
    if not explicit_data.get("success", False):
        print("[成功] 显式test_user=False正确拒绝直接注册")
    else:
        print("[警告]  显式test_user=False意外允许直接注册")
    
    # ======== 安全性提醒 ========
    print("\n[安全] 安全性提醒")
    print("[警告]  test_user模式仅供开发调试使用")
    print("[警告]  生产环境中应禁用或严格控制该功能")
    print("[警告]  该模式跳过了重要的邮箱验证安全步骤")
    
    print("\n[完成] test_user模式注册测试完成！")
    print("[成功] 验证了开发调试模式的快速注册流程")
    print("[成功] 确认了普通模式和test_user模式的行为差异")
    print("[成功] 测试了相关边界情况")
    
    return True


def test_test_user_mode_with_existing_email():
    """
    测试test_user模式下使用已存在邮箱的处理
    
    验证test_user模式下重复邮箱的处理逻辑。
    """
    # client 通过 TestClient() 创建测试客户端实例
    client = TestClient()
    
    # existing_email 通过 generate_test_email 生成测试邮箱
    # 使用相同标识符确保邮箱重复使用
    existing_email = generate_test_email("existing_for_testuser")
    
    print("[步骤] 附加测试：test_user模式处理已存在邮箱")
    print(f"测试邮箱: {existing_email}")
    
    # ======== 第一次注册 ========
    print("\n[注册] 第一步：先创建一个账户")
    
    first_register_data = {
        "email": existing_email,
        "password": "FirstPassword123!",
        "test_user": True
    }
    
    # first_response 通过 client.post 发送第一次注册请求
    first_response = client.post("/auth/register", first_register_data)
    print_test_result("第一次test_user注册", first_response, 200)
    
    # 如果第一次注册失败，跳过后续测试
    if (first_response.get("status_code") != 200 or 
        not first_response.get("data", {}).get("success", False)):
        print("[失败] 第一次注册失败，跳过重复邮箱测试")
        return False
    
    # ======== 第二次注册（重复邮箱）========
    print("\n[步骤] 第二步：使用相同邮箱再次注册")
    
    second_register_data = {
        "email": existing_email,
        "password": "SecondPassword456!",
        "test_user": True
    }
    
    # second_response 通过 client.post 发送第二次注册请求
    second_response = client.post("/auth/register", second_register_data)
    print_test_result("重复邮箱test_user注册", second_response, 200)
    
    # 分析第二次注册的结果
    second_data = second_response.get("data", {})
    if second_data.get("success", False):
        print("[列表] test_user模式：允许重复邮箱，可能更新了密码")
    else:
        error_type = second_data.get("error_type", "")
        if error_type == "USER_EXISTS":
            print("[列表] test_user模式：正确识别并拒绝重复邮箱")
        else:
            print(f"[列表] test_user模式：其他处理逻辑 ({error_type})")
    
    return True


if __name__ == "__main__":
    """
    脚本直接执行入口
    
    执行test_user模式相关的所有测试。
    """
    print("[实验] 执行test_user模式测试套件")
    
    # 执行主要的test_user模式测试
    success1 = test_register_with_test_user_mode()
    
    print("\n" + "="*60)
    
    # 执行重复邮箱处理测试
    success2 = test_test_user_mode_with_existing_email()
    
    # 所有测试都成功才返回成功
    overall_success = success1 and success2
    
    print(f"\n[目标] 测试套件完成，总体结果: {'成功' if overall_success else '失败'}")
    
    # 根据测试结果设置程序退出状态码
    exit(0 if overall_success else 1)
