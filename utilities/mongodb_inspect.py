#!/usr/bin/env python3
"""
MongoDB 数据库检查脚本
用于检查重构后的数据存储结构和内容

功能：
- 连接 MongoDB 数据库
- 检查各集合的文档结构
- 验证数据分离是否正确执行
- 显示字段分布和数据统计

使用方法：
python mongodb_inspect.py
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

def get_project_root():
    """获取项目根目录"""
    return Path(__file__).parent.parent.absolute()

def setup_environment():
    """设置环境"""
    project_root = get_project_root()
    sys.path.insert(0, str(project_root))
    
    print(f"项目根目录: {project_root}")
    print(f"Python 版本: {sys.version}")
    print(f"工作目录: {os.getcwd()}")
    
def inspect_database():
    """检查数据库内容"""
    print("\n" + "="*60)
    print("MongoDB 数据库内容检查")
    print("="*60)
    
    try:
        # 导入 MongoDB 连接器
        from utilities.mongodb_connector import DatabaseOperations, COLLECTIONS
        
        # 初始化数据库连接
        db_ops = DatabaseOperations()
        db = db_ops.db
        
        print(f"\n已连接到数据库: {db.name}")
        print(f"检查集合: {COLLECTIONS}")
        
        # 统计总览
        total_documents = 0
        collections_with_data = []
        
        for collection_name in COLLECTIONS:
            print(f"\n{'='*50}")
            print(f"集合: {collection_name}")
            print(f"{'='*50}")
            
            try:
                collection = db[collection_name]
                
                # 获取文档数量
                doc_count = collection.count_documents({})
                total_documents += doc_count
                
                print(f"文档数量: {doc_count}")
                
                if doc_count > 0:
                    collections_with_data.append(collection_name)
                    
                    # 获取所有文档
                    documents = list(collection.find({}))
                    
                    # 分析字段结构
                    all_fields = set()
                    for doc in documents:
                        all_fields.update(doc.keys())
                    
                    print(f"字段列表: {sorted(list(all_fields))}")
                    print(f"\n文档详情:")
                    print("-" * 30)
                    
                    for i, doc in enumerate(documents, 1):
                        print(f"\n[文档 {i}]")
                        for key, value in doc.items():
                            if key == "_id":
                                print(f"  _id: {str(value)}")
                            elif isinstance(value, str) and len(value) > 50:
                                # 截断过长的字符串
                                print(f"  {key}: {value[:50]}...")
                            else:
                                print(f"  {key}: {value}")
                    
                    # 特殊分析
                    if collection_name == "user_profiles":
                        analyze_user_profiles(documents)
                    elif collection_name == "user_status":
                        analyze_user_status(documents)
                    elif collection_name == "user_archive":
                        analyze_user_archive(documents)
                        
                else:
                    print("集合为空")
                    
            except Exception as e:
                print(f"检查集合 '{collection_name}' 时出错: {str(e)}")
        
        # 数据关联性检查
        print(f"\n{'='*60}")
        print("数据关联性检查")
        print(f"{'='*60}")
        check_data_relationships(db)
        
        # 总结
        print(f"\n{'='*60}")
        print("检查总结")
        print(f"{'='*60}")
        print(f"总文档数: {total_documents}")
        print(f"有数据的集合: {collections_with_data}")
        print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return True
        
    except ImportError as e:
        print(f"导入模块失败: {str(e)}")
        print("请确保在正确的环境中运行此脚本")
        return False
    except Exception as e:
        print(f"数据库检查失败: {str(e)}")
        return False

def analyze_user_profiles(documents):
    """分析 user_profiles 集合"""
    print(f"\n[user_profiles 集合分析]")
    expected_fields = {"user_id", "username", "email"}
    dynamic_fields = {"hashed_password", "oauth_google_id", "oauth_facebook_id"}
    
    for doc in documents:
        fields = set(doc.keys()) - {"_id"}
        has_static_only = expected_fields.issubset(fields)
        has_dynamic_fields = any(field in fields for field in dynamic_fields)
        
        print(f"  用户 {doc.get('user_id', 'Unknown')}:")
        print(f"    静态字段完整: {'✓' if has_static_only else '✗'}")
        print(f"    包含动态字段: {'✗ (需迁移)' if has_dynamic_fields else '✓'}")
        
        if has_dynamic_fields:
            found_dynamic = fields & dynamic_fields
            print(f"    发现的动态字段: {found_dynamic}")

def analyze_user_status(documents):
    """分析 user_status 集合"""
    print(f"\n[user_status 集合分析]")
    expected_fields = {"user_id"}
    dynamic_fields = {"hashed_password", "oauth_google_id", "oauth_facebook_id"}
    
    for doc in documents:
        fields = set(doc.keys()) - {"_id"}
        has_user_id = "user_id" in fields
        has_dynamic_data = any(field in fields for field in dynamic_fields)
        
        print(f"  状态记录 {doc.get('user_id', 'Unknown')}:")
        print(f"    有user_id: {'✓' if has_user_id else '✗'}")
        print(f"    有动态数据: {'✓' if has_dynamic_data else '✗'}")
        
        found_dynamic = fields & dynamic_fields
        if found_dynamic:
            print(f"    动态字段: {found_dynamic}")

def analyze_user_archive(documents):
    """分析 user_archive 集合"""
    print(f"\n[user_archive 集合分析]")
    
    for doc in documents:
        fields = set(doc.keys()) - {"_id", "user_id"}
        archived_fields = [field for field in fields if "_" in field and any(
            field.startswith(prefix) for prefix in ["hashed_password_", "oauth_google_id_", "oauth_facebook_id_"]
        )]
        
        print(f"  归档记录 {doc.get('user_id', 'Unknown')}:")
        print(f"    归档字段数量: {len(archived_fields)}")
        if archived_fields:
            print(f"    归档字段样例: {archived_fields[:3]}")  # 显示前3个

def check_data_relationships(db):
    """检查数据关联性"""
    try:
        # 获取各集合的用户ID
        profiles_users = set()
        status_users = set()
        archive_users = set()
        
        # user_profiles 中的用户
        profiles_collection = db["user_profiles"]
        for doc in profiles_collection.find({}, {"user_id": 1}):
            if "user_id" in doc:
                profiles_users.add(doc["user_id"])
        
        # user_status 中的用户
        status_collection = db["user_status"]
        for doc in status_collection.find({}, {"user_id": 1}):
            if "user_id" in doc:
                status_users.add(doc["user_id"])
                
        # user_archive 中的用户
        archive_collection = db["user_archive"]
        for doc in archive_collection.find({}, {"user_id": 1}):
            if "user_id" in doc:
                archive_users.add(doc["user_id"])
        
        print(f"user_profiles 中的用户: {len(profiles_users)}")
        print(f"user_status 中的用户: {len(status_users)}")
        print(f"user_archive 中的用户: {len(archive_users)}")
        
        # 检查一致性
        missing_status = profiles_users - status_users
        extra_status = status_users - profiles_users
        
        if missing_status:
            print(f"⚠️  缺少状态记录的用户: {missing_status}")
        if extra_status:
            print(f"⚠️  多余状态记录的用户: {extra_status}")
            
        if not missing_status and not extra_status and profiles_users:
            print("✓ 用户画像和状态记录完全匹配")
        elif not profiles_users and not status_users:
            print("ℹ️  数据库为空，无法检查关联性")
            
    except Exception as e:
        print(f"关联性检查失败: {str(e)}")

def main():
    """主函数"""
    print("MongoDB 数据库内容检查工具")
    print("用于验证 Auth 模块重构后的数据分离")
    
    # 设置环境
    setup_environment()
    
    # 检查数据库
    if inspect_database():
        print(f"\n✓ 数据库检查完成！")
        sys.exit(0)
    else:
        print(f"\n✗ 数据库检查失败！")
        sys.exit(1)

if __name__ == "__main__":
    main()
