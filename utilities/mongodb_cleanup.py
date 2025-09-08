#!/usr/bin/env python3
"""
MongoDB 数据库清理脚本
用于清除所有集合中的文档，但保留集合结构和索引

功能：
- 激活虚拟环境
- 连接 MongoDB 数据库
- 清除所有集合中的文档（保留集合结构）
- 保留 user_id 唯一索引
- 显示清理结果统计

使用方法：
python db_cleanup.py
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def activate_venv():
    """激活虚拟环境"""
    print("正在激活虚拟环境...")

    # 获取项目根目录
    project_root = Path(__file__).parent.absolute()

    # Windows 环境下虚拟环境激活脚本路径
    venv_activate = project_root / "venv" / "Scripts" / "activate.bat"

    if not venv_activate.exists():
        print(f"错误：虚拟环境激活脚本不存在：{venv_activate}")
        print("请确保虚拟环境已正确安装")
        return False

    try:
        # 使用 subprocess 执行激活脚本
        result = subprocess.run(
            str(venv_activate),
            shell=True,
            capture_output=True,
            text=True,
            cwd=str(project_root)
        )

        if result.returncode == 0:
            print("✓ 虚拟环境激活成功")
            return True
        else:
            print(f"✗ 虚拟环境激活失败：{result.stderr}")
            return False

    except Exception as e:
        print(f"✗ 激活虚拟环境时发生错误：{str(e)}")
        return False

def cleanup_database():
    """清理数据库"""
    print("\n开始数据库清理...")

    try:
        # 导入 MongoDB 连接器
        from utilities.mongodb_connector import DatabaseOperations, COLLECTIONS

        # 初始化数据库连接
        db_ops = DatabaseOperations()

        # 获取数据库对象
        db = db_ops.db

        print(f"已连接到数据库：{db.name}")
        print(f"需要清理的集合：{COLLECTIONS}")

        # 统计清理结果
        total_collections = len(COLLECTIONS)
        cleaned_collections = 0
        total_docs_deleted = 0

        for collection_name in COLLECTIONS:
            try:
                collection = db[collection_name]

                # 获取集合中文档数量
                doc_count_before = collection.count_documents({})

                # 删除所有文档（保留集合和索引）
                delete_result = collection.delete_many({})

                # 获取删除后的文档数量
                doc_count_after = collection.count_documents({})

                docs_deleted = delete_result.deleted_count

                print(f"✓ 集合 '{collection_name}': 删除 {docs_deleted} 个文档")

                if docs_deleted > 0:
                    cleaned_collections += 1
                    total_docs_deleted += docs_deleted

                # 检查并确保 user_id 唯一索引存在（如果适用）
                if collection_name in ['user_profiles', 'user_status', 'user_chathistory', 'user_archive']:
                    try:
                        # 检查是否已有 user_id 索引
                        indexes = list(collection.list_indexes())
                        user_id_index_exists = any(
                            'user_id' in str(index['key']) for index in indexes
                        )

                        if not user_id_index_exists:
                            # 创建 user_id 唯一索引
                            collection.create_index('user_id', unique=True)
                            print(f"  - 已创建 user_id 唯一索引")
                        else:
                            print(f"  - user_id 索引已存在")

                    except Exception as e:
                        print(f"  - 索引检查/创建失败：{str(e)}")

            except Exception as e:
                print(f"✗ 清理集合 '{collection_name}' 时出错：{str(e)}")

        # 输出清理总结
        print("\n=== 清理总结 ===")
        print(f"总集合数：{total_collections}")
        print(f"已清理集合数：{cleaned_collections}")
        print(f"总删除文档数：{total_docs_deleted}")

        if cleaned_collections > 0:
            print("✓ 数据库清理完成！")
        else:
            print("ℹ 没有需要清理的文档")

        return True

    except ImportError as e:
        print(f"✗ 导入模块失败：{str(e)}")
        print("请确保在虚拟环境中运行此脚本")
        return False
    except Exception as e:
        print(f"✗ 数据库清理失败：{str(e)}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("MongoDB 数据库清理脚本")
    print("=" * 50)

    # 检查 Python 版本
    print(f"Python 版本：{sys.version}")

    # 激活虚拟环境
    if not activate_venv():
        print("\n由于虚拟环境激活失败，脚本退出")
        sys.exit(1)

    # 等待一下确保环境变量生效
    time.sleep(1)

    # 清理数据库
    if cleanup_database():
        print("\n✓ 脚本执行完成！")
        sys.exit(0)
    else:
        print("\n✗ 脚本执行失败！")
        sys.exit(1)

if __name__ == "__main__":
    main()
