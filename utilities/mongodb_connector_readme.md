# 🗄️ MongoDB Connector Development Documentation

## 🏗️ MongoDB连接器模块实现规范

> **开发策略**: 提供MongoDB数据库的最小必要操作封装，支持业务模块的数据库交互需求

### 📅 实现状态概览

```
当前实现 ✅ → 计划扩展 📋
基础CRUD操作     完整业务功能扩展
```

---

# 📍 当前实现：基础CRUD操作封装

## 🎯 实现目标
提供MongoDB数据库基础操作的封装，支持现有业务模块的数据交互需求。

## 🏗️ 核心实现架构

### **DatabaseOperations类**
**MongoDB操作封装类**
```python
class DatabaseOperations:
    def __init__(self, connection_string: str = "mongodb://localhost:27017/",
                 database_name: str = "careerbot_mongodb"):
        # 初始化MongoDB连接
        # 创建数据库和集合的引用

    def insert(self, collection: str, document: dict):
        # 插入文档到指定集合

    def find(self, collection: str, filter: dict, projection: dict = None):
        # 查询文档列表

    def update(self, collection: str, filter: dict, data: dict):
        # 更新文档并自动归档旧值
```

### **核心方法说明**

#### **insert() 方法**
- **功能**：插入文档到指定集合
- **参数**：
  - `collection`: 目标集合名称
  - `document`: 要插入的文档字典
- **返回**：InsertOneResult对象
- **异常处理**：捕获PyMongoError并重新抛出

#### **find() 方法**
- **功能**：查询文档列表
- **参数**：
  - `collection`: 要查询的集合名称
  - `filter`: 查询过滤条件字典
  - `projection`: 可选的字段投影字典
- **返回**：查询到的文档列表
- **异常处理**：捕获PyMongoError并重新抛出

#### **update() 方法**
- **功能**：更新文档并按字段日志式归档旧值
- **参数**：
  - `collection`: 要更新的集合名称
  - `filter`: 更新过滤条件字典
  - `data`: 要更新的数据字典
- **返回**：UpdateResult对象
- **特殊功能**：
  - 自动识别需要归档的字段
  - 将旧值归档到user_archive集合
  - 支持字段级别的历史追踪
- **异常处理**：捕获PyMongoError并重新抛出

## 🔧 数据操作需求

### **当前支持的数据库交互**

#### **MBTI模块数据库交互**
- **用户状态查询**：检查MBTI测试完成状态和求职注册状态
- **测试结果保存**：存储各步骤的测试数据和最终人格类型
- **步骤状态更新**：标记测试各步骤的完成状态
- **用户认证**：登录、注册、密码验证等基础认证功能

#### **必需的数据库操作**
- `mongodb_connector_query` - 查询用户状态和测试数据
- `mongodb_connector_save` - 保存MBTI测试结果
- `mongodb_connector_auth` - 用户认证管理
- `mongodb_connector_update` - 更新测试步骤状态
- `mongodb_connector_chat_save` - 保存聊天历史
- `mongodb_connector_chat_query` - 查询聊天历史

## 📋 开发实施计划

### **已实现功能**
```
数据库操作：
✅ DatabaseOperations类实现 (MongoDB连接封装)
✅ insert()方法实现 (文档插入)
✅ find()方法实现 (文档查询)
✅ update()方法实现 (文档更新+自动归档)

集成测试：
⏳ MBTI模块数据库集成测试
⏳ 用户认证流程测试
⏳ 聊天记录管理测试
```

### **核心功能映射**
```
MBTI Step1 → mongodb_connector_query(user_status.JobFindingRegistryComplete)
MBTI Step2 → mongodb_connector_save(user_profiles.mbti_results) + mongodb_connector_update(user_status.mbti_step2)
MBTI Step3 → mongodb_connector_save(user_profiles.mbti_results) + mongodb_connector_update(user_status.mbti_step3)
MBTI Step4 → mongodb_connector_save(user_profiles.mbti_results) + mongodb_connector_update(user_status.mbti_step4)
MBTI Step5 → mongodb_connector_save(user_profiles.mbti_results) + mongodb_connector_update(user_status.mbti_step5)
用户登录 → mongodb_connector_auth(login)
用户注册 → mongodb_connector_auth(register)
聊天记录 → mongodb_connector_chat_save(user_chathistory)
```

## 📅 开发时间统计

```
当前实现 (1周):
├── DatabaseOperations类设计: 2天
├── 基础CRUD方法实现: 3天
├── 自动归档功能实现: 2天
```

## 🎯 核心设计要点总结

### **三大核心特性**
1. **简化封装**：提供标准MongoDB操作的最小封装
2. **自动归档**：update操作自动进行字段级历史追踪
3. **错误处理**：统一的异常捕获和处理机制

### **设计理念**
- **职责单一**：专注于数据库操作封装，不涉及业务逻辑
- **扩展性**：标准CRUD操作为未来扩展提供基础
- **可靠性**：完善的异常处理和错误恢复机制

## 📊 数据库初始化和索引验证

### **初始化脚本**
使用 `init_mongodb_corrected.py` 脚本进行数据库初始化，该脚本将：
- 创建所有必需的集合
- 设置正确的索引结构
- 插入示例数据用于测试

### **索引验证命令**
```bash
# 检查所有集合的索引
docker exec mongodb-dev mongosh careerbot_mongodb --eval "db.user_profiles.getIndexes(); db.user_status.getIndexes(); db.user_chathistory.getIndexes();"

# 验证集合统计
docker exec mongodb-dev mongosh careerbot_mongodb --eval "db.getCollectionNames();"
```

### **索引设计验证清单**
- ✅ `user_profiles.user_id` - 唯一索引
- ✅ `user_status.user_id` - 唯一索引
- ✅ `user_chathistory.user_id` - 唯一索引
- ✅ `user_archive.user_id` - 唯一索引

### **索引策略说明**
1. **简化原则**: 每个集合都只有 `user_id` 作为唯一索引
2. **数据优先**: 其他字段仅作为文档数据存储，无额外索引
3. **性能考虑**: 写入性能优先，查询时可接受全表扫描

---

# 📍 扩展计划：完整业务功能支持

> **目标**: 扩展支持所有业务模块的数据库交互需求

### **扩展方向**
- [ ] 批量操作支持
- [ ] 聚合查询封装
- [ ] 事务支持
- [ ] 性能监控和优化
- [ ] 连接池管理
- [ ] 缓存层集成

---

*此文档基于实际的 `mongodb_connector.py` 实现编写，准确反映当前模块的功能和设计理念。*
