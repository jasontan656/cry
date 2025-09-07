# matching_agent_Structured_readme.md

## 文档骨架结构提取

## 字段迁移说明  
```
所有数据模型/Schema已迁移至global_schemas.json，由routing_agent动态生成和分发：
- SearchHistoryRecord模型 - 搜索历史记录已迁移至global_schemas.json
- MatchingResult模型 - 匹配结果（包含candidate_id、match_score、layer_scores）已迁移
- SearchRequest模型 - 搜索请求参数已迁移至global_schemas.json
- SearchResponse模型 - 搜索响应结果已迁移至global_schemas.json
- CandidateStatus模型 - 候选人状态管理已迁移至global_schemas.json

所有配置参数已迁移至global_config.json：
- matching_agent完整配置组包含：
  - algorithm_config（layer_weights、weight_type_multipliers）
  - threshold_config、search_config、privacy_config
  - performance_config、user_experience_config
```

## A: 开发边界与职责说明

```
matching_agent是Career Bot系统的基于向量相似度的智能匹配引擎，负责调取数据库中由taggings_agent预生成的七层标签向量，通过ChromaDB向量相似度匹配直接计算候选人与职位的匹配分数。该模块无需复杂算法计算，仅通过向量检索和cosine_similarity即可获得精准的匹配结果。现在需要完全融入企业招聘对话流程，支持流式输出双简历展示、5分钟全局搜索间隔限制、脱敏保护机制、候选人搜索历史管理、重复候选人过滤、档案更新检测以及样本简历展示功能，确保企业用户获得最优的候选人搜索体验同时保护候选人隐私。
```

------------------------------

### A-1: 核心概念统一定义

```
- 匹配分数: 向量相似度计算结果，范围0.0-1.0，统一替代"匹配度"/"兼容性得分"/"总体兼容性得分"等变体叫法
- 向量相似度匹配: 基于cosine_similarity的向量计算方法，统一替代"向量匹配"/"语义匹配"/"相似度匹配"等变体叫法
- 候选人: 求职者的统一叫法，替代文档中所有"求职者"/"用户"等变体叫法
- 脱敏保护: 隐私信息保护机制的统一叫法，替代"隐私保护"/"脱敏机制"/"标准脱敏保护"等变体叫法
- 全局搜索间隔: 搜索频率控制机制的统一叫法，替代"搜索间隔"/"搜索冷却时间"等变体叫法
```

------------------------------

### A-2: 关键数值参数定义

```
- SEARCH_INTERVAL_MINUTES=5: 全局搜索间隔分钟数
- MAX_CANDIDATES_PER_SEARCH=2: 每次搜索返回的候选人数量
- CREDIT_COST_PER_SEARCH=2: 每次搜索消耗的点数
- MINIMUM_PURCHASE_UNITS=10: 最小购买点数单位
- MATCHING_THRESHOLD=0.6: 匹配分数阈值
- SUSPENSION_PURCHASE_THRESHOLD=2: 触发暂停的购买次数阈值
- SUSPENSION_DAYS=3: 暂停天数
- DELIST_PURCHASE_THRESHOLD=10: 触发下架的购买次数阈值
```

------------------------------

### B: 依赖与职责关系

```
B: 依赖与职责关系
├── B-1: 上游触发
│   ├── B-1.1: routing_agent - 任务调度和配置管理，接收企业搜索任务
│   ├── B-1.2: jobpost_agent - 职位信息和企业选择完成后触发搜索
│   ├── B-1.3: auth_agent - 雇主身份验证和搜索权限检查
│   └── B-1.4: company_identity_agent - 企业验证状态确认
├── B-2: 下游调用
│   ├── B-2.1: database_agent - 获取预生成标签向量、搜索历史管理、购买计数更新
│   ├── B-2.2: taggings_agent - 获取七层标签体系向量数据和匹配权重配置
│   └── B-2.3: mail_agent - 搜索结果通知和简历购买确认邮件（如需要）
├── B-3: 数据约束
│   ├── B-3.1: 向量相似度匹配 - 基于预生成七层标签向量进行cosine_similarity计算
│   ├── B-3.2: 搜索历史维度 - 按(雇主ID+职位ID+候选人ID)维度记录和过滤
│   ├── B-3.3: 暂停用户过滤 - 静默过滤暂停状态候选人，不出现在搜索结果中
│   └── B-3.4: 购买计数更新 - 每次购买后更新候选人被购买计数
├── B-4: 过滤/去重/历史维度
│   ├── B-4.1: 重复候选人过滤 - 已搜索的(雇主+职位+候选人)组合不重复出现
│   ├── B-4.2: 暂停状态过滤 - 2次购买暂停3天的用户从搜索结果中静默移除
│   ├── B-4.3: 下架用户排除 - 10次购买下架的用户完全不出现在搜索池中
│   └── B-4.4: 地理距离过滤 - 基于预构建地理距离矩阵进行位置匹配
└── B-5: 并发/顺序性
    ├── B-5.1: 全局搜索间隔控制 - SEARCH_INTERVAL_MINUTES=5分钟全局搜索间隔，所有职位共享限制
    ├── B-5.2: 搜索历史原子性 - 搜索记录写入的原子性操作保证
    ├── B-5.3: 购买计数同步 - 与database_agent的购买计数同步更新
    └── B-5.4: 流式输出并发 - 双简历并发流式输出的线程安全
```

------------------------------

### C: 重大决策机制

```
C: 重大决策机制
├── C-1: 搜索与匹配核心策略
│   ├── C-1.1: 向量相似度匹配 - 基于taggings_agent预生成七层标签向量，使用cosine_similarity直接计算匹配分数
│   ├── C-1.2: 双简历流式输出 - 每次搜索同时输出MAX_CANDIDATES_PER_SEARCH=2份最高匹配分数简历，提升雇主搜索效率
│   ├── C-1.3: 全局搜索间隔 - 全局搜索间隔限制，雇主所有职位搜索共享SEARCH_INTERVAL_MINUTES=5分钟冷却时间
│   └── C-1.4: 基于向量数据库 - 匹配分数排序基于向量数据库语义近似度，最高匹配分数优先显示
├── C-2: 搜索历史与过滤策略
│   ├── C-2.1: 搜索历史维度 - 按(雇主ID+职位ID)维度存储，同职位不重复搜索同一候选人
│   ├── C-2.2: 暂停用户静默过滤 - SUSPENSION_PURCHASE_THRESHOLD=2次购买暂停SUSPENSION_DAYS=3天的用户静默从搜索结果过滤，雇主无感知
│   ├── C-2.3: 下架用户完全排除 - DELIST_PURCHASE_THRESHOLD=10次购买下架用户完全移出搜索池，不出现在任何搜索中
│   └── C-2.4: 搜索记录保持 - 候选人重新上架时保持原搜索记录，已搜索过的雇主仍看不到
├── C-3: 脱敏保护策略
│   ├── C-3.1: 脱敏保护 - 自动脱敏姓名、联系方式、住址、出生年月日等敏感信息
│   ├── C-3.2: 完整信息展示 - 显示工作经历、教育背景、技能、薪资期望等非敏感完整信息
│   ├── C-3.3: UserID显示机制 - 简历末尾显示UserID供雇主联系平台付费获取完整版
│   └── C-3.4: 付费解锁模式 - 雇主需要付费购买才能获得候选人完整联系方式
├── C-4: 点数管理与购买策略
│   ├── C-4.1: 每次搜索扣费 - 每次搜索扣除CREDIT_COST_PER_SEARCH=2份额度（对应显示MAX_CANDIDATES_PER_SEARCH=2份简历）
│   ├── C-4.2: 最小购买单位 - 雇主最少购买MINIMUM_PURCHASE_UNITS=10份额度，只支持偶数购买
│   ├── C-4.3: 余额验证机制 - 搜索前验证账户余额，不足时阻断搜索并提示充值
│   └── C-4.4: 线下付费管理 - 目前通过线下付费，后台手动添加份数到账户
└── C-5: 匹配算法与权重策略
    ├── C-5.1: 动态权重应用 - 根据工作模式调整各维度权重（技能、地理、经验等）
    ├── C-5.2: 七层标签匹配 - 完整支持taggings_agent的Layer 0-6标签体系匹配
    ├── C-5.3: REQUIRED/PREFERRED/CONTEXTUAL - 按标签权重分类进行差异化匹配计算
    └── C-5.4: 地理距离实时计算 - 唯一需要实时计算的部分，其他均基于预生成向量
```

------------------------------

### D: 契约与字段规范

```
D: 契约与字段规范
├── D-1: 搜索历史管理字段
│   ├── D-1.1: 搜索记录字段
│   │   ├── search_history_key: (雇主ID+职位ID+候选人ID)组合键
│   │   ├── searched_at: 搜索时间戳
│   │   ├── search_session_id: 搜索会话标识
│   │   └── match_score_at_search: 搜索时的匹配分数
│   └── D-1.2: 过滤配置字段
│       ├── exclude_searched_candidates: 排除已搜索候选人开关（默认true）
│       ├── search_history_retention: 搜索历史保留策略
│       └── reset_history_on_job_update: 职位更新时重置搜索历史
├── D-2: 用户状态过滤字段
│   ├── D-2.1: 状态过滤字段
│   │   ├── suspension_filter_enabled: 暂停用户过滤开关（默认true）
│   │   ├── delisted_filter_enabled: 下架用户过滤开关（默认true）
│   │   └── filter_mode: 过滤模式（silent/notify）
│   └── D-2.2: 状态检查字段
│       ├── user_status: 用户状态（ACTIVE/SUSPENDED/DELISTED）
│       ├── suspension_until: 暂停结束时间
│       └── purchase_count: 被购买次数
├── D-3: 搜索间隔控制字段
│   ├── D-3.1: 时间控制字段
│   │   ├── last_search_timestamp: 最后搜索时间戳
│   │   ├── search_interval_minutes: 搜索间隔分钟数（默认SEARCH_INTERVAL_MINUTES=5）
│   │   ├── global_search_cooldown: 全局搜索冷却时间
│   │   └── next_search_allowed_at: 下次允许搜索时间
│   └── D-3.2: 限制配置字段
│       ├── search_rate_limit_enabled: 搜索频率限制开关（默认true）
│       ├── searches_per_hour: 每小时最大搜索次数（默认12）
│       └── daily_search_limit: 每日搜索限制
├── D-4: 脱敏与隐私字段
│   ├── D-4.1: 脱敏配置字段
│   │   ├── privacy_mask_enabled: 隐私脱敏开关（默认true）
│   │   ├── sensitive_fields: 敏感字段列表（姓名、联系方式、地址等）
│   │   └── mask_pattern: 脱敏模式配置
│   └── D-4.2: 信息展示字段
│       ├── show_complete_experience: 显示完整工作经历（默认true）
│       ├── show_education_details: 显示教育背景详情（默认true）
│       └── show_salary_expectation: 显示薪资期望（默认true）
├── D-5: 向量匹配相关字段
│   ├── D-5.1: 匹配算法字段
│   │   ├── vector_similarity_method: 向量相似度计算方法（cosine_similarity）
│   │   ├── matching_threshold: 匹配分数阈值（默认MATCHING_THRESHOLD=0.6）
│   │   └── max_candidates_per_search: 每次搜索最大候选人数（默认MAX_CANDIDATES_PER_SEARCH=2）
│   └── D-5.2: 权重配置字段
│       ├── layer_weights: 七层标签权重配置
│       ├── geographic_weight: 地理位置权重
│       ├── experience_weight: 经验匹配权重
│       └── skills_weight: 技能匹配权重
├── D-6: 点数管理相关字段
│   ├── D-6.1: 购买验证字段
│   │   ├── credit_balance: 雇主账户余额
│   │   ├── credit_cost_per_search: 每次搜索消耗点数（默认CREDIT_COST_PER_SEARCH=2）
│   │   └── minimum_purchase_units: 最小购买单位（默认MINIMUM_PURCHASE_UNITS=10）
│   └── D-6.2: 消费记录字段
│       ├── search_transaction_id: 搜索交易ID
│       ├── credits_consumed: 消费点数
│       └── balance_after_search: 搜索后余额
├── D-7: 新增配置键
│   ├── D-7.1: 搜索优化配置
│   │   ├── vector_cache_enabled: 向量缓存开关（默认true）
│   │   ├── matching_performance_mode: 匹配性能模式（balanced/accuracy/speed）
│   │   └── concurrent_matching_enabled: 并发匹配开关（默认true）
│   └── D-7.2: 用户体验配置
│       ├── stream_output_enabled: 流式输出开关（默认true）
│       ├── search_progress_feedback: 搜索进度反馈（默认true）
│       └── result_display_format: 结果显示格式配置
├── D-8: 标准错误码（统一格式MATCHING/REASON）
│   ├── D-8.1: 搜索相关错误码
│   │   ├── MATCHING/INSUFFICIENT_CREDITS: 账户余额不足
│   │   ├── MATCHING/SEARCH_RATE_LIMIT: 搜索频率超限
│   │   ├── MATCHING/NO_CANDIDATES_FOUND: 未找到匹配候选人
│   │   └── MATCHING/VECTOR_DATA_MISSING: 向量数据缺失
│   └── D-8.2: 过滤相关错误码
│       ├── MATCHING/USER_STATUS_FILTERED: 用户状态被过滤
│       ├── MATCHING/SEARCH_HISTORY_CONFLICT: 搜索历史冲突
│       └── MATCHING/GEOGRAPHIC_DATA_ERROR: 地理数据错误
└── D-9: 受影响的上下游字段联动
    ├── D-9.1: database_agent需同步更新 - search_history_schema, user_status_filters, purchase_transaction_log
    ├── D-9.2: taggings_agent需同步更新 - vector_matching_weights, layer_priority_config, semantic_similarity_params
    ├── D-9.3: auth_agent需同步更新 - employer_search_permissions, credit_authorization, search_rate_limits
    └── D-9.4: frontend_service_agent需同步更新 - search_result_display, privacy_mask_ui, credit_balance_indicator
```

------------------------------

### E: 核心功能特性

```
E: 核心功能特性
├── E-1: 向量相似度匹配
│   ├── E-1.1: 向量调取 - 从database_agent获取候选人、职位、企业的预生成标签向量（七层标签体系）
│   ├── E-1.2: 相似度计算 - 使用cosine_similarity直接计算向量间的相似度（0.0-1.0），转换为匹配分数
│   ├── E-1.3: 地理位置计算 - 唯一需要实时计算的部分，使用地理距离公式计算地理匹配分数
│   ├── E-1.4: 权重应用 - 应用预配置的动态权重策略，根据工作模式调整各维度权重
│   └── E-1.5: 即时匹配 - 向量相似度匹配直接产生最终匹配分数，无需复杂的算法处理
├── E-2: 雇主搜索流式输出机制
│   ├── E-2.1: 双简历并发流式输出 - 每次搜索同时流式输出MAX_CANDIDATES_PER_SEARCH=2份最高匹配分数简历，提升雇主体验效率
│   ├── E-2.2: 脱敏保护 - 自动脱敏姓名、联系方式、住址、出生年月日，保护候选人隐私
│   ├── E-2.3: 完整信息展示 - 显示除脱敏字段外的所有文字信息，包括完整工作经历、教育背景、薪资期望等
│   ├── E-2.4: userID显示机制 - 每份简历末尾显示userID，供雇主联系平台付费获取完整简历
│   └── E-2.5: 全局搜索间隔 - 雇主所有职位搜索共享SEARCH_INTERVAL_MINUTES=5分钟间隔限制，防止频繁搜索影响系统性能
└── E-3: EnrichedTag系统匹配
    ├── E-3.1: 标签分类匹配 - 按权重分类标签（REQUIRED/PREFERRED/CONTEXTUAL），与taggings_agent权重体系完全一致
    ├── E-3.2: 向量相似度匹配 - 基于ChromaDB向量进行标签语义匹配
    ├── E-3.3: 权重计算 - 支持配置化的标签权重和匹配分数算法，动态权重分配机制
    └── E-3.4: 层级匹配 - 支持七层标签体系的分层匹配分析（Layer 0-6）
```

------------------------------

### F: 生产级测试指南

```
F: 生产级测试指南
├── F-1: 向量匹配算法与企业搜索流式输出测试
│   ├── F-1.1: 测试环境准备
│   │   ├── F-1.1.1: 测试数据准备 - 企业文件、职位文件、用户简历、确保数据库中已有预生成的七层标签向量
│   │   └── F-1.1.2: 模块接入说明 - matching_agent是被动调用的业务模块，不包含启动逻辑和测试代码
│   ├── F-1.2: 预期处理步骤验证
│   │   ├── F-1.2.1: 向量数据调取阶段 - 从database_agent获取预生成用户标签向量、获取职位标签向量、验证向量维度一致性
│   │   ├── F-1.2.2: 相似度计算阶段 - ChromaDB向量相似度匹配、地理位置实时计算、动态权重应用
│   │   ├── F-1.2.3: 企业搜索流式输出阶段 - 双简历并发流式输出、脱敏保护机制、完整信息展示、userID显示
│   │   └── F-1.2.4: 搜索限制与历史管理 - 5分钟全局搜索间隔限制、重复候选人过滤、搜索历史管理
│   ├── F-1.3: 测试输出示例 - JSON格式的匹配结果示例，包含状态、匹配结果、流式输出、搜索限制等信息
│   └── F-1.4: 测试验证方法 - 向量匹配验证、脱敏保护验证、流式输出验证、搜索限制验证、地理匹配验证
├── F-2: 付费搜索验证机制
│   ├── F-2.1: 雇主账户余额验证流程 - 雇主发起搜索到检查账户余额到扣除份额度到执行搜索的完整流程
│   └── F-2.2: 账户余额管理规则 - 购买单位、扣除规则、余额显示、充值方式等管理规则
├── F-3: 流式输出实现机制
│   ├── F-3.1: 付费验证后的双简历流式输出流程 - 从雇主搜索触发到双简历并发流式输出的完整流程
│   ├── F-3.2: 脱敏保护标准规范 - 姓名脱敏、联系方式脱敏、住址脱敏、出生信息脱敏、完整保留内容等规范
│   └── F-3.3: 搜索间隔控制机制 - 全局间隔限制、跨职位限制、倒计时提示、历史搜索访问等控制机制
├── F-4: 简历购买与联系方式解锁机制
│   ├── F-4.1: 简历购买流程 - 雇主点击购买按钮到记录购买日志到解锁联系方式的完整流程
│   ├── F-4.2: 联系方式解锁显示 - 解锁内容、显示方式、解锁标识、永久访问等显示机制
│   └── F-4.3: 简历购买统计与下架机制 - 购买计数、自动下架、下架通知、重新激活等机制
├── F-5: 权重体系匹配算法
│   ├── F-5.1: 权重分类标准 - REQUIRED权重、PREFERRED权重、CONTEXTUAL权重的定义和影响
│   └── F-5.2: 基于taggings_agent的三实体向量匹配 - 用户画像向量、企业文化向量、职位要求向量等匹配机制
└── F-6: 向量匹配结果处理
    ├── F-6.1: 分数聚合 - 按预设权重将各层向量匹配分数聚合为最终分数
    ├── F-6.2: 动态权重 - 根据工作模式（remote_allowed/must_onsite）动态调整地理权重
    ├── F-6.3: 阈值过滤 - 应用最低匹配分数阈值过滤低质量匹配
    └── F-6.4: 排序输出 - 按最终匹配分数排序，返回推荐列表
```

------------------------------

### G: 系统架构位置

```
企业搜索请求 → entry_agent → routing_agent → [matching_agent]
                                                  ↓
            预生成标签向量调取 ← → database_agent ← → MongoDB  
                ↓
            cosine_similarity向量匹配 ← → 标签向量库 ← → ChromaDB
                ↓
            匹配分数排序 → 推荐列表 → entry_agent
```

------------------------------

### H: 技术规范约束

```
H: 技术规范约束
├── H-1: Python环境完整规范
│   ├── H-1.1: Python版本 - Python 3.10+（强制）
│   ├── H-1.2: 运行环境 - 支持asyncio异步并发处理
│   ├── H-1.3: 依赖管理 - 使用requirements.txt管理依赖版本
│   └── H-1.4: 资源要求 - 内存1GB+，CPU 1核+（向量检索和相似度计算，非算法计算密集）
├── H-2: Pydantic V2完整规范
│   ├── H-2.1: 必须使用 - model_validate(), model_dump(), Field(), BaseModel
│   ├── H-2.2: 严禁使用 - .dict(), .parse_obj(), .json(), parse_obj_as()
│   ├── H-2.3: 字段验证 - 必须使用pattern=r"regex"，严禁使用regex=r"regex"
│   ├── H-2.4: 模型导入 - 统一从global_schemas导入，禁止本地重复定义
│   └── H-2.5: 模型验证示例 - 从global_schemas导入MatchingResult、CandidateProfile、JobRequirements等模型的使用示例
├── H-3: 异步处理完整规范
│   ├── H-3.1: 必须 - 所有向量检索和相似度计算方法使用async def
│   ├── H-3.2: 禁止 - 同步阻塞操作、threading、multiprocessing
│   ├── H-3.3: 并发 - 使用asyncio.create_task(), asyncio.gather()处理并发向量匹配
│   └── H-3.4: 实现机制 - 使用asyncio.gather()并发处理候选人向量检索，通过database_agent获取预生成标签向量等具体实现机制
├── H-4: 配置管理完整规范
│   ├── H-4.1: 获取方式 - 通过await routing_agent.get_config("matching_agent", config_type)
│   ├── H-4.2: 配置类型 - "vector_matching_config", "weight_strategies", "similarity_thresholds", "geographic_config"
│   ├── H-4.3: 严禁 - 硬编码配置、本地配置文件、环境变量直接读取
│   ├── H-4.4: 热更新 - 支持配置实时更新，无需重启服务
│   └── H-4.5: 配置结构 - 包含向量匹配权重配置、动态权重策略、相似度阈值等核心参数，与taggings_agent权重体系保持一致
├── H-5: LLM调用完整规范
│   ├── H-5.1: 场景限制 - 仅在匹配解释生成时使用LLM
│   ├── H-5.2: 调用方式 - 通过await routing_agent.call_agent("llm_handler_agent", payload)
│   ├── H-5.3: 严禁 - 直接访问OpenAI、Claude、Gemini等API
│   ├── H-5.4: 模型 - 强制使用gpt-4o-2024-08-06
│   └── H-5.5: LLM调用机制 - 从global_config获取匹配解释提示模板，构造包含system_prompt和user_prompt的llm_payload等具体机制
├── H-6: 模块协作完整规范
│   ├── H-6.1: 被动调用 - 仅响应routing_agent的匹配任务分发，不主动运行
│   ├── H-6.2: 无状态 - 完全无状态设计，每次调用独立完成，不保存匹配状态
│   ├── H-6.3: 中枢调度 - 与其他模块交互统一通过await routing_agent.call_agent()
│   ├── H-6.4: 统一入口 - 仅暴露async def run(request: AgentRequest) -> AgentResponse接口
│   ├── H-6.5: 核心数据依赖 - 依赖taggings_agent预生成的七层标签向量，通过database_agent和ChromaDB获取
│   ├── H-6.6: 向量检索协作 - 从database_agent获取用户、职位、企业的预生成标签向量进行相似度匹配
│   └── H-6.7: 无标签生成职责 - 不参与标签生成过程，仅消费taggings_agent的输出结果
├── H-7: 日志记录完整规范
│   ├── H-7.1: 日志框架 - 使用Python标准logging模块
│   ├── H-7.2: 必要字段 - request_id, agent_name, job_id, candidate_count, vector_matching_type, processing_time
│   ├── H-7.3: 结构化 - JSON格式，包含向量匹配过程上下文信息
│   ├── H-7.4: 禁止 - 使用print()进行任何输出
│   └── H-7.5: 日志内容 - 记录request_id、job_id、候选人池大小、向量匹配类型等关键匹配过程信息
├── H-8: 异常处理完整规范
│   ├── H-8.1: 异常类型 - VectorMatchingError, CandidateDataError, GeographicCalculationError
│   ├── H-8.2: 向上传播 - 异常向routing_agent传播，提供详细的错误上下文
│   ├── H-8.3: 用户友好 - 对用户屏蔽详细错误，保留完整日志记录
│   └── H-8.4: 异常处理机制 - VectorMatchingError包含匹配类型和错误详情，通过try-catch捕获向量匹配异常等具体机制
├── H-9: 测试规范完整约束
│   ├── H-9.1: 生产级测试 - 使用真实的候选人标签向量和职位向量进行向量相似度匹配验证
│   ├── H-9.2: 完整流程 - 测试向量获取→cosine_similarity计算→权重聚合→结果排序的完整链路
│   ├── H-9.3: 向量匹配验证 - 验证向量相似度计算的准确性、一致性和ChromaDB检索性能
│   └── H-9.4: 测试覆盖范围 - 完整流程测试、一致性测试、地理计算特殊测试等具体测试范围
└── H-10: 部署规范完整约束
    ├── H-10.1: 环境要求 - Python 3.10+，内存1GB+，CPU 1核+
    ├── H-10.2: 依赖服务 - routing_agent, database_agent, ChromaDB向量数据库, global_config
    ├── H-10.3: 核心依赖 - 依赖taggings_agent预生成的标签向量，通过ChromaDB进行向量检索
    ├── H-10.4: 监控指标 - 向量匹配成功率>98%，响应时间<5秒，匹配准确率>85%，并发处理200+请求/分钟
    └── H-10.5: 健康检查 - ChromaDB连通性验证、向量数据完整性检查、cosine_similarity计算验证
```

------------------------------

### I: 模块架构设计约束

```
I: 模块架构设计约束
├── I-1: 架构设计原则
│   ├── I-1.1: 主入口文件职责 - 仅提供统一接口注册和任务分发能力，不实现具体业务逻辑，保持主文件简洁性和可维护性
│   ├── I-1.2: 业务实现分离 - 所有具体业务功能必须通过独立的业务处理模块实现
│   ├── I-1.3: 模块化组织约束 - 避免单一文件承载过多业务逻辑，按功能域进行合理拆分
│   └── I-1.4: 配置驱动 - 所有匹配算法参数、权重策略、相似度阈值通过routing_agent从global_config动态获取，支持热更新和版本管理
└── I-2: 具体业务功能模块 - 增强标签匹配与语义相似度计算逻辑、动态权重调整与多维度评分算法、地理位置匹配与距离计算处理、匹配结果可视化与解释生成、标签分析解释与推理逻辑等模块需要独立实现
```

------------------------------

### J: 详细运行流程

```
J: 详细运行流程
├── J-1: 完整匹配链路
│   ├── J-1.1: 输入数据提取与验证 - 接收AgentRequest格式的匹配请求、从扁平化字段提取职位信息和搜索参数、验证职位数据的完整性、设置用户上下文到日志系统
│   ├── J-1.2: 候选人池获取 - 验证和清洗搜索参数、构建安全的MongoDB查询、通过routing_agent调用database_agent获取符合条件的候选人
│   ├── J-1.3: 多维度匹配计算 - 技能维度、经验维度、性格维度、地理维度、文化维度等多维度匹配计算
│   ├── J-1.4: EnrichedTag系统匹配 - 从候选人和职位的EnrichedTagProfile中提取所有标签、按意图分类标签、进行标签级别的精确匹配和语义匹配
│   ├── J-1.5: 综合评分计算 - 基于work_mode参数和权重类型动态调整评分策略、REQUIRED标签处理、PREFERRED标签处理、CONTEXTUAL标签处理等具体评分计算
│   ├── J-1.6: 结果排序与过滤 - 按匹配分数降序排列候选人、应用兼容性阈值过滤、应用搜索限制
│   └── J-1.7: 匹配结果格式化 - 生成详细的匹配分析报告、提供推荐等级、包含候选人关键信息摘要和匹配时间戳
└── J-2: ⚠️ 未定义 - 其他详细运行流程步骤需要进一步补充
```

------------------------------

### K: 匹配算法配置

```
K: 匹配算法配置
├── K-1: 动态权重配置系统
│   ├── K-1.1: tag_weight_system - 包含REQUIRED、PREFERRED、CONTEXTUAL三种权重类型的配置
│   ├── K-1.2: work_mode_weights - 包含remote_allowed和must_onsite两种工作模式的权重配置
│   ├── K-1.3: layer_weight_distribution - 七层标签（Layer_0到Layer_6）的权重分配配置
│   └── K-1.4: compatibility_levels - 包含excellent_threshold、good_threshold、fail_threshold等兼容性等级阈值
├── K-2: 权重体系匹配算法 - 基于taggings_agent权重标注的匹配算法实现，包括calculate_weighted_match_score函数和_calculate_tag_group_match函数的详细实现逻辑
├── K-3: 地理位置距离匹配系统
│   ├── K-3.1: 基于预设城市距离关系 - Manila、Pasay/Makati、其他Metro Manila、Cebu等城市的距离值和匹配分数对应关系
│   ├── K-3.2: 计算公式 - geo_score = max(0, 1 - distance_value/10)
│   └── K-3.3: 及格线 - geo_score < 0.3时，必须到岗职位综合分数降至60分以下
└── K-4: 性格适配规则 - 技术职位、管理职位、销售职位等不同职位类型的性格适配规则和默认兼容性设置
```

------------------------------

### L: 匹配结果数据模型

```
L: 匹配结果数据模型
├── L-1: EnrichedMatchResult结构
│   ├── L-1.1: 基本匹配信息 - overall_score, recommendation_level等基本匹配结果信息
│   ├── L-1.2: 权重体系匹配结果 - required_match_details, preferred_match_details, contextual_match_details等权重体系匹配详情
│   ├── L-1.3: 分层匹配结果 - layer_match_scores, layer_match_details等各层级匹配结果
│   └── L-1.4: 传统维度匹配 - component_scores, matching_details, risk_assessment, statistics等传统维度匹配信息
├── L-2: WeightGroupMatchDetail - 权重体系匹配详情模型，包含weight_type、matched_count、total_count、match_percentage、matched_tags、missing_tags、weighted_score等字段
└── L-3: CandidateMatchRecord - 候选人匹配记录模型，包含user_id、candidate_id、name、overall_compatibility_score等完整的候选人匹配信息
```

------------------------------

### M: 安全与性能优化

```
M: 安全与性能优化
├── M-1: 输入验证与安全
│   ├── M-1.1: 字符串清洗 - 移除危险字符和模式，防止注入攻击
│   ├── M-1.2: 参数边界 - 排除候选人ID最多1000个，位置偏好最多50个
│   ├── M-1.3: 类型验证 - 严格的参数类型和格式验证
│   └── M-1.4: 安全查询 - 构建安全的MongoDB查询条件
└── M-2: 性能优化策略
    ├── M-2.1: 异步处理 - 所有数据库查询和匹配算法使用async/await
    ├── M-2.2: 流式处理 - 候选人数据流式处理，避免大量内存占用
    ├── M-2.3: 缓存机制 - 位置兼容性矩阵和配置参数内存缓存
    └── M-2.4: 批量优化 - 支持批量候选人匹配，提升处理效率
```

------------------------------

### N: 开发边界限制

```
N: 开发边界限制（严格遵守）
├── N-1: 适用范围与角色
│   ├── N-1.1: 目标 - 限制自动化生成在文件创建/编辑/依赖方向/接口契约四个维度的自由度，避免脑补
│   └── N-1.2: 占位符映射 - MODULE_NAME为matching_agent、MODULE_ROOT为applications/matching_agent/目录等具体映射关系
├── N-2: 目录与文件边界（文件系统红线）
│   ├── N-2.1: 工作区 - 生成和修改仅允许发生在applications/matching_agent/内
│   ├── N-2.2: 主入口约定 - 模块主入口文件名与matching_agent同名
│   ├── N-2.3: 粒度限制 - 单次变更仅允许操作一个文件；若超过300行，自动截断并停止
│   └── N-2.4: 结构稳定性 - 禁止因实现便利而新建"公共"目录等稳定性要求
├── N-3: 职责分层边界（单一职责红线）
│   ├── N-3.1: Main（主文件）- 只做策略选择、依赖装配、流程编排；禁止任何业务规则、存储访问、外部I/O
│   ├── N-3.2: Adapter（适配层）- 只实现外设与机制；禁止写业务决策
│   ├── N-3.3: Aux（私有实现）- 仅供Main/Adapter内部复用；不得跨模块导出；禁止出现横向依赖
│   └── N-3.4: 拆分触发 - 当单文件同时承担两类以上变更原因或超过200行时必须拆分到对应层
├── N-4: 契约与模型来源（数据红线）
│   ├── N-4.1: 模型唯一来源 - 所有数据模型/Schema一律从global_schemas引入
│   ├── N-4.2: 接口契约 - 本模块README必须提供最小可执行契约
│   └── N-4.3: 版本与兼容 - 任何新增/变更字段必须在README标注语义、默认值、兼容策略
├── N-5: 配置与特性开关（配置红线）
│   ├── N-5.1: 配置唯一来源 - 配置仅可经由routing_agent的global_config读取
│   └── N-5.2: 热更新与回滚 - 配置键名/层级不可私改；新增键必须提供默认值、回滚策略
├── N-6: 外部I/O与状态（副作用红线）
│   ├── N-6.1: 状态存取 - 模块不得直接访问持久化；必须通过指定Adapter间接访问database_agent
│   ├── N-6.2: 副作用隔离 - 任何网络/系统I/O仅可写在Adapter
│   └── N-6.3: 可重复执行 - 生成的任意函数需满足幂等/可重放要求
├── N-7: 并发与资源（执行红线）
│   ├── N-7.1: 并发原语 - 仅允许使用语言原生异步原语；禁止线程池/进程池
│   └── N-7.2: 超时与重试 - 必须经global_config注入；禁止在代码内写死超时/重试参数
├── N-8: 观测与审计（可见性红线）
│   ├── N-8.1: 日志必填字段 - request_id、module_name、operation、duration_ms、success、retry_count
│   ├── N-8.2: 敏感信息 - 日志/错误信息不得包含密钥、令牌、身份证件等敏感信息
│   └── N-8.3: 指标 - 至少暴露调用次数、成功率、时延分布三类指标
├── N-9: 错误与返回（一致性红线）
│   ├── N-9.1: 错误码规范 - 采用MATCHING/{REASON}命名
│   ├── N-9.2: 异常传播 - 只允许抛出仓库标准异常基类及其子类
│   └── N-9.3: 失败回退 - 失败时必须返回可操作指令
├── N-10: 安全与合规（安全红线）
│   ├── N-10.1: 秘钥管理 - 不得在代码/README/示例中出现任何真实秘钥
│   ├── N-10.2: 输入校验 - 所有外部输入必须显式校验
│   └── N-10.3: 权限与最小化 - 输入验证与安全、数据脱敏、算法透明度等安全要求
├── N-11: 测试与验收（交付红线）
│   ├── N-11.1: 最小用例 - 本模块至少提供冒烟链路与失败路径两类用例
│   └── N-11.2: 验收门槛 - 生成变更必须先通过本模块用例再提交
├── N-12: 生成器执行规范（AI行为红线）
│   ├── N-12.1: 部分修改优先 - 每次仅修改一个文件，≤300行
│   ├── N-12.2: 禁止脑补 - 遇到缺失信息，停止输出并在README的"待补要点"清单中列明
│   ├── N-12.3: 依赖单向 - Domain → Adapter单向依赖
│   ├── N-12.4: 不迁移/不重命名/不删除 - 除非README的"迁移方案"明确列出变更映射
│   └── N-12.5: 不新增公共层 - 任何"utils/common/shared"目录新增一律拒绝
├── N-13: 关键词黑名单（检测红线） - 禁止本地业务模型定义、禁止硬编码配置、禁止跨层I/O、禁止并发越界、禁止未脱敏日志等黑名单关键词
└── N-14: "待补要点"机制（歧义兜底） - 必要说明，遇到字段未定义、路径不明、错误码缺失、指标未命名等情况的处理机制
```

------------------------------

### O: 接口契约

```
O: 接口契约
├── O-1: 核心接口规范
│   ├── O-1.1: 统一入口接口 - async def run(request: AgentRequest) -> AgentResponse的完整接口定义
│   └── O-1.2: 支持的任务类型 - candidate_search、job_recommendation、match_analysis、similarity_calculate、health_check等任务类型
├── O-2: 错误码规范
│   ├── O-2.1: 标准错误码格式 - 使用MATCHING/{REASON}命名格式
│   ├── O-2.2: 匹配算法相关错误码 - MATCHING/NO_CANDIDATES、MATCHING/ALGORITHM_FAILED等错误码
│   └── O-2.3: 数据相关错误码 - MATCHING/INVALID_PROFILE、MATCHING/MISSING_VECTORS等错误码
├── O-3: 配置依赖清单
│   ├── O-3.1: 必需配置项 - algorithm_config、threshold_config、vector_config、performance_config等配置项
│   └── O-3.2: 依赖模块清单 - 必须依赖和可选依赖的模块清单
├── O-4: 数据模型规范
│   ├── O-4.1: 必须使用的Schema - 从global_schemas导入的标准模型
│   └── O-4.2: 模块特定Schema - MatchResult、SimilarityScore、CandidateRanking等模块特定模型
├── O-5: 性能指标规范
│   ├── O-5.1: 必须暴露的指标 - matching_agent_requests_total、matching_agent_success_rate等基础指标
│   └── O-5.2: 模块特定指标 - matching_agent_calculations_total、matching_agent_candidate_discovery_rate等特定指标
├── O-6: 最小可执行示例 - 候选人搜索示例的完整代码示例
├── O-7: SLA承诺 - 可用性99.5%、响应时间95%匹配请求<5秒、准确性85%匹配结果用户满意度、吞吐量支持每秒100+匹配请求
└── O-8: 核心接口定义
    ├── O-8.1: 主接口run()方法 - Name、Method、Path/Topic、Minimal Request、Minimal Response、Error Codes等接口定义
    └── O-8.2: 特殊约束 - 匹配算法职责、向量计算、LLM调用约束、质量控制等特殊约束要求
```

------------------------------

### P: 模块契约总结

```
matching_agent作为Career Bot系统的智能匹配核心：

核心职责: 多维度匹配算法、候选人推荐、智能评分、匹配可视化、结果优化
运行模式: 被动调用，无状态设计，异步处理，高并发支持
匹配能力: 七层标签匹配（Layer 0-6），三权重体系评分（REQUIRED/PREFERRED/CONTEXTUAL），地理位置兼容性，MBTI性格适配
架构特性: 向量语义匹配，配置驱动算法，安全输入验证，流式数据处理
严格约束: 无Mock机制，真实匹配结果，安全防护，配置外部化

关键价值:
- 精准匹配: 基于多维度算法的精准候选人职位匹配
- 智能推荐: 语义理解的智能推荐和排序算法
- 可视化分析: 详细的匹配分析报告和可视化图表
- 高性能处理: 支持大规模候选人库的高效匹配计算

该模块是整个Career Bot系统的匹配智能核心，通过先进的算法和数据分析技术，为企业和候选人提供精准的智能匹配服务，实现高效的人才配置和职业发展。
```

------------------------------

### Q: 待补要点

```
Q: 待补要点
├── Q-1: 配置参数待补
│   ├── Q-1.1: 匹配质量评估参数
│   │   ├── 待补键名: matching_confidence_level
│   │   ├── 建议默认值: 0.75（匹配置信度阈值）
│   │   ├── 取值域: 0.0-1.0之间的浮点数
│   │   ├── 影响面: 匹配结果可信度评估，影响推荐质量控制
│   │   └── 最小决策集: 高置信度阈值0.8/中等置信度阈值0.7/低置信度阈值0.6三个选项
│   └── Q-1.2: 向量相似度计算精度控制
│       ├── 待补键名: vector_similarity_precision
│       ├── 建议默认值: 4（小数点后保留位数）
│       ├── 取值域: 正整数1-8
│       ├── 影响面: 匹配分数计算精度，影响排序稳定性
│       └── 最小决策集: 高精度4位小数/中精度3位小数两个选项
├── Q-2: 接口字段待补
│   ├── Q-2.1: 流式输出状态指示字段
│   │   ├── 待补字段名: streaming_status
│   │   ├── 建议类型: enum: ["STREAMING", "COMPLETED", "ERROR"]
│   │   ├── 默认值: "STREAMING"
│   │   ├── 影响面: 前端显示控制，用户体验优化
│   │   └── 最小决策集: 详细状态枚举/简单状态枚举两个选项
│   └── Q-2.2: 匹配分数置信度字段
│       ├── 待补字段名: match_confidence_score
│       ├── 建议类型: float (0.0-1.0)
│       ├── 默认值: 0.0
│       ├── 影响面: 匹配结果可信度显示，业务决策参考
│       └── 最小决策集: 基于多维度综合计算置信度/基于向量相似度直接映射置信度两个选项
├── Q-3: 错误处理待补
│   ├── Q-3.1: 向量数据不完整错误处理
│   │   ├── 待补错误码: MATCHING/INCOMPLETE_VECTOR_DATA
│   │   ├── 错误场景: 候选人或职位的向量数据部分缺失时的处理策略
│   │   ├── 影响面: 搜索结果完整性，用户体验
│   │   └── 最小决策集: 跳过不完整数据/使用默认向量补齐缺失数据/抛出错误要求修复后重试三个选项
│   └── Q-3.2: 超大候选人池处理策略
│       ├── 待补错误码: MATCHING/CANDIDATE_POOL_OVERFLOW
│       ├── 错误场景: 候选人池超过系统处理能力上限
│       ├── 影响面: 系统稳定性，响应时间控制
│       └── 最小决策集: 分批处理返回部分结果/提高匹配阈值减少候选人数量/返回资源不足错误三个选项
└── Q-4: 依赖模块接口待补
    └── Q-4.1: taggings_agent向量数据格式规范
        ├── 待补接口规范: 七层标签向量的数据结构标准化
        ├── 影响面: 向量匹配计算的正确性
        └── 最小决策集: 统一向量维度1536/动态向量维度两个选项
```

------------------------------

### R: ⚠️ 其他未分类内容待补

```
⚠️ 以下内容在原文档中存在但未明确归类，需要后续补充：

R-1: 企业搜索流式输出机制的详细技术实现
R-2: 付费搜索验证机制的具体业务流程
R-3: 简历购买与联系方式解锁的完整技术方案
R-4: 向量匹配算法的性能优化策略
R-5: 多维度匹配计算的算法实现细节
```

