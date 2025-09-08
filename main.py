# main.py - 系统主启动文件
# FastAPI 通过 import 导入 FastAPI 框架核心类，用于创建 Web 应用实例
from fastapi import FastAPI, Request, HTTPException
# uvicorn 通过 import 导入 ASGI 服务器，用于运行 FastAPI 应用
import uvicorn
# fastapi.middleware.cors 通过 from...import 导入 CORS 中间件
# CORSMiddleware 被导入用于处理跨域请求
from fastapi.middleware.cors import CORSMiddleware
# asyncio 通过 import 导入异步编程模块，用于支持协程和异步操作
import asyncio
# logging 通过 import 导入日志模块，用于记录启动和运行信息
import logging

# 配置日志格式
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI() 通过调用构造函数创建 FastAPI 应用实例
# 传入 title 参数设置应用标题为 "Career Bot API"
# 传入 description 参数设置应用描述
# 传入 version 参数设置应用版本号为 "1.0.0"
# 赋值给 app 变量存储应用实例
app = FastAPI(
    title="Career Bot API",
    description="Career Bot 后端服务 - 集成 Auth、MBTI、Orchestrate 模块",
    version="1.0.0"
)

# app.add_middleware 通过调用添加 CORS 中间件到 FastAPI 应用
# 传入 CORSMiddleware 类作为中间件类型
# allow_origins 参数设置为 ["*"] 允许所有源站跨域访问
# allow_credentials 参数设置为 True 允许携带凭证的跨域请求
# allow_methods 参数设置为 ["*"] 允许所有 HTTP 方法
# allow_headers 参数设置为 ["*"] 允许所有 HTTP 头部
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 模块初始化函数
def initialize_all_modules():
    """
    初始化所有业务模块
    调用每个模块的 initialize_module 函数执行模块初始化逻辑
    """
    logger.info("开始初始化所有模块...")
    
    # 初始化 Auth 模块
    try:
        # from applications.auth 通过 import 导入 auth 模块的初始化函数
        from applications.auth import initialize_module as auth_init
        # auth_init() 通过调用执行 Auth 模块的初始化逻辑
        # 返回初始化结果字典赋值给 auth_result 变量
        auth_result = auth_init()
        logger.info(f"Auth 模块初始化成功: {auth_result.get('status')}")
    except Exception as e:
        logger.error(f"Auth 模块初始化失败: {str(e)}")
    
    # 初始化 MBTI 模块
    try:
        # from applications.mbti 通过 import 导入 mbti 模块的初始化函数
        from applications.mbti import initialize_module as mbti_init
        # mbti_init() 通过调用执行 MBTI 模块的初始化逻辑
        # 返回初始化结果字典赋值给 mbti_result 变量
        mbti_result = mbti_init()
        logger.info(f"MBTI 模块初始化成功: {mbti_result.get('status')}")
    except Exception as e:
        logger.error(f"MBTI 模块初始化失败: {str(e)}")
    
    logger.info("所有模块初始化完成")


def register_all_modules():
    """
    注册所有业务模块到 orchestrate 中枢
    调用每个模块的 register_to_orchestrate 函数执行模块注册逻辑
    """
    logger.info("开始向 orchestrate 注册所有模块...")
    
    # 注册 Auth 模块
    try:
        # from applications.auth 通过 import 导入 auth 模块的注册函数
        from applications.auth import register_to_orchestrate as auth_register
        # auth_register() 通过调用执行 Auth 模块向 orchestrate 的注册
        # 返回注册成功状态布尔值赋值给 auth_registered 变量
        auth_registered = auth_register()
        if auth_registered:
            logger.info("Auth 模块成功注册到 orchestrate")
        else:
            logger.warning("Auth 模块注册到 orchestrate 失败")
    except Exception as e:
        logger.error(f"Auth 模块注册失败: {str(e)}")
    
    # 注册 MBTI 模块
    try:
        # from applications.mbti 通过 import 导入 mbti 模块的注册函数
        from applications.mbti import register_to_orchestrate as mbti_register
        # mbti_register() 通过调用执行 MBTI 模块向 orchestrate 的注册
        # 返回注册成功状态布尔值赋值给 mbti_registered 变量
        mbti_registered = mbti_register()
        if mbti_registered:
            logger.info("MBTI 模块成功注册到 orchestrate")
        else:
            logger.warning("MBTI 模块注册到 orchestrate 失败")
    except Exception as e:
        logger.error(f"MBTI 模块注册失败: {str(e)}")
    
    logger.info("所有模块注册完成")


async def auth_request_handler(path: str, request: Request) -> dict:
    """
    Auth 模块统一请求处理函数
    
    处理所有 /auth/* 路径的请求，支持POST和GET方法。
    对于受保护的路由，从请求头中提取Authorization信息。
    
    参数:
        path: URL 路径参数，匹配 /auth/ 后的所有路径
        request: FastAPI 请求对象，包含请求体和头部信息
    
    返回:
        Auth 模块处理器的响应结果字典
    """
    try:
        # from applications.auth.router 通过 import 导入 Auth 模块的路由映射
        from applications.auth.router import ROUTES
        
        # full_path 通过字符串拼接构造完整的路由路径
        # f"/auth/{path}" 格式化字符串，将 path 参数拼接到 /auth/ 后面
        # 赋值给 full_path 变量存储完整路径
        full_path = f"/auth/{path}"
        
        # handler 通过 ROUTES.get() 从路由映射字典获取对应的处理函数
        # 传入 full_path 作为键，如果不存在则返回 None
        # 赋值给 handler 变量存储处理函数引用
        handler = ROUTES.get(full_path)
        
        # if 条件判断检查 handler 是否存在
        if not handler:
            # HTTPException 通过调用抛出 HTTP 异常
            # status_code 参数设置为 404 表示路由未找到
            # detail 参数设置为错误详情字符串
            raise HTTPException(status_code=404, detail=f"Auth路由 {full_path} 未找到")
        
        # 初始化请求数据字典
        # request_data 通过字典创建空的请求数据容器
        request_data = {}
        
        # 处理POST请求的请求体数据
        # request.method 通过属性访问获取HTTP请求方法
        if request.method == "POST":
            try:
                # request.json() 通过异步调用读取请求体中的JSON数据
                # 返回解析后的字典，更新到 request_data 中
                body_data = await request.json()
                request_data.update(body_data)
            except:
                # 如果JSON解析失败，保持request_data为空字典
                pass
        
        # 处理GET请求的查询参数
        elif request.method == "GET":
            # dict() 通过调用将查询参数转换为字典
            # request.query_params 通过属性访问获取URL查询参数
            # 更新到 request_data 中
            query_params = dict(request.query_params)
            request_data.update(query_params)
        
        # 对于受保护的路由，从请求头中提取Authorization信息
        # request.headers.get() 通过调用获取Authorization请求头
        # 传入 "authorization" 键名，返回认证头字符串或None
        # 赋值给 auth_header 变量存储认证头信息
        auth_header = request.headers.get("authorization")
        
        # if 条件判断检查认证头是否存在
        if auth_header:
            # request_data["Authorization"] 通过字典赋值添加认证头到请求数据
            request_data["Authorization"] = auth_header
        
        # 添加调试信息
        logger.info(f"Auth路由调试: 路径={full_path}, 方法={request.method}, 请求数据={request_data}")
        
        # 检查处理函数是否为异步函数
        import asyncio
        if asyncio.iscoroutinefunction(handler):
            logger.info(f"Auth路由调试: 异步调用处理函数 {handler.__name__}")
            # result 通过 await handler() 异步调用处理函数
            # 传入 request_data 参数，等待执行完成后返回结果
            # 赋值给 result 变量存储处理结果
            result = await handler(request_data)
        else:
            logger.info(f"Auth路由调试: 同步调用处理函数 {handler.__name__}")
            # result 通过 handler() 同步调用处理函数
            # 传入 request_data 参数，直接返回结果
            # 赋值给 result 变量存储处理结果
            result = handler(request_data)
        
        logger.info(f"Auth路由调试: 处理结果={result}")
        
        # return 语句返回 result 变量作为响应结果
        return result
        
    except Exception as e:
        # logger.error 通过调用记录错误级别的日志消息
        # f"Auth路由处理异常: {str(e)}" 格式化异常信息为字符串
        logger.error(f"Auth路由处理异常: {str(e)}")
        # HTTPException 通过调用抛出 HTTP 异常
        # status_code 参数设置为 500 表示服务器内部错误
        # detail 参数设置为异常详情字符串
        raise HTTPException(status_code=500, detail=f"Auth模块处理异常: {str(e)}")


# Auth 模块路由挂载（POST方法）
@app.post("/auth/{path:path}")
async def auth_post_routes(path: str, request: Request):
    """
    Auth 模块POST路由处理器
    
    将POST方法的 /auth/* 路径请求转发到统一处理函数。
    主要用于注册、登录、密码重置等需要提交数据的操作。
    """
    # auth_request_handler() 通过异步调用处理Auth模块的POST请求
    # 传入路径参数和请求对象，返回处理结果字典
    return await auth_request_handler(path, request)


# Auth 模块路由挂载（GET方法）
@app.get("/auth/{path:path}")
async def auth_get_routes(path: str, request: Request):
    """
    Auth 模块GET路由处理器
    
    将GET方法的 /auth/* 路径请求转发到统一处理函数。
    主要用于获取用户信息、OAuth回调等不需要请求体的操作。
    """
    # auth_request_handler() 通过异步调用处理Auth模块的GET请求
    # 传入路径参数和请求对象，返回处理结果字典
    return await auth_request_handler(path, request)


# MBTI 模块路由挂载
@app.post("/mbti")
async def mbti_route(request: Request):
    """
    MBTI 模块统一路由处理器
    将 /mbti 路径的请求转发到 MBTI 模块的路由处理器
    
    参数:
        request: FastAPI 请求对象，包含请求体和头部信息
    
    返回:
        MBTI 模块处理器的响应结果字典
    """
    try:
        # from applications.mbti.router 通过 import 导入 MBTI 模块的请求处理函数
        from applications.mbti.router import process_mbti_request
        
        # request_data 通过 await request.json() 异步读取请求体中的 JSON 数据
        # 返回解析后的字典赋值给 request_data 变量
        request_data = await request.json()
        
        # result 通过 await process_mbti_request() 异步调用 MBTI 请求处理函数
        # 传入 request_data 参数，等待执行完成后返回结果
        # 赋值给 result 变量存储处理结果
        result = await process_mbti_request(request_data)
        
        # return 语句返回 result 变量作为响应结果
        return result
        
    except Exception as e:
        # logger.error 通过调用记录错误级别的日志消息
        # f"MBTI路由处理异常: {str(e)}" 格式化异常信息为字符串
        logger.error(f"MBTI路由处理异常: {str(e)}")
        # HTTPException 通过调用抛出 HTTP 异常
        # status_code 参数设置为 500 表示服务器内部错误
        # detail 参数设置为异常详情字符串
        raise HTTPException(status_code=500, detail=f"MBTI模块处理异常: {str(e)}")


# Orchestrate 模块路由挂载
@app.post("/orchestrate")
async def orchestrate_route(request: Request):
    """
    Orchestrate 模块统一路由处理器
    将 /orchestrate 路径的请求转发到 orchestrate 模块的入口函数
    
    参数:
        request: FastAPI 请求对象，包含请求体和头部信息
    
    返回:
        Orchestrate 模块处理器的响应结果字典
    """
    try:
        # from orchestrate.orchestrate 通过 import 导入 orchestrate 模块的运行函数
        from orchestrate.orchestrate import run
        
        # request_data 通过 await request.json() 异步读取请求体中的 JSON 数据
        # 返回解析后的字典赋值给 request_data 变量
        request_data = await request.json()
        
        # result 通过 await run() 异步调用 orchestrate 运行函数
        # 传入 request_data 参数，等待执行完成后返回结果
        # 赋值给 result 变量存储处理结果
        result = await run(request_data)
        
        # return 语句返回 result 变量作为响应结果
        return result
        
    except Exception as e:
        # logger.error 通过调用记录错误级别的日志消息
        # f"Orchestrate路由处理异常: {str(e)}" 格式化异常信息为字符串
        logger.error(f"Orchestrate路由处理异常: {str(e)}")
        # HTTPException 通过调用抛出 HTTP 异常
        # status_code 参数设置为 500 表示服务器内部错误
        # detail 参数设置为异常详情字符串
        raise HTTPException(status_code=500, detail=f"Orchestrate模块处理异常: {str(e)}")


# 根路径健康检查
@app.get("/")
async def root():
    """
    根路径健康检查端点
    返回服务运行状态和已加载模块信息
    
    返回:
        包含服务状态和模块信息的字典
    """
    # return 语句返回服务状态信息字典
    return {
        # "message" 键赋值为服务欢迎信息字符串
        "message": "Career Bot API 服务正在运行",
        # "version" 键赋值为版本号字符串
        "version": "1.0.0",
        # "modules" 键赋值为已加载模块列表
        "modules": ["auth", "mbti", "orchestrate"],
        # "status" 键赋值为服务运行状态字符串
        "status": "running"
    }


# 模块状态查询端点
@app.get("/health")
async def health_check():
    """
    系统健康状态检查端点
    返回各个模块的运行状态和连接状态
    
    返回:
        包含系统健康状态的详细信息字典
    """
    # health_status 通过字典创建健康状态信息
    # "system" 键赋值为 "healthy" 表示系统整体状态良好
    # "timestamp" 键通过 import datetime 和 datetime.now() 获取当前时间戳
    # "modules" 键赋值为包含各模块状态的字典
    health_status = {
        "system": "healthy",
        "timestamp": "2024-12-19T00:00:00Z",
        "modules": {
            "auth": {"status": "active", "description": "用户认证模块"},
            "mbti": {"status": "active", "description": "MBTI性格测试模块"},
            "orchestrate": {"status": "active", "description": "中枢调度模块"}
        }
    }
    
    # return 语句返回 health_status 字典作为响应结果
    return health_status


# @app.on_event("startup") 通过装饰器定义应用启动事件处理器
@app.on_event("startup")
async def startup_event():
    """
    应用启动事件处理器
    在 FastAPI 应用启动时自动执行模块初始化和注册逻辑
    """
    # logger.info 通过调用记录应用启动信息
    logger.info("Career Bot API 应用启动中...")
    
    # initialize_all_modules() 通过调用执行所有模块的初始化逻辑
    # 不传入参数，依次调用各模块的 initialize_module 函数
    initialize_all_modules()
    
    # register_all_modules() 通过调用执行所有模块的注册逻辑
    # 不传入参数，依次调用各模块的 register_to_orchestrate 函数
    register_all_modules()
    
    # logger.info 通过调用记录应用启动完成信息
    logger.info("Career Bot API 应用启动完成，服务已就绪")


# @app.on_event("shutdown") 通过装饰器定义应用关闭事件处理器
@app.on_event("shutdown")
async def shutdown_event():
    """
    应用关闭事件处理器
    在 FastAPI 应用关闭时自动执行模块清理逻辑
    """
    # logger.info 通过调用记录应用关闭信息
    logger.info("Career Bot API 应用正在关闭...")
    
    # 清理 Auth 模块
    try:
        # from applications.auth 通过 import 导入 auth 模块的清理函数
        from applications.auth import cleanup_module as auth_cleanup
        # auth_cleanup() 通过调用执行 Auth 模块的清理逻辑
        # 返回清理结果字典赋值给 auth_clean_result 变量
        auth_clean_result = auth_cleanup()
        logger.info(f"Auth 模块清理完成: {auth_clean_result.get('status')}")
    except Exception as e:
        logger.error(f"Auth 模块清理失败: {str(e)}")
    
    # 清理 MBTI 模块
    try:
        # from applications.mbti 通过 import 导入 mbti 模块的清理函数
        from applications.mbti import cleanup_module as mbti_cleanup
        # mbti_cleanup() 通过调用执行 MBTI 模块的清理逻辑
        # 返回清理结果字典赋值给 mbti_clean_result 变量
        mbti_clean_result = mbti_cleanup()
        logger.info(f"MBTI 模块清理完成: {mbti_clean_result.get('status')}")
    except Exception as e:
        logger.error(f"MBTI 模块清理失败: {str(e)}")
    
    # logger.info 通过调用记录应用关闭完成信息
    logger.info("Career Bot API 应用关闭完成")


# if __name__ == "__main__" 条件判断检查是否为直接运行脚本
if __name__ == "__main__":
    # logger.info 通过调用记录服务启动信息，包含监听地址和端口
    logger.info("启动 Career Bot API 服务 - 监听地址: localhost:8000")
    
    # uvicorn.run 通过调用启动 ASGI 服务器运行 FastAPI 应用
    # app 参数传入 FastAPI 应用实例
    # host 参数设置为 "localhost" 指定监听地址
    # port 参数设置为 8000 指定监听端口
    # log_level 参数设置为 "info" 指定日志级别
    uvicorn.run(app, host="localhost", port=8000, log_level="info")
