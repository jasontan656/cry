# 忘记密码流程测试脚本
# 测试完整的忘记密码流程：发送重置验证码 -> 验证验证码 -> 重置密码

from test_config import TestClient, generate_test_email, print_test_result
import json


def test_complete_forgot_password_flow():
    """
    测试完整的忘记密码流程
    
    模拟用户忘记密码的完整操作序列：
    1. 先创建一个测试用户账户
    2. 发送忘记密码验证码
    3. 验证重置验证码
    4. 重置密码为新密码
    5. 验证可以使用新密码登录
    6. 验证旧密码不能再登录
    
    该测试验证忘记密码流程的完整性和安全性。
    """
    # client 通过 TestClient() 创建测试客户端实例
    # 用于发送HTTP请求到auth模块API
    client = TestClient()
    
    # test_email 通过 generate_test_email 生成测试用邮箱地址
    # 传入标识符 "forgot_password" 生成唯一邮箱
    test_email = generate_test_email("forgot_password")
    # old_password 设置为原始密码字符串
    old_password = "OldPassword123!"
    # new_password 设置为新密码字符串
    new_password = "NewPassword456!"
    
    print(f"Forgot password flow test starting")
    print(f"Test email: {test_email}")
    print(f"Original password length: {len(old_password)}")
    print(f"New password length: {len(new_password)}")
    print(f"Password change planned: {old_password != new_password}")
    
    # ======== 准备阶段：创建测试用户 ========
    print("\n[准备] 创建测试用户账户")
    
    # register_data 构造test_user模式的注册请求数据
    # 使用test_user=True快速创建账户，跳过验证码流程
    register_data = {
        "email": test_email,
        "password": old_password,
        "test_user": True
    }
    
    # register_response 通过 client.post 发送注册请求
    # 调用 /auth/register 接口快速创建测试账户
    register_response = client.post("/auth/register", register_data)
    
    # 调用 print_test_result 打印注册结果
    print_test_result("创建测试用户", register_response, 200, register_data)
    
    # 检查账户创建是否成功
    if (register_response.get("status_code") != 200 or 
        not register_response.get("data", {}).get("success", False)):
        print("[错误] 创建测试账户失败，无法进行忘记密码测试")
        return False
    
    print("[成功] 测试用户账户创建成功")
    
    # ======== 步骤1: 发送忘记密码验证码 ========
    print("\n[步骤1] 发送忘记密码验证码")
    
    # forgot_password_data 构造忘记密码请求数据字典
    # 包含需要重置密码的邮箱地址和测试用户标识
    # test_user设为True时生成固定重置验证码123456，便于测试
    forgot_password_data = {
        "email": test_email,
        "test_user": True  # 开启测试模式，使用固定验证码123456
    }
    
    # forgot_response 通过 client.post 发送POST请求
    # 调用 /auth/forgot-password 接口，传入邮箱数据
    # 得到发送重置验证码的响应结果
    forgot_response = client.post("/auth/forgot-password", forgot_password_data)
    
    # 调用 print_test_result 打印步骤1的测试结果
    print_test_result("发送忘记密码验证码", forgot_response, 200, forgot_password_data)
    
    # 检查发送重置验证码是否成功
    if (forgot_response.get("status_code") != 200 or 
        not forgot_response.get("data", {}).get("success", False)):
        print("[错误] 发送忘记密码验证码失败，终止测试")
        return False
    
    print("[成功] 忘记密码验证码发送成功")
    
    # ======== 步骤2: 重置密码（验证码+新密码一步完成）========
    print("\n[步骤2] 重置用户密码（验证码+新密码一步完成）")
    
    # 注意：开启test_user模式后，忘记密码功能生成固定验证码123456
    # 直接在重置密码步骤中使用，无需单独验证步骤
    print("[注意] 测试模式已开启，直接使用固定验证码 '123456' 进行密码重置")
    print("[注意] 标准忘记密码流程：验证码+新密码一次性提交")
    
    # reset_code 设置为测试用的重置验证码
    # 使用固定验证码123456（test_user模式生成）
    reset_code = "123456"
    
    # reset_password_data 构造重置密码的请求数据字典
    # 包含邮箱地址、验证码和新密码
    reset_password_data = {
        "email": test_email,
        "code": reset_code,
        "new_password": new_password
    }
    
    # reset_response 通过 client.post 发送POST请求
    # 调用 /auth/reset-password 接口，传入重置密码数据
    # 得到密码重置的响应结果
    reset_response = client.post("/auth/reset-password", reset_password_data)
    
    # 调用 print_test_result 打印重置密码的测试结果
    print_test_result("重置密码", reset_response, 200, reset_password_data)
    
    # 检查密码重置是否成功
    if (reset_response.get("status_code") != 200 or 
        not reset_response.get("data", {}).get("success", False)):
        print("[错误] 重置密码失败，终止测试")
        return False
    
    print("[成功] 密码重置成功")
    
    # ======== 验证步骤1: 使用新密码登录 ========
    print("\n[验证1] 使用新密码登录")
    
    # new_login_data 构造新密码登录测试的请求数据字典
    # 包含邮箱和重置后的新密码
    new_login_data = {
        "email": test_email,
        "password": new_password
    }
    
    # new_login_response 通过 client.post 发送POST请求
    # 调用 /auth/login 接口，传入新密码登录凭证
    # 得到新密码登录的响应结果
    new_login_response = client.post("/auth/login", new_login_data)
    
    # 调用 print_test_result 打印新密码登录的测试结果
    print_test_result("新密码登录验证", new_login_response, 200, new_login_data)
    
    # 检查新密码登录是否成功
    new_password_works = (new_login_response.get("status_code") == 200 and 
                         new_login_response.get("data", {}).get("success", False))
    
    if not new_password_works:
        print("[错误] 新密码登录失败，密码重置可能不完整")
        return False
    
    print("[成功] 新密码登录成功")
    
    # ======== 验证步骤2: 确认旧密码失效 ========
    print("\n[验证2] 确认旧密码不能再登录")
    
    # old_login_data 构造旧密码登录测试的请求数据字典
    # 包含邮箱和重置前的旧密码
    old_login_data = {
        "email": test_email,
        "password": old_password
    }
    
    # old_login_response 通过 client.post 发送POST请求
    # 调用 /auth/login 接口，传入旧密码登录凭证
    # 得到旧密码登录的响应结果
    old_login_response = client.post("/auth/login", old_login_data)
    
    # 调用 print_test_result 打印旧密码登录的测试结果
    print_test_result("旧密码登录验证", old_login_response, 200, old_login_data)
    
    # 检查旧密码登录是否失败（期望失败）
    old_password_works = (old_login_response.get("status_code") == 200 and 
                         old_login_response.get("data", {}).get("success", False))
    
    # 分析密码重置效果
    print(f"\n[分析] 密码重置效果验证:")
    print(f"   新密码可登录: {'是' if new_password_works else '否'}")
    print(f"   旧密码可登录: {'是' if old_password_works else '否'}")
    
    if new_password_works and not old_password_works:
        print("[成功] 密码重置成功：新密码生效，旧密码失效")
        final_result = True
    elif not new_password_works and old_password_works:
        print("[错误] 密码重置失败：旧密码仍有效，新密码无效")
        final_result = False
    elif new_password_works and old_password_works:
        print("[异常] 异常情况：新旧密码都可以登录")
        final_result = False
    else:
        print("[错误] 严重错误：新旧密码都无法登录")
        final_result = False
    
    print("\n[完成] 忘记密码流程测试完成！")
    if final_result:
        print("[成功] 忘记密码功能正常工作")
        print("[成功] 密码重置逻辑安全可靠")
        print("[成功] 新旧密码切换正确")
    else:
        print("[失败] 忘记密码功能存在问题")
    
    return final_result


def test_forgot_password_for_nonexistent_user():
    """
    测试不存在用户的忘记密码处理
    
    验证系统对不存在用户的忘记密码请求处理。
    """
    print("\n[测试] 不存在用户忘记密码处理")
    
    # client 通过 TestClient() 创建测试客户端实例
    client = TestClient()
    
    # nonexistent_email 通过 generate_test_email 生成不存在的邮箱
    # 使用特殊标识确保该邮箱未被注册
    nonexistent_email = generate_test_email("nonexistent_forgot")
    
    print(f"不存在的邮箱: {nonexistent_email}")
    
    # nonexistent_forgot_data 构造不存在邮箱的忘记密码请求数据
    nonexistent_forgot_data = {
        "email": nonexistent_email
    }
    
    # nonexistent_response 通过 client.post 发送不存在邮箱的忘记密码请求
    nonexistent_response = client.post("/auth/forgot-password", nonexistent_forgot_data)
    
    # 调用 print_test_result 打印不存在邮箱忘记密码测试结果
    print_test_result("不存在邮箱忘记密码", nonexistent_response, 200, nonexistent_forgot_data)
    
    # 分析不存在邮箱忘记密码的响应
    nonexistent_data = nonexistent_response.get("data", {})
    
    # 检查系统是否正确处理不存在的邮箱
    if not nonexistent_data.get("success", False):
        error_message = nonexistent_data.get("error", "")
        error_type = nonexistent_data.get("error_type", "")
        
        print(f"[成功] 系统正确拒绝不存在邮箱的忘记密码请求")
        print(f"   错误信息: {error_message}")
        print(f"   错误类型: {error_type}")
        return True
    else:
        print("[错误] 系统意外接受了不存在邮箱的忘记密码请求")
        return False


def test_forgot_password_with_invalid_code():
    """
    测试错误验证码的忘记密码处理
    
    验证系统对错误重置验证码的安全处理。
    """
    print("\n[测试] 错误重置验证码处理")
    
    # client 通过 TestClient() 创建测试客户端实例
    client = TestClient()
    
    # test_email 通过 generate_test_email 生成测试邮箱
    test_email = generate_test_email("invalid_reset_code")
    
    # 先创建用户
    register_data = {
        "email": test_email,
        "password": "TestPassword123!",
        "test_user": True
    }
    
    # setup_response 通过 client.post 创建测试账户
    setup_response = client.post("/auth/register", register_data)
    
    if not (setup_response.get("status_code") == 200 and 
            setup_response.get("data", {}).get("success", False)):
        print("[错误] 创建测试账户失败")
        return False
    
    print("[准备] 测试账户创建成功")
    
    # 发送忘记密码验证码
    forgot_data = {
        "email": test_email,
        "test_user": True  # 开启测试模式，使用固定验证码123456
    }
    forgot_response = client.post("/auth/forgot-password", forgot_data)
    
    if not (forgot_response.get("status_code") == 200 and 
            forgot_response.get("data", {}).get("success", False)):
        print("[错误] 发送忘记密码验证码失败")
        return False
    
    print("[成功] 忘记密码验证码发送成功")
    
    # 使用错误的验证码进行验证
    wrong_codes = ["000000", "999999", "abcdef", "", "12345", "1234567"]
    
    for wrong_code in wrong_codes:
        print(f"\n   测试错误验证码: '{wrong_code}'")
        
        # verify_wrong_data 构造错误验证码的验证请求数据
        verify_wrong_data = {
            "email": test_email,
            "code": wrong_code
        }
        
        # verify_wrong_response 通过 client.post 发送错误验证码验证请求
        verify_wrong_response = client.post("/auth/verify-reset-code", verify_wrong_data)
        
        # 简化的结果检查
        wrong_data = verify_wrong_response.get("data", {})
        if not wrong_data.get("success", False):
            print(f"      [成功] 正确拒绝错误验证码")
        else:
            print(f"      [错误] 意外接受错误验证码")
            return False
    
    print("[成功] 所有错误验证码都被正确拒绝")
    return True


if __name__ == "__main__":
    """
    脚本直接执行入口
    
    执行忘记密码相关的所有测试。
    """
    print("[启动] 执行忘记密码功能测试套件")
    
    # 执行完整的忘记密码流程测试
    success1 = test_complete_forgot_password_flow()
    
    print("\n" + "="*80)
    
    # 执行不存在用户的忘记密码测试
    success2 = test_forgot_password_for_nonexistent_user()
    
    print("\n" + "="*80)
    
    # 执行错误验证码处理测试
    success3 = test_forgot_password_with_invalid_code()
    
    # 所有测试都成功才返回成功
    overall_success = success1 and success2 and success3
    
    print(f"\n[结果] 忘记密码测试套件完成")
    print(f"总体结果: {'成功' if overall_success else '失败'}")
    
    if overall_success:
        print("[提示] 忘记密码功能已完整实现并测试通过")
    else:
        print("[警告] 忘记密码功能存在问题，需要进一步检查")
    
    # 根据测试结果设置程序退出状态码
    exit(0 if overall_success else 1)
