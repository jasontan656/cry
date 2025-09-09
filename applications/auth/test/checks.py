# checks.py 导入必要的模块进行断言和验证
import sys
from typing import Dict, Any, Optional, List

# 从utils模块导入相关功能
try:
    from .utils import mask_sensitive_data, log_json
except ImportError:
    # 如果相对导入失败，使用绝对导入
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from utils import mask_sensitive_data, log_json
try:
    from .config import *
except ImportError:
    # 如果相对导入失败，使用绝对导入
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from config import *


class TestAssertionError(Exception):
    """
    TestAssertionError 自定义异常类用于测试断言失败
    当断言失败时抛出此异常，包含详细的失败信息
    """

    def __init__(self, message: str, details: Dict[str, Any] = None):
        # message 通过参数传入赋值给实例属性
        self.message = message
        # details 通过参数传入或默认空字典赋值给实例属性
        self.details = details or {}
        # super().__init__ 通过调用父类构造函数初始化异常
        super().__init__(self.message)


def assert_http_status(response: Dict[str, Any], expected_status: int, context: str = "") -> None:
    """
    assert_http_status 函数断言HTTP响应状态码
    如果实际状态码与期望不符，抛出TestAssertionError异常

    参数:
        response: HTTP响应字典，包含status_code字段
        expected_status: 期望的HTTP状态码
        context: 断言上下文描述，用于错误信息

    异常:
        TestAssertionError: 当状态码不匹配时抛出
    """
    actual_status = response.get("status_code")

    # 检查响应是否包含status_code字段
    if actual_status is None:
        error_msg = f"HTTP状态码断言失败 - 响应中缺少status_code字段"
        if context:
            error_msg += f" ({context})"

        raise TestAssertionError(error_msg, {
            "expected_status": expected_status,
            "response": response,
            "context": context
        })

    # 检查状态码是否匹配
    if actual_status != expected_status:
        error_msg = f"HTTP状态码断言失败 - 期望: {expected_status}, 实际: {actual_status}"
        if context:
            error_msg += f" ({context})"

        raise TestAssertionError(error_msg, {
            "expected_status": expected_status,
            "actual_status": actual_status,
            "response": response,
            "context": context
        })


def assert_field_exists(data: Dict[str, Any], field_path: str, context: str = "") -> None:
    """
    assert_field_exists 函数断言字段在数据中存在
    支持点分隔的嵌套字段路径，如"data.user_id"

    参数:
        data: 要检查的数据字典
        field_path: 字段路径字符串，支持嵌套路径
        context: 断言上下文描述

    异常:
        TestAssertionError: 当字段不存在时抛出
    """
    current_data = data
    path_parts = field_path.split(".")

    # 遍历路径的每一部分
    for i, part in enumerate(path_parts):
        if not isinstance(current_data, dict):
            error_msg = f"字段存在性断言失败 - 路径 '{'.'.join(path_parts[:i])}' 不是字典类型"
            if context:
                error_msg += f" ({context})"

            raise TestAssertionError(error_msg, {
                "field_path": field_path,
                "current_path": '.'.join(path_parts[:i]),
                "data": data,
                "context": context
            })

        if part not in current_data:
            error_msg = f"字段存在性断言失败 - 字段 '{field_path}' 不存在"
            if context:
                error_msg += f" ({context})"

            raise TestAssertionError(error_msg, {
                "field_path": field_path,
                "missing_field": part,
                "available_fields": list(current_data.keys()),
                "data": data,
                "context": context
            })

        # 移动到下一级数据
        current_data = current_data[part]

    # 字段存在，断言通过


def assert_field_value(data: Dict[str, Any], field_path: str, expected_value: Any, context: str = "") -> None:
    """
    assert_field_value 函数断言字段的值等于期望值
    支持点分隔的嵌套字段路径

    参数:
        data: 要检查的数据字典
        field_path: 字段路径字符串
        expected_value: 期望的字段值
        context: 断言上下文描述

    异常:
        TestAssertionError: 当字段值不匹配时抛出
    """
    # 首先确保字段存在
    assert_field_exists(data, field_path, context)

    current_data = data
    path_parts = field_path.split(".")

    # 遍历到最后一个字段
    for part in path_parts:
        current_data = current_data[part]

    # 检查值是否匹配
    if current_data != expected_value:
        error_msg = f"字段值断言失败 - 字段 '{field_path}' 期望: {expected_value}, 实际: {current_data}"
        if context:
            error_msg += f" ({context})"

        raise TestAssertionError(error_msg, {
            "field_path": field_path,
            "expected_value": expected_value,
            "actual_value": current_data,
            "data": data,
            "context": context
        })


def assert_response_success(response: Dict[str, Any], context: str = "") -> None:
    """
    assert_response_success 函数断言API响应表示成功
    检查响应体的success字段为True且HTTP状态码为2xx

    参数:
        response: HTTP响应字典
        context: 断言上下文描述

    异常:
        TestAssertionError: 当响应不表示成功时抛出
    """
    # 检查HTTP状态码
    assert_http_status(response, 200, context)

    # 检查响应体中的success字段
    response_body = response.get("response_body", {})
    if not isinstance(response_body, dict):
        error_msg = f"响应成功断言失败 - 响应体不是字典类型"
        if context:
            error_msg += f" ({context})"

        raise TestAssertionError(error_msg, {
            "response_body": response_body,
            "context": context
        })

    if not response_body.get("success", False):
        error_msg = f"响应成功断言失败 - success字段为False"
        if context:
            error_msg += f" ({context})"

        raise TestAssertionError(error_msg, {
            "response_body": response_body,
            "context": context
        })


def assert_db_document_exists(snapshot: Dict[str, Any], collection: str, context: str = "") -> None:
    """
    assert_db_document_exists 函数断言数据库集合中存在文档
    检查指定集合的文档数量大于0

    参数:
        snapshot: 数据库快照字典
        collection: 集合名称
        context: 断言上下文描述

    异常:
        TestAssertionError: 当集合中没有文档时抛出
    """
    if "collections" not in snapshot:
        error_msg = f"数据库文档存在断言失败 - 快照中缺少collections字段"
        if context:
            error_msg += f" ({context})"

        raise TestAssertionError(error_msg, {
            "snapshot": snapshot,
            "collection": collection,
            "context": context
        })

    if collection not in snapshot["collections"]:
        error_msg = f"数据库文档存在断言失败 - 快照中缺少集合 '{collection}'"
        if context:
            error_msg += f" ({context})"

        raise TestAssertionError(error_msg, {
            "snapshot": snapshot,
            "collection": collection,
            "available_collections": list(snapshot["collections"].keys()),
            "context": context
        })

    collection_data = snapshot["collections"][collection]
    doc_count = collection_data.get("count", 0)

    if doc_count == 0:
        error_msg = f"数据库文档存在断言失败 - 集合 '{collection}' 中没有文档"
        if context:
            error_msg += f" ({context})"

        raise TestAssertionError(error_msg, {
            "snapshot": snapshot,
            "collection": collection,
            "document_count": doc_count,
            "context": context
        })


def assert_db_document_count(snapshot: Dict[str, Any], collection: str, expected_count: int, context: str = "") -> None:
    """
    assert_db_document_count 函数断言数据库集合中的文档数量
    检查指定集合的文档数量是否等于期望值

    参数:
        snapshot: 数据库快照字典
        collection: 集合名称
        expected_count: 期望的文档数量
        context: 断言上下文描述

    异常:
        TestAssertionError: 当文档数量不匹配时抛出
    """
    # 确保集合存在
    assert_db_document_exists(snapshot, collection, context)

    collection_data = snapshot["collections"][collection]
    actual_count = collection_data.get("count", 0)

    if actual_count != expected_count:
        error_msg = f"数据库文档数量断言失败 - 集合 '{collection}' 期望: {expected_count}, 实际: {actual_count}"
        if context:
            error_msg += f" ({context})"

        raise TestAssertionError(error_msg, {
            "snapshot": snapshot,
            "collection": collection,
            "expected_count": expected_count,
            "actual_count": actual_count,
            "context": context
        })


def assert_db_field_exists(snapshot: Dict[str, Any], collection: str, field_name: str, context: str = "") -> None:
    """
    assert_db_field_exists 函数断言数据库文档中存在指定字段
    检查指定集合的第一个文档是否包含指定字段

    参数:
        snapshot: 数据库快照字典
        collection: 集合名称
        field_name: 字段名称
        context: 断言上下文描述

    异常:
        TestAssertionError: 当字段不存在时抛出
    """
    # 确保集合中有文档
    assert_db_document_exists(snapshot, collection, context)

    collection_data = snapshot["collections"][collection]
    documents = collection_data.get("documents", [])

    if not documents:
        error_msg = f"数据库字段存在断言失败 - 集合 '{collection}' 中没有文档数据"
        if context:
            error_msg += f" ({context})"

        raise TestAssertionError(error_msg, {
            "snapshot": snapshot,
            "collection": collection,
            "context": context
        })

    # 检查第一个文档是否包含指定字段
    first_doc = documents[0]
    if field_name not in first_doc:
        error_msg = f"数据库字段存在断言失败 - 字段 '{field_name}' 在集合 '{collection}' 的文档中不存在"
        if context:
            error_msg += f" ({context})"

        raise TestAssertionError(error_msg, {
            "snapshot": snapshot,
            "collection": collection,
            "field_name": field_name,
            "available_fields": list(first_doc.keys()),
            "document": first_doc,
            "context": context
        })


def assert_tokens_different(token1: str, token2: str, context: str = "") -> None:
    """
    assert_tokens_different 函数断言两个token不同
    用于验证token刷新后生成了新的token

    参数:
        token1: 第一个token字符串
        token2: 第二个token字符串
        context: 断言上下文描述

    异常:
        TestAssertionError: 当两个token相同时抛出
    """
    if token1 == token2:
        error_msg = f"Token差异断言失败 - 两个token相同，期望不同"
        if context:
            error_msg += f" ({context})"

        raise TestAssertionError(error_msg, {
            "token1_masked": mask_sensitive_data(token1),
            "token2_masked": mask_sensitive_data(token2),
            "context": context
        })


def assert_snapshot_has_changes(diff: Dict[str, Any], context: str = "") -> None:
    """
    assert_snapshot_has_changes 函数断言快照比较结果表示有变化
    检查diff字典中的has_changes字段为True

    参数:
        diff: 快照差异比较结果字典
        context: 断言上下文描述

    异常:
        TestAssertionError: 当没有检测到变化时抛出
    """
    if not diff.get("has_changes", False):
        error_msg = f"快照变化断言失败 - 未检测到数据库变化"
        if context:
            error_msg += f" ({context})"

        raise TestAssertionError(error_msg, {
            "diff": diff,
            "context": context
        })


def assert_oauth_env_available() -> bool:
    """
    assert_oauth_env_available 函数检查OAuth环境变量是否可用
    如果不可用但配置为必须，则抛出异常；否则返回False表示跳过

    返回:
        bool: OAuth环境是否可用

    异常:
        TestAssertionError: 当OAuth必需但环境变量不可用时抛出
    """
    import os

    google_client_id = os.getenv("GOOGLE_CLIENT_ID")
    google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

    env_available = bool(google_client_id and google_client_secret)

    if not env_available:
        if OAUTH_SKIP_IF_MISSING:
            # 配置为跳过，返回False
            return False
        else:
            # 配置为必需，抛出异常
            raise TestAssertionError("OAuth环境变量断言失败 - GOOGLE_OAUTH_CLIENT_ID 和 GOOGLE_OAUTH_CLIENT_SECRET 必需但未设置", {
                "google_client_id_set": bool(google_client_id),
                "google_client_secret_set": bool(google_client_secret),
                "skip_if_missing": OAUTH_SKIP_IF_MISSING
            })

    return True


def validate_test_result(success: bool, error_message: str = "", details: Dict[str, Any] = None) -> None:
    """
    validate_test_result 函数验证测试结果
    如果测试失败，记录错误信息并退出程序

    参数:
        success: 测试是否成功
        error_message: 错误信息
        details: 详细错误信息字典
    """
    if not success:
        # 记录失败信息到日志
        log_data = {
            "stage": "test_validation",
            "success": False,
            "error_message": error_message,
            "details": details or {}
        }
        log_json(log_data)

        # 打印错误信息
        print(f"\n✗ 测试失败: {error_message}")

        # 以非零退出码退出
        sys.exit(1)

    # 测试成功，记录成功信息
    log_data = {
        "stage": "test_validation",
        "success": True,
        "message": "断言验证通过"
    }
    log_json(log_data)
