# entry_agent_Structured_readme.md

## 结构化文档骨架 - entry_agent 系统入口点Intent验证器

---

### A1: 术语与名词表

```
核心术语统一定义包括Intent白名单、数据规范校验、字段完整性、routing_agent、AgentRequest/AgentResponse等关键概念的准确定义。
```

------------------------------

### A2: 模块概述与定位

```
entry_agent是Career Bot系统的轻量级入口验证器，采用缓存优先策略实现高效验证。
核心职责是检查用户意图是否在允许列表中，并验证数据字段的完整性。
系统启动时一次性从routing_agent加载配置并缓存到内存，运行时直接从缓存验证，无需重复网络调用。
职责边界专注于验证逻辑，不处理业务逻辑、状态管理和复杂路由。
```

------------------------------

### A3: 技术规范约束

```
├── A-3.1: Python环境规范
│   └── Python 3.10+强制要求，支持asyncio异步并发处理，使用requirements.txt管理依赖版本
├── A-3.2: Pydantic V2规范
│   └── 必须使用model_validate()、model_dump()、Field()、BaseModel，严禁使用.dict()、.parse_obj()、.json()、parse_obj_as()
├── A-3.3: 异步处理规范
│   └── 主要方法使用async def，禁止同步阻塞操作
├── A-3.4: 配置管理规范
│   └── 启动时通过await routing_agent.get_config()一次性加载配置并缓存到内存，运行时直接从缓存读取
├── A-3.5: 模块协作规范
│   └── 被动调用模式，仅响应routing_agent调度，统一通过await routing_agent.call_agent()转发请求，仅暴露async def run()接口
├── A-3.6: 日志记录规范
│   └── 使用Python标准logging模块，必要字段包括request_id、agent_name、timestamp、level，JSON格式结构化记录，禁止使用print()
├── A-3.7: 异常处理规范
│   └── 使用标准异常类型，异常向routing_agent传播，保留日志记录
```

------------------------------

### A4: 依赖与职责

```
├── A-4.1: 上游触发源
│   ├── routing_agent调度请求（intent验证需求）
│   └── 系统启动时从routing_agent获取配置并缓存
├── A-4.2: 下游调用对象
│   └── routing_agent唯一业务调度中心
├── A-4.3: 数据约束条件
│   └── Intent白名单验证、字段完整性检查
├── A-4.4: 并发顺序性控制
│   └── 请求并发处理、验证顺序保证
```

------------------------------

### A5: 重大决策

```
├── A-5.1: 轻量化验证策略
│   └── 专注Intent白名单检查和数据规范验证，拒绝复杂状态管理
├── A-5.2: 严格职责边界
│   └── 不处理用户认证、状态管理、业务逻辑，仅负责基础验证
├── A-5.3: 快速转发机制
│   └── 验证通过立即转发routing_agent，验证失败立即拒绝
├── A-5.4: 缓存优先策略
│   └── 启动时一次性加载配置，运行时直接从内存缓存验证，保证O(1)查找效率
```

------------------------------

### A6: 契约与字段

```
├── A-6.1: Intent验证字段
│   ├── intent - 用户意图标识符（必须字段）
│   ├── request_id - 请求唯一标识符（必须字段）
│   └── timestamp - 请求时间戳（必须字段）
├── A-6.2: Intent白名单配置字段
│   ├── intent_whitelist - 允许的intent列表配置
│   └── validation_rules - 字段验证规则配置
├── A-6.3: 错误码
│   ├── ENTRY/INTENT_NOT_ALLOWED - 意图不在白名单中
│   ├── ENTRY/FIELD_MISSING - 必需字段缺失
│   └── ENTRY/VALIDATION_FAILED - 数据验证失败
```

------------------------------

### A7: 标准数据格式

```
├── A-7.1: 简化AgentRequest输入结构
│   └── request_id、task_type、intent、timestamp必需字段定义
├── A-7.2: 简化AgentResponse输出结构
│   └── request_id、agent_name、success、timestamp、error_code基础字段定义
├── A-7.3: 处理结果状态
│   └── valid（验证通过）、invalid_intent（意图无效）、field_missing（字段缺失）三种状态
```

------------------------------

### A8: 配置获取机制

```
├── A-8.1: 启动时缓存加载
│   └── 系统启动时通过routing_agent.get_config()一次性加载所有配置并存储到内存缓存
├── A-8.2: 运行时缓存读取
│   └── 每次验证直接从内存缓存读取，无需重复调用routing_agent
├── A-8.3: 配置内容
│   ├── intent_whitelist（允许的intent列表，使用set存储保证O(1)查找）
│   ├── validation_rules（字段验证规则配置）
│   └── agent_mappings（intent到agent的映射关系）
```

------------------------------

### A9: 系统架构位置

```
├── A-9.1: 缓存验证器架构
│   ├── entry_agent（缓存验证器）：负责intent白名单验证、数据字段校验、格式检查
│   ├── routing_agent（业务调度器）：负责agent匹配、任务编排、状态管理和流程控制
│   └── 协作流程：entry_agent验证 → routing_agent调度 → 业务agent执行
├── A-9.2: 职责边界重定义
│   ├── entry_agent职责：✅验证（intent白名单、数据字段、格式检查）❌业务逻辑
│   ├── routing_agent职责：✅调度（agent匹配、任务编排、状态管理）❌验证逻辑
│   └── 设计优势：职责分离清晰，性能高效，维护简单
```

------------------------------

### A10: 核心验证逻辑

```
├── A-10.1: Intent白名单验证
│   ├── 从内存缓存读取intent_whitelist（set数据结构，O(1)查找）
│   ├── 直接对比请求intent是否在白名单中
│   └── 返回验证结果：valid/invalid_intent
├── A-10.2: 数据规范校验
│   ├── 检查必需字段：request_id、task_type、timestamp
│   ├── 验证字段格式和数据类型
│   ├── 可选字段存在性检查
│   └── 返回验证结果：valid/field_missing/validation_failed
├── A-10.3: 处理结果
│   ├── 验证通过：转发给routing_agent.process_verified_request()
│   ├── 验证失败：返回标准错误响应，包含error_code和详细错误信息
│   └── 性能保证：内存缓存验证，无网络调用开销
```

------------------------------

### A11: 核心接口规范

```
├── A-11.1: 主要接口
│   ├── async def run(request: AgentRequest) -> AgentResponse（核心处理接口）
│   ├── async def initialize(routing_agent) -> None（启动时初始化接口）
│   └── async def get_cached_config() -> dict（获取缓存配置接口）
├── A-11.2: 处理流程
│   ├── 系统启动：调用initialize()一次性加载配置到缓存
│   ├── 请求处理：run()方法直接从缓存验证，无需网络调用
│   ├── 验证通过：转发routing_agent.process_verified_request()
│   └── 验证失败：返回标准错误响应
```

------------------------------

### A12: 基本日志要求

```
├── A-12.1: 必需日志字段
│   └── request_id、agent_name、timestamp、intent、success、error_code
├── A-12.2: 日志级别
│   └── INFO（正常处理）、ERROR（验证失败）
```

------------------------------

### A13: 依赖清单

```
├── A-13.1: 必需依赖
│   └── routing_agent（配置获取和转发）
├── A-13.2: 数据模型
│   └── AgentRequest、AgentResponse（从global_schemas导入）
```

------------------------------

---

### A12: 文件架构设计

```
├── A-12.1: 核心文件结构
│   ├── entry_agent.py（主文件：编排验证逻辑，日志记录，请求转发）
│   ├── cache/config_cache.py（配置缓存：启动时加载，运行时提供高效访问）
│   ├── validators/intent_validator.py（Intent验证：直接从缓存验证intent白名单）
│   ├── validators/data_validator.py（数据验证：检查字段完整性和格式正确性）
│   └── __init__.py（包初始化：统一导出核心接口）
├── A-12.2: 设计原则
│   ├── 缓存优先：启动时加载，运行时直接使用，避免重复网络调用
│   ├── 职责单一：每个模块只负责一个具体的验证职责
│   ├── 性能导向：使用set等高效数据结构保证O(1)查找
│   └── 接口统一：所有验证器返回标准化的ValidationResult对象
```

---

```

## 模块契约总结

entry_agent是Career Bot系统的轻量级入口验证器，采用缓存优先策略实现高效验证。

### 核心职责

1. **启动时配置加载** - 系统启动时一次性从routing_agent获取配置并缓存到内存
2. **Intent白名单验证** - 直接从内存缓存验证用户意图，O(1)时间复杂度
3. **数据规范校验** - 验证AgentRequest字段的完整性和格式正确性
4. **快速转发机制** - 验证通过则转发routing_agent，验证失败则立即拒绝

### 技术特点

- **缓存优先设计** - 启动时加载，运行时直接验证，避免重复网络调用
- **高效数据结构** - 使用set存储intent白名单，保证O(1)查找效率
- **职责分离清晰** - 只负责验证，不处理业务逻辑、状态管理和复杂路由
- **性能导向** - 内存直接访问，无磁盘I/O延迟，响应速度极快

### 架构优势

- **减少网络开销** - 启动后无需每次请求都调用routing_agent.get_config()
- **提高系统性能** - 内存缓存验证，降低请求处理延迟
- **职责边界明确** - 验证和调度完全分离，便于维护和扩展
- **启动优化** - 一次性加载配置，运行时零额外开销

通过缓存优先的验证机制，entry_agent在保证系统安全的同时实现极高的处理性能，成为真正的高效入口验证器。
