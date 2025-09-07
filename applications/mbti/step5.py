#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
step5.py - MBTI反向能力测试最终报告生成器
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


# 通过 class 定义 MbtiReportGenerator 类，封装最终报告生成功能的完整实现
class MbtiReportGenerator:
    """MBTI反向能力测试报告生成器"""

    # __init__ 方法在创建 MbtiReportGenerator 实例时自动调用，无需传入参数
    def __init__(self):
        # 通过 self._load_output_templates() 调用私有方法加载输出模板，赋值给实例变量
        self.output_templates = self._load_output_templates()

    # _load_output_templates 方法定义为私有方法，通过 -> Dict 返回输出模板字典
    def _load_output_templates(self) -> Dict:
        """加载最终输出模板数据"""
        # try 块开始尝试执行文件读取操作，捕获可能的异常
        try:
            # os.path.dirname 函数通过传入 os.path.abspath(__file__) 获取当前脚本所在目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # os.path.join 函数通过传入目录路径和文件名拼接完整文件路径
            file_path = os.path.join(current_dir, 'step5_final_output_template.json')
            # with open() 语句以只读模式打开文件，指定 utf-8 编码，赋值给变量 f
            with open(file_path, 'r', encoding='utf-8') as f:
                # json.load 函数通过传入文件对象 f 解析JSON数据，返回字典对象
                return json.load(f)
        # except 捕获 FileNotFoundError 异常，当文件不存在时执行
        except FileNotFoundError:
            # raise 语句抛出新的 FileNotFoundError 异常，传入自定义错误信息字符串
            raise FileNotFoundError("step5_final_output_template.json not found")

    # generate_report 方法接收 mbti_type、reverse_dimensions、dimension_scores 参数
    def generate_report(self, mbti_type: str, reverse_dimensions: List[str], dimension_scores: Dict[str, int]) -> Dict[str, Union[str, List]]:
        """
        生成最终反向能力报告
        Args:
            mbti_type: 用户的MBTI类型，如"INTJ"
            reverse_dimensions: 反向维度列表，如["E", "S", "F", "P"]
            dimension_scores: 各维度得分字典，如{"E": 2, "S": 1, "F": 3, "P": 0}
        Returns:
            包含完整报告内容的字典
        """
        # report_sections 通过列表初始化，用于存储各维度的报告段落
        report_sections = []
        # self.output_templates.get 方法通过传入 "outputTemplates" 键获取输出模板字典
        templates = self.output_templates.get("outputTemplates", {})
        
        # for i, reverse_dim in enumerate(reverse_dimensions) 遍历反向维度列表，获取索引和维度字符
        for i, reverse_dim in enumerate(reverse_dimensions):
            # mbti_type[i] 通过索引获取原始MBTI类型的对应位置字符
            original_dim = mbti_type[i]
            # f"{original_dim}_to_{reverse_dim}" 通过格式化字符串生成模板键名
            template_key = f"{original_dim}_to_{reverse_dim}"
            # dimension_scores.get 方法通过传入反向维度获取该维度得分，默认值为0
            score = dimension_scores.get(reverse_dim, 0)
            
            # templates.get 方法通过传入模板键名获取该维度的模板列表，默认值为空列表
            dimension_templates = templates.get(template_key, [])
            # _select_template_by_score 方法通过传入模板列表和得分选择合适模板
            selected_template = self._select_template_by_score(dimension_templates, score)
            
            # if 条件判断检查是否成功选择到模板
            if selected_template:
                # section 通过字典创建单个维度的报告段落结构
                section = {
                    "dimension": f"{original_dim} → {reverse_dim}",  # 维度转换标识
                    "score": score,                                   # 该维度得分
                    "score_range": selected_template.get("scoreRange", ""),  # 得分范围
                    "content": selected_template.get("template", "")         # 报告内容文本
                }
                # report_sections.append 方法将段落字典添加到报告段落列表中
                report_sections.append(section)
        
        # report 通过字典创建完整的报告结构
        report = {
            "title": f"{mbti_type}类型反向能力评估报告",
            "mbti_type": mbti_type,
            "reverse_dimensions": reverse_dimensions,
            "dimension_scores": dimension_scores,
            "report_sections": report_sections,
            "summary": self._generate_summary(mbti_type, dimension_scores)
        }
        
        # return 语句返回包含完整报告内容的字典
        return report

    # _select_template_by_score 方法接收 templates 和 score 参数，返回选中的模板字典
    def _select_template_by_score(self, templates: List[Dict], score: int) -> Optional[Dict]:
        """
        根据得分选择合适的模板
        Args:
            templates: 该维度的模板列表
            score: 维度得分，范围0-3
        Returns:
            匹配的模板字典，如果没有匹配则返回None
        """
        # for template in templates 遍历模板列表中的每个模板字典
        for template in templates:
            # template.get 方法通过传入 "scoreRange" 键获取该模板的得分范围字符串
            score_range = template.get("scoreRange", "")
            
            # if 条件判断检查得分是否在0-1范围内且模板范围包含 "0-1"
            if score <= 1 and "0-1" in score_range:
                # return 语句返回匹配的模板字典
                return template
            # elif 条件判断检查得分是否等于2且模板范围包含 "2 points"
            elif score == 2 and "2 points" in score_range:
                # return 语句返回匹配的模板字典
                return template
            # elif 条件判断检查得分是否等于3且模板范围包含 "3 points"
            elif score == 3 and "3 points" in score_range:
                # return 语句返回匹配的模板字典
                return template
        
        # return 语句返回 None，当没有匹配的模板时
        return None

    # _generate_summary 方法接收 mbti_type 和 dimension_scores 参数，返回总结字符串
    def _generate_summary(self, mbti_type: str, dimension_scores: Dict[str, int]) -> str:
        """
        生成报告总结
        Args:
            mbti_type: 用户的MBTI类型
            dimension_scores: 各维度得分字典
        Returns:
            报告总结文本
        """
        # sum 函数通过传入 dimension_scores.values() 计算所有维度得分总和
        total_score = sum(dimension_scores.values())
        # len 函数通过传入 dimension_scores 计算维度数量
        avg_score = total_score / len(dimension_scores)
        
        # if 条件判断检查平均得分是否小于1.5
        if avg_score < 1.5:
            # flexibility_level 变量赋值为 "较低" 字符串
            flexibility_level = "较低"
            # summary_text 变量赋值为对应的总结文本
            summary_text = "你在反向能力方面表现出典型的偏好特征，建议通过有意识的练习来培养平衡能力。"
        # elif 条件判断检查平均得分是否小于2.5
        elif avg_score < 2.5:
            # flexibility_level 变量赋值为 "中等" 字符串
            flexibility_level = "中等"
            # summary_text 变量赋值为对应的总结文本
            summary_text = "你具备一定的反向能力，能在需要时调动非偏好技能，继续保持和发展这种平衡。"
        else:
            # flexibility_level 变量赋值为 "较高" 字符串
            flexibility_level = "较高"
            # summary_text 变量赋值为对应的总结文本
            summary_text = "你展现出出色的反向能力，能够灵活运用各种技能，注意避免过度切换造成的能量消耗。"
        
        # f-string 通过格式化字符串拼接完整的总结文本，包含MBTI类型、灵活性水平和总结内容
        return f"作为{mbti_type}类型，你的反向能力灵活性为{flexibility_level}水平。{summary_text}"


async def process(request: Dict[str, Union[str, int, bool, None, Dict, List]]) -> Dict[str, Union[str, bool, int, List, Dict]]:
    """
    处理最终报告生成请求，从step4接收计分结果生成报告
    Args:
        request: 包含step4计分结果的请求字典
    Returns:
        包含完整最终报告的结果字典
    """
    # try 块开始尝试执行主要处理逻辑，捕获可能的异常
    try:
        # validate_request_id 函数通过传入 request.get("request_id") 验证request_id格式
        # 如果UUID格式无效，立即抛出异常拒绝服务
        request_id = validate_request_id(request.get("request_id"))

        # request.get 方法通过传入各个键名获取必要的数据字段
        user_id = request.get("user_id")
        mbti_type = request.get("mbti_type")
        reverse_dimensions = request.get("reverse_dimensions", [])
        dimension_scores = request.get("dimension_scores", {})

        # if 条件判断检查必要参数是否存在
        if not mbti_type or not reverse_dimensions or not dimension_scores:
            # return 语句返回包含错误信息的响应字典
            return {
                "request_id": request_id,
                "user_id": user_id,
                "success": False,
                "step": "mbti_step5",
                "error_message": "Missing required parameters: mbti_type, reverse_dimensions or dimension_scores"
            }

        # MbtiReportGenerator 构造函数创建报告生成器实例，赋值给 generator 变量
        generator = MbtiReportGenerator()
        # generator.generate_report 方法通过传入参数生成完整报告
        final_report = generator.generate_report(mbti_type, reverse_dimensions, dimension_scores)

        # return 语句返回包含完整最终报告的响应字典
        return {
            "request_id": request_id,
            "user_id": user_id,
            "success": True,
            "step": "mbti_step5",
            "mbti_type": mbti_type,
            "dimension_scores": dimension_scores,
            "final_report": final_report,
            "completed": True
        }

    # except 捕获 Exception 异常，当系统异常发生时执行
    except Exception as e:
        # return 语句返回包含异常信息的错误响应字典
        return {
            "request_id": request.get("request_id"),
            "user_id": request.get("user_id"),
            "success": False,
            "step": "mbti_step5",
            "error_message": f"处理异常: {str(e)}"
        }
