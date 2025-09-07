"""
MBTI性格测试中心模块字段定义和数据加载
职责：读取step3_mbti_reversed_questions.json文件，定义字段规范（包括UUID字段类型），向validator提供字段定义，向中枢注入字段信息
"""

import json
import os
from typing import Dict, Union, List, Set, Optional  # 类型注解支持，使用精确类型定义


# 字段定义配置，意味着定义所有可用的字段类型和规范
FIELD_DEFINITIONS = {
    # 基础字段类型定义
    "field_types": {
        # 基础请求响应字段
        "request_id": "uuid",  # 请求唯一标识符（UUID格式）
        "user_id": "string",  # 用户标识符
        "step": "string",  # 测试步骤
        "response_data": "dict",  # 响应数据
        "error_message": "string",  # 错误信息
        "success": "bool",  # 成功标志
        "intent": "string",  # 请求意图标识符

        # 反向问题字段
        "reverse_questions_id": "int",  # 反向问题ID
        "reverse_questions_text": "string",  # 反向问题文本
        "reverse_questions_options": "dict",  # 反向问题选项

        # MBTI测试数据字段
        "test_user": "bool",  # 测试模式标识符
        "mbti_type": "string",  # MBTI类型
        "responses": "dict",  # 用户答案字典
        "reverse_dimensions": "list",  # 反向评估维度列表
        "dimension_scores": "dict",  # 维度得分字典
        "percentages": "dict",  # 百分比数据字典
        "dimension_details": "dict",  # 维度详细信息字典

        # 用户状态和完成状态字段
        "JobFindingRegistryComplete": "bool",  # 用户注册完成状态
        "mbti_step1_complete": "bool",  # step1完成状态
        "completed": "bool",  # 完成状态
        "completion_status": "string",  # 完成状态描述

        # 前端交互字段
        "form_schema": "dict",  # 前端表单schema
        "button_config": "string",  # 按钮配置
        "content": "string",  # 内容文本
        "query_fields": "list",  # 查询字段列表

        # 表单字段配置
        "field_id": "string",  # 字段唯一标识符
        "field_type": "string",  # 字段类型
        "question_id": "int",  # 问题ID
        "required": "bool",  # 是否必填
        "value": "string",  # 字段值

        # 问题处理字段
        "questions_count": "int",  # 问题数量
        "selected_questions": "list",  # 选定的问题列表
        "questions_data": "dict",  # 问题数据字典
        "output_templates": "dict",  # 输出模板字典

        # 结果字段
        "mbti_result": "dict",  # MBTI计算结果
        "final_report": "dict",  # 最终报告
        "report_sections": "list",  # 报告段落列表
        "section": "dict",  # 报告段落
        "analysis": "string",  # 性格分析文本

        # MBTI维度和类型字段
        "dimension_type": "string",  # MBTI维度类型
        "user_mbti_type": "string",  # 用户MBTI类型

        # 评估和评分字段
        "assessment_result": "dict",  # 评估结果
        "scoring_data": "dict",  # 评分数据
        "raw_scores": "dict",  # 原始得分数据

        # MBTI问题字段
        "mbti_questions": "list",  # MBTI问题列表
        "text": "string",  # 问题文本
        "mbti_questions_text": "string",  # MBTI问题文本（统一字段）
        "dimension": "string",  # 问题所属维度
        "reverse": "bool",  # 是否为反向问题

        # JSON元数据字段
        "purpose": "string",  # 文档目的描述
        "testCoreLogic": "dict",  # 测试核心逻辑
        "title": "string",  # 标题
        "description": "string",  # 描述
        "example": "dict",  # 示例
        "userType": "string",  # 用户类型
        "evaluatedAbilities": "list",  # 评估能力列表
        "dimensionAssessments": "list",  # 维度评估列表
        "targetUserType": "string",  # 目标用户类型
        "assessedAbility": "string",  # 评估能力

        # 维度详情字段
        "score": "int",  # 分数
        "percentage": "int",  # 百分比
        "direction": "string",  # 方向
        "preference": "string",  # 偏好
        "opposite": "string",  # 对立面

        # MBTI类型定义字段
        "mbti_types": "dict",  # MBTI类型字典
        "ISTJ": "dict", "ISFJ": "dict", "INFJ": "dict", "INTJ": "dict",  # 内向判断型
        "ISTP": "dict", "ISFP": "dict", "INFP": "dict", "INTP": "dict",  # 内向感知型
        "ESTP": "dict", "ESFP": "dict", "ENFP": "dict", "ENTP": "dict",  # 外向感知型
        "ESTJ": "dict", "ESFJ": "dict", "ENTJ": "dict", "ENFJ": "dict",  # 外向判断型
        "label": "string",  # 类型标签
        "detail": "string",  # 类型详情

        # 评分指南字段
        "scoring_guide": "dict",  # 评分指南
        "generalScoringRules": "dict",  # 通用评分规则
        "scoreInterpretation": "list",  # 得分解释列表
        "range": "string",  # 分数范围
        "interpretation": "string",  # 解释内容
        "max_score": "int",  # 最高分
        "threshold": "int",  # 阈值
        "reverse_scoring": "string",  # 反向评分规则
        "percentage_calculation": "string",  # 百分比计算公式

        # 输出模板字段
        "outputTemplates": "dict",  # 输出模板字典
        "E_to_I": "list", "I_to_E": "list",  # 外向-内向转换
        "S_to_N": "list", "N_to_S": "list",  # 感知-直觉转换
        "T_to_F": "list", "F_to_T": "list",  # 思考-情感转换
        "J_to_P": "list", "P_to_J": "list",  # 判断-感知转换
        "scoreRange": "string",  # 分数范围
        "template": "string"  # 模板内容
    },

    # 字段分组定义
    "field_groups": {
        "request_fields": ["request_id", "user_id", "step", "intent"],  # 请求必需字段
        "response_fields": ["request_id", "success", "step"],  # 响应必需字段
        "reverse_question_fields": [
            "reverse_questions_id",
            "reverse_questions_text",
            "reverse_questions_options"
        ],  # 反向问题字段
        "mbti_test_fields": [
            "test_user",
            "mbti_type",
            "responses",
            "reverse_dimensions",
            "dimension_scores"
        ],  # MBTI测试数据字段

        "user_status_fields": [
            "JobFindingRegistryComplete",
            "mbti_step1_complete",
            "completed",
            "completion_status"
        ],  # 用户状态字段

        "ui_response_fields": [
            "form_schema",
            "button_config",
            "content",
            "query_fields",
            "questions_count",
            "selected_questions",
            "questions_data",
            "output_templates"
        ],  # 前端交互字段

        "form_field_config_fields": [
            "field_id",
            "field_type",
            "question_id",
            "required",
            "value"
        ],  # 表单字段配置

        "result_fields": [
            "mbti_result",
            "final_report",
            "report_sections",
            "section",
            "analysis"
        ],  # 结果字段
        "assessment_fields": [
            "dimension_type",
            "user_mbti_type",
            "assessment_result",
            "scoring_data",
            "raw_scores",
            "percentages",
            "dimension_details"
        ],  # 评估相关字段
        "question_fields": [
            "mbti_questions",
            "text",
            "mbti_questions_text",
            "dimension",
            "reverse",
            "purpose",
            "testCoreLogic",
            "title",
            "description",
            "example",
            "userType",
            "evaluatedAbilities",
            "dimensionAssessments",
            "targetUserType",
            "assessedAbility"
        ],  # 问题相关字段
        "dimension_detail_fields": [
            "score",
            "percentage",
            "direction",
            "preference",
            "opposite"
        ],  # 维度详情字段
        "mbti_type_fields": [
            "mbti_types",
            "label",
            "detail"
        ],  # MBTI类型定义字段
        "scoring_guide_fields": [
            "scoring_guide",
            "generalScoringRules",
            "scoreInterpretation",
            "range",
            "interpretation",
            "max_score",
            "threshold",
            "reverse_scoring",
            "percentage_calculation"
        ],  # 评分指南字段
        "output_template_fields": [
            "outputTemplates",
            "E_to_I", "I_to_E",
            "S_to_N", "N_to_S",
            "T_to_F", "F_to_T",
            "J_to_P", "P_to_J",
            "scoreRange",
            "template"
        ]  # 输出模板字段
    },

    # 步骤定义
    "steps": {
        "step1": {"description": "初始MBTI测试", "order": 1},
        "step2": {"description": "反向问题生成", "order": 2},
        "step3": {"description": "结果评估输出", "order": 3}
    }
}

# 字段注入配置，支持动态扩展
FIELD_INJECTIONS = {
    "injected_fields": [],  # 已注入的字段列表
    "target_modules": [],  # 目标模块列表
    "injection_metadata": {}  # 注入元数据
}


class SchemaManager:
    """
    字段定义管理器
    职责：管理字段定义，加载JSON数据，提供字段规范给validator使用
    """

    def __init__(self):
        """初始化字段定义管理器"""
        self.field_definitions = FIELD_DEFINITIONS.copy()  # 复制字段定义配置
        self.field_injections = FIELD_INJECTIONS.copy()  # 复制字段注入配置
        self.reverse_questions_data = self._load_reverse_questions_data()  # 加载反向问题数据
        self._inject_reverse_questions_fields()  # 注入反向问题字段定义

    def get_field_types(self) -> Dict[str, str]:
        """
        获取所有字段类型定义
        返回：字段名到类型的映射字典
        """
        return self.field_definitions["field_types"].copy()

    def get_field_groups(self) -> Dict[str, List[str]]:
        """
        获取字段分组定义
        返回：分组名到字段列表的映射字典
        """
        return self.field_definitions["field_groups"].copy()

    def get_steps(self) -> Dict[str, Dict[str, Union[str, int]]]:
        """
        获取步骤定义
        返回：步骤名到步骤信息的映射字典
        """
        return self.field_definitions["steps"].copy()

    def get_request_fields(self) -> List[str]:
        """
        获取请求必需字段列表
        返回：请求字段名称列表
        """
        return self.field_definitions["field_groups"]["request_fields"].copy()

    def get_response_fields(self) -> List[str]:
        """
        获取响应必需字段列表
        返回：响应字段名称列表
        """
        return self.field_definitions["field_groups"]["response_fields"].copy()

    def get_reverse_question_fields(self) -> List[str]:
        """
        获取反向问题字段列表
        返回：反向问题字段名称列表
        """
        return self.field_definitions["field_groups"]["reverse_question_fields"].copy()

    def get_assessment_fields(self) -> List[str]:
        """
        获取评估相关字段列表
        返回：评估字段名称列表
        """
        return self.field_definitions["field_groups"]["assessment_fields"].copy()

    def get_valid_steps(self) -> List[str]:
        """
        获取有效步骤列表
        返回：步骤名称列表
        """
        return list(self.field_definitions["steps"].keys())
    
    def _load_reverse_questions_data(self) -> Dict[str, Union[str, dict, list]]:
        """
        从step3_mbti_reversed_questions.json文件加载反向问题数据
        返回：解析后的JSON数据字典
        """
        json_path = os.path.join(os.path.dirname(__file__), "step3_mbti_reversed_questions.json")  # 构建JSON文件路径
        try:
            with open(json_path, 'r', encoding='utf-8') as f:  # 打开JSON文件
                return json.load(f)  # 解析JSON内容
        except FileNotFoundError:  # 处理文件不存在的情况
            raise RuntimeError(f"Step3 reversed questions JSON file not found: {json_path}")  # 抛出异常
        except json.JSONDecodeError as e:  # 处理JSON解析错误的情况
            raise RuntimeError(f"Invalid JSON in step3 reversed questions file: {e}")  # 抛出异常

    def _inject_reverse_questions_fields(self) -> None:
        """
        将反向问题JSON中的字段注入到字段定义中
        """
        # 从JSON数据中提取字段定义
        if "dimensionAssessments" in self.reverse_questions_data:
            for dimension in self.reverse_questions_data["dimensionAssessments"]:
                if "questions" in dimension:
                    for question in dimension["questions"]:
                        # 为每个问题字段添加类型定义
                        for field_key in question.keys():
                            if field_key not in self.field_definitions["field_types"]:
                                # 根据字段名推断类型
                                if "id" in field_key:
                                    field_type = "int"
                                elif "text" in field_key:
                                    field_type = "string"
                                elif "options" in field_key:
                                    field_type = "dict"
                                else:
                                    field_type = "string"

                                self.field_definitions["field_types"][field_key] = field_type
                                # 将反向问题字段添加到相应分组
                                if field_key not in self.field_definitions["field_groups"]["reverse_question_fields"]:
                                    self.field_definitions["field_groups"]["reverse_question_fields"].append(field_key)

    def inject_field(self, field_name: str, field_type: str, target_group: str = "custom") -> None:
        """
        注入新字段到字段定义中
        参数：字段名、字段类型、目标分组
        """
        # 添加字段类型定义
        self.field_definitions["field_types"][field_name] = field_type

        # 添加到指定分组
        if target_group not in self.field_definitions["field_groups"]:
            self.field_definitions["field_groups"][target_group] = []

        if field_name not in self.field_definitions["field_groups"][target_group]:
            self.field_definitions["field_groups"][target_group].append(field_name)

        # 记录注入信息
        self.field_injections["injected_fields"].append(field_name)

    def get_reverse_questions_data(self) -> Dict[str, Union[str, dict, list]]:
        """
        获取反向问题数据
        返回：完整的反向问题JSON数据
        """
        return self.reverse_questions_data.copy()

    def get_all_field_definitions(self) -> Dict[str, Union[Dict[str, Union[str, dict, list]], dict, list]]:
        """
        获取所有字段定义信息
        返回：包含所有字段定义的字典
        """
        return {
            "field_definitions": self.field_definitions,
            "reverse_questions_data": self.reverse_questions_data,
            "field_injections": self.field_injections,
            "metadata": {
                "version": "2.1.0",
                "module_name": "mbti",
                "questions_file": "step3_mbti_reversed_questions.json",
                "reverse_questions_loaded": True,
                "total_fields": len(self.field_definitions["field_types"])
            }
        }

    def inject_to_target_module(self, target_module: str) -> Dict[str, Union[str, dict, list]]:
        """
        向目标模块注入字段定义信息
        参数：目标模块名称
        返回：注入的字段信息字典
        """
        injection_data = {
            "field_definitions": self.field_definitions,
            "reverse_questions_data": self.reverse_questions_data,
            "target_module": target_module,
            "injection_timestamp": "auto-generated",
            "version": "2.1.0",
            "source_file": "step3_mbti_reversed_questions.json"
        }

        # 记录注入目标
        if target_module not in self.field_injections["target_modules"]:
            self.field_injections["target_modules"].append(target_module)

        self.field_injections["injection_metadata"][target_module] = {
            "timestamp": "auto-generated",
            "version": "2.1.0",
            "source_file": "step3_mbti_reversed_questions.json"
        }

        return injection_data


# 创建全局字段定义管理器实例
schema_manager = SchemaManager()

# 导出接口函数
def get_field_types() -> Dict[str, str]:
    """
    获取字段类型定义接口函数
    返回：字段名到类型的映射字典
    """
    return schema_manager.get_field_types()

def get_field_groups() -> Dict[str, List[str]]:
    """
    获取字段分组定义接口函数
    返回：分组名到字段列表的映射字典
    """
    return schema_manager.get_field_groups()

def get_request_fields() -> List[str]:
    """
    获取请求必需字段列表接口函数
    返回：请求字段名称列表
    """
    return schema_manager.get_request_fields()

def get_response_fields() -> List[str]:
    """
    获取响应必需字段列表接口函数
    返回：响应字段名称列表
    """
    return schema_manager.get_response_fields()

def get_reverse_question_fields() -> List[str]:
    """
    获取反向问题字段列表接口函数
    返回：反向问题字段名称列表
    """
    return schema_manager.get_reverse_question_fields()

def get_assessment_fields() -> List[str]:
    """
    获取评估相关字段列表接口函数
    返回：评估字段名称列表
    """
    return schema_manager.get_assessment_fields()

def get_valid_steps() -> List[str]:
    """
    获取有效步骤列表接口函数
    返回：步骤名称列表
    """
    return schema_manager.get_valid_steps()

def get_reverse_questions_data() -> Dict[str, Union[str, dict, list]]:
    """
    获取反向问题数据接口函数
    返回：完整的反向问题JSON数据
    """
    return schema_manager.get_reverse_questions_data()

def get_all_field_definitions() -> Dict[str, Union[Dict[str, Union[str, dict, list]], dict, list]]:
    """
    获取所有字段定义信息接口函数
    返回：包含所有字段定义的字典
    """
    return schema_manager.get_all_field_definitions()

def inject_field(field_name: str, field_type: str, target_group: str = "custom") -> None:
    """
    注入新字段接口函数
    参数：字段名、字段类型、目标分组
    """
    schema_manager.inject_field(field_name, field_type, target_group)

def inject_to_target_module(target_module: str) -> Dict[str, Union[str, dict, list]]:
    """
    向目标模块注入字段定义信息接口函数
    参数：目标模块名称
    返回：注入的字段信息字典
    """
    return schema_manager.inject_to_target_module(target_module)

