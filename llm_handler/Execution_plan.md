### A1: 唯一入口与任务接收（run/request）
```
说明：llm_handler_agent作为系统唯一LLM调用通道，仅通过统一入口函数run(request)被routing_agent动员执行，职责是接收上游已构建好的prompt与调用参数，进行合规校验后转交适配层完成LLM推理，并返回未加工的原始响应，确保与业务逻辑解耦与可观测。
执行时机：当routing_agent分发LLM任务时触发；本模块不主动发起任何任务；无HTTP路径，内部调用完成一次请求-响应闭环。
模块关系：由routing_agent发起；由llm_handler_agent执行；结果返回routing_agent，再由其回传上游模块；不得被其他模块直接调用。
输入输出与数据格式：输入为AgentRequest（request_id、task_type、user_id、timestamp、message、intent等扁平化字段），最小请求要求message存在；输出为AgentResponse（request_id、agent_name="llm_handler_agent"、success、timestamp、processing_status、results或error_details）。
同步/异步与并发：run为异步函数；整体异步执行；并发由模块并发限制统一控制；不得使用线程池/进程池。
配置/模型/调用边界：调用仅接受routing_agent；配置仅可由routing_agent的global_config提供；强制模型gpt-4o-2024-08-06；禁止任何模块绕过本模块直接访问LLM供应商API。
日志与指标：全链路记录request_id、operation、duration_ms、success、retry_count；按约定指标上报请求计数、成功率、时延分布。
异常与降级：仅抛出仓库标准异常基类及子类；不得抛裸异常；错误码前缀LLM/；错误信息面向调用方。
行为链关系：本动作为入口，顺序先于A2输入校验与Schema验证，后续依次进入A3类型分发。
特殊依赖或注意事项：无状态设计，不保存调用历史；禁止直接访问DB/Cache/FS；Pydantic V2用作Schema验证。
未定义项：routing_agent内部调用的具体函数名/路径 ⚠️ 未定义；additional_params具体键集 ⚠️ 未定义。
```
------------------------------
### A2: AgentRequest与LLMRequest输入校验与Schema验证
```
说明：对AgentRequest与LLMRequest字段进行严格校验，确保类型、长度、必填性满足契约，避免向下游传递非法数据；遵循Pydantic V2（model_validate、model_dump、Field）。
执行时机：A1完成接收后立即执行；是所有下游步骤的前置条件。
模块关系：由llm_handler_agent执行；输入来自routing_agent传入的AgentRequest；校验通过的数据供A3类型分发与A5参数合成使用；校验失败直接构建失败AgentResponse并返回routing_agent。
输入输出与数据格式：AgentRequest必含request_id、task_type、user_id、timestamp、message；LLMRequest字段：prompt:str(1..50000)、system_prompt:Optional[str(<=5000)]、temperature:float[0.0,2.0]默认0.7、max_tokens:int[1,4000]默认1000、json_mode:bool默认False；当message为空或越界时判定为LLM/INVALID_PROMPT或LLM/PROMPT_TOO_LONG。
同步/异步与并发：本动作为纯计算校验，异步上下文内执行，无阻塞外部I/O。
配置/模型/调用边界：输入校验规则来自J1；不得改变字段命名与层级；禁止在本动作写入外部存储。
日志与指标：记录operation=validate_input；成功/失败与duration_ms；不记录敏感信息；必要时脱敏。
异常与降级：输入不合规映射至LLM/INVALID_PROMPT、LLM/PROMPT_TOO_LONG、LLM/INVALID_PARAMS；异常不向外泄露实现细节。
行为链关系：顺序先于A3；校验失败直接终止并返回；通过则进入A3任务类型识别。
特殊依赖或注意事项：严格遵守Token上限（输入最大50000、输出最大4000）作为参数边界；不得在此处构建业务提示或prompt改写。
未定义项：context整体结构除data.prompt外的其他必填/可选键 ⚠️ 未定义；user_id格式规范 ⚠️ 未定义。
```
------------------------------
### A3: 任务类型识别与分支控制（llm_completion/llm_chat/llm_json/health_check/api_status）
```
说明：依据AgentRequest.task_type进行分支；将标准文本生成、对话式交互、JSON结构化输出与健康/可用性检查分流到不同后续路径；保证不可识别类型被拒绝并返回标准错误。
执行时机：A2校验通过后立即；对执行链路进行控制分派。
模块关系：由llm_handler_agent执行；输入来自A2；输出路由到A4~A13（LLM调用链）或A14（健康/可用性检查）。
输入输出与数据格式：task_type允许值：llm_completion、llm_chat、llm_json、health_check、api_status；不在集合内→LLM/INVALID_PARAMS；分支后维持AgentRequest上下文与LLMRequest参数。
同步/异步与并发：分支判断为同步计算；后续各分支在异步上下文内继续。
配置/模型/调用边界：不得在此处变更模型与配置；保持透明分发。
日志与指标：记录operation=route_task，包含task_type与success标记。
异常与降级：未知task_type→失败AgentRequestResponse，错误码LLM/INVALID_PARAMS。
行为链关系：顺序先于A4；health_check与api_status走A14分支并在该分支终止；其余进入A4配置获取。
特殊依赖或注意事项：此处仅作分发，不得引入业务改写策略。
未定义项：llm_chat与llm_json在调用参数差异化细节 ⚠️ 未定义（仅知json_mode存在）。
```
------------------------------
### A4: 配置获取与唯一来源约束（global_config）
```
说明：从routing_agent的global_config中拉取本模块所需配置；遵循“配置唯一来源”规则，禁止本地硬编码可变配置；新增配置键需有默认值与回滚策略。
执行时机：A3完成分发后，进入LLM调用前置阶段；A8客户端装配、A9超时控制、A10重试策略均依赖本动作产物。
模块关系：由llm_handler_agent执行；通过routing_agent.get_config("llm_handler_agent", config_type)获取；产出供A5~A10使用；不向外部下游输出。
输入输出与数据格式：配置类型包含model_config、rate_limits、timeout_config、api_config、retry_config、security_config、emergency_prompts；模型统一要求gpt-4o-2024-08-06。
同步/异步与并发：通过异步方式获取配置；不得阻塞或缓存为跨请求状态。
配置/模型/调用边界：配置仅可经由routing_agent的global_config读取；禁止私改配置键名/层级。
日志与指标：operation=load_config；记录成功与耗时；不写敏感值。
异常与降级：配置缺失或访问异常→LLM/API_ERROR或相关错误码；严禁在异常时落地临时本地配置。
行为链关系：顺序先于A5参数合成与A8客户端装配；失败则终止并返回错误。
特殊依赖或注意事项：api_key须来自model_config或api_config；紧急prompt仅用于系统诊断。
未定义项：各配置具体字段结构与示例值 ⚠️ 未定义；回滚策略实施细节 ⚠️ 未定义；key_rotation_enabled行为细节 ⚠️ 未定义（J-5.1待补）。
```
------------------------------
### A5: 模型与请求参数合成（强制gpt-4o-2024-08-06）
```
说明：基于A2校验后的LLMRequest与A4的model_config，合成最终调用参数；强制选择模型gpt-4o-2024-08-06；保持上游prompt原样，不做业务改写；根据json_mode与max_tokens等形成最终参数集。
执行时机：A4配置加载完成后立即；在A8客户端装配前。
模块关系：由llm_handler_agent执行；输入来自A2与A4；产出供A8与A9实际调用使用；不直接对外输出。
输入输出与数据格式：输入prompt、system_prompt、temperature、max_tokens、json_mode；输出为适配层可直接使用的参数字典（未定义具体字段名）；严格遵守Token限制（输入<=50000，输出<=4000）。
同步/异步与并发：本动作为参数整备，异步上下文内无外部I/O。
配置/模型/调用边界：模型名固定gpt-4o-2024-08-06；禁止动态切换至其他模型；参数范围严格按J1规范。
日志与指标：仅记录operation=build_params与成功标记；不得输出prompt全文或密钥。
异常与降级：参数越界映射到LLM/INVALID_PARAMS；不进行隐式截断或自动纠正。
行为链关系：顺序先于A8；失败则终止返回。
特殊依赖或注意事项：保持与上游prompt的“原样性”，不得注入、拼接或重写。
未定义项：适配层参数字典精确键名 ⚠️ 未定义。
```
------------------------------
### A6: 安全与合规输入检查（安全配置与黑名单约束）
```
说明：按照安全配置与黑名单进行输入合规性检查与执行边界守护；禁止在本模块定义本地业务模型；禁止硬编码配置；禁止跨层I/O；禁止未脱敏日志。
执行时机：A5之后、A8之前；作为调用前的最后一道安全门。
模块关系：由llm_handler_agent执行；输入来自A2与A4；若违规直接构造失败响应返还routing_agent；合规则继续A7并发与速率限制。
输入输出与数据格式：不改变AgentRequest与LLMRequest，仅进行策略校验；黑名单正则包含“class .*Model”“data class .*”“interface .*DTO”“API_KEY=”“timeout\\s*=\\s*\\d+”“retry\\s*=\\s*\\d+”“http”“db”“sql”“open(”“requests”“fetch”“Thread”“Process”“fork”“Pool”“未脱敏日志关键词”。
同步/异步与并发：同步策略判断；无外部I/O。
配置/模型/调用边界：遵从security_config；最小权限原则，API密钥通过global_config管理。
日志与指标：记录operation=security_check；仅输出判定结果与request_id。
异常与降级：违规映射至LLM/INVALID_PARAMS或LLM/API_ERROR（按策略分类）；不泄露内部策略细节。
行为链关系：顺序先于A7；失败终止。
特殊依赖或注意事项：不得落地或缓存敏感数据；对日志进行必要脱敏。
未定义项：security_config具体键名与取值 ⚠️ 未定义。
```
------------------------------
### A7: 并发限制与速率限制应用（最大100并发）
```
说明：依据模块限制与rate_limits应用并发与速率控制，确保最大并发不超过100，并在需要时进行排队或拒绝；为后续实际LLM调用提供稳定窗口。
执行时机：A6通过后，在A8适配层调用前；贯穿调用过程的门控。
模块关系：由llm_handler_agent执行；输入为A4的rate_limits与并发限制；影响A8~A10调用行为；不向外部输出。
输入输出与数据格式：无新增数据结构；对当前请求施加并发/速率策略；超限时返回失败响应。
同步/异步与并发：采用异步原语实现；禁止线程池/进程池；遵循仅异步的并发控制。
配置/模型/调用边界：并发上限100；响应时间上限300秒；策略细节由rate_limits与timeout_config提供。
日志与指标：记录operation=apply_rate_limit；输出是否限流、排队耗时；指标更新请求量与被限流量。
异常与降级：超过速率限制→LLM/RATE_LIMITED；不要自定义退避以外的隐式行为。
行为链关系：先于A8；限流失败则终止。
特殊依赖或注意事项：不得突破模块并发边界；避免饥饿。
未定义项：具体限流算法与窗口参数 ⚠️ 未定义。
```
------------------------------
### A8: 适配层客户端装配（LiteLLM）与密钥注入
```
说明：在Adapter层基于A4的model_config与api_config装配LiteLLM客户端；使用litellm.acall执行异步调用；所有密钥从配置注入，不得硬编码。
执行时机：A7之后；在A9正式调用前完成客户端与上下文装配。
模块关系：由llm_handler_agent的Adapter执行；输入为A4与A5的参数；产出为可执行的异步调用器供A9使用；不对外输出。
输入输出与数据格式：客户端接收模型名gpt-4o-2024-08-06与api_key；其余参数沿用A5合成；无额外公共结构暴露。
同步/异步与并发：装配过程在异步上下文进行；不进行外部I/O。
配置/模型/调用边界：api_key来源model_config["api_key"]或api_config；严格遵守模型统一策略。
日志与指标：记录operation=adapter_init；不输出密钥；记录装配耗时。
异常与降级：装配失败映射LLM/INVALID_MODEL或LLM/API_ERROR。
行为链关系：先于A9；失败终止。
特殊依赖或注意事项：禁止绕过适配层直接调用供应商SDK。
未定义项：客户端装配的对象结构与生命周期细节 ⚠️ 未定义。
```
------------------------------
### A9: LLM异步调用执行与超时控制
```
说明：通过litellm.acall在异步上下文中发起模型推理请求；应用timeout_config进行超时控制；记录调用耗时以用于日志与指标。
执行时机：A8完成装配后立即执行；是链路中的核心外部调用动作。
模块关系：由llm_handler_agent的Adapter执行；输入为A5参数与A4的timeout_config；下游对接OpenAI API（经LiteLLM）；输出为模型原始响应返回上层以供A11格式化。
输入输出与数据格式：输入为合成参数；输出为LLM原始文本或JSON（取决于json_mode），不做业务加工。
同步/异步与并发：严格异步；遵守响应时间上限300秒。
配置/模型/调用边界：timeout_config控制请求超时；模型名固定；不得进行多供应商回退切换（未定义）。
日志与指标：记录operation=llm_call、duration_ms、success、retry_count（由A10管理）；更新时延与成功率指标。
异常与降级：API超时→LLM/API_TIMEOUT；网络异常→LLM/NETWORK_ERROR；速率限制→LLM/RATE_LIMITED；其他API错误→LLM/API_ERROR。
行为链关系：顺序先于A10重试与A11格式化；失败可能触发A10重试；成功则进入A11响应标准化。
特殊依赖或注意事项：遵守敏感信息不落日志；不回传密钥或内部错误堆栈。
未定义项：返回payload内部字段结构（供应商原始结构） ⚠️ 未定义。
```
------------------------------
### A10: 重试策略与错误码映射
```
说明：根据retry_config在允许的范围内对可恢复错误进行异步重试；对错误统一映射为约定的LLM/*错误码；错误信息对调用方友好且不泄露实现细节。
执行时机：A9调用失败的可重试场景触发；A9成功时跳过。
模块关系：由llm_handler_agent执行；输入为A4.retry_config与A9错误；输出为重试后成功的原始响应或最终失败错误码与消息。
输入输出与数据格式：不改变AgentRequest结构；仅更新retry_count并将最终状态交由A11构造AgentRequestResponse。
同步/异步与并发：异步重试；不得使用线程/进程；遵守模块并发限制。
配置/模型/调用边界：retry_config定义次数与策略（字段未定义）；禁止自定义与配置不一致的退避策略。
日志与指标：记录operation=retry、retry_count、最终success；指标计入请求成功率与时延。
异常与降级：超过重试上限或不可恢复错误→对应LLM/*错误码返回；J-5.3模型切换策略为待补，不实施自动模型回退。
行为链关系：位于A9与A11之间；最终结果进入A11标准化。
特殊依赖或注意事项：不得更改上游prompt；不得合成业务层补救文本。
未定义项：retry_config具体字段（次数、间隔、策略） ⚠️ 未定义；哪些错误可重试的枚举表 ⚠️ 未定义。
```
------------------------------
### A11: 响应标准化与AgentRequestResponse构建
```
说明：将LLM原始响应与元数据格式化为AgentRequestResponse；包含request_id、agent_name、success、timestamp、response或error；不进行语义级解析或业务解释。
执行时机：A9成功或A10完成后立即执行；是对外返回前的最后一步。
模块关系：由llm_handler_agent执行；输入为A9/A10的结果与A1的AgentRequest基础字段；输出AgentRequestResponse返回routing_agent。
输入输出与数据格式：LLMResponse模型字段包括raw_output、model_used、tokens_used(TokenUsage)、call_duration_ms（若可得）；标准响应字段按E-1.3。
同步/异步与并发：异步上下文内执行，纯计算。
配置/模型/调用边界：遵守E-1.3响应结构；不得附带额外内部字段。
日志与指标：记录operation=build_response与duration_ms；不打印raw_output全文（如存在敏感内容则脱敏）。
异常与降级：格式化失败映射到LLM/API_ERROR；不向外暴露内部栈信息。
行为链关系：顺序在A10之后并终止，响应回交routing_agent。
特殊依赖或注意事项：保持原始输出的“未处理性”，不转换为业务结构。
未定义项：TokenUsage的completion_tokens_detail字段为待补（J-5.2）。
```
------------------------------
### A12: Token使用统计与性能/费用指标上报
```
说明：统计本次调用的Token用量、耗时等信息，并将模块指标进行上报；指标用于运行监控与容量规划；不改变业务返回。
执行时机：与A11并行或紧随其后；不阻塞响应回传。
模块关系：由llm_handler_agent执行；输入为A9/A10的调用耗时与Token信息；指标供监控系统消费（未定义对接端）。
输入输出与数据格式：必须暴露指标：llm_handler_agent_requests_total、llm_handler_agent_success_rate、llm_handler_agent_duration_seconds；模块特定指标：llm_handler_agent_tokens_used_total、llm_handler_agent_api_cost_total、llm_handler_agent_model_calls_total。
同步/异步与并发：建议异步非阻塞更新（机制未定义），避免影响主链路。
配置/模型/调用边界：不涉及模型参数；遵守无状态约束。
日志与指标：按J3名称进行指标累加；日志记录operation=metrics_update。
异常与降级：指标上报失败不影响主流程，记录日志即可（行为细节未定义）。
行为链关系：与A11并行或随后执行；对外响应已在A11完成。
特殊依赖或注意事项：成本统计需基于Token数据（计算方式未规定）。
未定义项：指标上报的出口/协议/汇聚系统 ⚠️ 未定义；费用计算公式 ⚠️ 未定义。
```
------------------------------
### A13: 日志记录与敏感信息脱敏
```
说明：在关键节点记录必填日志字段，确保可追踪性、性能分析与故障定位；同时遵循敏感信息处理规范，禁止输出密钥、令牌或身份证件等。
执行时机：贯穿A1~A12各关键动作；在动作完成后即时写入；不阻塞主流程。
模块关系：由llm_handler_agent执行；日志输出供运维与审计系统使用（未定义接收端）。
输入输出与数据格式：日志必填：request_id、module_name、operation、duration_ms、success、retry_count；内容需脱敏；错误码采用LLM/{REASON}格式。
同步/异步与并发：可在异步上下文写入；避免阻塞；遵守无状态。
配置/模型/调用边界：遵守E-3.2敏感信息处理；不记录密钥与原始个人敏感数据。
异常与降级：日志系统异常仅记录本地错误事件（机制未定义），不影响主流程。
行为链关系：贯穿全链路并与各动作并行发生；不改变数据流向。
特殊依赖或注意事项：严格执行黑名单中“禁止未脱敏日志”的要求。
未定义项：日志落地/聚合方案、日志级别与格式化模板 ⚠️ 未定义。
```
------------------------------
### A14: 健康检查与API可用性检查（health_check/api_status）
```
说明：处理辅助任务类型以供系统自检；health_check用于模块健康状态检查；api_status用于LLM调用API可用性检查；遵循被动调用与统一返回格式。
执行时机：A3将health_check或api_status分支引导至本动作；与主调用链路互斥。
模块关系：由llm_handler_agent执行；输入来自A3分支；结果返回routing_agent。
输入输出与数据格式：输入为AgentRequest（task_type=health_check或api_status）；输出为AgentRequestResponse，data中包含检查结果（字段未定义）。
同步/异步与并发：异步执行；不进行业务逻辑处理。
配置/模型/调用边界：可读取必要配置进行连通性探测（细节未定义）。
日志与指标：记录operation=health_check或operation=api_status；成功/失败与耗时。
异常与降级：失败时返回可操作指令（如flow指令/重试建议/联系渠道）；错误码按规范映射。
行为链关系：本分支在完成后终止，不进入A4~A13。
特殊依赖或注意事项：不得调用真实LLM生成内容（除可用性探测所需最小调用外，未定义）。
未定义项：检查项列表、判断阈值与返回data结构 ⚠️ 未定义。
```
------------------------------
### A15: 模块限制与执行边界守护（无状态/禁止跨层I/O/性能边界）
```
说明：在整个生命周期内持续约束实现以符合模块限制；无状态设计、禁止直接访问DB/Cache/FS、禁止Main/Aux执行外部I/O、遵守并发/Token/超时等性能边界。
执行时机：贯穿所有动作的设计与实现期以及运行期；在代码审查与执行中均应生效。
模块关系：由llm_handler_agent内部自我约束；对外仅体现为合规行为；不产生对外数据流。
输入输出与数据格式：不引入新结构；仅作用于实现方式与运行约束。
同步/异步与并发：仅允许异步原语；禁止Thread/Process/fork/Pool等并发越界。
配置/模型/调用边界：并发最大100、输入最大50000 tokens、输出最大4000 tokens、超时最大300秒；配置不可本地硬编码。
日志与指标：可在审计日志中记录边界策略启用信息（细节未定义）。
异常与降级：违反边界应在A6触发安全失败或在调用时抛出规范化错误。
行为链关系：对A1~A14提供全程保护；不单独改变链路。
特殊依赖或注意事项：结构稳定性要求禁止为实现便利新建“公共”目录；工作区限制在llm_handler_agent/内；单次变更仅允许一个文件（>300行自动截断的规则为文档限制说明）。
未定义项：如何在运行时强制执行这些边界的机制 ⚠️ 未定义。
```
------------------------------
### A16: 测试与验收门禁对接（冒烟/失败路径）与SLA指标校验
```
说明：本模块需提供冒烟链路测试与失败路径测试；所有变更在通过本模块用例后方可提交；运行中以SLA目标评估可用性、响应时间、并发与Token准确性。
执行时机：在交付与回归阶段由运行流程触发（触发主体未定义）；与线上调用链解耦。
模块关系：由llm_handler_agent提供测试用例并配合执行；上游routing_agent参与完整链路测试；对外不暴露实现细节。
输入输出与数据格式：测试必须使用真实OpenAI API；链路为routing_agent→llm_handler_agent→OpenAI；验证Token计费统计准确性（统计方式未定义）。
同步/异步与并发：测试覆盖异步链路；不得Mock对外契约。
配置/模型/调用边界：与生产一致的配置与模型要求；禁止在测试中绕过配置唯一来源。
日志与指标：测试期间同样记录日志与指标；用于验收判断。
异常与降级：失败路径覆盖API_TIMEOUT、TOKEN_LIMIT、RATE_LIMITED、API_ERROR、INVALID_MODEL等；用例需验证异常恢复。
行为链关系：不属于主请求链；为交付门禁与运行质量评估；通过后方可进入部署与运行阶段（部署策略未定义）。
特殊依赖或注意事项：SLA目标：可用性99.5%；95%调用<30秒；并发100；Token计费统计100%准确。
未定义项：测试执行框架、触发方式与报告格式 ⚠️ 未定义；部署与监控接入细节 ⚠️ 未定义。
```

