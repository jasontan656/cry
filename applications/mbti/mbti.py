"""
MBTI性格测试中心模块主入口
职责：接收orchestrate请求，中转到内部router处理
"""

# from 语句通过 router 模块名导入 process_mbti_request 函数
# 使用绝对导入方式，支持测试环境和独立运行环境
from applications.mbti.router import process_mbti_request


async def run(request):
    """
    模块统一入口函数，供orchestrate调用
    参数：任意请求对象（中转不做类型检查）
    返回：响应结果
    """
    return await process_mbti_request(request)  # 中转到内部路由处理器

