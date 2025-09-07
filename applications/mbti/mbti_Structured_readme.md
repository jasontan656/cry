# mbti_agent - MBTI性格测试中心 结构化文档骨架

### A1: 开发边界与职责说明

```
mbti_agent是Career Bot系统的MBTI性格测试模块，采用模块自治架构，负责完整的MBTI测试流程。模块内置测试题库、评分规则和所有必要配置，在系统启动时向routing_agent注册自己的字段参数和能力。该模块实现真正的热插拔：存在即提供MBTI测试能力，缺失则系统无此能力但全局运行不受影响。每个测试步骤都通过routing_agent与database_agent集成进行数据存储，并通过routing_agent与entry_agent协调前端交互。
```

------------------------------

### A2: 核心功能特性

```
A-2.1: MBTI三步测试流程
├── A-2.1.1: Step1 初始测试 - 提供MBTI测试题（不告知用户这是MBTI测试）
├── A-2.1.2: Step2 选择题生成 - 收到Step1结果后生成12道选择题
└── A-2.1.3: Step3 结果输出 - 收到Step2结果后输出规则设置的最终结果

A-2.2: 模块自治架构
├── A-2.2.1: 内置题库 - 模块内置所有测试题和选择题（外部提供内容）
├── A-2.2.2: 内置配置 - 评分规则、字段参数等全部自管理
├── A-2.2.3: 能力注册 - 启动时向routing_agent注册模块字段参数和能力
└── A-2.2.4: 热插拔支持 - 模块存在=能力存在，模块缺失=能力缺失但不影响全局

A-2.3: 数据库集成流程
├── A-2.3.1: Step1存储 - 初始测试结果通过routing_agent存储到database_agent
├── A-2.3.2: Step2存储 - 选择题结果通过routing_agent存储到database_agent
├── A-2.3.3: Step3存储 - 最终结果通过routing_agent存储到database_agent
└── A-2.3.4: 前端协调 - 每步都通过routing_agent与entry_agent协调前端交互
```

------------------------------

### A3: 系统架构位置

```
用户触发MBTI测试 → entry_agent → routing_agent → [mbti_agent]
                                                        ↓
                  Step1: 提供测试题 → database_agent存储 → entry_agent前端显示
                                    ↓
                  Step2: 生成12道选择题 → database_agent存储 → entry_agent前端显示
                                    ↓
                  Step3: 输出最终结果 → database_agent存储 → entry_agent前端显示
                                    ↓
                  完成后可触发后续测试模块（如ninetest_agent）
```

------------------------------

### B1: 输入输出规范

```
B-1.1: 输入字段
├── B-1.1.1: request_id - str, 必填, 请求唯一标识符
├── B-1.1.2: user_id - str, 必填, 用户标识符
├── B-1.1.3: step - str, 必填, 枚举值["step1", "step2", "step3"]
├── B-1.1.4: user_answers - List[Dict], step2和step3时必填, 用户答题结果
└── B-1.1.5: session_data - Dict, 可选, 会话上下文数据

B-1.2: 输出字段
├── B-1.2.1: request_id - str, 必填, 对应请求ID
├── B-1.2.2: success - bool, 必填, 处理成功状态
├── B-1.2.3: step - str, 必填, 当前步骤
├── B-1.2.4: data - Dict, 成功时必填, 包含题目或结果数据
├── B-1.2.5: storage_request - Dict, 必填, 发送给database_agent的存储请求
├── B-1.2.6: frontend_response - Dict, 必填, 发送给entry_agent的前端响应
└── B-1.2.7: error_message - str, 失败时必填, 错误描述
```

------------------------------

### B2: 模块自治配置

```
B-2.1: 自治配置管理
模块内置所有配置，包括测试题库、评分规则、字段参数等。启动时向routing_agent注册模块能力和字段定义，无需外部配置依赖。

B-2.2: 内置配置类型
├── B-2.2.1: step1_questions.json - Step1测试题库JSON文件
├── B-2.2.2: step2_questions.json - Step2选择题库JSON文件
├── B-2.2.3: step3_scoring.json - Step3评分规则JSON文件
└── B-2.2.4: field_schema.json - 模块字段参数定义（注册给routing_agent）
```

------------------------------

### B3: 数据模型

```
B-3.1: 模块内置数据模型
模块自定义并管理所有业务数据模型，启动时向routing_agent注册字段定义供其他模块验证使用。

B-3.2: 核心数据结构
├── B-3.2.1: MBTIQuestion - MBTI测试题目模型
├── B-3.2.2: MBTIAnswer - 用户答题结果模型
├── B-3.2.3: MBTIResult - MBTI测试结果模型
└── B-3.2.4: MBTIReport - MBTI最终报告模型
```

------------------------------

### B4: 调用方式

```
B-4.1: 注册暴露模式
模块启动时向routing_agent注册自己的能力和字段参数。中枢根据注册信息自动注入字段用于验证和对齐。

B-4.2: 统一入口接口
async def run(request: dict) -> dict - 模块统一入口方法

B-4.3: 支持的步骤
├── B-4.3.1: step1 - 提供MBTI测试题
├── B-4.3.2: step2 - 生成12道选择题
└── B-4.3.3: step3 - 输出最终结果

B-4.4: 调用特性
自治模块，热插拔，三步流程，内置配置，数据库集成。模块存在即提供能力，缺失不影响全局。
```

------------------------------

### C1: 用户流程

```
C-1.1: MBTI三步测试流程
├── C-1.1.1: Step1 - 初始MBTI测试
│   ├── C-1.1.1.1: 提供测试题 - 从step1_questions.json获取MBTI测试题（不告知用户测试类型）
│   ├── C-1.1.1.2: 前端展示 - 通过routing_agent向entry_agent发送题目到前端
│   ├── C-1.1.1.3: 收集答案 - 用户完成答题后收集结果
│   └── C-1.1.1.4: 数据存储 - 通过routing_agent向database_agent存储Step1结果
├── C-1.1.2: Step2 - 12道选择题生成
│   ├── C-1.1.2.1: 结果分析 - 基于Step1答案分析用户MBTI类型倾向
│   ├── C-1.1.2.2: 生成选择题 - 从step2_questions.json生成针对性的12道选择题
│   ├── C-1.1.2.3: 前端展示 - 通过routing_agent向entry_agent发送选择题到前端
│   ├── C-1.1.2.4: 收集答案 - 用户完成12道选择题
│   └── C-1.1.2.5: 数据存储 - 通过routing_agent向database_agent存储Step2结果
└── C-1.1.3: Step3 - 最终结果输出
    ├── C-1.1.3.1: 综合评估 - 综合Step1和Step2结果进行MBTI类型判定
    ├── C-1.1.3.2: 生成报告 - 根据step3_scoring.json评分规则生成MBTI分析报告
    ├── C-1.1.3.3: 前端展示 - 通过routing_agent向entry_agent发送最终结果到前端
    └── C-1.1.3.4: 数据存储 - 通过routing_agent向database_agent存储最终结果
```

------------------------------

### C2: 前端交互流程

```
C-2.1: 前端协调机制
├── C-2.1.1: Step1交互 - 模块通过routing_agent向entry_agent发送测试题，前端生成答题界面
├── C-2.1.2: Step2交互 - 模块通过routing_agent向entry_agent发送12道选择题，前端生成选择界面
├── C-2.1.3: Step3交互 - 模块通过routing_agent向entry_agent发送最终结果，前端展示分析报告
└── C-2.1.4: 进度管理 - 每步完成后更新进度，支持中途暂停和继续

C-2.2: 数据库同步机制
├── C-2.2.1: 实时存储 - 每步完成后立即通过routing_agent存储到database_agent
├── C-2.2.2: 状态追踪 - 记录用户测试进度和当前步骤状态
└── C-2.2.3: 结果归档 - 完整保存测试过程和最终结果供后续分析
```

------------------------------

### C3: 步骤识别机制

```
C-3.1: 步骤识别
通过输入的step字段识别当前步骤，枚举值["step1", "step2", "step3"]

C-3.2: 状态管理
模块无状态设计，每次调用独立处理。测试状态通过database_agent持久化，支持多用户并行测试。

C-3.3: 流程控制
严格按照step1→step2→step3顺序执行，每步完成后存储结果并准备下一步数据。
```

------------------------------

### D1: 接口结构

```
D-1.1: 核心接口
async def run(request: dict) -> dict - MBTI测试模块统一入口方法

D-1.2: 接口契约
├── D-1.2.1: 输入参数 - 包含request_id、user_id、step、user_answers等字段的字典
├── D-1.2.2: 输出参数 - 包含处理结果、存储请求、前端响应的字典
└── D-1.2.3: 异常处理 - 标准错误信息和处理建议

D-1.3: 模块注册接口
async def register_capabilities() -> dict - 向中枢注册模块能力和字段定义
```

------------------------------

### D2: 状态管理

```
D-2.1: 无状态设计
模块本身完全无状态，每次调用独立处理。用户测试状态通过database_agent持久化。

D-2.2: 流程控制
三步严格顺序执行：step1 → step2 → step3。每步完成后自动存储结果并准备下一步。

D-2.3: 并发支持
支持多用户并行测试，使用asyncio异步处理，通过user_id区分不同用户会话。
```

------------------------------


------------------------------

### E1: 前端交互

```
E-1.1: 题目展示
模块通过routing_agent向entry_agent发送结构化题目数据，前端根据题目类型生成对应界面。

E-1.2: 进度管理
提供"MBTI测试进度 (Step 2/3)"的进度反馈，支持中途暂停和继续。

E-1.3: 结果展示
Step3完成后通过routing_agent向前端发送完整的MBTI分析报告。
```

------------------------------

### E2: 模块协作

```
E-2.1: routing_agent注册
启动时向routing_agent注册模块能力、字段定义和依赖关系。

E-2.2: 数据库协作
每步完成后通过routing_agent向database_agent发送存储请求。

E-2.3: 前端协作
通过routing_agent向entry_agent发送题目、进度和结果信息。
```

------------------------------

### E3: 错误处理

```
E-3.1: 常见错误
├── E-3.1.1: INPUT_INVALID - 输入参数验证失败
├── E-3.1.2: QUESTION_BANK_ERROR - 题库加载失败
├── E-3.1.3: SCORING_ERROR - 评分计算错误
└── E-3.1.4: STORAGE_ERROR - 数据存储失败

E-3.2: 错误处理
失败时返回错误信息和处理建议，保证用户体验不受影响。
```

------------------------------

### F1: 技术要求

```
F-1.1: 运行环境
├── F-1.1.1: Python 3.10+ 支持asyncio异步处理
├── F-1.1.2: 内存256MB+，CPU 1核+
└── F-1.1.3: 依赖中枢服务（routing_agent、database_agent、entry_agent）

F-1.2: 实现约束
├── F-1.2.1: 使用异步编程，禁止同步阻塞操作
├── F-1.2.2: 模块无状态设计，支持并发处理
└── F-1.2.3: 基于规则算法，无需LLM调用
```

------------------------------

### G1: 部署要求

```
G-1.1: 基础环境
├── G-1.1.1: Python 3.10+
├── G-1.1.2: 内存256MB+，CPU 1核+
└── G-1.1.3: 依赖中枢服务正常运行

G-1.2: 模块特性
├── G-1.2.1: 自治模块 - 内置所有配置和题库
├── G-1.2.2: 热插拔 - 可动态加载和卸载
└── G-1.2.3: 并发支持 - 异步处理多用户测试
```

------------------------------

### H1: 测试与验收

```
H-1.1: 测试方法
├── H-1.1.1: 三步流程测试 - 验证step1→step2→step3完整流程
├── H-1.1.2: 数据库集成测试 - 验证每步数据正确存储
├── H-1.1.3: 前端协作测试 - 验证题目和结果正确传递到前端
└── H-1.1.4: 并发测试 - 验证多用户同时测试不互相影响

H-1.2: 测试环境准备
├── H-1.2.1: 测试用户MBTI类型准备 - 测试MBTI类型: INTJ, ESFP, ENTP, ISFJ，各维度逆向映射: E↔I, S↔N, T↔F, J↔P，确保4个维度都有对应的逆向测试题
└── H-1.2.2: 模块接入说明 - mbti_agent是被动调用的业务模块，不包含启动逻辑和测试代码。整个Career Bot系统的启动入口统一在boot/目录中
```

------------------------------

### I1: 核心概念

```
I-1.1: MBTI测试流程
├── I-1.1.1: Step1 - 初始MBTI测试题（不告知用户测试类型）
├── I-1.1.2: Step2 - 基于Step1结果生成12道选择题
├── I-1.1.3: Step3 - 综合评估输出MBTI分析报告
└── I-1.1.4: 确定性算法 - 基于内置规则进行评分，无需LLM

H-2.2: 测试验证方法
├── H-2.2.1: 逆向映射验证 - 确认MBTI四维度的正确逆向映射关系
├── H-2.2.2: 问题生成验证 - 检查个性化问题的针对性和有效性
├── H-2.2.3: 前端显示验证 - 确认侧边栏模块正确显示，不干扰聊天流程
├── H-2.2.4: 能力评估验证 - 验证确定性算法的准确性和一致性
└── H-2.2.5: 状态流转验证 - 确保与routing_agent的无缝协作和状态转换

H-2.3: 验收门槛
生成变更必须先通过本模块用例再提交；未达门槛禁止继续生成下一文件。
```

------------------------------

### I2: 协作关系

```
I-2.1: routing_agent服务协作
├── I-2.1.1: routing_agent - 注册能力，接收调用请求，协调其他服务
├── I-2.1.2: database_agent - 存储测试过程和结果数据
└── I-2.1.3: entry_agent - 发送题目和结果到前端展示

I-2.2: 职责边界
├── I-2.2.1: 负责 - 完整MBTI测试流程（3步）
├── I-2.2.2: 不负责 - 用户界面渲染、数据持久化实现
└── I-2.2.3: 特性 - 自治、热插拔、无状态、并发支持
```

------------------------------

### I3: 实现要点


I-3.2: 数据流转
├── I-3.2.1: 每步存储 - 通过routing_agent实时存储到database_agent
├── I-3.2.2: 前端交互 - 通过routing_agent发送到entry_agent展示
└── I-3.2.3: 状态跟踪 - 记录用户当前测试步骤和进度

### I1: 术语与名词表

```
I-1.1: 核心概念统一定义
├── I-1.1.1: MBTI逆向维度测试 - 基于用户原MBTI类型，测试其在四个逆向维度上的能力表现
├── I-1.1.2: 逆向维度映射 - E↔I, S↔N, T↔F, J↔P的严格对应关系
├── I-1.1.3: 维度能力评估 - 根据逆向测试得分，评定"典型类型"/"具备逆向能力"/"强逆向能力"三级水平
├── I-1.1.4: 确定性算法 - 基于预定义规则的评分计算，不依赖LLM调用
└── I-1.1.5: 双阶段处理 - 初始问题生成阶段 + 答案处理评估阶段
```

------------------------------

### K1: 实现约束

```
K-1.1: 开发规范
├── K-1.1.1: 模块边界 - 仅在applications/mbti_agent/目录内开发
├── K-1.1.2: 异步编程 - 使用asyncio，禁止同步阻塞和多线程
├── K-1.1.3: 数据安全 - 日志中不包含敏感信息
└── K-1.1.4: 标准异常 - 使用标准异常处理机制

I-2.2: 下游调用关系
├── I-2.2.1: database_agent - MBTI逆向评估结果存储
├── I-2.2.2: ninetest_agent - 自动触发下一阶段测试
├── I-2.2.3: global_schemas - 数据模型与验证
└── I-2.2.4: 数据输出 - 四维逆向能力评估结果

I-2.3: 职责边界
├── I-2.3.1: 核心职责 - MBTI逆向维度测试与能力评估
├── I-2.3.2: 不负责 - MBTI基础类型判定、职业匹配推荐
├── I-2.3.3: 处理方式 - 被动调用，无状态，双阶段处理
└── I-2.3.4: 并发控制 - 支持多用户并行处理，每次调用独立完成
```

------------------------------



### I4: 契约与字段

```
I-4.1: 核心接口契约
async def run(request: AgentRequest) -> AgentResponse - MBTI逆向维度测试统一入口方法

I-4.2: 输入字段全集
├── I-4.2.1: request_id - str, 必填, 请求唯一标识符
├── I-4.2.2: task_type - str, 必填, 枚举值["mbti_followup_test", "generate_reverse_test", "analyze_ability_assessment"]
├── I-4.2.3: context.data.mbti_type - str, 必填, 正则[EI][SN][TF][JP]
├── I-4.2.4: context.data.stage - str, 必填, 枚举值["question_generation", "answer_processing"]
├── I-4.2.5: context.data.current_task_step - str, 必填, 枚举值["initial", "processing"]
├── I-4.2.6: context.data.user_answers - List[Dict], 仅答案处理阶段必填
├── I-4.2.7: context.metadata.user_id - str, 必填, 用户标识符
└── I-4.2.8: additional_params - Dict, 可选, 附加参数

I-4.3: 输出字段全集
├── I-4.3.1: request_id - str, 必填, 对应请求ID
├── I-4.3.2: agent_name - str, 必填, 固定值"mbti_agent"
├── I-4.3.3: success - bool, 必填, 处理成功状态
├── I-4.3.4: timestamp - str, 必填, ISO8601格式响应时间
├── I-4.3.5: response.status - str, 必填, 枚举值["QUESTIONS_READY", "TEST_COMPLETE", "ERROR"]
├── I-4.3.6: response.data - Dict, 成功时必填, 业务数据载荷
├── I-4.3.7: response.trigger_next_agent - str, 测试完成时必填, 固定值"ninetest_agent"
├── I-4.3.8: error.code - str, 失败时必填, {DOMAIN}/{REASON}格式
└── I-4.3.9: error.message - str, 失败时必填, 错误描述

I-4.4: 错误码全集
├── I-4.4.1: VALIDATION/INVALID_INPUT - 输入参数验证失败
├── I-4.4.2: MBTI/INVALID_MBTI_TYPE - MBTI类型格式错误
├── I-4.4.3: MBTI/QUESTION_GENERATION_ERROR - 逆向维度问题生成失败
├── I-4.4.4: MBTI/ABILITY_CALCULATION_ERROR - 能力评估计算错误
├── I-4.4.5: MBTI/INCOMPLETE_ANSWERS - 测试答案不完整
├── I-4.4.6: MBTI/DIMENSION_MAPPING_ERROR - 维度映射配置错误
├── I-4.4.7: CONFIG/NOT_FOUND - 配置项不存在
├── I-4.4.8: CONFIG/INVALID_FORMAT - 配置格式错误
└── I-4.4.9: TIMEOUT/REQUEST_TIMEOUT - 请求处理超时

I-4.5: 配置清单
├── I-4.5.1: mbti_agent.test_config - 测试基础配置
├── I-4.5.2: mbti_agent.dimension_mapping - 维度映射关系
├── I-4.5.3: mbti_agent.scoring_rules - 评分规则配置
├── I-4.5.4: mbti_agent.question_templates - 问题模板配置
├── I-4.5.5: mbti_agent.timeout_config - 超时配置
└── I-4.5.6: mbti_agent.retry_config - 重试策略配置
```

------------------------------



------------------------------

### J1: MBTI维度测试系统

```
J-1.1: 逆向维度映射
├── J-1.1.1: E (外向) → I (内向) - 测试外向者的内向能力
├── J-1.1.2: I (内向) → E (外向) - 测试内向者的外向能力
├── J-1.1.3: S (感觉) → N (直觉) - 测试感觉型的直觉能力
├── J-1.1.4: N (直觉) → S (感觉) - 测试直觉型的感觉能力
├── J-1.1.5: T (思考) → F (情感) - 测试思考型的情感能力
├── J-1.1.6: F (情感) → T (思考) - 测试情感型的思考能力
├── J-1.1.7: J (判断) → P (感知) - 测试判断型的感知能力
└── J-1.1.8: P (感知) → J (判断) - 测试感知型的判断能力

J-1.2: 评分标准系统
├── J-1.2.1: 固定评分规则
│   ├── J-1.2.1.1: 选择A - 得1分，表示具备逆向能力
│   ├── J-1.2.1.2: 选择B - 得0分，表示偏向原维度
│   └── J-1.2.1.3: 总分范围 - 每维度0-3分（3个问题）
└── J-1.2.2: 解释分级标准
    ├── J-1.2.2.1: 0-1分 - 典型类型，逆向能力相对缺乏，偏向原维度特征
    ├── J-1.2.2.2: 2分 - 具备逆向能力，可以在需要时调用逆向维度能力
    └── J-1.2.2.3: 3分 - 强逆向能力，接近逆向类型水平，具备杰出的平衡能力

J-1.3: 问题ID兼容性设计
├── J-1.3.1: 新格式 - "{dimension}-{question_id}"复合ID，全局唯一（如"I-1"）
├── J-1.3.2: 旧格式 - 纯数字ID，保持向后兼容
└── J-1.3.3: 处理优先级 - 优先匹配复合ID，回退到legacy ID
```

------------------------------

### J2: 配置管理系统

```
J-2.1: 配置数据结构
从global_config获取，包含dimensionAssessments数组，每个元素包含targetUserType、assessedAbility、questions、interpretationTemplates等字段。

J-2.2: 配置优化策略
├── J-2.2.1: 预处理机制 - 启动时转换配置为高效查找结构
├── J-2.2.2: 完整性验证 - 验证关键配置的完整性，缺失时系统退出
└── J-2.2.3: 兼容性支持 - 支持多种配置键名的灵活解析

J-2.3: 配置数据预处理
├── J-2.3.1: 启动优化 - 将JSON配置转换为O(1)查找的字典结构
├── J-2.3.2: 维度索引 - 按维度字符建立快速访问索引
└── J-2.3.3: 完整性验证 - 验证关键配置的完整性
```

------------------------------

### J3: 输出数据结构规范

```
J-3.1: 预格式化输出结构
mbti_agent负责输出MBTI评估结果，输出结构必须与database_agent的用户画像存储格式完全匹配。

J-3.2: MBTI评估结果输出格式
包含user_id、mbti_assessment（mbti_type、assessment_date、confidence_score、detailed_scores、reverse_ability_analysis、assessment_summary）、metadata等字段。

J-3.3: 输出数据校验规则
├── J-3.3.1: mbti_type - 必须为有效的16种MBTI类型之一
├── J-3.3.2: assessment_date - 必须为ISO8601格式的UTC时间
├── J-3.3.3: confidence_score - 浮点数，范围0.0-1.0，基于答题一致性计算
├── J-3.3.4: detailed_scores - 四个维度得分，格式为"维度(百分比%)"
├── J-3.3.5: reverse_ability_analysis - 每个维度的逆向能力分析
├── J-3.3.6: score - 整数，范围0-100，表示逆向维度能力得分
└── J-3.3.7: level - 枚举值："典型类型"/"具备逆向能力"/"强逆向能力"

J-3.4: 原性格维度分析
├── J-3.4.1: 四维度映射 - E↔I, S↔N, T↔F, J↔P的逆向关系
├── J-3.4.2: 能力评估 - 典型类型、具备逆向能力、强逆向能力三级分析
├── J-3.4.3: 个性化解释 - 根据得分匹配相应的解释模板和发展建议
└── J-3.4.4: 结构化报告 - 生成完整的MBTI逆向测试分析报告
```

