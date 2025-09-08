"""
orchestrate.py - Career Bot 系统主入口文件
职责：接收各个模块和前端的请求，中转到内部router路由处理
"""

# 从当前目录导入 router 模块的 orchestrate_entry 函数
# 作为统一的请求处理入口，所有路由逻辑都在 router 中完成
from orchestrate.router import orchestrate_entry


async def run(request):
    """
    模块统一入口函数，供外部系统调用
    纯粹的中转职责，直接将请求转发给 router 路由处理

    参数：
        request: 包含intent和其他数据的请求字典

    返回：
        响应结果字典
    """
    # 从 request 中提取 intent 和其他数据
    intent = request.get("intent")
    
    # 如果没有找到 intent 字段，返回错误响应
    if not intent:
        return {
            "error": "Missing intent in request",
            "status": "invalid_request"
        }
    
    # 创建 request_body，移除 intent 字段，保留其他数据
    request_body = {k: v for k, v in request.items() if k != "intent"}
    
    # 通过 orchestrate_entry 函数处理请求
    # 传入 intent 和 request_body 参数到路由处理器
    # await 等待异步执行完成后返回结果作为函数返回值
    return await orchestrate_entry(intent, request_body)
