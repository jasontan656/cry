#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
step3.py - MBTI反向能力测试表单生成器（流程驱动版本）
"""

# import 语句通过 json 模块名导入用于JSON数据读取和解析操作
import json
# import 语句通过 os 模块名导入用于文件路径处理操作
import os
# import 语句通过 re 模块名导入用于request ID格式验证的正则表达式操作
import re
# import 语句通过 sys 模块名导入用于路径操作
import sys
# from...import 语句通过 typing 模块导入类型提示工具，使用精确类型定义和Any类型
from typing import Dict, List, Union, Optional, Any

# 添加上级目录到Python路径，以便导入utilities和hub模块
parent_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, parent_dir)

# 从utilities模块导入Time类，用于生成带时间戳的request ID
# 使用绝对导入路径utilities.time.Time确保跨环境兼容性
from utilities.time import Time

# 导入流程状态管理模块
from hub.status import UserFlowState, user_status_manager


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


def validate_request_id(request_id: str) -> str:
    """
    验证传入的request_id是否为有效的timestamp_uuid格式
    Args:
        request_id: 待验证的request_id字符串
    Returns:
        str: 验证通过的request ID字符串
    Raises:
        ValueError: 当request ID格式无效时抛出异常
    """
    # if 条件判断检查 request_id 是否为空值或空字符串
    if not request_id:
        # raise 语句抛出 ValueError 异常，传入错误信息字符串
        raise ValueError("Request ID is required and cannot be empty")

    # if 条件判断检查 request_id 是否为有效的timestamp_uuid格式
    if not is_valid_request_id(request_id):
        # raise 语句抛出 ValueError 异常，传入包含无效request ID的错误信息字符串
        raise ValueError(f"Invalid request ID format: {request_id}. Request rejected for security reasons.")

    # return 语句返回验证通过的request ID字符串
    return request_id


# 通过 class 定义 MbtiReverseQuestion 类型字典，包含单个反向问题结构的精确类型字段
class MbtiReverseQuestion:
    """反向问题数据结构"""
    def __init__(self, question_id: int, text: str, options: Dict[str, str]):
        # question_id 字段定义为 int 类型，用于存储问题的唯一标识符
        self.question_id = question_id
        # text 字段定义为 str 类型，用于存储问题文本内容
        self.text = text
        # options 字段定义为 Dict[str, str] 类型，用于存储选项键值对
        self.options = options


async def process(request: Dict[str, Union[str, int, bool, None]]) -> Dict[str, Union[str, bool, int, List, Dict]]:
    """
    处理MBTI反向能力测试表单生成请求
    Args:
        request: 包含用户ID、MBTI类型等信息的请求字典
    Returns:
        包含表单schema和配置的完整结果
    """
    # try 块开始尝试执行主要处理逻辑，捕获可能的异常
    try:
        # validate_request_id 函数通过传入 request.get("request_id") 验证request_id格式
        # 如果UUID格式无效，立即抛出异常拒绝服务
        request_id = validate_request_id(request.get("request_id"))

        # request.get 方法通过传入 "user_id" 键获取用户标识符
        user_id = request.get("user_id")
        # request.get 方法通过传入 "mbti_type" 键获取用户的MBTI类型字符串
        mbti_type = request.get("mbti_type")

        # if 条件判断检查 mbti_type 是否为空值或非字符串类型
        if not mbti_type or not isinstance(mbti_type, str) or len(mbti_type) != 4:
            # return 语句返回包含错误信息的响应字典
            return {
                "request_id": request_id,
                "user_id": user_id,
                "success": False,
                "step": "mbti_step3",
                "error_message": "Invalid MBTI type provided"
            }

        # _load_reverse_questions 函数通过调用加载反向问题数据
        # 返回包含所有反向问题的字典结构，赋值给 questions_data 变量
        questions_data = _load_reverse_questions()
        
        # _get_reverse_dimensions 函数通过传入 mbti_type 参数计算反向维度
        # 返回包含4个反向维度字符的列表，赋值给 reverse_dimensions 变量
        reverse_dimensions = _get_reverse_dimensions(mbti_type)
        
        # _extract_questions 函数通过传入 questions_data 和 reverse_dimensions 参数
        # 从问题库中提取对应维度的问题，返回问题列表赋值给 selected_questions 变量
        selected_questions = _extract_questions(questions_data, reverse_dimensions)
        
        # _generate_form_schema 函数通过传入 selected_questions 参数
        # 生成前端表单渲染所需的JSON schema，赋值给 form_schema 变量
        form_schema = _generate_form_schema(selected_questions)

        # return 语句返回包含完整表单配置的响应字典
        return {
            "request_id": request_id,
            "user_id": user_id,
            "success": True,
            "step": "mbti_step3",
            "mbti_type": mbti_type,
            "reverse_dimensions": reverse_dimensions,
            "form_schema": form_schema,
            "questions_count": len(selected_questions),
            "next_step": "mbti_step4"
        }

    # except 捕获 Exception 异常，当系统异常发生时执行
    except Exception as e:
        # return 语句返回包含异常信息的错误响应字典
        return {
            "request_id": request.get("request_id"),
            "user_id": request.get("user_id"),
            "success": False,
            "step": "mbti_step3",
            "error_message": f"处理异常: {str(e)}"
        }


def _load_reverse_questions() -> Dict:
    """加载反向问题数据文件"""
    # try 块开始尝试执行文件读取操作，捕获可能的异常
    try:
        # os.path.dirname 函数通过传入 os.path.abspath(__file__) 获取当前脚本所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # os.path.join 函数通过传入目录路径和文件名拼接完整文件路径
        file_path = os.path.join(current_dir, 'step3_mbti_reversed_questions.json')
        # with open() 语句以只读模式打开文件，指定 utf-8 编码，赋值给变量 f
        with open(file_path, 'r', encoding='utf-8') as f:
            # json.load 函数通过传入文件对象 f 解析JSON数据，返回字典对象
            return json.load(f)
    # except 捕获 FileNotFoundError 异常，当文件不存在时执行
    except FileNotFoundError:
        # raise 语句抛出新的 FileNotFoundError 异常，传入自定义错误信息字符串
        raise FileNotFoundError("step3_mbti_reversed_questions.json not found")


def _get_reverse_dimensions(mbti_type: str) -> List[str]:
    """
    根据MBTI类型计算反向维度
    Args:
        mbti_type: 4位MBTI类型字符串，如"INTJ"
    Returns:
        包含4个反向维度的列表，如["E", "S", "F", "P"]
    """
    # DIMENSION_REVERSE_MAP 通过字典创建常量，存储MBTI维度的反向映射关系
    DIMENSION_REVERSE_MAP = {
        'I': 'E',  # 内向(I) 的反向是 外向(E)
        'E': 'I',  # 外向(E) 的反向是 内向(I)
        'N': 'S',  # 直觉(N) 的反向是 感觉(S)
        'S': 'N',  # 感觉(S) 的反向是 直觉(N)
        'F': 'T',  # 情感(F) 的反向是 思考(T)
        'T': 'F',  # 思考(T) 的反向是 情感(F)
        'P': 'J',  # 感知(P) 的反向是 判断(J)
        'J': 'P'   # 判断(J) 的反向是 感知(P)
    }
    
    # reverse_dimensions 通过列表推导式创建反向维度列表
    # for char in mbti_type 遍历MBTI类型的每个字符
    # DIMENSION_REVERSE_MAP[char] 通过字符索引获取对应的反向维度字符
    reverse_dimensions = [DIMENSION_REVERSE_MAP[char] for char in mbti_type]
    
    # return 语句返回包含4个反向维度字符的列表
    return reverse_dimensions


def _extract_questions(questions_data: Dict, reverse_dimensions: List[str]) -> List[MbtiReverseQuestion]:
    """
    从问题库中提取指定维度的问题
    Args:
        questions_data: 完整的问题数据字典
        reverse_dimensions: 需要提取的反向维度列表
    Returns:
        包含选中问题的MbtiReverseQuestion对象列表
    """
    # selected_questions 通过列表初始化，用于存储提取出的问题对象
    selected_questions = []
    
    # for dimension in reverse_dimensions 遍历需要提取的每个反向维度
    for dimension in reverse_dimensions:
        # questions_data.get 方法通过传入 "dimensionAssessments" 键获取维度评估数据
        # 返回包含所有维度评估的列表，赋值给 dimension_assessments 变量
        dimension_assessments = questions_data.get("dimensionAssessments", [])
        
        # for assessment in dimension_assessments 遍历每个维度评估数据
        for assessment in dimension_assessments:
            # assessment.get 方法通过传入 "assessedAbility" 键获取被评估的能力维度
            assessed_ability = assessment.get("assessedAbility")
            
            # if 条件判断检查被评估能力是否包含当前需要的反向维度
            if assessed_ability and f"{dimension} (" in assessed_ability:
                # assessment.get 方法通过传入 "questions" 键获取该维度的问题列表
                questions = assessment.get("questions", [])
                
                # for question in questions 遍历该维度的每个问题
                for question in questions:
                    # MbtiReverseQuestion 构造函数通过传入问题数据创建问题对象
                    # question.get 方法分别获取问题ID、文本和选项数据
                    # 创建的对象添加到 selected_questions 列表中
                    selected_questions.append(MbtiReverseQuestion(
                        question_id=question.get("reverse_questions_id"),
                        text=question.get("reverse_questions_text"),
                        options=question.get("reverse_questions_options", {})
                    ))
                # break 语句跳出当前循环，找到匹配维度后不再继续查找
                break
    
    # return 语句返回包含所有选中问题对象的列表
    return selected_questions


def _generate_form_schema(questions: List[MbtiReverseQuestion]) -> Dict:
    """
    生成前端表单渲染所需的JSON schema
    Args:
        questions: MbtiReverseQuestion对象列表
    Returns:
        包含完整表单配置的字典
    """
    # form_fields 通过列表初始化，用于存储所有表单字段配置
    form_fields = []
    
    # for i, question in enumerate(questions) 遍历问题列表，获取索引和问题对象
    for i, question in enumerate(questions):
        # field_config 通过字典创建单个字段的配置结构
        field_config = {
            # "field_id" 键通过 f"question_{i}" 格式化字符串生成字段唯一标识符
            "field_id": f"question_{i}",
            # "question_id" 键赋值为 question.question_id，存储问题的原始ID
            "question_id": question.question_id,
            # "field_type" 键设为 "radio"，指定字段类型为单选框
            "field_type": "radio",
            # "label" 键赋值为 question.text，存储问题文本作为字段标签
            "label": question.text,
            # "required" 键设为 True，指定该字段为必填项
            "required": True,
            # "options" 键通过列表推导式转换问题选项格式
            # for key, value in question.options.items() 遍历选项键值对
            # 生成包含 "value" 和 "label" 的字典结构
            "options": [
                {"value": key, "label": value} 
                for key, value in question.options.items()
            ],
            # "validation" 键包含字段验证规则配置
            "validation": {
                "required": True,
                "message": "请选择一个答案"
            }
        }
        # form_fields.append 方法将字段配置添加到表单字段列表中
        form_fields.append(field_config)
    
    # schema 通过字典创建完整的表单schema结构
    schema = {
        # "form_title" 键设置表单标题文本
        "form_title": "MBTI反向能力评估测试",
        # "form_description" 键设置表单描述文本
        "form_description": "请根据您的实际情况选择最符合的答案，每题都需要作答",
        # "fields" 键赋值为 form_fields 列表，包含所有字段配置
        "fields": form_fields,
        # "submit_config" 键包含提交按钮和处理配置
        "submit_config": {
            "button_text": "提交测试",
            "next_step": "mbti_step4",
            "validation_message": "请确保所有问题都已作答"
        },
        # "draft_save" 键包含草稿保存配置
        "draft_save": {
            "enabled": True,
            "storage_key": "mbti_step3_draft",
            "auto_save_interval": 30
        }
    }
    
    # return 语句返回完整的表单schema字典
    return schema
