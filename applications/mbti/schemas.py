"""
MBTI性格测试中心模块字段定义和数据加载
职责：读取step2_questions.json文件，定义字段规范（包括UUID字段类型），向validator提供字段定义，向中枢注入字段信息
"""

import json
import os
from typing import Dict, Union, List, Set, Optional  # 类型注解支持，使用精确类型定义


# 字段定义配置，意味着定义所有可用的字段类型和规范
FIELD_DEFINITIONS = {
    # 基础字段类型定义
    "field_types": {
        "request_id": "uuid",  # 请求唯一标识符（UUID格式）
        "user_id": "string",  # 用户标识符
        "step": "string",  # 测试步骤
        "response_data": "dict",  # 响应数据
        "error_message": "string",  # 错误信息
        "success": "bool",  # 成功标志
        "reverse_questions_id": "int",  # 反向问题ID
        "reverse_questions_text": "string",  # 反向问题文本
        "reverse_questions_options": "dict",  # 反向问题选项
        "dimension_type": "string",  # MBTI维度类型
        "user_mbti_type": "string",  # 用户MBTI类型
        "assessment_result": "dict",  # 评估结果
        "scoring_data": "dict"  # 评分数据
    },

    # 字段分组定义
    "field_groups": {
        "request_fields": ["request_id", "user_id", "step"],  # 请求必需字段
        "response_fields": ["request_id", "success", "step"],  # 响应必需字段
        "reverse_question_fields": [
            "reverse_questions_id",
            "reverse_questions_text",
            "reverse_questions_options"
        ],  # 反向问题字段
        "assessment_fields": [
            "dimension_type",
            "user_mbti_type",
            "assessment_result",
            "scoring_data"
        ]  # 评估相关字段
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
        从step2_questions.json文件加载反向问题数据
        返回：解析后的JSON数据字典
        """
        json_path = os.path.join(os.path.dirname(__file__), "step2_questions.json")  # 构建JSON文件路径
        try:
            with open(json_path, 'r', encoding='utf-8') as f:  # 打开JSON文件
                return json.load(f)  # 解析JSON内容
        except FileNotFoundError:  # 处理文件不存在的情况
            raise RuntimeError(f"Step2 questions JSON file not found: {json_path}")  # 抛出异常
        except json.JSONDecodeError as e:  # 处理JSON解析错误的情况
            raise RuntimeError(f"Invalid JSON in step2 questions file: {e}")  # 抛出异常

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
                "questions_file": "step2_questions.json",
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
            "source_file": "step2_questions.json"
        }

        # 记录注入目标
        if target_module not in self.field_injections["target_modules"]:
            self.field_injections["target_modules"].append(target_module)

        self.field_injections["injection_metadata"][target_module] = {
            "timestamp": "auto-generated",
            "version": "2.1.0",
            "source_file": "step2_questions.json"
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

