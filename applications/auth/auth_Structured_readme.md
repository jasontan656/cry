# auth_agent_Structured_readme.md

# 字段迁移说明
```
所有数据模型/Schema已迁移至global_schemas.json，由routing_agent动态生成和分发：
- SessionData模型 - 会话数据结构已迁移至global_schemas.json
- UserProfile模型 - 用户信息结构已迁移至global_schemas.json  
- AuthenticationError模型 - 认证错误结构已迁移至global_schemas.json
- ValidationError模型 - 验证错误结构已迁移至global_schemas.json
- ContextData模型 - context.data通信字段已迁移至global_schemas.json

所有配置参数已迁移至global_config.json，由routing_agent统一管理：
- jwt_config、session_config、security_config等已迁移
```

## A: 开发边界与职责说明

### A-1: 模块基本定义

```
auth_agent是Career Bot系统的用户认证与安全管理中心，负责整个用户身份生命周期管理，包括用户注册、身份验证、权限控制、会话管理和安全防护。该模块构建了系统的安全边界，确保只有经过授权的用户能够访问相应的系统资源。采用单账户双激活身份模型，一个邮箱注册用户可同时享受双边服务。
```

------------------------------

### A-2: 核心功能特性

```
├── A-2.1: 用户认证管理
│   ├── A-2.1.1: 传统认证 - 用户名密码认证、邮箱验证、多因子认证
│   ├── A-2.1.2: OAuth第三方登录 - 支持Facebook、Google等第三方登录平台
│   ├── A-2.1.3: JWT令牌管理 - RS256算法签名、令牌刷新和黑名单机制
│   └── A-2.1.4: 会话管理 - 跨设备会话同步、并发会话限制、安全状态跟踪
├── A-2.2: 双身份激活机制
│   ├── A-2.2.1: 求职者身份激活 - 完成求职测试和简历上传激活求职者身份
│   ├── A-2.2.2: 雇主身份激活 - 上传企业资料激活雇主身份
│   ├── A-2.2.3: 身份状态并存 - 支持双身份状态并存显示和无缝切换
│   └── A-2.2.4: 激活周期管理 - 状态转换管理和重新激活机制
├── A-2.3: 安全防护机制
│   ├── A-2.3.1: 密码安全 - bcrypt哈希算法、强密码策略、账户锁定保护
│   ├── A-2.3.2: 登录安全 - 异常登录检测、IP白名单、设备指纹验证
│   ├── A-2.3.3: 权限控制 - RBAC角色权限控制模型、操作级权限验证
│   └── A-2.3.4: 审计追踪 - 完整的认证操作审计日志和安全事件记录
└── A-2.4: 企业认证特例
    ├── A-2.4.1: MVP简化验证 - 采用地址强一致性验证、自动化验证无需人工审核
    ├── A-2.4.2: 双路径认证 - 支持SEC注册和DTI注册两种认证路径
    ├── A-2.4.3: 多公司管理 - 支持用户验证多个企业、需要对话流程选择当前操作企业
    └── A-2.4.4: 对话即时反馈 - 企业认证结果直接在聊天窗口即时显示
```

------------------------------

### A-3: 职责边界定义

```
├── A-3.1: 核心职责范围
│   ├── A-3.1.1: 身份认证 - 验证用户身份的合法性和真实性
│   ├── A-3.1.2: 授权验证 - 检查用户对特定资源的访问权限
│   ├── A-3.1.3: 会话管理 - 维护用户登录状态和会话生命周期
│   ├── A-3.1.4: 安全策略执行 - 执行密码策略、登录限制等安全规则
│   └── A-3.1.5: 用户状态识别 - 对话流程中的精确用户状态识别和路径引导
├── A-3.2: 新增职责范围
│   ├── A-3.2.1: 注册进度跟踪 - 跟踪用户注册和身份激活进度
│   ├── A-3.2.2: 差异化认证管理 - 企业用户与个人用户的差异化认证管理
│   ├── A-3.2.3: 跨Agent状态同步 - 与其他模块协作的用户状态同步
│   └── A-3.2.4: 管理员权限控制 - 系统管理员权限验证和操作控制
├── A-3.3: 职责边界排除
│   ├── A-3.3.1: 不涉及具体业务逻辑处理 - 专注于认证授权，不处理业务规则
│   ├── A-3.3.2: 不负责资源级权限校验 - 只负责用户身份验证，具体资源权限由业务模块处理
│   └── A-3.3.3: 不进行业务数据处理 - 仅处理认证相关数据，不涉及业务数据操作
└── A-3.4: 协作边界
    ├── A-3.4.1: 通过routing_agent与database_agent协作进行用户数据持久化
    ├── A-3.4.2: 通过routing_agent与mail_agent协作完成邮箱验证和密码重置流程
    └── A-3.4.3: 确保认证流程的完整性和安全性
```

------------------------------

## B: 系统架构与模块定义

### B-1: 架构定位与层次

```
├── B-1.1: 系统架构位置
│   └── Frontend → entry_agent → routing_agent → [auth_agent] → database_agent
│                                     ↓
│                               JWT Token Service
│                                     ↓  
│                               Session Management
│                                     ↓
│                               mail_agent (邮箱验证)
├── B-1.2: 模块调用关系
│   ├── B-1.2.1: 被动调用设计 - 仅响应routing_agent的认证任务分发
│   ├── B-1.2.2: 无状态架构 - 完全无状态设计，会话状态存储在Redis/database
│   ├── B-1.2.3: 中枢调度 - 与其他模块交互统一通过routing_agent
│   └── B-1.2.4: 统一入口 - 仅暴露run()方法作为唯一接口
└── B-1.3: 启动与装配
    ├── B-1.3.1: 系统启动 - 使用python main.py --start从boot/启动整个系统
    ├── B-1.3.2: 模块装配 - 通过boot/launcher.py基于applications/__registry__.py装配
    ├── B-1.3.3: 服务调用 - 启动后通过routing_agent进行统一调度
    └── B-1.3.4: 功能测试 - 测试逻辑已迁移至utility_tools/global_test/进行独立管理
```

------------------------------

### B-2: 依赖关系映射

```
├── B-2.1: 上游触发源
│   ├── B-2.1.1: routing_agent - 唯一调用来源，提供身份验证任务分发和配置管理
│   ├── B-2.1.2: entry_agent - 用户注册和登录请求的首次触发入口
│   ├── B-2.1.3: database_agent - 用户状态变更时的身份同步触发
│   └── B-2.1.4: frontend_service_agent - 双身份切换和状态查询请求
├── B-2.2: 下游调用目标
│   ├── B-2.2.1: database_agent - 用户认证信息存储、双身份状态管理、购买计数查询
│   ├── B-2.2.2: mail_agent - 邮箱验证、密码重置、安全通知邮件发送
│   ├── B-2.2.3: matching_agent - 提供用户身份和权限状态用于搜索授权验证
│   └── B-2.2.4: company_identity_agent - 雇主用户身份验证完成后的多公司状态同步
├── B-2.3: 数据流约束
│   ├── B-2.3.1: 双身份独立 - 求职者和雇主身份独立激活，状态互不影响
│   ├── B-2.3.2: 状态转换 - 激活→暂停(2次购买)→下架(10次购买)→重新激活严格顺序
│   ├── B-2.3.3: 购买权限验证 - 雇主购买前检查点数余额和身份激活状态
│   └── B-2.3.4: 企业多公司 - 支持用户关联多个验证企业，需要选择当前操作企业
└── B-2.4: 并发与顺序控制
    ├── B-2.4.1: 身份激活原子性 - 使用分布式锁确保双身份激活操作的原子性
    ├── B-2.4.2: 状态转换一致性 - 确保购买计数和状态转换的严格一致性
    ├── B-2.4.3: 会话管理并发 - 支持跨设备会话同步和冲突处理
    └── B-2.4.4: 身份状态缓存 - 用户双身份状态缓存5分钟，权限变更立即失效
```

------------------------------

## C: 输入输出规范

### C-1: 标准数据格式定义

```
├── C-1.1: 完整AgentRequest输入结构
│   ├── C-1.1.1: 基础请求字段
│   │   ├── request_id: uuid-string - 请求唯一标识符
│   │   ├── task_type: "user_auth" - 统一用户认证任务类型
│   │   ├── user_id: string - 用户标识
│   │   └── timestamp: ISO8601格式时间戳
│   ├── C-1.1.2: 上下文数据结构
│   │   ├── operation字段 - 具体操作类型(user_login/user_register/token_refresh)
│   │   ├── credentials字段 - 用户凭证信息(username/password/login_type)
│   │   ├── oauth_credentials字段 - OAuth第三方登录凭证
│   │   └── registration_data字段 - 用户注册数据
│   └── C-1.1.3: 元数据信息
│       ├── source_agent - 来源模块标识
│       ├── client_ip - 客户端IP地址
│       └── user_agent - 浏览器用户代理信息
├── C-1.2: 完整AgentResponse输出结构
│   ├── C-1.2.1: 基础响应字段
│   │   ├── request_id - 对应的请求标识符
│   │   ├── agent_name: "auth_agent" - 模块名称
│   │   ├── success: boolean - 操作成功状态
│   │   └── timestamp - 响应时间戳
│   ├── C-1.2.2: 响应结果数据
│   │   ├── operation_type - 操作类型标识
│   │   ├── authentication_status - 认证状态
│   │   ├── user_info - 用户基本信息(脱敏后)
│   │   ├── token_info - JWT令牌信息
│   │   └── session_info - 会话信息
│   └── C-1.2.3: 流程控制信息
│       ├── next_intents - 下一步意图数组
│       └── flow_directive - 流程指令
└── C-1.3: OAuth第三方登录数据结构
    ├── C-1.3.1: OAuth登录凭证
    │   ├── provider - OAuth提供商(google/facebook)
    │   ├── authorization_code - 授权码
    │   ├── redirect_uri - 回调URI
    │   └── state - CSRF保护状态参数
    ├── C-1.3.2: OAuth用户信息
    │   ├── oauth_user_id - OAuth用户唯一标识
    │   ├── email - OAuth邮箱地址
    │   ├── email_verified - 邮箱验证状态
    │   ├── name - 用户姓名
    │   └── profile_picture_url - 头像URL
    └── C-1.3.3: OAuth令牌交换
        ├── access_token - OAuth访问令牌
        ├── token_type - 令牌类型(bearer)
        ├── expires_in - 令牌有效期
        └── refresh_token - 刷新令牌(可选)
```

------------------------------

### C-2: 配置获取机制

```
├── C-2.1: JWT令牌配置管理
│   ├── C-2.1.1: 配置键名 - "jwt_config"
│   ├── C-2.1.2: 算法配置 - algorithm(默认RS256)
│   ├── C-2.1.3: 密钥配置 - private_key/public_key
│   ├── C-2.1.4: 过期配置 - access_expire(60分钟)/refresh_expire(30天)
│   └── C-2.1.5: 安全配置 - 时钟偏移容忍、签名验证要求
├── C-2.2: 密码策略配置
│   ├── C-2.2.1: 配置键名 - "password_policy"
│   ├── C-2.2.2: 复杂度要求 - 最小长度、大小写字母、数字、特殊字符要求
│   ├── C-2.2.3: 安全策略 - 最大尝试次数、锁定时长
│   └── C-2.2.4: 加密参数 - bcrypt rounds(≥12)
├── C-2.3: OAuth第三方登录配置
│   ├── C-2.3.1: Facebook登录配置
│   │   ├── 配置键名 - "facebook_oauth"
│   │   ├── 客户端配置 - client_id/client_secret
│   │   ├── 回调配置 - redirect_uri
│   │   └── 权限范围 - scopes["email", "public_profile"]
│   ├── C-2.3.2: Google登录配置
│   │   ├── 配置键名 - "google_oauth"
│   │   ├── 客户端配置 - client_id/client_secret
│   │   ├── 权限范围 - scopes["openid", "email", "profile"]
│   │   └── 地图API - maps_api_key
│   └── C-2.3.3: OAuth安全配置
│       ├── 配置键名 - "oauth_security"
│       ├── 状态参数TTL - state_ttl(10分钟)
│       ├── CSRF保护 - csrf_protection_enabled
│       └── 令牌交换超时 - exchange_timeout(30秒)
└── C-2.4: 会话管理配置
    ├── C-2.4.1: 配置键名 - "session_config"
    ├── C-2.4.2: 并发限制 - max_concurrent_sessions(3个)
    ├── C-2.4.3: 超时设置 - idle_timeout(30分钟)/absolute_timeout(24小时)
    └── C-2.4.4: 清理策略 - cleanup_interval和过期会话清理
```

------------------------------

## D: 配置机制

### D-1: 配置管理体系

```
├── D-1.1: 配置获取方式
│   ├── D-1.1.1: 获取接口 - 通过await routing_agent.get_config("auth_agent", config_type)
│   ├── D-1.1.2: 支持的配置类型 - "jwt_config", "password_policy", "session_config", "security_config"
│   └── D-1.1.3: 热更新支持 - JWT密钥轮换、密码策略调整等配置热更新
├── D-1.2: JWT令牌管理配置
│   ├── D-1.2.1: 核心算法配置
│   │   ├── algorithm: "RS256" - 签名算法
│   │   ├── access_token_expire_minutes: 60 - Access Token有效期
│   │   ├── refresh_token_expire_days: 30 - Refresh Token有效期
│   │   └── clock_skew_seconds: 120 - 时钟偏移容忍
│   ├── D-1.2.2: 密钥管理配置
│   │   ├── private_key - JWT签名私钥
│   │   ├── public_key - JWT验证公钥
│   │   ├── key_rotation_enabled: true - 密钥轮换开关
│   │   └── key_rotation_interval_days: 90 - 密钥轮换间隔
│   └── D-1.2.3: 令牌验证配置
│       ├── issuer: "career-bot-auth" - 令牌签发方
│       ├── audience: "career-bot-services" - 令牌受众
│       └── verify_signature: true - 签名验证要求
├── D-1.3: 会话管理配置参数
│   ├── D-1.3.1: 并发控制配置
│   │   ├── max_concurrent_sessions: 3 - 最大并发会话数
│   │   └── session_conflict_resolution - 设备冲突解决策略
│   ├── D-1.3.2: 超时控制配置
│   │   ├── session_idle_timeout_minutes: 30 - 闲置超时时间
│   │   ├── session_absolute_timeout_hours: 24 - 绝对超时时间
│   │   └── session_renewal_threshold_minutes: 5 - 会话续期阈值
│   └── D-1.3.3: 安全策略配置
│       ├── secure_session_cookies: true - 安全会话Cookie
│       └── session_key_rotation_hours: 6 - 会话密钥轮换间隔
└── D-1.4: 安全策略配置参数
    ├── D-1.4.1: 密码安全配置
    │   ├── bcrypt_rounds: 12 - bcrypt哈希轮数
    │   ├── password_history_count: 5 - 密码历史记录数量
    │   └── password_reset_token_ttl_minutes: 30 - 密码重置令牌有效期
    ├── D-1.4.2: 登录安全配置
    │   ├── max_login_attempts: 5 - 最大登录尝试次数
    │   ├── account_lockout_duration_minutes: 30 - 账户锁定时长
    │   └── captcha_after_fails: 3 - 触发验证码阈值
    └── D-1.4.3: 限流保护配置
        ├── rate_limit_login_per_ip: 30/min - IP登录限流
        ├── rate_limit_register_per_ip: 20/hour - IP注册限流
        └── rate_limit_verify_code_per_user: 10/day - 用户验证码限流
```

------------------------------

## E: 模型路径

### E-1: 数据模型来源与规范

```
├── E-1.1: 全局模型导入规范
│   ├── E-1.1.1: 唯一数据来源 - 所有数据模型/Schema一律从global_schemas引入
│   ├── E-1.1.2: 禁止本地定义 - 禁止在模块内新增/复制业务模型或DTO
│   └── E-1.1.3: 版本兼容性 - 任何新增/变更字段必须同步更新global_schemas对应版本
├── E-1.2: 核心认证模型
│   ├── E-1.2.1: 基础载荷模型
│   │   ├── AgentRequest - 请求载荷模型
│   │   ├── AgentResponse - 响应载荷模型
│   │   └── User - 用户基本信息模型
│   ├── E-1.2.2: 认证专用模型
│   │   ├── UserCredentials - 用户凭证模型
│   │   ├── UserRegistration - 用户注册模型
│   │   ├── AuthToken - 认证令牌模型
│   │   └── TokenInfo - JWT令牌信息模型
│   └── E-1.2.3: OAuth登录模型
│       ├── OAuthLoginCredentials - OAuth登录凭证模型
│       ├── OAuthUserInfo - OAuth用户信息模型
│       └── OAuthTokenExchange - OAuth令牌交换模型
├── E-1.3: 会话与状态模型
│   ├── E-1.3.1: 会话管理模型
│   │   ├── AuthSession - 用户认证会话模型
│   │   └── LoginAttempt - 登录尝试记录模型
│   ├── E-1.3.2: 密码管理模型
│   │   └── PasswordResetToken - 密码重置令牌模型
│   └── E-1.3.3: OAuth状态模型
│       └── OAuthState - OAuth状态管理模型
└── E-1.4: 模型字段映射约束
    ├── E-1.4.1: OAuth字段一致性
    │   ├── oauth_provider → database_agent.user_profiles.oauth_provider
    │   ├── oauth_user_id → database_agent.user_profiles.oauth_user_id
    │   ├── oauth_email_verified → database_agent.user_profiles.oauth_email_verified
    │   └── oauth_profile_data → database_agent.user_profiles.oauth_profile_data
    ├── E-1.4.2: 同步机制要求
    │   └── auth_agent完成OAuth认证后必须将用户OAuth信息同步到database_agent
    └── E-1.4.3: 跨Agent数据一致性
        └── 确保跨Agent的用户身份数据一致性
```

------------------------------

## F: 调用方式

### F-1: 统一调用接口

```
├── F-1.1: 核心入口方法
│   ├── F-1.1.1: 方法签名 - async def run(request: AgentRequest) -> AgentResponse
│   ├── F-1.1.2: 参数说明 - request为扁平化请求载荷，包含request_id、task_type、user_id、session_id、message、intent等直接字段
│   ├── F-1.1.3: 返回值 - AgentResponse扁平化响应载荷，包含success状态、processing_status、results数据、error_details信息
│   └── F-1.1.4: 异常处理 - 抛出AuthenticationError、AuthorizationError、TokenError、ValidationError
├── F-1.2: 支持的任务类型
│   ├── F-1.2.1: 用户认证 - task_type: "user_auth"，统一用户认证任务类型
│   ├── F-1.2.2: 权限验证 - task_type: "permission_check"，用户权限验证
│   ├── F-1.2.3: 会话管理 - task_type: "session_manage"，用户会话管理
│   ├── F-1.2.4: 角色管理 - task_type: "role_manage"，用户角色管理
│   └── F-1.2.5: 健康检查 - task_type: "health_check"，模块健康状态检查
├── F-1.3: 操作类型细分
│   ├── F-1.3.1: 登录操作 - operation: "user_login"，用户登录处理
│   ├── F-1.3.2: 注册操作 - operation: "user_register"，用户注册处理
│   ├── F-1.3.3: 令牌操作 - operation: "token_refresh"，JWT令牌刷新
│   ├── F-1.3.4: 密码操作 - operation: "password_reset"，密码重置处理
│   └── F-1.3.5: OAuth操作 - operation: "oauth_login"，第三方登录处理
└── F-1.4: 调用示例规范
    ├── F-1.4.1: 基础调用模式 - 构建AgentRequest → 调用run方法 → 处理AgentResponse
    ├── F-1.4.2: 成功响应处理 - 提取user_info、token_info、session_info等结果数据
    └── F-1.4.3: 错误响应处理 - 获取error_code和error_message进行异常处理
```

------------------------------

## G: 用户流程

### G-1: 完整对话流程认证支持

```
├── G-1.1: 单账户双激活状态检测
│   ├── G-1.1.1: 求职者身份激活状态检测
│   │   ├── 激活状态检测 - 检查求职者身份激活状态和生命周期
│   │   ├── 状态分类处理
│   │   │   ├── ACTIVE状态 - 激活状态，功能完全可用，正在匹配职位机会
│   │   │   ├── DELISTED状态 - 下架状态，显示重新激活成功提示
│   │   │   ├── incomplete状态 - 部分完成，显示缺失信息列表
│   │   │   └── none状态 - 未激活，显示求职者介绍和引导
│   │   └── 购买次数状态管理 - 基于purchase_count进行状态判断和转换
│   ├── G-1.1.2: 招聘者身份激活状态检测
│   │   ├── 企业验证状态检测 - 检查用户关联的企业验证状态
│   │   ├── 状态分类处理
│   │   │   ├── active状态 - 企业已验证，显示招聘者仪表板
│   │   │   ├── locked_reverify_required状态 - 企业认证过期，需要重新验证
│   │   │   ├── verification_failed状态 - 企业认证失败，显示失败原因
│   │   │   └── none状态 - 未激活，显示招聘者介绍
│   │   └── 多企业管理 - 支持用户验证多个企业，选择当前操作企业
│   └── G-1.1.3: 双身份并存状态统合检测
│       ├── 身份状态统合 - 同时检测求职者和招聘者身份状态
│       ├── UI指令生成 - 确定前端按钮显示逻辑和状态
│       └── 按钮状态管理 - activated/in_progress/unactivated三种状态显示
├── G-1.2: 跨设备会话同步管理
│   ├── G-1.2.1: 设备间状态同步机制
│   │   ├── 会话状态同步 - 同步用户跨设备会话状态和对话状态
│   │   ├── 状态恢复功能 - 恢复到用户上次离开的对话位置
│   │   └── 活跃设备管理 - 维护用户当前活跃设备列表
│   └── G-1.2.2: 会话冲突处理机制
│       ├── 冲突检测 - 检测设备间的会话冲突
│       ├── 选择界面 - 提供"在此设备继续"或"注销其他设备"选项
│       └── 冲突解决 - 根据用户选择处理会话冲突
├── G-1.3: 企业验证与个人认证差异化管理
│   ├── G-1.3.1: 企业认证MVP简化流程
│   │   ├── 验证流程启动 - 显示MVP简化验证要求和必需文档
│   │   ├── 文档类型支持
│   │   │   ├── SEC注册路径 - Latest GIS、Business Permit、SEC Certificate、Articles of Incorporation、BIR 2303
│   │   │   └── DTI注册路径 - DTI BN Certificate、Business Permit、BIR 2303
│   │   ├── 地址一致性验证 - 强制要求公司名称、注册号码、营业地址匹配
│   │   └── 自动化验证模式 - 自动验证无需人工审核，即时返回结果
│   └── G-1.3.2: 多公司管理流程
│       ├── 多公司检测 - 检测用户关联的多个企业
│       ├── 企业选择界面 - 显示企业选择列表供用户选择
│       └── 当前企业设定 - 设定用户当前操作的企业身份
└── G-1.4: 用户路径统计与分析
    ├── G-1.4.1: 认证行为跟踪 - 跟踪用户路径选择和认证行为
    ├── G-1.4.2: 转换模式分析 - 分析用户在不同路径间的转换模式
    └── G-1.4.3: 用户行为记录 - 记录用户操作日志用于行为分析
```

------------------------------

## H: 对话流程

### H-1: 认证对话流程设计

```
⚠️ 未定义 - 具体的对话流程步骤和交互逻辑需要进一步定义
```

------------------------------

## I: 意图识别机制

### I-1: 认证意图识别

```
⚠️ 未定义 - 用户认证相关的意图识别规则和处理机制需要进一步定义
```

------------------------------

## J: 接口结构

### J-1: 核心接口规范

```
├── J-1.1: 统一入口接口
│   ├── J-1.1.1: 接口签名
│   │   ├── 方法名 - async def run(request: AgentRequest) -> AgentResponse
│   │   ├── 参数类型 - AgentRequest扁平化请求载荷
│   │   └── 返回类型 - AgentResponse扁平化响应载荷
│   ├── J-1.1.2: 请求参数结构
│   │   ├── request_id - 请求唯一标识符
│   │   ├── task_type - 任务类型标识("user_auth"/"permission_check"/"session_manage")
│   │   ├── context - 核心任务数据和元数据
│   │   └── additional_params - 可选附加参数
│   ├── J-1.1.3: 响应参数结构
│   │   ├── request_id - 对应请求ID
│   │   ├── agent_name - "auth_agent"
│   │   ├── success - 认证操作成功状态
│   │   ├── timestamp - 响应时间戳
│   │   ├── response - 认证结果数据
│   │   └── error - 错误信息(成功时为null)
│   └── J-1.1.4: 异常处理机制
│       ├── AuthenticationError - 认证失败异常
│       ├── AuthorizationError - 授权失败异常
│       ├── TokenError - JWT令牌相关错误
│       └── ValidationError - 输入参数验证失败
├── J-1.2: 错误码规范体系
│   ├── J-1.2.1: AUTH前缀错误码
│   │   ├── AUTH/INVALID_CREDENTIALS - 用户名密码错误
│   │   ├── AUTH/ACCOUNT_LOCKED - 账户被锁定
│   │   ├── AUTH/TOKEN_EXPIRED - JWT令牌已过期
│   │   ├── AUTH/INSUFFICIENT_PERMISSIONS - 权限不足
│   │   └── AUTH/SESSION_EXPIRED - 会话已过期
│   └── J-1.2.2: OAUTH前缀错误码
│       ├── OAUTH/INVALID_STATE - OAuth状态参数无效
│       ├── OAUTH/AUTHORIZATION_FAILED - OAuth授权失败
│       ├── OAUTH/TOKEN_EXCHANGE_FAILED - OAuth令牌交换失败
│       └── OAUTH/PROVIDER_UNAVAILABLE - OAuth提供商不可用
├── J-1.3: 配置依赖清单
│   ├── J-1.3.1: 必需配置项
│   │   ├── jwt_config - JWT签名密钥、过期时间、算法设置
│   │   ├── password_policy - 密码复杂度、过期策略
│   │   ├── session_config - 会话超时、并发限制
│   │   ├── security_config - 加密设置、防暴力破解参数
│   │   └── email_config - 验证邮件发送配置
│   └── J-1.3.2: 配置获取方式
│       └── await routing_agent.get_config("auth_agent", config_type)
└── J-1.4: 依赖模块清单
    ├── J-1.4.1: 必须依赖
    │   ├── routing_agent - 统一调度和配置管理
    │   ├── global_schemas - 数据模型定义
    │   ├── database_agent - 用户数据存储(通过routing_agent调用)
    │   └── mail_agent - 邮件发送服务(通过routing_agent调用)
    └── J-1.4.2: 第三方依赖
        ├── bcrypt>=4.0.0 - 密码哈希
        ├── PyJWT>=2.8.0 - JWT令牌
        └── cryptography>=41.0.0 - 加密支持
```

------------------------------

## K: 状态管理

### K-1: 用户状态管理机制

```
├── K-1.1: 双身份状态管理
│   ├── K-1.1.1: 身份激活字段
│   │   ├── jobseeker_activated - 求职者身份激活状态(boolean)
│   │   ├── employer_activated - 雇主身份激活状态(boolean)
│   │   ├── jobseeker_activated_at - 求职者激活时间戳
│   │   └── employer_activated_at - 雇主激活时间戳
│   ├── K-1.1.2: 状态枚举定义
│   │   ├── ACTIVE - 激活状态，功能完全可用
│   │   ├── SUSPENDED - 暂停状态，暂时不可被搜索(求职者专用)
│   │   └── DELISTED - 下架状态，完全移出搜索池(求职者专用)
│   └── K-1.1.3: 身份切换管理
│       ├── current_active_identity - 当前激活身份类型
│       └── last_identity_switch - 最后身份切换时间戳
├── K-1.2: 会话状态管理
│   ├── K-1.2.1: 跨设备会话同步
│   │   ├── cross_device_sync_enabled - 跨设备同步开关
│   │   ├── last_dialogue_state - 最后对话状态快照
│   │   ├── session_restore_data - 会话恢复数据
│   │   └── device_conflict_resolution - 设备冲突解决策略
│   └── K-1.2.2: 状态恢复管理
│       ├── dialogue_checkpoint - 对话断点信息
│       ├── ui_state_snapshot - UI状态快照
│       └── restore_target_step - 恢复目标步骤
├── K-1.3: 企业认证状态管理
│   ├── K-1.3.1: 多企业关联管理
│   │   ├── verified_companies - 已验证企业列表数组
│   │   ├── selected_company_id - 当前选择操作的企业ID
│   │   └── company_switch_history - 企业切换历史记录
│   └── K-1.3.2: 企业选择配置
│       ├── company_selection_required - 是否需要选择企业(默认true)
│       ├── default_company_behavior - 默认企业选择行为
│       └── multi_company_enabled - 多企业功能开关
└── K-1.4: 状态缓存与一致性
    ├── K-1.4.1: 缓存策略
    │   ├── 身份状态缓存5分钟，权限变更立即失效
    │   ├── 用户权限信息缓存5分钟，提升认证性能
    │   └── 登录历史维护用于异常检测和安全分析
    ├── K-1.4.2: 去重机制
    │   ├── 会话去重防止同一用户并发登录产生多个有效会话冲突
    │   └── 企业切换时需要明确当前操作企业身份
    └── K-1.4.3: 并发控制
        ├── 身份激活原子性使用分布式锁确保双身份激活操作的原子性
        └── 状态转换一致性确保购买计数和状态转换的严格一致性
```

------------------------------

## L: 日志与异常策略

### L-1: 错误处理与技术支持策略

```
├── L-1.1: 统一重试机制
│   ├── L-1.1.1: 重试策略 - 所有认证失败情况统一要求重新尝试操作
│   ├── L-1.1.2: 零容错简化处理 - 网络错误、验证失败等所有异常统一返回失败状态
│   └── L-1.1.3: 智能重试算法 - 瞬时性错误采用指数退避算法和熔断保护机制
├── L-1.2: 用户友好反馈机制
│   ├── L-1.2.1: 明确失败原因 - 提供明确失败原因和重新操作指导
│   ├── L-1.2.2: 一键技术支持邮件 - 如果用户碰到无法处理的问题，提供support@4waysgroup.com邮件联系方式
│   └── L-1.2.3: 自动邮件模板 - 自动收集认证问题信息，生成技术支持邮件模板供用户复制发送
├── L-1.3: 错误分类与处置策略
│   ├── L-1.3.1: 瞬时性错误处理
│   │   ├── 网络抖动、服务短暂不可用、限流触发等临时性问题
│   │   ├── 智能重试策略，包含退避算法和熔断保护机制
│   │   └── 429限流触发采用指数退避算法加随机抖动重试最多3次
│   ├── L-1.3.2: 永久性错误处理
│   │   ├── 凭证错误、权限不足、签名无效、配置错误等结构性问题
│   │   ├── 立即失败并提供明确的修复指引
│   │   └── 不修正数据或配置无法解决的问题
│   └── L-1.3.3: 具体错误处置清单
│       ├── 400/422参数不合法 - 立即失败，返回具体参数错误信息和正确格式示例
│       ├── 401认证失败 - expired_token静默刷新，invalid_token直接失败引导重新登录
│       ├── 403权限不足 - 立即失败，提供权限申请路径或账户切换建议
│       ├── 404路由错误 - 立即失败并触发系统报警
│       └── 5xx服务器错误 - 仅对幂等请求自动重试最多3次
└── L-1.4: 日志记录与审计策略
    ├── L-1.4.1: 必填日志字段
    │   ├── request_id - 请求唯一标识
    │   ├── module_name - 模块名称
    │   ├── operation - 操作类型
    │   ├── duration_ms - 执行时长
    │   ├── success - 成功状态
    │   └── retry_count - 重试次数
    ├── L-1.4.2: 敏感信息脱敏
    │   ├── 密码、令牌、身份证件不写入任何日志文件
    │   ├── 邮箱全量、手机号全量等必要时脱敏
    │   └── 仅记录操作结果，避免敏感数据泄露
    └── L-1.4.3: 审计日志管理
        ├── 关键操作审计 - 登录失败记录、管理员操作追踪、令牌操作审计
        ├── 数据保留策略 - 审计日志保留90天后自动清理
        └── 合规要求 - 符合GDPR、CCPA标准的数据保护
```

------------------------------

## M: WebSocket / LLM / 上传机制等集成接口

### M-1: 外部系统集成接口

```
├── M-1.1: LLM集成接口
│   ├── M-1.1.1: 调用场景限制 - auth_agent主要不使用LLM，仅在安全威胁分析、异常行为检测等特殊情况下调用
│   ├── M-1.1.2: 调用方式 - 通过routing_agent调用llm_handler_agent
│   └── M-1.1.3: 安全分析Prompt - 异常行为分析prompt用于紧急情况的安全威胁分析
├── M-1.2: 邮件服务集成
│   ├── M-1.2.1: 邮箱验证邮件发送流程
│   │   ├── 验证码生成 - 生成6位数字验证码，有效期10分钟
│   │   ├── 邮件任务创建 - 通过routing_agent向mail_agent发送邮件任务
│   │   ├── 邮件内容标准 - 包含验证码、有效期、安全提醒等标准内容
│   │   └── 发送确认 - 接收mail_agent的发送状态反馈，记录邮件发送结果
│   ├── M-1.2.2: 密码重置邮件流程
│   │   ├── 重置令牌生成 - 生成安全的密码重置令牌，有效期30分钟
│   │   ├── 邮件通知发送 - 发送包含重置链接的安全邮件
│   │   ├── 链接验证机制 - 验证重置链接的有效性和安全性
│   │   └── 状态跟踪 - 跟踪重置邮件的发送和使用状态
│   └── M-1.2.3: 安全通知邮件触发
│       ├── 异常登录通知 - 检测到异常IP或设备登录时发送警告邮件
│       ├── 权限变更通知 - 管理员角色变更、重要权限修改时发送通知
│       └── 账户安全通知 - 密码修改、双因素认证变更等安全事件通知
├── M-1.3: 数据库集成接口
│   ├── M-1.3.1: 用户数据集成 - 用户账户信息存储和查询、密码哈希验证和更新
│   ├── M-1.3.2: 会话数据管理 - 会话信息和审计日志存储
│   └── M-1.3.3: JWT令牌黑名单管理 - 令牌撤销和黑名单维护、过期令牌自动清理
└── M-1.4: 第三方OAuth集成
    ├── M-1.4.1: Facebook登录集成
    │   ├── 客户端配置 - client_id: 1364332831428891, client_secret配置
    │   ├── 权限范围 - scopes["email", "public_profile"]
    │   └── API版本 - api_version: "v18.0"
    ├── M-1.4.2: Google登录集成
    │   ├── 客户端配置 - client_id配置, client_secret配置
    │   ├── 权限范围 - scopes["openid", "email", "profile"]
    │   └── 地图API支持 - maps_api_key集成
    └── M-1.4.3: OAuth安全管理
        ├── CSRF保护 - state参数TTL 10分钟，csrf_protection_enabled
        ├── 令牌交换 - token_exchange_timeout 30秒
        └── 用户信息缓存 - userinfo_cache TTL 5分钟
```

------------------------------

## N: 环境配置

### N-1: 部署环境要求

```
├── N-1.1: 基础环境要求
│   ├── N-1.1.1: Python版本要求 - Python 3.10+(强制要求)
│   ├── N-1.1.2: 核心依赖库 - routing_agent, global_schemas, bcrypt, PyJWT
│   ├── N-1.1.3: 安全要求 - RSA密钥对、环境变量加密
│   └── N-1.1.4: 资源要求 - 内存512MB+, CPU 1核+
├── N-1.2: 第三方库版本约束
│   ├── N-1.2.1: 安全相关库
│   │   ├── bcrypt>=4.0.0 - 密码哈希算法
│   │   ├── PyJWT>=2.8.0 - JWT令牌处理
│   │   ├── cryptography>=41.0.0 - 加密支持
│   │   └── passlib>=1.7.4 - 密码工具库
│   └── N-1.2.2: 异步支持
│       └── asyncio - Python内置异步支持
├── N-1.3: 配置开关与默认值
│   ├── N-1.3.1: 密码与登录配置
│   │   ├── auth.password.bcrypt_cost=12 - bcrypt成本因子
│   │   ├── auth.login.max_fail=5 - 最大失败次数
│   │   ├── auth.login.lock_minutes=30 - 锁定时长
│   │   └── auth.login.captcha_after_fails=3 - 触发验证码阈值
│   ├── N-1.3.2: JWT令牌配置
│   │   ├── jwt.alg=RS256 - 签名算法
│   │   ├── jwt.access_ttl=60m - Access Token有效期
│   │   ├── jwt.refresh_ttl=30d - Refresh Token有效期
│   │   ├── jwt.clock_skew=120s - 时钟偏移容忍
│   │   └── jwt.blacklist.cleanup_interval=1h - 黑名单清理间隔
│   ├── N-1.3.3: 会话与限流配置
│   │   ├── session.max_concurrent=3 - 最大并发会话
│   │   ├── session.idle_timeout=30m - 闲置超时
│   │   ├── rate.limit.login_per_ip=30/min - IP登录限流
│   │   ├── rate.limit.register_per_ip=20/hour - IP注册限流
│   │   └── rate.limit.verify_code_per_user=10/day - 用户验证码限流
│   └── N-1.3.4: 功能开关配置
│       ├── feature.degrade_on=false - 降级模式开关
│       ├── feature.email_verification.required=true - 强制邮箱验证
│       ├── feature.oauth.facebook.enabled=true - Facebook登录开关
│       ├── feature.oauth.google.enabled=true - Google登录开关
│       └── feature.admin.double_confirm=true - 管理员操作二次确认
└── N-1.4: 监控指标设置
    ├── N-1.4.1: 必须暴露的指标
    │   ├── auth_agent_requests_total - 调用次数指标
    │   ├── auth_agent_success_rate - 成功率指标
    │   └── auth_agent_duration_seconds - 时延分布指标
    ├── N-1.4.2: 模块特定指标
    │   ├── auth_agent_login_attempts_total - 登录尝试次数
    │   ├── auth_agent_authentication_success_rate - 认证成功率
    │   └── auth_agent_token_refresh_total - 令牌刷新次数
    └── N-1.4.3: SLO保障目标
        ├── 登录成功率SLO目标≥99.5% - 5分钟窗口内成功率监控
        ├── Token刷新失败率目标<1% - 连续失败超过阈值自动降级
        ├── 邮箱退信率监控>2%触发报警 - 检查邮件服务状态
        └── 第三方IdP熔断 - Facebook/Google等IdP连续5次5xx错误触发60秒熔断保护
```

------------------------------

## O: 运行要求

### O-1: 系统运行要求

```
├── O-1.1: 技术规范完整约束
│   ├── O-1.1.1: Pydantic V2完整规范
│   │   ├── 必须使用 - model_validate(), model_dump(), Field(), BaseModel
│   │   ├── 严禁使用 - .dict(), .parse_obj(), .json(), parse_obj_as()
│   │   ├── 字段验证 - 必须使用pattern=r"regex"，严禁使用regex=r"regex"
│   │   └── 模型导入 - 统一从global_schemas导入，禁止本地重复定义
│   ├── O-1.1.2: 异步处理完整规范
│   │   ├── 异步方法要求 - 所有认证方法使用async def
│   │   ├── 同步操作禁止 - 禁止同步阻塞操作、threading、multiprocessing
│   │   └── 并发处理 - 使用asyncio.create_task(), asyncio.gather()处理并发认证
│   └── O-1.1.3: 安全规范完整约束
│       ├── 密码加密 - 使用bcrypt哈希算法，salt rounds ≥ 12
│       ├── JWT令牌 - RS256算法签名，支持令牌刷新和黑名单
│       ├── 会话管理 - 安全的会话令牌生成、存储和验证
│       └── 权限控制 - RBAC角色权限控制模型
├── O-1.2: 模块协作完整规范
│   ├── O-1.2.1: 被动调用原则 - 仅响应routing_agent的认证任务分发
│   ├── O-1.2.2: 无状态设计 - 完全无状态设计，会话状态存储在Redis/database
│   ├── O-1.2.3: 中枢调度 - 与其他模块交互统一通过routing_agent
│   └── O-1.2.4: 统一入口 - 仅暴露run()方法作为唯一接口
└── O-1.3: 性能边界约束
    ├── O-1.3.1: 并发处理能力
    │   ├── 并发认证 - 最大1000个并发请求
    │   ├── 令牌缓存 - 活跃令牌最大10000个
    │   ├── 会话存储 - Redis最大容量100MB
    │   └── 黑名单大小 - JWT黑名单最大50000条目
    ├── O-1.3.2: 响应时间要求
    │   ├── 认证成功率 - >99%(排除恶意尝试)
    │   ├── 响应时间 - 95%请求<200ms
    │   └── 安全事件监控 - 异常登录、暴力破解监控
    └── O-1.3.3: 数据处理约束
        ├── 审计日志保留 - 保留90天，自动清理
        ├── 数据隐私保护 - 密码、令牌不记录在日志中
        └── 访问控制严格 - RBAC严格权限控制，符合GDPR、CCPA标准
```

------------------------------

## P: 版本依赖

### P-1: 依赖关系清单

```
├── P-1.1: 上游依赖服务
│   ├── P-1.1.1: routing_agent - 任务调度和配置管理
│   ├── P-1.1.2: global_schemas - 认证数据模型
│   └── P-1.1.3: 全局配置系统 - JWT密钥、安全策略
├── P-1.2: 下游服务依赖
│   ├── P-1.2.1: database_agent - 用户数据存储
│   ├── P-1.2.2: mail_agent - 邮件通知服务
│   └── P-1.2.3: 缓存服务 - JWT黑名单、会话缓存
├── P-1.3: 第三方库版本管理
│   ├── P-1.3.1: 核心安全库
│   │   ├── bcrypt>=4.0.0 - 密码哈希处理
│   │   ├── PyJWT>=2.8.0 - JWT令牌管理
│   │   ├── cryptography>=41.0.0 - 加密算法支持
│   │   └── passlib>=1.7.4 - 密码处理工具
│   └── P-1.3.2: 异步支持库
│       └── asyncio - Python内置异步处理
└── P-1.4: 版本兼容性管理
    ├── P-1.4.1: 向后兼容要求 - 确保新版本与现有API兼容
    ├── P-1.4.2: 升级路径规划 - 提供清晰的版本升级路径和迁移指南
    └── P-1.4.3: 依赖更新策略 - 定期更新安全库版本，确保安全性
```

------------------------------

## Q: 模块限制

### Q-1: 开发边界限制(严格遵守)

```
├── Q-1.1: 适用范围与角色
│   ├── Q-1.1.1: 目标限制 - 限制自动化生成在文件创建/编辑/依赖方向/接口契约四个维度的自由度
│   ├── Q-1.1.2: 占位符映射
│   │   ├── MODULE_NAME: auth_agent
│   │   ├── MODULE_ROOT: applications/auth_agent/目录
│   │   ├── GLOBAL_SCHEMAS: global_schemas模块(通过routing_agent统一管理)
│   │   ├── GLOBAL_CONFIG: routing_agent的config_manager服务
│   │   └── STATE_STORE: database_agent统一管理的存储层
│   └── Q-1.1.3: 避免脑补原则 - 遇到缺失信息时停止输出并在待补要点清单中列明
├── Q-1.2: 目录与文件边界(文件系统红线)
│   ├── Q-1.2.1: 工作区限制 - 生成和修改仅允许发生在applications/auth_agent/内
│   ├── Q-1.2.2: 主入口约定 - 模块主入口文件名与auth_agent同名
│   ├── Q-1.2.3: 粒度限制 - 单次变更仅允许操作一个文件，超过300行自动截断
│   └── Q-1.2.4: 结构稳定性 - 禁止因实现便利而新建"公共"目录
├── Q-1.3: 职责分层边界(单一职责红线)
│   ├── Q-1.3.1: Main主文件职责 - 只做策略选择、依赖装配、流程编排
│   ├── Q-1.3.2: Adapter适配层职责 - 只实现外设与机制，禁止写业务决策
│   ├── Q-1.3.3: Aux私有实现职责 - 仅供Main/Adapter内部复用，不得跨模块导出
│   └── Q-1.3.4: 拆分触发条件 - 单文件承担两类以上变更原因或超过200行时必须拆分
├── Q-1.4: 契约与模型来源(数据红线)
│   ├── Q-1.4.1: 模型唯一来源 - 所有数据模型/Schema一律从global_schemas引入
│   ├── Q-1.4.2: 接口契约要求 - 必须提供最小可执行契约，仅声明入参/出参/错误码
│   └── Q-1.4.3: 版本兼容管理 - 新增/变更字段必须标注语义、默认值、兼容策略
└── Q-1.5: 安全与合规约束(安全红线)
    ├── Q-1.5.1: 密钥管理约束 - 不得在代码/README/示例中出现任何真实秘钥
    ├── Q-1.5.2: 输入校验约束 - 所有外部输入必须显式校验(长度/类型/枚举/格式)
    ├── Q-1.5.3: 权限最小化约束
    │   ├── 密码强制加密 - 使用bcrypt哈希算法，salt rounds ≥ 12
    │   ├── JWT令牌安全 - RS256算法签名，支持令牌刷新和黑名单
    │   ├── 会话管理 - 安全的会话令牌生成、存储和验证
    │   └── 权限控制 - RBAC角色权限控制模型
    └── Q-1.5.4: 审计日志约束 - 完整的认证操作审计日志记录
```

------------------------------

## R: 测试策略

### R-1: 测试环境认证机制(E2E专用)

```
├── R-1.1: 测试模式邮件验证绕过
│   ├── R-1.1.1: 测试接口设计规范
│   │   ├── 测试模式标识 - 通过ENV=test环境变量激活测试专用接口
│   │   ├── 安全限制 - 测试接口仅在测试环境可用，生产环境严格禁用
│   │   └── 邮件验证模拟 - 支持邮件验证码模拟提取和自动化测试流程
│   ├── R-1.1.2: 测试专用邮件验证API
│   │   ├── 验证码生成 - 生成测试验证码(固定6位数字)
│   │   ├── 邮箱验证跳过 - 直接标记邮箱为已验证(跳过真实邮件发送)
│   │   └── 测试码返回 - 返回验证码供测试脚本使用
│   └── R-1.1.3: 测试用户注册快速通道
│       ├── 快速账户创建 - 跳过邮件验证，直接创建已激活账户
│       ├── 自动令牌生成 - 自动生成JWT令牌
│       └── 测试账户标记 - 标记为测试账户便于后续清理
├── R-1.2: 第三方登录测试机制
│   ├── R-1.2.1: Google登录测试Token验证 - 仅验证接口连通性，不进行完整OAuth流程
│   ├── R-1.2.2: Facebook登录测试Token验证 - 仅验证接口连通性，不进行完整OAuth流程
│   └── R-1.2.3: OAuth配置测试 - 测试OAuth配置有效性和API连通性
├── R-1.3: 生产级测试要求
│   ├── R-1.3.1: 真实认证测试 - 使用真实的JWT签名、bcrypt哈希进行测试
│   ├── R-1.3.2: 完整流程测试 - 测试注册→验证→登录→权限检查的完整流程
│   ├── R-1.3.3: OAuth集成测试 - 测试Facebook/Google登录的完整授权流程
│   ├── R-1.3.4: 邮件验证测试 - 与mail_agent协作测试验证码发送和验证
│   ├── R-1.3.5: 安全测试 - 测试各种攻击场景和安全防护机制
│   └── R-1.3.6: 并发测试 - 测试高并发认证的正确性和性能
└── R-1.4: 关键测试用例
    ├── R-1.4.1: 用户登录流程测试 - 测试完整登录流程和令牌生成
    ├── R-1.4.2: JWT令牌验证测试 - 测试令牌验证和生命周期管理
    ├── R-1.4.3: OAuth登录流程测试 - 测试第三方登录完整流程
    └── R-1.4.4: 邮件验证协作测试 - 测试与mail_agent的邮箱验证协作
```

------------------------------

## S: 验收机制

### S-1: SLA承诺与验收标准

```
├── S-1.1: 核心SLA指标
│   ├── S-1.1.1: 可用性保障 - 99.9%服务可用性
│   ├── S-1.1.2: 响应时间保障 - 95%请求<200ms响应
│   ├── S-1.1.3: 安全保障 - 零认证漏洞容忍度
│   └── S-1.1.4: 认证准确性 - 100%认证结果准确性
├── S-1.2: 验收门槛标准
│   ├── S-1.2.1: 最小用例要求 - 本模块至少提供冒烟链路与失败路径两类用例
│   ├── S-1.2.2: 用例限制 - 用例不得Mock掉对外契约(可Mock外设)
│   └── S-1.2.3: 通过门槛 - 生成变更必须先通过本模块用例再提交
├── S-1.3: 安全验收标准
│   ├── S-1.3.1: 密码策略验收 - 最少8位，包含大小写字母、数字、特殊字符
│   ├── S-1.3.2: JWT安全验收 - RS256签名，私钥安全存储，支持轮换
│   ├── S-1.3.3: 会话安全验收 - 最大3个并发会话，30分钟闲置超时
│   ├── S-1.3.4: 登录限制验收 - 5次失败锁定30分钟，IP黑名单支持
│   └── S-1.3.5: 数据加密验收 - 密码bcrypt哈希(≥12 rounds)
└── S-1.4: 性能验收标准
    ├── S-1.4.1: 并发认证验收 - 最大1000个并发请求
    ├── S-1.4.2: 令牌缓存验收 - 活跃令牌最大10000个
    ├── S-1.4.3: 会话存储验收 - Redis最大容量100MB
    └── S-1.4.4: 黑名单验收 - JWT黑名单最大50000条目
```

------------------------------

## T: 部署策略

### T-1: 部署与运维策略

```
├── T-1.1: 部署环境配置
│   ├── T-1.1.1: 环境要求 - Python 3.10+, 内存512MB+, CPU 1核+
│   ├── T-1.1.2: 依赖管理 - routing_agent, global_schemas, bcrypt, PyJWT
│   └── T-1.1.3: 安全配置 - RSA密钥对、环境变量加密
├── T-1.2: 故障诊断与调试
│   ├── T-1.2.1: JWT令牌验证失败诊断 - 检查令牌格式、签名密钥、时间同步
│   ├── T-1.2.2: 用户无法登录诊断 - 检查账户状态、密码哈希、数据库连接
│   └── T-1.2.3: 会话管理异常诊断 - 检查会话存储、Redis连接、过期策略
└── T-1.3: 监控与告警配置
    ├── T-1.3.1: 实时监控机制
    │   ├── 异常登录监控 - 检测异常IP、异常时间、异常设备等登录模式
    │   └── 认证性能监控 - 跟踪认证响应时间、成功率、错误分布
    └── T-1.3.2: 安全配置检查清单
        ├── JWT密钥轮换机制启用
        ├── 密码哈希强度≥12 rounds
        ├── 账户锁定策略配置
        ├── 会话超时策略设置
        └── 审计日志记录完整
```

------------------------------

## U: 未来规划

### U-1: 功能扩展规划

```
├── U-1.1: 双身份系统增强
│   ├── U-1.1.1: 身份管理配置扩展
│   │   ├── dual_identity_enabled - 双身份功能开关(默认true)
│   │   ├── identity_switch_cooldown - 身份切换冷却时间(默认0)
│   │   └── auto_identity_detection - 自动身份检测开关(默认true)
│   └── U-1.1.2: 状态转换配置优化
│       ├── suspension_notification_enabled - 暂停通知开关(默认false)
│       ├── reactivation_simplified - 简化重新激活开关(默认true)
│       └── state_transition_logging - 状态转换日志记录(默认true)
├── U-1.2: 管理员权限系统扩展
│   ├── U-1.2.1: 预设管理员配置 - jason.tan656@gmail.com为不可删除的超级管理员
│   ├── U-1.2.2: admin权限扩展 - 管理用户角色、雇主充值、企业认证状态、标签审核
│   └── U-1.2.3: 操作审计增强 - 所有管理员操作记录完整审计日志
└── U-1.3: 安全机制增强
    ├── U-1.3.1: 新增错误码支持
    │   ├── AUTH/IDENTITY_NOT_ACTIVATED - 身份未激活
    │   ├── AUTH/DUAL_IDENTITY_CONFLICT - 双身份冲突
    │   ├── AUTH/COMPANY_SELECTION_REQUIRED - 需要选择企业
    │   └── AUTH/INSUFFICIENT_CREDITS - 点数不足无法操作
    └── U-1.3.2: 企业认证错误码
        ├── AUTH/COMPANY_NOT_VERIFIED - 企业未验证
        ├── AUTH/MULTI_COMPANY_CONFLICT - 多企业冲突
        └── AUTH/COMPANY_VERIFICATION_FAILED - 企业验证失败
```

------------------------------

## V: 未定义项

### V-1: 需要补充定义的功能项

```
├── V-1.1: 对话流程设计
│   └── ⚠️ 未定义 - 具体的对话流程步骤和交互逻辑需要进一步定义
├── V-1.2: 意图识别机制
│   └── ⚠️ 未定义 - 用户认证相关的意图识别规则和处理机制需要进一步定义
├── V-1.3: 企业认证具体实现
│   └── ⚠️ 未定义 - 企业认证MVP具体的文档解析和验证算法需要进一步定义
└── V-1.4: 多设备冲突处理细节
    └── ⚠️ 未定义 - 跨设备会话冲突的具体检测算法和处理策略需要进一步定义
```

------------------------------

## W: 待补要点

### W-1: 未能定稿的配置键名

```
├── W-1.1: OAuth回调域名白名单
│   ├── 配置键名 - allowed_redirect_domains的完整域名列表
│   ├── 建议值 - ["yourdomain.com", "localhost:3000", "localhost:8080"]
│   └── 影响面 - 第三方登录集成测试、生产环境域名配置
├── W-1.2: 管理员邮箱配置
│   ├── 配置问题 - 预设管理员邮箱是否可通过配置修改
│   └── 影响面 - 系统安全架构
└── W-1.3: 企业认证文档类型
    ├── 配置缺失 - SEC/DTI认证路径的具体文档类型枚举定义
    └── 影响面 - 企业认证流程实现
```

------------------------------

### W-2: 未能定稿的数值阈值

```
├── W-2.1: 权限缓存TTL协调
│   ├── 问题描述 - 5分钟权限缓存与30分钟会话超时的协调机制
│   ├── 建议方案 - 权限5分钟、会话30分钟、分层缓存
│   └── 影响面 - 认证性能和安全一致性
└── W-2.2: OAuth状态令牌TTL
    ├── 问题描述 - 10分钟是否适用于所有OAuth提供商
    └── 影响面 - 第三方登录体验
```

------------------------------

### W-3: 未能定稿的字段映射

```
├── W-3.1: incomplete状态枚举
│   ├── 当前状态 - 使用"incomplete"字符串
│   ├── 统一建议 - 是否应统一为INCOMPLETE大写枚举
│   └── 影响面 - 状态检测逻辑、database_agent存储结构
└── W-3.2: role字段枚举
    ├── 当前状态 - "jobseeker"/"employer"枚举值
    ├── 兼容性问题 - 是否需要"job_seeker"/"recruiter"别名支持
    └── 影响面 - API文档、前端显示文案、邮件模板内容
```

------------------------------

## X: 黑名单

### X-1: 关键词黑名单(检测红线)

```
├── X-1.1: 禁止本地业务模型定义
│   ├── "class .*Model" - 禁止定义本地模型类
│   ├── "data class .*" - 禁止数据类定义
│   └── "interface .*DTO" - 禁止接口DTO定义
├── X-1.2: 禁止硬编码配置
│   ├── "API_KEY=" - 禁止硬编码API密钥
│   ├── "timeout\\s*=\\s*\\d+" - 禁止硬编码超时值
│   └── "retry\\s*=\\s*\\d+" - 禁止硬编码重试次数
├── X-1.3: 禁止跨层I/O
│   ├── 在Main/Aux中禁止 - "http", "db", "sql", "open(", "requests", "fetch"
│   └── I/O隔离要求 - 任何网络/系统I/O仅可写在Adapter
├── X-1.4: 禁止并发越界
│   ├── "Thread", "Process", "fork", "Pool" - 禁止线程和进程池
│   └── 仅允许异步原语 - async/await、事件循环
└── X-1.5: 禁止未脱敏日志
    ├── "print(" - 禁止直接打印
    ├── "console.log(" - 禁止控制台日志
    └── "logging.info(f\\".*password|token|secret" - 禁止敏感信息日志
```

------------------------------

## Y: 禁用规则

### Y-1: 坚决避免的反模式

```
├── Y-1.1: 权限校验误区
│   ├── 职责混淆 - auth_agent只负责"用户是否已登录"认证
│   └── 授权区分 - 不负责"用户是否能访问特定资源"的授权校验
├── Y-1.2: 令牌安全误区
│   ├── 算法禁止 - 坚决不使用HS256对称加密算法
│   ├── 有效期限制 - 不设置过长的Access Token有效期(>2小时)
│   └── 安全风险 - 避免令牌被盗用的安全风险
├── Y-1.3: 重试策略误区
│   ├── 无限重试禁止 - 遇到429限流或5xx错误时不进行无限重试
│   └── 熔断机制 - 必须设置最大重试次数和熔断机制
└── Y-1.4: 降级策略误区
    ├── 安全约束 - 系统降级不等于"放宽权限验证"
    └── 安全检查 - 任何情况下都不能绕过必要的安全检查
```

------------------------------

## 📋 模块契约总结

**🎯 核心职责**: 身份认证、权限验证、会话管理、安全防护、JWT令牌管理  
**🔄 运行模式**: 被动调用、无状态设计、安全优先、高可用架构  
**📊 处理能力**: 高并发认证、多重安全验证、智能威胁检测、权限动态控制  
**🏗️ 架构特性**: JWT无状态认证、RBAC权限模型、多层安全防护、审计追踪  
**⚠️ 严格约束**: 密码强制加密、令牌安全管理、会话严格控制、隐私数据保护

**SLA承诺**:
- 可用性: 99.9%服务可用性
- 响应时间: 95%请求<200ms响应
- 安全保障: 零认证漏洞容忍度
- 认证准确性: 100%认证结果准确性
- 数据保护: 100%敏感数据加密

该模块是整个Career Bot系统安全防护的核心基石，提供了可靠的身份认证服务和全面的安全保护机制。
