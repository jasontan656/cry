# final_analysis_output_agent 结构化文档骨架

# 字段迁移说明  
```
所有数据模型/Schema已迁移至global_schemas.json，由routing_agent动态生成和分发：
- MBTIAssessment模型 - MBTI评估数据已迁移至global_schemas.json
- NinetestAssessment模型 - 天赋测试数据已迁移至global_schemas.json
- Resume26Fields模型 - 用户26字段档案已迁移至global_schemas.json
- ProcessingResult模型 - 分析处理结果已迁移至global_schemas.json
- SystemError模型 - 系统错误处理已迁移至global_schemas.json

所有配置参数已迁移至global_config.json：
- final_analysis_output_agent配置组包含output_config、template_version等
- LLM分析提示模板、输出格式模板、报告配置已迁移
```

## A: 开发边界与职责说明

### A-1: 模块基本定义
```
final_analysis_output_agent是Career Bot系统的用户画像分析总结服务，负责整合多个测试结果，调用LLM生成职业分析文本，并返回JSON格式的分析结果给前端显示和数据库存储。该模块通过双阶段分析机制提供渐进式的职业建议：第一阶段分析（用户完成MBTI→NINETEST测试后，整合两个测试结果，生成基础职业画像分析）和第二阶段分析（用户完成简历上传和信息补足后，结合简历信息和第一阶段分析，生成最终综合分析）。
```

------------------------------

### A-2: 核心功能特性
```
A-2.1: 双阶段分析机制
├── A-2.1.1: 第一阶段分析 - 用户完成MBTI→NINETEST测试后的基础职业画像分析
├── A-2.1.2: 第二阶段分析 - 用户完成简历上传和信息补足后的最终综合分析
├── A-2.1.3: 渐进式分析 - 从基础画像到综合分析的两阶段过程
└── A-2.1.4: 事件驱动触发 - 基于上游模块完成事件自动触发分析流程

A-2.2: 多源数据智能整合
├── A-2.2.1: 第一阶段整合 - MBTI性格测试 + ninetest反向测试 → 基础职业画像
├── A-2.2.2: 第二阶段整合 - 第一阶段报告 + 简历分析 + 技能补足 → 最终综合分析
├── A-2.2.3: 动态数据验证 - 自动验证上游数据完整性，确保分析质量
└── A-2.2.4: 智能补缺机制 - 当部分数据缺失时，提供合理的分析建议并标注数据来源

A-2.3: LLM分析调用
├── A-2.3.1: 综合分析报告生成 - 通过大语言模型进行职业分析报告生成
├── A-2.3.2: 职业建议生成 - 基于测试结果的个性化职业方向建议
├── A-2.3.3: 个性化推荐 - 具体可执行的职业发展步骤
└── A-2.3.4: 风险预警提示 - 需要慎重考虑的职位和心理风险

A-2.4: JSON格式输出
├── A-2.4.1: 标准化响应 - 每次分析完成后返回JSON格式的分析文本给前端显示
├── A-2.4.2: 数据库存储 - JSON格式分析结果传递给database_agent存储
├── A-2.4.3: 状态感知处理 - 根据用户当前完成阶段，选择对应的分析模板和数据源
└── A-2.4.4: 质量控制 - 严禁Fallback，确保分析结果真实性
```

------------------------------

### A-3: 严格边界约束
```
A-3.1: 适用范围与角色
├── A-3.1.1: 目标 - 限制自动化生成在文件创建/编辑/依赖方向/接口契约四个维度的自由度，避免脑补
└── A-3.1.2: 占位符映射 - MODULE_NAME: final_analysis_output_agent, MODULE_ROOT: applications/final_analysis_output_agent/, GLOBAL_SCHEMAS: global_schemas模块, GLOBAL_CONFIG: routing_agent的config_manager服务, STATE_STORE: database_agent统一管理的存储层

A-3.2: 目录与文件边界
├── A-3.2.1: 工作区 - 生成和修改仅允许发生在applications/final_analysis_output_agent/内，禁止创建、移动、重命名、删除该目录之外的任何文件/目录
├── A-3.2.2: 主入口约定 - 模块主入口文件名与final_analysis_output_agent同名，非主入口的新增文件必须归类为Adapter或Aux
├── A-3.2.3: 粒度限制 - 单次变更仅允许操作一个文件；若超过300行，自动截断并停止，等待下一次续写
└── A-3.2.4: 结构稳定性 - 禁止因实现便利而新建"公共"目录；禁止在模块间互放工具文件；不得私自抽公共层

A-3.3: 职责分层边界
├── A-3.3.1: Main（主文件） - 只做策略选择、依赖装配、流程编排；禁止任何业务规则、存储访问、外部I/O
├── A-3.3.2: Adapter（适配层） - 只实现外设与机制（HTTP/DB/Cache/Queue/FS/LLM调用等）；禁止写业务决策
├── A-3.3.3: Aux（私有实现） - 仅供Main/Adapter内部复用；不得跨模块导出；禁止出现横向依赖
└── A-3.3.4: 拆分触发 - 当单文件同时承担两类以上变更原因或超过200行时必须拆分到对应层
```

------------------------------

## B: 系统架构与模块定义

### B-1: 架构设计原则
```
B-1.1: 主入口文件职责 - 仅提供统一接口注册和任务分发能力，不实现具体业务逻辑，保持主文件简洁性和可维护性
B-1.2: 业务实现分离 - 所有具体业务功能必须通过独立的业务处理模块实现，包括多agent分析数据整合与处理逻辑、综合分析报告生成与格式化、输出格式适配与模板渲染、数据模型转换与结构化输出、报告配置加载与模板管理
B-1.3: 模块化组织约束 - 避免单一文件承载过多业务逻辑，按功能域进行合理拆分；每个业务模块专注单一职责，确保代码可测试性和可维护性；通过依赖注入和接口抽象，降低模块间耦合度
B-1.4: 配置驱动 - 所有LLM分析提示模板、输出格式模板、报告配置通过routing_agent从global_config动态获取，支持热更新和版本管理
```

------------------------------

### B-2: 系统架构位置
```
B-2.1: 架构流程图
用户完成测试 → entry_agent → routing_agent → [final_analysis_output_agent]
                                                      ↓
            数据整合 → llm_handler_agent (分析) → JSON分析文本
                  ↓                        ↓
              database_agent ← ← ← ← ← 文本存储

B-2.2: 模块接入说明 - final_analysis_output_agent是被动调用的业务模块，不包含启动逻辑和测试代码。系统启动使用python main.py --start从boot/启动整个系统，模块装配通过boot/launcher.py基于applications/__registry__.py装配，服务调用启动后通过routing_agent进行统一调度，功能测试测试逻辑已迁移至utility_tools/global_test/进行独立管理
```

------------------------------

## C: 输入输出规范、配置机制、模型路径、调用方式

### C-1: 接口契约规范
```
C-1.1: 统一入口接口
async def run(request: AgentRequest) -> AgentResponse:
    模块统一入口方法
    Args: request: 扁平化请求载荷 - request_id: str请求唯一标识符, task_type: str任务类型标识, user_id: str用户标识符, session_id: str会话标识符, message: str用户消息, intent: str意图标识等直接字段
    Returns: AgentResponse: 扁平化响应载荷 - request_id: str对应请求ID, agent_name: str处理模块名称, success: bool处理成功状态, timestamp: str响应时间戳, processing_status: str处理状态, results: Dict处理结果数据, error_details: Dict错误信息（成功时为null）
    Raises: ValidationError输入参数验证失败, ConfigurationError配置获取失败, ProcessingError业务处理异常

C-1.2: 支持的任务类型
├── C-1.2.1: 核心任务类型 - 第一阶段分析: first_analysis_report, 综合分析报告: comprehensive_analysis_report, 分析报告生成: analysis_generation, 数据整合分析: data_integration_analysis
└── C-1.2.2: 辅助任务类型 - 健康检查: health_check, 配置获取: get_config
```

------------------------------

### C-2: 错误码规范
```
C-2.1: 标准错误码格式 - 使用{DOMAIN}/{REASON}命名格式

C-2.2: 通用错误码
├── C-2.2.1: 验证类错误 - VALIDATION/INVALID_INPUT输入参数验证失败
├── C-2.2.2: 配置类错误 - CONFIG/NOT_FOUND配置项不存在, CONFIG/INVALID_FORMAT配置格式错误
├── C-2.2.3: 系统类错误 - TIMEOUT/REQUEST_TIMEOUT请求处理超时, AUTH/UNAUTHORIZED权限验证失败, IO/UNAVAILABLE外部服务不可用
└── C-2.2.4: 分析生成特定错误码 - ANALYSIS/DATA_INCOMPLETE分析所需数据不完整或缺失, ANALYSIS/LLM_CALL_FAILED LLM分析调用失败或超时, ANALYSIS/REPORT_GENERATION_ERROR分析报告生成异常, ANALYSIS/VALIDATION_ERROR分析结果验证失败, ANALYSIS/DATA_INTEGRATION_FAILED多数据源整合失败, ANALYSIS/TEMPLATE_LOADING_ERROR分析模板加载失败
```

------------------------------

### C-3: 配置依赖清单
```
C-3.1: 必需配置项 - 通过await routing_agent.get_config("final_analysis_output_agent", config_type)获取
├── C-3.1.1: 基础配置 - basic_config基础配置, timeout_config超时配置, retry_config重试配置
├── C-3.1.2: 业务配置 - llm_prompts LLM提示配置, report_templates报告模板配置, analysis_config分析配置, output_formats输出格式配置
└── C-3.1.3: 配置结构 - 包含综合报告结构定义(comprehensive_report_structure)、职业推荐标准(career_recommendation_criteria)、分析置信度阈值(analysis_confidence_thresholds)等核心分析参数

C-3.2: 依赖模块清单
├── C-3.2.1: 必须依赖 - routing_agent统一调度和配置管理, global_schemas数据模型定义, llm_handler_agent LLM分析报告生成服务, database_agent分析数据获取和存储服务
└── C-3.2.2: 可选依赖 - mail_agent分析报告邮件发送服务
```

------------------------------

### C-4: 数据模型规范
```
C-4.1: 必须使用的Schema - 从global_schemas导入的标准模型
├── C-4.1.1: 基础模型 - AgentRequest请求载荷模型, AgentResponse响应载荷模型
├── C-4.1.2: 业务模型 - FinalReport最终分析报告模型, AnalysisReport分析报告模型, CareerRecommendation职业推荐模型
└── C-4.1.3: 输入输出模型 - InputReports输入报告模型, FinalReportStructure输出报告模型

C-4.2: 输入报告模型结构
InputReports(BaseModel):
├── talent_test_report: Dict[str, Any] 才能测试报告(必填)
├── mbti_reverse_test_report: Dict[str, Any] MBTI逆向测试报告(必填)
└── resume_analysis_report: Optional[Dict[str, Any]] 简历分析报告(可选)

C-4.3: 输出报告模型结构
FinalReportStructure(BaseModel):
├── suitable_career_directions: List[CareerDirection] 适合的职业方向列表
├── positions_to_consider_carefully: List[PositionToConsider] 需要慎重考虑的职位列表
├── overall_career_development_advice: List[str] 整体职业发展建议列表
└── report_summary: str 报告摘要
```

------------------------------

## D: 用户流程、对话流程、意图识别机制

### D-1: 双阶段触发流程
```
D-1.1: 触发点1 - NINETEST完成后自动触发(MBTI已完成)
严格5步流程: MBTI完成 → NINETEST开始并完成 → entry_agent检测完成状态 → 自动触发final_analysis_output_agent
↓ 自动收集: MBTI结果 + NINETEST分析数据
↓ 调用LLM: 第一阶段职业画像分析
↓ 返回JSON: 分析文本返回给前端显示
↓ 存储: database_agent → 用户第一轮分析数据

D-1.2: 触发点2 - 简历补足完成后自动触发
用户完成简历上传+信息补足 → entry_agent检测完成状态 → 自动触发final_analysis_output_agent
↓ 自动收集: 简历分析数据 + 第一轮分析数据 + 补足信息
↓ 调用LLM: 第二阶段综合分析
↓ 返回JSON: 分析文本返回给前端显示
↓ 存储: database_agent → 用户最终综合分析数据
```

------------------------------

### D-2: 完整分析链路
```
D-2.1: 联动触发数据验证与提取
├── D-2.1.1: 触发请求接收 - 接收TriggerEvent格式的自动触发请求，包含触发类型和用户状态
├── D-2.1.2: 数据自动提取 - 根据触发阶段自动从database_agent提取对应的分析数据
├── D-2.1.3: 阶段1验证 - talent_test_report + mbti_reverse_test_report
└── D-2.1.4: 阶段2验证 - 第一轮报告 + resume_analysis_report + 补足信息

D-2.2: 报告数据结构化验证
├── D-2.2.1: 模型验证 - 使用InputReports Pydantic模型验证输入数据
├── D-2.2.2: 字段检查 - 检查必需报告字段不为空，确保分析数据基础
└── D-2.2.3: 错误处理 - 提供详细的验证错误信息便于问题定位

D-2.3: LLM提示词构建
├── D-2.3.1: 模板获取 - 通过routing_agent从global_config获取系统提示和用户提示模板
├── D-2.3.2: 数据序列化 - 将多个报告数据序列化为结构化的JSON格式文本
└── D-2.3.3: 提示构建 - 动态插入报告内容到提示模板中，形成完整的LLM输入

D-2.4: LLM分析调用
├── D-2.4.1: 服务调用 - 通过routing_agent分发到llm_handler_agent
├── D-2.4.2: 参数设置 - 使用严格的JSON模式确保结构化输出
└── D-2.4.3: 一致性保证 - 低温度参数（0.1）确保分析结果的一致性

D-2.5: 响应解析与验证
├── D-2.5.1: JSON解析 - 解析LLM返回的JSON格式分析报告
├── D-2.5.2: 结构验证 - 可选使用FinalReportStructure模型进行结构验证
└── D-2.5.3: 内容检查 - 确保返回的报告包含必需的职业方向建议和发展建议

D-2.6: 标准化响应构建
├── D-2.6.1: 响应格式 - 使用ResponseRules创建标准化的成功响应格式
├── D-2.6.2: 元数据包含 - 包含完整的最终分析报告、请求ID、代理名称等元数据
└── D-2.6.3: 错误处理 - 提供统一的错误处理和异常响应格式

D-2.7: 多层异常处理
├── D-2.7.1: 分层处理 - 分层处理不同类型异常：输入验证、LLM调用、任务执行
├── D-2.7.2: 上下文提供 - 提供详细的错误上下文和诊断信息
└── D-2.7.3: 优雅处理 - 确保所有异常都能被优雅处理并返回标准化错误响应
```

------------------------------

### D-3: 术语与名词表
```
D-3.1: 核心概念的唯一叫法与定义
├── D-3.1.1: final_analysis_output_agent - 用户画像分析总结服务的唯一名称，负责整合多个测试结果生成职业分析文本
├── D-3.1.2: 第一阶段分析 - 用户完成MBTI→NINETEST测试后的基础职业画像分析
├── D-3.1.3: 第二阶段分析 - 用户完成简历上传和信息补足后的最终综合分析
├── D-3.1.4: 双阶段分析 - 渐进式的分析机制，从基础画像到综合分析的两阶段过程
├── D-3.1.5: LLM分析 - 通过大语言模型进行职业分析报告生成的统一术语
├── D-3.1.6: 事件驱动触发 - 基于上游模块完成事件自动触发分析流程的机制
└── D-3.1.7: 用户画像分析总结服务 - 模块的核心职责描述，负责多数据源整合和分析输出
```

------------------------------

## E: 接口结构、状态管理、日志与异常策略

### E-1: 核心接口定义
```
E-1.1: 主接口run()方法
├── E-1.1.1: 接口签名 - Name: run(request: AgentRequest) -> AgentResponse, Method: 异步函数调用
├── E-1.1.2: 调用路径 - Path/Topic: 通过routing_agent调用，分析报告生成任务
├── E-1.1.3: 最小请求格式 - request_id: uuid-string, task_type: analysis_generation, user_id: user_id, context包含data操作信息
├── E-1.1.4: 最小响应格式 - success: true|false, response包含results分析结果, error包含错误码和消息
└── E-1.1.5: 错误码定义 - ANALYSIS/DATA_INCOMPLETE数据不足, ANALYSIS/LLM_CALL_FAILED LLM调用失败, ANALYSIS/REPORT_GENERATION_ERROR报告生成失败

E-1.2: 双阶段分析触发机制
├── E-1.2.1: 事件驱动触发 - 监听ninetest_agent和resume_agent的完成事件，自动触发分析流程
├── E-1.2.2: 双阶段渐进式分析 - 第一阶段基础画像 → 第二阶段综合分析的渐进式分析
├── E-1.2.3: JSON格式输出 - 每次分析完成后返回JSON格式的分析文本给前端和数据库
└── E-1.2.4: 状态感知处理 - 根据用户当前完成阶段，选择对应的分析模板和数据源
```

------------------------------

### E-2: 状态管理机制
```
⚠️ 未定义 - 具体的状态管理实现机制和状态存储策略需要进一步明确
```

------------------------------

### E-3: 日志记录规范
```
E-3.1: 日志框架与字段
├── E-3.1.1: 日志框架 - 使用Python标准logging模块
├── E-3.1.2: 必要字段 - request_id, agent_name, user_id, report_type, data_sources, confidence_level
├── E-3.1.3: 结构化格式 - JSON格式，包含综合分析上下文信息
└── E-3.1.4: 输出约束 - 禁止使用print()进行任何输出

E-3.2: 必填日志字段
├── E-3.2.1: 通用字段 - request_id请求标识, module_name模块名称, operation操作类型, duration_ms处理时长, success成功状态, retry_count重试次数
└── E-3.2.2: 敏感信息处理 - 日志/错误信息不得包含密钥、令牌、身份证件、邮箱全量、手机号全量等；必要时脱敏
```

------------------------------

### E-4: 异常处理策略
```
E-4.1: 异常类型定义
├── E-4.1.1: 业务异常 - ReportGenerationError报告生成错误, DataIntegrationError数据整合错误, AnalysisValidationError分析验证错误
├── E-4.1.2: 系统异常 - ValidationError输入验证失败, ConfigurationError配置获取失败, ProcessingError业务处理异常
└── E-4.1.3: 异常传播 - 只允许抛出仓库标准异常基类及其子类；不得抛裸异常；错误信息需面向调用方而非实现细节

E-4.2: 异常处理机制
├── E-4.2.1: 向上传播 - 异常向routing_agent传播，提供详细的错误上下文
├── E-4.2.2: 用户友好 - 对用户屏蔽详细错误，保留完整日志记录
├── E-4.2.3: 失败回退 - 失败时必须返回可操作指令（如flow指令/重试建议/联系渠道），不得要求调用方自行猜测
└── E-4.2.4: 异常处理机制 - ReportGenerationError包含报告类型和错误详情，通过try-catch捕获分析生成异常，记录error_type、user_id、report_type等上下文信息后向routing_agent传播
```

------------------------------

### E-5: 性能指标规范
```
E-5.1: 必须暴露的指标
├── E-5.1.1: 基础指标 - 调用次数: final_analysis_output_agent_requests_total, 成功率: final_analysis_output_agent_success_rate, 时延分布: final_analysis_output_agent_duration_seconds
├── E-5.1.2: 业务指标 - 报告生成成功率: final_report_generation_success_rate, LLM调用成功率: final_llm_call_success_rate, 分析完整性: final_analysis_completeness_rate
└── E-5.1.3: 指标要求 - 至少暴露调用次数、成功率、时延分布三类指标，指标名在README固化，禁止私改
```

------------------------------

## F: UI组件结构、事件响应、错误处理机制

### F-1: UI组件结构
```
⚠️ 未定义 - final_analysis_output_agent作为后端分析服务，不直接涉及UI组件结构，主要通过JSON格式向前端提供分析结果
```

------------------------------

### F-2: 事件响应机制
```
F-2.1: 自动触发事件响应
├── F-2.1.1: 触发事件类型 - ninetest_completion事件触发第一阶段分析, resume_completion事件触发第二阶段分析
├── F-2.1.2: 事件监听机制 - 通过entry_agent检测完成状态，自动触发final_analysis_output_agent
├── F-2.1.3: 响应处理流程 - 事件接收 → 数据收集 → LLM调用 → JSON返回 → 数据存储
└── F-2.1.4: 统一入口接口 - 暴露async def run(request: AgentRequest)和async def auto_trigger(trigger_event: TriggerEvent)接口

F-2.2: 模块协作事件
├── F-2.2.1: 事件驱动调用 - 通过事件驱动机制自动触发，监听ninetest_agent和resume_agent的完成事件
├── F-2.2.2: 双触发点设计 - 触发点1: ninetest完成 → entry_agent通知 → 自动触发第一阶段分析; 触发点2: 简历补足完成 → entry_agent通知 → 自动触发第二阶段分析
├── F-2.2.3: 状态感知处理 - 根据用户当前完成阶段，选择分析模板和数据源
└── F-2.2.4: 数据协作 - 与database_agent协作存储分析文本、与上游Agent获取分析数据
```

------------------------------

### F-3: 前端交互机制
```
F-3.1: JSON数据传输
├── F-3.1.1: 输出数据结构 - 每次分析完成后返回JSON格式的分析文本给前端显示和数据库存储
├── F-3.1.2: 第一阶段JSON输出格式 - 包含user_id, analysis_reports.first_report(report_id, generation_date, report_type, content, key_strengths, recommended_careers, positions_to_avoid, overall_advice), metadata(analysis_type, data_sources, confidence_level, processing_time)
├── F-3.1.3: 第二阶段JSON输出格式 - 包含user_id, analysis_reports.comprehensive_report(report_id, generation_date, report_type, content, growth_environment_analysis, psychological_profile, development_suggestions, risk_warnings, breakthrough_strategies), metadata
└── F-3.1.4: 数据校验规则 - report_id必须唯一格式为"report_" + 3位序号, generation_date必须为ISO8601格式UTC时间, content完整报告文本支持markdown格式, key_strengths数组至少包含3个核心优势描述, recommended_careers数组至少包含3个推荐职业方向, positions_to_avoid数组至少包含2个需要谨慎的职位类型, confidence_level浮点数范围0.0-1.0表示分析可信度
```

------------------------------

## G: WebSocket / LLM / 上传机制等集成接口

### G-1: LLM集成接口
```
G-1.1: LLM调用规范
├── G-1.1.1: 核心用途 - 综合分析报告生成、职业建议生成、个性化推荐
├── G-1.1.2: 调用方式 - 通过await routing_agent.call_agent("llm_handler_agent", payload)调用
├── G-1.1.3: 访问约束 - 严禁直接访问OpenAI、Claude、Gemini等API
├── G-1.1.4: 模型要求 - 强制使用gpt-4o-2024-08-06模型
└── G-1.1.5: 参数设置 - 使用temperature=0.1确保分析一致性

G-1.2: LLM调用机制
├── G-1.2.1: 配置获取 - 从global_config获取综合分析提示模板
├── G-1.2.2: 载荷构造 - 构造包含system_prompt和user_prompt的llm_payload
├── G-1.2.3: 模式设置 - 使用json_mode和低温度参数(0.1)确保一致性
└── G-1.2.4: 服务调用 - 通过routing_agent调用llm_handler_agent生成结构化分析报告

G-1.3: LLM配置管理
├── G-1.3.1: 参数配置 - temperature: 0.1, json_mode: true, max_tokens: 4000, timeout: 30
├── G-1.3.2: 提示模板管理 - final_analysis_report_generation包含system_prompt高级职业规划师和生涯教练角色定义, user_prompt用户指令模板包含报告占位符
└── G-1.3.3: 报告类型配置 - required必需报告: talent_test_report, mbti_reverse_test_report; optional可选报告: resume_analysis_report
```

------------------------------

### G-2: WebSocket机制
```
⚠️ 未定义 - 文档中未明确定义WebSocket相关的集成接口和通信机制
```

------------------------------

### G-3: 上传机制
```
⚠️ 未定义 - final_analysis_output_agent主要处理分析结果输出，不直接涉及文件上传机制，上传功能由其他模块负责
```

------------------------------

### G-4: 外部服务集成
```
G-4.1: 依赖服务集成
├── G-4.1.1: routing_agent集成 - 统一调度和配置管理服务
├── G-4.1.2: database_agent集成 - 分析数据获取和存储服务
├── G-4.1.3: llm_handler_agent集成 - LLM分析报告生成服务
└── G-4.1.4: mail_agent集成 - 分析报告邮件发送服务(可选)

G-4.2: 服务通信协议
├── G-4.2.1: 统一通信格式 - 使用AgentRequest和AgentResponse扁平化字段传输格式
├── G-4.2.2: 异步调用模式 - 所有服务调用使用async/await模式
└── G-4.2.3: 错误传播机制 - 标准化错误码和异常处理流程
```

------------------------------

## H: 环境配置、运行要求、版本依赖、模块限制

### H-1: Python环境规范
```
H-1.1: 版本要求
├── H-1.1.1: Python版本 - Python 3.10+（强制要求）
├── H-1.1.2: 运行环境 - 支持asyncio异步并发处理
└── H-1.1.3: 资源要求 - 内存640MB+，CPU 1核+

H-1.2: 核心依赖
├── H-1.2.1: 基础库依赖 - 仅需基础Python库: pydantic, asyncio, logging, json
├── H-1.2.2: 无需额外库 - 不需要PDF生成库、邮件发送库、文档处理库等
└── H-1.2.3: 依赖说明 - 核心依赖: pydantic>=2.0.0(数据验证), json(报告解析), asyncio(异步处理); Agent依赖: routing_agent(调度中心), llm_handler_agent(LLM分析), database_agent(数据获取), mail_agent(报告发送); 外部服务: OpenAI API(通过llm_handler), PDF生成服务; 运行环境: Python 3.10+, 640MB+内存（大报告生成）
```

------------------------------

### H-2: Pydantic V2规范
```
H-2.1: 必须使用的方法
├── H-2.1.1: 推荐方法 - model_validate(), model_dump(), Field(), BaseModel
├── H-2.1.2: 严禁使用 - .dict(), .parse_obj(), .json(), parse_obj_as()
├── H-2.1.3: 字段验证 - 必须使用pattern=r"regex"，严禁使用regex=r"regex"
└── H-2.1.4: 模型导入 - 统一从global_schemas导入，禁止本地重复定义

H-2.2: 模型验证示例
from global_schemas import FinalReport, AnalysisReport, CareerRecommendation
final_report = FinalReport.model_validate(raw_data)
analysis_report = AnalysisReport.model_validate(report_data)  
response_dict = final_report.model_dump()
```

------------------------------

### H-3: 异步处理规范
```
H-3.1: 异步要求
├── H-3.1.1: 必须使用 - 所有报告生成和分析方法使用async def
├── H-3.1.2: 禁止使用 - 同步阻塞操作、threading、multiprocessing
└── H-3.1.3: 并发处理 - 使用asyncio.create_task(), asyncio.gather()处理并发分析任务

H-3.2: 实现示例
async def generate_comprehensive_analysis(self, reports: Dict) -> Dict:
    analysis_tasks = [
        asyncio.create_task(self.analyze_mbti_data(reports["mbti_report"])),
        asyncio.create_task(self.analyze_talent_data(reports["talent_report"])),
        asyncio.create_task(self.generate_career_recommendations(combined_data))
    ]
    mbti_analysis, talent_analysis, career_rec = await asyncio.gather(*analysis_tasks)
    return self.merge_final_report(mbti_analysis, talent_analysis, career_rec)
```

------------------------------

### H-4: 配置管理规范
```
H-4.1: 配置获取方式
├── H-4.1.1: 获取方法 - 通过await routing_agent.get_config("final_analysis_output_agent", config_type)
├── H-4.1.2: 配置类型 - llm_prompts, report_templates, analysis_config, output_formats
├── H-4.1.3: 严禁操作 - 硬编码配置、本地配置文件、环境变量直接读取
└── H-4.1.4: 热更新支持 - 支持配置实时更新，无需重启服务

H-4.2: 配置唯一来源
├── H-4.2.1: 来源约束 - 配置仅可经由routing_agent的config_manager服务读取
├── H-4.2.2: 热更新与回滚 - 配置键名/层级不可私改；新增键必须提供默认值、回滚策略；未在routing_agent的config_manager服务注册的键不得使用
└── H-4.2.3: 配置结构 - 包含综合报告结构定义(comprehensive_report_structure)、职业推荐标准(career_recommendation_criteria)、分析置信度阈值(analysis_confidence_thresholds)等核心分析参数
```

------------------------------

### H-5: 模块限制约束
```
H-5.1: 契约与模型来源
├── H-5.1.1: 模型唯一来源 - 所有数据模型/Schema一律从global_schemas引入；禁止在模块内新增/复制业务模型或DTO
├── H-5.1.2: 接口契约 - 本模块README必须提供最小可执行契约（接口签名或伪码），仅声明入参/出参/错误码；不提供实现样例
└── H-5.1.3: 版本与兼容 - 任何新增/变更字段必须在README标注语义、默认值、兼容策略，并同步更新global_schemas对应版本

H-5.2: 外部I/O与状态
├── H-5.2.1: 状态存取 - 模块不得直接访问持久化（DB/Cache/FS）；必须通过指定Adapter间接访问database_agent统一管理的存储层
├── H-5.2.2: 副作用隔离 - 任何网络/系统I/O仅可写在Adapter；Main/Aux出现I/O视为违规
└── H-5.2.3: 可重复执行 - 生成的任意函数需满足幂等/可重放要求（同输入不应产生额外副作用）

H-5.3: 并发与资源
├── H-5.3.1: 并发原语 - 仅允许使用语言原生异步原语（如async/await、事件循环）；禁止线程池/进程池，除非在Adapter层且README明示风险与回收策略
└── H-5.3.2: 超时与重试 - 必须经routing_agent的config_manager服务注入；禁止在代码内写死超时/重试参数

H-5.4: 安全与合规
├── H-5.4.1: 秘钥管理 - 不得在代码/README/示例中出现任何真实秘钥；仅允许读取环境变量或安全管理器的别名
├── H-5.4.2: 输入校验 - 所有外部输入必须显式校验（长度/类型/枚举/格式），校验规则写入README的契约章节
└── H-5.4.3: 权限与最小化 - 模块内不得提升权限；仅请求所需最小范围的权限与数据字段
```

------------------------------

## I: 测试策略、验收机制、部署策略、未来规划

### I-1: 测试策略规范
```
I-1.1: 测试规范约束
├── I-1.1.1: 最小用例 - 本模块至少提供冒烟链路与失败路径两类用例；用例不得Mock掉对外契约（可Mock外设）
├── I-1.1.2: 验收门槛 - 生成变更必须先通过本模块用例再提交；未达门槛禁止继续生成下一文件
└── I-1.1.3: 测试迁移 - 功能测试逻辑已迁移至utility_tools/global_test/进行独立管理

I-1.2: 测试覆盖范围
├── I-1.2.1: 联动触发测试 - 测试双阶段自动触发机制的准确性和时序性
├── I-1.2.2: 渐进式分析测试 - 验证第一阶段→第二阶段报告的连贯性和增量价值
├── I-1.2.3: 前端推送测试 - 验证报告生成后自动推送到前端的完整性
└── I-1.2.4: 生产级测试 - 使用真实的多Agent报告数据进行综合分析验证

I-1.3: 具体测试类型
├── I-1.3.1: 第一阶段触发测试 - 验证ninetest_completed触发事件处理，包含TriggerEvent构造、auto_trigger方法调用、first_report生成和frontend_pushed状态检查
├── I-1.3.2: 第二阶段触发测试 - 验证resume_completed触发事件处理，包含第二阶段数据整合、second_report生成和渐进式增强验证
└── I-1.3.3: 渐进式分析连贯性测试 - 验证第一阶段到第二阶段报告的连贯性，确保第二阶段包含并优化第一阶段的建议内容
```

------------------------------

### I-2: 验收机制
```
⚠️ 未定义 - 具体的验收标准和验收流程需要进一步明确定义
```

------------------------------

### I-3: 部署策略规范
```
I-3.1: 环境要求
├── I-3.1.1: 基础环境 - Python 3.10+，内存640MB+，CPU 1核+
├── I-3.1.2: 依赖服务 - routing_agent, llm_handler_agent, database_agent, global_config
└── I-3.1.3: 启动命令 - 最小启动命令: python main.py --start

I-3.2: 监控指标
├── I-3.2.1: 性能指标 - 报告生成成功率 > 98%，响应时间 < 15秒，分析完整性 > 95%，用户满意度 > 90%
└── I-3.2.2: 健康检查 - LLM服务连通性验证、报告模板加载检查、数据整合能力验证

I-3.3: 快速启动指南
├── I-3.3.1: Prerequisites - Python 3.10+, PDF生成库依赖, 邮件服务配置, MBTI、ninetest_agent数据源就绪
├── I-3.3.2: Install & Configure - 安装依赖（已包含在全局requirements.txt）pip install reportlab>=4.0.0 jinja2>=3.1.0; 分析报告配置示例ANALYSIS_CONFIG包含first_report_trigger, second_report_trigger, pdf_template
└── I-3.3.3: Run & Smoke Test - 第一次分析报告生成测试，使用AgentRequest格式调用run方法，检查返回状态为REPORT_GENERATED
```

------------------------------

### I-4: 故障排查指南
```
I-4.1: 常见问题解决
├── I-4.1.1: 触发事件缺失 - 确认用户已完成MBTI和九型测试
├── I-4.1.2: PDF生成失败 - 检查reportlab库版本和模板文件
├── I-4.1.3: 邮件发送失败 - 确认mail_agent配置和网络连接
├── I-4.1.4: 报告生成失败 - 检查用户数据完整性和LLM服务状态
├── I-4.1.5: PDF生成异常 - 确认PDF生成服务连接和模板文件
└── I-4.1.6: 数据验证错误 - 检查输入报告数据格式和必需字段

I-4.2: 快速诊断命令
# 检查分析服务状态
curl http://localhost:8000/agents/final_analysis_output_agent/health
# 检查最近的分析日志  
tail -f logs/final_analysis.log | grep "ANALYSIS_"
# 验证用户数据完整性
python -c "from database_agent import get_user_analysis_data; print(get_user_analysis_data('user_id'))"
```

------------------------------

### I-5: 未来规划
```
⚠️ 未定义 - 文档中未明确定义模块的未来发展规划和扩展计划
```

------------------------------

## J: 未定义项、待补要点、黑名单、禁用规则等

### J-1: 生成器执行规范
```
J-1.1: AI行为红线
├── J-1.1.1: 部分修改优先 - 每次仅修改一个文件，≤300行；若需要新增文件，先在README标注"文件名 + 角色(Main/Adapter/Aux) + 责任"，再生成
├── J-1.1.2: 禁止脑补 - 遇到缺失信息（路径/键名/Schema字段/错误码），停止输出并在README的"待补要点"清单中列明，不得擅自发明
├── J-1.1.3: 依赖单向 - Domain → Adapter单向依赖；Aux不得被跨模块引用。生成器如果检测到反向引用，直接终止
├── J-1.1.4: 不迁移/不重命名/不删除 - 除非README的"迁移方案"明确列出变更映射
└── J-1.1.5: 不新增公共层 - 任何"utils/common/shared"目录新增一律拒绝；确有必要需先在顶层规范中建制并评审

J-1.2: 待补要点机制
├── J-1.2.1: 必要说明 - 遇到字段未定义、路径不明、错误码缺失、指标未命名等情况，生成器不得继续实现，必须在README的"待补要点"清单中列出
├── J-1.2.2: 清单内容 - 待补键名/字段（含建议默认值/取值域）, 影响面（调用方、下游模块、运行时风险）, 最小决策集（给出2～3个可选项，偏保守）
└── J-1.2.3: 重要提醒 - 上述待补要点未明确前，AI代码生成器应该停止实现相关功能，等待明确指令后再继续。禁止基于假设或经验进行"脑补"
```

------------------------------

### J-2: 关键词黑名单
```
J-2.1: 检测红线
├── J-2.1.1: 禁止本地业务模型定义 - "class .*Model", "data class .*", "interface .*DTO"
├── J-2.1.2: 禁止硬编码配置 - "API_KEY=", "timeout\\s*=\\s*\\d+", "retry\\s*=\\s*\\d+"
├── J-2.1.3: 禁止跨层I/O - 在Main/Aux中出现"http", "db", "sql", "open(", "requests", "fetch"
├── J-2.1.4: 禁止并发越界 - "Thread", "Process", "fork", "Pool"
└── J-2.1.5: 禁止未脱敏日志 - "print(", "console.log(", "logging.info(f\\".*password|token|secret"
```

------------------------------

### J-3: 配置参数待补
```
J-3.1: 缺失的配置键名
├── J-3.1.1: 置信度阈值配置
│   ├── 配置键名: final_analysis_output_agent.analysis_config.confidence_thresholds
│   ├── 建议默认值: {"minimum": 0.7, "good": 0.85, "excellent": 0.95}
│   ├── 取值域: 浮点数[0.0, 1.0]
│   ├── 影响面: 分析报告可信度评估和质量控制
│   └── 最小决策集: 选项1: 三级阈值（最低、良好、优秀）; 选项2: 二级阈值（合格、优秀）

├── J-3.1.2: 触发事件映射配置
│   ├── 配置键名: final_analysis_output_agent.report_templates.trigger_event_mappings
│   ├── 建议默认值: {"ninetest_completed": "first_analysis", "resume_completed": "comprehensive_analysis"}
│   ├── 影响面: 自动触发机制的事件到报告类型映射
│   └── 最小决策集: 选项1: 固定映射关系（简化处理）; 选项2: 可配置映射关系（灵活适应）

└── J-3.1.3: LLM提示配置
    ├── 配置键名: final_analysis_output_agent.llm_prompts.analysis_generation_prompts
    ├── 建议默认值: 结构化的双阶段分析提示模板
    ├── 影响面: LLM生成分析报告的质量和一致性
    └── 最小决策集: 选项1: 专业职业规划风格（权威性高）; 选项2: 用户友好对话风格（可读性强）
```

------------------------------

### J-4: Schema字段待补
```
J-4.1: global_schemas中缺失的字段定义
├── J-4.1.1: FinalReport模型缺失字段
│   ├── 缺失字段: trigger_event
│   ├── 建议类型: str
│   ├── 影响面: 报告生成触发事件的记录和追踪
│   └── 最小决策集: 选项1: 枚举类型（类型安全）; 选项2: 字符串类型（灵活性高）

├── J-4.1.2: AnalysisReport模型缺失字段
│   ├── 缺失字段: data_sources
│   ├── 建议类型: List[str]
│   ├── 影响面: 分析数据来源的透明度和可追溯性
│   └── 最小决策集: 选项1: 详细数据源列表（完整追踪）; 选项2: 简化数据源标识（降低复杂度）

└── J-4.1.3: CareerRecommendation模型缺失字段
    ├── 缺失字段: positions_to_avoid
    ├── 建议类型: List[Dict[str, str]]
    ├── 影响面: 职业风险提示和谨慎建议的存储
    └── 最小决策集: 选项1: 结构化字典格式（支持详细说明）; 选项2: 简单字符串列表（简化处理）
```

------------------------------

### J-5: 路径映射待补
```
J-5.1: 未明确的文件路径
├── 路径用途: 分析报告模板文件存储
├── 待确认路径: {MODULE_ROOT}/templates/ vs 完全依赖routing_agent配置
├── 影响面: 报告生成模板的管理和版本控制
└── 最小决策集: 选项1: 完全依赖routing_agent（架构一致性）; 选项2: 本地模板备份（可用性保障）
```

------------------------------

### J-6: 错误码待补
```
J-6.1: 模块特定错误码
├── J-6.1.1: 数据冲突处理错误
│   ├── 错误场景: 数据整合过程中的数据冲突处理
│   ├── 建议错误码: ANALYSIS/DATA_CONFLICT_DETECTED
│   ├── 错误消息模板: "分析数据冲突: {conflict_details}"
│   ├── 影响面: 多数据源整合的准确性和可靠性
│   └── 最小决策集: 选项1: 详细冲突信息（便于调试）; 选项2: 简化冲突提示（用户友好）

└── J-6.1.2: 分析质量不达标错误
    ├── 错误场景: 分析报告质量不达标
    ├── 建议错误码: ANALYSIS/QUALITY_INSUFFICIENT
    ├── 错误消息模板: "分析报告质量不达标: confidence={confidence}"
    ├── 影响面: 分析输出的质量控制和用户体验
    └── 最小决策集: 选项1: 严格质量控制（确保准确性）; 选项2: 宽松质量标准（提升可用性）
```

------------------------------

### J-7: 指标名称待补
```
J-7.1: 性能监控指标
├── 指标用途: 分析报告触发成功率监控
├── 建议指标名: final_analysis_trigger_success_rate
├── 指标类型: Gauge
├── 标签维度: trigger_event, analysis_type, success_status
├── 影响面: 自动触发机制的监控和优化
└── 最小决策集: 选项1: 事件级别监控（精细化分析）; 选项2: 整体触发监控（简化指标）
```

------------------------------

### J-8: 依赖关系待补
```
J-8.1: 模块间协作关系
├── 协作场景: 与entry_agent的触发事件协作
├── 目标模块: entry_agent
├── 交互方式: 事件驱动触发机制
├── 数据传递格式: TriggerEvent标准格式
├── 影响面: 自动分析流程的时序控制和可靠性
└── 最小决策集: 选项1: 实时触发机制（即时响应）; 选项2: 定时触发检查（降低复杂度）
```

------------------------------

### J-9: 业务规则待补
```
J-9.1: 业务逻辑决策点
├── J-9.1.1: 分析数据不完整处理策略
│   ├── 业务场景: 分析数据不完整时的处理策略
│   ├── 决策点: 部分数据缺失时是否生成基础分析报告
│   ├── 影响面: 用户体验和分析报告的完整性平衡
│   └── 最小决策集: 选项1: 严格要求完整数据（确保质量）; 选项2: 允许部分分析并标记（用户友好）; 选项3: 智能补全缺失数据（算法辅助）

└── J-9.1.2: 阶段分析衔接策略
    ├── 业务场景: 第一阶段到第二阶段分析的衔接策略
    ├── 决策点: 第二阶段分析如何整合和优化第一阶段结果
    ├── 影响面: 分析报告的连贯性和增值性
    └── 最小决策集: 选项1: 完全重新生成（确保一致性）; 选项2: 增量优化更新（保持连贯性）; 选项3: 并行对比分析（提供多角度）
```

------------------------------

## K: 模块契约总结

### K-1: 核心职责定义
```
final_analysis_output_agent作为Career Bot系统的用户画像分析总结服务：
├── 核心职责: 数据整合、LLM分析调用、个性化建议生成、JSON格式输出
├── 运行模式: 被动调用，无状态设计，事件驱动，双阶段分析
├── 处理能力: 多数据源整合，结构化验证，职业方向推荐，发展建议生成
├── AI集成: 通过routing_agent调用LLM，JSON格式输出，低温度一致性
├── 架构特性: 配置驱动系统，异步处理，异常分层处理，轻量级设计
└── 严格约束: 无Mock机制，真实分析，仅基础依赖，异步并发处理
```

------------------------------

### K-2: 关键价值实现
```
K-2.1: 价值实现 - 将多维度测试数据转化为用户易懂、可操作的分析文本
K-2.2: 个性化服务 - 基于用户完整画像提供定制化的职业发展建议
K-2.3: 轻量设计 - 简洁高效的JSON文本输出，无需额外文件生成
K-2.4: 用户体验 - 作为系统的分析核心，提供有价值的职业发展指导
```

------------------------------

### K-3: 技术规范遵循
```
K-3.1: 核心约束
├── K-3.1.1: Pydantic V2 - 使用model_validate()和model_dump()，禁用V1方法
├── K-3.1.2: 字段验证 - 使用pattern替代regex
├── K-3.1.3: 异步处理 - 所有LLM调用使用async/await模式
├── K-3.1.4: 配置驱动 - 所有提示模板和参数通过routing_agent从global_config获取
└── K-3.1.5: 数据格式 - 输入输出严格遵循AgentRequest和AgentResponse

K-3.2: 架构约束
├── K-3.2.1: 被动调用 - 模块不主动运行，仅响应中枢调度
├── K-3.2.2: 无状态设计 - 完全无状态，支持并发处理多个分析请求
├── K-3.2.3: 中枢调度 - 与其他模块的交互统一通过routing_agent
└── K-3.2.4: 统一入口 - 仅暴露run()方法作为唯一接口

K-3.3: 特殊约束
├── K-3.3.1: 综合分析职责 - 承担系统最终分析报告生成核心职责
├── K-3.3.2: LLM调用约束 - 报告生成必须通过llm_handler_agent调用
├── K-3.3.3: JSON格式强制 - LLM输出必须为有效JSON格式
├── K-3.3.4: 质量控制 - 严禁Fallback，确保分析结果真实性
└── K-3.3.5: 异常处理 - 分层异常处理，确保错误信息的准确性
```

------------------------------

### K-4: 系统定位总结
```
该模块是整个Career Bot系统的用户画像分析总结服务，确保用户能够获得有价值、可操作的职业发展指导，实现从数据收集到价值输出的完整闭环。
```