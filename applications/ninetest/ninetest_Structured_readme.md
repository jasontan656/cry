# ninetest_agent 结构化文档骨架

## 文档结构化分析 - Step 1

### A1: 开发边界限制与规范约束

```
├── A1-1: 适用范围与角色定义
│   ├── A1-1.1: 目标说明 - 限制自动化生成在文件创建/编辑/依赖方向/接口契约四个维度的自由度，避免脑补
│   └── A1-1.2: 占位符映射 - MODULE_NAME: ninetest_agent, MODULE_ROOT: applications/ninetest_agent/, GLOBAL_SCHEMAS: global_schemas模块, GLOBAL_CONFIG: routing_agent的config_manager服务, STATE_STORE: database_agent统一管理的存储层
├── A1-2: 目录与文件边界约束
│   ├── A1-2.1: 工作区限制 - 生成和修改仅允许发生在applications/ninetest_agent/内，禁止创建、移动、重命名、删除外部文件/目录
│   ├── A1-2.2: 主入口约定 - 模块主入口文件名与ninetest_agent同名，非主入口的新增文件必须归类为Adapter或Aux
│   ├── A1-2.3: 粒度限制 - 单次变更仅允许操作一个文件，若超过300行自动截断并停止，等待下一次续写
│   └── A1-2.4: 结构稳定性 - 禁止因实现便利而新建"公共"目录，禁止在模块间互放工具文件，不得私自抽公共层
├── A1-3: 职责分层边界约束
│   ├── A1-3.1: Main层职责 - 只做策略选择、依赖装配、流程编排，禁止任何业务规则、存储访问、外部I/O
│   ├── A1-3.2: Adapter层职责 - 只实现外设与机制（HTTP/DB/Cache/Queue/FS/LLM调用等），禁止写业务决策
│   ├── A1-3.3: Aux层职责 - 仅供Main/Adapter内部复用，不得跨模块导出，禁止出现横向依赖
│   └── A1-3.4: 拆分触发条件 - 当单文件同时承担两类以上变更原因或超过200行时必须拆分到对应层
├── A1-4: 契约与模型来源约束
│   ├── A1-4.1: 模型唯一来源 - 所有数据模型/Schema已迁移至global_schemas.json，由routing_agent动态分发。禁止在模块内新增/复制业务模型或DTO
│   ├── A1-4.1.1: 字段已迁移声明 - NinetestAssessment、TalentCategories、NarrativeReport、DetailedScores、ContextData、ProcessingResult等模型已迁移至global_schemas.json
│   ├── A1-4.1.2: 配置已迁移声明 - 所有测试配置、数字天赋定义、分析公式、LLM提示模板已迁移至global_config.json
│   ├── A1-4.2: 接口契约要求 - 本模块README必须提供最小可执行契约（接口签名或伪码），仅声明入参/出参/错误码，不提供实现样例
│   └── A1-4.3: 版本与兼容策略 - 任何新增/变更字段必须在README标注语义、默认值、兼容策略，并同步更新global_schemas对应版本
├── A1-5: 配置与特性开关约束
│   ├── A1-5.1: 配置唯一来源 - 配置仅可经由routing_agent的config_manager服务读取，禁止本地硬编码可变配置
│   └── A1-5.2: 热更新与回滚 - 配置键名/层级不可私改，新增键必须提供默认值、回滚策略，未在routing_agent的config_manager服务注册的键不得使用
```

------------------------------

### A2: 模块基本定义与概述

```
├── A2-1: 模块核心定义
│   └── A2-1.1: 模块身份 - ninetest_agent是Career Bot系统的九型数字天赋测试分析中心，负责处理基于出生日期数字频率分析的天赋测试，通过确定性算法计算数字频率，结合AI文本生成，为用户提供个性化的天赋分析报告
├── A2-2: 核心功能特性概览
│   ├── A2-2.1: 数字频率天赋分析 - 出生日期解析、数字频率计算、天赋分类系统、确定性算法、对话确认机制
│   ├── A2-2.2: 十维天赋评估体系 - 行动本能组、执行习惯组、意识直觉组、核心整合力四大分组，涵盖十个维度的能力评估
│   └── A2-2.3: 多层次分析报告 - 结构化数据、叙述风格报告、双格式输出、发展建议
└── A2-3: 模块接入说明
    ├── A2-3.1: 运行模式 - ninetest_agent是被动调用的业务模块，不包含启动逻辑和测试代码
    ├── A2-3.2: 系统启动方式 - 使用python main.py --start从boot/启动整个系统，通过boot/launcher.py基于applications/__registry__.py装配
    ├── A2-3.3: 服务调用方式 - 启动后通过routing_agent进行统一调度
    └── A2-3.4: 功能测试方式 - 测试逻辑已迁移至utility_tools/global_test/进行独立管理
```

------------------------------

### A3: 系统架构与模块定位

```
├── A3-1: 系统架构位置
│   └── A3-1.1: 调用链路 - 用户输入出生日期 → entry_agent → routing_agent → [ninetest_agent] → 数字频率计算 → 天赋分类 → llm_handler_agent(文本生成) → 结构化报告+叙述文本 → database_agent
├── A3-2: 模块架构设计约束
│   ├── A3-2.1: 架构设计原则 - 主入口文件职责仅提供统一接口注册和任务分发能力，不实现具体业务逻辑，保持主文件简洁性和可维护性
│   ├── A3-2.2: 业务实现分离 - 所有具体业务功能必须通过独立的业务处理模块实现，包括数字天赋分析与频率计算逻辑、出生日期处理与数字提取算法、天赋分类与评估体系处理、LLM报告生成与格式化输出、天赋配置加载与规则管理
│   ├── A3-2.3: 模块化组织约束 - 避免单一文件承载过多业务逻辑，按功能域进行合理拆分，每个业务模块专注单一职责，确保代码可测试性和可维护性，通过依赖注入和接口抽象降低模块间耦合度
│   └── A3-2.4: 配置驱动 - 所有数字天赋定义、分析公式、LLM提示模板通过routing_agent从global_config动态获取，支持热更新和版本管理
└── A3-3: 协作关系与触发机制
    ├── A3-3.1: 模块协作规范 - 被动调用、无状态设计、中枢调度、统一入口、独立触发协作、输出协议扩展、流程位置、数据协作
    └── A3-3.2: 自动触发策略 - 完成NINETEST天赋分析后立即自动触发final_analysis_output_agent第一阶段分析，无需等待其他条件，分析完成后输出包含trigger_first_analysis: true标志
```

------------------------------

### A4: 输出数据结构与规范

```
├── A4-1: 预格式化输出结构
│   ├── A4-1.1: 天赋测试结果输出格式 - 包含user_id、ninetest_assessment完整结构，与database_agent的用户画像存储格式完全匹配
│   ├── A4-1.2: 数字频率数据结构 - digit_frequency包含0-9所有数字的频次统计，值域0-8
│   ├── A4-1.3: 天赋分类结构 - 按core_talents、good_abilities、basic_abilities、missing_abilities四个层次分类的完整天赋列表
│   └── A4-1.4: 叙述报告结构 - narrative_report包含结构化报告和原始文本的完整AI生成报告
├── A4-2: 输出数据校验规则
│   ├── A4-2.1: 基础字段校验 - birth_date必须为YYYY-MM-DD格式已验证有效日期，frequency为整数表示数字在出生日期中的出现次数（0-8）
│   ├── A4-2.2: 分类字段校验 - category英文枚举值、chinese_category中文枚举值、name和chinese_name天赋名称与用户提供规则完全一致
│   └── A4-2.3: 描述字段校验 - description英文频率解释、chinese_description中文频率解释、workplace_applications职场应用领域数组、development_suggestions缺失能力的发展建议
├── A4-3: 标准天赋分类评级系统
│   ├── A4-3.1: 频次分级统一 - 核心才能(3次+)、良好能力(2次)、基础能力(1次)、缺失能力(0次)
│   └── A4-3.2: 分级标准描述 - 各频次等级对应的标准化描述文本和能力解释
└── A4-4: 输出报告格式规范
    ├── A4-4.1: 双格式输出 - 结合结构化数据报告和AI生成的风格化文本
    ├── A4-4.2: 标签兼容输出 - 与taggings_agent标签格式兼容的输出结构
    └── A4-4.3: 上下文传递 - 设置下阶段上下文，传递才能测试报告到最终分析阶段
```

------------------------------

### A5: 完整技术规范约束

```
├── A5-1: Python环境完整规范
│   ├── A5-1.1: 版本要求 - Python 3.10+（强制），支持asyncio异步并发处理
│   ├── A5-1.2: 依赖管理 - 使用requirements.txt管理依赖版本
│   └── A5-1.3: 资源要求 - 内存512MB+，CPU 1核+
├── A5-2: Pydantic V2完整规范
│   ├── A5-2.1: 必须使用方法 - model_validate()、model_dump()、Field()、BaseModel
│   ├── A5-2.2: 严禁使用方法 - .dict()、.parse_obj()、.json()、parse_obj_as()
│   ├── A5-2.3: 字段验证规范 - 必须使用pattern=r"regex"，严禁使用regex=r"regex"
│   ├── A5-2.4: 模型导入规范 - 统一从global_schemas导入，禁止本地重复定义
│   └── A5-2.5: 模型验证机制 - 从global_schemas导入NinetestAssessment、TalentCategory、BirthDateAnalysis模型，使用model_validate()验证输入数据，model_dump()序列化输出结果
├── A5-3: 异步处理完整规范
│   ├── A5-3.1: 异步方法要求 - 所有天赋分析和报告生成方法使用async def
│   ├── A5-3.2: 禁止同步操作 - 禁止同步阻塞操作、threading、multiprocessing
│   ├── A5-3.3: 并发处理 - 使用asyncio.create_task()、asyncio.gather()处理并发分析任务
│   └── A5-3.4: 并发处理机制 - 使用asyncio.create_task()创建数字频率计算、天赋分类、叙述报告生成并发任务，通过asyncio.gather()并行执行并聚合分析结果
├── A5-4: 配置管理完整规范
│   ├── A5-4.1: 获取方式统一 - 配置方法统一通过await routing_agent.get_config("ninetest_agent", config_type)
│   ├── A5-4.2: 配置类型定义 - "talent_mapping"、"digit_descriptions"、"llm_prompts"、"category_thresholds"
│   ├── A5-4.3: 严禁本地配置 - 严禁硬编码配置、本地配置文件、环境变量直接读取
│   ├── A5-4.4: 热更新支持 - 支持配置实时更新，无需重启服务
│   └── A5-4.5: 配置结构 - 包含数字与天赋的映射关系(digit_to_talent_mapping)、频率分类规则(frequency_category_rules)、职场应用映射(talent_workplace_mapping)等核心天赋分析配置
├── A5-5: LLM调用完整规范
│   ├── A5-5.1: 混合模式 - 确定性算法+LLM叙述生成，确定性部分：数字频率计算、分类逻辑无需LLM，LLM使用：仅用于叙述报告生成
│   ├── A5-5.2: 调用方式 - 通过await routing_agent.call_agent("llm_handler_agent", payload)
│   ├── A5-5.3: 严禁直接调用 - 严禁直接访问OpenAI、Claude、Gemini等API
│   ├── A5-5.4: 模型规范 - 强制使用gpt-4o-2024-08-06
│   └── A5-5.5: LLM调用机制 - 从global_config获取叙述生成提示模板，构造包含system_prompt和user_prompt的llm_payload，设置json_mode为False输出自然语言，通过routing_agent调用llm_handler_agent生成天赋叙述报告
└── A5-6: 其他技术规范约束
    ├── A5-6.1: 日志记录完整规范 - 使用Python标准logging模块，必要字段：request_id、agent_name、user_id、birth_date、analysis_stage、digit_frequency，结构化JSON格式，禁止使用print()
    ├── A5-6.2: 异常处理完整规范 - 异常类型：BirthDateValidationError、TalentCalculationError、ReportGenerationError，向上传播异常到routing_agent，提供详细错误上下文，用户友好错误信息
    ├── A5-6.3: 测试规范完整约束 - 生产级测试使用真实出生日期数据和确定性算法验证，完整流程测试，算法验证，一致性测试，测试覆盖范围包含完整流程测试和算法确定性测试
    └── A5-6.4: 部署规范完整约束 - 环境要求Python 3.10+，依赖服务routing_agent/llm_handler_agent/database_agent/global_config，监控指标，健康检查
```

------------------------------

### A6: 对话确认完整机制

```
├── A6-1: 出生日期确认对话流程
│   ├── A6-1.1: 日期输入与初步验证 - 当用户提供出生日期时，进行初步验证和确认，包括基础格式验证、合理性检查、验证结果生成、确认问题生成
│   ├── A6-1.2: 前端确认表单生成 - ninetest_agent返回确认问题，前端生成相应的确认界面，包含确认结构和验证规则
│   ├── A6-1.3: 日期修正与重新验证 - 如果用户指出日期不准确，提供修正机制和重新验证流程
│   ├── A6-1.4: 补充信息收集 - 为了增强分析准确性，收集一些可选的补充信息
│   ├── A6-1.5: 分析结果确认 - 生成分析报告后，让用户确认结果的准确性
│   └── A6-1.6: 与Frontend_service_agent协调机制 - 状态同步、流程控制、结果反馈、快速模式
└── A6-2: 确认机制技术实现
    ├── A6-2.1: 验证函数设计 - validate_and_confirm_birth_date函数实现
    ├── A6-2.2: 确认问题生成 - 根据年龄和合理性生成相应的确认问题
    └── A6-2.3: 协调机制保证 - 确保九型数字天赋测试的基础数据准确性，通过日期确认+可选补充的方式，提高分析结果的可信度和用户认同感
```

------------------------------

### A7: 详细运行流程

```
├── A7-1: 天赋分析完整链路
│   ├── A7-1.1: 出生日期输入与验证 - 数据提取优先从context.data.dob获取，回退到text_input，格式验证严格验证YYYY-MM-DD格式，用户上下文设置用户上下文到日志系统进行请求追踪
│   ├── A7-1.2: 数字频率计算 - 日期转换将出生日期转换为8位数字字符串，频率统计使用collections.Counter统计每个数字（0-9）出现频次，数据结构生成频率映射字典作为分析基础
│   ├── A7-1.3: 配置数据加载与验证 - 数字意义配置通过routing_agent从global_config获取10个数字的天赋定义，提示模板通过routing_agent从global_config获取LLM报告生成模板，完整性验证启动时验证关键配置完整性，缺失时抛出异常
│   ├── A7-1.4: 天赋分类与归档 - 分层分类根据数字频率将能力分为4个层次，天赋映射将数字频率映射到具体的天赋名称和分组，缺失识别识别频次为0的数字，归类为需要发展的潜在弱项
│   ├── A7-1.5: AI风格化报告生成 - 提示构建将分类后的天赋数据转换为格式化提示文本，LLM调用通过routing_agent调用LLM生成叙述风格报告，角色设定使用职业发展教练角色，生成鼓励性和建设性的专业分析
│   └── A7-1.6: 多格式输出整合 - 双重输出结合结构化数据报告和AI生成的风格化文本，上下文传递设置下阶段上下文，传递才能测试报告到最终分析阶段，调试支持保留原始处理数据便于问题排查
└── A7-2: 流程技术实现细节
    ├── A7-2.1: 数字频率计算算法 - 出生日期"1992-03-25"转换为"19920325"，使用Counter统计得到频率结果
    ├── A7-2.2: 天赋分类逻辑 - 根据频次将能力分为核心才能、良好能力、基础能力、缺失能力四个层次
    └── A7-2.3: 报告生成流程 - AI生成叙述风格报告的具体实现步骤和技术细节
```

------------------------------

### A8: 标准Nine-Test十维天赋评估体系

```
├── A8-1: 完整数字天赋定义系统
│   ├── A8-1.1: 行动本能组数字定义
│   │   ├── 数字1：责任感与纪律性 - 分组：行动本能组，核心特征：强执行力守承诺可靠性高，频率解释包含3次+/2次/1次/0次的标准描述，职场应用：项目管理、质量控制、合规管理、流程执行
│   │   ├── 数字4：判断与分析力 - 分组：行动本能组，核心特征：决策果断思维清晰，频率解释包含各层次标准描述，职场应用：数据分析、战略规划、风险评估、决策支持
│   │   └── 数字7：执行与行动力 - 分组：行动本能组，核心特征：专注实务行动力强，频率解释包含各层次标准描述，职场应用：运营管理、销售执行、实施落地、生产运作
│   ├── A8-1.2: 执行习惯组数字定义
│   │   ├── 数字2：服务与感知力 - 分组：执行习惯组，核心特征：极度关怀他人善于支持协助，频率解释包含各层次标准描述，职场应用：客户服务、人力资源、团队协作、用户体验
│   │   ├── 数字5：决策与冒险精神 - 分组：执行习惯组，核心特征：勇于尝试目标感强，频率解释包含各层次标准描述，职场应用：创业创新、业务拓展、变革管理、新市场开发
│   │   └── 数字8：管理与协调力 - 分组：执行习惯组，核心特征：善于规划资源配置高效，频率解释包含各层次标准描述，职场应用：团队管理、项目协调、组织规划、资源调配
│   ├── A8-1.3: 意识直觉组数字定义
│   │   ├── 数字3：共情与视野力 - 分组：意识直觉组，核心特征：情感敏感表达力强，频率解释包含各层次标准描述，职场应用：市场营销、公关传播、客户关系、团队沟通
│   │   ├── 数字6：精力与专注力 - 分组：意识直觉组，核心特征：持久耐力意志力超强，频率解释包含各层次标准描述，职场应用：研发工作、深度分析、长期项目、质量保证
│   │   └── 数字9：灵感与洞察力 - 分组：意识直觉组，核心特征：洞察力强创意非凡，频率解释包含各层次标准描述，职场应用：创意设计、产品开发、战略咨询、创新研发
│   └── A8-1.4: 核心整合力数字定义
│       └── 数字0：整合与转化力 - 分组：核心整合力，核心特征：善于总结自我觉察能力超强，频率解释包含各层次标准描述，职场应用：综合管理、教练培训、系统思维、知识管理
├── A8-2: 标准天赋分级评级系统
│   ├── A8-2.1: 分级标准定义 - 3次+核心才能：强大功能突出优势，2次良好能力：中等强度能力，1次基础能力：基本稳定表现，0次缺失能力：潜在弱项需补偿
│   └── A8-2.2: 频率计算算法 - 出生日期"1992-03-25"示例，date_string="19920325"，使用Counter统计得到frequency结果
└── A8-3: 天赋评估体系应用
    ├── A8-3.1: 十维能力覆盖 - 行动本能组3个维度、执行习惯组3个维度、意识直觉组3个维度、核心整合力1个维度
    ├── A8-3.2: 四层分级应用 - 根据数字频次将能力科学分为四个层次，确保测试结果的科学性和一致性
    └── A8-3.3: 职场应用指导 - 每个天赋维度都包含具体的职场应用领域，直接指导职业发展方向
```

------------------------------

### A9: 配置管理系统

```
├── A9-1: 完整数字天赋配置规范
│   ├── A9-1.1: 数字天赋配置结构 - 每个数字（0-9）包含name、chinese_name、group、chinese_group、frequency_interpretation、chinese_frequency_interpretation、workplace_applications、workplace_applications_chinese完整结构
│   └── A9-1.2: 配置示例结构 - 以数字1为例展示完整的配置数据结构，包含所有必需字段和多语言支持
├── A9-2: LLM提示词配置类型
│   ├── A9-2.1: 配置类型定义 - nintest_config：数字天赋定义和频率解释的完整配置，llm_prompts：AI报告生成提示词模板配置，output_templates：标准输出格式模板配置，validation_rules：数据校验规则配置
│   └── A9-2.2: 配置获取示例 - 加载数字天赋配置、LLM提示词模板、输出格式模板的具体实现方法
├── A9-3: LLM提示模板配置系统
│   ├── A9-3.1: AI报告生成提示词模板 - ninetest_report_generation_en包含system_prompt、user_prompt、model、temperature、max_tokens、variables的完整配置
│   ├── A9-3.2: 标准报告输出格式模板 - 包含reportTitle、subtitle、note、strengths、areasForImprovement、warmReminder的标准结构
│   └── A9-3.3: 提示词调用机制 - 与taggings_agent一致的提示词调用实现，包括获取提示词配置、准备变量数据、构建LLM请求、调用LLM生成报告的完整流程
└── A9-4: 配置管理技术实现
    ├── A9-4.1: 配置获取机制 - 通过routing_agent.get_config()统一获取各类配置
    ├── A9-4.2: 配置验证机制 - 启动时验证关键配置完整性，确保所有必需配置项存在
    └── A9-4.3: 配置热更新支持 - 支持配置实时更新，无需重启服务，保证系统的灵活性和可维护性
```

------------------------------

### A10: 接口契约与技术规范

```
├── A10-1: 核心接口规范
│   ├── A10-1.1: 统一入口接口 - async def run(request: AgentRequest) -> AgentResponse，包含完整的参数说明、返回值定义、异常处理规范
│   └── A10-1.2: 接口参数要求 - request结构包含request_id、task_type、user_id、session_id、message、intent等直接字段，返回AgentResponse包含request_id、agent_name、success、timestamp、processing_status、results、error_details
├── A10-2: 支持的任务类型
│   ├── A10-2.1: 核心任务类型 - ninetest_analysis（主要任务类型）、birth_date_validation、digit_frequency_calculation、talent_report_generation、health_check、get_config
│   └── A10-2.2: 任务类型统一标识 - 使用标准化的task_type标识符，确保调用的一致性和可维护性
├── A10-3: 错误码规范
│   ├── A10-3.1: 标准错误码格式 - 使用{DOMAIN}/{REASON}命名格式
│   ├── A10-3.2: 通用错误码 - VALIDATION/INVALID_INPUT、CONFIG/NOT_FOUND、CONFIG/INVALID_FORMAT、TIMEOUT/REQUEST_TIMEOUT、AUTH/UNAUTHORIZED、IO/UNAVAILABLE
│   └── A10-3.3: 九型测试特定错误码 - NINETEST/INVALID_BIRTH_DATE、NINETEST/DIGIT_CALCULATION_ERROR、NINETEST/REPORT_GENERATION_FAILED、NINETEST/LLM_ANALYSIS_ERROR、NINETEST/TALENT_MAPPING_ERROR、NINETEST/CATEGORY_CLASSIFICATION_FAILED
├── A10-4: 配置依赖清单
│   ├── A10-4.1: 必需配置项 - basic_config、timeout_config、retry_config、talent_mapping、classification_rules、llm_prompts、report_templates
│   └── A10-4.2: 配置获取方式 - 通过await routing_agent.get_config("ninetest_agent", config_type)统一获取
├── A10-5: 依赖模块清单
│   ├── A10-5.1: 必须依赖 - routing_agent：统一调度和配置管理，global_schemas：数据模型定义，llm_handler_agent：LLM天赋分析报告生成服务，database_agent：天赋测试结果存储服务
│   └── A10-5.2: 模块协作方式 - 所有模块交互统一通过routing_agent进行调度和协调
├── A10-6: 数据模型规范
│   ├── A10-6.1: 必须使用的Schema - 从global_schemas导入的标准模型：AgentRequest、AgentResponse、NineTestAssessment、TalentAnalysis、DigitFrequency
│   └── A10-6.2: 模型使用约束 - 严格使用Pydantic V2规范，禁止本地重复定义业务模型
├── A10-7: 性能指标规范
│   ├── A10-7.1: 必须暴露的指标 - ninetest_agent_requests_total、ninetest_agent_success_rate、ninetest_agent_duration_seconds、ninetest_calculation_accuracy、ninetest_llm_call_success_rate、ninetest_report_generation_success_rate
│   └── A10-7.2: 指标命名规范 - 所有指标名称在README中固化，禁止私改
└── A10-8: 最小可执行示例
    ├── A10-8.1: 九型天赋测试调用示例 - 包含AgentRequest构造、调用执行、响应处理的完整示例代码
    └── A10-8.2: 错误处理示例 - 展示如何处理各种错误情况和异常场景
```

------------------------------

### A11: 核心接口定义与约束

```
├── A11-1: C4_INTERFACE_MINIMUM规范
│   ├── A11-1.1: 主接口run()方法 - Name：run(request: AgentRequest) -> AgentResponse，Method：异步函数调用，Path/Topic：通过routing_agent调用九型数字天赋分析
│   ├── A11-1.2: 最小请求格式 - 包含request_id、task_type、user_id、context等必需字段的标准请求结构
│   ├── A11-1.3: 最小响应格式 - 包含status、data等字段的标准响应结构，支持ANALYSIS_COMPLETE和ERROR状态
│   └── A11-1.4: 错误代码定义 - INVALID_DATE_FORMAT、CALCULATION_ERROR、REPORT_GENERATION_ERROR标准错误码
├── A11-2: 特殊约束
│   ├── A11-2.1: 数字天赋分析职责 - 承担系统天赋测试核心职责
│   ├── A11-2.2: 确定性算法约束 - 数字频率计算基于完全确定的算法
│   ├── A11-2.3: LLM调用约束 - 仅通过llm_handler_agent进行文本风格化，核心逻辑基于规则
│   └── A11-2.4: 质量控制约束 - 严禁Fallback，确保真实测试结果
└── A11-3: 接口技术实现要求
    ├── A11-3.1: 异步处理要求 - 所有接口方法必须使用async/await模式
    ├── A11-3.2: 参数验证要求 - 严格验证所有输入参数的格式和有效性
    └── A11-3.3: 响应格式要求 - 统一使用标准化的响应格式和错误处理机制
```

------------------------------

### A12: 模块契约总结与协作机制

```
├── A12-1: 核心职责总结
│   ├── A12-1.1: 核心职责定义 - 数字频率天赋分析、出生日期处理、天赋分类评估、结构化报告生成、AI文本风格化、标签兼容输出
│   ├── A12-1.2: 运行模式 - 被动调用、无状态设计、确定性算法、AI文本增强、与taggings_agent协作
│   ├── A12-1.3: 分析能力 - 十维天赋体系、四层分级标准(3+/2/1/0)、数字频率算法、双语输出、标签兼容
│   ├── A12-1.4: AI集成 - 通过routing_agent调用LLM、专业文本生成、鼓励性分析报告、结构化JSON输出
│   ├── A12-1.5: 架构特性 - 配置驱动规则、内存缓存优化、双格式输出、标签映射机制、上下文传递
│   └── A12-1.6: 严格约束 - 无Mock机制、确定性计算、配置管理、异步并发、真实测试结果、标签一致性
├── A12-2: 关键价值
│   ├── A12-2.1: 科学性 - 基于数字频率的确定性算法，结果可重现和验证
│   ├── A12-2.2: 个性化 - 基于出生日期的个人天赋分析，提供独特的自我认知视角
│   ├── A12-2.3: 实用性 - 十维天赋体系覆盖职场核心能力，直接指导职业发展
│   ├── A12-2.4: 用户友好 - AI生成的专业叙述报告，易于理解和应用
│   └── A12-2.5: 标签兼容 - 与taggings_agent的Layer标签体系完全兼容，支持智能匹配
├── A12-3: 与taggings_agent协作机制
│   ├── A12-3.1: 天赋标签映射到Layer体系 - 核心才能→Layer 4+PREFERRED权重、良好能力→Layer 4+CONTEXTUAL权重、基础能力→Layer 4+CONTEXTUAL权重、缺失能力→Layer 5+CONTEXTUAL权重
│   ├── A12-3.2: 标签生成协作流程 - generate_talent_tags_for_tagging函数生成与taggings_agent兼容的天赋标签，处理核心才能和缺失能力的标签转换
│   └── A12-3.3: 完整标签生成流程 - trigger_full_tagging_process函数触发完整的标签生成流程，包含ninetest天赋标签和调用taggings_agent进行完整用户标签生成
└── A12-4: 测试科学性保证
    ├── A12-4.1: 算法透明性 - 数字频率计算过程完全透明，用户可验证
    ├── A12-4.2: 结果一致性 - 相同出生日期必然产生相同的分析结果
    ├── A12-4.3: 发展导向 - 重点关注潜在发展领域而非固化能力标签
    └── A12-4.4: 平衡视角 - 强调天赋是参考工具，需结合个人经历综合理解
```

------------------------------

### A13: 术语与名词表统一定义

```
├── A13-1: 主要术语
│   ├── A13-1.1: 核心术语定义 - 模块名称：ninetest_agent，测试类型：九型数字天赋测试，核心算法：数字频率计算算法，分级标准：四层频次分级，任务类型：ninetest_analysis，配置来源：routing_agent配置管理
│   └── A13-1.2: 术语使用规范 - 所有术语必须使用统一的标准名称，确保文档和代码的一致性
├── A13-2: 数据模型术语
│   ├── A13-2.1: 模型术语定义 - 请求载荷：AgentRequest，响应载荷：AgentResponse，天赋测试模型：NineTestAssessment，天赋分析模型：TalentAnalysis
│   └── A13-2.2: 模型来源统一 - 所有数据模型术语都来源于global_schemas模块，确保系统的一致性
└── A13-3: 错误码术语
    ├── A13-3.1: 错误码前缀 - 九型测试错误：NINETEST/，通用验证错误：VALIDATION/，配置错误：CONFIG/
    └── A13-3.2: 错误码命名规范 - 使用{DOMAIN}/{REASON}格式，确保错误码的标准化和可读性
```

------------------------------

### A14: 依赖与职责边界定义

```
├── A14-1: 上游依赖
│   ├── A14-1.1: 触发来源 - entry_agent → routing_agent → ninetest_agent
│   ├── A14-1.2: 数据来源 - context.data.birth_date (YYYY-MM-DD格式)
│   ├── A14-1.3: 配置来源 - routing_agent.get_config("ninetest_agent", config_type)
│   └── A14-1.4: 模型来源 - global_schemas模块的标准数据模型
├── A14-2: 下游调用
│   ├── A14-2.1: 存储协作 - database_agent存储天赋测试结果
│   ├── A14-2.2: 文本生成 - llm_handler_agent生成叙述风格报告
│   ├── A14-2.3: 自动触发 - final_analysis_output_agent完成后触发第一阶段分析
│   └── A14-2.4: 标签协作 - taggings_agent提供天赋标签用于智能匹配
├── A14-3: 核心职责边界
│   ├── A14-3.1: 负责范围 - 数字频率计算、天赋分类、结构化输出、AI文本生成调度
│   └── A14-3.2: 不负责范围 - 用户认证、数据持久化、直接LLM调用、前端显示
└── A14-4: 并发与顺序性
    ├── A14-4.1: 内部并发 - 数字计算与配置加载可并行处理
    ├── A14-4.2: 外部顺序 - 必须在MBTI测试完成后被触发，完成后触发第一次综合分析
    └── A14-4.3: 状态管理 - 完全无状态设计，每次调用独立完成
```

------------------------------

### A15: 重大决策与架构约束

```
├── A15-1: 算法决策
│   ├── A15-1.1: 确定性计算 - 数字频率计算基于完全确定的数学算法，无随机性
│   ├── A15-1.2: 频次分级 - 采用3次+/2次/1次/0次标准，映射到核心才能/良好能力/基础能力/缺失能力
│   └── A15-1.3: 双语输出 - 同时提供中英文天赋描述和职场应用建议
├── A15-2: 技术架构决策
│   ├── A15-2.1: 被动调用模式 - 仅响应routing_agent调度，不主动运行
│   ├── A15-2.2: 配置驱动 - 所有天赋定义、描述模板通过配置管理，支持热更新
│   └── A15-2.3: 混合生成 - 确定性算法处理分类，LLM处理文本风格化
├── A15-3: 集成决策
│   ├── A15-3.1: 自动触发策略 - 完成天赋分析后立即触发final_analysis_output_agent第一阶段
│   ├── A15-3.2: 标签兼容性 - 输出格式与taggings_agent Layer体系完全兼容
│   └── A15-3.3: 错误处理策略 - 异常向routing_agent传播，保留完整错误上下文
└── A15-4: 质量控制决策
    ├── A15-4.1: 无Mock约束 - 严禁使用Mock数据，确保真实测试结果
    ├── A15-4.2: 算法验证 - 相同出生日期必须产生完全相同的分析结果
    └── A15-4.3: 配置完整性 - 启动时验证关键配置完整性，缺失时抛出异常
```

------------------------------

### A16: 契约与字段详细规范

```
├── A16-1: 主接口契约
│   ├── A16-1.1: 接口定义 - async def run(request: AgentRequest) -> AgentResponse，包含完整的参数说明和返回值定义
│   ├── A16-1.2: 必填参数 - request.request_id、request.task_type、request.birth_date
│   ├── A16-1.3: 返回字段 - success、response.talent_categories、response.digit_frequency、response.narrative_report、response.trigger_first_analysis
│   └── A16-1.4: 错误码全集 - NINETEST/INVALID_BIRTH_DATE、NINETEST/CALCULATION_ERROR、NINETEST/REPORT_GENERATION_FAILED、CONFIG/NOT_FOUND、VALIDATION/INVALID_INPUT
├── A16-2: 输入字段规范
│   ├── A16-2.1: 字段定义 - birth_date：str类型必填，YYYY-MM-DD格式有效日期；include_llm_report：bool类型可选，默认true；user_id：str类型可选，从request.user_id提取
│   └── A16-2.2: 校验规则 - 所有输入字段都有明确的校验规则和默认值定义
├── A16-3: 输出字段规范
│   ├── A16-3.1: 主要输出字段 - talent_categories各层次列表、digit_frequency数字频次映射、narrative_report.raw_narrative_text、trigger_first_analysis触发标志
│   ├── A16-3.2: 字段取值域 - 每个输出字段都有明确的类型定义和取值范围
│   └── A16-3.3: 天赋对象结构规范 - 包含digit、name、chinese_name、frequency、category、chinese_category、description、workplace_applications的完整结构
└── A16-4: 配置契约
    ├── A16-4.1: 配置类型定义 - nintest_config、llm_prompts、timeout_config、retry_config及其必填字段要求
    ├── A16-4.2: 配置获取方式 - 通过await routing_agent.get_config("ninetest_agent", config_type)统一获取
    └── A16-4.3: 配置校验要求 - 每种配置类型都有明确的校验要求和数据完整性检查
```

------------------------------

### A17: 指标与日志要点规范

```
├── A17-1: 必填指标名称
│   ├── A17-1.1: 核心指标 - ninetest_requests_total、ninetest_success_rate、ninetest_calculation_duration_ms、ninetest_llm_generation_duration_ms、ninetest_accuracy_rate
│   └── A17-1.2: 指标命名规范 - 所有指标名称在README中固化，禁止私改，确保监控的一致性
├── A17-2: 必填日志字段
│   ├── A17-2.1: 核心日志字段 - request_id、module_name、operation、birth_date、duration_ms、success、retry_count及其类型和含义定义
│   └── A17-2.2: 日志格式要求 - 使用结构化JSON格式，包含时间戳、日志级别等标准字段
└── A17-3: 日志结构示例
    ├── A17-3.1: 标准日志结构 - 展示完整的日志记录结构，包含所有必填字段和扩展字段
    └── A17-3.2: 脱敏处理 - birth_date字段脱敏处理示例，保护用户隐私信息
```

------------------------------

### A18: 待补要点与未定义项

```
├── A18-1: 配置相关待补项
│   ├── A18-1.1: LLM模型版本策略 - 当前固定使用gpt-4o-2024-08-06，待补模型版本回退策略和兼容性规则，影响面：报告生成质量成本控制，保守选项：版本锁定策略/渐进升级策略/A/B测试策略
│   ├── A18-1.2: 数字频率计算边界情况 - 当前基础YYYY-MM-DD处理，待补闰年2月29日、国际日期格式兼容性处理规则，影响面：算法准确性用户体验，保守选项：严格ISO8601/本地化格式支持/智能格式识别
│   └── A18-1.3: 天赋描述本地化策略 - 当前中英双语硬编码，待补多语言扩展机制和翻译质量保证，影响面：国际化支持维护成本，保守选项：配置驱动翻译/API翻译服务/人工翻译库
├── A18-2: 性能相关待补项
│   ├── A18-2.1: 并发处理上限 - 待补单实例最大并发请求数和资源限制，影响面：系统稳定性资源消耗，保守选项：100并发限制/200并发限制/动态限制
│   └── A18-2.2: 配置缓存策略 - 待补配置更新频率和缓存失效机制，影响面：性能优化配置一致性，保守选项：5分钟TTL/15分钟TTL/手动刷新
└── A18-3: 错误处理待补项
    └── A18-3.1: LLM服务降级策略 - 待补当llm_handler_agent不可用时的Fallback机制，影响面：服务可用性用户体验，保守选项：默认模板报告/延迟重试/服务暂停
```

------------------------------

### A19: 外部I/O与状态管理约束

```
├── A19-1: 状态存取约束
│   ├── A19-1.1: 状态管理原则 - 模块不得直接访问持久化（DB/Cache/FS），必须通过指定Adapter间接访问database_agent统一管理的存储层
│   └── A19-1.2: 无状态设计 - 完全无状态设计，每次调用独立完成，不保存分析状态
├── A19-2: 副作用隔离约束
│   ├── A19-2.1: I/O限制 - 任何网络/系统I/O仅可写在Adapter，Main/Aux出现I/O视为违规
│   └── A19-2.2: 副作用控制 - 任何函数需满足幂等/可重放要求（同输入不应产生额外副作用）
├── A19-3: 并发与资源约束
│   ├── A19-3.1: 并发原语限制 - 仅允许使用语言原生异步原语（如async/await、事件循环），禁止线程池/进程池，除非在Adapter层且README明示风险与回收策略
│   └── A19-3.2: 超时与重试配置 - 必须经routing_agent的config_manager服务注入，禁止在代码内写死超时/重试参数
└── A19-4: 观测与审计约束
    ├── A19-4.1: 日志必填字段 - request_id、module_name、operation、duration_ms、success、retry_count
    ├── A19-4.2: 敏感信息处理 - 日志/错误信息不得包含密钥、令牌、身份证件、邮箱全量、手机号全量等，必要时脱敏
    └── A19-4.3: 指标暴露要求 - 至少暴露调用次数、成功率、时延分布三类指标，指标名在README固化，禁止私改
```

------------------------------

### A20: 错误与返回一致性约束

```
├── A20-1: 错误码规范约束
│   ├── A20-1.1: 命名规范 - 采用{DOMAIN}/{REASON}命名（如：AUTH/TIMEOUT、IO/UNAVAILABLE），README列明取值全集
│   └── A20-1.2: 错误码完整性 - 所有可能的错误情况都必须有对应的标准错误码
├── A20-2: 异常传播约束
│   ├── A20-2.1: 异常类型限制 - 只允许抛出仓库标准异常基类及其子类，不得抛裸异常
│   └── A20-2.2: 错误信息要求 - 错误信息需面向调用方而非实现细节
└── A20-3: 失败回退约束
    ├── A20-3.1: 回退策略 - 失败时必须返回可操作指令（如flow指令/重试建议/联系渠道），不得要求调用方自行猜测
    └── A20-3.2: 用户友好处理 - 对用户屏蔽详细错误，保留完整日志记录
```

------------------------------

### A21: 安全与合规约束

```
├── A21-1: 秘钥管理约束
│   ├── A21-1.1: 秘钥安全 - 不得在代码/README/示例中出现任何真实秘钥，仅允许读取环境变量或安全管理器的别名
│   └── A21-1.2: 配置安全 - 所有敏感配置必须通过安全渠道获取，不得硬编码
├── A21-2: 输入校验约束
│   ├── A21-2.1: 校验规则 - 所有外部输入必须显式校验（长度/类型/枚举/格式），校验规则写入README的契约章节
│   └── A21-2.2: 数据验证 - 出生日期等关键数据必须经过严格的格式和合理性验证
└── A21-3: 权限与最小化约束
    ├── A21-3.1: 权限控制 - 模块内不得提升权限，仅请求所需最小范围的权限与数据字段
    └── A21-3.2: 数据最小化 - 只处理和存储必要的数据，避免过度收集用户信息
```

------------------------------

### A22: 测试与验收约束

```
├── A22-1: 最小用例约束
│   ├── A22-1.1: 用例覆盖 - 本模块至少提供冒烟链路与失败路径两类用例，用例不得Mock掉对外契约（可Mock外设）
│   └── A22-1.2: 测试真实性 - 使用真实的出生日期数据和确定性算法验证，确保测试的有效性
├── A22-2: 验收门槛约束
│   ├── A22-2.1: 交付标准 - 生成变更必须先通过本模块用例再提交，未达门槛禁止继续生成下一文件
│   └── A22-2.2: 质量保证 - 算法验证、一致性测试、完整流程测试都是必须的验收条件
└── A22-3: 测试覆盖范围
    ├── A22-3.1: 完整流程测试 - 验证birth_date_analysis操作的端到端流程，包含AgentRequest构造、天赋分析执行、ninetest_assessment生成和字段完整性检查
    └── A22-3.2: 算法确定性测试 - 验证相同出生日期产生相同数字频率结果，确保天赋计算的稳定性和可重现性
```

------------------------------

### A23: 生成器执行规范约束

```
├── A23-1: 部分修改优先约束
│   ├── A23-1.1: 修改粒度 - 每次仅修改一个文件，≤300行；若需要新增文件，先在README标注"文件名+角色(Main/Adapter/Aux)+责任"，再生成
│   └── A23-1.2: 文件管理 - 严格按照Main/Adapter/Aux的角色分工创建和组织文件
├── A23-2: 禁止脑补约束
│   ├── A23-2.1: 信息缺失处理 - 遇到缺失信息（路径/键名/Schema字段/错误码），停止输出并在README的"待补要点"清单中列明，不得擅自发明
│   └── A23-2.2: 准确性保证 - 所有实现必须基于明确的规范和配置，不得主观推测或补充未定义的内容
├── A23-3: 依赖单向约束
│   ├── A23-3.1: 依赖方向 - Domain → Adapter单向依赖，Aux不得被跨模块引用，生成器如果检测到反向引用，直接终止
│   └── A23-3.2: 模块边界 - 严格维护模块间的边界，避免循环依赖和不当的模块引用
├── A23-4: 变更限制约束
│   ├── A23-4.1: 操作限制 - 不迁移/不重命名/不删除，除非README的"迁移方案"明确列出变更映射
│   └── A23-4.2: 公共层限制 - 不新增公共层，任何"utils/common/shared"目录新增一律拒绝，确有必要需先在顶层规范中建制并评审
└── A23-5: 关键词黑名单约束
    ├── A23-5.1: 禁止本地业务模型定义 - "class .*Model"、"data class .*"、"interface .*DTO"
    ├── A23-5.2: 禁止硬编码配置 - "API_KEY="、"timeout\\s*=\\s*\\d+"、"retry\\s*=\\s*\\d+"
    ├── A23-5.3: 禁止跨层I/O - 在Main/Aux中出现"http"、"db"、"sql"、"open("、"requests"、"fetch"
    ├── A23-5.4: 禁止并发越界 - "Thread"、"Process"、"fork"、"Pool"
    └── A23-5.5: 禁止未脱敏日志 - "print("、"console.log("、"logging.info(f\\".*password|token|secret"
```

------------------------------

## 📋 文档骨架构建完成

本结构化文档骨架已完整覆盖ninetest_agent原始README文档中的所有信息类型和分类，包括：

✅ **已覆盖的主要内容类别**：
- 开发边界限制与规范约束 (B1-B14完整覆盖)
- 模块定义、功能特性、接入说明
- 系统架构、技术规范、配置管理
- 运行流程、天赋评估体系、数据结构
- 接口契约、协作机制、错误处理
- 术语定义、依赖关系、重大决策
- 指标日志、测试验收、待补要点

✅ **结构化组织特点**：
- 采用A1-A23编号系统，树状层级结构清晰
- 每个编号下内容用代码块包裹
- 编号间使用30个连字符分隔
- 保留所有原文信息，未定义项已标注
- 适用于Step 2的内容补全输入

该骨架文件已创建完成，为后续的内容补全和开发任务分解提供了完整的结构化基础。
