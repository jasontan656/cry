"""
MBTI性格测试中心模块主入口
职责：接收hub请求，中转到内部router处理
"""

# from 语句通过 flow_router 模块名导入 process_with_flow_context 函数
# 使用绝对导入方式，支持测试环境和独立运行环境
from applications.mbti.flow_router import process_with_flow_context


async def run(request):
    """
    模块统一入口函数，供hub调用
    参数：任意请求对象（中转不做类型检查）
    返回：响应结果
    """
    # 从request中提取intent参数进行流程驱动路由
    intent = request.get("intent", "mbti_step1")
    return await process_with_flow_context(intent, request)  # 中转到流程驱动路由处理器

