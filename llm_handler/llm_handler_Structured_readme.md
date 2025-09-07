# llm_handler_agent_Structured_readme.md

## A: 开发边界与职责说明

### A1: 模块基本定义
```
llm_handler_agent是Career Bot系统中唯一负责大语言模型（LLM）调用执行的模块。它不负责构建prompt，也不解析结果含义，仅作为"LLM调用的中转站"，完成大模型推理请求并返回原始响应。作为系统唯一的LLM调用引擎入口，确保所有大模型调用的统一性、安全性和可监控性，将LLM调用与业务逻辑完全分离。
```

------------------------------

### A2: 核心职责范围
```
专注于LLM调用执行，不涉及prompt构建、结果解析或业务逻辑处理。接收已构建好的prompt和调用参数，返回未处理的模型原始输出，确保LLM调用与业务逻辑的完全解耦。提供标准化的LLM调用服务，支持调用追踪、性能监控和错误处理。
```

------------------------------

### A3: 模块协作规范
```
├── A-3.1: 被动调用模式 - 仅响应routing_agent的任务分发
├── A-3.2: 无状态设计 - 完全无状态设计，不保存任何调用历史
├── A-3.3: 中枢调度 - 仅接受routing_agent分发的LLM任务
└── A-3.4: 统一入口 - 仅暴露run()方法作为唯一接口
```

------------------------------

## B: 系统架构与模块定义

### B1: 系统架构位置
```
上游模块（构建Prompt） → routing_agent → [llm_handler_agent] → OpenAI API
                                              ↓
                       原始结果返回 → routing_agent → 上游模块
```

------------------------------

### B2: 模块内部架构
```
├── B-2.1: Main（主文件）- 只做策略选择、依赖装配、流程编排；禁止任何业务规则、存储访问、外部I/O
├── B-2.2: Adapter（适配层）- 只实现外设与机制（LLM API调用、配置管理等）；禁止写业务决策
└── B-2.3: Aux（私有实现）- 仅供Main/Adapter内部复用；不得跨模块导出；禁止出现横向依赖
```

------------------------------

## C: 输入输出规范、配置机制、模型路径、调用方式

### C1: 核心接口定义
```
├── C-1.1: 主接口规范
│   ├── Name: run(request: AgentRequest) -> AgentResponse
│   ├── Method: 异步函数调用
│   ├── Path/Topic: 通过routing_agent内部调用，无HTTP路径
│   └── 错误码: LLM/API_ERROR, LLM/INVALID_PROMPT, LLM/RATE_LIMITED, LLM/NETWORK_ERROR
├── C-1.2: 最小请求格式
│   ├── request_id: uuid-string
│   ├── task_type: llm_completion
│   ├── user_id: string
│   └── context: {"data": {"prompt": "string"}}
└── C-1.3: 最小响应格式
    ├── success: true
    ├── data: {"response": "LLM输出内容"}
    └── processing_time: "3.2s"
```

------------------------------

### C2: 支持的任务类型
```
├── C-2.1: 核心任务类型
│   ├── llm_completion - 标准文本生成任务
│   ├── llm_chat - 对话式交互任务
│   └── llm_json - 结构化JSON输出任务
└── C-2.2: 辅助任务类型
    ├── health_check - 模块健康状态检查
    └── api_status - LLM调用API可用性检查
```

------------------------------

### C3: 快速启动指南
```
├── C-3.1: 环境要求
│   ├── Python 3.10+
│   ├── OpenAI API密钥配置
│   └── routing_agent依赖就绪
├── C-3.2: 安装配置
│   ├── 安装依赖: pip install openai==1.12.0 aiohttp>=3.8.0
│   ├── 环境变量: export OPENAI_API_KEY="your-api-key"
│   └── 模型配置: export LLM_MODEL="gpt-4o-2024-08-06"
└── C-3.3: 运行测试
    └── 最小运行测试代码示例（仅用于协议理解，不得据此实现）
```

------------------------------

### C4: 配置获取机制
```
├── C-4.1: 配置来源规范
│   ├── 获取方式: await routing_agent.get_config("llm_handler_agent", config_type)
│   ├── 配置类型: "model_config", "rate_limits", "timeout_config"
│   └── 模型配置: 强制使用gpt-4o-2024-08-06
├── C-4.2: 必需配置项
│   ├── 模型配置: model_config - 模型选择和参数设置
│   ├── API配置: api_config - API密钥和连接设置
│   ├── 超时配置: timeout_config - 请求和响应超时设置
│   ├── 重试配置: retry_config - 重试策略和次数
│   ├── 安全配置: security_config - 输入验证和审计设置
│   └── 紧急Prompt: emergency_prompts - 系统诊断用内置prompt
└── C-4.3: 配置唯一来源规则
    ├── 配置仅可经由routing_agent的global_config读取
    ├── 禁止本地硬编码可变配置
    └── 配置键名/层级不可私改；新增键必须提供默认值、回滚策略
```

------------------------------

## D: 用户流程、对话流程、意图识别机制

### D1: 用户流程
```
⚠️ 未定义 - 本模块作为LLM调用中转站，不涉及用户流程和意图识别机制
```

------------------------------

### D2: 对话流程
```
⚠️ 未定义 - 本模块仅负责LLM调用执行，不处理对话流程逻辑
```

------------------------------

### D3: 意图识别机制
```
⚠️ 未定义 - 意图识别由上游模块负责，本模块不涉及意图识别
```

------------------------------

## E: 接口结构、状态管理、日志与异常策略

### E1: 接口结构定义
```
├── E-1.1: 统一入口接口
│   ├── 函数签名: async def run(request: AgentRequest) -> AgentResponse
│   ├── 输入参数: request - 扁平化请求载荷
│   ├── 返回值: AgentResponse - 扁平化响应载荷
│   └── 异常: APIConnectionError, TokenLimitError, ValidationError
├── E-1.2: 完整AgentRequest输入结构
│   ├── request_id: uuid-string - 请求唯一标识符
│   ├── task_type: string - 任务类型标识
│   ├── user_id: string - 用户标识
│   ├── timestamp: ISO时间戳
│   ├── context: 核心任务数据和元数据
│   └── additional_params: 可选附加参数
└── E-1.3: 完整AgentResponse输出结构
    ├── request_id: 对应请求ID
    ├── agent_name: "llm_handler_agent"
    ├── success: bool - LLM调用成功状态
    ├── timestamp: 响应时间戳
    ├── response: LLM响应结果数据
    └── error: 错误信息（成功时为null）
```

------------------------------

### E2: 状态管理策略
```
├── E-2.1: 无状态设计原则
│   ├── 完全无状态设计，不保存任何调用历史
│   ├── 模块不得直接访问持久化（DB/Cache/FS）
│   └── 必须通过指定Adapter间接访问database_agent
└── E-2.2: 可重复执行要求
    └── 生成的任意函数需满足幂等/可重放要求（同输入不应产生额外副作用）
```

------------------------------

### E3: 日志与异常策略
```
├── E-3.1: 日志必填字段规范
│   ├── request_id - 请求追踪标识
│   ├── module_name - 模块名称标识
│   ├── operation - 操作类型标识
│   ├── duration_ms - 执行耗时统计
│   ├── success - 执行结果状态
│   └── retry_count - 重试次数统计
├── E-3.2: 敏感信息处理
│   ├── 日志/错误信息不得包含密钥、令牌、身份证件
│   └── 必要时进行脱敏处理
├── E-3.3: 错误码规范
│   ├── 命名格式: 采用LLM/{REASON}命名
│   ├── API调用相关: LLM/API_TIMEOUT, LLM/TOKEN_LIMIT, LLM/RATE_LIMITED, LLM/API_ERROR, LLM/INVALID_MODEL
│   └── 输入验证相关: LLM/INVALID_PROMPT, LLM/PROMPT_TOO_LONG, LLM/INVALID_PARAMS
└── E-3.4: 异常传播规范
    ├── 只允许抛出仓库标准异常基类及其子类
    ├── 不得抛裸异常
    └── 错误信息需面向调用方而非实现细节
```

------------------------------

## F: UI组件结构、事件响应、错误处理机制

### F1: UI组件结构
```
⚠️ 未定义 - 本模块为后端服务模块，不涉及UI组件
```

------------------------------

### F2: 事件响应机制
```
⚠️ 未定义 - 本模块采用被动调用模式，不涉及主动事件响应
```

------------------------------

### F3: 错误处理机制
```
├── F-3.1: 常见故障排查
│   ├── LLM/API_ERROR → 检查OpenAI API密钥有效性
│   ├── LLM/RATE_LIMITED → LLM调用过于频繁，等待1分钟后重试
│   └── LLM/NETWORK_ERROR → 检查网络状态和防火墙设置
├── F-3.2: 失败回退策略
│   └── 失败时必须返回可操作指令（如flow指令/重试建议/联系渠道）
└── F-3.3: 常见问题解决方案
    ├── API调用超时 → 调整timeout配置、检查网络连接
    ├── Token超限 → 减少prompt长度或max_tokens设置
    └── 速率限制 → 降低调用频率、升级API配额
```

------------------------------

## G: WebSocket/LLM/上传机制等集成接口

### G1: LLM集成接口
```
├── G-1.1: LiteLLM客户端集成
│   ├── 模型统一: 强制使用gpt-4o-2024-08-06
│   ├── API密钥: 通过model_config["api_key"]获取
│   └── 调用方法: 使用litellm.acall异步调用
├── G-1.2: LLM调用完整规范
│   ├── 唯一入口: 系统中所有LLM调用的唯一通道
│   ├── 严禁绕过: 任何模块不得直接访问OpenAI、Claude、Gemini等接口
│   └── 模型统一: 强制使用gpt-4o-2024-08-06
└── G-1.3: LLM调用链路流程
    ├── 任务接收与验证 → 验证任务类型、提取prompt、设置调用上下文
    ├── 模型配置加载 → 加载模型配置、初始化LLM客户端、应用速率限制
    ├── LLM API调用执行 → 执行模型推理、记录统计数据、处理异常重试
    └── 响应格式化与返回 → 格式化响应、统计Token使用、返回标准格式
```

------------------------------

### G2: LLM任务类型支持

```
├── G-2.1: 意图识别任务 - 用户消息的意图分类
├── G-2.2: 对话生成任务 - 基于上下文的回复生成
├── G-2.3: 文档解析任务 - 简历企业文档职位文档的解析
└── G-2.4: 分析报告生成 - 综合分析报告的生成任务
```

------------------------------

### G3: LLM调用优化

```
├── G-3.1: 调用缓存机制 - 相同请求的缓存优化
├── G-3.2: 并发控制 - LLM调用的并发数量限制
├── G-3.3: 失败重试 - LLM调用失败的重试策略
└── G-3.4: 性能监控 - LLM调用的性能指标收集
```

------------------------------

### G4: WebSocket集成
```
⚠️ 未定义 - 本模块不涉及WebSocket通信机制
```

------------------------------

### G5: LLM调用协调机制集成

```
├── G-5.1: routing_agent集成机制 - 通过routing_agent调度LLM任务
├── G-5.2: LLM超时配置管理 - llm_handler_agent: 60秒超时设置
├── G-5.3: Intent分类Prompt配置 - routing_agent管理的intent分类prompt配置
└── G-5.4: LLM任务调度支持 - 支持"llm_*"模式的intent映射
```

------------------------------

### G6: 上传机制
```
⚠️ 未定义 - 本模块不涉及文件上传处理机制
```

------------------------------

## H: 环境配置、运行要求、版本依赖、模块限制

### H1: 环境配置要求
```
├── H-1.1: 基础环境
│   ├── Python版本: Python 3.10+
│   ├── 核心依赖: litellm, routing_agent
│   └── API密钥: OpenAI API Key
├── H-1.2: 资源要求
│   ├── 内存: 256MB+
│   └── CPU: 1核+
└── H-1.3: 环境变量配置
    ├── OPENAI_API_KEY: OpenAI API密钥
    └── LLM_MODEL: gpt-4o-2024-08-06
```

------------------------------

### H2: 版本依赖清单
```
├── H-2.1: 第三方库依赖
│   ├── litellm>=1.0.0 - LLM API统一调用库
│   ├── openai>=1.0.0 - OpenAI官方Python SDK
│   └── asyncio - Python内置异步支持
├── H-2.2: 上游依赖模块
│   ├── routing_agent - 唯一调用来源
│   ├── global_schemas - 数据模型定义
│   └── OpenAI API - 实际LLM服务
└── H-2.3: 技术规范约束
    ├── Pydantic V2完整规范 - 必须使用model_validate(), model_dump(), Field(), BaseModel
    ├── 异步处理规范 - 所有LLM调用方法使用async def
    └── 并发原语限制 - 仅允许使用异步原语，禁止线程池/进程池
```

------------------------------

### H3: 模块限制规范
```
├── H-3.1: 性能边界约束
│   ├── 并发限制: 最大100个并发调用
│   ├── Token限制: 输入最大50000 tokens，输出最大4000 tokens
│   └── 响应时间: 最大300秒超时
├── H-3.2: 安全与合规限制
│   ├── 秘钥管理: 不得在代码/README/示例中出现任何真实秘钥
│   ├── 输入校验: 所有外部输入必须显式校验（长度/类型/枚举/格式）
│   └── 权限最小化: API密钥通过global_config安全管理
└── H-3.3: 开发边界限制
    ├── 工作区限制: 生成和修改仅允许发生在llm_handler_agent/内
    ├── 粒度限制: 单次变更仅允许操作一个文件；若超过300行，自动截断
    └── 结构稳定性: 禁止因实现便利而新建"公共"目录
```

------------------------------

## I: 测试策略、验收机制、部署策略、未来规划

### I1: 测试策略
```
├── I-1.1: 生产级测试要求
│   ├── 真实API: 使用真实的OpenAI API进行测试
│   ├── 完整调用链: 测试routing_agent → llm_handler_agent → OpenAI完整链路
│   └── Token计费: 验证费用统计准确性
├── I-1.2: 关键测试用例
│   ├── 冒烟链路测试 - 验证基本LLM调用功能
│   └── 失败路径测试 - 验证错误处理和异常恢复
└── I-1.3: 最小用例要求
    └── 本模块至少提供冒烟链路与失败路径两类用例；用例不得Mock掉对外契约
```

------------------------------

### I2: 验收机制
```
├── I-2.1: 验收门槛
│   └── 生成变更必须先通过本模块用例再提交；未达门槛禁止继续生成下一文件
└── I-2.2: SLA承诺
    ├── 可用性: 99.5%服务可用性
    ├── 响应时间: 95% LLM调用 < 30秒（性能目标，超时上限300秒）
    ├── 并发能力: 支持100并发LLM调用
    └── Token准确性: Token计费统计100%准确
```

------------------------------

### I3: 部署策略
```
├── I-3.1: 部署环境要求
│   ├── Python版本: Python 3.10+
│   ├── 核心依赖: litellm, routing_agent
│   ├── API密钥: OpenAI API Key
│   └── 资源要求: 内存256MB+, CPU 1核+
└── I-3.2: 监控指标
    ├── 调用量: 每分钟LLM调用次数
    ├── 响应时间: 平均响应时间 < 3000ms
    ├── 成功率: 调用成功率 > 99%
    └── Token消耗: 日Token使用量和费用
```

------------------------------

### I4: 未来规划
```
⚠️ 未定义 - 未来规划和扩展计划需要进一步明确
```

------------------------------

## J: 未定义项、待补要点、黑名单、禁用规则

### J1: 数据模型规范
```
├── J-1.1: 必须使用的Schema
│   ├── 从global_schemas导入: AgentRequest, AgentResponse, LLMRequest, LLMResponse
│   └── 模块特定Schema: TokenUsage, ModelConfiguration
├── J-1.2: LLMRequest请求模型
│   ├── prompt: str (min_length=1, max_length=50000)
│   ├── system_prompt: Optional[str] (max_length=5000)
│   ├── temperature: float (default=0.7, ge=0.0, le=2.0)
│   ├── max_tokens: int (default=1000, ge=1, le=4000)
│   └── json_mode: bool (default=False)
└── J-1.3: LLMResponse响应模型
    ├── raw_output: str - LLM原始输出
    ├── model_used: str - 使用的模型名称
    ├── tokens_used: TokenUsage - Token使用统计
    └── call_duration_ms: float - 调用耗时毫秒
```

------------------------------

### J2: 可用Prompt模板
```
├── J-2.1: Prompt模板规范
│   └── 本模块不构建prompt，所有prompt由上游模块构建完成后传入
└── J-2.2: 紧急Prompt配置
    └── 仅在系统诊断等紧急情况下使用内置prompt: emergency_prompts.system_status_check
```

------------------------------

### J3: 性能指标规范
```
├── J-3.1: 必须暴露的指标
│   ├── 调用次数: llm_handler_agent_requests_total
│   ├── 成功率: llm_handler_agent_success_rate
│   └── 时延分布: llm_handler_agent_duration_seconds
└── J-3.2: 模块特定指标
    ├── Token消耗: llm_handler_agent_tokens_used_total
    ├── API费用: llm_handler_agent_api_cost_total
    └── 模型调用: llm_handler_agent_model_calls_total
```

------------------------------

### J4: 关键词黑名单（检测红线）
```
├── J-4.1: 禁止本地业务模型定义
│   └── "class .*Model", "data class .*", "interface .*DTO"
├── J-4.2: 禁止硬编码配置
│   └── "API_KEY=", "timeout\\s*=\\s*\\d+", "retry\\s*=\\s*\\d+"
├── J-4.3: 禁止跨层I/O
│   └── 在Main/Aux中出现"http", "db", "sql", "open(", "requests", "fetch"
├── J-4.4: 禁止并发越界
│   └── "Thread", "Process", "fork", "Pool"
└── J-4.5: 禁止未脱敏日志
    └── "print(", "console.log(", "logging.info(f\\".*password|token|secret"
```

------------------------------

### J5: 待补要点清单
```
├── J-5.1: 配置参数待补
│   └── API密钥轮换机制
│       ├── 配置键名: api_config.key_rotation_enabled
│       ├── 建议默认值: false
│       ├── 取值域: [true, false]
│       ├── 影响面: API安全性和故障恢复
│       └── 最小决策集: 选项1-启用轮换（高安全性）, 选项2-单一密钥（简化管理）
├── J-5.2: Schema字段待补
│   └── Token使用详情
│       ├── 模型名称: TokenUsage
│       ├── 缺失字段: completion_tokens_detail
│       ├── 建议类型: Dict[str, int]
│       ├── 默认值: {}
│       ├── 影响面: 费用计算和性能分析
│       └── 最小决策集: 选项1-详细统计（便于分析）, 选项2-简化统计（降低开销）
└── J-5.3: 错误码待补
    └── 模型切换策略
        ├── 错误场景: 主模型不可用时的备选策略
        ├── 建议错误码: LLM/MODEL_FALLBACK_TRIGGERED
        ├── 错误消息模板: "主模型{primary_model}不可用，切换到备选模型{fallback_model}"
        ├── 影响面: 服务连续性和用户体验
        └── 最小决策集: 选项1-自动切换备选模型（高可用性）, 选项2-直接失败并报告（透明性优先）
```

------------------------------

## 📋 模块契约总结

该模块是Career Bot系统AI能力的核心基础设施，确保所有LLM调用任务的统一、安全和高效执行。通过标准化的API调用接口和完整的错误处理机制，为整个系统提供稳定可靠的AI推理服务。

