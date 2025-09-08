#!/usr/bin/env python3
"""
临时脚本：获取MongoDB中已创建的collection名称

此脚本用于连接到MongoDB数据库，获取所有已存在的collection名称，
并将结果打印输出，以便后续硬编码到mongodb_connector.py中。
"""

from pymongo import MongoClient
from pymongo.errors import PyMongoError
import json


def get_collections():
    """
    获取MongoDB中所有collection的名称和基本信息

    返回:
        dict: 包含collection名称和统计信息的字典
    """
    try:
        # 连接到MongoDB，使用与mongodb_connector.py相同的配置
        connection_string = "mongodb://localhost:27017/"
        database_name = "careerbot_mongodb"

        print(f"连接到MongoDB: {connection_string}")
        print(f"数据库名称: {database_name}")

        # 建立连接
        client = MongoClient(connection_string)
        db = client[database_name]

        # 获取所有collection名称
        collections = db.list_collection_names()

        print(f"\n找到 {len(collections)} 个collections:")
        print("-" * 50)

        collections_info = {}

        for collection_name in sorted(collections):
            try:
                collection = db[collection_name]
                # 获取collection的基本统计信息
                stats = collection.estimated_document_count()

                collections_info[collection_name] = {
                    "document_count": stats,
                    "description": ""  # 稍后可以手动添加描述
                }

                print(f"Collection: {collection_name}")
                print(f"  文档数量: {stats}")
                print(f"  用途: [待补充]")
                print()

            except PyMongoError as e:
                print(f"获取 {collection_name} 统计信息失败: {str(e)}")
                collections_info[collection_name] = {
                    "document_count": "unknown",
                    "description": ""
                }

        # 保存到JSON文件供后续使用
        with open("collections_info.json", "w", encoding="utf-8") as f:
            json.dump(collections_info, f, ensure_ascii=False, indent=2)

        print("collection信息已保存到 collections_info.json")
        print("\nPython代码格式的collection列表:")
        print("# MongoDB Collections")
        print("COLLECTIONS = [")
        for name in sorted(collections):
            print(f'    "{name}",')
        print("]")

        return collections_info

    except PyMongoError as e:
        print(f"MongoDB连接失败: {str(e)}")
        print("请确保MongoDB服务正在运行")
        return None
    except Exception as e:
        print(f"发生错误: {str(e)}")
        return None


if __name__ == "__main__":
    print("开始获取MongoDB collections...")
    collections = get_collections()

    if collections:
        print("\n操作完成!")
    else:
        print("\n操作失败!")
