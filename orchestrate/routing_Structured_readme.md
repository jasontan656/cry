# routing_agent_Structured_readme.md

## 文档骨架提取 - 任务控制中枢结构重建

---

### A: 开发边界与职责说明

```
├── A-1: 模块基本定义
│   └── routing_agent是Career Bot系统的任务控制中枢（Task Control Center, TCC），是所有后端功能Agent的调度核心。它不处理具体业务逻辑，仅负责任务调度、Agent协调、状态追踪与任务链闭环控制，同时作为全局配置管理者统一管理global_config。
├── A-2: 核心功能特性  
│   ├── A-2.1: 任务控制中枢能力
│   │   ├── A-2.1.1: 任务调度分发 - 统一管理所有Agent间的协作
│   │   ├── A-2.1.2: 状态追踪管理 - 支持复杂多步骤对话流程状态
│   │   ├── A-2.1.3: 任务链控制 - 闭环控制确保流程完整性
│   │   └── A-2.1.4: Agent协调 - 确保Agent间严格隔离和松耦合架构
│   ├── A-2.2: 双核心业务路径支持
│   │   ├── A-2.2.1: 求职者路径管理 - 完整支持人才测试环节状态管理
│   │   ├── A-2.2.2: 企业招聘路径管理 - 企业验证状态管理和多公司支持
│   │   ├── A-2.2.3: 管理员后台路由 - 支持管理员功能路由控制
│   │   └── A-2.2.4: 跨路径状态同步 - 断点续传和跨设备对话恢复
│   └── A-2.3: 全局配置管理职责
│       ├── A-2.3.1: 配置唯一管理者 - 作为global_config的唯一管理和分发中心
│       ├── A-2.3.2: 配置热更新协调 - 配置变更时协调所有Agent缓存刷新
│       ├── A-2.3.3: 配置版本控制 - 配置版本管理和安全回滚机制
│       └── A-2.3.4: 环境差异化管理 - 开发测试生产环境配置差异化
├── A-3: 职责边界限制
│   ├── A-3.1: 专注职责 - 专注对话状态管理、任务调度、意图路由、Agent协调
│   ├── A-3.2: 不涉及业务处理 - 不涉及任何具体业务处理逻辑
│   ├── A-3.3: 新增职责边界 - 对话流程断点续传、用户注册完成度跟踪、企业验证状态管理
│   └── A-3.4: 统一错误处理 - 协调所有Agent的错误信息统一格式和支持邮件模板
```

------------------------------

### B: 系统架构与模块定义

```
├── B-1: 模块依赖关系结构
│   ├── B-1.1: 上游触发源
│   │   ├── B-1.1.1: entry_agent - 唯一调用来源，提供用户意图和对话请求
│   │   ├── B-1.1.2: 用户交互 - 通过frontend_service_agent接收用户输入
│   │   ├── B-1.1.3: 系统启动 - boot系统启动时的Agent装配和注册管理
│   │   └── B-1.1.4: 配置变更 - 外部配置系统的热更新触发
│   ├── B-1.2: 下游调用目标
│   │   ├── B-1.2.1: 所有业务Agent - 作为唯一调度中枢协调任务分发
│   │   ├── B-1.2.2: auth_agent - 用户身份验证和双身份状态管理
│   │   ├── B-1.2.3: database_agent - 对话状态存储用户数据查询配置缓存
│   │   ├── B-1.2.4: matching_agent - 搜索任务调度和结果协调
│   │   ├── B-1.2.5: company_identity_agent - 企业验证流程协调
│   │   └── B-1.2.6: mail_agent - 通知邮件发送任务调度
│   ├── B-1.3: 数据约束管理
│   │   ├── B-1.3.1: 对话状态完整性 - 确保跨Agent调用中状态完整传递
│   │   ├── B-1.3.2: 双身份路由 - 根据用户当前激活身份的不同路由策略
│   │   ├── B-1.3.3: 企业多公司协调 - 多企业用户的公司选择和任务分发
│   │   └── B-1.3.4: 配置一致性 - 确保所有Agent获得一致配置参数
│   └── B-1.4: 并发控制机制
│       ├── B-1.4.1: 串行状态管理 - 同一用户对话状态更新严格串行
│       ├── B-1.4.2: 并发任务调度 - 支持跨用户的并发任务处理
│       ├── B-1.4.3: Agent实例管理 - 管理各Agent实例生命周期和负载均衡
│       └── B-1.4.4: 熔断保护 - 对异常Agent实施熔断保护机制
├── B-2: 系统架构位置定义
│   ├── B-2.1: 架构层次关系
│   │   └── entry_agent → [routing_agent (任务控制中枢)] → Specialized agents
│   ├── B-2.2: 上下游关系
│   │   ├── B-2.2.1: 上游 - entry_agent（唯一请求来源）
│   │   ├── B-2.2.2: 下游 - 所有业务Agent（auth_agent、database_agent、llm_handler_agent等）
│   │   └── B-2.2.3: 配置客户 - 所有Agent都从routing_agent获取配置
│   └── B-2.3: 配置分发架构
│       └── global_config (配置管理) → 所有模块 ← 配置分发
```

------------------------------

### C: 输入输出规范、配置机制、模型路径、调用方式

```
├── C-1: 输入输出数据规范
│   ├── C-1.1: 标准AgentRequest输入结构
│   │   ├── C-1.1.1: 基础字段 - request_id, task_type, user_id, session_id, timestamp
│   │   ├── C-1.1.2: 核心数据 - context.data包含message, intent, current_stage
│   │   ├── C-1.1.3: 元数据 - context.metadata包含source_agent, priority, retry_count
│   │   └── C-1.1.4: 调度参数 - additional_params包含timeout_seconds, max_retries, enable_circuit_breaker
│   ├── C-1.2: 标准AgentResponse输出结构
│   │   ├── C-1.2.1: 响应基础 - request_id, agent_name, success, timestamp
│   │   ├── C-1.2.2: 调度结果 - response.results包含dispatched_tasks, task_chain_status
│   │   ├── C-1.2.3: 流程控制 - next_intents, flow_directive指令
│   │   └── C-1.2.4: 错误信息 - error字段（成功时为null）
│   └── C-1.3: 任务调度流程控制指令
│       ├── C-1.3.1: continue_chain - 继续派发next_intents到目标Agent
│       ├── C-1.3.2: return_to_entry - 任务完成，结果返回给entry_agent
│       ├── C-1.3.3: finish - 任务链闭环，流程结束
│       └── C-1.3.4: retry - 任务失败，根据重试策略重新调度
├── C-2: routing_agent配置管理职责定义
│   ├── ⚠️ 职责边界澄清：global_config.json仅为配置文件载体，routing_agent是配置管理执行者
│   ├── C-2.1: routing_agent作为配置管理者的核心职责
│   │   ├── C-2.1.1: 配置存储管理 - routing_agent负责从global_config.json文件加载配置并建立内存缓存机制
│   │   ├── C-2.1.2: 配置加载机制 - routing_agent在系统启动时主动读取global_config.json并解析为配置对象
│   │   ├── C-2.1.3: 模块配置分发 - routing_agent通过get_config()方法为其他Agent提供配置数据服务
│   │   ├── C-2.1.4: Schema管理与分发 - routing_agent从global_schemas.json加载字段定义，动态生成Pydantic模型，通过get_schema()方法分发给各Agent
│   │   └── C-2.1.5: 配置热更新 - routing_agent检测global_config.json和global_schemas.json变更并通知相关Agent刷新缓存
│   ├── C-2.2: routing_agent管理的配置分类体系
│   │   ├── ⚠️ 配置源：global_config.json（配置数据）+ global_schemas.json（字段schema定义）
│   │   ├── C-2.2.1: module_registry - routing_agent维护所有模块的注册信息配置
│   │   ├── C-2.2.2: intent_mapping - routing_agent管理Intent到模块的映射规则配置
│   │   ├── C-2.2.3: timeout_config - routing_agent分发各种操作的超时设置配置
│   │   ├── C-2.2.4: retry_config - routing_agent提供重试策略和次数配置
│   │   └── C-2.2.5: circuit_breaker_config - routing_agent控制熔断器参数设置配置
│   └── C-2.3: routing_agent的Agent注册与管理机制
│       ├── C-2.3.1: 注册信息管理 - routing_agent维护agent_path, supported_tasks, instance, status等注册信息
│       ├── C-2.3.2: 健康检查协调 - routing_agent主动发起模块健康状态检查并维护健康状态记录
│       ├── C-2.3.3: 实例生命周期管理 - routing_agent负责Agent实例的创建、缓存和回收策略
│       └── C-2.3.4: 负载均衡决策 - routing_agent基于配置执行round_robin等负载均衡算法
├── C-3: Schema管理与模型分发机制
│   ├── C-3.1: Schema集中化管理
│   │   ├── C-3.1.1: JSON定义源 - 所有字段定义存储在global_schemas.json，由routing_agent统一管理
│   │   ├── C-3.1.2: 动态生成模型 - routing_agent启动时从JSON生成Pydantic V2模型类
│   │   ├── C-3.1.3: Schema分发 - 通过get_schema(model_name)接口向各Agent分发模型定义
│   │   └── C-3.1.4: 版本控制 - Schema变更支持版本控制和向下兼容
│   ├── C-3.2: Pydantic V2规范
│   │   ├── C-3.2.1: 必须使用 - model_validate(), model_dump(), Field(), BaseModel
│   │   ├── C-3.2.2: 严禁使用 - .dict(), .parse_obj(), .json(), parse_obj_as()
│   │   ├── C-3.2.3: 字段验证 - 必须使用pattern=r"regex"，严禁regex=r"regex"
│   │   └── C-3.2.4: 统一验证 - routing_agent提供validate_model(data, model_name)统一验证服务
│   └── C-3.3: 异步处理规范
│       ├── C-3.3.1: 必须使用 - 所有任务调度方法使用async def
│       ├── C-3.3.2: 禁止使用 - 同步阻塞操作、threading、multiprocessing
│       ├── C-3.3.3: 并发控制 - 使用asyncio.create_task(), asyncio.gather()
│       └── C-3.3.4: 异常处理 - TaskExecutionError, AgentNotFoundError, ConfigurationError
│   └── C-3.4: 任务调度调用方式
│       ├── C-3.4.1: 唯一通道 - 系统中所有跨模块调用的唯一通道
│       ├── C-3.4.2: 严禁直接调用 - 模块间禁止直接import或调用
│       ├── C-3.4.3: 调度机制 - 基于intent_mapping进行任务分发
│       └── C-3.4.4: 任务链支持 - 支持复合任务的拆解和串行并行执行
```

------------------------------

### D: 用户流程、对话流程、意图识别机制

```
├── D-1: 核心对话路径状态管理
│   ├── D-1.1: 求职者路径状态编排
│   │   ├── D-1.1.1: welcome状态 - next_states: login_required, user_status_detection
│   │   ├── D-1.1.2: first_time_intro状态 - next_states: mbti_introduction
│   │   ├── D-1.1.3: mbti_introduction状态 - next_states: mbti_result_selection
│   │   ├── D-1.1.4: mbti_result_selection状态 - next_states: four_dimension_intro
│   │   ├── D-1.1.5: four_dimension_test状态 - next_states: four_dimension_analysis
│   │   ├── D-1.1.6: four_dimension_analysis状态 - next_states: birthday_input
│   │   ├── D-1.1.7: talent_test状态 - next_states: resume_upload
│   │   ├── D-1.1.8: resume_upload状态 - next_states: registration_completion, resume_upload_retry
│   │   ├── D-1.1.9: registration_completion状态 - next_states: comprehensive_analysis
│   │   ├── D-1.1.10: comprehensive_analysis状态 - next_states: completion_waiting
│   │   └── D-1.1.11: completion_waiting状态 - 终态，无后续状态
│   ├── D-1.2: 企业招聘路径状态编排
│   │   ├── D-1.2.1: company_intro状态 - next_states: sample_resume_preview, company_verification_intro
│   │   ├── D-1.2.2: sample_resume_preview状态 - next_states: company_verification_intro
│   │   ├── D-1.2.3: company_verification_intro状态 - next_states: document_upload
│   │   ├── D-1.2.4: document_upload状态 - next_states: multi_company_selection, company_verified_dashboard, document_upload_retry
│   │   ├── D-1.2.5: company_verified_dashboard状态 - next_states: candidate_search, job_posting, job_management
│   │   ├── D-1.2.6: candidate_search状态 - next_states: search_results
│   │   ├── D-1.2.7: job_posting状态 - next_states: company_verified_dashboard, job_posting_retry
│   │   └── D-1.2.8: job_posting_retry状态 - next_states: company_verified_dashboard, job_posting_retry
│   ├── D-1.3: 人才测试环节状态编排（求职者路径子流程）
│   │   ├── D-1.3.1: talent_test_intro状态 - next_states: login_required, mbti_introduction
│   │   ├── D-1.3.2: independent_test_results状态 - next_states: conversion_prompt
│   │   └── D-1.3.3: conversion_prompt状态 - next_states: resume_upload, test_completion
│   └── D-1.4: 管理员路径状态编排
│       ├── D-1.4.1: admin_console_entry状态 - next_states: admin_dashboard, permission_denied
│       ├── D-1.4.2: admin_dashboard状态 - next_states: credit_management, role_management, company_verification_review, tag_audit, admin_operation_logs
│       ├── D-1.4.3: credit_management状态 - next_states: credit_operation_form, admin_dashboard
│       ├── D-1.4.4: credit_operation_form状态 - next_states: credit_operation_success, credit_operation_failed
│       ├── D-1.4.5: role_management状态 - next_states: role_operation_form, admin_dashboard
│       ├── D-1.4.6: role_operation_form状态 - next_states: role_operation_success, role_operation_failed
│       ├── D-1.4.7: company_verification_review状态 - next_states: verification_decision, admin_dashboard
│       ├── D-1.4.8: tag_audit状态 - next_states: tag_audit_action, admin_dashboard
│       └── D-1.4.9: admin_operation_logs状态 - next_states: admin_dashboard
├── D-2: 跨Agent协作编排机制
│   ├── D-2.1: 对话状态追踪与恢复
│   │   ├── D-2.1.1: 获取用户当前状态 - current_path, current_stage, completed_steps, pending_info, session_data
│   │   ├── D-2.1.2: 更新用户状态 - user_id, new_state, data同步到database_agent
│   │   └── D-2.1.3: 检查注册完成度 - 包含required_fields检查和missing_fields统计
│   ├── D-2.2: 企业验证状态管理
│   │   ├── D-2.2.1: 处理企业验证文档 - multiple_companies_detected检测和处理
│   │   ├── D-2.2.2: 企业验证失败处理 - 统一错误处理机制和支持邮件模板
│   │   └── D-2.2.3: 获取用户已验证公司列表 - 通过database_agent获取
│   ├── D-2.3: 简历处理失败管理
│   │   ├── D-2.3.1: 简历解析失败处理 - 统一错误响应和重试机制
│   │   └── D-2.3.2: 支持邮件模板集成 - 包含filename, filesize等错误上下文
│   └── D-2.4: 职位发布处理管理
│       ├── D-2.4.1: 职位发布解析失败处理 - 统一错误响应机制
│       └── D-2.4.2: 职位发布重试机制 - job_posting_retry状态支持
├── D-3: 意图识别与路由机制
│   ├── D-3.1: 意图解析与模块匹配
│   │   ├── D-3.1.1: intent_mapping配置 - Intent到模块的映射关系
│   │   ├── D-3.1.2: 模式匹配 - 支持通配符模式和精确匹配
│   │   ├── D-3.1.3: 动态路由 - 根据用户状态和身份进行动态路由
│   │   └── D-3.1.4: 错误处理 - 未找到匹配Agent时的处理机制
│   ├── D-3.2: 任务分发与执行
│   │   ├── D-3.2.1: 获取目标模块实例 - 从AGENT_REGISTRY获取
│   │   ├── D-3.2.2: 任务执行监控 - 包含超时控制和性能监控
│   │   ├── D-3.2.3: 执行结果记录 - 记录执行时间和成功状态
│   │   └── D-3.2.4: 异常处理机制 - 超时和执行失败的处理
│   └── D-3.3: 任务链管理与闭环控制
│       ├── D-3.3.1: 任务链处理 - 基于flow_directive的链式执行
│       ├── D-3.3.2: 后续任务调度 - next_intents的迭代处理
│       ├── D-3.3.3: 链式执行控制 - continue_chain指令的循环控制
│       └── D-3.3.4: 任务链结束 - 链式执行的结束条件判断
```

------------------------------

### E: 接口结构、状态管理、日志与异常策略

```
├── E-1: 接口结构完整定义
│   ├── E-1.1: 核心接口规范
│   │   ├── E-1.1.1: 统一入口接口 - run(request: AgentRequest) -> AgentResponse
│   │   ├── E-1.1.2: 参数规范 - request_id, task_type, context, additional_params
│   │   ├── E-1.1.3: 返回值规范 - request_id, agent_name, success, timestamp, response, error
│   │   └── E-1.1.4: 异常规范 - TaskExecutionError, AgentNotFoundError, ConfigurationError
│   ├── E-1.2: 支持的任务类型
│   │   ├── E-1.2.1: dispatch_task - 将任务分发给目标模块
│   │   ├── E-1.2.2: get_config - 获取模块配置信息
│   │   ├── E-1.2.3: register_agent - 注册新模块
│   │   ├── E-1.2.4: health_check - 模块健康状态检查
│   │   └── E-1.2.5: get_agent_status - 获取模块运行状态
│   ├── E-1.3: 错误码规范
│   │   ├── E-1.3.1: ROUTING前缀错误码 - AGENT_NOT_FOUND, TIMEOUT, TASK_EXECUTION_FAILED等
│   │   ├── E-1.3.2: CONFIG前缀错误码 - NOT_FOUND, INVALID_FORMAT, LOAD_FAILED等
│   │   ├── E-1.3.3: 错误码格式 - ROUTING/{REASON}命名格式
│   │   └── E-1.3.4: 错误码完整清单 - 所有标准错误码的定义和说明
│   └── E-1.4: 配置依赖接口
│       ├── E-1.4.1: 配置提供服务 - module_registry, intent_mapping, timeout_config等
│       ├── E-1.4.2: 配置获取接口 - get_config(module_name, config_type)
│       ├── E-1.4.3: Schema分发接口 - get_schema(model_name) -> dict, validate_model(data, model_name) -> bool
│       ├── E-1.4.4: 必须依赖模块 - global_schemas.json, global_config.json, 所有业务模块
│       └── E-1.4.5: 被依赖关系 - 所有其他模块的配置、Schema和跨模块调用依赖
├── E-2: 状态管理完整机制
│   ├── E-2.1: 对话状态管理字段
│   │   ├── E-2.1.1: 对话路径字段 - current_dialogue_path, dialogue_stage, completed_steps等
│   │   ├── E-2.1.2: 状态同步字段 - cross_device_sync, last_active_device, state_version
│   │   ├── E-2.1.3: 断点恢复数据 - checkpoint_data用于流程恢复
│   │   └── E-2.1.4: 待完成动作 - pending_actions列表管理
│   ├── E-2.2: 双身份路由字段
│   │   ├── E-2.2.1: 身份路由配置 - identity_routing_rules, default_identity_behavior等
│   │   ├── E-2.2.2: 路由状态字段 - current_active_identity, identity_permissions等
│   │   ├── E-2.2.3: 身份切换控制 - identity_switch_enabled开关
│   │   └── E-2.2.4: 路由上下文 - routing_context数据传递
│   ├── E-2.3: 任务调度配置字段
│   │   ├── E-2.3.1: 调度控制配置 - task_timeout_seconds, max_concurrent_tasks等
│   │   ├── E-2.3.2: 性能监控字段 - task_execution_stats, agent_response_times等
│   │   ├── E-2.3.3: 重试策略配置 - retry_policy详细配置
│   │   └── E-2.3.4: 熔断器控制 - circuit_breaker_enabled开关
│   └── E-2.4: 企业多公司协调字段
│       ├── E-2.4.1: 多公司管理 - company_selection_state, multi_company_routing等
│       ├── E-2.4.2: 企业验证协调 - verification_workflow_state, document_processing_queue等
│       ├── E-2.4.3: 公司切换历史 - company_switch_history记录
│       └── E-2.4.4: 验证重试配置 - verification_retry_config参数
├── E-3: 日志记录完整规范
│   ├── E-3.1: 日志框架规范
│   │   ├── E-3.1.1: 日志框架 - 使用Python标准logging模块
│   │   ├── E-3.1.2: 必要字段 - request_id, agent_name, target_agent, task_type, duration
│   │   ├── E-3.1.3: 追踪支持 - request_id贯穿整个任务调度链
│   │   └── E-3.1.4: 性能监控 - 记录任务分发时间、执行时间、成功率
│   ├── E-3.2: 日志必填字段规范
│   │   ├── E-3.2.1: 基础追踪字段 - request_id, module_name, operation
│   │   ├── E-3.2.2: 性能字段 - duration_ms, success, retry_count
│   │   ├── E-3.2.3: 敏感信息处理 - 不得包含密钥、令牌、身份证件等
│   │   └── E-3.2.4: 脱敏要求 - 邮箱全量、手机号全量等必要时脱敏
│   └── E-3.3: 性能指标规范
│       ├── E-3.3.1: 必须暴露指标 - routing_agent_requests_total等三类指标
│       ├── E-3.3.2: 模块特定指标 - routing_agent_dispatch_total等调度指标
│       ├── E-3.3.3: 指标命名规范 - 统一的指标命名约定
│       └── E-3.3.4: 指标数据格式 - 调用次数、成功率、时延分布
├── E-4: 异常处理与对话流程恢复策略
│   ├── E-4.1: 异常类型定义
│   │   ├── E-4.1.1: TaskExecutionError - 任务执行失败异常
│   │   ├── E-4.1.2: AgentNotFoundError - Agent不存在异常  
│   │   ├── E-4.1.3: ConfigurationError - 配置错误异常
│   │   └── E-4.1.4: ServiceUnavailableError - 服务不可用异常
│   ├── E-4.2: 异常传播机制
│   │   ├── E-4.2.1: 向entry_agent传播 - 提供详细错误上下文
│   │   ├── E-4.2.2: 熔断机制 - Agent调用失败超过阈值时触发熔断
│   │   ├── E-4.2.3: 验证失败协调 - Agent返回验证失败时的统一处理
│   │   └── E-4.2.4: 对话状态保护 - 验证失败时维护完整对话上下文
│   ├── E-4.3: 错误恢复与重试策略
│   │   ├── E-4.3.1: 重试配置 - max_retries, retry_delay_seconds, exponential_backoff
│   │   ├── E-4.3.2: 可重试错误 - TimeoutError, ServiceUnavailableError等
│   │   ├── E-4.3.3: 不可重试错误 - ValidationError, AuthenticationError等
│   │   └── E-4.3.4: 重试延迟控制 - 指数退避和抖动机制
│   └── E-4.4: 技术支持集成
│       ├── E-4.4.1: 支持邮件模板 - support@4waysgroup.com邮件模板
│       ├── E-4.4.2: 跨Agent一致性 - 确保错误处理模板的一致性
│       ├── E-4.4.3: 错误上下文收集 - 包含模块名、错误类别、错误码等
│       └── E-4.4.4: 用户友好提示 - 提供可操作的解决方案指导
```

------------------------------

### F: Agent调度映射与依赖关系

```
├── F-1: 核心Agent调度映射
│   ├── F-1.1: entry_agent → routing_agent → 业务Agent调度链
│   ├── F-1.2: llm_handler_agent调度映射 - 支持"llm_*"模式的intent映射
│   ├── F-1.3: database_agent调度映射 - 所有数据存储操作调度
│   ├── F-1.4: mail_agent调度映射 - 邮件发送任务调度
│   └── F-1.5: 文件处理类Agent调度映射 - resume_agent、jobpost_agent、company_identity_agent
└── F-2: Agent依赖关系管理
    ├── F-2.1: 上游依赖 - entry_agent作为唯一调度入口
    ├── F-2.2: 下游依赖 - 业务Agent集群的依赖协调
    ├── F-2.3: 横向依赖 - Agent间协作关系管理
    └── F-2.4: 配置依赖 - global_config和global_schemas统一依赖
```

------------------------------

### G: 环境配置、运行要求、版本依赖、模块限制

```
├── H-1: 环境配置完整要求
│   ├── H-1.1: Python版本要求
│   │   ├── H-1.1.1: Python 3.10+ - 强制要求，用于异步特性支持
│   │   ├── H-1.1.2: asyncio内置支持 - Python 3.10内置异步框架
│   │   ├── H-1.1.3: 类型提示支持 - 完整的类型提示和泛型支持
│   │   └── H-1.1.4: 标准库依赖 - logging, time等标准库模块
│   ├── H-1.2: 核心依赖模块
│   │   ├── H-1.2.1: global_schemas.json - 全局数据模型JSON定义文件，由routing_agent动态加载和分发
│   │   ├── H-1.2.2: global_config - 全局配置数据源依赖
│   │   ├── H-1.2.3: pydantic>=2.0.0 - 数据验证和序列化框架
│   │   └── H-1.2.4: 第三方库版本 - 严格的版本依赖控制
│   ├── H-1.3: 系统资源要求
│   │   ├── H-1.3.1: 内存要求 - 1GB+内存（任务调度中心）
│   │   ├── H-1.3.2: CPU要求 - 2核+CPU（并发任务处理）
│   │   ├── H-1.3.3: 存储要求 - 配置文件和日志存储空间
│   │   └── H-1.3.4: 网络要求 - Agent间通信网络连接
│   └── H-1.4: 运行环境配置
│       ├── H-1.4.1: 环境变量配置 - GLOBAL_CONFIG_PATH等关键环境变量
│       ├── H-1.4.2: 配置文件路径 - global_config.json文件位置
│       ├── H-1.4.3: 日志配置 - 日志级别和输出路径配置
│       └── H-1.4.4: 服务端口配置 - Agent间通信端口设置
├── H-2: 版本依赖与兼容性
│   ├── H-2.1: Pydantic版本规范
│   │   ├── H-2.1.1: Pydantic V2强制 - 必须使用Pydantic 2.0+版本
│   │   ├── H-2.1.2: API兼容性 - 严禁使用V1 API (.dict(), .parse_obj()等)
│   │   ├── H-2.1.3: 字段验证语法 - pattern=r"regex"而非regex=r"regex"
│   │   └── H-2.1.4: 模型定义规范 - routing_agent从global_schemas.json动态生成并分发Pydantic模型
│   ├── H-2.2: 异步框架版本
│   │   ├── H-2.2.1: asyncio版本 - Python 3.10+内置版本
│   │   ├── H-2.2.2: 异步库兼容 - 与其他异步库的兼容性要求
│   │   ├── H-2.2.3: 事件循环管理 - 统一的事件循环管理策略
│   │   └── H-2.2.4: 异步上下文 - 异步上下文管理器的使用规范
│   ├── H-2.3: Agent依赖版本
│   │   ├── H-2.3.1: 所有业务Agent - 必须兼容routing_agent接口
│   │   ├── H-2.3.2: 接口版本控制 - Agent接口的版本兼容性管理
│   │   ├── H-2.3.3: 配置版本同步 - 配置格式的向下兼容性
│   │   └── H-2.3.4: 协议版本管理 - AgentRequest/AgentResponse协议版本
│   └── H-2.4: 系统集成版本
│       ├── H-2.4.1: 数据库版本 - MongoDB等数据库版本要求
│       ├── H-2.4.2: 缓存系统版本 - Redis等缓存系统版本要求  
│       ├── H-2.4.3: 消息队列版本 - 如使用消息队列的版本要求
│       └── H-2.4.4: 监控系统版本 - 日志和监控系统版本要求
├── H-3: 模块限制与约束
│   ├── H-3.1: 性能边界约束
│   │   ├── H-3.1.1: 并发限制 - 最大500个并发任务调度
│   │   ├── H-3.1.2: 任务队列限制 - 每个优先级队列最大1000个任务
│   │   ├── H-3.1.3: 响应时间约束 - 任务分发延迟 < 10ms
│   │   └── H-3.1.4: 任务链长度限制 - 最大10个串行任务，防止死循环
│   ├── H-3.2: 资源使用限制
│   │   ├── H-3.2.1: 内存使用限制 - 配置缓存和任务队列内存控制
│   │   ├── H-3.2.2: CPU使用限制 - 任务调度的CPU使用率控制
│   │   ├── H-3.2.3: 网络连接限制 - Agent间连接数量限制
│   │   └── H-3.2.4: 文件描述符限制 - 系统文件句柄使用限制
│   ├── H-3.3: 安全与权限限制
│   │   ├── H-3.3.1: 模块隔离 - 严格的模块间隔离，防止直接调用
│   │   ├── H-3.3.2: 权限验证 - 验证任务调度的权限和合法性
│   │   ├── H-3.3.3: 熔断保护 - 故障模块的熔断器保护机制
│   │   └── H-3.3.4: 输入校验 - 所有外部输入的严格校验要求
│   └── H-3.4: 开发边界限制
│       ├── H-3.4.1: 文件系统边界 - 仅允许在routing_agent/目录内操作
│       ├── H-3.4.2: 职责分层边界 - Main/Adapter/Aux的职责严格分离
│       ├── H-3.4.3: 配置来源限制 - 配置必须来自global_config，禁止本地硬编码
│       └── H-3.4.4: 副作用隔离 - 网络/系统I/O仅可写在Adapter层
```

------------------------------

### H: 测试策略、验收机制、部署策略、未来规划

```
├── I-1: 测试策略完整定义
│   ├── I-1.1: 生产级测试要求
│   │   ├── I-1.1.1: 真实模块测试 - 测试时加载真实agent模块，不使用Mock
│   │   ├── I-1.1.2: 完整调度链测试 - 测试完整的任务分发和结果汇总流程
│   │   ├── I-1.1.3: 配置集成测试 - 使用真实global_config配置进行测试
│   │   └── I-1.1.4: 端到端测试 - 完整业务流程的端到端测试覆盖
│   ├── I-1.2: 关键测试用例设计
│   │   ├── I-1.2.1: 任务调度链测试 - 完整任务调度链的功能测试
│   │   ├── I-1.2.2: 熔断器测试 - 熔断器保护机制的测试验证
│   │   ├── I-1.2.3: 配置管理测试 - 配置获取和热更新的测试
│   │   ├── I-1.2.4: 并发处理测试 - 高并发场景下的性能测试
│   │   ├── I-1.2.5: 错误处理测试 - 各种异常情况的处理测试
│   │   └── I-1.2.6: 状态恢复测试 - 对话状态断点续传功能测试
│   ├── I-1.3: 性能测试策略
│   │   ├── I-1.3.1: 负载测试 - 500+并发任务调度的负载测试
│   │   ├── I-1.3.2: 响应时间测试 - 95%任务调度 < 50ms的性能测试
│   │   ├── I-1.3.3: 内存泄漏测试 - 长时间运行的内存泄漏检测
│   │   └── I-1.3.4: 稳定性测试 - 7×24小时稳定性测试
│   └── I-1.4: 测试环境管理
│       ├── I-1.4.1: 测试数据准备 - 测试用配置和数据的准备
│       ├── I-1.4.2: 测试环境隔离 - 开发测试生产环境的隔离
│       ├── I-1.4.3: 自动化测试 - CI/CD流程中的自动化测试集成
│       └── I-1.4.4: 回归测试 - 版本更新后的回归测试策略
├── I-2: 验收机制完整定义
│   ├── I-2.1: 功能验收标准
│   │   ├── I-2.1.1: 任务调度功能 - 所有Agent的任务调度正常运行
│   │   ├── I-2.1.2: 配置管理功能 - 配置获取分发和热更新正常
│   │   ├── I-2.1.3: 状态管理功能 - 对话状态追踪和恢复正常
│   │   ├── I-2.1.4: 错误处理功能 - 异常处理和重试机制正常
│   │   └── I-2.1.5: 双路径支持 - 求职者和企业路径功能完整
│   ├── I-2.2: 性能验收标准
│   │   ├── I-2.2.1: 可用性 - 99.95%服务可用性（高于业务模块）
│   │   ├── I-2.2.2: 响应时间 - 95%任务调度 < 50ms
│   │   ├── I-2.2.3: 并发能力 - 支持500+并发任务调度
│   │   └── I-2.2.4: 配置管理 - 配置热更新零停机时间
│   ├── I-2.3: 安全验收标准
│   │   ├── I-2.3.1: 模块隔离 - Agent间严格隔离无直接调用
│   │   ├── I-2.3.2: 权限控制 - 任务调度权限验证机制有效
│   │   ├── I-2.3.3: 数据安全 - 敏感信息脱敏和加密处理
│   │   └── I-2.3.4: 熔断保护 - 故障模块熔断机制有效
│   └── I-2.4: 验收流程管理
│       ├── I-2.4.1: 验收清单 - global_config加载成功等验收项目
│       ├── I-2.4.2: 验收环境 - 独立的验收测试环境准备
│       ├── I-2.4.3: 验收报告 - 详细的验收测试结果报告
│       └── I-2.4.4: 问题跟踪 - 验收过程中发现问题的跟踪处理
├── I-3: 部署策略完整定义
│   ├── I-3.1: 部署环境准备
│   │   ├── I-3.1.1: 环境要求检查 - Python 3.10+, 内存1GB+, CPU 2核+
│   │   ├── I-3.1.2: 依赖安装 - global_schemas, global_config等核心依赖
│   │   ├── I-3.1.3: 配置文件部署 - global_config.json等配置文件部署
│   │   └── I-3.1.4: 环境变量设置 - GLOBAL_CONFIG_PATH等环境变量配置
│   ├── I-3.2: 部署流程管理
│   │   ├── I-3.2.1: 蓝绿部署 - 零停机的蓝绿部署策略
│   │   ├── I-3.2.2: 滚动升级 - 分批次的滚动升级策略
│   │   ├── I-3.2.3: 回滚策略 - 快速回滚到上一个稳定版本
│   │   └── I-3.2.4: 健康检查 - 部署后的健康检查和验证
│   ├── I-3.3: 监控与运维
│   │   ├── I-3.3.1: 监控指标 - 任务吞吐量、响应时间、成功率等指标
│   │   ├── I-3.3.2: 日志管理 - 统一的日志收集和分析
│   │   ├── I-3.3.3: 告警机制 - 异常情况的及时告警通知
│   │   └── I-3.3.4: 运维工具 - 自动化运维工具和脚本
│   └── I-3.4: 容灾与备份
│       ├── I-3.4.1: 数据备份 - 配置和状态数据的定期备份
│       ├── I-3.4.2: 服务容灾 - 多节点部署和故障切换
│       ├── I-3.4.3: 配置备份 - 配置版本的备份和恢复
│       └── I-3.4.4: 应急预案 - 突发故障的应急处理预案

```

------------------------------

### I: 模块运转机制与任务调度实现

```
├── J-1: 完整任务调度链路实现
│   ├── J-1.1: 任务接收与验证
│   │   ├── J-1.1.1: run方法入口 - async def run(request: AgentRequest) -> AgentResponse
│   │   ├── J-1.1.2: 请求格式验证 - _validate_request(request)验证
│   │   ├── J-1.1.3: 任务信息提取 - task_type, intent, user_id等信息提取
│   │   └── J-1.1.4: 日志上下文设置 - request_id, task_type, user_id日志记录
│   ├── J-1.2: 意图解析与模块匹配
│   │   ├── J-1.2.1: resolve_intent_to_agent方法 - 意图到Agent的映射解析
│   │   ├── J-1.2.2: intent_mapping配置获取 - 从global_config获取映射配置
│   │   ├── J-1.2.3: 模式匹配算法 - 支持通配符(*)和精确匹配
│   │   └── J-1.2.4: 异常处理 - 未找到匹配Agent时抛出TaskExecutionError
│   ├── J-1.3: 任务分发与执行
│   │   ├── J-1.3.1: dispatch_task方法 - 标准任务分发实现
│   │   ├── J-1.3.2: Agent实例获取 - _get_agent_instance获取目标Agent
│   │   ├── J-1.3.3: 超时控制 - asyncio.wait_for实现超时控制
│   │   ├── J-1.3.4: 执行时间统计 - start_time和execution_time计算
│   │   └── J-1.3.5: 结果日志记录 - target_agent, execution_time_ms, success记录
│   └── J-1.4: 任务链管理与闭环控制
│       ├── J-1.4.1: handle_task_chain方法 - 任务链处理实现
│       ├── J-1.4.2: 流程控制判断 - flow_directive的continue_chain判断
│       ├── J-1.4.3: 后续任务迭代 - next_intents的循环处理
│       └── J-1.4.4: 任务链终止 - 链式执行的结束条件控制
├── J-2: 模块注册与管理机制
│   ├── J-2.1: 模块注册表管理
│   │   ├── J-2.1.1: ModuleRegistry类 - Agent注册信息管理
│   │   ├── J-2.1.2: register_agent方法 - 新模块注册实现
│   │   ├── J-2.1.3: intent映射更新 - 注册时更新intent_mapping
│   │   └── J-2.1.4: Agent实例管理 - 实例的懒加载和缓存
│   ├── J-2.2: Agent实例生命周期
│   │   ├── J-2.2.1: get_agent方法 - Agent实例获取实现
│   │   ├── J-2.2.2: 实例懒加载 - _load_agent_instance按需加载
│   │   ├── J-2.2.3: 实例缓存机制 - 实例的内存缓存管理
│   │   └── J-2.2.4: 异常处理 - AgentNotFoundError异常抛出
│   ├── J-2.3: 健康检查机制
│   │   ├── J-2.3.1: ⚠️ 未定义 - 健康检查接口规范
│   │   ├── J-2.3.2: ⚠️ 未定义 - 健康状态评估标准
│   │   ├── J-2.3.3: ⚠️ 未定义 - 故障恢复机制
│   │   └── J-2.3.4: ⚠️ 未定义 - 健康检查调度策略
│   └── J-2.4: 负载均衡机制
│       ├── J-2.4.1: ⚠️ 未定义 - round_robin负载均衡算法
│       ├── J-2.4.2: ⚠️ 未定义 - 加权轮询策略
│       ├── J-2.4.3: ⚠️ 未定义 - 最少连接策略
│       └── J-2.4.4: ⚠️ 未定义 - 动态权重调整
├── J-3: 任务队列管理机制
│   ├── J-3.1: 优先级队列实现
│   │   ├── J-3.1.1: TaskQueue类 - 多优先级队列管理
│   │   ├── J-3.1.2: 队列初始化 - high_priority, normal_priority, low_priority
│   │   ├── J-3.1.3: enqueue_task方法 - 按优先级入队实现
│   │   └── J-3.1.4: dequeue_task方法 - 优先级队列出队实现
│   ├── J-3.2: 队列容量管理
│   │   ├── J-3.2.1: ⚠️ 未定义 - 队列容量限制机制
│   │   ├── J-3.2.2: ⚠️ 未定义 - 队列满时的处理策略
│   │   ├── J-3.2.3: ⚠️ 未定义 - 队列监控和告警
│   │   └── J-3.2.4: ⚠️ 未定义 - 动态队列扩容
│   ├── J-3.3: 任务调度策略
│   │   ├── J-3.3.1: 优先级调度 - 高优先级任务优先处理
│   │   ├── J-3.3.2: 公平调度 - 防止低优先级任务饿死
│   │   ├── J-3.3.3: 批量处理 - 相同类型任务的批量处理优化
│   │   └── J-3.3.4: 延迟调度 - 特定条件下的延迟执行
│   └── J-3.4: 队列监控机制
│       ├── J-3.4.1: 队列长度监控 - 实时队列长度统计
│       ├── J-3.4.2: 处理速度监控 - 任务处理速度统计
│       ├── J-3.4.3: 等待时间监控 - 任务队列等待时间统计
│       └── J-3.4.4: 积压预警 - 队列积压的预警机制
├── J-4: 熔断器保护机制
│   ├── J-4.1: CircuitBreaker实现
│   │   ├── J-4.1.1: CircuitBreaker类 - 熔断器状态管理
│   │   ├── J-4.1.2: 状态定义 - closed, open, half_open三种状态
│   │   ├── J-4.1.3: 失败计数 - failure_count和failure_threshold管理
│   │   └── J-4.1.4: 超时控制 - timeout_seconds和last_failure_time
│   ├── J-4.2: 熔断策略实现
│   │   ├── J-4.2.1: call_with_breaker方法 - 带熔断器的调用实现
│   │   ├── J-4.2.2: 状态检查逻辑 - open状态下的时间检查
│   │   ├── J-4.2.3: 半开状态处理 - half_open状态的恢复逻辑
│   │   └── J-4.2.4: 失败统计更新 - 失败次数和状态的更新逻辑
│   ├── J-4.3: 熔断参数配置
│   │   ├── J-4.3.1: failure_threshold配置 - 失败阈值设置（默认5）
│   │   ├── J-4.3.2: timeout_seconds配置 - 熔断超时时间设置（默认60）
│   │   ├── J-4.3.3: half_open_max_calls - 半开状态最大调用次数
│   │   └── J-4.3.4: recovery_timeout_seconds - 恢复超时时间配置
│   └── J-4.4: 熔断监控与统计
│       ├── J-4.4.1: 熔断状态监控 - 实时熔断器状态监控
│       ├── J-4.4.2: 失败率统计 - Agent失败率的统计分析
│       ├── J-4.4.3: 恢复时间统计 - 熔断恢复时间的统计
│       └── J-4.4.4: 熔断事件日志 - 熔断触发和恢复的事件记录
```

------------------------------

### J: 数据模型与Schema完整定义

```
├── K-1: 核心数据模型定义
│   ├── K-1.1: TaskRequest任务请求模型
│   │   ├── K-1.1.1: 基础字段 - task_id, target_agent, intent, payload
│   │   ├── K-1.1.2: 控制字段 - priority(1-10), timeout_seconds, retry_config
│   │   ├── K-1.1.3: 字段验证 - 使用Field()进行字段验证和描述
│   │   └── K-1.1.4: 模型来源 - 从global_schemas统一导入
│   ├── K-1.2: TaskResponse任务响应模型
│   │   ├── K-1.2.1: 响应字段 - task_id, agent_name, execution_time_ms, success
│   │   ├── K-1.2.2: 结果字段 - result(AgentResponse), retry_count, error_info
│   │   ├── K-1.2.3: 时间统计 - 执行时间的毫秒级统计
│   │   └── K-1.2.4: 错误信息 - Optional[Dict]类型的错误详情
│   ├── K-1.3: AgentRegistration模块注册模型
│   │   ├── K-1.3.1: 注册信息 - agent_name, module_path, supported_tasks
│   │   ├── K-1.3.2: 运行状态 - instance(Optional), status, health_check_url
│   │   ├── K-1.3.3: 支持任务 - List[str]类型的任务类型列表
│   │   └── K-1.3.4: 健康检查 - Optional[str]类型的健康检查地址
│   └── K-1.4: TaskChain任务链模型
│       ├── K-1.4.1: 链标识 - chain_id, chain_name唯一标识
│       ├── K-1.4.2: 任务列表 - List[TaskRequest]类型的任务序列
│       ├── K-1.4.3: 执行状态 - Literal状态枚举和当前执行索引
│       ├── K-1.4.4: 时间统计 - started_at, completed_at, execution_time_ms
│       └── K-1.4.5: 错误处理 - failed_task_id, error_details, retry_count
├── K-2: 系统状态模型定义
│   ├── K-2.1: CircuitBreakerState熔断器状态模型
│   │   ├── K-2.1.1: Agent标识 - agent_name目标Agent名称
│   │   ├── K-2.1.2: 熔断状态 - state(closed/open/half_open)状态枚举
│   │   ├── K-2.1.3: 统计计数 - failure_count, success_count, total_requests
│   │   ├── K-2.1.4: 时间管理 - last_failure_time, next_attempt_time
│   │   └── K-2.1.5: 默认值设置 - 所有字段的合理默认值
│   ├── K-2.2: ModuleHealthStatus模块健康状态模型
│   │   ├── K-2.2.1: 模块标识 - module_name模块名称
│   │   ├── K-2.2.2: 健康状态 - status(healthy/degraded/unhealthy/unknown)
│   │   ├── K-2.2.3: 检查信息 - last_check_time, response_time_ms, error_rate
│   │   ├── K-2.2.4: 失败统计 - consecutive_failures连续失败次数
│   │   └── K-2.2.5: 健康详情 - Optional[Dict]类型的详细健康信息
│   ├── K-2.3: DialogueStateManager对话状态模型
│   │   ├── K-2.3.1: ⚠️ 未定义 - 具体的对话状态字段结构
│   │   ├── K-2.3.2: ⚠️ 未定义 - 状态序列化和反序列化格式
│   │   ├── K-2.3.3: ⚠️ 未定义 - 跨设备同步的数据格式
│   │   └── K-2.3.4: ⚠️ 未定义 - 状态版本控制机制
│   └── K-2.4: CompanyVerificationManager企业验证模型
│       ├── K-2.4.1: ⚠️ 未定义 - 企业验证文档的数据结构
│       ├── K-2.4.2: ⚠️ 未定义 - 多公司检测结果的数据格式
│       ├── K-2.4.3: ⚠️ 未定义 - 验证失败错误信息的标准格式
│       └── K-2.4.4: ⚠️ 未定义 - 公司信息的标准化数据结构
├── K-3: Pydantic V2规范实现
│   ├── K-3.1: 模型验证规范
│   │   ├── K-3.1.1: model_validate()使用 - 替代parse_obj()进行数据验证
│   │   ├── K-3.1.2: model_dump()使用 - 替代.dict()进行序列化
│   │   ├── K-3.1.3: Field()配置 - 使用Field()进行字段配置和验证
│   │   └── K-3.1.4: 禁用V1 API - 严禁使用.dict(), .parse_obj(), .json()等
│   ├── K-3.2: 字段验证规范
│   │   ├── K-3.2.1: pattern参数 - 使用pattern=r"regex"进行正则验证
│   │   ├── K-3.2.2: 禁用regex参数 - 严禁使用regex=r"regex"语法
│   │   ├── K-3.2.3: 类型提示 - 完整的类型提示和泛型使用
│   │   └── K-3.2.4: 默认值设置 - 合理的字段默认值设置
│   ├── K-3.3: 模型导入规范
│   │   ├── K-3.3.1: 统一导入源 - 从global_schemas统一导入所有模型
│   │   ├── K-3.3.2: 禁止本地定义 - 禁止在模块内重复定义业务模型
│   │   ├── K-3.3.3: 版本兼容性 - 模型版本的向下兼容性管理
│   │   └── K-3.3.4: 依赖管理 - 模型依赖关系的清晰定义
│   └── K-3.4: 序列化反序列化
│       ├── K-3.4.1: JSON序列化 - model_dump()的JSON序列化
│       ├── K-3.4.2: 数据验证 - model_validate()的数据验证
│       ├── K-3.4.3: 错误处理 - 验证失败时的错误处理机制
│       └── K-3.4.4: 性能优化 - 序列化反序列化的性能优化
├── K-4: Schema版本管理
│   ├── K-4.1: 版本控制策略
│   │   ├── K-4.1.1: 语义版本控制 - 使用semver进行版本管理
│   │   ├── K-4.1.2: 向下兼容 - 新版本保持向下兼容性
│   │   ├── K-4.1.3: 废弃机制 - 过时字段的废弃和迁移机制
│   │   └── K-4.1.4: 版本检查 - 运行时版本兼容性检查
│   ├── K-4.2: 字段变更管理
│   │   ├── K-4.2.1: 新增字段 - 新增字段必须提供默认值
│   │   ├── K-4.2.2: 字段重命名 - 字段重命名的向下兼容处理
│   │   ├── K-4.2.3: 字段删除 - 字段删除的渐进式处理
│   │   └── K-4.2.4: 类型变更 - 字段类型变更的兼容性处理
│   ├── K-4.3: 迁移机制
│   │   ├── K-4.3.1: 数据迁移 - 历史数据的迁移策略
│   │   ├── K-4.3.2: 配置迁移 - 配置格式的迁移机制
│   │   ├── K-4.3.3: API迁移 - 接口变更的迁移支持
│   │   └── K-4.3.4: 回滚策略 - 迁移失败时的回滚机制
│   └── K-4.4: 文档与契约
│       ├── K-4.4.1: Schema文档 - 完整的Schema文档维护
│       ├── K-4.4.2: 变更日志 - 详细的版本变更日志
│       ├── K-4.4.3: 兼容性矩阵 - 版本间的兼容性矩阵
│       └── K-4.4.4: 升级指南 - 版本升级的详细指南
```

------------------------------

### K: 存储与外部集成完整定义

```
├── L-1: 模块注册表管理
│   ├── L-1.1: ModuleRegistry存储机制
│   │   ├── L-1.1.1: Agent注册信息存储 - _agents字典存储AgentRegistration
│   │   ├── L-1.1.2: Intent映射存储 - _intent_mapping字典存储意图到Agent映射
│   │   ├── L-1.1.3: 实例缓存管理 - Agent实例的内存缓存机制
│   │   └── L-1.1.4: 注册信息持久化 - ⚠️ 未定义注册信息持久化策略
│   ├── L-1.2: Agent实例管理
│   │   ├── L-1.2.1: register_agent方法 - 新模块注册实现
│   │   ├── L-1.2.2: get_agent方法 - Agent实例获取实现
│   │   ├── L-1.2.3: 懒加载机制 - _load_agent_instance按需加载
│   │   └── L-1.2.4: 实例生命周期 - Agent实例的创建和销毁管理
│   ├── L-1.3: Intent映射更新
│   │   ├── L-1.3.1: 动态映射更新 - 注册时自动更新intent_mapping
│   │   ├── L-1.3.2: 通配符支持 - 支持"*"通配符的模式匹配
│   │   ├── L-1.3.3: 冲突检测 - 映射冲突的检测和处理
│   │   └── L-1.3.4: 映射优先级 - 不同映射规则的优先级管理
│   └── L-1.4: 异常处理机制
│       ├── L-1.4.1: AgentNotFoundError - Agent不存在异常抛出
│       ├── L-1.4.2: 注册冲突处理 - 重复注册的处理策略
│       ├── L-1.4.3: 实例加载失败 - 实例加载失败的错误处理
│       └── L-1.4.4: 映射解析失败 - Intent映射解析失败的处理
├── L-2: 任务队列管理存储
│   ├── L-2.1: TaskQueue优先级存储
│   │   ├── L-2.1.1: 高优先级队列 - _high_priority asyncio.Queue实现
│   │   ├── L-2.1.2: 普通优先级队列 - _normal_priority asyncio.Queue实现
│   │   ├── L-2.1.3: 低优先级队列 - _low_priority asyncio.Queue实现
│   │   └── L-2.1.4: 队列容量管理 - ⚠️ 未定义队列容量限制机制
│   ├── L-2.2: 任务入队机制
│   │   ├── L-2.2.1: enqueue_task方法 - 按优先级将任务放入对应队列
│   │   ├── L-2.2.2: 优先级判断 - priority >= 8高优先级, >= 5普通, <5低优先级
│   │   ├── L-2.2.3: 队列选择逻辑 - 根据任务优先级选择目标队列
│   │   └── L-2.2.4: 异步入队操作 - await queue.put()异步入队
│   ├── L-2.3: 任务出队机制
│   │   ├── L-2.3.1: dequeue_task方法 - 按优先级顺序出队任务
│   │   ├── L-2.3.2: 优先级调度 - 高→普通→低优先级的调度顺序
│   │   ├── L-2.3.3: 非阻塞出队 - queue.get_nowait()非阻塞操作
│   │   └── L-2.3.4: 空队列处理 - 所有队列为空时返回None
│   └── L-2.4: 队列监控机制
│       ├── L-2.4.1: ⚠️ 未定义 - 队列长度实时监控
│       ├── L-2.4.2: ⚠️ 未定义 - 队列处理速度统计
│       ├── L-2.4.3: ⚠️ 未定义 - 队列等待时间统计
│       └── L-2.4.4: ⚠️ 未定义 - 队列积压预警机制
├── L-3: 熔断器保护存储
│   ├── L-3.1: CircuitBreaker状态存储
│   │   ├── L-3.1.1: 失败计数存储 - failure_count失败次数计数
│   │   ├── L-3.1.2: 状态管理 - state(closed/open/half_open)状态存储
│   │   ├── L-3.1.3: 时间记录 - last_failure_time最后失败时间记录
│   │   └── L-3.1.4: 阈值配置 - failure_threshold和timeout_seconds配置
│   ├── L-3.2: 熔断策略存储
│   │   ├── L-3.2.1: call_with_breaker实现 - 带熔断器的调用逻辑
│   │   ├── L-3.2.2: 状态检查逻辑 - open状态下的超时检查
│   │   ├── L-3.2.3: 半开状态处理 - half_open状态的恢复逻辑
│   │   └── L-3.2.4: 统计更新机制 - 失败成功统计的实时更新
│   ├── L-3.3: 熔断配置管理
│   │   ├── L-3.3.1: 默认配置 - failure_threshold=5, timeout_seconds=60
│   │   ├── L-3.3.2: 配置热更新 - ⚠️ 未定义熔断器配置热更新机制
│   │   ├── L-3.3.3: Agent级配置 - ⚠️ 未定义每个Agent的独立熔断配置
│   │   └── L-3.3.4: 配置验证 - ⚠️ 未定义熔断器配置参数验证
│   └── L-3.4: 异常抛出机制
│       ├── L-3.4.1: ServiceUnavailableError - 熔断器开启时抛出
│       ├── L-3.4.2: 错误消息格式 - "Circuit breaker open for {target_agent}"
│       ├── L-3.4.3: 异常传播 - 熔断异常向上层传播
│       └── L-3.4.4: 恢复通知 - ⚠️ 未定义熔断恢复的通知机制
├── L-4: 外部集成接口存储
│   ├── L-4.1: Database Agent集成
│   │   ├── L-4.1.1: 对话状态存储 - 通过database_agent存储用户对话状态
│   │   ├── L-4.1.2: 配置缓存存储 - 通过database_agent缓存配置信息
│   │   ├── L-4.1.3: 用户数据查询 - 通过database_agent查询用户数据
│   │   └── L-4.1.4: 协调日志存储 - 通过database_agent存储任务协调日志
│   ├── L-4.2: 配置管理集成
│   │   ├── L-4.2.1: global_config加载 - 从配置源加载全局配置
│   │   ├── L-4.2.2: 配置分发管理 - 向其他Agent分发配置参数
│   │   ├── L-4.2.3: 配置缓存机制 - _config_cache配置缓存存储
│   │   └── L-4.2.4: 热更新通知 - 配置变更时的Agent通知机制
│   ├── L-4.3: 日志系统集成
│   │   ├── L-4.3.1: Python logging - 使用标准logging模块进行日志记录
│   │   ├── L-4.3.2: 结构化日志 - request_id等字段的结构化日志
│   │   ├── L-4.3.3: 性能日志 - execution_time_ms等性能指标日志
│   │   └── L-4.3.4: 错误日志 - 异常和错误的详细日志记录
│   └── L-4.4: 监控系统集成
│       ├── L-4.4.1: 指标暴露 - routing_agent_requests_total等指标
│       ├── L-4.4.2: 性能监控 - 任务调度性能指标的实时监控
│       ├── L-4.4.3: 健康检查 - Agent健康状态的监控集成
│       └── L-4.4.4: 告警集成 - ⚠️ 未定义告警系统集成机制
```

------------------------------

### L: 故障诊断与调试、依赖关系清单

```
├── M-1: 常见问题解决方案
│   ├── M-1.1: 模块调用失败诊断
│   │   ├── M-1.1.1: 问题症状 - dispatch_task抛出TaskExecutionError
│   │   ├── M-1.1.2: 排查步骤 - 检查目标模块状态、网络连接、payload格式
│   │   ├── M-1.1.3: 解决方案 - 重启目标模块、修正payload、检查模块注册
│   │   └── M-1.1.4: 预防措施 - 健康检查机制和实时监控
│   ├── M-1.2: 配置获取失败诊断
│   │   ├── M-1.2.1: 问题症状 - get_config返回空配置或异常
│   │   ├── M-1.2.2: 排查步骤 - 检查global_config文件完整性、配置key正确性
│   │   ├── M-1.2.3: 解决方案 - 恢复配置备份、重新加载global_config
│   │   └── M-1.2.4: 预防措施 - 配置版本控制和自动备份机制
│   ├── M-1.3: 任务链死循环诊断
│   │   ├── M-1.3.1: 问题症状 - continue_chain指令导致无限循环
│   │   ├── M-1.3.2: 排查步骤 - 检查模块返回的next_intents、flow_directive逻辑
│   │   ├── M-1.3.3: 解决方案 - 设置最大任务链长度限制、修正模块逻辑
│   │   └── M-1.3.4: 预防措施 - 任务链长度监控和自动终止机制
│   └── M-1.4: 熔断器误触发诊断
│       ├── M-1.4.1: 问题症状 - Agent频繁熔断导致服务不可用
│       ├── M-1.4.2: 排查步骤 - 检查failure_threshold设置、Agent响应时间、错误率
│       ├── M-1.4.3: 解决方案 - 调整熔断参数、优化Agent性能、增加重试机制
│       └── M-1.4.4: 预防措施 - 动态熔断参数调整和智能阈值设置
├── M-2: 调试工具与方法
│   ├── M-2.1: 日志分析工具
│   │   ├── M-2.1.1: 结构化日志查询 - 基于request_id的链路追踪
│   │   ├── M-2.1.2: 性能日志分析 - execution_time_ms等性能指标分析
│   │   ├── M-2.1.3: 错误日志聚合 - 相同错误类型的聚合分析
│   │   └── M-2.1.4: 日志可视化 - ⚠️ 未定义日志可视化工具集成
│   ├── M-2.2: 性能分析工具
│   │   ├── M-2.2.1: 任务调度性能 - 任务分发时间和成功率分析
│   │   ├── M-2.2.2: Agent响应时间 - 各Agent的响应时间分布分析
│   │   ├── M-2.2.3: 并发性能分析 - 高并发场景下的性能瓶颈分析
│   │   └── M-2.2.4: 内存使用分析 - 内存使用模式和泄漏检测
│   ├── M-2.3: 状态诊断工具
│   │   ├── M-2.3.1: Agent状态查询 - 实时Agent健康状态查询
│   │   ├── M-2.3.2: 熔断器状态监控 - 熔断器状态的实时监控
│   │   ├── M-2.3.3: 队列状态检查 - 任务队列长度和积压情况
│   │   └── M-2.3.4: 配置状态验证 - 当前配置状态的验证和对比
│   └── M-2.4: 故障模拟工具
│       ├── M-2.4.1: ⚠️ 未定义 - Agent故障模拟工具
│       ├── M-2.4.2: ⚠️ 未定义 - 网络故障模拟工具
│       ├── M-2.4.3: ⚠️ 未定义 - 配置错误模拟工具
│       └── M-2.4.4: ⚠️ 未定义 - 高负载模拟工具
├── M-3: 依赖关系完整清单
│   ├── M-3.1: 上游依赖服务
│   │   ├── M-3.1.1: entry_agent - 唯一请求来源，提供任务调度请求
│   │   ├── M-3.1.2: global_config - 全局配置数据源，提供所有配置参数
│   │   ├── M-3.1.3: global_schemas - 全局模型定义，提供数据结构
│   │   └── M-3.1.4: Python asyncio - 异步并发框架，支持高并发调度
│   ├── M-3.2: 下游服务依赖
│   │   ├── M-3.2.1: 所有business agent - 业务处理模块，接受任务调度
│   │   ├── M-3.2.2: llm_handler_agent - LLM调用专用模块
│   │   ├── M-3.2.3: database_agent - 数据存储专用模块
│   │   └── M-3.2.4: 配置缓存服务 - 内部配置管理服务
│   ├── M-3.3: 第三方库依赖
│   │   ├── M-3.3.1: pydantic>=2.0.0 - 数据验证和序列化框架
│   │   ├── M-3.3.2: asyncio - Python 3.10内置异步框架
│   │   ├── M-3.3.3: logging - Python标准库日志模块
│   │   └── M-3.3.4: time - Python标准库时间模块
│   └── M-3.4: 系统依赖
│       ├── M-3.4.1: Python 3.10+ - 强制Python版本要求
│       ├── M-3.4.2: 操作系统支持 - Linux/Windows/macOS兼容性
│       ├── M-3.4.3: 网络连接 - Agent间通信网络要求
│       └── M-3.4.4: 文件系统 - 配置文件和日志存储要求
├── M-4: 版本兼容性管理
│   ├── M-4.1: 向上兼容性
│   │   ├── M-4.1.1: entry_agent接口 - 确保与entry_agent接口向上兼容
│   │   ├── M-4.1.2: global_schemas版本 - 支持global_schemas版本升级
│   │   ├── M-4.1.3: 配置格式兼容 - global_config格式的向上兼容
│   │   └── M-4.1.4: 协议版本兼容 - AgentRequest协议的版本兼容性
│   ├── M-4.2: 向下兼容性
│   │   ├── M-4.2.1: 业务Agent接口 - 确保业务Agent接口向下兼容
│   │   ├── M-4.2.2: 配置分发接口 - 配置获取接口的向下兼容
│   │   ├── M-4.2.3: 错误码兼容 - 错误码格式的向下兼容性
│   │   └── M-4.2.4: 数据模型兼容 - 数据模型字段的向下兼容
│   ├── M-4.3: 迁移策略
│   │   ├── M-4.3.1: 灰度发布 - 新版本的灰度发布策略
│   │   ├── M-4.3.2: 回滚计划 - 升级失败时的快速回滚计划
│   │   ├── M-4.3.3: 数据迁移 - 版本升级时的数据迁移策略
│   │   └── M-4.3.4: 配置迁移 - 配置格式变更时的迁移方案
│   └── M-4.4: 测试验证
│       ├── M-4.4.1: 兼容性测试 - 版本间兼容性的自动化测试
│       ├── M-4.4.2: 回归测试 - 升级后功能完整性的回归测试
│       ├── M-4.4.3: 性能测试 - 升级对性能影响的测试验证
│       └── M-4.4.4: 集成测试 - 与其他模块集成的测试验证
```

------------------------------

### M: 开发边界限制与待补要点

```
├── N-1: 开发边界限制完整定义（严格遵守）
│   ├── N-1.1: 适用范围与角色
│   │   ├── N-1.1.1: 限制目标 - 限制文件创建/编辑/依赖方向/接口契约的自由度
│   │   ├── N-1.1.2: 占位符映射 - MODULE_NAME: routing_agent, MODULE_ROOT: routing_agent/
│   │   ├── N-1.1.3: 全局依赖 - GLOBAL_SCHEMAS: global_schemas, GLOBAL_CONFIG: routing_agent配置管理
│   │   └── N-1.1.4: 状态存储 - STATE_STORE: database_agent统一管理的存储层
│   ├── N-1.2: 目录与文件边界（文件系统红线）
│   │   ├── N-1.2.1: 工作区限制 - 生成和修改仅允许在routing_agent/内
│   │   ├── N-1.2.2: 文件操作禁止 - 禁止创建、移动、重命名、删除routing_agent/外的文件
│   │   ├── N-1.2.3: 主入口约定 - 模块主入口文件名与routing_agent同名
│   │   ├── N-1.2.4: 粒度限制 - 单次变更仅允许操作一个文件，超过300行自动截断
│   │   └── N-1.2.5: 结构稳定性 - 禁止新建公共目录和跨模块工具文件
│   ├── N-1.3: 职责分层边界（单一职责红线）
│   │   ├── N-1.3.1: Main主文件 - 只做策略选择、依赖装配、流程编排
│   │   ├── N-1.3.2: Adapter适配层 - 只实现外设与机制（模块调度、配置管理等）
│   │   ├── N-1.3.3: Aux私有实现 - 仅供Main/Adapter内部复用，不得跨模块导出
│   │   ├── N-1.3.4: 职责禁止 - Main/Aux禁止业务规则、存储访问、外部I/O
│   │   └── N-1.3.5: 拆分触发 - 单文件承担两类以上变更原因或超过200行时必须拆分
│   ├── N-1.4: 契约与模型来源（数据红线）
│   │   ├── N-1.4.1: 模型唯一来源 - 所有数据模型从global_schemas引入
│   │   ├── N-1.4.2: 禁止本地定义 - 禁止模块内新增/复制业务模型或DTO
│   │   ├── N-1.4.3: 接口契约 - README提供最小可执行契约，不提供实现样例
│   │   └── N-1.4.4: 版本兼容 - 新增/变更字段必须标注语义、默认值、兼容策略
│   └── N-1.5: 关键词黑名单（检测红线）
│       ├── N-1.5.1: 禁止本地业务模型 - "class .*Model", "data class .*", "interface .*DTO"
│       ├── N-1.5.2: 禁止硬编码配置 - "API_KEY=", "timeout\\s*=\\s*\\d+", "retry\\s*=\\s*\\d+"
│       ├── N-1.5.3: 禁止跨层I/O - Main/Aux中出现"http", "db", "sql", "open(", "requests"
│       ├── N-1.5.4: 禁止并发越界 - "Thread", "Process", "fork", "Pool"
│       └── N-1.5.5: 禁止未脱敏日志 - 包含"password|token|secret"的日志输出
├── N-2: 配置与特性开关（配置红线）
│   ├── N-2.1: 配置唯一来源
│   │   ├── N-2.1.1: 全局配置管理 - routing_agent作为全局配置管理者
│   │   ├── N-2.1.2: 禁止本地配置 - 其他模块禁止本地硬编码可变配置
│   │   ├── N-2.1.3: 配置获取接口 - 必须通过routing_agent获取配置
│   │   └── N-2.1.4: 配置分发责任 - 统一配置分发和版本管理
│   ├── N-2.2: 热更新与回滚
│   │   ├── N-2.2.1: 配置键名控制 - 配置键名/层级不可私改
│   │   ├── N-2.2.2: 新增键要求 - 新增键必须提供默认值、回滚策略
│   │   ├── N-2.2.3: 版本回滚 - 支持最近5个版本的配置回滚
│   │   └── N-2.2.4: 热更新零停机 - 配置更新零停机时间要求
│   └── N-2.3: 配置验证机制
│       ├── N-2.3.1: 配置格式验证 - 配置格式的严格验证
│       ├── N-2.3.2: 依赖关系检查 - 配置间依赖关系的检查
│       ├── N-2.3.3: 环境一致性 - 不同环境配置的一致性检查
│       └── N-2.3.4: 配置安全性 - 敏感配置的安全处理机制
├── N-3: 外部I/O与状态（副作用红线）
│   ├── N-3.1: 状态存取限制
│   │   ├── N-3.1.1: 禁止直接访问 - 模块不得直接访问持久化（DB/Cache/FS）
│   │   ├── N-3.1.2: 间接访问 - 必须通过指定Adapter间接访问database_agent
│   │   ├── N-3.1.3: 状态同步 - 状态更新的同步和一致性保证
│   │   └── N-3.1.4: 状态版本控制 - 状态的版本控制和冲突解决
│   ├── N-3.2: 副作用隔离
│   │   ├── N-3.2.1: I/O限制 - 任何网络/系统I/O仅可写在Adapter
│   │   ├── N-3.2.2: 违规检测 - Main/Aux出现I/O视为违规
│   │   ├── N-3.2.3: 异步处理 - 所有I/O操作必须异步处理
│   │   └── N-3.2.4: 错误处理 - I/O操作的统一错误处理机制
│   └── N-3.3: 可重复执行要求
│       ├── N-3.3.1: 幂等性要求 - 任意函数满足幂等要求
│       ├── N-3.3.2: 可重放性 - 同输入不应产生额外副作用
│       ├── N-3.3.3: 状态无关 - 函数执行不依赖外部可变状态
│       └── N-3.3.4: 事务性 - 复杂操作的事务性保证
├── N-4: 待补要点清单（歧义兜底）
│   ├── N-4.1: 配置来源与键名待定
│   │   ├── N-4.1.1: global_config具体来源路径 - 影响所有配置获取功能实现
│   │   ├── N-4.1.2: 保守选项 - 环境变量 | 配置文件路径 | 配置服务URL
│   │   ├── N-4.1.3: 建议方案 - 使用环境变量GLOBAL_CONFIG_PATH指定
│   │   └── N-4.1.4: 缓存预热策略 - 启动时预热 | 惰性加载 | 混合策略（建议默认惰性）
│   ├── N-4.2: 数值阈值待定
│   │   ├── N-4.2.1: 熔断器阈值配置 - 影响系统稳定性和故障恢复
│   │   ├── N-4.2.2: failure_threshold选项 - 3|5|10（建议默认5）
│   │   ├── N-4.2.3: 任务队列容量上限 - 影响内存使用和性能
│   │   └── N-4.2.4: 队列容量选项 - 100|500|1000每优先级（建议默认500）
│   ├── N-4.3: 接口字段语义待定
│   │   ├── N-4.3.1: routing_context字段结构 - 影响所有Agent间上下文传递
│   │   ├── N-4.3.2: 结构选项 - 扁平结构 | 嵌套结构 | 混合结构（建议扁平）
│   │   ├── N-4.3.3: state_sync_info同步粒度 - 影响状态同步效率和一致性
│   │   └── N-4.3.4: 同步选项 - 全量 | 增量 | 版本控制（建议版本控制增量）
│   └── N-4.4: 外部依赖接口待定
│       ├── N-4.4.1: 健康检查端点规范 - 影响Agent状态监控和运维
│       ├── N-4.4.2: 端点选项 - HTTP endpoint | gRPC | 内部接口（建议HTTP /health）
│       ├── N-4.4.3: 邮件模板格式 - support@4waysgroup.com模板格式
│       └── N-4.4.4: 模板选项 - 纯文本 | HTML | 结构化JSON（建议HTML含错误上下文）
```

------------------------------

### N: 完整全局配置参数与错误码总结

```
├── O-1: 全局配置参数总结
│   ├── O-1.1: 对话流程配置
│   │   ├── O-1.1.1: dialogue_persistence_enabled - bool, 默认true, 对话持久化开关
│   │   ├── O-1.1.2: checkpoint_save_interval - int, 默认30秒, 断点保存间隔
│   │   ├── O-1.1.3: state_recovery_timeout - int, 默认10秒, 状态恢复超时
│   │   └── O-1.1.4: 配置来源 - 全部来源global_config统一管理
│   ├── O-1.2: 路由优化配置
│   │   ├── O-1.2.1: intelligent_routing_enabled - bool, 默认true, 智能路由开关
│   │   ├── O-1.2.2: load_balancing_strategy - str, 默认"round_robin", 负载均衡策略
│   │   ├── O-1.2.3: cache_warming_enabled - bool, 默认false, 缓存预热开关
│   │   └── O-1.2.4: 配置热更新支持 - 支持运行时动态更新
│   ├── O-1.3: 熔断器保护配置
│   │   ├── O-1.3.1: failure_threshold - int, 默认5, 失败阈值
│   │   ├── O-1.3.2: timeout_seconds - int, 默认60, 熔断超时时间
│   │   ├── O-1.3.3: half_open_max_calls - int, 默认3, 半开状态最大调用
│   │   ├── O-1.3.4: recovery_timeout_seconds - int, 默认300, 恢复超时时间
│   │   ├── O-1.3.5: failure_rate_threshold - float, 默认0.5, 失败率阈值
│   │   ├── O-1.3.6: slow_call_duration_threshold - int, 默认5000ms, 慢调用阈值
│   │   ├── O-1.3.7: minimum_number_of_calls - int, 默认10, 最小调用次数
│   │   └── O-1.3.8: sliding_window_size - int, 默认100, 滑动窗口大小
│   └── O-1.4: 跨Agent配置分发
│       ├── O-1.4.1: database_agent配置 - mongodb_config, security_config
│       ├── O-1.4.2: auth_agent配置 - jwt_config, oauth_security
│       ├── O-1.4.3: 模块注册配置 - health_check_interval_seconds等
│       └── O-1.4.4: 重试策略配置 - max_retries, retry_delay_seconds等
├── O-2: 完整全局错误码总结
│   ├── O-2.1: ROUTING前缀错误码（统一格式）
│   │   ├── O-2.1.1: ROUTING/AGENT_NOT_FOUND - 目标Agent不存在
│   │   ├── O-2.1.2: ROUTING/TIMEOUT - 任务调度超时
│   │   ├── O-2.1.3: ROUTING/TASK_EXECUTION_FAILED - 任务执行失败
│   │   ├── O-2.1.4: ROUTING/INVALID_TASK_TYPE - 任务类型不支持
│   │   ├── O-2.1.5: ROUTING/CIRCUIT_BREAKER_OPEN - 熔断器开启
│   │   ├── O-2.1.6: ROUTING/TASK_CHAIN_FAILED - 任务链执行失败
│   │   ├── O-2.1.7: ROUTING/AGENT_UNHEALTHY - 目标Agent健康检查失败
│   │   ├── O-2.1.8: ROUTING/CONCURRENT_LIMIT_EXCEEDED - 并发任务数量超限
│   │   ├── O-2.1.9: ROUTING/CONFIGURATION_ERROR - 路由配置错误
│   │   ├── O-2.1.10: ROUTING/IDENTITY_ROUTING_FAILED - 身份路由失败
│   │   ├── O-2.1.11: ROUTING/DIALOGUE_STATE_CORRUPTED - 对话状态损坏
│   │   ├── O-2.1.12: ROUTING/TASK_COORDINATION_FAILED - 任务协调失败
│   │   ├── O-2.1.13: ROUTING/STATE_SYNC_FAILED - 状态同步失败
│   │   └── O-2.1.14: ROUTING/COMPANY_SELECTION_REQUIRED - 需要选择企业
│   ├── O-2.2: CONFIG前缀错误码
│   │   ├── O-2.2.1: CONFIG/NOT_FOUND - 配置项不存在
│   │   ├── O-2.2.2: CONFIG/INVALID_FORMAT - 配置格式错误
│   │   ├── O-2.2.3: CONFIG/LOAD_FAILED - 配置加载失败
│   │   ├── O-2.2.4: CONFIG/VALIDATION_FAILED - 配置验证失败
│   │   └── O-2.2.5: CONFIG/HOT_RELOAD_FAILED - 热更新失败
│   ├── O-2.3: 统一支持邮件模板
│   │   ├── O-2.3.1: 模块名称 - 错误发生的模块名称标识
│   │   ├── O-2.3.2: 错误类别 - 错误的分类和类型
│   │   ├── O-2.3.3: 错误码 - 标准化的错误码信息
│   │   ├── O-2.3.4: 尝试解决方案 - 用户已尝试的解决方案
│   │   └── O-2.3.5: 支持邮箱 - support@4waysgroup.com技术支持邮箱
│   └── O-2.4: 错误处理一致性
│       ├── O-2.4.1: 错误格式统一 - 所有Agent使用统一错误响应格式
│       ├── O-2.4.2: 错误码标准化 - 遵循ROUTING/{REASON}命名规范
│       ├── O-2.4.3: 用户友好提示 - 提供可操作的解决方案指导
│       └── O-2.4.4: 技术支持集成 - 错误信息包含技术支持联系方式
├── O-3: 性能指标规范总结
│   ├── O-3.1: 必须暴露指标
│   │   ├── O-3.1.1: routing_agent_requests_total - 调用次数统计
│   │   ├── O-3.1.2: routing_agent_success_rate - 调用成功率
│   │   ├── O-3.1.3: routing_agent_duration_seconds - 时延分布统计
│   │   └── O-3.1.4: 指标命名规范 - 统一的指标命名约定
│   ├── O-3.2: 模块特定指标
│   │   ├── O-3.2.1: routing_agent_dispatch_total - 任务调度次数
│   │   ├── O-3.2.2: routing_agent_config_requests_total - 配置获取次数
│   │   ├── O-3.2.3: routing_agent_circuit_breaker_trips_total - 熔断触发次数
│   │   └── O-3.2.4: routing_agent_task_chain_length - 任务链长度分布
│   ├── O-3.3: SLA承诺总结
│   │   ├── O-3.3.1: 可用性承诺 - 99.95%服务可用性（高于业务模块）
│   │   ├── O-3.3.2: 响应时间承诺 - 95%任务调度 < 50ms
│   │   ├── O-3.3.3: 并发能力承诺 - 支持500+并发任务调度
│   │   └── O-3.3.4: 配置管理承诺 - 配置热更新零停机时间
│   └── O-3.4: 监控告警策略
│       ├── O-3.4.1: 成功率告警 - 成功率低于99%时告警
│       ├── O-3.4.2: 响应时间告警 - 95%响应时间超过50ms时告警
│       ├── O-3.4.3: 熔断器告警 - 熔断器开启时立即告警
│       └── O-3.4.4: 配置异常告警 - 配置加载失败时告警
```

---

## 📋 完整模块契约总结

### ✅ 核心价值定位

routing_agent是Career Bot系统的**任务控制中枢**（Task Control Center），统一管理所有Agent间的协作，支持复杂的多步骤对话流程、状态断点续传、跨Agent数据传递和闭环控制。确保Agent间严格隔离，防止直接调用，实现松耦合的微服务架构。

### ✅ 关键职责边界

1. **任务调度与协调** - 作为系统中所有跨模块调用的唯一通道
2. **全局配置管理** - 作为global_config的唯一管理者和分发中心  
3. **对话流程控制** - 支持求职者路径、企业招聘路径、管理员后台的完整状态管理
4. **Agent协调编排** - 协调所有Agent的任务分发、结果汇总和异常处理
5. **断点续传支持** - 用户对话状态的完整持久化和跨设备恢复

### ✅ 技术架构要求

- **异步优先**: 所有操作基于Python 3.10+ asyncio异步框架
- **Pydantic V2**: 严格使用Pydantic V2 API，禁用V1兼容接口
- **配置统一**: 所有配置来源global_config，禁止本地硬编码
- **Schema统一**: 从global_schemas.json动态生成Pydantic模型并分发给各Agent
- **状态隔离**: 完全无状态设计，状态通过database_agent管理
- **职责清晰**: 专注任务路由和Agent协调，UI控制已移交frontend_service_agent

### ✅ 性能与可靠性

- **高可用**: 99.95%服务可用性，支持500+并发任务调度
- **低延迟**: 95%任务调度延迟 < 50ms  
- **熔断保护**: 故障Agent的自动熔断和恢复机制
- **配置热更新**: 零停机时间的配置动态更新

routing_agent作为整个Career Bot系统的神经中枢和Schema管理中心，确保各个专业Agent能够高效、有序地协同工作，为用户提供流畅的对话体验和完整的业务流程支撑。

⚠️ **架构优化说明**: UI组件控制、事件响应、前端界面相关功能已完全迁移至frontend_service_agent，routing_agent专注于任务路由调度和Schema统一管理，职责边界更加清晰。
