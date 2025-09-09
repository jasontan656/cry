# seed.py 导入必要的模块进行测试环境准备
import sys
import os
from typing import Dict, Any, List

# 将项目根目录添加到系统路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
sys.path.append(project_root)

# 从config和utils模块导入相关功能
try:
    from .config import *
    from .utils import get_db_connection, make_request, log_json, generate_test_email
except ImportError:
    # 如果相对导入失败，使用绝对导入
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from config import *
    from utils import get_db_connection, make_request, log_json, generate_test_email


def clean_test_collections(db_ops, test_email_prefix: str = TEST_EMAIL_PREFIX) -> Dict[str, Any]:
    """
    clean_test_collections 函数清理测试相关的数据库集合
    只删除以测试邮箱前缀开头的用户数据，确保安全

    参数:
        db_ops: 数据库操作实例
        test_email_prefix: 测试邮箱前缀，用于识别测试数据

    返回:
        dict: 清理结果统计信息
    """
    result = {
        "timestamp": None,  # 稍后设置
        "collections_cleaned": [],
        "total_documents_removed": 0,
        "errors": []
    }

    # 如果没有数据库连接，返回错误
    if db_ops is None:
        result["errors"].append("数据库连接不可用")
        return result

    # 构建测试数据过滤条件
    test_filter = {
        "email": {"$regex": f"^{test_email_prefix}_.*@test\\.local$"}
    }

    # 检查是否有delete_many方法（DatabaseOperations实例）
    if hasattr(db_ops, 'db'):
        # 如果是DatabaseOperations实例
        db_instance = db_ops.db
    else:
        # 如果是直接的MongoDB数据库实例
        db_instance = db_ops

    # 清理各个集合
    for collection_name in COLLECTIONS:
        try:
            # 获取集合实例
            collection = db_instance[collection_name]

            # 查询符合条件的文档数量
            before_count = collection.count_documents(test_filter)

            # 删除符合条件的文档
            delete_result = collection.delete_many(test_filter)

            # 记录清理结果
            result["collections_cleaned"].append({
                "collection": collection_name,
                "documents_removed": delete_result.deleted_count,
                "before_count": before_count
            })

            # 累加删除总数
            result["total_documents_removed"] += delete_result.deleted_count

        except Exception as e:
            # 记录清理过程中的错误
            result["errors"].append(f"清理集合 {collection_name} 失败: {str(e)}")

    # 设置时间戳
    import time
    result["timestamp"] = time.time()

    # 返回清理结果
    return result


def check_environment() -> Dict[str, Any]:
    """
    check_environment 函数检查测试环境是否准备就绪
    检查数据库连接、API可用性、OAuth环境变量等

    返回:
        dict: 环境检查结果
    """
    import time
    result = {
        "timestamp": time.time(),
        "checks": {},
        "overall_ready": False
    }

    # 1. 检查数据库连接
    print("检查数据库连接...")
    db_ops = get_db_connection()
    if db_ops is None:
        result["checks"]["mongodb"] = {
            "status": "failed",
            "message": "无法连接到MongoDB数据库"
        }
    else:
        result["checks"]["mongodb"] = {
            "status": "passed",
            "message": "MongoDB连接正常"
        }

    # 2. 检查API可用性
    print("检查API服务可用性...")
    try:
        # 直接发送GET请求到健康检查端点
        import requests
        response = requests.get(f"{BASE_URL}/health", timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            result["checks"]["api_service"] = {
                "status": "passed",
                "message": "API服务运行正常"
            }
        else:
            result["checks"]["api_service"] = {
                "status": "failed",
                "message": f"API服务响应异常，状态码: {response.status_code}"
            }
    except Exception as e:
        result["checks"]["api_service"] = {
            "status": "failed",
            "message": f"无法连接到API服务: {str(e)}"
        }

    # 3. 检查OAuth环境变量
    print("检查OAuth环境变量...")
    google_client_id = os.getenv("GOOGLE_CLIENT_ID")
    google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

    if google_client_id and google_client_secret:
        result["checks"]["oauth_google"] = {
            "status": "passed",
            "message": "Google OAuth环境变量已配置"
        }
    else:
        result["checks"]["oauth_google"] = {
            "status": "skipped",
            "message": "Google OAuth环境变量未配置，将跳过OAuth测试"
        }

    # 4. 检查必要的Python包
    print("检查Python依赖...")
    required_packages = ["requests", "pymongo"]
    missing_packages = []

    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        result["checks"]["python_packages"] = {
            "status": "failed",
            "message": f"缺少必要的Python包: {', '.join(missing_packages)}"
        }
    else:
        result["checks"]["python_packages"] = {
            "status": "passed",
            "message": "所有必要的Python包都已安装"
        }

    # 5. 确定整体就绪状态
    critical_checks = ["mongodb", "api_service", "python_packages"]
    all_critical_passed = all(
        result["checks"].get(check, {}).get("status") == "passed"
        for check in critical_checks
    )

    result["overall_ready"] = all_critical_passed

    # 输出检查结果摘要
    print(f"\n环境检查完成:")
    print(f"  整体状态: {'✓ 就绪' if result['overall_ready'] else '✗ 未就绪'}")

    for check_name, check_result in result["checks"].items():
        status_icon = "✓" if check_result["status"] == "passed" else ("⚠" if check_result["status"] == "skipped" else "✗")
        print(f"  {status_icon} {check_name}: {check_result['message']}")

    # 返回环境检查结果
    return result


def setup_test_environment() -> Dict[str, Any]:
    """
    setup_test_environment 函数执行完整的测试环境设置
    包括环境检查和数据库清理

    返回:
        dict: 环境设置结果
    """
    import time
    result = {
        "timestamp": time.time(),
        "environment_check": None,
        "cleanup_result": None,
        "setup_success": False
    }

    print("=== 开始设置测试环境 ===")

    # 1. 执行环境检查
    print("\n1. 执行环境检查...")
    env_check = check_environment()
    result["environment_check"] = env_check

    # 如果环境检查失败，直接返回
    if not env_check["overall_ready"]:
        print("✗ 环境检查失败，无法继续设置测试环境")
        return result

    # 2. 清理测试数据
    print("\n2. 清理测试数据...")
    db_ops = get_db_connection()
    if db_ops is not None:
        cleanup = clean_test_collections(db_ops)
        result["cleanup_result"] = cleanup

        # 输出清理结果
        print(f"清理完成:")
        print(f"  删除文档总数: {cleanup['total_documents_removed']}")
        for collection_info in cleanup["collections_cleaned"]:
            print(f"  {collection_info['collection']}: 删除 {collection_info['documents_removed']} 个文档")

        if cleanup["errors"]:
            print("  清理过程中的错误:")
            for error in cleanup["errors"]:
                print(f"    ✗ {error}")

    # 3. 设置成功状态
    result["setup_success"] = True

    print("\n=== 测试环境设置完成 ===")
    return result


def generate_test_user_data() -> Dict[str, Any]:
    """
    generate_test_user_data 函数生成测试用户数据
    为测试流程准备标准化的用户数据

    返回:
        dict: 包含测试用户数据的字典
    """
    import time

    # 生成唯一的测试邮箱
    test_email = generate_test_email()

    # 返回测试用户数据
    return {
        "email": test_email,
        "password": "TestPass123!",  # 符合密码强度要求的测试密码
        "test_user": True,
        "generated_at": time.time()
    }


# 如果直接运行此脚本，执行环境设置
if __name__ == "__main__":
    print("执行测试环境设置...")

    # 执行环境设置
    result = setup_test_environment()

    # 记录设置结果到日志
    log_json({
        "stage": "environment_setup",
        "result": result
    })

    # 如果设置成功，生成并显示测试用户数据
    if result["setup_success"]:
        test_user = generate_test_user_data()
        print("\n测试用户数据已生成:")
        print(f"  邮箱: {test_user['email']}")
        print(f"  密码: {test_user['password']}")

        # 记录测试用户数据到日志
        log_json({
            "stage": "test_user_generated",
            "user_data": test_user
        })
