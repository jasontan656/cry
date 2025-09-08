# 用户认证模块 (Auth Module)

本模块实现用户注册功能，使用Pydantic进行数据建模，通过调用`utilities/mongodb_connector.py`进行数据库操作。

## 功能特性

- ✅ 用户注册功能
- ✅ 输入数据验证（用户名、邮箱、密码格式）
- ✅ 密码加密存储（bcrypt）
- ✅ 用户存在性检查
- ✅ 自定义异常处理
- ✅ 类型注解支持

## 文件结构

```
applications/auth/
├── __init__.py          # 模块初始化
├── auth.py              # 主入口文件
├── router.py            # 路由处理
├── schemas.py           # Pydantic数据模型
├── validators.py        # 输入验证逻辑
├── hashing.py           # 密码加密逻辑
├── repository.py        # 数据库操作封装
├── register.py          # 注册主逻辑
├── exceptions.py        # 自定义异常类
└── test_register.py     # 功能测试文件
```

## 核心组件说明

### 数据模型 (schemas.py)
- `UserRegisterRequest`: 注册请求数据
- `UserResponse`: 注册响应数据
- `UserData`: 内部用户数据结构

### 异常类型 (exceptions.py)
- `UserAlreadyExistsError`: 用户已存在异常
- `InvalidInputError`: 输入数据无效异常

### 验证规则 (validators.py)
- 邮箱：标准邮箱格式验证（同时作为用户名）
- 密码：至少8个字符

## API 端点

### 🔗 可用的HTTP端点

| 方法 | 端点 | 功能 | 请求数据格式 |
|------|------|------|-------------|
| POST | `/auth/register` | 用户注册 | `{"email": "user@example.com", "password": "password123"}` |
| POST | `/auth/login` | 用户登录 | `{"email": "user@example.com", "password": "password123"}` |
| POST | `/auth/send-verification` | 发送验证码 | `{"email": "user@example.com"}` |
| POST | `/auth/verify-code` | 验证验证码 | `{"email": "user@example.com", "code": "123456"}` |
| POST | `/auth/set-password` | 设置密码 | `{"email": "user@example.com", "password": "password123"}` |
| POST | `/auth/google` | Google OAuth授权 | `{"state": "optional_state"}` |
| POST | `/auth/google/callback` | Google OAuth回调 | `{"code": "auth_code", "state": "state", "expected_state": "expected"}` |
| POST | `/auth/facebook` | Facebook OAuth授权 | `{"state": "optional_state"}` |
| POST | `/auth/facebook/callback` | Facebook OAuth回调 | `{"code": "auth_code", "state": "state", "expected_state": "expected"}` |

## 使用方法

### 1. 基本注册调用

```python
from applications.auth import register_user, UserRegisterRequest

# 创建注册请求
request = UserRegisterRequest(
    email="test@example.com",
    password="securepassword123"
)

# 执行注册
result = register_user(request)
print(result)  # UserResponse对象
```

### 2. 基本登录调用

```python
from applications.auth import login_user

# 执行登录
result = login_user("test@example.com", "securepassword123")
print(result)  # UserResponse对象
```

### 3. HTTP路由调用

```python
from applications.auth.router import ROUTES, handle_login_request

# 标准登录
response = handle_login_request({
    "email": "test@example.com",
    "password": "securepassword123"
})
print(response)

# Google OAuth授权
from applications.auth.router import handle_google_auth
response = handle_google_auth({"state": "random123"})
print(response["data"]["auth_url"])  # 获取授权URL
```

### 4. 邮箱验证码注册流程

```python
from applications.auth import send_verification_code_to_email, verify_email_code, set_user_password_after_verification
from applications.auth.schemas import SendVerificationRequest, VerifyCodeRequest, SetPasswordRequest

# 步骤1: 发送验证码
send_request = SendVerificationRequest(email="user@example.com")
result = await send_verification_code_to_email(send_request)
print(result)  # {"success": true, "message": "验证码已发送到您的邮箱，请查收"}

# 步骤2: 验证验证码
verify_request = VerifyCodeRequest(email="user@example.com", code="123456")
result = verify_email_code(verify_request)
print(result)  # 返回用户状态信息

# 步骤3: 设置密码完成注册
if result.success:
    set_password_request = SetPasswordRequest(email="user@example.com", password="secure123")
    result = set_user_password_after_verification(set_password_request)
    print(result)  # {"success": true, "message": "注册成功！您可以使用邮箱和密码登录"}
```

### 5. OAuth用户设置密码

```python
# 对于已通过OAuth注册但未设置密码的用户
from applications.auth.router import handle_send_verification_code, handle_verify_code, handle_set_password

# 发送验证码到OAuth用户的邮箱
send_result = await handle_send_verification_code({"email": "oauth_user@gmail.com"})
print(send_result)

# 验证验证码
verify_result = handle_verify_code({"email": "oauth_user@gmail.com", "code": "123456"})
print(verify_result)  # 应该显示 is_oauth_user: true

# 设置密码启用邮箱登录
set_result = handle_set_password({"email": "oauth_user@gmail.com", "password": "newpassword123"})
print(set_result)  # {"success": true, "message": "密码设置成功！现在您可以使用邮箱密码登录"}
```

### 6. 异常处理

```python
from applications.auth import register_user, UserRegisterRequest
from applications.auth.exceptions import UserAlreadyExistsError, InvalidInputError

try:
    result = register_user(request)
except UserAlreadyExistsError:
    print("用户已存在")
except InvalidInputError as e:
    print(f"输入数据无效: {e}")
```

## 数据库设计

用户数据存储在 `user_profiles` 集合中：

```javascript
{
  "user_id": "uuid-string",
  "username": "testuser",
  "email": "test@example.com",
  "hashed_password": "bcrypt-hash-string"
}
```

## 依赖要求

确保在 `requirements.txt` 中包含以下依赖：

```
pydantic>=2.0.0
bcrypt>=4.0.0
email-validator>=2.0.0
pymongo>=4.0.0
```

## 运行测试

```python
python -m applications.auth.test_register
```

## 扩展建议

- 添加用户登录功能
- 实现Token认证机制
- 添加密码重置功能
- 集成邮箱验证
- 添加用户状态管理

## 注意事项

1. 密码使用bcrypt进行不可逆加密
2. 用户ID使用UUID自动生成
3. 所有数据库操作通过`utilities/mongodb_connector.py`完成
4. 输入验证在注册流程早期执行
5. 异常信息不包含敏感数据
