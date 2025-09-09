"""
数据库基础操作封装模块

本模块提供数据库的最小必要操作封装，包括：
- 文档插入操作
- 文档查询操作
- 文档更新操作（包含自动归档功能）

所有操作不涉及业务逻辑判断，由调用方决定操作类型和数据结构。

MongoDB Collections 信息（已创建的数据集合）：
===========================================

当前数据库中的所有collections及其用途：

1. user_archive (1个文档)
   - 用途：用户数据归档集合
   - 说明：存储用户字段变更的历史记录，按user_id分组归档

2. user_chathistory (1个文档)
   - 用途：用户聊天历史记录
   - 说明：存储用户的对话记录和聊天历史

3. user_profiles (1个文档)
   - 用途：用户个人资料
   - 说明：存储用户的个人信息、偏好设置等

4. user_status (1个文档)
   - 用途：用户状态信息
   - 说明：存储用户的登录状态、在线状态等

Collections常量列表：
"""
# MongoDB Collections 常量定义
COLLECTIONS = [
    "user_archive",      # 用户归档数据
    "user_chathistory",  # 用户聊天历史
    "user_profiles",     # 用户个人画像
    "user_status",       # 用户状态信息
]

# 从 utilities.time 模块导入 Time 类，用于生成时间戳和UUID
import sys
import os

# 将项目根目录添加到系统路径中，以便绝对路径导入
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.append(project_root)

# 绝对路径导入 utilities.time.Time 类
from utilities.time import Time

# 导入 pymongo 相关模块进行数据库操作
from pymongo import MongoClient
from pymongo.errors import PyMongoError


class DatabaseOperations:
    """
    数据库操作封装类

    提供数据库基础操作的最小封装，所有操作使用标准 pymongo 写法。
    不进行任何业务逻辑处理，由调用方决定操作策略。
    """

    def __init__(self, connection_string: str = "mongodb://localhost:27017/", database_name: str = "careerbot_mongodb"):
        """
        初始化数据库连接

        通过 MongoClient 建立数据库连接，并选择指定的数据库。
        默认连接到本地 MongoDB 实例，使用 careerbot_mongodb 数据库。

        参数:
            connection_string: MongoDB 连接字符串，默认为本地连接
            database_name: 数据库名称，默认为 careerbot_mongodb
        """
        # 通过 MongoClient 建立与 MongoDB 的连接
        self.client = MongoClient(connection_string)

        # 选择指定的数据库 careerbot_mongodb
        self.db = self.client[database_name]

    def insert(self, collection: str, document: dict):
        """
        插入文档到指定集合

        使用 pymongo 的 insert_one() 方法将指定的文档插入到指定集合中。
        不进行任何字段验证或结构处理，直接执行插入操作。

        参数:
            collection: 目标集合名称
            document: 要插入的文档字典

        返回:
            InsertOneResult: 插入操作的结果对象

        异常:
            PyMongoError: 数据库操作异常
        """
        try:
            # 获取指定的集合对象
            collection_obj = self.db[collection]

            # 使用 insert_one() 方法将文档插入到集合中
            result = collection_obj.insert_one(document)

            # 返回插入操作的结果
            return result

        except PyMongoError as e:
            # 捕获并打印数据库操作异常
            print(f"数据库插入操作失败，集合: {collection}, 错误: {str(e)}")

            # 重新抛出异常供调用方处理
            raise

    def find(self, collection: str, filter: dict, projection: dict = None):
        """
        查询文档列表

        使用 pymongo 的 find() 方法在指定集合中执行查询操作。
        支持可选的字段投影过滤，返回查询结果的文档列表。

        参数:
            collection: 要查询的集合名称
            filter: 查询过滤条件字典
            projection: 可选的字段投影字典，用于指定返回的字段

        返回:
            list: 查询到的文档列表，如果没有找到文档则返回空列表

        异常:
            PyMongoError: 数据库操作异常
        """
        try:
            # 获取指定的集合对象
            collection_obj = self.db[collection]

            # 使用 find() 方法执行查询，传入过滤条件和投影参数
            cursor = collection_obj.find(filter, projection)

            # 将查询结果转换为列表并返回
            return list(cursor)

        except PyMongoError as e:
            # 捕获并打印数据库查询异常
            print(f"数据库查询操作失败，集合: {collection}, 错误: {str(e)}")

            # 重新抛出异常供调用方处理
            raise

    def update(self, collection: str, filter: dict, data: dict):
        """
        更新文档并按字段日志式归档旧值

        在更新前读取旧文档，仅用于提取旧值。
        仅对已存在且将被改变的字段做归档。
        归档写入 user_archive 集合：_id=user_id。
        归档条目键：字段名_时间戳_uuid，值为旧值。
        归档成功后再更新原集合，upsert=False。

        参数:
            collection: 要更新的集合名称
            filter: 更新过滤条件字典
            data: 要更新的数据字典

        返回:
            UpdateResult: 更新操作的结果对象

        异常:
            PyMongoError: 数据库操作异常
        """
        try:
            # 通过 self.db[...] 获取集合对象
            # 传入集合名 collection，得到集合对象
            # 结果赋值给 collection_obj，用于后续操作
            collection_obj = self.db[collection]

            # 通过 find_one(filter) 读取旧文档
            # 传入过滤条件 filter，获取旧数据
            # 结果赋值 old_document，用于比较旧值
            old_document = collection_obj.find_one(filter)

            # 若读取不到旧文档，则无法归档
            # 打印错误并抛出异常，终止更新链
            if old_document is None:
                print(f"更新前读取失败，集合:{collection}, 条件:{filter}")
                raise ValueError("未找到旧文档，归档失败，未执行更新")

            # 从 filter 读取 user_id 用于归档主键
            # 要求 filter 提供 user_id，赋值给 user_id
            user_id = filter.get('user_id')

            # 若缺少 user_id，无从定位归档文档
            # 打印错误并抛出异常，终止更新链
            if user_id is None:
                print(f"归档需要 user_id，集合:{collection}, 条件:{filter}")
                raise ValueError("缺少 user_id，归档失败，未执行更新")

            # 遍历 data，比较旧值与新值
            # 仅挑选旧文档存在且将改变的字段
            # 结果构造 logs 映射：日志键->旧值
            logs = {}
            for field_name, new_value in data.items():
                if field_name in old_document:
                    old_value = old_document[field_name]
                    if old_value != new_value:
                        # 通过 Time.timestamp() 生成时间戳+uuid
                        # 组合日志键：字段名_时间戳_uuid
                        log_key = f"{field_name}_{Time.timestamp()}"
                        # 将旧值映射到日志键，写入 logs
                        logs[log_key] = old_value

            # 若存在需要归档的字段，则先写入归档
            if logs:
                # 通过 self.db['user_archive'] 获取归档集合
                # 得到 archive_collection，用于写入日志
                archive_collection = self.db['user_archive']

                # 使用 update_one 归档日志，upsert=True
                # 以 {_id:user_id} 定位或创建文档
                # 用 {$set: logs} 写入多个日志键
                # 同时确保 user_id 字段被正确设置
                archive_data = logs.copy()
                archive_data['user_id'] = user_id
                archive_result = archive_collection.update_one(
                    {'_id': user_id},
                    {'$set': archive_data},
                    upsert=True
                )

                # 校验归档是否成功：需 acknowledged
                # 且 matched>0 或 upserted_id 存在
                if (not archive_result.acknowledged) or (
                    archive_result.matched_count == 0 and archive_result.upserted_id is None
                ):
                    print(f"归档写入失败，集合:user_archive, _id:{user_id}")
                    raise ValueError("归档写入未确认，未执行更新")

            # 使用 update_one 执行原集合更新
            # 传入 filter 与 {$set:data} 覆盖字段
            # upsert=False，遵循上层已存在前提
            update_result = collection_obj.update_one(
                filter,
                {'$set': data},
                upsert=False
            )

            # 返回更新操作结果 UpdateResult
            return update_result

        except PyMongoError as e:
            # 捕获并打印数据库更新异常
            print(f"数据库更新操作失败，集合: {collection}, 错误: {str(e)}")

            # 重新抛出异常供调用方处理
            raise
