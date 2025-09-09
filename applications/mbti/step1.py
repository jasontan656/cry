#!/usr/bin/env python3  # 指定Python3解释器运行这个脚本
# -*- coding: utf-8 -*-  # 声明文件使用UTF-8编码，支持中文字符
"""
step1.py - MBTI测试引导处理器（流程驱动版本）
MBTI测试第一步：接收用户请求，创建request_id，写入用户状态为ongoing，返回英文测试引导信息
按照hub/flow_example.py标准实现流程上下文支持和状态管理
"""

import re  # 导入正则表达式模块，用于request ID格式验证
from typing import Dict, Union, Any  # 导入类型提示，支持流程上下文字段
import sys  # 导入sys模块，用于路径操作
import os  # 导入os模块，用于路径操作

# 添加上级目录到Python路径，以便导入utilities和hub模块
parent_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, parent_dir)

# Time 通过绝对导入路径utilities.time.Time获取，用于生成带时间戳的request ID
from utilities.time import Time

# DatabaseOperations 通过绝对导入路径utilities.mongodb_connector.DatabaseOperations获取
# 用于执行数据库写入操作，设置用户MBTI测试状态
from utilities.mongodb_connector import DatabaseOperations

# 导入流程状态管理模块
from hub.status import UserFlowState, user_status_manager
from hub.registry_center import RegistryCenter



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


async def process(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    process 通过异步执行处理MBTI测试引导请求（流程驱动版本）
    先验证request_id并生成新ID，再使用user_status_manager创建流程状态，最后返回测试引导信息
    符合hub/flow_example.py的标准流程处理格式
    """
    try:
        # validate_and_generate_request_id 通过调用验证传入的request_id
        # 若无效或为空则生成新的timestamp_uuid格式ID，返回字符串赋值给request_id
        request_id = validate_and_generate_request_id(request.get("request_id"))

        # user_id 通过字典get方法从request获取用户标识符
        # 返回字符串或None，赋值给user_id变量用于后续状态管理
        user_id = request.get("user_id")
        
        # flow_id 通过字典get方法从request获取流程标识符
        # 默认值为"mbti_personality_test"，符合标准流程ID命名
        flow_id = request.get("flow_id", "mbti_personality_test")

        # === 创建或更新用户流程状态 ===
        
        # Time.timestamp() 通过调用Time类timestamp方法生成时间戳
        # 赋值给created_at变量，用于记录流程开始时间
        created_at = Time.timestamp()
        
        # UserFlowState 通过构造函数创建用户流程状态对象
        # 包含用户ID、流程ID、当前步骤、状态等完整信息
        user_state = UserFlowState(
            user_id=user_id,
            flow_id=flow_id,
            current_step="mbti_step1",
            last_completed_step="none",
            created_at=created_at,
            updated_at=created_at,
            status="ongoing"
        )
        
        # user_status_manager.save_user_flow_state 通过调用状态管理器
        # 传入user_state参数，创建或更新用户的流程状态记录
        await user_status_manager.save_user_flow_state(user_state)

        # _handle_mbti_step_jump 通过await调用异步函数，传入request_id、user_id、flow_id和步骤编号1
        # 返回包含测试引导信息的字典，包含预设的英文提示和测试链接
        return await _handle_mbti_step_jump(request_id, user_id, flow_id, 1)
        
    except Exception as e:
        # 捕获处理过程中的异常，返回标准化错误响应
        return {
            "request_id": request.get("request_id", "unknown"),
            "user_id": request.get("user_id"),
            "flow_id": request.get("flow_id", "mbti_personality_test"),
            "success": False,
            "step": "mbti_step1",
            "error_message": f"Step1处理异常: {str(e)}",
            "error_code": "STEP1_PROCESSING_ERROR"
        }



async def _handle_mbti_step_jump(request_id: str, user_id: str, flow_id: str, current_step: int) -> Dict[str, Any]:
    """
    _handle_mbti_step_jump 通过异步执行处理MBTI测试引导逻辑（流程驱动版本）
    根据步骤编号返回对应的测试引导信息和预设英文提示，包含流程上下文字段
    """
    # current_step 等于1时表示用户在MBTI第一步测试引导阶段
    # 返回包含request_id、user_id、flow_id、success状态和预设英文引导信息的字典
    if current_step == 1:
        return {
            "request_id": request_id,  # request_id 赋值给字典的request_id键，作为请求标识符
            "user_id": user_id,  # user_id 赋值给字典的user_id键，作为用户标识符
            "flow_id": flow_id,  # flow_id 赋值给字典的flow_id键，作为流程标识符
            "success": True,  # success 设置为True，表示处理成功
            "step": "mbti_step1",  # step 设置为字符串"mbti_step1"，标识当前步骤
            "message": "First, please complete the following scenario test so that we can better understand you. Please use the link below to access the test questions page.",  # message 赋值英文预设提示信息
            "button_config": "[Take Test](mbti_survey.html)",  # button_config 设置为测试链接配置，指向mbti_survey.html页面
            "next_step": "mbti_step2",  # next_step 设置为字符串"mbti_step2"，表示下一步骤标识
            "current_mbti_step": current_step  # current_mbti_step 赋值当前步骤编号1
        }
    else:
        # current_step 不等于1时表示异常情况，不应该到达此分支
        # 返回包含错误信息的字典，标识处理失败和异常步骤
        return {
            "request_id": request_id,  # request_id 赋值给字典的request_id键，保持请求标识符
            "user_id": user_id,  # user_id 赋值给字典的user_id键，保持用户标识符
            "flow_id": flow_id,  # flow_id 赋值给字典的flow_id键，保持流程标识符
            "success": False,  # success 设置为False，表示处理失败
            "step": "error",  # step 设置为字符串"error"，标识错误步骤
            "message": f"Unexpected step in _handle_mbti_step_jump: {current_step}",  # message 赋值格式化字符串，包含异常步骤信息
            "error_code": "UNEXPECTED_STEP"  # error_code 设置为字符串"UNEXPECTED_STEP"，标识错误类型
        }
