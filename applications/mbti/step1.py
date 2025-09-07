#!/usr/bin/env python3  # 指定Python3解释器运行这个脚本
# -*- coding: utf-8 -*-  # 声明文件使用UTF-8编码，支持中文字符
"""
step1.py - MBTI测试引导处理器  # 处理用户点击找工作按钮后的引导
"""

import re  # 导入正则表达式模块，用于request ID格式验证
from typing import Dict, Union  # 导入类型提示，使用Union替代Any
import sys  # 导入sys模块，用于路径操作
import os  # 导入os模块，用于路径操作

# 添加上级目录到Python路径，以便导入utilities模块
parent_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, parent_dir)

# 从utilities模块导入Time类，用于生成带时间戳的request ID
# 使用绝对导入路径utilities.time.Time确保跨环境兼容性
from utilities.time import Time

# import 语句通过 orchestrate_connector 模块名导入 process_orchestrate_request 函数
# 使用绝对导入方式，支持测试环境和独立运行环境
from applications.mbti.orchestrate_connector import process_orchestrate_request


def is_valid_request_id(request_id_string: str) -> bool:
    """
    验证字符串是否为有效的request ID格式（timestamp_uuid）
    Args:
        request_id_string: 待验证的字符串
    Returns:
        bool: 是否为有效request ID格式
    """
    # request_id_pattern 通过正则表达式定义timestamp_uuid格式
    # 格式：YYYY-MM-DDTHH:MM:SS+TZ_xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx
    request_id_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+\d{4}_[0-9a-f]{8}-[0-9a-f]{4}-[4][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
    # re.match 函数通过传入正则模式和字符串进行匹配，re.IGNORECASE 忽略大小写
    # bool 函数将匹配结果转换为布尔值返回
    return bool(re.match(request_id_pattern, str(request_id_string), re.IGNORECASE))


def validate_and_generate_request_id(provided_request_id: str = None) -> str:
    """
    验证传入的request_id或生成新的timestamp_uuid格式request ID
    Args:
        provided_request_id: 传入的request_id字符串，可为None或空字符串
    Returns:
        str: 有效的timestamp_uuid格式request ID字符串
    """
    # if 条件判断检查 provided_request_id 是否为空值或空字符串
    if not provided_request_id:
        # Time.timestamp() 通过Time类调用timestamp方法，生成timestamp_uuid格式的request ID
        return Time.timestamp()

    # if 条件判断检查 provided_request_id 是否为有效的timestamp_uuid格式
    if is_valid_request_id(provided_request_id):
        # return 语句返回验证通过的request ID字符串
        return provided_request_id
    else:
        # 传入的request_id格式无效，抛出异常拒绝服务
        raise ValueError(f"Invalid request ID format: {provided_request_id}. Request rejected for security reasons.")


async def process(request: Dict[str, Union[str, int, bool, None]]) -> Dict[str, Union[str, bool]]:
    """
    处理用户点击找工作按钮的请求
    返回测试引导信息和测试链接
    """
    # validate_and_generate_request_id 函数通过传入 request.get("request_id") 获取并验证request_id
    # 如果未传入或格式无效，则生成新的timestamp_uuid格式request ID；如果有效则直接使用
    request_id = validate_and_generate_request_id(request.get("request_id"))

    # 获取用户ID  # 从请求中提取用户标识
    user_id = request.get("user_id")

    # request.get 方法通过传入 "test_user" 键获取测试模式标识
    # 返回布尔值或 None，赋值给 test_user 变量
    test_user = request.get("test_user")

    # if 条件判断检查 test_user 变量是否为 True 布尔值
    if test_user is True:
        # 测试模式下使用预设的默认用户状态，跳过数据库查询
        # user_status 变量通过字典赋值设置默认测试状态
        user_status = {
            "JobFindingRegistryComplete": False,
            "mbti_step1_complete": False
        }
    else:
        # _check_user_completion_status 函数通过传入 user_id 参数被调用
        # await 关键字等待异步函数执行完成，返回查询结果赋值给 user_status 变量
        # 非测试模式下通过中枢查询数据库获取用户状态
        user_status = await _check_user_completion_status(user_id)

    # 根据用户状态决定下一步骤  # 检查JobFindingRegistryComplete字段决定处理方式
    if user_status.get("JobFindingRegistryComplete", False):
        # 用户已完成所有模块注册，返回orchestrate处理
        return {
            "request_id": request_id,  # 请求唯一标识符
            "user_id": user_id,  # 用户标识符
            "success": True,  # 处理成功标志
            "step": "orchestrate",  # 返回orchestrate处理
            "completed": True  # 完成状态布尔值
        }
    else:
        # 用户未完成所有模块注册，检查是否已完成step1
        step1_completed = user_status.get("mbti_step1_complete", False)

        # 如果step1已完成，返回布尔值给router调用step2处理
        if step1_completed:
            # 用户已完成step1，返回状态给router调用step2处理
            return {
                "request_id": request_id,  # 请求唯一标识符
                "user_id": user_id,  # 用户标识符
                "success": True,  # 处理成功标志
                "step": "mbti_step1",  # 当前步骤标识
                "completed": True,  # step1完成布尔值
                "next_step": "mbti_step2"  # 下一步骤标识
            }
        else:
            # 用户未完成step1，直接运行step1逻辑
            return await _handle_mbti_step_jump(request_id, user_id, 1)


async def _check_user_completion_status(user_id: str) -> Dict[str, Union[bool, int]]:
    """
    检查用户测试完成状态
    通过中枢查询数据库，获取JobFindingRegistryComplete和mbti_step1_complete字段
    如果数据库查询失败，抛出异常拒绝服务
    """
    # 构造数据库查询请求字典，包含intent、user_id、query_fields、table四个键
    # intent 键赋值为 "database_query" 字符串，表示数据库查询意图
    # user_id 键赋值为传入的 user_id 参数，作为用户标识符
    # query_fields 键赋值为包含两个字符串的列表，指定查询字段
    # table 键赋值为 "user_profile" 字符串，指定查询表名
    db_request = {
        "intent": "database_query",
        "user_id": user_id,
        "query_fields": ["JobFindingRegistryComplete", "mbti_step1_complete"],
        "table": "user_profile"
    }

    # process_orchestrate_request 函数通过传入 db_request 字典参数被调用
    # await 关键字等待异步函数执行完成，返回响应字典赋值给 db_response 变量
    db_response = await process_orchestrate_request(db_request)

    # db_response.get 方法通过传入 "success" 键和 False 默认值获取成功状态
    # 结果赋值给 success 变量，用于判断数据库查询是否成功
    success = db_response.get("success", False)
    
    # if 条件判断检查 success 变量的布尔值是否为假
    if not success:
        # db_response.get 方法通过传入 "error" 键和默认错误消息获取错误信息
        # 结果赋值给 error_message 变量
        error_message = db_response.get("error", "Database connection failed")
        # raise 语句抛出 Exception 异常，传入包含错误信息的格式化字符串
        # 拒绝服务而不是使用默认值继续执行
        raise Exception(f"Database query failed: {error_message}")

    # db_response.get 方法通过传入 "data" 键和包含默认状态的字典获取查询数据
    # 如果 data 键存在但值为空，使用默认值字典
    # 返回包含 JobFindingRegistryComplete 和 mbti_step1_complete 字段的字典
    return db_response.get("data", {"JobFindingRegistryComplete": False, "mbti_step1_complete": False})


async def _orchestrate_next_module(user_id: str) -> Dict[str, Union[str, bool]]:
    """
    编排下一个模块
    当用户完成所有MBTI测试后，通知中枢编排后续模块
    """
    # 构造编排请求  # 使用orchestrate_next_module intent向中枢发起请求
    orchestrate_request = {
        "intent": "orchestrate_next_module",  # 编排下一个模块意图
        "user_id": user_id,  # 用户标识符
        "current_module": "mbti",  # 当前模块标识
        "completion_status": "all_tests_completed"  # 完成状态
    }

    # 通过编排代理连接器向中枢发送请求  # 调用process_orchestrate_request函数，传入orchestrate_request参数
    orchestrate_response = await process_orchestrate_request(orchestrate_request)

    # 返回编排结果  # 如果编排失败，返回默认值
    return orchestrate_response.get("data", {"next_module": "unknown", "success": False})


async def _handle_mbti_step_jump(request_id: str, user_id: str, current_step: int) -> Dict[str, Union[str, bool]]:
    """
    处理MBTI step1引导逻辑
    当用户处于step1时，返回MBTI测试引导信息
    """
    # 确认当前步骤为step1  # 只有step1会调用此函数
    if current_step == 1:
        # 用户在MBTI step1，返回MBTI测试引导
        return {
            "request_id": request_id,  # 请求唯一标识符
            "user_id": user_id,  # 用户标识符
            "success": True,  # 处理成功标志
            "step": "mbti_step1",  # 当前步骤标识
            "button_config": "[Take Test](mbti_survey.html)",  # 测试按钮配置
            "next_step": "mbti_step2",  # 下一步骤标识
            "current_mbti_step": current_step  # 当前MBTI步骤
        }
    else:
        # 异常情况，不应该到达这里
        return {
            "request_id": request_id,  # 请求唯一标识符
            "user_id": user_id,  # 用户标识符
            "success": False,  # 处理失败标志
            "step": "error",  # 错误步骤标识
            "message": f"Unexpected step in _handle_mbti_step_jump: {current_step}",  # 错误消息
            "error_code": "UNEXPECTED_STEP"  # 错误码
        }
