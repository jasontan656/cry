# utils.py 导入必要的模块进行HTTP请求和数据库操作
import json
import time
import os
from typing import Dict, Any, Optional
import requests
from pymongo import MongoClient
from pymongo.errors import PyMongoError
import sys
import os

# 将项目根目录添加到系统路径，以便导入utilities模块
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
sys.path.append(project_root)

# 从config模块导入配置常量
try:
    from .config import *
except ImportError:
    # 如果相对导入失败，使用绝对导入
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from config import *


def make_request(intent: str, payload: Dict[str, Any], base_url: str = BASE_URL, timeout: int = REQUEST_TIMEOUT) -> Dict[str, Any]:
    """
    make_request 函数封装HTTP POST请求到/intent端点
    用于发送意图驱动的API请求

    参数:
        intent: 意图标识字符串，如"register_step1"
        payload: 请求载荷字典，包含业务数据
        base_url: API基础URL，默认为配置中的BASE_URL
        timeout: 请求超时时间，默认为配置中的REQUEST_TIMEOUT

    返回:
        dict: 包含响应状态和数据的字典
    """
    # url 通过字符串拼接构造完整的API端点URL
    url = f"{base_url}/intent"

    # request_body 通过字典创建包含intent和payload的请求体
    request_body = {
        "intent": intent,
        "payload": payload
    }

    try:
        # requests.post 发送POST请求到/intent端点
        # 传入url、json参数（自动序列化request_body）、timeout参数
        response = requests.post(url, json=request_body, timeout=timeout)

        # 返回包含状态码和响应数据的字典
        return {
            "status_code": response.status_code,
            "response_body": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
            "headers": dict(response.headers),
            "success": response.status_code < 400
        }

    except requests.exceptions.RequestException as e:
        # 捕获网络请求异常，返回错误信息
        return {
            "status_code": None,
            "response_body": {"error": f"请求失败: {str(e)}"},
            "headers": {},
            "success": False
        }


def log_json(data: Dict[str, Any]) -> None:
    """
    log_json 函数将数据以单行JSON格式打印到控制台
    用于生成结构化的数据流转日志，支持MongoDB ObjectId序列化

    参数:
        data: 要打印的数据字典，会自动添加timestamp字段
    """
    # data_copy 通过字典复制创建副本，避免修改原始数据
    data_copy = data.copy()

    # time.time() 获取当前时间戳，添加到data_copy中
    data_copy["timestamp"] = time.time()

    # 自定义JSON编码器处理MongoDB ObjectId
    def json_encoder(obj):
        """处理MongoDB ObjectId和其他不可序列化的对象"""
        from bson import ObjectId
        if isinstance(obj, ObjectId):
            return str(obj)
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

    # json.dumps 将字典序列化为JSON字符串，使用自定义编码器
    try:
        print(json.dumps(data_copy, ensure_ascii=False, default=json_encoder))
    except Exception as e:
        # 如果仍然有序列化问题，输出简化版本
        simplified_copy = {k: str(v) if not isinstance(v, (dict, list, str, int, float, bool, type(None))) else v 
                          for k, v in data_copy.items()}
        print(json.dumps(simplified_copy, ensure_ascii=False))


def mask_sensitive_data(data: str) -> str:
    """
    mask_sensitive_data 函数对敏感数据进行脱敏处理
    对邮箱和token等信息进行部分隐藏

    参数:
        data: 需要脱敏的字符串数据

    返回:
        str: 脱敏后的字符串
    """
    if not isinstance(data, str):
        # 如果不是字符串类型，直接返回原值
        return data

    # 处理邮箱地址：保留前2后2个字符
    if "@" in data and "." in data:
        try:
            # 找到@符号位置，保留前2个字符和后2个字符
            at_index = data.find("@")
            if at_index > 2:
                return data[:2] + "***" + data[at_index-2:at_index] + "***" + data[-2:]
        except:
            pass

    # 处理token：如果是JWT格式，保留前后部分
    if data.count(".") == 2 and len(data) > 20:
        try:
            parts = data.split(".")
            if len(parts) == 3:
                return parts[0][:4] + "***." + parts[1][:4] + "***." + parts[2][:4] + "***"
        except:
            pass

    # 默认返回原字符串
    return data


def get_db_connection():
    """
    get_db_connection 函数建立MongoDB数据库连接
    使用配置中的连接字符串和数据库名

    返回:
        DatabaseOperations: 数据库操作实例，如果连接失败返回None
    """
    try:
        # 尝试导入utilities.mongodb_connector模块
        from utilities.mongodb_connector import DatabaseOperations

        # DatabaseOperations 通过构造函数创建数据库操作实例
        # 传入MONGODB_CONNECTION_STRING和MONGODB_DATABASE_NAME参数
        db_ops = DatabaseOperations(MONGODB_CONNECTION_STRING, MONGODB_DATABASE_NAME)

        # 返回数据库操作实例
        return db_ops

    except ImportError:
        # 如果无法导入utilities模块，尝试直接使用pymongo
        try:
            # MongoClient 通过构造函数创建MongoDB客户端连接
            # 传入MONGODB_CONNECTION_STRING参数
            client = MongoClient(MONGODB_CONNECTION_STRING)

            # client[MONGODB_DATABASE_NAME] 获取指定数据库实例
            db = client[MONGODB_DATABASE_NAME]

            # 返回数据库实例（简化版本，不包含所有DatabaseOperations方法）
            return db

        except Exception as e:
            # 连接失败时打印错误信息并返回None
            print(f"MongoDB连接失败: {str(e)}")
            return None
    except Exception as e:
        # 其他异常情况打印错误信息并返回None
        print(f"数据库连接初始化失败: {str(e)}")
        return None


def get_user_snapshot(db_ops, user_email: str) -> Dict[str, Any]:
    """
    get_user_snapshot 函数获取用户的数据库快照
    查询所有相关集合中的用户数据

    参数:
        db_ops: 数据库操作实例
        user_email: 用户邮箱地址

    返回:
        dict: 包含各集合用户数据的快照字典
    """
    snapshot = {
        "email": mask_sensitive_data(user_email),
        "timestamp": time.time(),
        "collections": {}
    }

    # 检查是否是DatabaseOperations实例（通过检查类名）
    # DatabaseOperations实例有特定的find方法签名，而pymongo.Database的find是Collection
    if type(db_ops).__name__ == 'DatabaseOperations':
        # DatabaseOperations实例，有真正的find方法
        find_method = db_ops.find
    else:
        # 直接的MongoDB数据库实例，需要通过集合访问find方法
        find_method = lambda collection, filter: list(db_ops[collection].find(filter))

    # 查询各个集合的用户数据，根据集合类型使用不同的查询策略
    # 首先查询user_profiles获取user_id，然后用于关联查询其他集合
    user_id_from_profile = None
    
    # 确保user_profiles优先查询以获取user_id
    collections_ordered = ["user_profiles"] + [c for c in COLLECTIONS if c != "user_profiles"]
    
    for collection in collections_ordered:
        try:
            # 根据集合类型使用不同的查询条件
            if collection == "user_profiles":
                # user_profiles: 直接通过email查询
                docs = find_method(collection, {"email": user_email})
                # 获取user_id用于关联查询其他集合
                if docs and len(docs) > 0:
                    user_id_from_profile = docs[0].get("user_id")
            elif collection == "user_status" and user_id_from_profile:
                # user_status: 通过user_id关联查询
                docs = find_method(collection, {"user_id": user_id_from_profile})
            elif collection == "user_archive" and user_id_from_profile:
                # user_archive: 通过user_id关联查询
                docs = find_method(collection, {"user_id": user_id_from_profile})
            else:
                # 其他集合或无user_id时，尝试email查询
                docs = find_method(collection, {"email": user_email})

            # snapshot["collections"][collection] 存储查询结果
            snapshot["collections"][collection] = {
                "count": len(docs),
                "documents": docs,
                "exists": len(docs) > 0
            }

        except Exception as e:
            # 查询失败时记录错误信息
            snapshot["collections"][collection] = {
                "count": 0,
                "documents": [],
                "exists": False,
                "error": str(e)
            }

    # 返回完整的用户数据快照
    return snapshot


def compare_snapshots(before: Dict[str, Any], after: Dict[str, Any]) -> Dict[str, Any]:
    """
    compare_snapshots 函数比较两个数据库快照的差异
    用于验证数据变更是否符合预期

    参数:
        before: 变更前的快照
        after: 变更后的快照

    返回:
        dict: 包含差异信息的字典
    """
    diff = {
        "timestamp": time.time(),
        "has_changes": False,
        "changes": {}
    }

    # 比较各个集合的变化
    for collection in COLLECTIONS:
        before_count = before["collections"].get(collection, {}).get("count", 0)
        after_count = after["collections"].get(collection, {}).get("count", 0)

        # 检查文档数量变化
        if before_count != after_count:
            diff["has_changes"] = True
            diff["changes"][collection] = {
                "count_change": after_count - before_count,
                "before_count": before_count,
                "after_count": after_count
            }

    # 返回差异比较结果
    return diff


def generate_test_email(prefix: str = TEST_EMAIL_PREFIX, timestamp: Optional[float] = None) -> str:
    """
    generate_test_email 函数生成唯一的测试邮箱地址
    使用时间戳确保每次测试的邮箱唯一

    参数:
        prefix: 邮箱前缀，默认为配置中的TEST_EMAIL_PREFIX
        timestamp: 时间戳，如果不提供则使用当前时间

    返回:
        str: 生成的测试邮箱地址
    """
    # timestamp 通过逻辑运算符选择参数或当前时间
    if timestamp is None:
        timestamp = time.time()

    # int(timestamp) 将时间戳转换为整数
    # 然后通过f字符串格式化生成邮箱地址
    return f"{prefix}_{int(timestamp)}@test.local"
