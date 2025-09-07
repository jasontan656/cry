# __init__.py - MBTI模块热插拔接口定义
from .mbti import run as execute  # 执行接口，统一入口函数
from .schemas import (  # 字段定义和数据结构
    FIELD_DEFINITIONS,  # 字段规范定义
    schema_manager,     # 字段管理器实例
    get_field_types,    # 字段类型获取接口
    get_field_groups,   # 字段分组获取接口
    get_valid_steps     # 有效步骤获取接口
)
from .router import router, process_mbti_request  # 路由能力和编排接口

# 模块元信息（热插拔必需）
MODULE_INFO = {
    "name": "mbti",  # 模块名称标识
    "version": "1.0.0",    # 版本号
    "description": "MBTI性格测试中心模块",  # 模块功能描述
    "interface": {  # 对外暴露的接口
        "execute": execute,  # 统一执行接口
        "validate": None,    # 数据验证接口（暂未实现）
        "router": router,    # 路由器实例
        "process_mbti_request": process_mbti_request,  # 请求处理接口
        "schemas": {  # 数据结构定义
            "field_definitions": FIELD_DEFINITIONS,
            "schema_manager": schema_manager,
            "get_field_types": get_field_types,
            "get_field_groups": get_field_groups,
            "get_valid_steps": get_valid_steps
        }
    },
    "capabilities": {  # 模块能力声明
        "personality_test": {  # 性格测试能力
            "steps": ["step1", "step2", "step3"],  # 支持的测试步骤
            "description": "完整的MBTI三步测试流程"  # 能力描述
        },
        "mbti_analysis": {  # MBTI分析能力
            "input_types": ["user_answers", "assessment_data"],  # 支持的输入类型
            "output_types": ["mbti_result", "assessment_report"]  # 支持的输出类型
        }
    },
    "orchestrate_info": {  # 编排信息
        "supported_intents": ["mbti_test", "mbti_analyze", "mbti_*"],  # 支持的意图模式
        "step_flow": {  # 步骤流程定义
            "step1": {"next": "step2", "description": "初始MBTI测试题"},
            "step2": {"next": "step3", "description": "反向问题生成"},
            "step3": {"next": None, "description": "最终结果评估"}
        },
        "data_flow": {  # 数据流转定义
            "input_validation": "validator.validate_request_data",  # 输入验证
            "step_orchestrate": "router.process",  # 步骤编排
            "result_storage": "orchestrate.database",  # 结果存储
            "frontend_response": "orchestrate.entry"  # 前端响应
        }
    },
    "dependencies": [],  # 依赖的其他模块
    "metadata": {  # 模块元数据
        "author": "Career Bot Team",  # 开发团队
        "created": "2024-09-05",      # 创建日期
        "last_modified": "2024-09-05", # 最后修改日期
        "compatibility": "orchestrate v1.0+",  # 兼容性要求
        "license": "Internal Use Only"  # 使用许可
    }
}

# 热插拔钩子函数
def initialize_module(config: dict = None):
    """模块初始化钩子"""
    # 初始化日志记录器
    import logging
    logger = logging.getLogger(__name__)
    logger.info("MBTI Agent模块初始化完成")

    # 初始化字段管理器
    schema_manager  # 触发字段管理器初始化

    # 返回初始化状态
    return {
        "status": "initialized",
        "capabilities": MODULE_INFO["capabilities"],
        "orchestrate_info": MODULE_INFO["orchestrate_info"]
    }

def cleanup_module():
    """模块清理钩子"""
    import logging
    logger = logging.getLogger(__name__)
    logger.info("MBTI Agent模块清理完成")
    return {"status": "cleaned"}

def get_module_info():
    """获取模块完整信息"""
    return MODULE_INFO

def get_capabilities():
    """获取模块能力列表"""
    return MODULE_INFO["capabilities"]

def get_orchestrate_info():
    """获取编排信息"""
    return MODULE_INFO["orchestrate_info"]

# 模块就绪状态标识
MODULE_READY = True
