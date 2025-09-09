# Auth模块 - 面向AI的测试驱动文档

本文档基于代码审计分析，为后续自动化测试脚本生成提供精确的技术规格说明。严格以可执行代码路径为准，拒绝臆测。

## 1. 模块概览（Module Overview）

### 目标与职责

Auth模块采用**流程驱动架构**，提供完整的用户认证体系，核心能力清单：

#### 1.1 用户注册流程 (`user_registration`)
- **入口**: 意图 `register_step1` → `register_step2` → `register_step3`
- **输入**: `email`, `test_user` → `code` → `password` 
- **输出**: `UserResponse`(含access_token, refresh_token)
- **副作用**: 创建 `user_profiles` 和 `user_status` 记录，发送验证码邮件

#### 1.2 Google OAuth认证流程 (`oauth_google_authentication`)
- **入口**: `oauth_google_step1` → `oauth_google_step2`
- **输入**: `state` → `code`, `state`, `expected_state`
- **输出**: `UserResponse`(含OAuth用户信息和token)
- **副作用**: OAuth第三方认证、可能创建新用户或绑定现有邮箱

#### 1.3 Facebook OAuth认证流程 (`oauth_facebook_authentication`) 
- **入口**: `oauth_facebook_step1` → `oauth_facebook_step2`
- **输入**: `state` → `code`, `state`, `expected_state`
- **输出**: `UserResponse`(含OAuth用户信息和token)
- **副作用**: OAuth第三方认证、可能创建新用户或绑定现有邮箱

#### 1.4 密码重置流程 (`password_reset`)
- **入口**: `reset_step1` → `reset_step2`
- **输入**: `email`, `test_user` → `email`, `code`, `new_password`
- **输出**: 密码更新成功确认
- **副作用**: 更新 `user_status` 中的密码哈希，发送重置验证码邮件

#### 1.5 受保护功能
- **Token验证与刷新**: JWT令牌生命周期管理
- **用户信息获取**: 基于认证的用户资料访问
- **用户设置更新**: 认证用户的配置修改

### 上下游关系

Auth模块完全采用**中枢/Dispatcher/Intent驱动架构**：

#### 调用路径
```
外部请求 → hub/router.py:hub_entry(intent, payload) 
         → hub/router.py:Router.route(intent, payload)
         → flow_registry.get_step(intent).handler_func
         → applications/auth/intent_handlers.py:handle_auth_*
```

#### 入参结构
- **标准载荷**: `Dict[str, Any]` 包含业务参数
- **认证载荷**: 可选 `Authorization` 头部或 `access_token` 字段
- **流程上下文**: 自动注入 `_flow_context`, `_recovery_context`

#### 出参结构
```python
{
    "success": bool,
    "intent": str,
    "module": "auth", 
    "result": Dict[str, Any],  # 业务数据
    "stateful": bool,
    "flow_info": {
        "flow_id": str,
        "current_step": str,
        "progress": Dict
    }
}
```

#### 错误返回格式
**异常驱动**: 所有错误通过异常抛出，由hub层转换为HTTP响应
- `InvalidIntentError`: intent未注册 → 400
- `InvalidCredentialsError`: 凭证错误 → 401  
- `EmailAlreadyRegisteredError`: 邮箱已注册 → 409
- `RuntimeError`: 执行失败 → 500

## 2. 接口与意图（APIs & Intents）

### 路由/意图一览表

| Intent | 触发方式 | 请求字段 | 响应字段 | 鉴权需求 | 错误类型 |
|--------|---------|---------|----------|---------|---------|
| `auth_send_verification` | 流程步骤 | `email`, `test_user`? | `success`, `message` | 无 | `EMAIL_ALREADY_REGISTERED` |
| `auth_verify_code` | 流程步骤 | `email`, `code` | `success`, `message`, `user_exists`, `is_oauth_user` | 无 | `VERIFY_CODE_ERROR` |
| `auth_set_password` | 流程步骤 | `email`, `password` | `success`, `message`, `user_id`? | 无 | `SET_PASSWORD_ERROR` |
| `auth_login` | 直接调用 | `email`, `password` | `UserResponse` | 无 | `INVALID_CREDENTIALS` |
| `auth_oauth_google_url` | 流程步骤 | `state`? | `auth_url`, `provider` | 无 | `OAUTH_URL_GENERATION_ERROR` |
| `auth_oauth_google_callback` | 流程步骤 | `code`, `state`, `expected_state` | `UserResponse` | 无 | `OAUTH_VALIDATION_ERROR`, `OAUTH_CALLBACK_ERROR` |
| `auth_oauth_facebook_url` | 流程步骤 | `state`? | `auth_url`, `provider` | 无 | `OAUTH_URL_GENERATION_ERROR` |
| `auth_oauth_facebook_callback` | 流程步骤 | `code`, `state`, `expected_state` | `UserResponse` | 无 | `OAUTH_VALIDATION_ERROR`, `OAUTH_CALLBACK_ERROR` |
| `auth_forgot_password` | 流程步骤 | `email`, `test_user`? | `success`, `message` | 无 | `SEND_RESET_CODE_ERROR` |
| `auth_reset_password` | 流程步骤 | `email`, `code`, `new_password` | `success`, `message` | 无 | `RESET_PASSWORD_FAILED` |
| `auth_get_profile` | 直接调用 | 认证信息 | 用户资料 | 必须 | `AUTHENTICATION_REQUIRED` |
| `auth_update_settings` | 直接调用 | 认证信息 + 设置 | 更新结果 | 必须 | `AUTHENTICATION_REQUIRED` |
| `auth_refresh_token` | 直接调用 | `refresh_token` | 新token对 | 无 | `TOKEN_REFRESH_ERROR` |
| `auth_logout` | 直接调用 | 认证信息 | 登出确认 | 必须 | `AUTHENTICATION_REQUIRED` |

### 前置/后置条件

#### 邮箱验证注册流程
- **前置**: 邮箱格式验证，重复邮箱检查（OAuth用户例外）
- **流程**: `register_step1` → `register_step2` → `register_step3`
- **后置**: 创建完整用户记录，生成token对

#### OAuth流程
- **前置**: 第三方OAuth配置有效
- **邮箱并轨策略**: 
  - 若OAuth邮箱已存在且为完整用户 → 直接登录
  - 若OAuth邮箱已存在且为纯OAuth用户 → 绑定登录
  - 若OAuth邮箱不存在 → 创建新用户
- **后置**: 更新 `user_status` 中的 `oauth_*_id` 字段

#### 密码重置
- **前置**: 用户必须存在
- **验证码策略**: 独立于注册验证码，有效期10分钟
- **后置**: 密码哈希更新，旧值自动归档

#### Token管理
- **访问令牌**: 15分钟有效期，包含 `user_id`, `username`, `type="access_token"`
- **刷新令牌**: 7天有效期，包含 `user_id`, `username`, `type="refresh_token"`
- **刷新机制**: 验证刷新令牌 → 生成新token对

## 3. 数据模型与存储（Data Models & Storage）

### 涉及的数据库与集合

#### MongoDB集合设计
- **数据库**: 由 `utilities.mongodb_connector.DatabaseOperations` 管理
- **集合分离策略**: 静态画像与动态状态分离存储

#### 3.1 user_profiles（用户静态画像）
```javascript
{
  "user_id": "uuid4-string",        // 主键，UUID4格式
  "username": "user@example.com",   // 邮箱作为用户名
  "email": "user@example.com"       // 邮箱地址
}
```
- **主索引**: `user_id` (唯一)
- **业务索引**: `email` (唯一), `username` (唯一)
- **用途**: 存储不变的用户身份信息

#### 3.2 user_status（用户动态状态）
```javascript
{
  "user_id": "uuid4-string",                    // 关联user_profiles
  "hashed_password": "bcrypt-hash",             // bcrypt加密密码
  "oauth_google_id": "google-user-id",          // 可选，Google OAuth绑定
  "oauth_facebook_id": "facebook-user-id"       // 可选，Facebook OAuth绑定
}
```
- **主索引**: `user_id` (唯一)
- **用途**: 存储会变化的认证凭据和OAuth绑定

#### 3.3 user_archive（历史状态归档）
- **用途**: 自动归档 `user_status` 的字段变更历史
- **触发**: `DatabaseOperations.update()` 自动归档旧值
- **字段**: 原字段名、旧值、新值、变更时间戳、操作类型

### 写入/更新策略

#### 用户创建策略
1. **原子性**: 同时写入 `user_profiles` 和 `user_status`
2. **失败回滚**: 任一写入失败则整体创建失败
3. **重复检查**: 基于邮箱的 `check_user_exists()` 前置验证

#### 状态更新策略（密码、OAuth绑定）
1. **先归档后更新**: `DatabaseOperations.update()` 自动执行
   - 读取旧值 → 写入 `user_archive` → 更新 `user_status`
2. **幂等性**: 相同值更新不产生归档记录
3. **事务性**: **【TODO】** 验证MongoDB的事务保证机制

#### 异常回退策略
- **数据库异常**: 抛出 `ValueError` 或 `RuntimeError`
- **约束违反**: 依赖MongoDB唯一索引保证
- **并发写入**: **【TODO】** 验证并发控制机制

### 示例文档（脱敏）

#### 完整注册用户
```javascript
// user_profiles
{
  "user_id": "12345678-1234-1234-1234-123456789abc",
  "username": "test@example.com", 
  "email": "test@example.com"
}

// user_status  
{
  "user_id": "12345678-1234-1234-1234-123456789abc",
  "hashed_password": "$2b$12$abcdefg..."
}
```

#### OAuth用户（未设置密码）
```javascript
// user_profiles
{
  "user_id": "87654321-4321-4321-4321-cba987654321",
  "username": "oauth@gmail.com",
  "email": "oauth@gmail.com" 
}

// user_status
{
  "user_id": "87654321-4321-4321-4321-cba987654321", 
  "oauth_google_id": "google-oauth-123456789"
  // 注意：无hashed_password字段
}
```

#### 混合用户（OAuth + 密码）
```javascript  
// user_status
{
  "user_id": "11111111-2222-3333-4444-555555555555",
  "hashed_password": "$2b$12$xyz123...",
  "oauth_google_id": "google-oauth-987654321"
}
```

## 4. 配置与密钥（Configuration）

### 环境变量与默认值

| 环境变量 | 默认值 | 用途 | 失配影响 |
|---------|-------|------|---------|
| `JWT_SECRET_KEY` | `'your-secret-key-here'` | JWT令牌签名密钥 | 令牌验证失败 |
| **【TODO】验证以下配置** |
| `GOOGLE_OAUTH_CLIENT_ID` | - | Google OAuth客户端ID | OAuth流程失败 |
| `GOOGLE_OAUTH_CLIENT_SECRET` | - | Google OAuth客户端密钥 | OAuth认证失败 |
| `FACEBOOK_OAUTH_CLIENT_ID` | - | Facebook OAuth客户端ID | OAuth流程失败 |
| `FACEBOOK_OAUTH_CLIENT_SECRET` | - | Facebook OAuth客户端密钥 | OAuth认证失败 |
| `SMTP_*` | - | 邮件发送配置 | 验证码无法发送 |

### 依赖的第三方服务

#### 邮件服务
- **模块**: `utilities.mail.send_email`
- **用途**: 发送验证码和密码重置邮件
- **失败降级**: 返回 `False`，不抛出异常

#### OAuth提供商
- **Google OAuth**: **【TODO】** 分析 `oauth_google.py` 具体配置
- **Facebook OAuth**: **【TODO】** 分析 `oauth_facebook.py` 具体配置
- **Redirect URI**: **【TODO】** 确认回调URL配置

#### 数据库连接
- **MongoDB**: 通过 `utilities.mongodb_connector` 
- **连接失败**: 直接抛出异常，无降级机制

## 5. 安全与合规（Security）

### 密码策略
- **哈希算法**: bcrypt，自动盐值生成
- **复杂度要求**: 最少8个字符（`validators.py:validate_password`）
- **存储位置**: `user_status.hashed_password`
- **历史归档**: 密码变更自动归档至 `user_archive`

### Token安全
- **访问令牌**: 15分钟有效期，HS256算法
- **刷新令牌**: 7天有效期，HS256算法  
- **令牌结构**: 
  ```json
  {
    "user_id": "uuid",
    "username": "email", 
    "exp": timestamp,
    "iat": timestamp,
    "type": "access_token|refresh_token"
  }
  ```
- **吊销机制**: **【TODO】** 确认令牌黑名单机制

### 验证码策略
- **注册验证码**: 6位数字，5分钟有效期，内存存储
- **重置验证码**: 6位数字，10分钟有效期，独立内存存储
- **测试模式**: `test_user=true` 时固定为 "123456"
- **防暴力**: **【TODO】** 验证频率限制机制

### 重放与并发防护
- **验证码一次性**: 验证成功后立即从缓存删除
- **OAuth state防护**: **【TODO】** 分析state参数防CSRF机制
- **并发注册**: 依赖数据库唯一约束，**【TODO】** 验证竞争条件处理

### 敏感信息处理
- **日志打码**: **【TODO】** 验证密码、token的日志脱敏
- **审计轨迹**: **【TODO】** 确认操作人、IP、UA记录机制

## 6. 日志与可观测性（Logging & Observability）

### 关键日志点（推断基于代码结构）

#### 流程注册阶段
```python
# flow_definitions.py 中可见
print("=== 开始注册Auth模块认证流程 ===")  # INFO级别
print("✓ 用户注册流程注册成功: user_registration")  # INFO级别
print("✗ 用户注册流程注册失败: user_registration")  # ERROR级别
```

#### 请求处理阶段
```python  
# hub/router.py 流程调度
# 【TODO】加入以下日志断点
logger.info(f"Intent received: {intent}, user_id: {user_id}")
logger.info(f"Step execution started: {intent}")
logger.info(f"Step execution completed: {intent}, success: {result.get('success')}")
logger.error(f"Step execution failed: {intent}, error: {str(e)}")
```

#### 数据库操作阶段
```python
# repository.py 数据库操作
# 【TODO】加入以下日志断点  
logger.info(f"User created: user_id={user_id}, email=***")
logger.info(f"User status updated: user_id={user_id}, fields={updated_fields.keys()}")
logger.error(f"Database operation failed: operation={operation}, error={str(e)}")
```

#### 外部服务调用阶段
```python
# email_verification.py 邮件发送
# 【TODO】加入以下日志断点
logger.info(f"Verification code sent: email=***, success={send_result}")
logger.error(f"Email sending failed: email=***, error={str(e)}")
```

### 日志字段清单（建议结构）

```json
{
  "timestamp": "2024-12-19T10:30:00+08:00",
  "level": "INFO|WARN|ERROR", 
  "module": "auth",
  "intent": "auth_register",
  "flow_id": "user_registration",
  "step_id": "register_step1", 
  "user_id": "uuid-or-null",
  "email": "***@***.com",  // 脱敏
  "ip_address": "client-ip",
  "user_agent": "client-ua",
  "execution_time_ms": 150,
  "success": true,
  "error_type": "INVALID_INPUT|null",
  "message": "详细描述"
}
```

### 指标收集（建议）

**【TODO】** 验证是否已实现以下指标收集：
- **计数器**: 各intent调用次数、成功/失败分布
- **时延**: 各步骤执行时间分布（P50/P90/P99）
- **业务指标**: 注册成功率、OAuth成功率、密码重置成功率
- **错误分布**: 按错误类型统计失败原因

## 7. 状态机与用户旅程（State Machine & Flows）

### 用户注册流程状态机

```
[未注册] --auth_send_verification--> [验证码已发送]
    |                                        |
    |                                auth_verify_code
    |                                        |
    |                                   [邮箱已验证]
    |                                        |
    |                                auth_set_password  
    |                                        |
    +--test_user=true shortcut---------> [注册完成]
```

**状态节点**:
- `未注册`: 新用户，邮箱不存在于 `user_profiles`
- `验证码已发送`: 验证码存在于 `_verification_codes` 缓存
- `邮箱已验证`: 验证码验证通过，缓存已清除
- `注册完成`: `user_profiles` 和 `user_status` 记录已创建

**事件/条件**:
- `auth_send_verification`: 触发验证码发送
- `auth_verify_code`: 验证用户输入的验证码  
- `auth_set_password`: 设置密码完成注册
- `test_user=true shortcut`: 测试模式直接跳转

**守卫条件**:
- 邮箱格式验证 (`validate_email`)
- 重复邮箱检查 (`check_user_exists`, OAuth用户例外)
- 密码复杂度验证 (`validate_password`)

### OAuth认证流程状态机

```
[未认证] --oauth_*_url--> [重定向到第三方]
                                |
                          第三方授权完成
                                |
                        --oauth_*_callback--> [OAuth认证成功]
                                |
                         检查邮箱是否存在
                         /              \
                    已存在且完整        已存在OAuth用户     不存在
                        |                    |               |
                   [直接登录]           [绑定登录]        [创建新用户]
```

**动作/副作用**:
- `oauth_*_url`: 生成第三方授权URL
- `oauth_*_callback`: 验证授权码，获取用户信息
- `直接登录`: 返回已有用户的token
- `绑定登录`: 更新 `oauth_*_id` 字段
- `创建新用户`: 同时创建 `user_profiles` 和 `user_status`

### 密码重置流程状态机

```
[忘记密码] --auth_forgot_password--> [重置验证码已发送]
                                            |
                                    auth_reset_password
                                            |
                                      [密码已重置]
```

**状态持久化**:
- `重置验证码已发送`: 验证码存在于 `_reset_codes` 缓存（10分钟TTL）
- `密码已重置`: `user_status.hashed_password` 已更新，旧值已归档

### 并发/重复提交处理

#### 验证码并发防护
- **暴力尝试**: **【TODO】** 验证同一邮箱频繁申请验证码的限制机制
- **重复验证**: 验证成功后立即清除缓存，防止重复使用

#### 注册并发防护  
- **重复注册**: 依赖 `user_profiles.email` 唯一索引
- **竞争条件**: **【TODO】** 验证 `check_user_exists` → `create_user` 之间的竞争条件

#### OAuth并发防护
- **state参数**: **【TODO】** 验证OAuth回调的state防重放机制
- **重复回调**: **【TODO】** 验证同一授权码的重复使用防护

## 8. 测试矩阵（Test Matrix for Script Generation）

### 8.1 用户注册流程测试

#### 正向用例
| 用例ID | 前置条件 | 输入 | 期望HTTP响应 | 期望DB变更 | 期望日志 |
|--------|---------|------|------------|-----------|---------|
| REG-001 | 新邮箱 | `auth_send_verification: {email: "new@test.com", test_user: true}` | `{success: true, message: "测试验证码已发送..."}` | 验证码缓存: `_verification_codes["new@test.com"] = ("123456", timestamp)` | INFO: 验证码发送成功 |
| REG-002 | 有验证码 | `auth_verify_code: {email: "new@test.com", code: "123456"}` | `{success: true, user_exists: false, is_oauth_user: false}` | 清除验证码缓存 | INFO: 验证码验证成功 |  
| REG-003 | 已验证邮箱 | `auth_set_password: {email: "new@test.com", password: "password123"}` | `{success: true, user_id: "uuid"}` | 创建 user_profiles + user_status 记录 | INFO: 用户创建成功 |

#### 边界与对抗用例
| 用例ID | 前置条件 | 输入 | 期望错误类型 | 期望DB状态 | 验证点 |
|--------|---------|------|------------|-----------|---------|
| REG-E01 | 已注册完整用户 | `auth_send_verification: {email: "exists@test.com"}` | `EMAIL_ALREADY_REGISTERED` | 无变更 | 严格禁止重复注册 |
| REG-E02 | OAuth用户 | `auth_send_verification: {email: "oauth@test.com"}` | 成功 | 允许发送验证码 | OAuth用户可补设密码 |
| REG-E03 | 无效邮箱 | `auth_send_verification: {email: "invalid-email"}` | `INVALID_INPUT` | 无变更 | 邮箱格式验证 |
| REG-E04 | 弱密码 | `auth_set_password: {password: "123"}` | `INVALID_INPUT` | 无变更 | 密码长度 >= 8 |
| REG-E05 | 过期验证码 | 等待6分钟后 `auth_verify_code` | `VERIFY_CODE_ERROR` | 清除过期缓存 | TTL=5分钟 |
| REG-E06 | 错误验证码 | `auth_verify_code: {code: "000000"}` | `VERIFY_CODE_ERROR` | 保留正确验证码 | 验证码匹配检查 |

### 8.2 OAuth认证流程测试

#### Google OAuth正向用例
| 用例ID | 前置条件 | 输入 | 期望响应 | 期望DB变更 |
|--------|---------|------|---------|-----------|
| OAG-001 | 新用户 | `auth_oauth_google_url: {state: "random123"}` | `{auth_url: "https://accounts.google.com/...", provider: "google"}` | 无变更 |
| OAG-002 | 有授权码 | `auth_oauth_google_callback: {code: "auth_code", state: "random123", expected_state: "random123"}` | `UserResponse` | 创建新用户 + oauth_google_id |

#### Facebook OAuth边界用例  
| 用例ID | 输入 | 期望错误类型 | 验证点 |
|--------|------|------------|---------|
| OAF-E01 | `auth_oauth_facebook_callback: {code: "invalid"}` | `OAUTH_VALIDATION_ERROR` | 授权码验证失败 |
| OAF-E02 | `auth_oauth_facebook_callback: {state: "wrong"}` | `OAUTH_VALIDATION_ERROR` | state参数不匹配 |

#### OAuth邮箱并轨策略测试
| 用例ID | 前置条件 | 期望行为 | 期望DB变更 | 验证点 |
|--------|---------|---------|-----------|---------|
| OAM-001 | OAuth邮箱 = 已注册完整用户 | 直接登录 | 无变更 | 返回现有用户token |
| OAM-002 | OAuth邮箱 = 纯OAuth用户 | 绑定登录 | 更新 oauth_*_id | 多OAuth绑定 |
| OAM-003 | OAuth邮箱 = 不存在 | 创建新用户 | 新建记录含 oauth_*_id | 自动注册 |

### 8.3 密码重置流程测试

#### 正向用例
| 用例ID | 前置条件 | 输入 | 期望响应 | 期望DB变更 |
|--------|---------|------|---------|-----------|
| RST-001 | 存在用户 | `auth_forgot_password: {email: "user@test.com", test_user: true}` | `{success: true, message: "测试重置验证码..."}` | 重置码缓存 |
| RST-002 | 有重置码 | `auth_reset_password: {email: "user@test.com", code: "123456", new_password: "newpass123"}` | `{success: true}` | 更新 hashed_password + 归档旧值 |

#### 边界用例
| 用例ID | 输入 | 期望错误 | 验证点 |
|--------|------|---------|---------|
| RST-E01 | 不存在的邮箱 | `auth_forgot_password: {email: "none@test.com"}` | 返回false | 用户存在性检查 |
| RST-E02 | 过期重置码(11分钟后) | `auth_reset_password` | `RESET_PASSWORD_FAILED` | TTL=10分钟 |

### 8.4 Token管理测试

#### Token生成与验证
| 用例ID | 输入 | 期望行为 | 验证点 |
|--------|------|---------|---------|
| TOK-001 | 生成access_token | 15分钟后自动过期 | JWT exp字段 |
| TOK-002 | 生成refresh_token | 7天后自动过期 | JWT exp字段 |
| TOK-003 | 使用refresh_token换取新access_token | 返回新token对 | 刷新机制 |

#### Token安全测试
| 用例ID | 输入 | 期望错误 | 验证点 |
|--------|------|---------|---------|
| TOK-E01 | 使用access_token作为refresh_token | `TOKEN_REFRESH_ERROR` | type字段验证 |
| TOK-E02 | 篡改JWT签名 | `AUTHENTICATION_REQUIRED` | HS256签名验证 |
| TOK-E03 | 过期access_token访问受保护接口 | `AUTHENTICATION_REQUIRED` | exp字段检查 |

### 8.5 并发与边界测试

#### 并发注册测试
```python
# 伪代码：并发测试用例
async def test_concurrent_registration():
    """并发相同邮箱注册，验证唯一约束"""
    tasks = [
        auth_send_verification("same@test.com") 
        for _ in range(10)
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    # 验证：只有1个成功，9个EMAIL_ALREADY_REGISTERED
```

#### 验证码暴力测试
```python
async def test_verification_code_brute_force():
    """验证码暴力破解测试"""
    # 发送验证码
    await auth_send_verification("target@test.com")
    
    # 尝试1000次错误验证码 
    for i in range(1000):
        result = await auth_verify_code("target@test.com", f"{i:06d}")
        assert result["success"] == False
    
    # 验证正确验证码仍然有效
    correct_result = await auth_verify_code("target@test.com", "123456") 
    assert correct_result["success"] == True
```

## 9. 夹具与模拟（Fixtures & Mocks）

### 测试夹具（最小数据集）

#### 用户数据夹具
```python
@pytest.fixture
def test_users():
    return {
        "complete_user": {
            "user_id": "11111111-1111-1111-1111-111111111111",
            "email": "complete@test.com",
            "username": "complete@test.com", 
            "hashed_password": "$2b$12$test.hash.value"
        },
        "oauth_only_user": {
            "user_id": "22222222-2222-2222-2222-222222222222", 
            "email": "oauth@test.com",
            "username": "oauth@test.com",
            "oauth_google_id": "google-123456789"
            # 注意：无hashed_password
        },
        "mixed_user": {
            "user_id": "33333333-3333-3333-3333-333333333333",
            "email": "mixed@test.com", 
            "username": "mixed@test.com",
            "hashed_password": "$2b$12$mixed.hash.value",
            "oauth_facebook_id": "facebook-987654321"
        }
    }
```

#### 验证码缓存夹具
```python
@pytest.fixture 
def verification_codes_cache():
    """模拟验证码缓存状态"""
    return {
        "valid@test.com": ("123456", time.time()),           # 有效验证码
        "expired@test.com": ("999999", time.time() - 400),   # 过期验证码(>5分钟)
    }
```

#### 数据库初始状态夹具
```python
@pytest.fixture
async def clean_database():
    """清空数据库并设置初始状态"""
    db = DatabaseOperations()
    
    # 清空相关集合
    await db.delete_many("user_profiles", {})
    await db.delete_many("user_status", {})  
    await db.delete_many("user_archive", {})
    
    yield db
    
    # 测试后清理
    await db.delete_many("user_profiles", {})
    await db.delete_many("user_status", {})
    await db.delete_many("user_archive", {})
```

### 外部依赖Mock策略

#### 邮件服务Mock
```python
@pytest.fixture
def mock_email_service(monkeypatch):
    """Mock邮件发送服务"""
    sent_emails = []
    
    async def mock_send_email(to, subject, body, content_type="plain"):
        sent_emails.append({
            "to": to,
            "subject": subject, 
            "body": body,
            "content_type": content_type,
            "timestamp": time.time()
        })
        return True  # 总是返回发送成功
    
    monkeypatch.setattr("utilities.mail.send_email", mock_send_email)
    return sent_emails
```

#### OAuth服务Mock
```python  
@pytest.fixture
def mock_google_oauth(monkeypatch):
    """Mock Google OAuth服务"""
    oauth_responses = {}
    
    def mock_google_auth_url(state=None):
        return f"https://accounts.google.com/oauth/authorize?state={state}"
    
    def mock_google_callback(code, state, expected_state): 
        if code == "valid_google_code":
            return {
                "user_id": "google-test-user-123",
                "email": "google@test.com",
                "access_token": "mock-google-token",
                "refresh_token": "mock-google-refresh"
            }
        else:
            raise ValueError("Invalid Google authorization code")
    
    monkeypatch.setattr("applications.auth.oauth_google.get_google_auth_url", mock_google_auth_url)
    monkeypatch.setattr("applications.auth.oauth_google.login_with_google", mock_google_callback)
    return oauth_responses
```

#### 时间控制Mock
```python
@pytest.fixture
def mock_time():
    """可控制的时间Mock，用于验证码过期测试"""
    base_time = time.time()
    current_offset = 0
    
    def mock_time_func():
        return base_time + current_offset
        
    def advance_time(seconds):
        nonlocal current_offset
        current_offset += seconds
    
    with patch('time.time', mock_time_func):
        mock_time_func.advance = advance_time
        yield mock_time_func
```

### 可复用构造器

#### 用户构造器
```python
class UserFactory:
    """用户数据构造器"""
    
    @staticmethod
    async def create_complete_user(email=None, password="testpass123"):
        """创建完整注册用户"""
        email = email or f"user{uuid.uuid4().hex[:8]}@test.com"
        
        # 模拟完整注册流程
        await auth_send_verification({"email": email, "test_user": True})
        await auth_verify_code({"email": email, "code": "123456"})
        result = await auth_set_password({"email": email, "password": password})
        
        return result["user_id"]
    
    @staticmethod 
    async def create_oauth_user(provider="google", email=None):
        """创建纯OAuth用户"""
        email = email or f"oauth{uuid.uuid4().hex[:8]}@test.com"
        
        # 模拟OAuth回调
        oauth_callback = {
            "code": "valid_oauth_code",
            "state": "test_state", 
            "expected_state": "test_state"
        }
        
        if provider == "google":
            result = await auth_oauth_google_callback(oauth_callback)
        elif provider == "facebook":
            result = await auth_oauth_facebook_callback(oauth_callback)
            
        return result["user_id"]
```

#### 流程状态构造器
```python
class FlowStateFactory:
    """流程状态构造器"""
    
    @staticmethod
    async def setup_registration_mid_flow(email):
        """设置注册流程中断状态"""
        # 发送验证码但不验证
        await auth_send_verification({"email": email, "test_user": True})
        return {"email": email, "expected_code": "123456"}
    
    @staticmethod
    async def setup_reset_mid_flow(email):
        """设置密码重置流程中断状态"""  
        await auth_forgot_password({"email": email, "test_user": True})
        return {"email": email, "expected_reset_code": "123456"}
```

## 10. 生成测试脚本的建议（Script-Generation Hints）

### 建议脚本技术栈

**主框架**: `pytest + httpx + asyncio`
- **理由**: 代码库大量使用 `async/await`，需要异步测试支持
- **HTTP客户端**: `httpx` 支持异步HTTP请求
- **断言库**: pytest内置断言 + `pytest-asyncio`

### 目录组织建议
```
tests/
├── auth/
│   ├── __init__.py
│   ├── conftest.py                 # 通用夹具
│   ├── fixtures/
│   │   ├── users.py               # 用户数据夹具
│   │   ├── mocks.py               # 外部依赖Mock
│   │   └── database.py            # 数据库操作夹具
│   ├── unit/
│   │   ├── test_validators.py     # 输入验证单元测试
│   │   ├── test_hashing.py        # 密码哈希单元测试
│   │   ├── test_tokens.py         # JWT令牌单元测试
│   │   └── test_repository.py     # 数据库操作单元测试
│   ├── integration/
│   │   ├── test_registration_flow.py    # 注册流程集成测试  
│   │   ├── test_oauth_flow.py          # OAuth流程集成测试
│   │   ├── test_password_reset_flow.py  # 重置流程集成测试
│   │   └── test_protected_routes.py     # 认证接口集成测试
│   ├── e2e/
│   │   ├── test_complete_user_journey.py # 端到端用户旅程
│   │   └── test_cross_flow_scenarios.py  # 跨流程场景测试
│   └── stress/
│       ├── test_concurrent_registration.py # 并发注册测试
│       └── test_verification_brute_force.py # 验证码暴力测试
```

### 命名规范
- **测试类**: `TestAuthRegistrationFlow`, `TestOAuthIntegration`
- **测试方法**: `test_{功能}_{场景}_{期望结果}`
  - `test_auth_send_verification_new_email_should_succeed`
  - `test_auth_verify_code_expired_code_should_fail`  
  - `test_oauth_google_callback_invalid_state_should_raise_error`

### 基线启动/清理流程

#### pytest配置 (pytest.ini)
```ini
[tool:pytest]
asyncio_mode = auto
markers = 
    auth: auth module tests
    e2e: end-to-end tests
    slow: tests that take > 5 seconds
    integration: integration tests requiring external services
```

#### conftest.py基线设置
```python
import pytest
import asyncio
from applications.auth import initialize_module, cleanup_module
from utilities.mongodb_connector import DatabaseOperations

@pytest.fixture(scope="session")  
async def event_loop():
    """提供会话级别的事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
async def setup_auth_module():
    """会话级别的auth模块初始化"""
    # 初始化auth模块
    await initialize_module({"test_mode": True})
    
    yield
    
    # 清理auth模块
    await cleanup_module()

@pytest.fixture(autouse=True)
async def clean_test_data():
    """每个测试前后清理测试数据"""
    db = DatabaseOperations()
    test_emails = ["test@", "@test.com", "oauth@", "complete@"]
    
    # 清理测试用户数据
    for email_pattern in test_emails:
        await db.delete_many("user_profiles", {"email": {"$regex": email_pattern}})
        await db.delete_many("user_status", {})  # 通过user_id关联清理
    
    yield
    
    # 测试后清理
    for email_pattern in test_emails:
        await db.delete_many("user_profiles", {"email": {"$regex": email_pattern}})
        await db.delete_many("user_status", {})
```

### 覆盖率目标

#### 功能覆盖率（100%）
- ✅ 所有已实现的intent处理器
- ✅ 所有数据模型验证逻辑
- ✅ 所有异常处理分支

#### 分支覆盖率（≥90%）
- ✅ 正向路径 + 主要错误路径
- ✅ OAuth用户 vs 完整用户分支
- ✅ test_user vs 正常用户分支

#### 场景覆盖率
- **基础场景**: 每个流程的happy path
- **边界场景**: 输入验证、过期时间、重复操作
- **并发场景**: 竞争条件、重复提交
- **故障场景**: 外部服务失败、数据库异常































## 11. 未定义与待确认（Open Points）

### 【TODO】配置与环境变量确认

**验证方法**: 搜索OAuth配置文件和环境变量引用
```bash
# 搜索OAuth配置
find . -name "*.py" -exec grep -l "GOOGLE_.*CLIENT" {} \;
find . -name "*.py" -exec grep -l "FACEBOOK_.*CLIENT" {} \;

# 搜索邮件配置
find . -name "*.py" -exec grep -l "SMTP_" {} \;
grep -r "mail.*config" utilities/mail/
```

**关键待确认**:
- `GOOGLE_OAUTH_CLIENT_ID` 和 `GOOGLE_OAUTH_CLIENT_SECRET` 的具体使用
- `FACEBOOK_OAUTH_CLIENT_ID` 和 `FACEBOOK_OAUTH_CLIENT_SECRET` 的具体使用  
- OAuth回调URL的配置方式
- SMTP邮件服务器配置项

### 【TODO】OAuth具体实现分析

**验证方法**: 详细分析OAuth相关文件
```bash
# 分析OAuth实现
cat applications/auth/oauth_google.py | head -50
cat applications/auth/oauth_facebook.py | head -50
cat applications/auth/oauth_utils.py | head -50

# 搜索OAuth状态管理
grep -r "state" applications/auth/oauth_*.py
grep -r "CSRF\|csrf" applications/auth/
```

**待确认机制**:
- OAuth state参数的生成和验证机制
- 授权码换取access_token的具体流程
- OAuth用户信息获取和解析逻辑
- OAuth错误处理和重试机制

### 【TODO】数据库事务和并发控制

**验证方法**: 分析数据库操作的事务性
```bash
# 检查事务使用
grep -r "transaction\|Transaction" utilities/mongodb_connector.py
grep -r "session\|Session" utilities/mongodb_connector.py

# 检查并发控制
grep -r "lock\|Lock\|atomic" applications/auth/
```

**关键验证点**:
- `create_user()` 双表写入的事务保证
- `check_user_exists()` → `create_user()` 竞争条件处理
- `user_status` 更新的原子性保证
- 高并发场景下的数据一致性

### 【TODO】令牌黑名单和吊销机制

**验证方法**: 搜索token管理相关代码
```bash
# 搜索令牌吊销
grep -r "revoke\|blacklist\|invalidate" applications/auth/
grep -r "logout" applications/auth/ | grep -i "token"

# 分析protected_routes实现
cat applications/auth/protected_routes.py
```

**待确认机制**:
- 用户登出时是否有令牌吊销机制
- 令牌黑名单的存储和检查机制
- 安全事件触发的批量令牌吊销

### 【TODO】速率限制和防暴力机制

**验证方法**: 搜索限流相关代码
```bash
# 搜索速率限制
grep -r "rate.*limit\|throttle\|frequency" applications/auth/
grep -r "attempt\|retry.*count" applications/auth/

# 检查验证码防护
grep -r "brute\|force\|attempt" applications/auth/email_verification.py
```

**待确认机制**:
- 验证码申请频率限制（同邮箱、同IP）
- 验证码暴力尝试防护
- 登录失败锁定机制
- OAuth回调频率限制

### 【TODO】日志和监控实现

**验证方法**: 检查实际日志代码
```bash
# 搜索日志调用
grep -r "logger\|logging\.info\|print" applications/auth/
grep -r "log.*auth\|auth.*log" utilities/logger/

# 检查监控指标
find . -name "*.py" -exec grep -l "metric\|counter\|timer" {} \;
```

**需要补充日志点**:
- 请求进入和响应时间记录
- 敏感操作审计日志（密码重置、OAuth绑定）
- 错误详细信息和堆栈跟踪
- 业务指标埋点（成功率、用户转换）

### 【TODO】现有测试覆盖情况

**验证方法**: 分析现有测试代码
```bash
# 检查现有测试
find applications/auth/test/ -name "*.py" -exec wc -l {} \;
ls -la applications/auth/test/

# 分析测试覆盖范围
grep -r "def test_" applications/auth/test/
```

**缺口分析**:
- 现有测试与本文档测试矩阵的对比
- 未覆盖的边界用例识别
- 集成测试和E2E测试的缺失情况

### 【TODO】错误处理和异常传播

**验证方法**: 跟踪异常处理链路
```bash
# 跟踪异常传播
grep -r "try:\|except\|raise" applications/auth/ | head -20
grep -r "Exception\|Error" hub/router.py

# 检查HTTP错误码映射
grep -r "400\|401\|409\|500" hub/
```

**待验证路径**:
- intent_handlers异常 → hub/router → HTTP响应码映射
- 数据库异常的具体错误类型和处理
- 外部服务（邮件、OAuth）异常的降级策略

### 【TODO】性能和扩展性考虑

**验证方法**: 分析性能瓶颈点
```bash
# 检查缓存使用
grep -r "cache\|Cache" applications/auth/
grep -r "_verification_codes\|_reset_codes" applications/auth/

# 分析数据库查询模式
grep -r "db\.find\|db\.insert\|db\.update" applications/auth/repository.py
```

**关键验证点**:
- 验证码内存缓存的扩展性（单机 vs 分布式）
- 数据库查询的索引使用情况
- 高并发场景下的性能表现
- OAuth第三方调用的超时和重试策略

---

## 验证建议清单

为确保本文档准确性，建议按以下优先级验证上述【TODO】项：

1. **P0 (必须验证)**: 配置项、OAuth实现、数据库事务
2. **P1 (高优先级)**: 错误处理、现有测试、令牌安全  
3. **P2 (中优先级)**: 速率限制、日志监控、性能考虑

**验证方法示例**:
```python
# 最小验证脚本
async def verify_oauth_config():
    """验证OAuth配置是否完整"""
    from applications.auth.oauth_google import get_google_auth_url
    try:
        url = get_google_auth_url("test_state")
        print(f"✓ Google OAuth配置正常: {url}")
    except Exception as e:
        print(f"✗ Google OAuth配置异常: {e}")

# 数据库事务验证
async def verify_user_creation_atomicity():
    """验证用户创建的原子性"""
    # 模拟创建过程中的异常，检查数据一致性
    pass
```

通过以上验证，可确保生成的自动化测试脚本覆盖所有真实的业务场景和技术约束。
