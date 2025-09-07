# boot 模块 - AI可执行动作清单

基于 boot 模块结构化文档提取的系统启动装配动作序列

------------------------------

### A1: CLI命令行参数解析与验证

```
简要说明：
解析用户输入的命令行参数，验证参数合法性，并根据参数选择对应的启动模式。该动作是整个系统的入口点，负责将用户意图转换为系统可执行的启动指令。

触发时机：
用户在命令行执行python main.py及其各种参数组合时触发，是系统启动的第一个动作。

模块关系：
- 执行模块：main.py（≤50行限制）
- 接收输入：命令行参数（sys.argv）
- 输出交付：解析后的参数对象传递给launcher.py的对应方法

行为链逻辑：
该动作是启动链的起始节点，根据解析结果决定后续动作的分支路径：env-check分支、health分支、start分支（默认）。

执行要素明细：
- 输入字段：--env-check（bool，默认False）、--health（bool，默认False）、--start（bool，默认False）、--production（bool，默认False）、--env-file（str，可选）
- 输出格式：结构化参数对象，包含操作类型和配置参数
- 依赖配置：使用Python内置argparse库，不依赖外部配置
- 调用方式：同步调用，直接调用launcher对应方法
- 错误处理策略：参数解析失败返回错误码1，输出参数帮助信息
- 日志记录字段：operation（parse_cli）、success、duration_ms
- 限制条件：main.py总行数不得超过50行

⚠️ 未定义项识别：
无参数时的默认行为已定义为等价于--start
```

------------------------------

### A2: 系统环境完整性检查

```
简要说明：
验证系统运行所需的基础环境条件，包括环境变量完整性、配置文件存在性、文件权限和端口可用性检查。这是必跑阶段，任何失败都会阻止系统启动。

触发时机：
由main.py调用launcher.env_check()方法触发，或用户直接执行python main.py --env-check时触发。在start流程中作为第一个必执行阶段。

模块关系：
- 执行模块：launcher.py的env_check()方法（≤25行限制）
- 接收输入：env_file参数（可选）
- 输出交付：返回整数状态码给main.py

行为链逻辑：
该动作是启动序列的第一个必执行节点，成功后进入deps_check阶段，失败则直接终止整个启动流程。

执行要素明细：
- 输入字段：env_file（str，可选指定配置文件路径）
- 输出格式：整数返回码（0=成功，1=失败）
- 依赖配置：需要验证.env文件中的所有必需环境变量完整性
- 依赖Schema或模型：routing_agent的config_manager服务提供的配置结构
- 调用方式：同步调用，单一职责方法
- 错误处理策略：环境变量缺失返回BOOT/ENV_MISSING错误，配置格式错误返回BOOT/CONFIG_INVALID错误
- 日志记录字段：request_id、module_name（boot）、operation（env_check）、duration_ms、success
- 限制条件：方法长度不超过25行，不得包含直接I/O操作

⚠️ 未定义项识别：
⚠️ 未定义：具体需要验证的环境变量清单和验证规则未完全明确
⚠️ 未定义：routing_agent的config_manager服务接口规范未定义
```

------------------------------

### A3: 外部依赖服务连通性检查

```
简要说明：
检查外部依赖服务的连通性和可用性，区分硬依赖和软依赖，支持降级模式。硬依赖失败会阻止启动，软依赖失败允许系统在降级模式下继续启动。

触发时机：
在env_check成功后自动触发，或用户可通过skip_non_critical参数跳过非关键依赖检查。

模块关系：
- 执行模块：launcher.py的deps_check()方法（≤25行限制）
- 接收输入：skip_non_critical参数（bool，默认True）
- 输出交付：返回整数状态码给启动流程

行为链逻辑：
该动作是环境检查后的第二阶段，成功或部分成功后进入连接器装配阶段。

执行要素明细：
- 输入字段：skip_non_critical（bool，默认True）
- 输出格式：整数返回码（0=全部成功，1=硬依赖失败，2=软依赖失败但可降级）
- 依赖配置：硬依赖服务（MongoDB、Redis、OpenAI API），软依赖服务（MinIO、ChromaDB）
- 调用方式：同步调用，需要调用各连接器的健康检查方法
- 错误处理策略：硬依赖不可用返回BOOT/DEPS_UNAVAILABLE错误码1，软依赖失败返回错误码2但继续启动
- 日志记录字段：request_id、module_name（boot）、operation（deps_check）、duration_ms、success、retry_count
- 限制条件：方法长度不超过25行，通过连接器间接访问外部服务

⚠️ 未定义项识别：
⚠️ 未定义：各连接器的健康检查方法接口未完全定义
⚠️ 未定义：降级模式的具体触发条件和状态标记机制
```

------------------------------

### A4: 外部服务连接器实例创建

```
简要说明：
通过连接器工厂模式创建所有外部服务的连接器实例，包括数据存储、缓存、对象存储和AI服务连接器。每个连接器封装特定的外部服务访问逻辑。

触发时机：
在deps_check通过后触发，需要根据依赖检查结果决定创建哪些连接器实例。

模块关系：
- 执行模块：launcher.py中的连接器装配方法
- 接收输入：env_config字典和deps_check结果
- 输出交付：连接器实例字典传递给Agent装配阶段

行为链逻辑：
该动作是依赖检查后的连接器准备阶段，成功后进入Agent注册表验证和装配阶段。

执行要素明细：
- 输入字段：env_config（Dict，环境配置）、available_services（依赖检查结果）
- 输出格式：Dict[str, Any]格式的连接器实例字典
- 依赖配置：各连接器的配置参数（MONGODB_CONNECTION_STRING、REDIS_MAX_CONNECTIONS等）
- 依赖Schema或模型：各连接器类的标准接口（create_connection、health_check、close_connection）
- 调用方式：同步调用，通过连接器工厂创建实例
- 错误处理策略：必需连接器创建失败终止启动，可选连接器失败记录警告继续
- 日志记录字段：request_id、module_name（boot）、operation（create_connectors）、duration_ms、success
- 限制条件：不得在launcher中包含具体连接实现逻辑，仅做装配编排

⚠️ 未定义项识别：
⚠️ 未定义：连接器工厂create_all_connectors()方法的具体接口签名
⚠️ 未定义：各连接器类的标准接口规范未完全明确
```

------------------------------

### A5: Agent注册表加载与验证

```
简要说明：
从applications/__registry__.py加载Agent配置信息，验证注册表结构完整性、依赖关系正确性，并检测循环依赖。确保Agent装配的前置条件满足。

触发时机：
在连接器实例创建完成后触发，是Agent装配的前置验证步骤。

模块关系：
- 执行模块：launcher.py中的注册表验证方法
- 接收输入：applications/__registry__.py文件
- 输出交付：验证后的Agent配置字典传递给分层装配阶段

行为链逻辑：
该动作是装配准备阶段，验证成功后进入三层Agent分层装配流程。

执行要素明细：
- 输入字段：registry文件路径（applications/__registry__.py）
- 输出格式：结构化的Agent配置字典，按core、business、service分层
- 依赖配置：注册表必需字段（name、module、required）
- 调用方式：同步调用，直接读取Python模块
- 错误处理策略：注册表格式错误终止启动，循环依赖检测失败返回配置错误
- 日志记录字段：request_id、module_name（boot）、operation（validate_registry）、duration_ms、success
- 限制条件：仅验证注册表结构，不执行Agent实例化

⚠️ 未定义项识别：
⚠️ 未定义：applications/__registry__.py的完整结构和字段定义
⚠️ 未定义：Agent间依赖关系的具体表达方式（dependencies字段等）
```

------------------------------

### A6: core层Agent并发装配

```
简要说明：
装配核心层Agent（routing_agent、auth_agent、database_agent等），这些是系统最基础的Agent，为其他层提供基础服务能力。支持同层并发装配以提高启动效率。

触发时机：
在注册表验证成功后触发，是三层装配的第一层。

模块关系：
- 执行模块：launcher.py中的core层装配方法
- 接收输入：core层Agent配置、连接器实例字典
- 输出交付：已装配的core层Agent实例传递给business层装配

行为链逻辑：
该动作是三层装配序列的第一层，成功后进入business层装配，失败则终止整个装配流程。

执行要素明细：
- 输入字段：core_agents_config（Dict）、connectors（Dict[str, Any]）
- 输出格式：装配成功的Agent实例字典
- 依赖Schema或模型：AgentFactory.create_agent()接口
- 调用方式：支持同层Agent并发装配，异步操作
- 错误处理策略：必需Agent装配失败终止启动，可选Agent装配失败记录警告继续
- 日志记录字段：request_id、module_name（boot）、operation（assemble_core_agents）、duration_ms、success
- 限制条件：严格按照三层顺序，core层必须在business层之前完成

⚠️ 未定义项识别：
⚠️ 未定义：AgentFactory.create_agent()方法的具体接口和实现方式
⚠️ 未定义：Agent实例化时的依赖注入机制具体实现
```

------------------------------

### A7: business层Agent并发装配

```
简要说明：
装配业务层Agent（resume_agent、matching_agent、company_identity_agent等），这些Agent实现核心业务逻辑，依赖core层Agent提供的基础服务。

触发时机：
在core层Agent装配成功后自动触发，是三层装配的第二层。

模块关系：
- 执行模块：launcher.py中的business层装配方法
- 接收输入：business层Agent配置、core层Agent实例、连接器实例
- 输出交付：已装配的business层Agent实例传递给service层装配

行为链逻辑：
该动作依赖core层装配成功，完成后进入service层装配，是装配序列的中间环节。

执行要素明细：
- 输入字段：business_agents_config（Dict）、core_agents（Dict）、connectors（Dict[str, Any]）
- 输出格式：装配成功的business层Agent实例字典
- 依赖Schema或模型：业务Agent的构造函数接口，需要core层Agent和连接器注入
- 调用方式：支持同层Agent并发装配，依赖core层Agent实例
- 错误处理策略：必需Agent装配失败终止启动，可选Agent装配失败记录警告继续
- 日志记录字段：request_id、module_name（boot）、operation（assemble_business_agents）、duration_ms、success
- 限制条件：必须等待core层完成后才能开始，同层内可并发

⚠️ 未定义项识别：
⚠️ 未定义：business层Agent与core层Agent的具体依赖注入接口
⚠️ 未定义：各business层Agent的初始化参数结构
```

------------------------------

### A8: service层Agent并发装配

```
简要说明：
装配服务层Agent（entry_agent、frontend_service_agent等），这些Agent提供对外服务接口，依赖business层和core层Agent的服务能力。

触发时机：
在business层Agent装配成功后自动触发，是三层装配的最后一层。

模块关系：
- 执行模块：launcher.py中的service层装配方法
- 接收输入：service层Agent配置、business层和core层Agent实例
- 输出交付：完整的Agent实例体系，系统进入启动就绪状态

行为链逻辑：
该动作是装配序列的终点，完成后系统进入服务就绪状态，开始提供对外服务。

执行要素明细：
- 输入字段：service_agents_config（Dict）、business_agents（Dict）、core_agents（Dict）
- 输出格式：完整的三层Agent实例体系
- 依赖Schema或模型：服务层Agent的构造函数接口，需要business和core层Agent注入
- 调用方式：支持同层Agent并发装配，依赖前两层Agent实例
- 错误处理策略：entry_agent等关键服务Agent失败终止启动，其他可选服务Agent失败记录警告
- 日志记录字段：request_id、module_name（boot）、operation（assemble_service_agents）、duration_ms、success
- 限制条件：必须等待business层完成后才能开始，依赖完整的下层Agent支撑

⚠️ 未定义项识别：
⚠️ 未定义：service层Agent与下层Agent的依赖注入具体实现
⚠️ 未定义：entry_agent和frontend_service_agent的启动端口配置机制
```

------------------------------

### A9: 系统服务启动与端口监听

```
简要说明：
启动对外服务端口监听，包括entry_agent和routing_agent的服务端口，使系统能够接收外部请求。这是系统从装配状态转入运行状态的关键步骤。

触发时机：
在所有Agent装配完成后触发，标志系统从装配状态进入运行服务状态。

模块关系：
- 执行模块：launcher.py中的服务启动方法
- 接收输入：装配完成的Agent实例、端口配置
- 输出交付：启动状态和端口监听信息

行为链逻辑：
该动作是装配完成后的服务启用，成功后进入最终健康验证阶段。

执行要素明细：
- 输入字段：agent_instances（Dict）、port_config（ENTRY_AGENT_PORT、ROUTING_AGENT_PORT）
- 输出格式：服务启动状态和监听端口信息
- 依赖配置：端口配置来源于.env文件中的端口参数
- 调用方式：同步调用，启动HTTP/WebSocket服务监听
- 错误处理策略：端口占用或启动失败返回BOOT/TIMEOUT错误，提供端口检查建议
- 日志记录字段：request_id、module_name（boot）、operation（start_services）、duration_ms、success
- 限制条件：不得在launcher中实现具体的服务启动逻辑，通过Agent实例的启动方法间接调用

⚠️ 未定义项识别：
⚠️ 未定义：Agent实例的启动方法接口规范未明确
⚠️ 未定义：端口占用检测和故障恢复机制
```

------------------------------

### A10: 系统最终健康状态验证

```
简要说明：
对整个系统进行最终健康检查，验证所有组件正常运行，包括Agent状态、连接器连通性、服务端口响应等。确认系统完全就绪可对外提供服务。

触发时机：
在系统服务启动完成后触发，或用户单独执行python main.py --health时触发。

模块关系：
- 执行模块：launcher.py的health()方法（≤25行限制）
- 接收输入：运行中的系统实例
- 输出交付：系统健康状态报告和返回码

行为链逻辑：
该动作是启动序列的最终验证节点，成功则系统完全就绪，失败则需要排查具体组件问题。

执行要素明细：
- 输入字段：system_instance（运行中的系统实例）
- 输出格式：整数返回码（0=健康，1=异常）和健康状态详情
- 依赖配置：各组件的健康检查接口
- 调用方式：同步调用，调用各Agent和连接器的健康检查方法
- 错误处理策略：组件异常时返回具体异常信息和恢复建议
- 日志记录字段：request_id、module_name（boot）、operation（health_check）、duration_ms、success
- 限制条件：方法长度不超过25行，不得包含具体的健康检查实现逻辑

⚠️ 未定义项识别：
⚠️ 未定义：各Agent和连接器的健康检查方法标准接口
⚠️ 未定义：健康状态详情的具体输出格式结构
```

------------------------------

### A11: 系统优雅关闭与资源清理

```
简要说明：
安全关闭系统运行，包括停止服务端口监听、关闭Agent实例、释放连接器资源、清理临时文件等。确保系统能够干净地停止运行。

触发时机：
接收到系统关闭信号时触发，或在启动失败需要清理时触发。

模块关系：
- 执行模块：launcher.py的shutdown()方法（≤25行限制）
- 接收输入：运行中的系统实例
- 输出交付：关闭状态码和清理完成确认

行为链逻辑：
该动作是系统生命周期的终止节点，按照与启动相反的顺序进行资源清理。

执行要素明细：
- 输入字段：system_instance（需要关闭的系统实例）
- 输出格式：整数返回码（0=成功关闭，1=关闭异常）
- 依赖配置：各组件的关闭方法接口
- 调用方式：同步调用，按启动逆序关闭各组件
- 错误处理策略：关闭异常时记录错误日志，强制清理剩余资源
- 日志记录字段：request_id、module_name（boot）、operation（shutdown）、duration_ms、success
- 限制条件：方法长度不超过25行，关闭顺序与启动顺序相反

⚠️ 未定义项识别：
⚠️ 未定义：各Agent和连接器的关闭方法标准接口
⚠️ 未定义：强制清理机制的具体实现方式
```

------------------------------
