# test_mbti_complete_flow.py - MBTI 完整流程自动化测试脚本
# 职责：从step1开始模拟完整MBTI测试流程，包括触发survey链接、填写随机答案和获得结果

import asyncio  # asyncio 通过 import 导入异步编程模块
import random  # random 通过 import 导入随机数生成模块
import sys  # sys 通过 import 导入系统模块
import os  # os 通过 import 导入操作系统模块
import json  # json 通过 import 导入JSON处理模块
import re  # re 通过 import 导入正则表达式模块

# 将上级目录添加到Python路径，以便导入step模块和utilities模块
current_dir = os.path.dirname(__file__)  # test目录
parent_dir = os.path.dirname(current_dir)  # mbti目录
grandparent_dir = os.path.dirname(parent_dir)  # applications目录
root_dir = os.path.dirname(grandparent_dir)  # 项目根目录

sys.path.insert(0, parent_dir)
sys.path.insert(0, root_dir)

# 直接导入Time类
try:
    from utilities.time import Time
except ImportError:
    # 如果直接导入失败，尝试动态导入
    import importlib.util
    utilities_time_path = os.path.join(root_dir, 'utilities', 'time.py')
    spec = importlib.util.spec_from_file_location("utilities.time", utilities_time_path)
    utilities_time = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(utilities_time)
    Time = utilities_time.Time

# 全局变量用于存储从step2获得的MBTI类型
step2_mbti_type = None

# 全局变量用于存储step1生成的request ID（timestamp_uuid），用于后续step验证
generated_request_id = None

# 直接导入step模块进行测试
import importlib.util
import types

# 硬编码导入orchestrate_connector模块，用于数据库查询失败模拟
# os.path.join 函数通过传入 parent_dir 和文件名参数构造完整文件路径
# 赋值给 orchestrate_connector_path 变量存储路径字符串
orchestrate_connector_path = os.path.join(parent_dir, "orchestrate_connector.py")
# importlib.util.spec_from_file_location 函数通过传入模块名和文件路径参数
# 创建模块规范对象，赋值给 spec_orch 变量
spec_orch = importlib.util.spec_from_file_location("orchestrate_connector", orchestrate_connector_path)
# importlib.util.module_from_spec 函数通过传入 spec_orch 规范对象
# 创建模块实例，赋值给 orchestrate_connector 变量
orchestrate_connector = importlib.util.module_from_spec(spec_orch)
# sys.modules 字典通过键赋值方式将模块实例注册到系统模块表
sys.modules["orchestrate_connector"] = orchestrate_connector
# spec_orch.loader.exec_module 方法通过传入模块实例参数执行模块加载
spec_orch.loader.exec_module(orchestrate_connector)

# 硬编码导入mbti主入口模块，遵循正确的系统架构
# os.path.join 函数通过传入 parent_dir 和 "mbti.py" 参数构造文件路径
# 赋值给 mbti_path 变量存储路径字符串
mbti_path = os.path.join(parent_dir, "mbti.py")
# importlib.util.spec_from_file_location 函数通过传入 "mbti" 模块名和路径参数
# 创建模块规范对象，赋值给 spec_mbti 变量
spec_mbti = importlib.util.spec_from_file_location("mbti", mbti_path)
# importlib.util.module_from_spec 函数通过传入 spec_mbti 规范对象
# 创建模块实例，赋值给 mbti 变量
mbti = importlib.util.module_from_spec(spec_mbti)
# sys.modules 字典通过键赋值方式将模块实例注册到系统模块表
sys.modules["mbti"] = mbti
# spec_mbti.loader.exec_module 方法通过传入模块实例参数执行模块加载
spec_mbti.loader.exec_module(mbti)



def extract_questions_from_html():
    """
    从mbti_survey.html文件中提取问题数据
    返回包含所有问题的列表
    """
    html_path = os.path.join(os.path.dirname(__file__), "..", "mbti_survey.html")

    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # 使用正则表达式提取questions数组
        # 查找包含questions变量的JavaScript代码块
        questions_pattern = r'const questions = \[([\s\S]*?)\];'
        match = re.search(questions_pattern, html_content)

        if match:
            questions_js = match.group(1)
            # 提取问题数量（计算引号包围的字符串数量）
            question_count = len(re.findall(r'"([^"]*)"', questions_js))
            print(f"从HTML中提取到 {question_count} 个问题")
            return question_count
        else:
            print("未找到questions数组，使用默认96个问题")
            return 96

    except Exception as e:
        print(f"读取HTML文件失败: {str(e)}，使用默认96个问题")
        return 96


async def generate_random_responses(question_count=None):
    """
    生成随机测试答案
    返回包含题目随机答案的字典
    """
    if question_count is None:
        question_count = extract_questions_from_html()

    # responses 变量通过字典推导式创建，包含0到question_count-1的索引
    # random.randint 函数通过传入1和5参数生成1-5之间的随机整数
    responses = {i: random.randint(1, 5) for i in range(question_count)}
    # 返回生成的responses字典
    return responses


def is_valid_request_id_format(request_id_string):
    """
    验证request ID格式的辅助函数
    Args:
        request_id_string: 待验证的字符串
    Returns:
        bool: 是否为有效的request ID格式（timestamp_uuid）
    """
    # request_id_pattern 通过正则表达式定义timestamp_uuid格式
    # 格式：YYYY-MM-DDTHH:MM:SS+TZ_xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx
    request_id_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+\d{4}_[0-9a-f]{8}-[0-9a-f]{4}-[4][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
    # re.match 函数通过传入正则模式和字符串进行匹配，re.IGNORECASE 忽略大小写
    # bool 函数将匹配结果转换为布尔值返回
    return bool(re.match(request_id_pattern, str(request_id_string), re.IGNORECASE))


async def test_request_id_validation():
    """
    测试request ID验证功能
    验证step1的timestamp_uuid生成和验证逻辑是否正常工作
    """
    print("\n=== 测试request ID验证功能 ===")

    # 测试用例1: 未传入request_id，验证是否生成有效timestamp_uuid格式
    print("测试用例1: 未传入request_id")
    test_request_no_request_id = {
        "intent": "mbti_step1",
        "user_id": "test_user_123",
        "test_user": True
    }

    try:
        result = await mbti.run(test_request_no_request_id)
        returned_request_id = result.get("request_id")

        # 验证返回的request_id是否为有效的timestamp_uuid格式
        if returned_request_id and is_valid_request_id_format(returned_request_id):
            print(f"✓ 未传入request_id时正确生成了有效timestamp_uuid: {returned_request_id}")
            global generated_request_id
            generated_request_id = returned_request_id
            return True
        else:
            print(f"✗ 未传入request_id时生成的request ID格式无效: {returned_request_id}")
            return False
    except Exception as e:
        print(f"✗ 测试用例1失败: {str(e)}")
        return False

    # 测试用例2: 传入有效timestamp_uuid，验证是否被正确使用
    print("\n测试用例2: 传入有效timestamp_uuid")
    valid_request_id = Time.timestamp()
    test_request_valid_request_id = {
        "intent": "mbti_step1",
        "user_id": "test_user_123",
        "request_id": valid_request_id,
        "test_user": True
    }

    try:
        result = await mbti.run(test_request_valid_request_id)
        returned_request_id = result.get("request_id")

        # 验证返回的request_id是否与传入的相同
        if returned_request_id == valid_request_id:
            print(f"✓ 传入有效timestamp_uuid时被正确使用: {returned_request_id}")
            return True
        else:
            print(f"✗ 传入有效timestamp_uuid时返回了不同的值: 期望={valid_request_id}, 实际={returned_request_id}")
            return False
    except Exception as e:
        print(f"✗ 测试用例2失败: {str(e)}")
        return False

    # 测试用例3: 传入无效request ID格式，验证是否被拒绝
    print("\n测试用例3: 传入无效request ID格式")
    invalid_request_id = "invalid-request-id-format-123"
    test_request_invalid_request_id = {
        "intent": "mbti_step1",
        "user_id": "test_user_123",
        "request_id": invalid_request_id,
        "test_user": True
    }

    try:
        result = await mbti.run(test_request_invalid_request_id)
        if result.get("success") == False and "Invalid request ID format" in result.get("error_message", ""):
            print(f"✓ 传入无效request ID格式时被正确拒绝: {result.get('error_message')}")
            return True
        else:
            print(f"✗ 传入无效request ID格式时未被拒绝: {result}")
            return False
    except Exception as e:
        print(f"✓ 传入无效request ID格式时抛出异常(符合预期): {str(e)}")
        return True


async def test_mbti_step1():
    """
    测试MBTI Step1流程
    通过mbti.py主入口模拟用户点击"我要找工作"按钮，触发MBTI测试引导
    首次调用：不提供test_user_status，触发数据库查询错误
    """
    # 构建测试请求数据字典，包含intent、user_id、test_user三个键（不传入request_id）
    # intent 键赋值为 "mbti_step1" 字符串，指定路由到step1处理器
    # user_id 键赋值为 "test_user_123" 字符串，作为测试用户标识
    # test_user 键赋值为 False 布尔值，标识非测试模式，触发数据库查询流程
    # 不传入request_id，让step1自动生成UUID
    test_request = {
        "intent": "mbti_step1",
        "user_id": "test_user_123",
        "test_user": False
    }

    # json.dumps 函数通过传入 test_request 字典和 indent 参数格式化输出
    # indent 赋值为 2 用于缩进，输出完整的请求数据结构
    print("REQUEST DATA:")
    print(json.dumps(test_request, indent=2))

    # try 块开始异常处理，捕获可能出现的异常情况
    try:
        # mbti.run 函数通过传入 test_request 字典参数被调用
        # await 关键字等待异步函数执行完成，返回结果赋值给 result 变量
        # 遵循正确架构：测试脚本 → mbti.py → router.py → step1.py
        result = await mbti.run(test_request)

        # json.dumps 函数通过传入 result 字典和 indent 参数格式化输出
        # indent 赋值为 2 用于缩进，输出完整的响应数据结构
        print("RESPONSE DATA:")
        print(json.dumps(result, indent=2))

        # result.get 方法通过传入 "success" 键获取处理成功状态
        # 返回布尔值用于 if 条件判断
        if result.get("success"):
            # result.get 方法通过传入 "button_config" 键和空字符串默认值
            # 获取按钮配置信息，赋值给 button_config 变量
            button_config = result.get("button_config", "")
            # if 条件判断检查 button_config 字符串是否包含 "mbti_survey.html"
            if "mbti_survey.html" in button_config:
                # return 语句返回 True 布尔值表示测试成功
                return True
            else:
                # return 语句返回 False 布尔值表示测试失败
                return False
        else:
            # return 语句返回 False 布尔值表示测试失败
            return False

    # except 捕获 Exception 异常类及其子类的异常实例
    # 异常对象赋值给变量 e
    except Exception as e:
        # print 函数通过传入异常信息字符串输出异常详情
        print(f"EXCEPTION: {str(e)}")
        # return 语句返回 False 布尔值表示测试失败
        return False


async def test_mbti_step1_with_test_data():
    """
    测试MBTI Step1流程（提供test_user_status）
    通过mbti.py主入口模拟用户点击"我要找工作"按钮，提供测试数据跳过数据库查询
    """
    # 构建测试请求数据字典，包含intent、user_id、test_user三个键（不传入request_id）
    # intent 键赋值为 "mbti_step1" 字符串，指定路由到step1处理器
    # user_id 键赋值为 "test_user_123" 字符串，作为测试用户标识
    # test_user 键赋值为 True 布尔值，标识测试模式，跳过数据库查询
    # 不传入request_id，让step1自动生成UUID
    test_request = {
        "intent": "mbti_step1",
        "user_id": "test_user_123",
        "test_user": True
    }

    # json.dumps 函数通过传入 test_request 字典和 indent 参数格式化输出
    # indent 赋值为 2 用于缩进，输出完整的请求数据结构
    print("REQUEST DATA:")
    print(json.dumps(test_request, indent=2))

    # try 块开始异常处理，捕获可能出现的异常情况
    try:
        # mbti.run 函数通过传入 test_request 字典参数被调用
        # await 关键字等待异步函数执行完成，返回结果赋值给 result 变量
        # 遵循正确架构：测试脚本 → mbti.py → router.py → step1.py
        result = await mbti.run(test_request)

        # json.dumps 函数通过传入 result 字典和 indent 参数格式化输出
        # indent 赋值为 2 用于缩进，输出完整的响应数据结构
        print("RESPONSE DATA:")
        print(json.dumps(result, indent=2))

        # result.get 方法通过传入 "success" 键获取处理成功状态
        # 返回布尔值用于 if 条件判断
        if result.get("success"):
            # result.get 方法通过传入 "button_config" 键和空字符串默认值
            # 获取按钮配置信息，赋值给 button_config 变量
            button_config = result.get("button_config", "")
            # if 条件判断检查 button_config 字符串是否包含 "mbti_survey.html"
            if "mbti_survey.html" in button_config:
                # return 语句返回 True 布尔值表示测试成功
                return True
            else:
                # return 语句返回 False 布尔值表示测试失败
                return False
        else:
            # return 语句返回 False 布尔值表示测试失败
            return False

    # except 捕获 Exception 异常类及其子类的异常实例
    # 异常对象赋值给变量 e
    except Exception as e:
        # print 函数通过传入异常信息字符串输出异常详情
        print(f"EXCEPTION: {str(e)}")
        # return 语句返回 False 布尔值表示测试失败
        return False


async def simulate_survey_click():
    """
    模拟用户点击survey链接
    检查mbti_survey.html文件是否存在并可访问
    """
    print("\n=== 模拟点击Survey链接 ===")

    html_path = os.path.join(os.path.dirname(__file__), "..", "mbti_survey.html")

    if os.path.exists(html_path):
        print(f"SURVEY FILE EXISTS: {html_path}")
        return True
    else:
        print(f"SURVEY FILE MISSING: {html_path}")
        return False


async def test_mbti_complete_flow():
    """
    测试完整的MBTI流程：从step1到最终获得测试结果
    第一阶段：测试数据库查询错误场景（预期失败）
    第二阶段：测试提供test_user_status的正确场景（预期成功）
    """
    # print 函数通过传入字符串输出测试开始信息
    print("=== STARTING MBTI COMPLETE FLOW TEST ===")

    # print 函数通过传入描述字符串输出第一阶段测试说明
    print("PHASE 1: Testing database query error scenario (expected failure)")
    # test_mbti_step1 函数被调用执行第一阶段测试
    # await 关键字等待异步函数完成，返回布尔结果赋值给 step1_success 变量
    step1_success = await test_mbti_step1()

    # if 条件判断检查 step1_success 变量的布尔值
    if not step1_success:
        # print 函数通过传入字符串输出第一阶段失败信息（这是预期的）
        print("✓ PHASE 1: Failed as expected, database error handling correct")
    else:
        # print 函数通过传入字符串输出意外成功的警告信息
        print("⚠ PHASE 1: Unexpected success, database query may have issues")

    # print 函数通过传入描述字符串输出第二阶段测试说明
    print("\nPHASE 2: Testing with test_user flag (expected success)")
    # test_mbti_step1_with_test_data 函数被调用执行第二阶段测试
    # await 关键字等待异步函数完成，返回布尔结果赋值给 step1_correct_success 变量
    step1_correct_success = await test_mbti_step1_with_test_data()
    
    # if 条件判断检查 step1_correct_success 变量的布尔值
    if not step1_correct_success:
        # print 函数通过传入字符串输出第二阶段失败信息并停止执行
        print("❌ 第二阶段失败，测试数据场景处理异常，停止执行")
        return False

    # Step 3: 模拟点击survey链接
    survey_success = await simulate_survey_click()
    if not survey_success:
        return False

    # Step 4: 生成随机答案并提交
    print("\n=== 生成随机测试答案 ===")
    responses = await generate_random_responses()
    print(f"已生成 {len(responses)} 道题目的随机答案")

    # 构建测试请求数据，模拟前端提交格式
    # 使用从step1生成的request ID作为request_id，验证request ID在各step间的传递
    global generated_request_id
    if generated_request_id:
        request_id = generated_request_id
        print(f"使用从step1生成的request ID: {request_id}")
    else:
        request_id = Time.timestamp()
        print(f"未获取到step1生成的request ID，使用新生成timestamp_uuid: {request_id}")

    test_request = {
        "intent": "mbti_step2",  # intent 字段设为 "mbti_step2"
        "responses": responses,  # responses 字段赋值为生成的随机答案字典
        "user_id": "test_user_123",  # user_id 字段设为测试用户ID
        "request_id": request_id  # 使用从step1生成的UUID或新生成UUID
    }

    # json.dumps 函数通过传入 test_request 字典和 indent 参数格式化输出
    # indent 赋值为 2 用于缩进，输出完整的请求数据结构
    print("STEP2 REQUEST DATA:")
    print(json.dumps(test_request, indent=2))

    try:
        # mbti.run 函数通过传入 test_request 字典参数被调用
        # await 关键字等待异步函数执行完成，返回结果赋值给 result 变量
        # 遵循正确架构：测试脚本 → mbti.py → router.py → step2.py
        result = await mbti.run(test_request)

        # json.dumps 函数通过传入 result 字典和 indent 参数格式化输出
        # indent 赋值为 2 用于缩进，输出完整的响应数据结构
        print("STEP2 RESPONSE DATA:")
        print(json.dumps(result, indent=2))

        # 检查返回结果的success字段
        if result.get("success"):
            # 从step2结果中提取MBTI类型，用于传递给step3-5测试
            mbti_result = result.get("mbti_result", {})
            mbti_type = mbti_result.get("mbti_type")
            if mbti_type:
                print(f"从step2获得MBTI类型: {mbti_type}")
                # 将MBTI类型存储为全局变量，供后续测试使用
                global step2_mbti_type
                step2_mbti_type = mbti_type
            return True
        else:
            return False

    except Exception as e:
        print(f"STEP2 EXCEPTION: {str(e)}")
        return False


async def main():
    """
    主函数，执行完整的MBTI流程测试
    从step1开始到获得最终测试结果
    """
    print("STARTING MBTI COMPLETE FLOW TEST")
    print("=" * 50)

    # 先执行request ID验证测试
    print("PHASE 0: Testing request ID validation")
    request_id_test_success = await test_request_id_validation()
    if not request_id_test_success:
        print("❌ request ID验证测试失败，终止后续测试")
        sys.exit(1)
    else:
        print("✓ request ID验证测试通过")

    # 执行完整的MBTI流程测试
    success = await test_mbti_complete_flow()

    print("\n" + "=" * 50)
    if success:
        print("FINAL RESULT: COMPLETE MBTI FLOW TEST PASSED")

        # 联动运行step3-5测试
        print("\n" + "=" * 50)
        print("STARTING STEP3-5 INTEGRATION TEST")
        print("=" * 50)

        try:
            # 动态导入并运行step3-5测试
            step3_5_test_path = os.path.join(os.path.dirname(__file__), "test_mbti_entry_3_4_5.py")
            spec = importlib.util.spec_from_file_location("test_mbti_entry_3_4_5", step3_5_test_path)
            step3_5_test = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(step3_5_test)

            # 运行step3-5测试，传递从step2获得的MBTI类型
            print(f"传递MBTI类型给step3-5测试: {step2_mbti_type}")
            step3_5_success = await step3_5_test.test_mbti_step3_to_5_flow(step2_mbti_type)
            if step3_5_success:
                print("FINAL RESULT: STEP3-5 INTEGRATION TEST PASSED")
            else:
                print("FINAL RESULT: STEP3-5 INTEGRATION TEST FAILED")
                success = False

        except Exception as e:
            print(f"EXCEPTION: Failed to run step3-5 test: {str(e)}")
            success = False

    else:
        print("FINAL RESULT: COMPLETE MBTI FLOW TEST FAILED")

    # 根据测试结果设置退出代码
    sys.exit(0 if success else 1)


# if __name__ == "__main__" 条件判断当前脚本是否作为主程序运行
if __name__ == "__main__":
    # asyncio.run 函数通过传入 main() 函数启动异步事件循环
    asyncio.run(main())