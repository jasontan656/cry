#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
step4.py - MBTI反向能力测试结果计算器
"""

# import 语句通过 json 模块名导入用于JSON数据读取和解析操作
import json
# import 语句通过 os 模块名导入用于文件路径处理操作
import os
# import 语句通过 re 模块名导入用于request ID格式验证的正则表达式操作
import re
# import 语句通过 sys 模块名导入用于路径操作
import sys
# from...import 语句通过 typing 模块导入类型提示工具，使用精确类型定义
from typing import Dict, List, Union, Optional

# 添加上级目录到Python路径，以便导入utilities模块
parent_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, parent_dir)

# 从utilities模块导入Time类，用于生成带时间戳的request ID
# 使用绝对导入路径utilities.time.Time确保跨环境兼容性
from utilities.time import Time


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


# 通过 class 定义 MbtiReverseScorer 类，封装反向能力计分功能的完整实现
class MbtiReverseScorer:
    """MBTI反向能力计分器"""

    # __init__ 方法在创建 MbtiReverseScorer 实例时自动调用，无需传入参数
    def __init__(self):
        # 通过 self._load_scoring_rules() 调用私有方法加载计分规则，赋值给实例变量
        self.scoring_rules = self._load_scoring_rules()

    # _load_scoring_rules 方法定义为私有方法，通过 -> Dict 返回计分规则字典
    def _load_scoring_rules(self) -> Dict:
        """加载计分规则数据"""
        # try 块开始尝试执行文件读取操作，捕获可能的异常
        try:
            # os.path.dirname 函数通过传入 os.path.abspath(__file__) 获取当前脚本所在目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # os.path.join 函数通过传入目录路径和文件名拼接完整文件路径
            file_path = os.path.join(current_dir, 'step4_mbti_reversed_questions_scoring.json')
            # with open() 语句以只读模式打开文件，指定 utf-8 编码，赋值给变量 f
            with open(file_path, 'r', encoding='utf-8') as f:
                # json.load 函数通过传入文件对象 f 解析JSON数据，返回字典对象
                return json.load(f)
        # except 捕获 FileNotFoundError 异常，当文件不存在时执行
        except FileNotFoundError:
            # raise 语句抛出新的 FileNotFoundError 异常，传入自定义错误信息字符串
            raise FileNotFoundError("step4_mbti_reversed_questions_scoring.json not found")

    # calculate_scores 方法接收 responses 和 reverse_dimensions 参数，返回计分结果字典
    def calculate_scores(self, responses: Dict[str, str], reverse_dimensions: List[str]) -> Dict[str, int]:
        """
        计算反向维度得分
        Args:
            responses: 用户答案字典，格式为 {question_id: answer}
            reverse_dimensions: 反向维度列表，如 ['E', 'S', 'F', 'P']
        Returns:
            各维度得分字典，格式为 {dimension: score}
        """
        # dimension_scores 通过字典初始化，创建反向维度的得分计数器，每个维度初始值设为0
        dimension_scores = {}
        # for dimension in reverse_dimensions 遍历每个反向维度字符
        for dimension in reverse_dimensions:
            # dimension_scores[dimension] 索引对应维度位置，将初始得分设为0
            dimension_scores[dimension] = 0

        # question_index 通过整数初始化为0，用作问题索引计数器
        question_index = 0
        # for dimension in reverse_dimensions 遍历每个反向维度字符
        for dimension in reverse_dimensions:
            # 每个维度有3道问题，需要累加得分
            # for i in range(3) 循环3次，处理每个维度的3道问题
            for i in range(3):
                # f"question_{question_index}" 通过格式化字符串生成问题ID
                question_id = f"question_{question_index}"
                # responses.get 方法通过传入问题ID获取用户答案，默认值为空字符串
                user_answer = responses.get(question_id, "")
                
                # if 条件判断检查用户答案是否为 "A"
                if user_answer == "A":
                    # dimension_scores[dimension] 索引对应维度位置，将得分累加1分
                    dimension_scores[dimension] += 1
                # elif 条件判断检查用户答案是否为 "B"  
                elif user_answer == "B":
                    # dimension_scores[dimension] 索引对应维度位置，得分保持不变（+0分）
                    dimension_scores[dimension] += 0
                
                # question_index 变量自增1，移动到下一道问题
                question_index += 1

        # return 语句返回包含各维度得分的字典
        return dimension_scores

    # get_score_interpretation 方法接收 score 参数，返回得分解释字符串
    def get_score_interpretation(self, score: int) -> str:
        """
        获取得分解释
        Args:
            score: 维度得分，范围0-3
        Returns:
            对应的能力解释文本
        """
        # self.scoring_rules.get 方法通过传入 "generalScoringRules" 键获取总体计分规则
        general_rules = self.scoring_rules.get("generalScoringRules", {})
        # general_rules.get 方法通过传入 "scoreInterpretation" 键获取得分解释列表
        interpretations = general_rules.get("scoreInterpretation", [])
        
        # for item in interpretations 遍历每个得分解释条目
        for item in interpretations:
            # item.get 方法通过传入 "range" 键获取得分范围字符串
            score_range = item.get("range", "")
            # if 条件判断检查得分是否在0-1分范围内
            if score <= 1 and "0-1" in score_range:
                # item.get 方法通过传入 "interpretation" 键返回对应解释文本
                return item.get("interpretation", "")
            # elif 条件判断检查得分是否等于2分
            elif score == 2 and "2 points" in score_range:
                # item.get 方法通过传入 "interpretation" 键返回对应解释文本
                return item.get("interpretation", "")
            # elif 条件判断检查得分是否等于3分
            elif score == 3 and "3 points" in score_range:
                # item.get 方法通过传入 "interpretation" 键返回对应解释文本
                return item.get("interpretation", "")
        
        # return 语句返回默认解释文本，当没有匹配的得分范围时使用
        return "Score interpretation not found"


async def process(request: Dict[str, Union[str, int, bool, None, Dict, List]]) -> Dict[str, Union[str, bool, int, List, Dict]]:
    """
    处理MBTI反向能力测试计分请求，自动联动step5生成报告
    Args:
        request: 包含用户ID、答案数据等信息的请求字典
    Returns:
        包含计分结果和最终报告的完整结果
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
        # request.get 方法通过传入 "responses" 键获取用户答案字典，默认值为空字典
        responses = request.get("responses", {})

        # if 条件判断检查必要参数是否存在
        if not mbti_type or not responses:
            # return 语句返回包含错误信息的响应字典
            return {
                "request_id": request_id,
                "user_id": user_id,
                "success": False,
                "step": "mbti_step4",
                "error_message": "Missing required parameters: mbti_type or responses"
            }

        # _get_reverse_dimensions 函数通过传入 mbti_type 参数计算反向维度列表
        reverse_dimensions = _get_reverse_dimensions(mbti_type)
        
        # MbtiReverseScorer 构造函数创建计分器实例，赋值给 scorer 变量
        scorer = MbtiReverseScorer()
        # scorer.calculate_scores 方法通过传入 responses 和 reverse_dimensions 参数计算得分
        dimension_scores = scorer.calculate_scores(responses, reverse_dimensions)
        
        # Step4职责：只返回反向问题计分结果，不调用Step5
        # 返回Step4自己的处理结果，供后续Step5使用
        return {
            "request_id": request_id,
            "user_id": user_id,
            "flow_id": request.get("flow_id", "mbti_personality_test"),
            "success": True,
            "step": "mbti_step4",
            "mbti_type": mbti_type,
            "reverse_dimensions": reverse_dimensions,
            "dimension_scores": dimension_scores,
            "completed": False  # Step4只是中间步骤，不是最终完成
        }

    # except 捕获 Exception 异常，当系统异常发生时执行
    except Exception as e:
        # return 语句返回包含异常信息的错误响应字典
        return {
            "request_id": request.get("request_id"),
            "user_id": request.get("user_id"),
            "success": False,
            "step": "mbti_step4",
            "error_message": f"处理异常: {str(e)}"
        }


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
