"""
MBTI性格测试中心模块字段定义和数据加载（流程驱动版本）
职责：定义流程驱动架构所需的字段规范，支持5步骤MBTI流程，提供流程上下文字段定义
"""

import json
import os
from typing import Dict, Union, List, Set, Optional  # 类型注解支持，使用精确类型定义


# 字段定义配置，定义流程驱动架构所需的所有字段类型和规范
FIELD_DEFINITIONS = {
    # 基础字段类型定义
    "field_types": {
        # === 流程上下文字段（流程驱动架构核心字段） ===
        "flow_id": "string",  # 流程标识符，用于标识完整的MBTI测试流程
        "step_id": "string",  # 步骤标识符，用于标识当前处理步骤
        "user_id": "string",  # 用户标识符，用于关联用户状态
        "request_id": "string",  # 请求标识符（UUID格式），用于请求追踪
        
        # === 基础请求响应字段 ===
        "step": "string",  # 当前步骤标识符
        "intent": "string",  # 请求意图标识符
        "success": "bool",  # 处理成功标志
        "error_message": "string",  # 错误信息描述
        "error_code": "string",  # 错误代码标识
        "message": "string",  # 处理结果消息
        "next_step": "string",  # 下一步骤标识符
        "previous_step": "string",  # 前一步骤标识符
        "current_mbti_step": "int",  # 当前MBTI步骤编号
        
        # === 用户输入数据字段 ===
        "responses": "dict",  # 用户在step2中提交的问卷答案字典
        "reverse_responses": "dict",  # 用户在step4中提交的反向问题答案字典
        
        # === MBTI计算结果字段 ===
        "mbti_type": "string",  # MBTI类型结果（如ENFP）
        "confirmed_type": "string",  # 经过反向验证确认的MBTI类型
        "raw_scores": "dict",  # 各维度原始得分数据
        "percentages": "dict",  # 各维度百分比数据
        "dimension_details": "dict",  # 维度详细信息字典
        "mbti_result": "dict",  # 完整的MBTI计算结果
        
        # === 输出内容字段 ===
        "analysis": "string",  # step2生成的性格分析文本
        "reverse_questions": "list",  # step3生成的反向问题列表
        "final_report": "dict",  # step5生成的最终报告
        
        # === 前端交互字段 ===
        "button_config": "string",  # 按钮配置信息
        "form_schema": "dict",  # 前端表单结构定义
        "content": "string",  # 显示内容文本
        
        # === MBTI问题数据字段 ===
        "mbti_questions": "list",  # MBTI问题列表
        "text": "string",  # 问题文本内容
        "dimension": "string",  # 问题所属维度（E/S/T/J）
        "reverse": "bool",  # 是否为反向计分题目
        
        # === 反向问题相关字段 ===
        "reverse_questions_id": "int",  # 反向问题ID
        "reverse_questions_text": "string",  # 反向问题文本
        "reverse_questions_options": "dict",  # 反向问题选项
        "reverse_dimensions": "list",  # 反向评估维度列表
        
        # === 评估和评分字段 ===
        "assessment_result": "dict",  # 评估结果
        "scoring_data": "dict",  # 评分数据
        "dimension_scores": "dict",  # 维度得分字典
        
        # === 维度详情字段 ===
        "score": "int",  # 维度分数
        "percentage": "int",  # 维度百分比
        "direction": "string",  # 维度方向
        "preference": "string",  # 偏好方向
        "opposite": "string",  # 对立方向
        "preference_strength": "string",  # 偏好强度描述
        "z_score": "float",  # Z-Score值
        
        # === MBTI类型定义字段 ===
        "dimension_type": "string",  # MBTI维度类型
        "user_mbti_type": "string",  # 用户MBTI类型
        "mbti_types": "dict",  # MBTI类型字典
        "ISTJ": "dict", "ISFJ": "dict", "INFJ": "dict", "INTJ": "dict",  # 内向判断型
        "ISTP": "dict", "ISFP": "dict", "INFP": "dict", "INTP": "dict",  # 内向感知型
        "ESTP": "dict", "ESFP": "dict", "ENFP": "dict", "ENTP": "dict",  # 外向感知型
        "ESTJ": "dict", "ESFJ": "dict", "ENTJ": "dict", "ENFJ": "dict",  # 外向判断型
        "label": "string",  # 类型标签
        "detail": "string",  # 类型详情
        
        # === 用户状态字段 ===
        "test_user": "bool",  # 测试模式标识符
        "JobFindingRegistryComplete": "bool",  # 用户注册完成状态
        "mbti_step1_complete": "bool",  # step1完成状态
        "completed": "bool",  # 完成状态
        "completion_status": "string",  # 完成状态描述
        
        # === 表单字段配置 ===
        "field_id": "string",  # 字段唯一标识符
        "field_type": "string",  # 字段类型
        "question_id": "int",  # 问题ID
        "required": "bool",  # 是否必填
        "value": "string",  # 字段值
        "query_fields": "list",  # 查询字段列表
        
        # === 问题处理字段 ===
        "questions_count": "int",  # 问题数量
        "selected_questions": "list",  # 选定的问题列表
        "questions_data": "dict",  # 问题数据字典
        "output_templates": "dict",  # 输出模板字典
        
        # === 报告相关字段 ===
        "report_sections": "list",  # 报告段落列表
        "section": "dict",  # 报告段落
        
        # === JSON元数据字段 ===
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
        
        # === 评分指南字段 ===
        "scoring_guide": "dict",  # 评分指南
        "generalScoringRules": "dict",  # 通用评分规则
        "scoreInterpretation": "list",  # 得分解释列表
        "range": "string",  # 分数范围
        "interpretation": "string",  # 解释内容
        "max_score": "int",  # 最高分
        "threshold": "int",  # 阈值
        "reverse_scoring": "string",  # 反向评分规则
        "percentage_calculation": "string",  # 百分比计算公式
        
        # === 输出模板字段 ===
        "outputTemplates": "dict",  # 输出模板字典
        "E_to_I": "list", "I_to_E": "list",  # 外向-内向转换
        "S_to_N": "list", "N_to_S": "list",  # 感知-直觉转换
        "T_to_F": "list", "F_to_T": "list",  # 思考-情感转换
        "J_to_P": "list", "P_to_J": "list",  # 判断-感知转换
        "scoreRange": "string",  # 分数范围
        "template": "string"  # 模板内容
    },

    # 字段分组定义（按功能分组）
    "field_groups": {
        # 流程上下文字段组 - 流程驱动架构核心字段
        "flow_context_fields": [
            "flow_id", "step_id", "user_id", "request_id"
        ],
        
        # 基础请求字段组 - 每个步骤处理的基础输入字段
        "request_fields": [
            "user_id", "request_id", "flow_id", "step", "intent"
        ],
        
        # 基础响应字段组 - 每个步骤返回的基础输出字段
        "response_fields": [
            "request_id", "user_id", "flow_id", "success", "step"
        ],
        
        # 步骤控制字段组 - 步骤流转控制字段
        "step_control_fields": [
            "next_step", "previous_step", "current_mbti_step"
        ],
        
        # 用户输入字段组 - 用户提交的答案数据
        "user_input_fields": [
            "responses", "reverse_responses"
        ],
        
        # MBTI结果字段组 - MBTI计算和分析结果
        "mbti_result_fields": [
            "mbti_type", "confirmed_type", "raw_scores", "percentages", 
            "dimension_details", "mbti_result"
        ],
        
        # 输出内容字段组 - 返回给用户的内容
        "output_content_fields": [
            "analysis", "reverse_questions", "final_report", "message"
        ],
        
        # 前端交互字段组 - 前端界面相关字段
        "ui_interaction_fields": [
            "button_config", "form_schema", "content"
        ],
        
        # 反向问题字段组 - step3和step4使用的反向问题相关字段
        "reverse_question_fields": [
            "reverse_questions_id", "reverse_questions_text", 
            "reverse_questions_options", "reverse_dimensions"
        ],
        
        # 评估字段组 - 评估和评分相关字段
        "assessment_fields": [
            "dimension_type", "user_mbti_type", "assessment_result", 
            "scoring_data", "dimension_scores", "raw_scores", 
            "percentages", "dimension_details"
        ],
        
        # 问题数据字段组 - MBTI问题相关字段
        "question_fields": [
            "mbti_questions", "text", "dimension", "reverse", 
            "questions_count", "selected_questions", "questions_data"
        ],
        
        # 维度详情字段组 - 维度计算结果详情
        "dimension_detail_fields": [
            "score", "percentage", "direction", "preference", 
            "opposite", "preference_strength", "z_score"
        ],
        
        # 用户状态字段组 - 用户状态和完成状态
        "user_status_fields": [
            "test_user", "JobFindingRegistryComplete", 
            "mbti_step1_complete", "completed", "completion_status"
        ],
        
        # 表单配置字段组 - 表单字段配置
        "form_config_fields": [
            "field_id", "field_type", "question_id", "required", 
            "value", "query_fields"
        ],
        
        # 错误处理字段组 - 错误信息相关字段
        "error_fields": [
            "error_message", "error_code"
        ]
    },

    # 步骤定义（5步骤MBTI流程）
    "steps": {
        "mbti_step1": {
            "description": "MBTI测试引导和问卷展示",
            "order": 1,
            "required_fields": ["user_id", "request_id"],
            "output_fields": ["step", "message", "success", "next_step", "flow_id", "current_mbti_step"]
        },
        "mbti_step2": {
            "description": "MBTI类型初步计算",
            "order": 2,
            "required_fields": ["user_id", "request_id", "responses"],
            "output_fields": ["step", "mbti_result", "analysis", "success", "flow_id"]
        },
        "mbti_step3": {
            "description": "反向问题生成",
            "order": 3,
            "required_fields": ["user_id", "request_id", "mbti_result"],
            "output_fields": ["step", "reverse_questions", "success", "flow_id"]
        },
        "mbti_step4": {
            "description": "反向问题计分和类型确认",
            "order": 4,
            "required_fields": ["user_id", "request_id", "reverse_responses"],
            "output_fields": ["step", "confirmed_type", "success", "flow_id"]
        },
        "mbti_step5": {
            "description": "最终报告生成",
            "order": 5,
            "required_fields": ["user_id", "request_id", "confirmed_type"],
            "output_fields": ["step", "final_report", "success", "flow_id"]
        }
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
    字段定义管理器（流程驱动版本）
    职责：管理流程驱动架构的字段定义，支持5步骤MBTI流程，提供字段规范给validator使用
    """

    # __init__ 方法通过调用初始化SchemaManager实例
    def __init__(self):
        """初始化字段定义管理器，加载流程驱动架构相关配置"""
        # FIELD_DEFINITIONS.copy() 通过调用复制字段定义配置到实例变量
        self.field_definitions = FIELD_DEFINITIONS.copy()
        # FIELD_INJECTIONS.copy() 通过调用复制字段注入配置到实例变量
        self.field_injections = FIELD_INJECTIONS.copy()
        # self._load_reverse_questions_data() 通过调用加载反向问题数据
        self.reverse_questions_data = self._load_reverse_questions_data()
        # self._inject_reverse_questions_fields() 通过调用注入反向问题字段定义
        self._inject_reverse_questions_fields()

    # get_field_types 方法通过调用返回所有字段类型定义
    def get_field_types(self) -> Dict[str, str]:
        """
        获取所有字段类型定义
        返回：字段名到类型的映射字典
        """
        # self.field_definitions["field_types"].copy() 通过调用复制并返回字段类型字典
        return self.field_definitions["field_types"].copy()

    # get_field_groups 方法通过调用返回字段分组定义
    def get_field_groups(self) -> Dict[str, List[str]]:
        """
        获取字段分组定义
        返回：分组名到字段列表的映射字典
        """
        # self.field_definitions["field_groups"].copy() 通过调用复制并返回字段分组字典
        return self.field_definitions["field_groups"].copy()

    # get_steps 方法通过调用返回步骤定义
    def get_steps(self) -> Dict[str, Dict[str, Union[str, int, List[str]]]]:
        """
        获取5步骤MBTI流程定义
        返回：步骤名到步骤信息的映射字典
        """
        # self.field_definitions["steps"].copy() 通过调用复制并返回步骤定义字典
        return self.field_definitions["steps"].copy()

    # get_request_fields 方法通过调用返回请求必需字段列表
    def get_request_fields(self) -> List[str]:
        """
        获取请求必需字段列表
        返回：请求字段名称列表
        """
        # self.field_definitions["field_groups"]["request_fields"].copy() 通过调用复制并返回请求字段列表
        return self.field_definitions["field_groups"]["request_fields"].copy()

    # get_response_fields 方法通过调用返回响应必需字段列表
    def get_response_fields(self) -> List[str]:
        """
        获取响应必需字段列表
        返回：响应字段名称列表
        """
        # self.field_definitions["field_groups"]["response_fields"].copy() 通过调用复制并返回响应字段列表
        return self.field_definitions["field_groups"]["response_fields"].copy()

    # get_reverse_question_fields 方法通过调用返回反向问题字段列表
    def get_reverse_question_fields(self) -> List[str]:
        """
        获取反向问题字段列表
        返回：反向问题字段名称列表
        """
        # self.field_definitions["field_groups"]["reverse_question_fields"].copy() 通过调用复制并返回反向问题字段列表
        return self.field_definitions["field_groups"]["reverse_question_fields"].copy()

    # get_assessment_fields 方法通过调用返回评估相关字段列表
    def get_assessment_fields(self) -> List[str]:
        """
        获取评估相关字段列表
        返回：评估字段名称列表
        """
        # self.field_definitions["field_groups"]["assessment_fields"].copy() 通过调用复制并返回评估字段列表
        return self.field_definitions["field_groups"]["assessment_fields"].copy()

    # get_valid_steps 方法通过调用返回有效步骤列表
    def get_valid_steps(self) -> List[str]:
        """
        获取有效步骤列表（mbti_step1到mbti_step5）
        返回：步骤名称列表
        """
        # list(self.field_definitions["steps"].keys()) 通过调用转换并返回步骤名称列表
        return list(self.field_definitions["steps"].keys())
    
    # _load_reverse_questions_data 方法通过调用从JSON文件加载反向问题数据
    def _load_reverse_questions_data(self) -> Dict[str, Union[str, dict, list]]:
        """
        从step3_mbti_reversed_questions.json文件加载反向问题数据
        返回：解析后的JSON数据字典
        """
        # os.path.join 通过调用构建JSON文件的完整路径
        # os.path.dirname(__file__) 获取当前文件所在目录路径
        json_path = os.path.join(os.path.dirname(__file__), "step3_mbti_reversed_questions.json")
        try:
            # open(json_path, 'r', encoding='utf-8') 通过调用以读取模式打开JSON文件
            with open(json_path, 'r', encoding='utf-8') as f:
                # json.load(f) 通过调用解析JSON文件内容并返回
                return json.load(f)
        except FileNotFoundError:  # 处理文件不存在的异常情况
            # raise RuntimeError 抛出运行时异常，包含具体的错误信息
            raise RuntimeError(f"Step3 reversed questions JSON file not found: {json_path}")
        except json.JSONDecodeError as e:  # 处理JSON解析错误的异常情况
            # raise RuntimeError 抛出运行时异常，包含JSON解析错误详情
            raise RuntimeError(f"Invalid JSON in step3 reversed questions file: {e}")

    # _inject_reverse_questions_fields 方法通过调用将反向问题JSON中的字段注入到字段定义中
    def _inject_reverse_questions_fields(self) -> None:
        """
        将反向问题JSON中的字段注入到字段定义中
        """
        # 从JSON数据中提取字段定义
        if "dimensionAssessments" in self.reverse_questions_data:
            # 遍历self.reverse_questions_data["dimensionAssessments"]列表中的每个维度
            for dimension in self.reverse_questions_data["dimensionAssessments"]:
                if "questions" in dimension:
                    # 遍历dimension["questions"]列表中的每个问题
                    for question in dimension["questions"]:
                        # 为每个问题字段添加类型定义
                        # question.keys() 通过调用获取问题字典的所有键
                        for field_key in question.keys():
                            # 检查字段是否已存在于字段类型定义中
                            if field_key not in self.field_definitions["field_types"]:
                                # 根据字段名推断字段类型
                                if "id" in field_key:
                                    field_type = "int"
                                elif "text" in field_key:
                                    field_type = "string"
                                elif "options" in field_key:
                                    field_type = "dict"
                                else:
                                    field_type = "string"

                                # 将推断的字段类型添加到字段定义中
                                self.field_definitions["field_types"][field_key] = field_type
                                # 将反向问题字段添加到相应分组
                                if field_key not in self.field_definitions["field_groups"]["reverse_question_fields"]:
                                    # self.field_definitions["field_groups"]["reverse_question_fields"].append 通过调用添加字段到反向问题字段分组
                                    self.field_definitions["field_groups"]["reverse_question_fields"].append(field_key)

    # inject_field 方法通过调用注入新字段到字段定义中
    def inject_field(self, field_name: str, field_type: str, target_group: str = "custom") -> None:
        """
        注入新字段到字段定义中
        参数：字段名、字段类型、目标分组
        """
        # 添加字段类型定义
        self.field_definitions["field_types"][field_name] = field_type

        # 添加到指定分组
        if target_group not in self.field_definitions["field_groups"]:
            # 如果目标分组不存在，创建新的分组
            self.field_definitions["field_groups"][target_group] = []

        # 检查字段是否已在目标分组中
        if field_name not in self.field_definitions["field_groups"][target_group]:
            # self.field_definitions["field_groups"][target_group].append 通过调用添加字段到目标分组
            self.field_definitions["field_groups"][target_group].append(field_name)

        # 记录注入信息
        # self.field_injections["injected_fields"].append 通过调用添加字段到已注入字段列表
        self.field_injections["injected_fields"].append(field_name)

    # get_reverse_questions_data 方法通过调用获取反向问题数据
    def get_reverse_questions_data(self) -> Dict[str, Union[str, dict, list]]:
        """
        获取反向问题数据
        返回：完整的反向问题JSON数据
        """
        # self.reverse_questions_data.copy() 通过调用复制并返回反向问题数据
        return self.reverse_questions_data.copy()

    # get_all_field_definitions 方法通过调用获取所有字段定义信息
    def get_all_field_definitions(self) -> Dict[str, Union[Dict[str, Union[str, dict, list]], dict, list]]:
        """
        获取所有字段定义信息
        返回：包含所有字段定义的字典
        """
        # return 语句返回包含完整字段定义信息的字典
        return {
            "field_definitions": self.field_definitions,
            "reverse_questions_data": self.reverse_questions_data,
            "field_injections": self.field_injections,
            "metadata": {
                "version": "3.0.0",  # 流程驱动版本
                "module_name": "mbti",
                "flow_type": "5_step_linear",  # 5步骤线性流程
                "questions_file": "step3_mbti_reversed_questions.json",
                "reverse_questions_loaded": True,
                "total_fields": len(self.field_definitions["field_types"]),
                "total_steps": len(self.field_definitions["steps"]),
                "architecture": "flow_driven"  # 流程驱动架构标识
            }
        }

    # inject_to_target_module 方法通过调用向目标模块注入字段定义信息
    def inject_to_target_module(self, target_module: str) -> Dict[str, Union[str, dict, list]]:
        """
        向目标模块注入字段定义信息
        参数：目标模块名称
        返回：注入的字段信息字典
        """
        # injection_data 通过字典构建包含注入信息的数据结构
        injection_data = {
            "field_definitions": self.field_definitions,
            "reverse_questions_data": self.reverse_questions_data,
            "target_module": target_module,
            "injection_timestamp": "auto-generated",
            "version": "3.0.0",  # 流程驱动版本
            "source_file": "step3_mbti_reversed_questions.json",
            "architecture": "flow_driven"
        }

        # 记录注入目标
        if target_module not in self.field_injections["target_modules"]:
            # self.field_injections["target_modules"].append 通过调用添加目标模块到注入列表
            self.field_injections["target_modules"].append(target_module)

        # 记录注入元数据
        self.field_injections["injection_metadata"][target_module] = {
            "timestamp": "auto-generated",
            "version": "3.0.0",
            "source_file": "step3_mbti_reversed_questions.json",
            "architecture": "flow_driven"
        }

        # 返回注入数据
        return injection_data


# schema_manager 通过SchemaManager()创建全局字段定义管理器实例
schema_manager = SchemaManager()

# === 导出接口函数 ===

# get_field_types 函数通过调用schema_manager.get_field_types()获取字段类型定义
def get_field_types() -> Dict[str, str]:
    """
    获取字段类型定义接口函数
    返回：字段名到类型的映射字典
    """
    return schema_manager.get_field_types()

# get_field_groups 函数通过调用schema_manager.get_field_groups()获取字段分组定义
def get_field_groups() -> Dict[str, List[str]]:
    """
    获取字段分组定义接口函数
    返回：分组名到字段列表的映射字典
    """
    return schema_manager.get_field_groups()

# get_request_fields 函数通过调用schema_manager.get_request_fields()获取请求必需字段列表
def get_request_fields() -> List[str]:
    """
    获取请求必需字段列表接口函数
    返回：请求字段名称列表
    """
    return schema_manager.get_request_fields()

# get_response_fields 函数通过调用schema_manager.get_response_fields()获取响应必需字段列表
def get_response_fields() -> List[str]:
    """
    获取响应必需字段列表接口函数
    返回：响应字段名称列表
    """
    return schema_manager.get_response_fields()

# get_reverse_question_fields 函数通过调用schema_manager.get_reverse_question_fields()获取反向问题字段列表
def get_reverse_question_fields() -> List[str]:
    """
    获取反向问题字段列表接口函数
    返回：反向问题字段名称列表
    """
    return schema_manager.get_reverse_question_fields()

# get_assessment_fields 函数通过调用schema_manager.get_assessment_fields()获取评估相关字段列表
def get_assessment_fields() -> List[str]:
    """
    获取评估相关字段列表接口函数
    返回：评估字段名称列表
    """
    return schema_manager.get_assessment_fields()

# get_valid_steps 函数通过调用schema_manager.get_valid_steps()获取有效步骤列表
def get_valid_steps() -> List[str]:
    """
    获取有效步骤列表接口函数（mbti_step1到mbti_step5）
    返回：步骤名称列表
    """
    return schema_manager.get_valid_steps()

# get_reverse_questions_data 函数通过调用schema_manager.get_reverse_questions_data()获取反向问题数据
def get_reverse_questions_data() -> Dict[str, Union[str, dict, list]]:
    """
    获取反向问题数据接口函数
    返回：完整的反向问题JSON数据
    """
    return schema_manager.get_reverse_questions_data()

# get_all_field_definitions 函数通过调用schema_manager.get_all_field_definitions()获取所有字段定义信息
def get_all_field_definitions() -> Dict[str, Union[Dict[str, Union[str, dict, list]], dict, list]]:
    """
    获取所有字段定义信息接口函数
    返回：包含所有字段定义的字典
    """
    return schema_manager.get_all_field_definitions()

# inject_field 函数通过调用schema_manager.inject_field()注入新字段
def inject_field(field_name: str, field_type: str, target_group: str = "custom") -> None:
    """
    注入新字段接口函数
    参数：字段名、字段类型、目标分组
    """
    schema_manager.inject_field(field_name, field_type, target_group)

# inject_to_target_module 函数通过调用schema_manager.inject_to_target_module()向目标模块注入字段定义信息
def inject_to_target_module(target_module: str) -> Dict[str, Union[str, dict, list]]:
    """
    向目标模块注入字段定义信息接口函数
    参数：目标模块名称
    返回：注入的字段信息字典
    """
    return schema_manager.inject_to_target_module(target_module)