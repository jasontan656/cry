# frontend_service 结构化文档骨架

# 字段迁移说明
```
所有数据模型/Schema已迁移至global_schemas.json，由routing动态生成和分发：
- UICommand模型 - UI控制指令（17种command_type）已迁移至global_schemas.json
- ButtonConfig模型 - 按钮配置（包含file_types、max_size_mb、permission_required）已迁移  
- IntentRequest模型 - 意图请求（包含button_action、text_input、current_ui_state）已迁移
- IntentResponse模型 - 意图响应（包含ui_updates、state_snapshot）已迁移
- ConversationState模型 - 对话状态（包含conversation_round、pending_fields、user_responses）已迁移
- SessionData模型 - 会话数据结构已迁移至global_schemas.json

所有配置参数已迁移至global_config.json：
- ui_interaction_config（button_configs、ui_layout_configs、state_display_configs）
- intent_definitions（jobseeker_intents、employer_intents、admin_intents、system_intents）
- frontend_service配置组包含ui_config、session_config、file_upload_config等
```

## A: 开发边界与职责说明

### A-1: 模块基本定义
```
frontend_service是Career Bot系统中的业务Agent之一，负责处理前端相关的服务请求，如API服务、文件上传、缓存管理等功能。该模块通过routing接收entry分发的任务，专门处理前端界面支撑相关的业务逻辑，不直接面向前端，而是作为后端业务处理模块的一部分。
```

------------------------------

### A-2: 核心功能特性
```
├── A-2.1: 业务Agent职责定位
│   ├── A-2.1.1: API服务处理 - 处理routing分发的前端API服务相关任务
│   ├── A-2.1.2: 文件上传管理 - 处理用户文件上传、存储、格式转换等业务逻辑
│   ├── A-2.1.3: 会话令牌管理 - 管理前端会话状态，提供会话验证和令牌刷新服务
│   └── A-2.1.4: 缓存服务 - 为前端提供数据缓存、临时存储等支撑服务
├── A-2.2: Agent协作模式
│   ├── A-2.2.1: 被动调用 - 仅响应routing分发的任务，不主动执行任何操作
│   ├── A-2.2.2: 任务专业化 - 专门处理前端服务支撑相关的业务逻辑
│   ├── A-2.2.3: 数据协作 - 与database协作进行数据存储，与其他Agent协作提供服务
│   └── A-2.2.4: 统一接口 - 遵循标准的AgentRequest/AgentResponse扁平化字段传输格式，统一集成到Agent生态
├── A-2.2: 完整对话流程集成
│   ├── A-2.2.1: 初始激活消息 - 发送测试开始消息激活MBTI测试流程
│   │   ├── A-2.2.1.1: 消息内容 - "现在我们就可以开始第一个测试，首先，请您完成如下情景测试，请使用下面的链接来访问测试问题页面。"
│   │   ├── A-2.2.1.2: 按钮配置 - [参加测试](https://www.topwyc.com/mbti)
│   │   ├── A-2.2.1.3: 消息来源 - mbti_followup_agent
│   │   └── A-2.2.1.4: 状态转换目标 - mbti_introduction_state
│   ├── A-2.2.2: 初始阶段 - MBTI类型验证和问题生成
```

------------------------------

### A-3: 适用范围与角色
```
├── A-3.1: 目标 - 限制自动化生成在文件创建/编辑/依赖方向/接口契约四个维度的自由度，避免脑补
├── A-3.2: 占位符映射
│   ├── A-3.2.1: MODULE_NAME - frontend_service
│   ├── A-3.2.2: MODULE_ROOT - applications/frontend_service/
│   ├── A-3.2.3: GLOBAL_SCHEMAS - global_schemas模块（通过routing统一管理）
│   ├── A-3.2.4: GLOBAL_CONFIG - routing的config_manager服务
│   └── A-3.2.5: STATE_STORE - database统一管理的存储层
```

------------------------------

## B: 系统架构与模块定义

### B-1: 目录与文件边界
```
├── B-1.1: 工作区 - 生成和修改仅允许发生在applications/frontend_service/内，禁止创建、移动、重命名、删除applications/frontend_service/之外的任何文件/目录
├── B-1.2: 主入口约定 - 模块主入口文件名与frontend_service同名，非主入口的新增文件必须归类为Adapter或Aux
├── B-1.3: 粒度限制 - 单次变更仅允许操作一个文件；若超过300行，自动截断并停止，等待下一次续写
└── B-1.4: 结构稳定性 - 禁止因实现便利而新建"公共"目录；禁止在模块间互放工具文件；不得私自抽公共层
```

------------------------------

### B-2: 职责分层边界
```
├── B-2.1: Main（主文件） - 只做策略选择、依赖装配、流程编排；禁止任何业务规则、存储访问、外部I/O
├── B-2.2: Adapter（适配层） - 只实现外设与机制（HTTP/DB/Cache/Queue/FS/LLM调用等）；禁止写业务决策
├── B-2.3: Aux（私有实现） - 仅供Main/Adapter内部复用；不得跨模块导出；禁止出现横向依赖
└── B-2.4: 拆分触发 - 当单文件同时承担两类以上变更原因或超过200行时必须拆分到对应层
```

------------------------------

### B-3: 模块依赖关系
```
├── B-3.1: 上游触发
│   ├── B-3.1.1: routing - 唯一任务调度来源，提供前端服务任务分发和配置管理
│   ├── B-3.1.2: 用户前端交互 - 接收用户的UI操作、文件上传、对话输入等前端事件
│   ├── B-3.1.3: 会话管理系统 - 处理用户登录、会话创建、令牌管理等认证相关请求
│   └── B-3.1.4: 文件上传触发 - 用户上传简历、企业文档、职位文档时的处理请求
├── B-3.2: 下游调用
│   ├── B-3.2.1: database - 会话状态存储、对话历史管理、文件元数据存储
│   ├── B-3.2.2: auth - 用户身份验证、双身份状态查询、权限验证
│   ├── B-3.2.3: resume - 简历文件上传后的处理转发
│   ├── B-3.2.4: company_identity - 企业文档上传后的验证转发
│   ├── B-3.2.5: jobpost - 职位文档上传后的处理转发
│   └── B-3.2.6: matching - 搜索请求转发和结果展示
├── B-3.3: 数据约束
│   ├── B-3.3.1: 对话状态完整性 - 确保用户对话状态在页面刷新、网络中断后的完整恢复
│   ├── B-3.3.2: 双身份界面适配 - 根据用户当前激活身份展示对应的界面和功能
│   ├── B-3.3.3: 文件上传安全 - 文件类型验证、大小限制、病毒扫描等安全检查
│   └── B-3.3.4: 会话令牌管理 - 令牌过期自动刷新、无效令牌处理、安全存储
├── B-3.4: 过滤/去重/历史维度
│   ├── B-3.4.1: 对话历史展示 - 展示用户历史对话记录，支持断点续传和上下文恢复
│   ├── B-3.4.2: 文件去重检查 - 避免用户重复上传相同文件，提供替换或跳过选择
│   ├── B-3.4.3: 状态缓存 - 用户界面状态缓存，减少重复加载和网络请求
│   └── B-3.4.4: 企业切换 - 支持雇主用户在多个验证企业间切换界面上下文
└── B-3.5: 并发/顺序性
    ├── B-3.5.1: 文件上传队列 - 多文件上传时按顺序处理，避免并发冲突
    ├── B-3.5.2: 对话状态同步 - 确保多标签页/设备间的对话状态实时同步
    └── B-3.5.3: 界面响应优先级 - 用户交互响应优先，后台任务异步处理
```

------------------------------

## C: 输入输出规范、配置机制、模型路径、调用方式

### C-1: 统一入口接口
```
async def run(request: AgentRequest) -> AgentResponse:
    模块统一入口方法
    
    Args:
        request: 扁平化请求载荷
            - request_id: str - 请求唯一标识符
            - task_type: str - 任务类型标识
            - context: Dict - 核心任务数据和元数据
            - additional_params: Dict - 可选附加参数
    
    Returns:
        AgentResponse: 扁平化响应载荷
            - request_id: str - 对应请求ID
            - agent_name: str - 处理模块名称  
            - success: bool - 处理成功状态
            - timestamp: str - 响应时间戳
            - response: Dict - 处理结果数据
            - error: Dict - 错误信息（成功时为null）
    
    Raises:
        ValidationError: 输入参数验证失败
        ConfigurationError: 配置获取失败
        ProcessingError: 业务处理异常
```

------------------------------

### C-2: 支持的任务类型
```
├── C-2.1: 核心任务类型
│   ├── C-2.1.1: 会话管理 - session_management
│   ├── C-2.1.2: 文件上传处理 - file_upload_processing
│   ├── C-2.1.3: 对话状态管理 - conversation_state_management
│   ├── C-2.1.4: 缓存操作 - cache_operations
│   ├── C-2.1.5: 角色权限管理 - role_permission_management
│   ├── C-2.1.6: 业务配置管理 - business_config_management
│   ├── C-2.1.7: 健康检查 - health_check
│   └── C-2.1.8: 配置获取 - get_config
```

------------------------------

### C-3: 核心API接口摘要
```
├── C-3.1: 会话管理接口（SessionService）
│   ├── C-3.1.1: 创建用户会话 - async def create_session(user_id: str, user_data: Dict) -> str: 返回session_id，用于后续所有请求认证
│   └── C-3.1.2: 验证会话有效性 - async def validate_session(session_id: str) -> bool: 验证session是否有效，自动延期TTL
├── C-3.2: 对话状态管理（ConversationStateService）
│   ├── C-3.2.1: 获取对话内容 - async def get_conversation_content(user_id: str, stage: str) -> Dict: 根据对话阶段路由到相应Agent获取问题内容
│   └── C-3.2.2: 存储用户回答 - async def store_user_response(session_id: str, responses: List[Dict]) -> bool: 存储用户回答并更新对话状态
├── C-3.3: 文件管理接口（FileService）
│   ├── C-3.3.1: 上传文件 - async def upload_file(file_data: bytes, owner_id: str, file_type: FileType) -> FileRecord: 上传文件到MinIO并记录元数据
│   └── C-3.3.2: 获取文件列表 - async def list_files_by_owner(owner_id: str, owner_type: OwnerType) -> List[FileRecord]: 获取用户/企业的文件列表
├── C-3.4: 缓存服务接口（CacheService）
│   ├── C-3.4.1: 设置缓存 - async def set(key: str, value: Any, ttl: int = 300, namespace: str = "default") -> bool: 支持TTL和命名空间
│   └── C-3.4.2: 获取缓存 - async def get(key: str, namespace: str = "default") -> Any
└── C-3.5: 角色管理接口（RoleService）
    ├── C-3.5.1: 获取用户角色状态 - async def get_role_status(user_id: str) -> Dict: 返回当前角色、权限、激活状态
    └── C-3.5.2: 激活角色 - async def activate_role(user_id: str, role_type: str) -> bool: 激活求职者/招聘者角色
```

------------------------------

### C-4: 配置依赖清单
```
├── C-4.1: 必需配置项 - 通过await routing.get_config("frontend_service", config_type)获取
│   ├── C-4.1.1: 基础配置 - basic_config
│   ├── C-4.1.2: 超时配置 - timeout_config
│   ├── C-4.1.3: 重试配置 - retry_config
│   ├── C-4.1.4: Redis配置 - redis_config
│   ├── C-4.1.5: 文件上传配置 - file_upload_config
│   ├── C-4.1.6: 会话配置 - session_config
│   └── C-4.1.7: 缓存配置 - cache_config
```

------------------------------

### C-5: 依赖模块清单
```
├── C-5.1: 必须依赖
│   ├── C-5.1.1: routing - 统一调度和配置管理
│   ├── C-5.1.2: global_schemas - 数据模型定义
│   └── C-5.1.3: database - 数据存储和用户信息管理
└── C-5.2: 可选依赖
    ├── C-5.2.1: auth - 用户认证服务
    ├── C-5.2.2: resume - 简历处理服务（文件上传触发）
    └── C-5.2.3: company_identity - 企业文档处理服务
```

------------------------------

## D: 用户流程、对话流程、意图识别机制

### D-1: 对话驱动UI策略
```
├── D-1.1: 预设按钮触发 - 当前通过"I want find job"/"I want to hire"预设按钮触发不同身份流程
├── D-1.2: 对话状态持久化 - 用户刷新页面、切换标签、网络中断后对话状态完整保留
├── D-1.3: 流程断点续传 - 支持用户中途退出任何对话流程，下次进入时从断点继续
└── D-1.4: 未来升级准备 - 预留自然语言意图识别的接口，支持未来升级到智能意图解析
```

------------------------------

### D-2: 双身份界面管理策略
```
├── D-2.1: 身份状态展示 - 实时展示用户的求职者/雇主身份激活状态
├── D-2.2: 界面动态切换 - 根据用户当前选择的身份动态调整界面布局和功能菜单
├── D-2.3: 身份激活引导 - 未激活身份时提供明确的激活流程引导和入口按钮
└── D-2.4: 权限可见性控制 - 基于身份状态和权限动态显示/隐藏相关功能
```

------------------------------

### D-3: 运行流程概述
```
├── D-3.1: 服务初始化与注册 - 启动时按序初始化会话管理服务(Redis) → 缓存服务(Redis) → 各专业化前端服务，建立Redis连接池，验证缓存和会话存储的连通性，注册全局服务实例，提供统一的服务访问接口
├── D-3.2: 会话生命周期管理
│   ├── D-3.2.1: 会话创建 - 用户登录 → 生成UUID会话ID → Redis存储会话数据 → 添加到用户会话列表 → 强制会话数量限制
│   ├── D-3.2.2: 会话验证 - 每次请求验证会话有效性 → 检查TTL过期 → 更新最后访问时间 → 自动延期会话
│   └── D-3.2.3: 会话清理 - 自动清理过期会话，手动清理用户所有会话
├── D-3.3: 对话状态管理与统一错误处理流程 - 接收用户消息 → 分析对话状态 → 确定目标agent → 路由获取对话内容 → 返回结构化问题 → 存储对话状态到database，支持多轮对话状态跟踪、动态agent路由、对话进度管理，不保存对话模板，仅管理对话状态和agent路由逻辑，每轮对话结束后自动存储对话历史到database，验证失败处理：当agent返回验证失败状态时，统一生成重新上传指导+一键技术支持邮件模板，状态恢复机制：验证失败后维护用户对话状态，支持重新上传后继续流程
├── D-3.4: 三实体文件管理服务流程
│   ├── D-3.4.1: 用户简历上传 - 接收简历文件 → 验证PDF/DOC格式 → MinIO存储 → 触发简历解析和头脑风暴标签生成
│   ├── D-3.4.2: 企业文档上传 - 接收SEC、GIS、Business Permit等 → 文档验证 → MinIO存储 → 企业画像生成和头脑风暴打标
│   ├── D-3.4.3: jobpost文档上传 - 接收职位描述文件 → 格式验证 → MinIO存储 → jobpost头脑风暴分析和标签生成
│   ├── D-3.4.4: 文件操作 - 获取文件信息、删除文件、按所有者列表文件、生成预签名下载URL
│   └── D-3.4.5: 存储路径 - user/{user_id}/resume/, company/{company_id}/documents/, company/{company_id}/jobpost/
├── D-3.5: 角色管理服务 - 获取用户角色状态 → 检查角色权限 → 返回角色要求和激活状态，支持角色激活流程，验证角色切换权限，管理不同角色(求职者/招聘者)的权限和功能访问
├── D-3.6: 业务配置管理 - 作用域配置的增删改查操作，支持配置的分层管理，配置合并功能，从多个作用域生成有效配置，配置验证功能，确保配置数据的完整性
├── D-3.7: 缓存管理服务 - 支持键值缓存、列表操作、命名空间管理、TTL控制，提供增量操作、模式匹配、批量清理功能，实时缓存统计和性能监控
└── D-3.8: 最终输出 - 为前端应用提供完整的API服务层，包含标准化的错误处理和响应格式，整个过程严格遵循routing调度架构，通过统一调度实现服务解耦
```

------------------------------

### D-4: Intent驱动前后端协作详解
```
├── D-4.1: 前后端状态协作机制
│   ├── D-4.1.1: 正确的Intent驱动数据流转架构 - Frontend Client(UI组件状态、用户交互事件、组件渲染逻辑、本地临时数据) → Entry Agent(Intent识别验证、用户状态管理、流程断点续传、Redis状态存储) → Routing Agent(Agent调度中枢、任务编排协调、配置管理中心、模块间协作) → 业务Agent协作
│   └── D-4.1.2: 前后端协作协议 - 前端发送intent_request包含intent、session_id、user_interaction、current_ui_state，Backend返回intent_response包含success、flow_update、ui_updates、state_snapshot
├── D-4.2: WebSocket实时状态同步
│   └── D-4.2.1: 状态同步事件类型 - flow_progress(流程进度更新)、ui_update(UI更新指令)、agent_response(Agent响应处理)、error_notification(错误通知)
└── D-4.3: 前端预设对话内容管理（由后端提供和控制）
    ├── D-4.3.1: 对话内容统一管理原则 - 所有前端显示的对话内容（包括系统消息、按钮文本、提示信息等）均由后端Agent提供，前端不得硬编码任何对话文本
    ├── D-4.3.2: 对话格式标准化控制 - 后端控制所有对话的输出格式、按钮布局、表单结构，前端仅负责根据后端指令动态渲染UI组件
    ├── D-4.3.3: 多语言对话支持 - 后端根据用户语言偏好提供对应语言的对话内容，前端通过locale参数请求特定语言版本
    └── D-4.3.4: 对话状态驱动机制 - 前端基于后端返回的conversation_state动态显示对话内容，包括当前阶段提示、可选操作按钮、进度指示等
```

------------------------------

## D-EXT: 完整对话流程内容库（由后端提供的预设对话模板）

### D-EXT-1: 求职者路径完整对话流程
```
⚠️ 重要说明：以下对话内容均由后端Agent提供，前端不得硬编码任何对话文本。所有示例仅用于协议理解，不得据此实现。

├── D-EXT-1.1: 初始界面和登录检查流程
│   ├── D-EXT-1.1.1: 状态转换 - welcome_state → login_required_state → user_status_detection_state
│   ├── D-EXT-1.1.2: 用户操作触发 - 点击"我要找工作"按钮
│   ├── D-EXT-1.1.3: 系统响应逻辑 - 检查用户登录状态，未登录弹出登录窗口，已登录直接进入用户状态检测
│   └── D-EXT-1.1.4: 后续流程分支 - 登录后根据用户类型进入不同介绍流程
├── D-EXT-1.2: 用户类型检测和介绍流程
│   ├── D-EXT-1.2.1: 状态分支 - first_time_user_intro_state | returning_user_status_state | completed_user_state
│   ├── D-EXT-1.2.2: 首次注册用户对话模板
│   │   ├── D-EXT-1.2.2.1: 中枢预设欢迎消息
│   │   │   ├── D-EXT-1.2.2.1.1: 系统消息内容 - "Hello，我是Career Bot职业规划机器人。我拥有很多强大的能力，但它们目前正在开发中。无论您想找工作还是测试，您只需按照流程完成我们的对话即可完成测试并查看您的摘要结果。请放心，测试过程不需要您的任何敏感信息。只有当您最终决定上传简历并注册您的个人信息时，我们才会获取和存储您的个人信息以为您匹配合适的工作和雇主。我们使用非常强大的匹配方法为您找到最接近您居住地且最适合您天赋和经验的工作。"
│   │   │   ├── D-EXT-1.2.2.1.2: 消息来源 - 中枢系统预设固定消息
│   │   │   └── D-EXT-1.2.2.1.3: 状态转换目标 - 等待第一个模块激活
│   │   ├── D-EXT-1.2.2.2: 第一个模块激活消息
│   │   │   ├── D-EXT-1.2.2.2.1: 系统消息内容 - "首先，请您完成如下情景测试以便我们加深对您的了解，请使用下面的链接来访问测试问题页面。"
│   │   │   ├── D-EXT-1.2.2.2.2: 按钮配置 - [参加测试](https://url)
│   │   │   ├── D-EXT-1.2.2.2.3: 消息来源 - 第一个模块（mbti_followup_agent）发出
│   │   │   └── D-EXT-1.2.2.2.4: 状态转换目标 - mbti_introduction_state
│   ├── D-EXT-1.2.3: 已开始但未完成注册用户对话模板
│   │   ├── D-EXT-1.2.3.1: 系统消息内容 - "您仍有以下信息需要完成，请继续填写。"
│   │   ├── D-EXT-1.2.3.2: 动态内容生成 - 显示缺失内容列表（动态从用户数据生成）
│   │   └── D-EXT-1.2.3.3: 状态转换目标 - registration_info_completion_state
│   └── D-EXT-1.2.4: 已完成注册用户对话模板
│       ├── D-EXT-1.2.4.1: 系统消息内容 - "请等待合适的雇主联系您。其他功能正在开发中。" + "目前不支持简历更新。简历编辑功能预计在一个月内推出。"
│       └── D-EXT-1.2.4.2: 状态转换目标 - completed_user_state
├── D-EXT-1.3: MBTI测试流程对话模板
│   ├── D-EXT-1.3.1: 状态转换 - mbti_introduction_state → mbti_result_selection_state → four_dimension_intro_state
│   ├── D-EXT-1.3.2: MBTI结果收集界面
│   │   ├── D-EXT-1.3.2.1: UI组件配置 - 16种MBTI类型选择器，一键提交到后端
│   │   └── D-EXT-1.3.2.2: 用户操作 - 用户完成外部MBTI测试后，可直接选择并提交结果给机器人
│   └── D-EXT-1.3.3: 四维能力测试介绍对话模板
│       ├── D-EXT-1.3.3.1: 系统消息内容 - "感谢您提交MBTI测试结果。为了进一步完善您的档案，请完成一个简短的逆向维度测试。我们将根据您的MBTI类型生成4套测试题，每套对应MBTI的一个维度。请点击下面的按钮前往评估页面，选择您的答案，并一键提交。"
│       ├── D-EXT-1.3.3.2: 按钮配置 - [进入MBTI四维能力补充评估]
│       └── D-EXT-1.3.3.3: 状态转换目标 - four_dimension_test_module_state
├── D-EXT-1.4: 四维能力测试模块对话管理
│   ├── D-EXT-1.4.1: 状态转换 - four_dimension_test_module_state → four_dimension_analysis_state
│   ├── D-EXT-1.4.2: 重要实现细节 - 评估页面作为新模块出现在聊天窗口旁边，不在聊天窗口内，也不在新浏览器标签页中
│   ├── D-EXT-1.4.3: 测试题自动生成逻辑 - 根据用户MBTI类型自动生成对应的四维跟进测试题，用户在评估页面选择答案并提交，系统自动收集并保存答案
│   └── D-EXT-1.4.4: 四维测试结果分析输出格式
│       ├── D-EXT-1.4.4.1: 输出结构模板 - 维度名称(例如：外向性(E)能力) + 用户选择(通过问题ID记录，使用复合ID格式如"维度-编号"，例如I-1, N-2，具有全局唯一性；兼容旧数字ID) + 解释说明(例如：您的外向能力非常突出...)
│       └── D-EXT-1.4.4.2: 综合分析模板 - "III. 综合分析" + "优势" + "需要改进的地方"，四个维度结果输出后统一输出
├── D-EXT-1.5: 人才测试流程对话模板
│   ├── D-EXT-1.5.1: 状态转换 - birthday_input_state → talent_result_display_state → resume_upload_state
│   ├── D-EXT-1.5.2: 生日输入对话 - 系统消息："接下来，请输入您的出生日期进行天赋评估。"，前端实现：日期选择器组件
│   ├── D-EXT-1.5.3: 人才测试结果显示 - 系统消息："您的天赋评估结果：XXXX。建议：XXX。"
│   └── D-EXT-1.5.4: 简历上传引导对话模板 - 系统消息："您可以进入下一步并上传您的简历（PDF、DOC或照片都可以接受）。上传简历是必要的步骤，将用于后续的招聘流程。您也可以选择在此结束对话，随时回来完成注册。我们将分析您上传的简历，您的敏感信息将被加密，不会被披露（仅用于招聘或求职场景）。"，前端实现：多格式文件上传组件（支持拖拽上传）
└── D-EXT-1.6: 注册信息完善流程对话模板
    ├── D-EXT-1.6.1: 状态转换 - registration_info_completion_state → comprehensive_analysis_state → completion_waiting_state
    ├── D-EXT-1.6.2: 必填信息检查逻辑 - 自动检查注册信息是否完整，如有缺失必填字段，列出并要求用户提供信息，等待用户完成信息填写，所有必填字段完成后确认注册
    ├── D-EXT-1.6.3: 必填信息清单 - 1.姓名全称 2.身高体重 3.婚姻状况和子女情况 4.当前地址(仅填写城市和街区) 5.居住情况(自有/租住，同居人数) 6.家庭背景(父母必填，兄弟姐妹选填) 7.电话号码和邮箱，确认首选联系方式 8.当前影响工作/生活的个人挑战(选填但建议填写)
    ├── D-EXT-1.6.4: 综合分析报告生成说明 - 所有信息完整后，系统将结合MBTI逆向测试结果、天赋测试结果和完整简历信息进行最终深度分析，系统输出：生成综合最终报告
    └── D-EXT-1.6.5: 流程完成对话模板 - 系统消息："您现在已经完成所有步骤。您的综合报告已生成。您现在需要做的就是等待合适的雇主联系您。其他功能，如企业招聘，预计将在下个月上线。我们将在功能上线时通过邮件通知您。"，系统行为：结束当前注册流程
```

------------------------------

### D-EXT-2: 企业招聘路径完整对话流程
```
├── D-EXT-2.1: 企业功能介绍对话模板
│   ├── D-EXT-2.1.1: 状态标识 - company_intro_state
│   ├── D-EXT-2.1.2: 系统消息模板（示例仅用于协议理解，不得据此实现） - "您好，这是Career Bot职业规划机器人。我们使用匹配机制来查找简历。这意味着您发布工作后，无需等待。您可以立即开始根据您的职位发布搜索匹配的简历。简历按相关性排名，前5名是根据您的工作要求、地点和潜在用户档案分析最匹配的候选人。当然，我们的分析可能并不完美，所以请使用您自己的判断。您现在可以点击按钮开始。您可以选择立即开始搜索（我们将向您显示5份样本简历，无需职位发布，这样您就可以看到质量），或者您可以从验证您的公司开始，发布正式工作并搜索真实的匹配候选人。"
│   └── D-EXT-2.1.3: 按钮选项配置 - [搜索样本简历] - 搜索样本简历、[开始验证流程] - 开始验证流程
├── D-EXT-2.2: 样本简历展示流程对话模板
│   ├── D-EXT-2.2.1: 状态标识 - sample_resume_preview_state
│   ├── D-EXT-2.2.2: 触发条件 - 如果点击[搜索样本简历]
│   ├── D-EXT-2.2.3: 系统消息模板 - "这里有5份样本简历来展示我们的输出质量。所有联系方式和敏感信息都已屏蔽。您可以随时验证您的公司以搜索真实候选人。"
│   ├── D-EXT-2.2.4: 显示内容配置 - 第一个示例屏蔽简历
│   └── D-EXT-2.2.5: 按钮选项配置 - [下一份简历] - 下一份简历、[上一份简历] - 上一份简历、[验证公司以搜索真实简历] - 验证公司以搜索真实简历
├── D-EXT-2.3: 企业MVP验证流程对话模板（SEC/DTI双轨自动化）
│   ├── D-EXT-2.3.1: 状态转换 - company_verification_mvp_intro_state → registry_type_selection_state → mvp_document_upload_state → verification_result_state
│   ├── D-EXT-2.3.2: MVP验证流程启动逻辑 - 点击[开始MVP验证流程]或[验证公司以搜索真实简历]，检查用户登录状态：未登录提示登录窗口，已登录立即进入SEC/DTI注册类型选择界面
│   ├── D-EXT-2.3.3: 注册类型选择界面对话模板
│   │   ├── D-EXT-2.3.3.1: 状态标识 - registry_type_selection_state
│   │   └── D-EXT-2.3.3.2: 系统消息模板 - "请选择您的企业注册类型：[SEC注册企业] - Securities and Exchange Commission注册、[DTI注册企业] - Department of Trade and Industry注册。⚠️ 重要提醒：企业名称、注册号和地址必须与您的账户资料完全一致。地址不匹配的申请将被直接拒绝，不提供修正机会。"
│   ├── D-EXT-2.3.4: MVP简化文档要求对话模板
│   │   ├── D-EXT-2.3.4.1: 状态标识 - mvp_document_upload_state
│   │   ├── D-EXT-2.3.4.2: SEC注册企业文档要求 - "请上传以下文档（缺一不可）：✅ Latest GIS — must be the current year (e.g., 2025)、✅ Business Permit / Mayor's Permit — must be valid for the current year、✅ SEC Certificate of Registration — identity match; year not required、✅ Articles of Incorporation — identity match; year not required、✅ BIR Certificate of Registration (Form 2303) — identity match; year not required。⚠️ Company name, SEC registration number, and business address on your documents must match your account profile. Address mismatches will be rejected."
│   │   ├── D-EXT-2.3.4.3: DTI注册企业文档要求 - "请上传以下文档（缺一不可）：✅ DTI Business Name (BN) Certificate — must be valid for the current year、✅ Business Permit / Mayor's Permit — must be valid for the current year、✅ BIR Certificate of Registration (Form 2303) — identity match; year not required。⚠️ Business address on BN/Permit must match your account profile. Address mismatches will be rejected."
│   │   ├── D-EXT-2.3.4.4: 通用上传说明 - "请添加您的联系信息（邮箱、电话和昵称）。" + "请通过拖放文件或使用聊天窗口的上传功能上传所有必需文档。系统将立即验证并在聊天窗口中显示结果（成功/失败/具体错误原因）。验证失败时可立即重新上传正确文档。" + "在您完成或主动取消此验证之前，请暂停其他操作。"
│   │   └── D-EXT-2.3.4.5: 系统行为说明 - 进入锁定对话状态，用户必须上传所有材料并获得验证结果，或主动取消，才能返回其他菜单。验证结果立即在聊天窗口中显示，无需等待邮件或页面跳转。
│   └── D-EXT-2.3.5: 多公司检测处理逻辑 - 如果检测到多个公司，提示用户选择要用于此会话的公司。完成后，将信息保存为'公司1 = xxxx'。验证成功后，用户进入"已登录且公司已验证"状态
├── D-EXT-2.4: 企业主控面板对话模板
│   ├── D-EXT-2.4.1: 状态标识 - company_verified_dashboard_state
│   ├── D-EXT-2.4.2: 系统消息模板 - "公司验证完成：公司1 = xxxx" + "欢迎使用我们的主动匹配平台。我们的系统通过将您的职位描述与我们的人才库进行匹配来工作。您不应该发布工作并等待申请，而应该发布工作然后主动搜索匹配的候选人。如果初始结果不是您要找的，您可以随时再次搜索以获得一组新的匹配档案。您可以立即开始联系候选人。"
│   └── D-EXT-2.4.3: 按钮选项配置 - [搜索候选人] - 搜索候选人、[发布新职位] - 发布新职位、[添加新公司] - 添加新公司、[显示/修改现有职位] - 显示/修改现有职位、[显示/修改现有公司] - 显示/修改现有公司
├── D-EXT-2.5: 候选人搜索流程对话模板
│   ├── D-EXT-2.5.1: 状态转换 - candidate_search_initiate_state → job_position_selection_state → search_results_display_state
│   ├── D-EXT-2.5.2: 搜索启动对话 - 点击[搜索候选人]，系统消息："请选择您发布的职位之一来查找匹配的候选人。"
│   ├── D-EXT-2.5.3: 职位选择和搜索逻辑 - 显示活跃职位列表供用户选择，用户选择职位后，系统自动开始搜索匹配候选人，显示搜索结果，包括详细候选人信息和联系方式
│   └── D-EXT-2.5.4: 重要实现注意事项 - 每个发布职位的搜索结果必须保存在雇主的搜索历史中，防止同一候选人在同一职位的后续搜索中再次出现(除非其档案已更新)，如果候选人更新了简历或档案信息，在现有搜索历史中添加标签（如"已更新"），当雇主再次搜索同一职位时，系统应重新评估更新的档案，可能会在新搜索结果中重新出现，新获得的档案应保存在相应职位的搜索历史中
└── D-EXT-2.6: 职位发布管理对话模板
    ├── D-EXT-2.6.1: 状态转换 - job_posting_form_state → existing_jobs_management_state → job_detail_edit_state
    ├── D-EXT-2.6.2: 新职位发布对话模板 - 系统消息："请上传或填写此职位的职位描述。" + "职位描述必须包括：工作职责、工作要求、薪资（范围或结构）、工作地点（远程或现场）以及简短的公司介绍。" + "请通过拖放文件或输入文本上传。"，系统行为：自动检查职位描述中的必备要素，如缺少任何要素，提示完善，所有要素完整后，保存新职位（例如CEO、营销经理），创建新职位后，返回主界面并提示用户继续发布、查看或修改职位信息
    └── D-EXT-2.6.3: 现有职位管理对话模板 - 系统消息："以下是您公司当前发布的职位列表（显示职位标题 + 当前招聘状态：招聘中/暂停）："，每个职位都有"查看详情"按钮，系统行为：点击"查看详情"后，系统独立输出职位的完整描述，底部显示操作按钮，如"删除"、"修改"、"暂停招聘/激活招聘"（按钮状态随职位状态变化），点击"修改"进入职位信息编辑流程，编辑后保存并返回职位列表，点击"删除"后再次确认，删除职位并刷新列表，点击"暂停招聘/激活招聘"切换职位状态并立即更新
```

------------------------------

### D-EXT-3: 人才测试路径完整对话流程
```
├── D-EXT-3.1: 测试路径特点说明 - 人才测试路径与求职者路径的主要区别在于，用户可以只进行测试而不必完成完整的求职注册流程。测试完成后，用户可以选择是否继续完成求职注册
├── D-EXT-3.2: 测试路径启动对话模板
│   ├── D-EXT-3.2.1: 状态转换 - talent_test_intro_state → login_required_state → direct_test_flow_state
│   ├── D-EXT-3.2.2: 用户操作触发 - 点击"我要人才测试"按钮
│   ├── D-EXT-3.2.3: 系统行为 - 检查登录状态，未登录则要求登录，登录后直接进入MBTI测试流程（与求职者路径A3相同）
│   └── D-EXT-3.2.4: 流程控制 - 流程控制：登录后直接进入MBTI测试流程（与求职者路径A3相同）
├── D-EXT-3.3: 测试结果独立展示
│   ├── D-EXT-3.3.1: 系统行为 - 完成所有测试后，提供独立的测试结果报告
│   └── D-EXT-3.3.2: 用户选择选项 - 结束测试会话、转换为完整求职者注册流程
└── D-EXT-3.4: 断点续传和会话管理
    ├── D-EXT-3.4.1: 会话状态恢复机制 - 用户重新登录时，根据后端恢复的状态显示对应的UI界面
    ├── D-EXT-3.4.2: 状态检查 - 自动检测用户当前处于哪个流程阶段
    ├── D-EXT-3.4.3: 界面恢复 - 精确恢复到用户离开时的界面状态
    └── D-EXT-3.4.4: 跨设备同步支持 - 支持用户在不同设备上继续相同的对话流程，所有状态数据通过后端实时同步
```

------------------------------

### D-EXT-4: 预设对话内容的技术实现规范
```
├── D-EXT-4.1: 后端对话内容提供机制
│   ├── D-EXT-4.1.1: 对话模板存储 - 所有对话模板存储在后端配置系统中，支持多语言版本和动态更新
│   ├── D-EXT-4.1.2: 动态内容生成 - 后端根据用户状态、流程阶段、个人信息动态生成个性化对话内容
│   ├── D-EXT-4.1.3: 模板参数化 - 支持占位符替换，如用户姓名、公司名称、测试结果等动态数据
│   └── D-EXT-4.1.4: A/B测试支持 - 支持不同对话版本的A/B测试，优化用户体验和转化率
├── D-EXT-4.2: 前端渲染控制机制
│   ├── D-EXT-4.2.1: 组件动态生成 - 前端根据后端返回的UI配置动态生成界面组件
│   ├── D-EXT-4.2.2: 按钮和表单配置 - 按钮文本、数量、样式、表单字段均由后端配置决定
│   ├── D-EXT-4.2.3: 进度指示控制 - 流程进度条、步骤指示、完成状态均由后端状态驱动
│   └── D-EXT-4.2.4: 错误和提示消息 - 所有用户提示、错误信息、帮助文本均由后端提供
├── D-EXT-4.3: 多语言和本地化支持
│   ├── D-EXT-4.3.1: 语言检测 - 自动检测用户浏览器语言偏好或根据用户设置
│   ├── D-EXT-4.3.2: 内容本地化 - 后端提供对应语言版本的对话内容和UI文本
│   ├── D-EXT-4.3.3: 文化适应性 - 根据用户所在地区提供符合当地文化的对话风格和内容
│   └── D-EXT-4.3.4: 实时语言切换 - 支持用户在对话过程中切换语言，保持对话状态连续性
└── D-EXT-4.4: 对话质量和一致性保障
    ├── D-EXT-4.4.1: 内容审核机制 - 所有对话内容经过人工审核和AI质量检测
    ├── D-EXT-4.4.2: 对话逻辑验证 - 确保对话流程的逻辑一致性和用户体验流畅性
    ├── D-EXT-4.4.3: 用户反馈收集 - 收集用户对对话内容的反馈，持续优化对话质量
    └── D-EXT-4.4.4: 版本管理和回滚 - 支持对话内容的版本管理，出现问题时快速回滚
```

------------------------------

## E: 接口结构、状态管理、日志与异常策略

### E-1: 错误码规范
```
├── E-1.1: 标准错误码格式 - 使用{DOMAIN}/{REASON}命名格式
├── E-1.2: 通用错误码
│   ├── E-1.2.1: VALIDATION/INVALID_INPUT - 输入参数验证失败
│   ├── E-1.2.2: CONFIG/NOT_FOUND - 配置项不存在
│   ├── E-1.2.3: CONFIG/INVALID_FORMAT - 配置格式错误
│   ├── E-1.2.4: TIMEOUT/REQUEST_TIMEOUT - 请求处理超时
│   ├── E-1.2.5: AUTH/UNAUTHORIZED - 权限验证失败
│   └── E-1.2.6: IO/UNAVAILABLE - 外部服务不可用
├── E-1.3: 前端服务特定错误码
│   ├── E-1.3.1: SESSION/NOT_FOUND - 会话不存在或已过期
│   ├── E-1.3.2: SESSION/VALIDATION_FAILED - 会话验证失败
│   ├── E-1.3.3: SESSION/LIMIT_EXCEEDED - 会话数量超限
│   ├── E-1.3.4: CACHE/CONNECTION_FAILED - 缓存连接失败
│   ├── E-1.3.5: CACHE/KEY_NOT_FOUND - 缓存键不存在
│   ├── E-1.3.6: FILE/UPLOAD_FAILED - 文件上传失败
│   ├── E-1.3.7: FILE/INVALID_FORMAT - 文件格式不支持
│   └── E-1.3.8: CONVERSATION/STATE_INVALID - 对话状态异常
└── E-1.4: 对话交互错误码
    ├── E-1.4.1: FRONTEND/CONVERSATION_STATE_LOST - 对话状态丢失
    ├── E-1.4.2: FRONTEND/IDENTITY_NOT_SELECTED - 身份未选择
    ├── E-1.4.3: FRONTEND/SESSION_EXPIRED - 会话已过期
    ├── E-1.4.4: FRONTEND/INVALID_TRIGGER - 无效的触发操作
    ├── E-1.4.5: FRONTEND/FILE_FORMAT_UNSUPPORTED - 不支持的文件格式
    ├── E-1.4.6: FRONTEND/FILE_SIZE_EXCEEDED - 文件大小超限
    ├── E-1.4.7: FRONTEND/UPLOAD_FAILED - 文件上传失败
    ├── E-1.4.8: FRONTEND/PROCESSING_TIMEOUT - 文件处理超时
    ├── E-1.4.9: FRONTEND/STATUS_SYNC_FAILED - 状态同步失败
    ├── E-1.4.10: FRONTEND/PERMISSION_DENIED - 权限不足
    └── E-1.4.11: FRONTEND/CACHE_CORRUPTED - 缓存数据损坏
```

------------------------------

### E-2: 日志记录规范
```
├── E-2.1: 记录字段 - user_id, session_id, service_type, operation_type, file_id, cache_key
├── E-2.2: 记录位置 - 服务初始化、Redis连接、会话操作、文件操作、缓存操作、异常发生时
├── E-2.3: 日志格式 - 使用标准logging模块，支持用户上下文追踪
├── E-2.4: 安全要求 - 不记录敏感会话数据内容，仅记录操作元数据
└── E-2.5: 日志必填字段 - request_id、module_name、operation、duration_ms、success、retry_count
```

------------------------------

### E-3: 异常处理与对话流程恢复策略
```
├── E-3.1: Redis故障 - 会话服务支持内存回退，缓存服务严格要求Redis可用
├── E-3.2: 任务调用失败 - 通过routing调用失败时提供详细错误信息
├── E-3.3: 文件操作异常 - 验证失败、存储失败等统一返回重新上传指导+技术支持邮件模板
├── E-3.4: 对话状态保护 - 验证失败时保持用户对话状态，支持重试后继续流程
├── E-3.5: 禁止用法 - 不允许直接访问数据库，必须通过routing路由
└── E-3.6: 统一错误响应 - 所有Agent验证失败统一格式化为前端可理解的错误状态+邮件模板数据
```

------------------------------

### E-4: 性能指标规范
```
├── E-4.1: 必须暴露的指标
│   ├── E-4.1.1: 调用次数 - frontend_service_requests_total
│   ├── E-4.1.2: 成功率 - frontend_service_success_rate
│   ├── E-4.1.3: 时延分布 - frontend_service_duration_seconds
│   ├── E-4.1.4: 会话创建成功率 - frontend_session_creation_success_rate
│   ├── E-4.1.5: 文件上传成功率 - frontend_file_upload_success_rate
│   └── E-4.1.6: 缓存命中率 - frontend_cache_hit_rate
```

------------------------------

## F: UI组件结构、事件响应、错误处理机制

### F-1: 文件上传处理策略
```
├── F-1.1: 多格式智能识别 - 支持PDF、DOCX、DOC、图像等多种文件格式自动识别
├── F-1.2: 上传进度可视化 - 实时显示文件上传进度、处理状态、结果反馈
├── F-1.3: 错误处理友好 - 上传失败时提供明确错误原因和重试建议
└── F-1.4: 即时处理反馈 - 文件上传完成后立即显示处理结果和下一步操作建议
```

------------------------------

### F-2: 用户状态可见性策略
```
├── F-2.1: 激活状态透明 - 清晰显示求职者激活/暂停/下架状态，但暂停期用户无感知
├── F-2.2: 重新激活入口 - 下架用户显示明显的"我要求职"重新激活按钮
├── F-2.3: 企业验证状态 - 雇主用户可见企业验证进度、结果、所需文档清单
└── F-2.4: 购买点数显示 - 雇主用户可见当前点数余额、消耗记录、充值入口
```

------------------------------

### F-3: 响应性能策略
```
├── F-3.1: 前端缓存优化 - 合理缓存用户状态、对话历史、配置信息减少API调用
├── F-3.2: 异步加载 - 非关键内容异步加载，优先保证核心交互响应速度
├── F-3.3: 错误降级 - 网络异常时提供离线功能和友好的错误提示
└── F-3.4: 移动端适配 - 响应式设计确保移动端用户体验一致
```

------------------------------

### F-4: MatchingService工作模式参数传递机制
```
├── F-4.1: 核心职责 - 为前端匹配功能提供后端参数传递和状态管理，确保work_mode参数在前后端间正确传递
├── F-4.2: work_mode参数传递流程 - 从前端请求中提取work_mode参数，构建扁平化request请求，通过routing调用matching，格式化返回前端所需格式
├── F-4.3: 前端UI参数收集 - 收集用户偏好的工作模式，传递给后端MatchingService
└── F-4.4: 全局参数一致性保障 - 参数命名work_mode字段在frontend_service、taggings_agent、matching间完全一致，取值规范严格使用"remote_allowed"|"must_onsite"两个枚举值，默认策略未指定时默认为"must_onsite"，传递路径前端→frontend_service→routing→matching，反向传递matching结果包含work_mode信息，前端可据此调整UI显示
```

------------------------------

## G: WebSocket集成与前端服务接口

### G-1: WebSocket实时通信集成接口
```
├── G-1.1: WebSocket连接管理机制 - 管理前端WebSocket连接的建立、维护和关闭
├── G-1.2: 实时消息推送接口 - 向前端推送文件处理状态、对话更新等实时消息
├── G-1.3: 连接状态同步机制 - 跨设备的用户状态实时同步和连接管理
└── G-1.4: 断线重连处理策略 - 网络中断时的自动重连和状态恢复机制
```

------------------------------

### G-2: 契约与模型来源
```
├── G-2.1: 模型唯一来源 - 所有数据模型/Schema一律从global_schemas引入；禁止在模块内新增/复制业务模型或DTO
├── G-2.2: 接口契约 - 本模块README必须提供最小可执行契约（接口签名或伪码），仅声明入参/出参/错误码；不提供实现样例
└── G-2.3: 版本与兼容 - 任何新增/变更字段必须在README标注语义、默认值、兼容策略，并同步更新global_schemas对应版本
```

------------------------------

### G-3: 配置与特性开关
```
├── G-3.1: 配置唯一来源 - 配置仅可经由routing的config_manager服务读取；禁止本地硬编码可变配置
└── G-3.2: 热更新与回滚 - 配置键名/层级不可私改；新增键必须提供默认值、回滚策略；未在routing的config_manager服务注册的键不得使用
```

------------------------------

### G-4: 外部I/O与状态
```
├── G-4.1: 状态存取 - 模块不得直接访问持久化（DB/Cache/FS）；必须通过指定Adapter间接访问database统一管理的存储层
├── G-4.2: 副作用隔离 - 任何网络/系统I/O仅可写在Adapter；Main/Aux出现I/O视为违规
└── G-4.3: 可重复执行 - 生成的任意函数需满足幂等/可重放要求（同输入不应产生额外副作用）
```

------------------------------

### G-5: 并发与资源
```
├── G-5.1: 并发原语 - 仅允许使用语言原生异步原语（如async/await、事件循环）；禁止线程池/进程池，除非在Adapter层且README明示风险与回收策略
└── G-5.2: 超时与重试 - 必须经routing的config_manager服务注入；禁止在代码内写死超时/重试参数
```

------------------------------

### G-6: 观测与审计
```
├── G-6.1: 敏感信息 - 日志/错误信息不得包含密钥、令牌、身份证件、邮箱全量、手机号全量等；必要时脱敏
└── G-6.2: 指标 - 至少暴露调用次数、成功率、时延分布三类指标，指标名在README固化，禁止私改
```

------------------------------

## H: 环境配置、运行要求、版本依赖、模块限制

### H-1: 技术规范遵循
```
├── H-1.1: 核心约束
│   ├── H-1.1.1: 统一入口 - 所有前端交互通过entry的扁平化字段传输机制处理
│   ├── H-1.1.2: 生产级测试 - UI组件渲染不得使用mock数据，必须基于真实后端响应
│   └── H-1.1.3: 数据格式 - 输入输出严格遵循AgentRequest和AgentResponse
├── H-1.2: Intent驱动前端服务规范
│   ├── H-1.2.1: 动态组件渲染 - 根据后端Agent响应动态生成UI组件（如MBTI测试页面、简历上传界面）
│   ├── H-1.2.2: 状态驱动渲染 - 基于用户流程状态决定前端组件的显示和交互逻辑
│   ├── H-1.2.3: 实时响应 - 支持多设备的实时状态同步，确保用户在任何设备上的体验一致性
│   └── H-1.2.4: 流程可视化 - 为用户提供当前流程进度和下一步操作的可视化指引
├── H-1.3: 技术实现约束
│   ├── H-1.3.1: 异步处理 - 所有函数使用async def，支持非阻塞UI更新
│   ├── H-1.3.2: 配置管理 - UI配置通过routing从global_config获取，禁止硬编码样式或布局
│   └── H-1.3.3: 错误处理 - 前端错误必须有用户友好的提示，同时记录详细日志
└── H-1.4: Pydantic规范 - 推荐方法model_validate()、model_dump()，禁止方法.dict()、.parse_obj()、.json()等V1方法，字段验证必须使用pattern，禁止使用regex，数据模型从全局schemas导入，禁止本地定义
```

------------------------------

### H-2: 全局规则与边界清单
```
├── H-2.1: Pydantic使用情况 - 依赖global_schemas中的Pydantic V2模型，数据模型FileRecord, FileType, OwnerType, FileStatus, FileCategory等，验证策略通过global_schemas统一验证，避免重复定义，模型重用从global_schemas重新导出文件相关模型
├── H-2.2: 数据传递方式 - 服务间通信通过routing实现代理间解耦调用，Redis存储会话数据和缓存数据存储在Redis中，JSON序列化会话和缓存数据使用JSON格式序列化，扁平化载荷所有routing调用使用AgentRequest格式
├── H-2.3: 默认值与路径规则 - 会话TTL通过settings.SESSION_TTL配置，默认支持多种时间单位，缓存TTL默认300秒，可通过namespace和key单独配置，会话限制每用户最大会话数通过settings.MAX_SESSIONS_PER_USER控制，Redis连接通过settings.CACHE_URL配置Redis连接
└── H-2.4: 关键约束规范（生产必遵） - 禁止直接数据库所有数据库操作必须通过routing路由，禁止硬编码所有配置参数通过settings管理，Redis强依赖缓存服务要求Redis可用，会话服务支持内存降级，标准化响应统一success/error响应格式
```

------------------------------

### H-3: 并发与性能约束
```
├── H-3.1: 异步必需 - 所有服务方法使用async/await
├── H-3.2: 连接池管理 - Redis连接池复用，避免连接泄漏
├── H-3.3: 缓存分区 - 通过命名空间隔离不同类型缓存数据
└── H-3.4: 边界控制 - 文件大小限制、会话数量限制、缓存TTL限制
```

------------------------------

### H-4: 模块接入说明
```
frontend_service是被动调用的业务模块，不包含启动逻辑和测试代码。整个Career Bot系统的启动入口统一在boot/目录中：
├── H-4.1: 系统启动 - 使用python main.py --start从boot/启动整个系统
├── H-4.2: 模块装配 - 通过boot/launcher.py基于applications/__registry__.py装配
├── H-4.3: 服务调用 - 启动后通过routing进行统一调度
└── H-4.4: 功能测试 - 测试逻辑已迁移至utility_tools/global_test/进行独立管理
```

------------------------------

## I: 测试策略、验收机制、部署策略、未来规划

### I-1: 错误与返回
```
├── I-1.1: 错误码规范 - 采用{DOMAIN}/{REASON}命名（如：AUTH/TIMEOUT、IO/UNAVAILABLE）；README列明取值全集
├── I-1.2: 异常传播 - 只允许抛出仓库标准异常基类及其子类；不得抛裸异常；错误信息需面向调用方而非实现细节
└── I-1.3: 失败回退 - 失败时必须返回可操作指令（如flow指令/重试建议/联系渠道），不得要求调用方自行猜测
```

------------------------------

### I-2: 安全与合规
```
├── I-2.1: 秘钥管理 - 不得在代码/README/示例中出现任何真实秘钥；仅允许读取环境变量或安全管理器的别名
├── I-2.2: 输入校验 - 所有外部输入必须显式校验（长度/类型/枚举/格式），校验规则写入README的契约章节
└── I-2.3: 权限与最小化 - 模块内不得提升权限；仅请求所需最小范围的权限与数据字段
```

------------------------------

### I-3: 测试与验收
```
├── I-3.1: 最小用例 - 本模块至少提供冒烟链路与失败路径两类用例；用例不得Mock掉对外契约（可Mock外设）
└── I-3.2: 验收门槛 - 生成变更必须先通过本模块用例再提交；未达门槛禁止继续生成下一文件
```

------------------------------

### I-4: 生成器执行规范
```
├── I-4.1: 部分修改优先 - 每次仅修改一个文件，≤300行；若需要新增文件，先在README标注"文件名+角色(Main/Adapter/Aux)+责任"，再生成
├── I-4.2: 禁止脑补 - 遇到缺失信息（路径/键名/Schema字段/错误码），停止输出并在README的"待补要点"清单中列明，不得擅自发明
├── I-4.3: 依赖单向 - Domain→Adapter单向依赖；Aux不得被跨模块引用。生成器如果检测到反向引用，直接终止
├── I-4.4: 不迁移/不重命名/不删除 - 除非README的"迁移方案"明确列出变更映射
└── I-4.5: 不新增公共层 - 任何"utils/common/shared"目录新增一律拒绝；确有必要需先在顶层规范中建制并评审
```

------------------------------

### I-5: 关键词黑名单
```
├── I-5.1: 禁止本地业务模型定义 - "class .*Model", "data class .*", "interface .*DTO"
├── I-5.2: 禁止硬编码配置 - "API_KEY=", "timeout\\s*=\\s*\\d+", "retry\\s*=\\s*\\d+"
├── I-5.3: 禁止跨层I/O - 在Main/Aux中出现"http", "db", "sql", "open(", "requests", "fetch"
├── I-5.4: 禁止并发越界 - "Thread", "Process", "fork", "Pool"
└── I-5.5: 禁止未脱敏日志 - "print(", "console.log(", "logging.info(f\\".*password|token|secret"
```

------------------------------

## J: 未定义项、待补要点、黑名单、禁用规则等

### J-1: 数据与Schema规范
```
├── J-1.1: 会话数据模型（SessionService）
│   ├── J-1.1.1: 会话数据结构 - session_id: str(UUID格式的会话标识), user_id: str(用户标识), user_data: Dict[str, Any](用户信息), created_at: float(创建时间戳), last_accessed: float(最后访问时间戳), user_agent: Optional[str](浏览器信息), ip_address: Optional[str](IP地址), ttl: int(会话过期时间秒)
│   └── J-1.1.2: Redis存储键结构 - session:{session_id}(会话数据存储), user_sessions:{user_id}(用户会话列表Redis Set)
├── J-1.2: 缓存数据模型（CacheService）
│   ├── J-1.2.1: 缓存操作接口 - set(key, value, ttl, namespace)设置缓存值, get(key, namespace)获取缓存值, delete(key, namespace)删除缓存, exists(key, namespace)检查键存在性, increment(key, amount, namespace, ttl)数值增量操作, set_list(key, values, ttl, namespace)设置列表值, append_to_list(key, value, max_length, namespace, ttl)追加到列表
│   └── J-1.2.2: 命名空间管理 - default(默认命名空间), user_data(用户数据缓存), conversation(对话状态缓存), temp(临时数据缓存)
├── J-1.3: 文件管理模型（FileService）
│   ├── J-1.3.1: FileRecord文件记录（来自global_schemas） - file_id: str(文件唯一标识), filename: str(原始文件名), file_type: FileType(文件类型枚举), owner_type: OwnerType(所有者类型枚举), owner_id: str(所有者ID), file_category: FileCategory(文件分类), status: FileStatus(文件状态), storage_path: str(MinIO存储路径), file_size: int(文件大小), mime_type: str(MIME类型), created_at: datetime(创建时间), updated_at: datetime(更新时间)
│   └── J-1.3.2: 文件类型枚举 - FileType: RESUME, AVATAR, DOCUMENT, IMAGE, VIDEO, AUDIO; OwnerType: USER, COMPANY, SYSTEM; FileStatus: ACTIVE, DELETED, PROCESSING, ERROR; FileCategory: PROFILE, ASSESSMENT, ANALYSIS, TEMP
├── J-1.4: 角色管理模型（RoleService）
│   ├── J-1.4.1: 角色状态结构 - user_id: str(用户ID), current_role: str(当前角色job_seeker/recruiter), role_activated: bool(角色激活状态), permissions: List[str](权限列表), role_requirements_met: bool(角色要求满足状态)
│   └── J-1.4.2: 角色要求结构 - role_type: str(角色类型), requirements: List[str](必需要求列表), optional_items: List[str](可选项目列表)
├── J-1.5: 业务配置模型（BusinessConfigService）
│   ├── J-1.5.1: 配置作用域管理 - scope: str(配置作用域名称), config_data: Dict[str, Any](配置数据), last_modified: str(最后修改时间)
│   └── J-1.5.2: 有效配置合并 - effective_config: Dict[str, Any](合并后的有效配置), merged_scopes: List[str](参与合并的作用域列表), generated_at: str(生成时间)
├── J-1.6: 对话状态存储机制（Redis存储设计）
│   ├── J-1.6.1: 对话状态Redis键结构 - conversation_state:{user_id}:{session_id}(存储格式JSON字符串，TTL 7200秒2小时，内容完整的对话状态数据), user_conversations:{user_id}(存储格式SET集合，内容该用户的所有活跃对话session_id列表), conversation_stage:{session_id}(存储格式简单字符串，TTL 3600秒1小时，内容当前对话阶段用于快速路由)
│   └── J-1.6.2: 对话历史Database_agent存储 - 每轮对话结束后，通过routing将对话数据传递给database，包含operation: "store_conversation_history", data包含user_id, session_id, conversation_round, stage, questions, user_responses, quality_scores, timestamp
├── J-1.7: 对话状态管理服务模型（ConversationStateService）
│   ├── J-1.7.1: 对话状态核心数据结构 - 包含user_id, session_id, conversation_state(current_stage, current_agent, conversation_round, pending_fields, completed_fields, user_responses, next_questions), agent_routing_map
│   ├── J-1.7.2: 对话状态管理职责 - 状态跟踪追踪用户在整个对话流程中的当前位置和进度, Agent路由根据对话阶段动态决定调用哪个agent获取问题内容, 数据整合收集各轮对话的用户回答进行质量评估和字段映射, 流程控制判断何时进入下一阶段或结束当前对话流程
│   ├── J-1.7.3: Agent路由决策机制 - 根据对话状态决定应该调用哪个agent获取对话内容，routing_rules包含resume_info_collection: "resume", resume_quality_check: "resume", mbti_reverse_test: "mbti_followup_agent", talent_birth_analysis: "ninetest_agent", final_report_generation: "final_analysis_output_agent"
│   └── J-1.7.4: 对话内容获取流程 - 接收用户输入→解析当前对话状态→确定目标agent→根据对话阶段路由到相应agent→请求对话内容→通过routing向目标agent请求下一轮问题→格式化响应→将agent返回的问题结构化为前端表单格式→状态更新→更新对话状态并存储到database
└── J-1.8: 统一响应格式 - 所有服务统一响应格式包含success: true|false, data: {...}|null, error包含code和message或null, request_id: "string", timestamp: "ISO_datetime"
```

------------------------------

### J-2: 存储与集合设计
```
├── J-2.1: 缓存存储设计（CacheService）
│   ├── J-2.1.1: 命名空间设计 - default:{key}(默认缓存数据), user_data:{key}(用户数据缓存), conversation:{key}(对话状态缓存), temp:{key}(临时数据缓存)
│   ├── J-2.1.2: 缓存操作策略 - 默认TTL 300秒5分钟, 数据序列化JSON格式支持复杂数据结构, 列表管理支持列表追加、长度限制、LRU清理, 模式匹配支持通配符模式的批量键操作
│   └── J-2.1.3: 缓存性能设计 - 连接池redis-py连接池管理并发连接, 批量操作支持pipeline批量操作减少网络开销, 统计监控实时缓存命中率、使用量统计
├── J-2.2: 文件存储集成设计
│   ├── J-2.2.1: MinIO对象存储集成 - 存储路径结构{owner_type}/{owner_id}/{file_type}/{filename}, 调用链路FileService→routing→database→MinIO, 元数据存储文件元数据存储在MongoDB实际文件存储在MinIO, database职责仅接收预格式化的文件信息进行校验和存储不做数据转换
│   └── J-2.2.2: 文件操作流程 - upload_file→routing→database→storage("storage.upload_file")→database→MinIO存储+MongoDB记录, get_file_info→routing→database→storage("storage.get_file_info")→database→MongoDB查询, delete_file→routing→database→storage("storage.delete_file")→database→软删除标记, list_files→routing→database→storage("storage.list_files_by_owner")→database→条件查询
├── J-2.3: 对话存储集成设计
│   └── J-2.3.1: MongoDB对话集合（通过ConversationService） - 调用路径ChatService→routing→ConversationService→MongoDB, 存储操作conversation.get_user_sessions获取用户会话列表, conversation.get_session_messages获取会话消息历史, conversation.store_message存储单条消息, conversation.create_session创建新会话
├── J-2.4: 配置存储设计
│   └── J-2.4.1: 业务配置存储（BusinessConfigService） - 内存存储结构Dict[str, Dict[str, Any]]作用域到配置的映射, 作用域管理支持多层级配置作用域和继承, 配置合并多作用域配置的智能合并算法, 配置操作作用域配置的CRUD操作、配置验证和格式检查、有效配置的动态生成和缓存
├── J-2.5: Redis连接管理设计
│   ├── J-2.5.1: 连接池配置 - Redis连接策略通过settings.CACHE_URL配置, 连接池redis-py自动连接池管理, 健康检查定期ping检查连接健康状态, 故障处理会话服务支持内存回退缓存服务严格要求Redis
│   └── J-2.5.2: 数据一致性 - 原子操作使用Redis事务确保复合操作的原子性, TTL同步会话列表TTL与会话数据TTL保持同步, 清理策略定期清理过期数据避免内存泄漏
├── J-2.6: 服务集成存储
│   ├── J-2.6.1: routing调度集成 - 调度调用模式routing获取全局客户端, 标准载荷所有调用使用标准化的intent和payload格式, 异步调用支持高并发的异步任务调用
│   └── J-2.6.2: 支持的调度意图 - storage.*文件存储操作, conversation.*对话管理操作, resume_analysis简历分析处理, database.*数据库操作
└── J-2.7: 性能优化存储
    └── J-2.7.1: 缓存优化策略 - 分层缓存Redis L1缓存+应用内存L2缓存, 批量操作支持批量设置和获取减少网络开销, 压缩存储大对象支持压缩存储节省内存, 智能过期基于访问模式的智能TTL管理
```

------------------------------

### J-3: 故障排除Runbook
```
├── J-3.1: Redis连接失败问题排查
│   ├── J-3.1.1: 症状识别 - ConnectionError: Error connecting to Redis, RedisConnectionError: Connection refused, TimeoutError: Redis operation timed out
│   ├── J-3.1.2: 排查步骤 - 检查Redis服务状态docker ps | grep redis或systemctl status redis, 验证网络连通性telnet <redis_host> <redis_port>, 检查Redis配置redis-cli ping和redis-cli info replication
│   └── J-3.1.3: 解决方案 - 修复连接配置检查URL格式CACHE_URL和REDIS_CONNECTION_POOL参数, 应用内降级策略使用safe_cache_operation进行Redis连接失败时的内存回退
├── J-3.2: 会话管理服务异常排查
│   ├── J-3.2.1: 症状识别 - SessionNotFound: Session not found or expired, InvalidSession: Session validation failed, SessionLimitExceeded: Too many active sessions
│   ├── J-3.2.2: 排查步骤 - 检查会话数据完整性使用redis检查特定用户的会话user_sessions和会话详情session_data、ttl
│   └── J-3.2.3: 解决方案 - 清理异常会话cleanup_user_sessions清理用户的所有无效会话, 重置会话TTL refresh_session_ttl刷新会话过期时间
├── J-3.3: 文件上传服务异常排查
│   ├── J-3.3.1: 症状识别 - FileUploadError: File upload failed, StorageError: MinIO connection failed, FileSizeExceeded: File too large, UnsupportedFileType: Invalid file format
│   ├── J-3.3.2: 排查步骤 - 检查MinIO连接状态check_minio_health检查MinIO健康状态, 验证文件处理管道diagnose_file_pipeline诊断文件处理管道各环节
│   └── J-3.3.3: 解决方案 - 文件上传重试机制robust_file_upload带重试的文件上传包含预检查存储空间、执行上传、验证上传结果, 存储空间清理cleanup_failed_uploads清理失败的文件上传
├── J-3.4: 快速诊断命令 - Redis健康检查一键脚本redis-cli --latency-history, 服务状态总览curl -f http://localhost:8000/health, 日志快速分析tail -100 app.log | grep -E "(ERROR|WARN|Redis|Session|Upload)"
├── J-3.5: 监控指标阈值 - Redis连接池使用率>80%告警, 会话创建失败率>5%告警, 文件上传失败率>10%告警, 平均响应时间>2秒告警
└── J-3.6: 性能优化建议 - Redis连接优化使用连接池避免频繁创建连接, 会话数据压缩大会话数据启用Redis压缩存储, 文件上传优化实现分片上传支持断点续传, 缓存分层热点数据使用本地缓存减少Redis压力
```

------------------------------

### J-4: 待补要点机制
```
├── J-4.1: 必要说明 - 遇到字段未定义、路径不明、错误码缺失、指标未命名等情况，生成器不得继续实现，必须在README的"待补要点"清单中列出：待补键名/字段（含建议默认值/取值域）、影响面（调用方、下游模块、运行时风险）、最小决策集（给出2～3个可选项，偏保守）
├── J-4.2: 配置参数待补
│   ├── J-4.2.1: 缺失的配置键名 - frontend_service.session_config.max_sessions_per_user建议默认值5取值域[1,10]影响面用户会话数量限制和资源控制, frontend_service.file_upload_config.max_file_size建议默认值52428800(50MB)取值域[1048576,104857600]影响面文件上传服务的容量限制和存储成本, frontend_service.cache_config.default_namespace_ttl建议默认值分类型TTL影响面不同类型缓存数据的过期策略
│   └── J-4.2.2: 对话内容管理配置待补 - frontend_service.conversation_config.template_cache_ttl建议默认值1800秒(30分钟)取值域[300,7200]影响面对话模板缓存性能和实时更新, frontend_service.conversation_config.supported_locales建议默认值["zh-CN", "en-US"]取值域ISO语言代码数组影响面多语言对话支持范围, frontend_service.conversation_config.content_version_control建议默认值true取值域[true,false]影响面对话内容的版本管理和回滚能力
├── J-4.3: Schema字段待补
│   ├── J-4.3.1: global_schemas中缺失的字段定义 - SessionData缺失字段client_metadata建议类型Dict[str, str]影响面客户端信息追踪和会话管理, ConversationState缺失字段agent_routing_history建议类型List[Dict[str, Any]]影响面对话路由历史的记录和分析, FileRecord缺失字段processing_status建议类型Literal["pending", "processing", "completed", "failed"]影响面文件处理状态的追踪和用户反馈
│   └── J-4.3.2: 对话内容相关Schema字段待补 - ConversationTemplate缺失字段content_version建议类型str影响面对话模板版本控制和内容管理, UIComponentConfig缺失字段button_actions建议类型List[Dict[str, str]]影响面前端按钮配置和动作绑定, DialogueState缺失字段locale_preference建议类型str影响面用户语言偏好的持久化存储, MessageTemplate缺失字段placeholder_variables建议类型Dict[str, str]影响面对话内容的动态变量替换
├── J-4.4: 路径映射待补
│   └── J-4.4.1: 未明确的文件路径 - 路径用途临时文件存储位置待确认路径{MODULE_ROOT}/temp/vs系统临时目录影响面文件上传处理过程中的临时存储
├── J-4.5: 错误码待补
│   ├── J-4.5.1: 模块特定错误码 - 错误场景Redis连接池耗尽处理建议错误码CACHE/CONNECTION_POOL_EXHAUSTED错误消息模板"缓存连接池耗尽: 当前连接数={current_connections}"影响面缓存服务的可用性和并发处理能力, 错误场景对话状态不一致处理建议错误码CONVERSATION/STATE_INCONSISTENT错误消息模板"对话状态不一致: session_id={session_id}"影响面对话流程的可靠性和用户体验
│   └── J-4.5.2: 对话内容相关错误码待补 - 错误场景对话模板加载失败建议错误码CONVERSATION/TEMPLATE_LOAD_FAILED错误消息模板"对话模板加载失败: template_id={template_id}, locale={locale}"影响面用户对话体验中断和多语言支持, 错误场景对话内容版本冲突建议错误码CONVERSATION/VERSION_CONFLICT错误消息模板"对话内容版本冲突: current_version={current}, required_version={required}"影响面对话内容一致性和版本管理
├── J-4.6: 指标名称待补
│   └── J-4.6.1: 性能监控指标 - 指标用途不同服务类型的处理性能监控建议指标名frontend_service_processing_duration_by_type指标类型Histogram标签维度service_type, operation, success_status影响面前端服务性能分析和优化决策
├── J-4.7: 依赖关系待补
│   └── J-4.7.1: 模块间协作关系 - 协作场景与entry的前端请求路由协作目标模块entry交互方式接收路由后的前端服务请求并返回处理结果数据传递格式标准化的前端服务请求和响应格式影响面前端用户体验和系统响应速度
└── J-4.8: 业务规则待补
    ├── J-4.8.1: 业务逻辑决策点 - 业务场景会话过期后的用户状态恢复策略决策点会话过期时是否自动创建新会话并尝试恢复用户状态影响面用户体验的连续性和系统资源消耗最小决策集自动恢复机制(用户无感知)、手动重新登录(确保安全性)、智能恢复策略(基于用户行为)
    ├── J-4.8.2: 文件上传失败重试策略 - 业务场景文件上传失败时的重试和通知策略决策点文件上传失败时的自动重试次数和用户通知方式影响面文件上传成功率和用户操作体验最小决策集3次自动重试+邮件通知(完整保障)、1次重试+即时提示(快速反馈)、智能重试机制(基于失败原因)
    └── J-4.8.3: 对话内容动态切换策略 - 业务场景用户在对话过程中切换语言或身份时的内容处理策略决策点是否保持对话状态连续性并重新加载对应语言的对话内容影响面多语言用户体验和对话流程的连贯性最小决策集完全重启对话流程(确保一致性)、智能内容映射切换(保持连贯性)、用户选择切换模式(灵活控制)
```

------------------------------

### J-5: 合约与字段变更
```
├── J-5.1: 对话驱动相关字段
│   ├── J-5.1.1: 对话状态字段 - conversation_context: 当前对话上下文状态, active_identity: 当前激活的身份类型(jobseeker/employer), conversation_stage: 对话流程当前阶段, last_interaction_timestamp: 最后交互时间戳
│   └── J-5.1.2: 按钮触发配置 - jobseeker_trigger_button: 求职者触发按钮配置, employer_trigger_button: 雇主触发按钮配置, intent_recognition_enabled: 意图识别功能开关, natural_language_support: 自然语言支持开关
├── J-5.2: 双身份界面字段
│   ├── J-5.2.1: 身份状态展示 - jobseeker_activation_status: 求职者身份激活状态展示, employer_activation_status: 雇主身份激活状态展示, identity_switch_available: 身份切换可用性标记, current_selected_identity: 当前选择的活动身份
│   └── J-5.2.2: 界面配置字段 - ui_layout_config: 基于身份的界面布局配置, menu_visibility_rules: 菜单可见性规则配置, permission_based_ui: 基于权限的界面控制配置
├── J-5.3: 状态可见性字段
│   ├── J-5.3.1: 用户状态展示 - listing_status_display: 上架状态展示配置(激活/暂停/下架), suspension_visibility: 暂停状态可见性控制(无感知), reactivation_button_show: 重新激活按钮显示条件, purchase_count_display: 购买次数展示配置
│   └── J-5.3.2: 企业状态字段 - company_verification_display: 企业验证状态展示, document_upload_progress: 文档上传进度显示, company_selection_ui: 企业选择界面配置
├── J-5.4: 文件上传相关字段
│   ├── J-5.4.1: 上传配置字段 - supported_file_formats: 支持的文件格式清单, max_file_size_limit: 文件大小限制配置, upload_security_rules: 文件上传安全规则, batch_upload_enabled: 批量上传功能开关
│   └── J-5.4.2: 处理状态字段 - upload_progress_tracking: 上传进度跟踪配置, processing_status_display: 处理状态展示配置, error_message_templates: 错误消息模板库
└── J-5.5: 受影响的上下游字段联动 - routing: 对话状态和任务调度上下文需保持同步, auth: 用户身份状态变更需立即同步到界面展示, database: 对话历史和用户状态存储需实时同步, resume: 简历上传和处理状态需在界面实时反馈, company_identity: 企业验证进度需在界面及时更新, jobpost: 职位创建流程状态需与界面状态联动, matching: 搜索权限和结果展示需基于用户状态控制
```

------------------------------

### K: UI组件控制与事件响应机制

```
├── K-1: UI指令与组件控制
│   ├── K-1.1: 求职者路径UI指令
│   │   ├── K-1.1.1: show_welcome_buttons - 显示欢迎按钮界面
│   │   ├── K-1.1.2: show_intro_message - 显示介绍信息界面
│   │   ├── K-1.1.3: show_mbti_link_button - 显示MBTI测试链接按钮
│   │   ├── K-1.1.4: show_mbti_selector - 显示MBTI选择器界面
│   │   ├── K-1.1.5: show_test_module_sidebar - 显示测试模块侧边栏
│   │   ├── K-1.1.6: show_analysis_results - 显示分析结果界面
│   │   ├── K-1.1.7: show_birthday_input - 显示生日输入界面
│   │   ├── K-1.1.8: show_file_upload - 显示文件上传界面
│   │   ├── K-1.1.9: show_missing_info_form - 显示缺失信息表单
│   │   ├── K-1.1.10: show_final_report - 显示最终报告界面
│   │   └── K-1.1.11: show_completion_message - 显示完成消息界面
│   ├── K-1.2: 企业路径UI指令
│   │   ├── K-1.2.1: show_company_options - 显示企业选项界面
│   │   ├── K-1.2.2: show_sample_resumes - 显示样本简历界面
│   │   ├── K-1.2.3: show_verification_requirements - 显示验证要求界面
│   │   ├── K-1.2.4: show_upload_interface - 显示上传界面
│   │   ├── K-1.2.5: show_dashboard_options - 显示仪表板选项
│   │   ├── K-1.2.6: show_job_position_selector - 显示职位选择器
│   │   ├── K-1.2.7: show_job_form - 显示职位表单界面
│   │   └── K-1.2.8: show_job_upload_retry_interface - 显示职位重试上传界面
│   ├── K-1.3: 管理员路径UI指令
│   │   ├── K-1.3.1: verify_admin_permission - 验证管理员权限界面
│   │   ├── K-1.3.2: show_admin_dashboard - 显示管理员仪表板
│   │   ├── K-1.3.3: show_credit_management_panel - 显示积分管理面板
│   │   ├── K-1.3.4: show_credit_form - 显示积分操作表单
│   │   ├── K-1.3.5: show_role_management_panel - 显示角色管理面板
│   │   ├── K-1.3.6: show_role_form - 显示角色操作表单
│   │   ├── K-1.3.7: show_verification_review_panel - 显示验证审核面板
│   │   ├── K-1.3.8: show_tag_audit_panel - 显示标签审计面板
│   │   └── K-1.3.9: show_operation_logs - 显示操作日志界面
│   └── K-1.4: 通用UI指令
│       ├── K-1.4.1: show_retry_with_support - 显示重试和支持界面
│       ├── K-1.4.2: show_verification_success - 显示验证成功界面
│       ├── K-1.4.3: show_company_selection - 显示公司选择界面
│       └── K-1.4.4: show_candidate_results - 显示候选人结果界面
├── K-2: 事件响应机制
│   ├── K-2.1: 用户交互事件
│   │   ├── K-2.1.1: 按钮点击事件 - 各种按钮点击的处理机制
│   │   ├── K-2.1.2: 文件上传事件 - 简历、企业文档、职位文档上传
│   │   ├── K-2.1.3: 表单提交事件 - 各种信息表单的提交处理
│   │   └── K-2.1.4: 选择器变更事件 - MBTI选择、公司选择等
│   ├── K-2.2: 系统状态变更事件
│   │   ├── K-2.2.1: 对话状态变更 - 状态机状态转换触发的事件
│   │   ├── K-2.2.2: 身份切换事件 - 求职者雇主身份切换事件
│   │   ├── K-2.2.3: 验证状态变更 - 企业验证状态变化事件
│   │   └── K-2.2.4: 任务完成事件 - 各种任务完成后的处理事件
│   └── K-2.3: 前端服务事件协调
│       ├── K-2.3.1: routing调用事件 - 接收routing任务分发的事件响应
│       ├── K-2.3.2: UI渲染完成事件 - UI组件渲染完成的事件处理
│       ├── K-2.3.3: 前端反馈事件 - 前端用户操作反馈的事件响应
│       └── K-2.3.4: 异常恢复事件 - 前端服务异常恢复的事件处理
├── K-3: 错误处理UI机制
│   ├── K-3.1: 统一错误处理界面
│   │   ├── K-3.1.1: 验证失败界面 - 文档验证失败的统一界面
│   │   ├── K-3.1.2: 解析失败界面 - 文件解析失败的统一界面  
│   │   ├── K-3.1.3: 网络错误界面 - 网络连接失败的界面
│   │   └── K-3.1.4: 系统错误界面 - 系统内部错误的界面
│   ├── K-3.2: 重试机制UI
│   │   ├── K-3.2.1: 简历上传重试 - resume_upload_retry状态界面
│   │   ├── K-3.2.2: 企业文档重试 - document_upload_retry状态界面
│   │   ├── K-3.2.3: 职位发布重试 - job_posting_retry状态界面
│   │   └── K-3.2.4: 通用重试按钮 - 统一的重试操作按钮
│   └── K-3.3: 支持联系机制
│       ├── K-3.3.1: 支持邮件模板 - support@4waysgroup.com邮件模板
│       ├── K-3.3.2: 错误信息收集 - 自动收集错误上下文信息
│       ├── K-3.3.3: 用户反馈渠道 - 提供用户反馈的界面入口
│       └── K-3.3.4: 问题分类指导 - 帮助用户分类和描述问题
```

------------------------------

⚠️ **职责边界说明**: K章节内容从routing迁移而来，明确frontend_service负责所有UI组件控制和前端事件响应，routing专注于任务路由和Agent协调。

⚠️ 重要提醒: 上述待补要点未明确前，AI代码生成器应该停止实现相关功能，等待明确指令后再继续。禁止基于假设或经验进行"脑补"。
