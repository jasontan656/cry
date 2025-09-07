# test_mbti_entry_3_4_5.py - MBTI step3-5 完整流程自动化测试脚本
# 职责：模拟用户完成step3表单填写，验证step4自动计分和step5报告生成

import asyncio  # asyncio 通过 import 导入异步编程模块
import random  # random 通过 import 导入随机数生成模块
import sys  # sys 通过 import 导入系统模块
import os  # os 通过 import 导入操作系统模块
import json  # json 通过 import 导入JSON处理模块
import re  # re 通过 import 导入正则表达式模块，用于request ID格式验证

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

# 直接导入step模块进行测试
import importlib.util
import types

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


def resolve_mbti_type(input_type=None):
    """
    独立业务逻辑：处理MBTI类型的生成或承接
    这是文件头部的核心业务逻辑，负责MBTI类型的统一处理

    Args:
        input_type: 从外部传入的MBTI类型，如果为None则随机生成

    Returns:
        str: 处理后的MBTI类型字符串
    """
    # 如果没有传入MBTI类型，则从16种类型中随机选择一个
    if input_type is None:
        # 完整的16种MBTI类型列表
        all_mbti_types = [
            "INTJ", "INTP", "ENTJ", "ENTP",
            "INFJ", "INFP", "ENFJ", "ENFP",
            "ISTJ", "ISFJ", "ESTJ", "ESFJ",
            "ISTP", "ISFP", "ESTP", "ESFP"
        ]
        # 从列表中随机选择一个类型
        input_type = random.choice(all_mbti_types)

    # 返回处理后的MBTI类型
    return input_type


def generate_random_reverse_responses():
    """
    生成随机反向能力测试答案
    返回包含12道反向问题的随机答案字典
    """
    # responses 变量通过字典推导式创建，包含12道反向问题
    # random.choice 函数从["A", "B"]中随机选择答案
    responses = {f"question_{i}": random.choice(["A", "B"]) for i in range(12)}
    # 返回生成的responses字典
    return responses


async def test_mbti_step3(mbti_type):
    """
    测试MBTI Step3流程
    验证step3根据MBTI类型生成反向问题表单schema
    Args:
        mbti_type: MBTI类型（已在上层函数中生成）
    """
    # 构建测试请求数据字典，包含intent、user_id、request_id、mbti_type四个键
    # intent 键赋值为 "mbti_step3" 字符串，指定路由到step3处理器
    # user_id 键赋值为 "test_user_123" 字符串，作为测试用户标识
    # request_id 使用 Time.timestamp() 生成带时间戳的request ID
    # mbti_type 键赋值为传入的MBTI类型
    test_request = {
        "intent": "mbti_step3",
        "user_id": "test_user_123",
        "request_id": Time.timestamp(),
        "mbti_type": mbti_type
    }

    # json.dumps 函数通过传入 test_request 字典和 indent 参数格式化输出
    # indent 赋值为 2 用于缩进，输出完整的请求数据结构
    print("REQUEST DATA:")
    print(json.dumps(test_request, indent=2))

    # try 块开始异常处理，捕获可能出现的异常情况
    try:
        # mbti.run 函数通过传入 test_request 字典参数被调用
        # await 关键字等待异步函数执行完成，返回结果赋值给 result 变量
        # 遵循正确架构：测试脚本 → mbti.py → router.py → step3.py
        result = await mbti.run(test_request)

        # json.dumps 函数通过传入 result 字典和 indent 参数格式化输出
        # indent 赋值为 2 用于缩进，输出完整的响应数据结构
        print("RESPONSE DATA:")
        print(json.dumps(result, indent=2))

        # result.get 方法通过传入 "success" 键获取处理成功状态
        # 返回布尔值用于 if 条件判断
        if result.get("success"):
            # result.get 方法通过传入 "form_schema" 键获取表单schema
            form_schema = result.get("form_schema")
            # if 条件判断检查 form_schema 是否存在且包含 "fields"
            if form_schema and "fields" in form_schema:
                # len 函数计算 fields 列表长度
                fields_count = len(form_schema["fields"])
                # if 条件判断检查字段数量是否等于12
                if fields_count == 12:
                    # return 语句返回 True 布尔值表示测试成功
                    return True
                else:
                    # return 语句返回 False 布尔值表示测试失败
                    return False
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


async def test_mbti_step4_with_answers(mbti_type):
    """
    测试MBTI Step4流程
    验证step4接收用户答案，自动计分并触发step5生成报告
    Args:
        mbti_type: MBTI类型（已在上层函数中生成）
    """
    # 生成随机答案数据，模拟用户填写反向能力测试
    responses = generate_random_reverse_responses()

    # 构建测试请求数据字典，包含intent、user_id、request_id、mbti_type、responses五个键
    # intent 键赋值为 "mbti_step4" 字符串，指定路由到step4处理器
    # user_id 键赋值为 "test_user_123" 字符串，作为测试用户标识
    # request_id 使用 Time.timestamp() 生成带时间戳的request ID
    # mbti_type 键赋值为传入的MBTI类型
    # responses 键赋值为生成的随机答案字典
    test_request = {
        "intent": "mbti_step4",
        "user_id": "test_user_123",
        "request_id": Time.timestamp(),
        "mbti_type": mbti_type,
        "responses": responses
    }

    # json.dumps 函数通过传入 test_request 字典和 indent 参数格式化输出
    # indent 赋值为 2 用于缩进，输出完整的请求数据结构
    print("REQUEST DATA:")
    print(json.dumps(test_request, indent=2))

    # try 块开始异常处理，捕获可能出现的异常情况
    try:
        # mbti.run 函数通过传入 test_request 字典参数被调用
        # await 关键字等待异步函数执行完成，返回结果赋值给 result 变量
        # 遵循正确架构：测试脚本 → mbti.py → router.py → step4.py → step5.py
        result = await mbti.run(test_request)

        # json.dumps 函数通过传入 result 字典和 indent 参数格式化输出
        # indent 赋值为 2 用于缩进，输出完整的响应数据结构
        print("RESPONSE DATA:")
        print(json.dumps(result, indent=2))

        # result.get 方法通过传入 "success" 键获取处理成功状态
        # 返回布尔值用于 if 条件判断
        if result.get("success"):
            # result.get 方法通过传入 "step" 键获取当前步骤标识
            step = result.get("step")
            # if 条件判断检查步骤是否为 "mbti_step5"
            if step == "mbti_step5":
                # result.get 方法通过传入 "final_report" 键获取最终报告
                final_report = result.get("final_report")
                # if 条件判断检查最终报告是否存在
                if final_report:
                    # print 函数输出包含报告标题的成功信息
                    # return 语句返回 True 布尔值表示测试成功
                    return True
                else:
                    # return 语句返回 False 布尔值表示测试失败
                    return False
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


async def test_mbti_step3_missing_mbti_type():
    """
    测试MBTI Step3异常场景：缺失MBTI类型
    验证错误输入时的异常处理机制
    """
    # 构建测试请求数据字典，缺少mbti_type字段
    # intent 键赋值为 "mbti_step3" 字符串，指定路由到step3处理器
    # user_id 键赋值为 "test_user_123" 字符串，作为测试用户标识
    # request_id 使用 Time.timestamp() 生成有效的request ID（即使是错误测试）
    test_request = {
        "intent": "mbti_step3",
        "user_id": "test_user_123",
        "request_id": Time.timestamp()
        # 故意缺失mbti_type字段
    }

    # json.dumps 函数通过传入 test_request 字典和 indent 参数格式化输出
    # indent 赋值为 2 用于缩进，输出完整的请求数据结构
    print("REQUEST DATA:")
    print(json.dumps(test_request, indent=2))

    # try 块开始异常处理，捕获可能出现的异常情况
    try:
        # mbti.run 函数通过传入 test_request 字典参数被调用
        # await 关键字等待异步函数执行完成，返回结果赋值给 result 变量
        # 验证异常场景下的错误处理机制
        result = await mbti.run(test_request)

        # json.dumps 函数通过传入 result 字典和 indent 参数格式化输出
        # indent 赋值为 2 用于缩进，输出完整的响应数据结构
        print("RESPONSE DATA:")
        print(json.dumps(result, indent=2))

        # result.get 方法通过传入 "success" 键获取处理成功状态
        # 返回布尔值用于 if 条件判断
        if not result.get("success"):
            # result.get 方法通过传入 "error_message" 键获取错误信息
            error_message = result.get("error_message", "")
            # if 条件判断检查错误信息是否包含 "Invalid MBTI type"
            if "Invalid MBTI type" in error_message:
                # return 语句返回 True 布尔值表示异常处理正确
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


async def test_mbti_step4_empty_responses():
    """
    测试MBTI Step4异常场景：空答案数据
    验证缺失答案时的异常处理机制
    """
    # 构建测试请求数据字典，包含空的responses字段
    # intent 键赋值为 "mbti_step4" 字符串，指定路由到step4处理器
    # user_id 键赋值为 "test_user_123" 字符串，作为测试用户标识
    # request_id 使用 Time.timestamp() 生成有效的request ID（即使是错误测试）
    # mbti_type 键赋值为 "INTJ" 字符串，作为测试MBTI类型
    # responses 键赋值为空字典，模拟用户未填写任何答案
    test_request = {
        "intent": "mbti_step4",
        "user_id": "test_user_123",
        "request_id": Time.timestamp(),
        "mbti_type": "INTJ",
        "responses": {}  # 空答案数据
    }

    # json.dumps 函数通过传入 test_request 字典和 indent 参数格式化输出
    # indent 赋值为 2 用于缩进，输出完整的请求数据结构
    print("REQUEST DATA:")
    print(json.dumps(test_request, indent=2))

    # try 块开始异常处理，捕获可能出现的异常情况
    try:
        # mbti.run 函数通过传入 test_request 字典参数被调用
        # await 关键字等待异步函数执行完成，返回结果赋值给 result 变量
        # 验证异常场景下的错误处理机制
        result = await mbti.run(test_request)

        # json.dumps 函数通过传入 result 字典和 indent 参数格式化输出
        # indent 赋值为 2 用于缩进，输出完整的响应数据结构
        print("RESPONSE DATA:")
        print(json.dumps(result, indent=2))

        # result.get 方法通过传入 "success" 键获取处理成功状态
        # 返回布尔值用于 if 条件判断
        if not result.get("success"):
            # result.get 方法通过传入 "error_message" 键获取错误信息
            error_message = result.get("error_message", "")
            # if 条件判断检查错误信息是否包含 "Missing required parameters"
            if "Missing required parameters" in error_message:
                # return 语句返回 True 布尔值表示异常处理正确
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


async def test_mbti_step3_to_5_flow(mbti_type=None):
    """
    测试完整的MBTI step3-5流程
    第一阶段：测试错误输入场景（预期失败）
    第二阶段：测试标准输入场景（预期成功）
    Args:
        mbti_type: 从step2传入的MBTI类型，如果为None则随机生成
    """
    # 第一步：调用独立的MBTI类型处理业务逻辑
    mbti_type = resolve_mbti_type(mbti_type)

    # Phase 1: 测试异常场景

    # 测试step3缺失MBTI类型
    step3_error_test = await test_mbti_step3_missing_mbti_type()

    # 测试step4空答案数据
    step4_error_test = await test_mbti_step4_empty_responses()

    # 测试step3正常生成表单
    step3_success = await test_mbti_step3(mbti_type)
    if not step3_success:
        return False

    # 测试step4正常计分并生成报告
    step4_success = await test_mbti_step4_with_answers(mbti_type)
    if not step4_success:
        return False
    return True


# 独立的测试入口函数，供外部调用
async def main(mbti_type=None):
    """
    主函数，执行完整的MBTI step3-5流程测试
    可独立运行或被其他测试脚本调用
    Args:
        mbti_type: 从step2传入的MBTI类型，如果为None则随机生成
    """
    # 第一步：调用独立的MBTI类型处理业务逻辑
    resolved_mbti_type = resolve_mbti_type(mbti_type)

    # 执行完整的step3-5流程测试，使用处理后的MBTI类型
    success = await test_mbti_step3_to_5_flow(resolved_mbti_type)

    # 根据测试结果设置退出代码
    sys.exit(0 if success else 1)


# if __name__ == "__main__" 条件判断当前脚本是否作为主程序运行
if __name__ == "__main__":
    # asyncio.run 函数通过传入 main() 函数启动异步事件循环
    asyncio.run(main())
