# intent_validator.py - Intent白名单验证器
"""
设计用途：
IntentValidator专门负责intent白名单验证逻辑，直接从ConfigCache读取intent_whitelist，
进行高效的集合成员检查。验证逻辑简单直接，无需复杂的状态管理和业务处理。

核心功能：
1. 白名单验证：检查请求的intent是否在预定义的白名单中
2. 高效查找：利用set数据结构的O(1)查找特性
3. 错误分类：区分intent为空和intent不在白名单两种错误情况
4. 结果返回：返回标准化的ValidationResult对象

验证规则：
- intent字段必须存在且不为空
- intent必须在预定义的白名单集合中
- 白名单来源于global_config.json的intent_mapping配置

设计理念：
- 单一职责：只负责intent验证，不涉及其他验证逻辑
- 性能优先：直接内存查找，无额外计算开销
- 结果标准化：返回统一的ValidationResult，便于主流程处理
- 配置驱动：验证规则完全由配置决定，便于动态调整
"""
