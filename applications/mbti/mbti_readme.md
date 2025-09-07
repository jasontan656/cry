# MBTI 模块 - MBTI性格测试与反向能力评估系统

## 📋 概述

MBTI模块是Career Bot系统的核心性格评估模块，实现完整的MBTI性格测试与反向能力评估流程。采用模块化架构，支持5步流程：用户引导 → MBTI基础测试 → 反向测试表单生成 → 反向测试计分 → 最终能力报告。

**核心特性**：
- 🎯 **完整的Intent驱动架构**：支持7个intent（5个核心步骤 + 2个系统级intent）
- 💾 **数据库集成**：通过`database_query`实现状态持久化和断点续传
- 🔄 **模块编排**：通过`orchestrate_next_module`实现跨模块流程编排
- 🏗️ **中枢集成**：完整的intent驱动架构，支持动态模块编排

## 🏗️ 系统架构

```
用户触发找工作 → orchestrate → [mbti模块]
                                    ↓
      Step1: 用户引导 → database_query检查状态 → 提供测试入口
                                    ↓
      Step2: MBTI测试 → 24题基础测试 → 计算MBTI类型 → 保存结果
                                    ↓
      Step3: 反向测试表单 → 生成针对性问题 → 基于MBTI类型
                                    ↓
      Step4: 反向测试计分 → A/B选择题评估 → 自动触发Step5
                                    ↓
      Step5: 最终报告 → 完整能力分析 → orchestrate_next_module编排下一模块
```

## 📁 文件结构

```
applications/mbti/
├── __init__.py                 # 包初始化
├── mbti.py                     # 模块统一入口
├── router.py                   # 路由处理器（核心路由器）
├── schemas.py                  # 字段定义和数据模型管理
├── step1.py                    # 用户引导处理器
├── step2.py                    # MBTI测试结果处理器
├── step3.py                    # 反向测试表单生成器
├── step4.py                    # 反向测试计分器
├── step5.py                    # 最终报告生成器
├── mbti_survey.html           # MBTI测试界面
├── step1_mbti_questions.json  # MBTI基础测试题库（24题）
├── step2_mbti_output_templates.json # MBTI类型分析模板
├── step2_mbti_scoring.json    # MBTI计分规则
├── step3_mbti_reversed_questions.json # 反向测试题库
├── step4_mbti_reversed_questions_scoring.json # 反向测试计分规则
├── step5_final_output_template.json # 最终报告模板
├── output_templates.json      # 输出模板配置
├── output_preview.md          # 输出预览文档
└── test/                      # 测试目录
    ├── test_mbti_entry_1_2.py # Step1/Step2测试
    └── test_mbti_entry_3_4_5.py # Step3-Step5测试
```

## 🔧 核心组件

### 1. 主入口 (mbti.py)
```python
async def run(request) -> dict:
    """模块统一入口，转发到router处理"""
    return await process_mbti_request(request)
```

### 2. 路由器 (router.py)
- **MBTIRouter类**: 核心路由处理器
- **Intent映射**: 根据intent路由到对应步骤处理器
- **支持的Intent**:
  - `"mbti_step1"`: 用户引导和状态检查
  - `"mbti_step2"`: MBTI测试结果处理
  - `"mbti_step3"`: 反向测试表单生成
  - `"mbti_step4"`: 反向测试计分
  - `"mbti_step5"`: 最终报告生成
  - `"database_query"`: 数据库查询操作（状态检查）
  - `"orchestrate_next_module"`: 模块编排（通知中枢切换到下一个模块）

### 3. 字段管理 (schemas.py)
- **SchemaManager类**: 字段定义管理器
- **字段类型定义**: UUID、String、Dict、Int等
- **字段分组**: 请求字段、响应字段、问题字段、评估字段
- **动态字段注入**: 支持运行时扩展字段定义


## 🔄 5步测试流程详解

### Step 1: 用户引导 (step1.py)
**功能**: 处理用户点击找工作按钮，检查完成状态，提供测试引导

**输入参数**:
- `request_id`: 可选，请求标识符
- `user_id`: 必填，用户标识符
- `test_user`: 可选，测试模式标识

**处理逻辑**:
1. 通过`database_query` intent查询用户完成状态（JobFindingRegistryComplete、mbti_step1_complete）
2. 如果已完成所有模块，通过`orchestrate_next_module` intent通知中枢编排下一个模块（job_matching）
3. 检查是否已完成step1，如是则跳转step2
4. 提供MBTI测试按钮和引导信息

**输出**:
- 测试引导信息和按钮配置
- 自动生成timestamp_uuid格式的request_id

### Step 2: MBTI测试处理 (step2.py)
**功能**: 处理用户提交的MBTI测试答案，计算类型，输出分析

**核心算法**: Z-Score阈值判定系统
- **理论分布**: 24题 × 3分 = 72分理论均值
- **标准差**: 6.6分（基于统计模拟）
- **判定阈值**:
  - 高阈值: +0.5 SD (75.3分) → 明显偏好该维度
  - 低阈值: -0.5 SD (68.7分) → 明显偏好对立维度
  - 中间值: 68.7-75.3分 → 中间型/边缘型

**维度映射**:
```python
DIMENSION_MAPPING = {
    'E': ['I', 'E'],  # 外向-内向
    'S': ['N', 'S'],  # 感觉-直觉
    'T': ['F', 'T'],  # 思考-情感
    'J': ['P', 'J']   # 判断-感知
}
```

**处理流程**:
1. 验证用户提交的24题答案（1-5分）
2. 使用MBTIScorer计算MBTI类型
3. 从step2_mbti_output_templates.json获取对应分析
4. 自动触发step3处理

### Step 3: 反向测试表单生成 (step3.py)
**功能**: 根据MBTI类型生成反向能力测试表单

**反向维度映射**:
```python
DIMENSION_REVERSE_MAP = {
    'I': 'E', 'E': 'I',  # 内向↔外向
    'N': 'S', 'S': 'N',  # 直觉↔感觉
    'F': 'T', 'T': 'F',  # 情感↔思考
    'P': 'J', 'J': 'P'   # 感知↔判断
}
```

**处理流程**:
1. 计算用户MBTI类型的反向维度
2. 从step3_mbti_reversed_questions.json提取对应问题
3. 生成前端表单渲染所需的JSON Schema
4. 包含表单标题、描述、字段配置、验证规则

### Step 4: 反向测试计分 (step4.py)
**功能**: 计算反向能力得分，自动联动Step5

**评分规则**:
- A选项: +1分（具备反向能力）
- B选项: +0分（偏向原维度）
- 每维度3题，总分0-3分

**能力水平解释**:
- 0-1分: "典型类型，反向能力相对缺乏"
- 2分: "具备反向能力，可在需要时调用"
- 3分: "强反向能力，接近反向类型水平"

**处理流程**:
1. 处理用户提交的A/B选择答案
2. 使用MbtiReverseScorer计算各维度得分
3. 自动触发step5生成最终报告

### Step 5: 最终报告生成 (step5.py)
**功能**: 生成完整的反向能力评估报告

**报告生成器**: MbtiReportGenerator类

**报告结构**:
- **标题**: "{MBTI类型}类型反向能力评估报告"
- **维度分析**: 每个反向维度的详细分析
- **得分展示**: 原始得分和能力水平解释
- **总结**: 基于平均分的能力灵活性评估

## 📊 数据结构

### TypedDict数据模型
```python
class Question(TypedDict):
    text: str          # 题目文本
    dimension: str     # 所属维度 (E/S/T/J)
    reverse: bool      # 是否反向题

class MBTIResult(TypedDict):
    raw_scores: Dict[str, int]          # 各维度原始得分
    percentages: Dict[str, int]         # 各维度百分比
    mbti_type: str                      # 最终MBTI类型
    dimension_details: Dict[str, DimensionDetail]

class DimensionDetail(TypedDict):
    score: int         # 原始得分
    percentage: int    # 百分比
    direction: str     # 判定方向
    preference: str    # 偏好方向
    opposite: str      # 对立方向
```

## 🔗 外部依赖

### 必需依赖
- **utilities.time.Time**: timestamp_uuid生成
- **orchestrate**: 中枢系统集成（intent路由和模块编排）
- **database**: 数据库操作模块（用户状态查询和结果存储）

### 标准库依赖
- **json**: JSON文件读取和解析
- **os**: 文件路径处理
- **re**: request ID格式验证
- **sys**: 路径管理和模块导入
- **typing**: 完整的类型注解支持

## 🚀 运行环境

- **Python**: 3.10+
- **内存**: 512MB+（需加载多个JSON配置文件）
- **网络**: 可选（中枢系统集成时需要）

## 🔄 调用方式

### 统一入口
```python
from applications.mbti.mbti import run

# 异步调用
result = await run(request_dict)
```

### Intent路由
```python
# Step1: 用户引导
request = {"intent": "mbti_step1", "user_id": "user123"}

# Step2: MBTI测试处理
request = {
    "intent": "mbti_step2",
    "user_id": "user123",
    "responses": {0: 4, 1: 3, ...}  # 24题答案
}

# Step3: 反向测试表单
request = {
    "intent": "mbti_step3",
    "user_id": "user123",
    "mbti_type": "INTJ"
}

# Step4: 反向测试计分
request = {
    "intent": "mbti_step4",
    "user_id": "user123",
    "responses": {"question_0": "A", "question_1": "B", ...}
}

# Step5: 最终报告
request = {
    "intent": "mbti_step5",
    "user_id": "user123",
    "mbti_type": "INTJ",
    "dimension_scores": {"E": 2, "S": 1, "F": 3, "P": 0}
}

# 数据库查询（状态检查）
request = {
    "intent": "database_query",
    "user_id": "user123",
    "query_fields": ["JobFindingRegistryComplete", "mbti_step1_complete"],
    "table": "user_profile"
}

# 模块编排（通知中枢）
request = {
    "intent": "orchestrate_next_module",
    "current_module": "mbti",
    "user_id": "user123",
    "completion_status": "all_tests_completed"
}
```

## 🎯 特性亮点

1. **完整的MBTI评估体系**: 基础MBTI测试 + 反向能力评估
2. **自动联动机制**: step2→step3，step4→step5自动触发
3. **Z-Score科学算法**: 基于统计学的MBTI类型判定
4. **模块化设计**: 路由器模式，热插拔支持
5. **严格类型注解**: 完整的TypedDict数据模型
6. **异常安全**: 每个步骤都有完善的异常处理
7. **数据库集成**: 通过`database_query` intent实现状态持久化和断点续传
8. **模块编排**: 通过`orchestrate_next_module` intent实现跨模块流程编排
9. **中枢集成**: 完整的intent驱动架构，支持动态模块编排

## 📝 输出示例

### MBTI测试结果 (Step2)
```json
{
  "request_id": "2024-01-01T10:00:00+0800_550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user123",
  "success": true,
  "step": "mbti_step2",
  "mbti_result": {
    "raw_scores": {"E": 78, "S": 65, "T": 82, "J": 71},
    "percentages": {"E": 81, "S": 68, "T": 85, "J": 74},
    "mbti_type": "ENTJ",
    "dimension_details": {...}
  },
  "analysis": "作为ENTJ类型，你展现出..."
}
```

### 最终能力报告 (Step5)
```json
{
  "request_id": "...",
  "user_id": "user123",
  "success": true,
  "step": "mbti_step5",
  "mbti_type": "ENTJ",
  "dimension_scores": {"E": 2, "S": 1, "F": 3, "P": 0},
  "final_report": {
    "title": "ENTJ类型反向能力评估报告",
    "mbti_type": "ENTJ",
    "dimension_scores": {"E": 2, "S": 1, "F": 3, "P": 0},
    "report_sections": [...],
    "summary": "作为ENTJ类型，你的反向能力灵活性为中等水平..."
  },
  "completed": true
}
```

## 🧪 测试说明

### 测试文件
- **test_mbti_entry_1_2.py**: 测试Step1和Step2功能
- **test_mbti_entry_3_4_5.py**: 测试Step3到Step5功能

### 测试覆盖
- 正常流程测试
- 异常处理测试
- 数据验证测试
- 集成测试

## 📚 相关文档

- **mbti_survey.html**: MBTI测试界面
- **output_preview.md**: 输出结果预览
- **step1_mbti_questions.json**: 详细的MBTI测试题库
- **step2_mbti_output_templates.json**: 16种MBTI类型分析模板

---



*该模块实现了完整的MBTI性格测试与反向能力评估流程，为Career Bot系统提供科学的性格分析能力和完善的数据库集成。*
