# company_identity_agent 结构化文档骨架

### A1: 开发边界与职责说明

```
A1代表company_identity_agent是Career Bot系统的企业身份验证处理中心，负责企业主体一致性验证和当年有效性检查。该模块支持SEC和DTI双注册类型，采用MVP简化验证策略，专注于文档间一致性验证，不进行线上/线下真伪核验。采用地址强一致性验证原则，地址不一致的申请一律拒绝，确保平台企业身份的真实性和可靠性。
```

------------------------------

### A2: 系统架构与模块定义

```
A2定义了company_identity_agent在Career Bot系统中的架构位置和模块边界。模块工作区严格限制在applications/company_identity_agent/内，禁止创建、移动、重命名、删除该目录之外的任何文件。主入口文件名与company_identity_agent同名，非主入口文件归类为Adapter或Aux。单次变更仅允许操作一个文件，超过300行自动截断。
```

------------------------------

### A3: 输入输出规范

```
├── A3.1: 统一接口规范
│   └── 模块统一入口方法为async def run(request: AgentRequest) -> AgentResponse，接收扁平化请求载荷，返回扁平化响应载荷。输入参数包含request_id、task_type、user_id、session_id、message、intent等直接字段，输出包含request_id、agent_name、success、timestamp、processing_status、results、error_details。
├── A3.2: 支持的任务类型
│   ├── A3.2.1: company_document_preliminary_check - 企业文档初步检查
│   ├── A3.2.2: company_holistic_verification - 企业全面合规验证
│   ├── A3.2.3: health_check - 健康检查
│   └── A3.2.4: get_config - 配置获取
├── A3.3: 数据模型规范
│   ├── A3.3.1: 必须使用Schema - 从global_schemas导入AgentRequest、AgentResponse、CompanyProfile、DocumentRecord、VerificationResult
│   └── A3.3.2: 模型验证机制 - 使用model_validate()验证输入数据，model_dump()序列化输出结果
```

------------------------------

### A4: 配置机制

```
├── A4.1: 配置唯一来源
│   └── 配置仅可经由routing_agent的config_manager服务读取，禁止本地硬编码可变配置。通过await routing_agent.get_config("company_identity_agent", config_type)获取配置。
├── A4.2: 必需配置项
│   ├── A4.2.1: basic_config - 基础配置
│   ├── A4.2.2: timeout_config - 超时配置
│   ├── A4.2.3: retry_config - 重试配置
│   ├── A4.2.4: verification_rules - 验证规则配置
│   ├── A4.2.5: document_templates - 文档模板配置
│   ├── A4.2.6: llm_prompts - LLM提示配置
│   └── A4.2.7: validation_config - 验证配置
├── A4.3: 热更新与回滚
│   └── 配置键名/层级不可私改，新增键必须提供默认值、回滚策略，未在routing_agent的config_manager服务注册的键不得使用
```

------------------------------

### A5: 模型路径

```
⚠️ 未定义 - 具体的模型文件路径需要在global_schemas中确认
```

------------------------------

### A6: 调用方式

```
├── A6.1: 被动调用模式
│   └── 仅响应routing_agent的企业验证任务分发，不主动运行。模块采用无状态设计，每次调用独立完成。
├── A6.2: LLM调用规范
│   └── 必须通过await routing_agent.call_agent("llm_handler_agent", payload)调用，严禁直接访问OpenAI、Claude、Gemini等API。强制使用gpt-4o-2024-08-06模型。
├── A6.3: 数据协作
│   └── 与database_agent协作存储企业档案，与mail_agent协作发送通知，与taggings_agent协作企业打标
```

------------------------------

### A7: 用户流程

```
├── A7.1: 企业文档上传流程
│   ├── A7.1.1: 用户上传文档 → entry_agent → routing_agent → company_identity_agent
│   ├── A7.1.2: 阶段一：初步检查 ← → llm_handler_agent
│   ├── A7.1.3: 阶段二：全面验证 ← → llm_handler_agent
│   └── A7.1.4: 验证结果 → database_agent/entry_agent
├── A7.2: SEC注册企业流程
│   ├── A7.2.1: 必需文档 - Latest GIS（当年）+ Business Permit（当年有效）+ SEC Certificate + Articles of Incorporation + BIR 2303
│   ├── A7.2.2: 一致性校验 - normalize_name公司名称一致性、normalize_regno注册号一致性、address_consistent地址强一致性
│   └── A7.2.3: 当年有效验证 - GIS必须为current_year、Permit必须覆盖当年且未过期
├── A7.3: DTI注册企业流程
│   ├── A7.3.1: 必需文档 - DTI BN Certificate（当年有效）+ Business Permit（当年有效）+ BIR 2303
│   ├── A7.3.2: 一致性校验 - normalize_name商业名称一致性、normalize_bnno编号一致性、address_consistent地址强一致性
│   └── A7.3.3: 业主名警告 - owner_name不一致仅OWNER_MISMATCH_WARN（不拦截），但地址不一致仍直接拒绝
```

------------------------------

### A8: 对话流程

```
├── A8.1: 验证成功对话反馈
│   └── 企业认证成功，显示企业名称、注册类型、注册号、验证时间，提供发布职位、搜索候选人、企业主控台等操作选项，包含年度更新提醒
├── A8.2: 验证失败统一处理对话反馈
│   └── 显示具体失败原因，提供统一解决方案要求重新上传正确企业文档，提供技术支持邮件联系方式和一键生成技术支持邮件功能
├── A8.3: 一键技术支持邮件模板功能
│   └── 自动收集问题信息生成技术支持邮件模板，包含问题类型、错误代码、发生时间、用户ID、企业名称、请求ID等详细信息
```

------------------------------

### A9: 意图识别机制

```
├── A9.1: 任务类型识别
│   ├── A9.1.1: company_document_preliminary_check - 初步文档检查
│   ├── A9.1.2: company_holistic_verification - 全面验证分析
│   ├── A9.1.3: health_check - 健康检查
│   └── A9.1.4: get_config - 配置获取
├── A9.2: 文档类型识别
│   ├── A9.2.1: 自动识别文件类型并转换为Base64编码
│   ├── A9.2.2: 支持直接文件传递或通过URL下载文档
│   └── A9.2.3: 文档完整性检查验证所有必需文档是否已上传
```

------------------------------

### A10: 接口结构

```
├── A10.1: 统一入口接口
│   └── async def run(request: AgentRequest) -> AgentResponse，严格遵循输入参数验证、配置获取和业务处理异常的错误处理机制
├── A10.2: 错误码规范
│   ├── A10.2.1: 通用错误码 - VALIDATION/INVALID_INPUT、CONFIG/NOT_FOUND、CONFIG/INVALID_FORMAT、TIMEOUT/REQUEST_TIMEOUT、AUTH/UNAUTHORIZED、IO/UNAVAILABLE
│   ├── A10.2.2: 企业验证特定错误码 - COMPANY/DOCUMENT_ERROR、COMPANY/CONSISTENCY_ERROR、COMPANY/VALIDITY_ERROR、COMPANY/EXTRACTION_ERROR、COMPANY/ADDRESS_MISMATCH、COMPANY/SYSTEM_ERROR
│   └── A10.2.3: 错误码格式 - 采用{DOMAIN}/{REASON}命名格式
├── A10.3: 依赖模块清单
│   ├── A10.3.1: 必须依赖 - routing_agent、global_schemas、llm_handler_agent、database_agent
│   └── A10.3.2: 可选依赖 - mail_agent企业认证邮件通知
```

------------------------------

### A11: 状态管理

```
├── A11.1: 无状态设计
│   └── 完全无状态设计，每次调用独立完成，不保存中间状态，支持并发处理多个验证请求，支持水平扩展
├── A11.2: 企业验证状态字段
│   ├── A11.2.1: 验证状态枚举 - PENDING等待验证处理、PROCESSING正在执行验证、VERIFIED验证通过、REJECTED验证失败、EXPIRED文档已过期需重新验证
│   └── A11.2.2: 验证结果字段 - verification_result验证结果详情、verification_timestamp验证完成时间戳、verification_errors验证失败错误列表、document_expiry_date文档到期时间
├── A11.3: 多公司管理字段
│   ├── A11.3.1: 企业关联字段 - user_companies用户关联企业列表、active_company_id当前选择的操作企业ID、company_verification_status各企业验证状态映射、company_document_sets企业文档集合存储
│   └── A11.3.2: 企业切换字段 - company_selection_context企业选择对话上下文、last_active_company上次选择的企业记录、company_switch_timestamp企业切换时间戳
```

------------------------------

### A12: 日志与异常策略

```
├── A12.1: 必填日志字段
│   └── request_id请求唯一标识符、module_name模块名称、operation操作类型、duration_ms处理耗时毫秒、success成功标志、retry_count重试次数
├── A12.2: 敏感信息处理
│   └── 日志/错误信息不得包含密钥、令牌、身份证件、邮箱全量、手机号全量等，必要时脱敏
├── A12.3: 日志记录规范
│   ├── A12.3.1: 使用Python标准logging模块
│   ├── A12.3.2: JSON格式结构化日志，包含文档处理上下文信息
│   └── A12.3.3: 禁止使用print()进行任何输出
├── A12.4: 异常处理规范
│   ├── A12.4.1: 异常类型 - DocumentValidationError、CompanyVerificationError、ConfigurationError
│   ├── A12.4.2: 向上传播 - 异常向routing_agent传播，提供详细的错误上下文
│   └── A12.4.3: 用户友好 - 对用户屏蔽详细错误，保留完整日志记录
```

------------------------------

### A13: UI组件结构

```
⚠️ 未定义 - company_identity_agent是后端处理模块，不涉及UI组件
```

------------------------------

### A14: 事件响应

```
├── A14.1: 上游触发事件
│   ├── A14.1.1: routing_agent - 唯一任务调度来源，提供企业认证任务分发和配置管理
│   ├── A14.1.2: auth_agent - 雇主身份激活后触发企业验证流程
│   ├── A14.1.3: frontend_service_agent - 用户上传企业文档后触发验证处理
│   └── A14.1.4: database_agent - 企业信息更新时触发重新验证和标签更新
├── A14.2: 下游调用事件
│   ├── A14.2.1: llm_handler_agent - AI文档解析、信息提取和一致性验证
│   ├── A14.2.2: database_agent - 企业验证状态存储、文档归档和多公司关系管理
│   ├── A14.2.3: taggings_agent - 企业文档上传完成后触发公司基础打标
│   └── A14.2.4: mail_agent - 验证成功/失败通知邮件发送
```

------------------------------

### A15: 错误处理机制

```
├── A15.1: C6_FALLBACKS统一错误分类
│   ├── A15.1.1: DOCUMENT_ERROR - 文档缺失、无法解析、格式不支持或损坏 → 统一要求重新上传
│   ├── A15.1.2: CONSISTENCY_ERROR - 企业名称、注册号、地址、税务信息不一致 → 统一要求重新上传
│   ├── A15.1.3: VALIDITY_ERROR - GIS非当年、Permit过期或不覆盖当年 → 统一要求重新上传
│   ├── A15.1.4: EXTRACTION_ERROR - LLM无法提取关键信息或文档内容异常 → 统一要求重新上传
│   └── A15.1.5: SYSTEM_ERROR - 网络错误、服务异常等技术问题 → 提供一键技术支持邮件
├── A15.2: 统一处理原则
│   ├── A15.2.1: 所有验证失败场景均要求重新上传，不提供特殊处理路径
│   ├── A15.2.2: 提供一键技术支持邮件模板生成功能：support@4waysgroup.com
│   └── A15.2.3: 失败反馈包含明确原因 + 重新上传指导 + 邮件支持选项
```

------------------------------

### A16: WebSocket集成接口

```
⚠️ 未定义 - company_identity_agent通过routing_agent进行异步调用，不直接使用WebSocket
```

------------------------------

### A17: LLM集成接口

```
├── A17.1: LLM调用规范
│   ├── A17.1.1: 唯一通道 - 必须通过await routing_agent.call_agent("llm_handler_agent", payload)
│   ├── A17.1.2: 严禁直接访问 - 禁止直接访问OpenAI、Claude、Gemini等API
│   ├── A17.1.3: 强制模型 - 使用gpt-4o-2024-08-06模型
│   └── A17.1.4: Prompt管理 - 通过global_config获取，禁止硬编码
├── A17.2: AI处理双阶段流程
│   ├── A17.2.1: 阶段一：文档初步检查 - 输出状态、存在文档、缺失文档、企业候选信息
│   └── A17.2.2: 阶段二：全面合规验证 - 输出验证摘要、字段状态、企业档案
├── A17.3: LLM分析处理
│   ├── A17.3.1: 专注于验证文档内容是否符合预期格式和要求
│   ├── A17.3.2: LLM调用失败时直接返回网络错误，无重试机制
│   └── A17.3.3: 支持结构化JSON输出，确保响应格式一致性
```

------------------------------

### A18: 企业文档上传集成

```
├── A18.1: 企业文档上传集成
│   ├── A18.1.1: company_identity_agent调度 - 企业验证文档处理
│   ├── A18.1.2: 验证状态管理 - document_upload状态流程控制
│   ├── A18.1.3: 多公司检测 - 多企业文档的检测和处理
│   └── A18.1.4: 验证失败处理 - 企业验证失败的重试机制
├── A18.2: 文档接收与预处理
│   ├── A18.2.1: 通过标准的AgentRequest接收企业相关文档
│   ├── A18.2.2: 支持直接文件传递或通过URL下载文档
│   └── A18.2.3: 自动识别文件类型并转换为Base64编码
├── A18.3: 文档处理策略
│   ├── A18.3.1: 无持久化 - 文档仅在内存中处理，不存储到磁盘
│   ├── A18.3.2: 自动清理 - 请求完成后自动释放内存资源
│   ├── A18.3.3: 类型识别 - 自动识别文件类型，支持多种文档格式
│   └── A18.3.4: Base64传输 - 安全的文档编码和传输机制
├── A18.4: 通用上传优化
│   ├── A18.4.1: 文件格式验证 - 支持PDF、DOC、DOCX等格式
│   ├── A18.4.2: 文件大小限制 - 上传文件大小的限制机制
│   ├── A18.4.3: 上传进度跟踪 - 文件上传进度的状态跟踪
│   └── A18.4.4: 临时文件清理 - 上传临时文件的清理机制
└── A18.5: 性能与扩展约束
    ├── A18.5.1: 文件大小限制 - 单个文档最大支持5MB
    ├── A18.5.2: 处理性能 - LLM文档分析处理时间通常在秒级内完成
    ├── A18.5.3: 并发支持 - 支持异步并发处理多个验证请求，无状态设计
    └── A18.5.4: 扩展性 - 水平扩展支持，无需额外优化或复杂缓存机制
```

------------------------------

### A19: 环境配置

```
├── A19.1: Python环境完整规范
│   ├── A19.1.1: Python版本 - Python 3.10+（强制）
│   ├── A19.1.2: 运行环境 - 支持asyncio异步并发处理
│   ├── A19.1.3: 依赖管理 - 使用requirements.txt管理依赖版本
│   └── A19.1.4: 资源要求 - 内存512MB+，CPU 1核+
├── A19.2: Pydantic V2 完整规范
│   ├── A19.2.1: 必须使用 - model_validate()、model_dump()、Field()、BaseModel
│   ├── A19.2.2: 严禁使用 - .dict()、.parse_obj()、.json()、parse_obj_as()
│   ├── A19.2.3: 字段验证 - 必须使用pattern=r"regex"，严禁使用regex=r"regex"
│   └── A19.2.4: 模型导入 - 统一从global_schemas导入，禁止本地重复定义
├── A19.3: 异步处理完整规范
│   ├── A19.3.1: 必须 - 所有文档处理和验证方法使用async def
│   ├── A19.3.2: 禁止 - 同步阻塞操作、threading、multiprocessing
│   └── A19.3.3: 并发 - 使用asyncio.create_task()、asyncio.gather()处理并发文档分析
```

------------------------------

### A20: 运行要求

```
├── A20.1: 部署规范完整约束
│   ├── A20.1.1: 环境要求 - Python 3.10+，内存512MB+，CPU 1核+
│   ├── A20.1.2: 依赖服务 - routing_agent、llm_handler_agent、database_agent、global_config
│   ├── A20.1.3: 监控指标 - 文档验证成功率>95%，响应时间<5秒，并发处理能力50+请求/分钟
│   └── A20.1.4: 健康检查 - 服务启动检查、配置加载验证、外部依赖连通性检查
├── A20.2: 模块接入说明
│   ├── A20.2.1: company_identity_agent是被动调用的业务模块，不包含启动逻辑和测试代码
│   ├── A20.2.2: 系统启动使用python main.py --start从boot/启动整个系统
│   ├── A20.2.3: 模块装配通过boot/launcher.py基于applications/__registry__.py装配
│   ├── A20.2.4: 服务调用启动后通过routing_agent进行统一调度
│   └── A20.2.5: 功能测试测试逻辑已迁移至utility_tools/global_test/进行独立管理
```

------------------------------

### A21: 版本依赖

```
├── A21.1: Python依赖版本
│   └── Python 3.10+，asyncio异步并发处理，requirements.txt依赖管理
├── A21.2: 框架依赖
│   ├── A21.2.1: Pydantic V2框架 - 模型验证和序列化
│   └── A21.2.2: 标准logging模块 - 日志记录
├── A21.3: 外部服务依赖
│   ├── A21.3.1: routing_agent - 统一调度和配置管理
│   ├── A21.3.2: global_schemas - 数据模型定义
│   ├── A21.3.3: llm_handler_agent - LLM文档分析服务
│   └── A21.3.4: database_agent - 企业档案存储服务
```

------------------------------

### A22: 模块限制

```
├── A22.1: 文件系统红线
│   ├── A22.1.1: 工作区 - 生成和修改仅允许发生在applications/company_identity_agent/内
│   ├── A22.1.2: 主入口约定 - 模块主入口文件名与company_identity_agent同名
│   ├── A22.1.3: 粒度限制 - 单次变更仅允许操作一个文件，超过300行自动截断
│   └── A22.1.4: 结构稳定性 - 禁止新建"公共"目录，禁止在模块间互放工具文件
├── A22.2: 职责分层边界
│   ├── A22.2.1: Main主文件 - 只做策略选择、依赖装配、流程编排，禁止任何业务规则、存储访问、外部I/O
│   ├── A22.2.2: Adapter适配层 - 只实现外设与机制，禁止写业务决策
│   ├── A22.2.3: Aux私有实现 - 仅供Main/Adapter内部复用，不得跨模块导出
│   └── A22.2.4: 拆分触发 - 单文件同时承担两类以上变更原因或超过200行时必须拆分
├── A22.3: 关键词黑名单
│   ├── A22.3.1: 禁止本地业务模型定义 - "class .*Model"、"data class .*"、"interface .*DTO"
│   ├── A22.3.2: 禁止硬编码配置 - "API_KEY="、"timeout\\s*=\\s*\\d+"、"retry\\s*=\\s*\\d+"
│   ├── A22.3.3: 禁止跨层I/O - 在Main/Aux中出现"http"、"db"、"sql"、"open("、"requests"、"fetch"
│   ├── A22.3.4: 禁止并发越界 - "Thread"、"Process"、"fork"、"Pool"
│   └── A22.3.5: 禁止未脱敏日志 - "print("、"console.log("、"logging.info(f\\".*password|token|secret"
```

------------------------------

### A23: 测试策略

```
├── A23.1: 生产级测试指南
│   ├── A23.1.1: 真实企业文档准备 - SEC注册企业、DTI注册企业、混合验证企业完整文档集
│   ├── A23.1.2: 预期处理步骤验证 - 文档识别与分类、LLM信息提取、标准化处理、一致性验证四个阶段
│   └── A23.1.3: 特殊测试场景 - 地址不一致测试、当年有效性测试、文档缺失测试
├── A23.2: 测试规范完整约束
│   ├── A23.2.1: 生产级测试 - 使用真实的文档验证流程，禁用Mock验证机制
│   ├── A23.2.2: 完整流程 - 测试完整的双阶段验证链路（初步检查→全面验证）
│   ├── A23.2.3: 真实集成 - 使用真实的routing_agent、llm_handler_agent、database_agent集成
│   └── A23.2.4: 并发测试 - 测试多文档并发处理的正确性和性能
├── A23.3: 最小用例要求
│   └── 本模块至少提供冒烟链路与失败路径两类用例，用例不得Mock掉对外契约（可Mock外设）
```

------------------------------

### A24: 验收机制

```
├── A24.1: 验收门槛
│   └── 生成变更必须先通过本模块用例再提交，未达门槛禁止继续生成下一文件
├── A24.2: 测试输出示例
│   ├── A24.2.1: 成功验证输出 - 包含状态、验证结果、企业档案、即时反馈等完整信息
│   └── A24.2.2: 失败验证输出 - 包含错误信息、重新上传指导、技术支持选项
├── A24.3: 测试验证方法
│   ├── A24.3.1: 文档解析验证 - 检查PDF解析和OCR文本提取的完整性
│   ├── A24.3.2: LLM提取验证 - 验证关键信息提取的准确性和格式规范性
│   ├── A24.3.3: 标准化算法验证 - 测试各标准化函数的处理效果和一致性
│   ├── A24.3.4: 一致性检查验证 - 确认跨文档一致性检查的严格性
│   ├── A24.3.5: 即时反馈验证 - 测试对话驱动的实时验证反馈机制
│   └── A24.3.6: 失败场景验证 - 测试地址不一致等失败场景的正确处理
```

------------------------------

### A25: 部署策略

```
├── A25.1: 部署配置
│   └── 生产环境监控指标包含验证成功率>95%、平均响应时间<5秒、文档处理速率>50/分钟、错误率<5%、LLM调用成功率>98%等关键指标
├── A25.2: 健康检查端点
│   └── 检查routing_agent连通性、llm_handler可用性、配置加载、文档处理等关键服务状态，返回整体健康状态和详细检查结果
├── A25.3: 故障诊断与调试规范
│   ├── A25.3.1: 常见问题解决 - 文档验证失败、配置加载异常、性能问题的诊断方法
│   ├── A25.3.2: 日志分析 - 使用request_id追踪完整验证链路
│   └── A25.3.3: 调试模式 - 支持详细日志输出和中间结果保存
```

------------------------------

### A26: 未来规划

```
⚠️ 未定义 - 原文档中未包含明确的未来规划内容
```

------------------------------

### A27: 未定义项

```
├── A27.1: 配置参数待补
│   ├── A27.1.1: company_identity_agent.verification_rules.address_match_tolerance - 地址匹配度阈值配置
│   ├── A27.1.2: company_identity_agent.document_templates.required_document_sets.sec - SEC注册企业必需文档清单
│   └── A27.1.3: company_identity_agent.timeout_config.llm_analysis_timeout - LLM文档分析处理超时控制
├── A27.2: Schema字段待补
│   ├── A27.2.1: CompanyProfile缺失registry_type字段 - 企业注册类型识别和验证规则选择
│   ├── A27.2.2: VerificationResult缺失verification_summary字段 - 验证规则执行结果的详细记录
│   └── A27.2.3: DocumentRecord缺失doc_hash_sha256字段 - 文档完整性验证和重复检测
├── A27.3: 路径映射待补
│   └── 企业文档临时处理目录路径 - {MODULE_ROOT}/temp_docs/ vs {MODULE_ROOT}/processing/
├── A27.4: 错误码待补
│   └── LLM文档分析失败错误码 - COMPANY/LLM_ANALYSIS_FAILED企业文档LLM分析失败场景
├── A27.5: 指标名称待补
│   └── company_document_processing_duration_seconds - 企业文档处理性能监控指标
├── A27.6: 依赖关系待补
│   └── 与database_agent的企业档案存储协作 - 交互方式和数据传递格式确认
├── A27.7: 业务规则待补
│   ├── A27.7.1: 地址部分匹配的容错处理 - 地址要素部分匹配时的通过标准
│   └── A27.7.2: DTI企业业主名不匹配的处理策略 - owner_name不匹配时是否影响最终验证结果
```

------------------------------

### A28: 待补要点

```
├── A28.1: 必要说明
│   └── 遇到字段未定义、路径不明、错误码缺失、指标未命名等情况，生成器不得继续实现，必须在README的"待补要点"清单中列出：待补键名/字段（含建议默认值/取值域）、影响面（调用方、下游模块、运行时风险）、最小决策集（给出2～3个可选项，偏保守）
├── A28.2: 禁止脑补机制
│   └── 遇到缺失信息（路径/键名/Schema字段/错误码），停止输出并在README的"待补要点"清单中列明，不得擅自发明
├── A28.3: 待补要点清单
│   └── 包含配置参数待补、Schema字段待补、路径映射待补、错误码待补、指标名称待补、依赖关系待补、业务规则待补等7个主要类别的未定义项目
```

------------------------------

### A29: 黑名单

```
├── A29.1: 检测红线
│   ├── A29.1.1: 禁止本地业务模型定义 - "class .*Model"、"data class .*"、"interface .*DTO"
│   ├── A29.1.2: 禁止硬编码配置 - "API_KEY="、"timeout\\s*=\\s*\\d+"、"retry\\s*=\\s*\\d+"
│   ├── A29.1.3: 禁止跨层I/O - 在Main/Aux中出现"http"、"db"、"sql"、"open("、"requests"、"fetch"
│   ├── A29.1.4: 禁止并发越界 - "Thread"、"Process"、"fork"、"Pool"
│   └── A29.1.5: 禁止未脱敏日志 - "print("、"console.log("、"logging.info(f\\".*password|token|secret"
├── A29.2: 生成器执行规范
│   ├── A29.2.1: 部分修改优先 - 每次仅修改一个文件，≤300行
│   ├── A29.2.2: 禁止脑补 - 遇到缺失信息停止输出并在README标注
│   ├── A29.2.3: 依赖单向 - Domain→Adapter单向依赖，检测到反向引用直接终止
│   ├── A29.2.4: 不迁移/不重命名/不删除 - 除非README明确列出变更映射
│   └── A29.2.5: 不新增公共层 - "utils/common/shared"目录新增一律拒绝
```

------------------------------

### A30: 禁用规则

```
├── A30.1: 文件操作禁用规则
│   ├── A30.1.1: 禁止创建、移动、重命名、删除applications/company_identity_agent/之外的任何文件/目录
│   ├── A30.1.2: 禁止因实现便利而新建"公共"目录
│   ├── A30.1.3: 禁止在模块间互放工具文件
│   └── A30.1.4: 不得私自抽公共层
├── A30.2: 数据访问禁用规则
│   ├── A30.2.1: 模块不得直接访问持久化（DB/Cache/FS）
│   ├── A30.2.2: 必须通过指定Adapter间接访问database_agent统一管理的存储层
│   ├── A30.2.3: 任何网络/系统I/O仅可写在Adapter
│   └── A30.2.4: Main/Aux出现I/O视为违规
├── A30.3: 并发控制禁用规则
│   ├── A30.3.1: 仅允许使用语言原生异步原语（如async/await、事件循环）
│   ├── A30.3.2: 禁止线程池/进程池，除非在Adapter层且README明示风险与回收策略
│   └── A30.3.3: 必须经routing_agent的config_manager服务注入超时与重试参数
├── A30.4: 安全与合规禁用规则
│   ├── A30.4.1: 不得在代码/README/示例中出现任何真实秘钥
│   ├── A30.4.2: 仅允许读取环境变量或安全管理器的别名
│   ├── A30.4.3: 所有外部输入必须显式校验（长度/类型/枚举/格式）
│   └── A30.4.4: 模块内不得提升权限，仅请求所需最小范围的权限与数据字段
```

