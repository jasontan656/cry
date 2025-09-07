# 通过 env 调用 python3 解释器执行当前脚本文件
#!/usr/bin/env python3
# 通过 coding 声明设置文件编码为 utf-8 以支持中文字符处理
# -*- coding: utf-8 -*-
"""
step2.py - MBTI测试结果处理器  # 处理测试结果，计算类型，输出分析
"""

# 通过 import 导入 json 模块，用于后续文件读取和数据解析操作
import json
# 通过 import 导入 os 模块，用于文件路径处理
import os
# 通过 import 导入 re 模块，用于request ID格式验证的正则表达式操作
import re
# 通过 import 导入 sys 模块，用于路径操作
import sys
# 通过 from...import 导入 typing 模块的类型提示工具，使用精确类型定义
from typing import Dict, List, TypedDict, Union, Optional
# 通过 import 导入 step3 模块，用于在step2完成后触发step3进一步测试
from applications.mbti import step3

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


# 通过 class 定义 Question 类型字典，包含单个题目结构的精确类型字段
class Question(TypedDict):
    # text 字段定义为 str 类型，用于存储题目文本内容，必须填写
    text: str
    # dimension 字段定义为 str 类型，用于存储题目所属维度，只能是E/S/T/J之一
    dimension: str
    # reverse 字段定义为 bool 类型，用于标识是否为反向题，True表示是反向题
    reverse: bool


# 通过 class 定义 QuestionData 类型字典，包含题目数据文件的完整结构
class QuestionData(TypedDict):
    # mbti_questions 字段定义为 List[Question] 类型，存储包含多个Question对象的题目列表
    mbti_questions: List[Question]


# 通过 class 定义 DimensionDetail 类型字典，包含维度详情的完整结构
class DimensionDetail(TypedDict):
    # score 字段定义为 int 类型，用于存储该维度的原始得分数值
    score: int
    # percentage 字段定义为 int 类型，用于存储该维度的百分比数值
    percentage: int
    # direction 字段定义为 str 类型，用于存储该维度的判定方向字母
    direction: str
    # preference 字段定义为 str 类型，用于存储该维度的偏好方向字母
    preference: str
    # opposite 字段定义为 str 类型，用于存储该维度的对立方向字母
    opposite: str


# 通过 class 定义 MBTIResult 类型字典，包含MBTI评分结果的完整结构
class MBTIResult(TypedDict):
    # raw_scores 字段定义为 Dict[str, int] 类型，用于存储各维度的原始得分数值
    raw_scores: Dict[str, int]
    # percentages 字段定义为 Dict[str, int] 类型，用于存储各维度的百分比数值
    percentages: Dict[str, int]
    # mbti_type 字段定义为 str 类型，用于存储最终计算出的MBTI类型字符串
    mbti_type: str
    # dimension_details 字段定义为 Dict[str, DimensionDetail] 类型，用于存储各维度的详细信息字典
    dimension_details: Dict[str, DimensionDetail]


# 通过 class 定义 TypeCalculationResult 类型字典，包含类型计算的中间结果结构
class TypeCalculationResult(TypedDict):
    # percentages 字段定义为 Dict[str, int] 类型，用于存储各维度的百分比数值字典
    percentages: Dict[str, int]
    # mbti_type 字段定义为 str 类型，用于存储拼接成的MBTI类型字符串
    mbti_type: str
    # dimension_details 字段定义为 Dict[str, DimensionDetail] 类型，用于存储各维度的详情字典
    dimension_details: Dict[str, DimensionDetail]


# 通过 class 定义 MBTIScorer 类，封装所有MBTI评分相关功能的完整实现
class MBTIScorer:
    """MBTI测试评分器"""  # 类功能简述，说明这是一个MBTI测试的评分工具

    # DIMENSION_MAPPING 通过字典创建常量，存储四个维度的字母映射关系，用于后续类型判定
    DIMENSION_MAPPING = {
        # 'E' 键映射到 ['I', 'E'] 列表，E维度低分取索引0的I(内向)，高分取索引1的E(外向)
        'E': ['I', 'E'],
        # 'S' 键映射到 ['N', 'S'] 列表，S维度低分取索引0的N(直觉)，高分取索引1的S(感觉)
        'S': ['N', 'S'],
        # 'T' 键映射到 ['F', 'T'] 列表，T维度低分取索引0的F(情感)，高分取索引1的T(思考)
        'T': ['F', 'T'],
        # 'J' 键映射到 ['P', 'J'] 列表，J维度低分取索引0的P(感知)，高分取索引1的J(判断)
        'J': ['P', 'J']
    }

    # __init__ 方法在创建 MBTIScorer 实例时自动调用，无需传入参数
    def __init__(self):
        # 通过 self._load_questions() 调用私有方法加载题目数据，赋值给 self.questions_data 实例变量存储
        self.questions_data = self._load_questions()

    # _load_questions 方法定义为私有方法，通过 -> QuestionData 返回精确的题目数据类型
    def _load_questions(self) -> QuestionData:
        """加载题目数据"""  # 方法功能说明，读取JSON格式的题目数据
        # try 块开始尝试执行文件读取操作，捕获可能的异常
        try:
            # 获取当前脚本文件所在目录，然后构建完整的文件路径
            current_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(current_dir, 'step1_mbti_questions.json')
            # 通过 with open() 以只读模式打开文件，指定 utf-8 编码，赋值给变量 f
            with open(file_path, 'r', encoding='utf-8') as f:
                # 通过 json.load() 传入文件对象 f 解析JSON数据，返回字典对象赋值给 data 变量
                data = json.load(f)
                # 通过 QuestionData(**data) 将字典 data 解包传入构造函数，转换为精确的QuestionData类型后返回
                return QuestionData(**data)
        # except 捕获 FileNotFoundError 异常，当文件不存在时执行
        except FileNotFoundError:
            # 通过 raise 抛出新的 FileNotFoundError 异常，传入自定义错误信息字符串
            raise FileNotFoundError("step1_mbti_questions.json not found")

    # calculate_scores 方法接收 responses 参数（Dict[str, int]类型），通过 -> MBTIResult 返回完整的评分结果
    def calculate_scores(self, responses: Dict[str, int]) -> MBTIResult:
        """
        计算MBTI得分  # 方法功能：根据用户答案计算各维度得分
        Args:  # 参数说明部分
            responses: {question_index: score} 格式的答案字典  # 说明输入格式
        Returns:  # 返回值说明部分
            包含原始得分、百分比和类型的完整结果  # 说明输出包含哪些内容
        """
        # dimension_scores 通过字典初始化，创建E/S/T/J四个维度的得分计数器，每个维度初始值设为0
        dimension_scores = {'E': 0, 'S': 0, 'T': 0, 'J': 0}

        # 通过 enumerate() 遍历 self.questions_data['mbti_questions'] 列表，获取题目索引idx和题目内容question
        for idx, question in enumerate(self.questions_data['mbti_questions']):
            # 通过 responses[idx] 获取用户对第idx题的原始得分（1-5分，所有题目必答），赋值给 raw_score 变量
            raw_score = responses[idx]
            # 通过 question['dimension'] 获取这道题所属的维度（E/S/T/J之一），赋值给 dimension 变量
            dimension = question['dimension']
            # 通过 question['reverse'] 检查这道题是否为反向题，布尔值赋值给 is_reverse 变量
            is_reverse = question['reverse']

            # processed_score 通过条件表达式计算：如果是反向题则用6减去raw_score，否则直接使用raw_score
            processed_score = 6 - raw_score if is_reverse else raw_score

            # 通过 dimension_scores[dimension] 索引对应维度，将 processed_score 累加到该维度的总分上
            dimension_scores[dimension] += processed_score

        # 通过 self._calculate_mbti_type() 调用私有方法，传入 dimension_scores 参数，计算百分比和类型，结果赋值给 result 变量
        result = self._calculate_mbti_type(dimension_scores)

        # 通过 return 返回包含完整计算结果的字典，包含raw_scores、percentages、mbti_type和dimension_details四个键值对
        return {
            # 'raw_scores' 键赋值为 dimension_scores 字典，存储各维度的原始得分数值
            'raw_scores': dimension_scores,
            # 'percentages' 键赋值为 result['percentages']，存储各维度的百分比数值
            'percentages': result['percentages'],
            # 'mbti_type' 键赋值为 result['mbti_type']，存储最终计算出的MBTI类型字符串
            'mbti_type': result['mbti_type'],
            # 'dimension_details' 键赋值为 result['dimension_details']，存储各维度的详细信息字典
            'dimension_details': result['dimension_details']
        }

    # _calculate_mbti_type 方法接收 scores 参数（Dict[str, int]类型），通过 -> TypeCalculationResult 返回类型计算结果
    def _calculate_mbti_type(self, scores: Dict[str, int]) -> TypeCalculationResult:
        """根据得分计算MBTI类型，使用Z-Score阈值"""  # 方法功能：将各维度得分转换为最终MBTI类型
        # percentages 通过字典初始化，用于存储各维度的百分比数值
        percentages = {}
        # mbti_letters 通过列表初始化，用于存储四个维度的判定字母，准备后续拼接成MBTI类型
        mbti_letters = []
        # dimension_details 通过字典初始化，用于存储各维度的详细信息字典
        dimension_details = {}

        # 基于24题（1-5分）的理论分布计算阈值
        # 理论平均分：24题 × 3分 = 72分
        # 理论标准差：约6.6分（通过统计模拟计算）
        THEORETICAL_MEAN = 72.0
        THEORETICAL_STD = 6.6
        HIGH_THRESHOLD = THEORETICAL_MEAN + 0.5 * THEORETICAL_STD  # +0.5 SD ≈ 75.3
        LOW_THRESHOLD = THEORETICAL_MEAN - 0.5 * THEORETICAL_STD   # -0.5 SD ≈ 68.7

        # 通过 scores.items() 遍历四个维度的得分，获取维度名称dimension和对应得分score
        for dimension, score in scores.items():
            # percentage 通过 round() 函数计算：score除以120(总分)乘以100，得到百分比并四舍五入取整
            percentage = round(score / 120 * 100)

            # 使用Z-Score阈值判断偏好方向
            if score > HIGH_THRESHOLD:
                # 高于+0.5 SD，明显偏好该维度
                direction_idx = 1
                preference_strength = "明显偏好"
            elif score < LOW_THRESHOLD:
                # 低于-0.5 SD，明显偏好对立维度
                direction_idx = 0
                preference_strength = "明显偏好对立"
            else:
                # 在-0.5 SD ~ +0.5 SD之间，中间型/边缘型
                # 取更接近的方向作为主要偏好
                direction_idx = 1 if score >= THEORETICAL_MEAN else 0
                preference_strength = "中间型/边缘型"

            # mbti_letter 通过 self.DIMENSION_MAPPING[dimension][direction_idx] 从映射表获取对应字母，赋值给变量
            mbti_letter = self.DIMENSION_MAPPING[dimension][direction_idx]

            # percentages[dimension] 索引对应维度位置，将 percentage 值存储到百分比字典中
            percentages[dimension] = percentage
            # 通过 mbti_letters.append() 将 mbti_letter 添加到字母列表末尾
            mbti_letters.append(mbti_letter)

            # dimension_details[dimension] 索引对应维度位置，创建包含详细信息的字典
            dimension_details[dimension] = {
                # 'score' 键赋值为 score 变量，存储该维度的原始得分数值
                'score': score,
                # 'percentage' 键赋值为 percentage 变量，存储该维度的百分比数值
                'percentage': percentage,
                # 'direction' 键赋值为 mbti_letter 变量，存储该维度的最终判定方向字母
                'direction': mbti_letter,
                # 'preference' 键赋值为 self.DIMENSION_MAPPING[dimension][direction_idx]，存储偏好方向字母
                'preference': self.DIMENSION_MAPPING[dimension][direction_idx],
                # 'opposite' 键赋值为 self.DIMENSION_MAPPING[dimension][1 - direction_idx]，存储对立方向字母
                'opposite': self.DIMENSION_MAPPING[dimension][1 - direction_idx],
                # 'preference_strength' 键赋值为 preference_strength，存储偏好强度描述
                'preference_strength': preference_strength,
                # 'z_score' 键计算并存储Z-Score值，表示相对于平均水平的标准差倍数
                'z_score': round((score - THEORETICAL_MEAN) / THEORETICAL_STD, 2)
            }

        # 通过 return 返回包含完整类型计算结果的字典
        return {
            # 'percentages' 键赋值为 percentages 字典，存储各维度的百分比数值
            'percentages': percentages,
            # 'mbti_type' 键通过 ''.join(mbti_letters) 将字母列表拼接成字符串，存储最终MBTI类型
            'mbti_type': ''.join(mbti_letters),
            # 'dimension_details' 键赋值为 dimension_details 字典，存储各维度的详细信息
            'dimension_details': dimension_details
        }



# load_output_templates 函数定义为独立函数，无需传入参数，通过 -> Dict[str, str] 返回模板字典
def load_output_templates() -> Dict[str, str]:
    """加载MBTI类型输出模板"""  # 方法功能：读取输出模板JSON文件
    # try 块开始尝试执行文件读取操作，捕获可能的异常
    try:
        # 获取当前脚本文件所在目录，然后构建完整的文件路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, 'step2_mbti_output_templates.json')
        # 通过 with open() 以只读模式打开文件，指定 utf-8 编码，赋值给变量 f
        with open(file_path, 'r', encoding='utf-8') as f:
            # 通过 json.load() 传入文件对象 f 解析JSON数据，返回字典对象后直接返回
            return json.load(f)
    # except 捕获 FileNotFoundError 异常，当文件不存在时执行
    except FileNotFoundError:
        # 通过 raise 抛出新的 FileNotFoundError 异常，传入自定义错误信息字符串
        raise FileNotFoundError("step2_mbti_output_templates.json not found")


# process 函数定义为异步函数，接收 request 参数（Dict[str, Union[str, int, bool, None]]类型），通过 -> Dict[str, Union[str, bool, int]] 返回处理结果字典
async def process(request: Dict[str, Union[str, int, bool, None]]) -> Dict[str, Union[str, bool, int]]:
    """
    处理用户测试结果，计算MBTI类型，输出分析结果
    调用数据库代理写入数据（占位符）
    """
    # try 块开始尝试执行主要处理逻辑，捕获可能的异常
    try:
        # validate_request_id 函数通过传入 request.get("request_id") 验证request_id格式
        # 如果UUID格式无效，立即抛出异常拒绝服务
        request_id = validate_request_id(request.get("request_id"))

        # user_responses 通过 request.get("responses", {}) 获取用户提交的答案字典，默认值为空字典
        user_responses = request.get("responses", {})
        # user_id 通过 request.get("user_id") 获取用户ID，赋值给变量
        user_id = request.get("user_id")

        # scorer 通过 MBTIScorer() 创建MBTI评分器实例，赋值给变量
        scorer = MBTIScorer()
        # mbti_result 通过 scorer.calculate_scores() 调用计算方法，传入 user_responses 参数，获取MBTI计算结果
        mbti_result = scorer.calculate_scores(user_responses)

        # output_templates 通过 load_output_templates() 调用独立函数，加载输出模板字典
        output_templates = load_output_templates()

        # mbti_type 通过 mbti_result['mbti_type'] 获取MBTI类型字符串，赋值给变量
        mbti_type = mbti_result['mbti_type']
        # analysis_text 通过 output_templates.get(mbti_type, "类型分析模板未找到") 获取对应类型的分析文本
        analysis_text = output_templates.get(mbti_type, "类型分析模板未找到")

        # response 通过字典创建，构建返回给前端的完整响应结构
        response = {
            # "request_id" 键通过 request.get("request_id") 获取请求ID
            "request_id": request.get("request_id"),
            # "user_id" 键赋值为 user_id 变量
            "user_id": user_id,
            # "success" 键设为 True，表示处理成功
            "success": True,
            # "step" 键设为 "mbti_step2"，表示当前步骤
            "step": "mbti_step2",
            # "mbti_result" 键赋值为 mbti_result 字典，存储MBTI计算结果
            "mbti_result": mbti_result,
            # "analysis" 键赋值为 analysis_text 变量，存储性格分析文本
            "analysis": analysis_text
        }

        # try 块开始尝试执行数据库存储操作，捕获可能的异常
        try:
            # 通过 await _call_database() 调用异步数据库函数，传入 request 和 mbti_result 参数
            await _call_database(request, mbti_result)
        # except 捕获 Exception 异常，当数据库调用失败时执行
        except Exception as db_error:
            # 通过 print() 输出数据库调用失败信息，但不影响主流程继续执行
            print(f"数据库存储失败: {str(db_error)}，跳过存储继续执行")

        # try 块开始尝试触发step3进一步测试，捕获可能的异常
        try:
            # step3_request 通过字典创建，构造传递给step3的请求参数
            step3_request = {
                # "request_id" 键通过 request.get("request_id") 获取原始请求ID
                "request_id": request.get("request_id"),
                # "user_id" 键赋值为 user_id 变量，传递用户标识
                "user_id": user_id,
                # "intent" 键设为 "mbti_step3" 字符串，指定下一步骤意图
                "intent": "mbti_step3",
                # "mbti_result" 键赋值为 mbti_result 字典，传递step2的MBTI计算结果
                "mbti_result": mbti_result,
                # "previous_step" 键设为 "mbti_step2" 字符串，标识来源步骤
                "previous_step": "mbti_step2"
            }
            # 通过 await step3.process() 调用step3的处理函数，传入 step3_request 参数
            step3_result = await step3.process(step3_request)
            # 通过 print() 输出step3触发成功信息和结果概要
            print(f"Step3触发成功，用户ID: {user_id}, MBTI类型: {mbti_type}")
        # except 捕获 Exception 异常，当step3调用失败时执行
        except Exception as step3_error:
            # 通过 print() 输出step3触发失败信息，但不影响step2的正常返回
            print(f"Step3触发失败: {str(step3_error)}，但step2处理完成，继续返回结果")

        # 通过 return 返回完整的 response 字典响应
        return response

    # except 捕获 Exception 异常，当系统异常发生时执行
    except Exception as e:
        # 通过 return 返回包含异常信息的错误响应字典
        return {
            # "request_id" 键通过 request.get("request_id") 获取请求ID
            "request_id": request.get("request_id"),
            # "user_id" 键通过 request.get("user_id") 获取用户ID
            "user_id": request.get("user_id"),
            # "success" 键设为 False，表示处理失败
            "success": False,
            # "step" 键设为 "mbti_step2"，表示当前步骤
            "step": "mbti_step2",
            # "error_message" 键通过 f"处理异常: {str(e)}" 格式化异常信息字符串
            "error_message": f"处理异常: {str(e)}"
        }


# _call_database 函数定义为异步私有函数，接收 request 和 mbti_result 参数，通过 -> None 不返回任何值
async def _call_database(request: Dict[str, Union[str, int, bool, None]], mbti_result: MBTIResult) -> None:
    """
    调用数据库代理写入MBTI测试结果（占位符）
    数据库结构待定，目前仅记录调用
    """
    # TODO: 实现数据库代理调用
    # 预期数据结构：
    # {
    #     "user_id": request["user_id"],
    #     "mbti_type": mbti_result["mbti_type"],
    #     "raw_scores": mbti_result["raw_scores"],
    #     "percentages": mbti_result["percentages"],
    #     "dimension_details": mbti_result["dimension_details"],
    #     "timestamp": datetime.now()
    # }

    # 通过 print() 输出格式化字符串，记录数据库代理被调用但不执行实际写入操作
    print(f"Database agent called for user {request.get('user_id')} with MBTI type {mbti_result['mbti_type']}")

    # TODO: 替换为实际的数据库代理调用代码
    # 例如：await database.save_mbti_result(request, mbti_result)
    # 目前处于开发阶段，数据库未配置，暂时使用 pass 占位

    # pass 语句表示函数体为空，占位符作用
    pass

