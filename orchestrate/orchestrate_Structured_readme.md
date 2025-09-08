# orchestrate - Career Bot 系统编排中枢

## 概述

orchestrate 是 Career Bot 系统的核心编排引擎，采用模块自治注册和意图驱动的架构设计，实现业务模块的动态注册、意图路由和流程编排。通过区分编排层、路由层和注册层的三层架构，实现模块间的松耦合协作和灵活的业务流程管理。

## 核心架构

### 三层架构设计

1. **注册层 (Registry Layer)**
   - 模块能力自主注册管理
   - 意图处理器统一索引
   - 字段结构和依赖关系管理

2. **路由层 (Router Layer)**
   - 意图驱动的动态分发
   - 普通业务意图的路由处理
   - 基于注册信息的智能匹配

3. **编排层 (Orchestration Layer)**
   - 业务流程的链式编排
   - 防循环机制和状态管理
   - 模板化的模块协作

## 核心组件

### 1. orchestrate.py - 主入口

```python
async def run(request):
    """
    系统统一入口，接收前端和模块请求
    职责：纯粹的中转，将请求转发给router处理
    """
```

**核心功能：**
- 请求参数解析和验证
- Intent提取和请求体构建
- 异步调用router进行处理

### 2. registry_center.py - 注册中心

**RegistryCenter类核心数据结构：**
- `module_meta`: 模块元信息存储
- `intent_handlers`: 意图到处理函数映射
- `intent_to_module`: 意图到模块的直接映射
- `module_fields`: 模块字段结构定义
- `dependencies`: 模块依赖关系管理

**核心方法：**
- `register_module()`: 模块自主注册
- `get_handler_for_intent()`: 获取意图处理器
- `get_module_for_intent()`: 获取意图对应模块
- `get_module_fields()`: 获取模块字段结构

### 3. router.py - 路由编排器

**Router类核心特性：**
- 意图分层处理：编排intent vs 普通路由intent
- 链式检查机制：用户点击一次，后台自动检查流程进度
- 防循环机制：完成流程用户标记管理

**业务流程支持：**
- **找工作流程**: mbti → ninetest → final_analysis_output → resume → final_analysis_output → taggings
- **企业流程**: company_identity/jobpost → taggings

## 核心设计理念

### 1. 模块自治注册
```python
# 模块通过register_function完全自主控制注册过程
def register_module(self, module_info: Dict[str, Any]) -> None:
    # 中枢被动接收，模块自主注册
    register_func(self, module_name, module_info)
```

### 2. 意图驱动路由
```python
# 基于注册信息的意图匹配
handler_func = self.registry.get_handler_for_intent(intent)
if handler_func:
    result = await handler_func(request_body)
```

### 3. 编排与路由分离
```python
# 只有明确请求编排的intent才进行编排
if intent == "orchestrate_next_module":
    next_module = self.get_hardcoded_next_module(current_module)
```

## 数据流向

```
前端请求 → orchestrate.run() → router.route()
                                    ↓
intent解析 → 注册中心查询 → 模块处理器执行
                                    ↓
结果返回 ← 响应封装 ← 异步等待完成
```

## 关键特性

### 1. 链式检查机制
- 用户从mbti_step1触发流程
- 每个模块step1检查用户完成状态
- 已完成则自动请求下一个模块
- 防循环：完成用户标记管理

### 2. 防循环保护
- 完成全流程用户打上`jobfindingregistrycomplate`标记
- mbti_step1检测标记直接拒绝服务
- 避免无限循环和重复处理

### 3. 异步嵌套编排
- 支持公司层面和职位层面的分离管理
- 一个公司可发布多个职位
- 每个职位独立处理，支持并发

## 使用示例

### 注册模块
```python
# 模块自主注册示例
module_info = {
    'name': 'mbti',
    'register_function': mbti_register_function,
    'orchestrate_info': {
        'supported_intents': ['mbti_step1', 'mbti_step2', ...]
    }
}
registry.register_module(module_info)
```

### 意图路由
```python
# 意图处理示例
request = {
    "intent": "mbti_step1",
    "user_id": "user123",
    "data": {...}
}
result = await orchestrate.run(request)
```

### 流程编排
```python
# 编排下一个模块示例
request = {
    "intent": "orchestrate_next_module",
    "current_module": "mbti"
}
result = await orchestrate.run(request)
# 返回: {"status": "next_module_found", "next_module": "ninetest"}
```

## 业务流程图

```
用户点击开始
      ↓
  mbti_step1 检查
      ↓
  已完成? → 是 → 请求编排下一个模块
      ↓          ↓
      否        ninetest_step1 检查
               ↓
           已完成? → 是 → 请求编排下一个模块
               ↓          ↓
               否        final_analysis_output_step1 检查
                        ↓
                    已完成? → 是 → 请求编排下一个模块
                        ↓          ↓
                        否        resume_step1 检查
                                 ↓
                             已完成? → 是 → 请求编排下一个模块
                                 ↓          ↓
                                 否        final_analysis_output_step1 检查
                                          ↓
                                       已完成? → 是 → 请求编排下一个模块
                                       ↓          ↓
                                       否        taggings_step1 检查
                                                ↓
                                            已完成? → 是 → 流程结束
                                            ↓          ↓
                                            否        处理业务逻辑
```

## 技术特点

- **模块化设计**: 高内聚、低耦合的模块架构
- **异步支持**: 基于asyncio的异步处理能力
- **类型安全**: 完整的类型注解和类型检查
- **错误处理**: 完善的异常处理和错误响应机制
- **可扩展性**: 支持新模块的动态注册和集成

## 依赖关系

- 内部依赖: registry_center, router
- 外部依赖: typing, asyncio, copy
- 模块依赖: 通过注册中心动态管理

## 总结

orchestrate 通过精心的架构设计，实现了模块自治、意图驱动和流程编排的完美平衡，为 Career Bot 系统提供了灵活、可扩展和高效的业务处理能力。