# hub/error_presets.py - 错误预设常量模块
# Fast Fail: 预构建不可变错误字典，避免动态拼装异常报文

# INVALID_INTENT 通过字典常量定义无效intent的标准错误响应
# 包含错误类型、错误代码、消息和建议信息
INVALID_INTENT = {
    "error_type": "InvalidIntent",
    "error_code": "INTENT_NOT_REGISTERED", 
    "message": "Intent not registered",
    "suggestion": "Register step via flow_registry.register_step()"
}

# MISSING_INTENT 通过字典常量定义缺失intent字段的标准错误响应
# 包含错误类型、错误代码、消息和建议信息
MISSING_INTENT = {
    "error_type": "InvalidRequest",
    "error_code": "INTENT_MISSING",
    "message": "Missing 'intent' field in request",
    "suggestion": "Provide 'intent' as step identifier"
}

# PROCESSING_ERROR 通过字典常量定义处理执行失败的标准错误响应
# 包含错误类型、错误代码和基础消息信息
PROCESSING_ERROR = {
    "error_type": "ProcessingError", 
    "error_code": "EXECUTION_FAILED",
    "message": "Intent execution failed",
    "suggestion": "Check handler function and input data"
}
