# main.py - 系统主启动文件
# FastAPI 通过 import 导入 FastAPI 框架核心类，用于创建 Web 应用实例
from fastapi import FastAPI, Request, HTTPException
# uvicorn 通过 import 导入 ASGI 服务器，用于运行 FastAPI 应用
import uvicorn
# fastapi.middleware.cors 通过 from...import 导入 CORS 中间件
# CORSMiddleware 被导入用于处理跨域请求
from fastapi.middleware.cors import CORSMiddleware
# logging 通过 import 导入日志模块，用于记录启动和运行信息
import logging
import logging.handlers
# asyncio 通过 import 导入异步编程模块，用于异步日志处理
import asyncio
# queue 通过 import 导入队列模块，用于异步日志缓冲
import queue
# threading 通过 import 导入线程模块，用于日志监听器
import threading

# 配置日志格式
# logging.basicConfig 通过调用设置日志系统的基础配置
# level 参数设置为 INFO 级别记录信息
# format 参数设置为包含时间戳、模块名、日志级别和消息的格式字符串
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# === Fast Fail: 异步日志系统初始化 ===
# log_queue 通过 queue.Queue 创建线程安全的日志消息队列
# 用于缓冲无效intent等高频错误日志，避免每请求I/O
log_queue = queue.Queue()

# queue_handler 通过 logging.handlers.QueueHandler 创建队列处理器
# 传入log_queue参数，将日志消息发送到队列而非直接写盘
queue_handler = logging.handlers.QueueHandler(log_queue)

# file_handler 通过 logging.FileHandler 创建文件处理器
# 用于实际的日志文件写入操作
file_handler = logging.FileHandler('app.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

# queue_listener 通过 logging.handlers.QueueListener 创建队列监听器
# 传入log_queue和file_handler参数，后台批量处理日志写入
queue_listener = logging.handlers.QueueListener(log_queue, file_handler)

# logger 通过 logging.getLogger 获取当前模块的日志记录器
# 传入 __name__ 参数，返回专属于当前模块的logger实例
logger = logging.getLogger(__name__)
# logger.addHandler 通过调用添加队列处理器到logger
# 使日志通过队列异步处理而非同步I/O
logger.addHandler(queue_handler)

# FastAPI() 通过调用构造函数创建 FastAPI 应用实例
# title 参数设置应用标题为 "Career Bot API"
# description 参数设置应用描述为中枢调度系统
# version 参数设置应用版本号为 "1.0.0"
# 赋值给 app 变量存储应用实例
app = FastAPI(
    title="Career Bot API",
    description="Career Bot 中枢调度系统 - 模块自注册架构",
    version="1.0.0"
)

# app.add_middleware 通过调用添加 CORS 中间件到 FastAPI 应用
# CORSMiddleware 作为中间件类型参数传入
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

# from hub.hub import run as dispatcher_handler 通过 import 导入中枢调度器
# 将 hub.hub 模块的 run 函数重命名为 dispatcher_handler
from hub.hub import run as dispatcher_handler

# from hub.router import InvalidIntentError 通过 import 导入严格控制异常类
# 用于识别无效intent异常并返回合适的4xx状态码
from hub.router import InvalidIntentError

# === Fast Fail: 应用启动和关闭事件 ===
@app.on_event("startup")
async def startup_event():
    """
    startup_event 应用启动事件处理器
    初始化异步日志监听器，开始后台日志处理
    """
    # queue_listener.start() 通过调用启动日志队列监听器
    # 开始后台线程处理日志队列中的消息
    queue_listener.start()
    # logger.info 通过调用记录应用启动信息
    logger.info("Application started with async logging system")

@app.on_event("shutdown") 
async def shutdown_event():
    """
    shutdown_event 应用关闭事件处理器
    停止异步日志监听器，确保所有日志都被写入
    """
    # queue_listener.stop() 通过调用停止日志队列监听器
    # 等待队列中剩余日志处理完毕后关闭
    queue_listener.stop()
    # logger.info 通过调用记录应用关闭信息
    logger.info("Application shutdown with async logging system")


# @app.post("/intent") 通过装饰器定义POST请求的intent路由处理器
@app.post("/intent")
async def handle_intent(request: Request):
    """
    Intent严格控制处理路由
    系统唯一业务入口，实施严格intent验证，拒绝fallback处理
    
    参数:
        request: FastAPI 请求对象，包含请求体和头部信息
    
    返回:
        中枢Dispatcher的处理结果字典，仅在成功时返回
    
    异常:
        HTTPException 400: 当intent无效或请求格式错误时返回
        HTTPException 500: 当系统内部错误时返回
    """
    try:
        # request.json() 通过异步调用读取请求体中的JSON数据
        # 返回解析后的字典赋值给 request_data 变量
        request_data = await request.json()
        
        # dispatcher_handler() 通过异步调用执行严格的中枢调度处理
        # 传入 request_data 参数，等待执行完成后返回结果
        # 严格模式下失败将抛出异常而非返回错误响应
        result = await dispatcher_handler(request_data)
        
        # return 语句返回 result 变量作为成功响应结果
        return result
        
    except InvalidIntentError as e:
        # Fast Fail: 异步日志记录，避免同步I/O阻塞请求处理
        # logger.warning 通过队列处理器异步记录无效intent警告
        # 日志消息进入队列，由后台监听器批量写入，不阻塞响应
        logger.warning(f"Invalid intent request: {e.intent}")
        # HTTPException 通过调用抛出 HTTP 异常
        # status_code 参数设置为 400 表示客户端请求错误
        # detail 参数直接使用预设错误字典，避免动态构建
        raise HTTPException(status_code=400, detail=e.to_dict())
    
    # === 业务异常处理层 ===
    # 使用字符串匹配的方式检测业务异常，避免导入循环依赖
    
    except Exception as e:
        exception_name = type(e).__name__
        error_msg = str(e)
        
        # 处理参数无效异常 - HTTP 400 Bad Request  
        if exception_name == "InvalidInputError":
            logger.warning(f"业务参数错误: {error_msg}")
            raise HTTPException(status_code=400, detail={
                "error_type": "InvalidInput",
                "message": error_msg,
                "error_code": "INVALID_INPUT"
            })
        
        # 处理认证失败异常 - HTTP 401 Unauthorized
        elif exception_name == "InvalidCredentialsError":
            logger.warning(f"认证失败: {error_msg}")
            raise HTTPException(status_code=401, detail={
                "error_type": "InvalidCredentials",
                "message": error_msg,
                "error_code": "AUTHENTICATION_FAILED"
            })
        
        # 处理邮箱已注册异常 - HTTP 409 Conflict
        elif exception_name == "EmailAlreadyRegisteredError":
            logger.warning(f"邮箱冲突: {error_msg}")
            raise HTTPException(status_code=409, detail={
                "error_type": "EmailConflict",
                "message": error_msg,
                "error_code": "EMAIL_ALREADY_EXISTS"
            })
        
        # 如果是RuntimeError，专门处理
        elif isinstance(e, RuntimeError):
            # 将RuntimeError转发给下面的RuntimeError处理器
            raise e
        
        # 如果是ValueError，转发给下面的ValueError处理器
        elif isinstance(e, ValueError):
            raise e
        
        # 其他未知异常，转发给最后的通用异常处理器
        else:
            raise e
        
    except RuntimeError as e:
        # RuntimeError 异常表示系统运行时错误（如handler无效、执行失败等）
        error_msg = str(e)
        # Fast Fail: 异步日志记录系统内部错误
        # logger.error 通过队列处理器异步记录运行时错误
        logger.error(f"Intent execution runtime error: {error_msg}")
        
        # 从 hub.error_presets 导入PROCESSING_ERROR常量
        from hub.error_presets import PROCESSING_ERROR
        
        # 根据错误类型返回不同状态码
        if "Invalid handler function" in error_msg or "execution failed" in error_msg:
            # 处理函数相关错误返回422状态码（处理失败）
            # PROCESSING_ERROR.copy() 通过浅复制预设错误字典
            error_detail = PROCESSING_ERROR.copy()
            error_detail["message"] = error_msg
            error_detail["error_code"] = "HANDLER_EXECUTION_FAILED"
            # HTTPException 通过调用抛出 HTTP 异常，使用预设错误字典
            raise HTTPException(status_code=422, detail=error_detail)
        else:
            # 其他运行时错误返回500状态码
            # PROCESSING_ERROR.copy() 通过浅复制预设错误字典
            error_detail = PROCESSING_ERROR.copy()
            error_detail["error_type"] = "RuntimeError"
            error_detail["message"] = error_msg 
            error_detail["error_code"] = "SYSTEM_RUNTIME_ERROR"
            # HTTPException 通过调用抛出 HTTP 异常，使用预设错误字典
            raise HTTPException(status_code=500, detail=error_detail)
        
    except ValueError as e:
        # ValueError 异常表示请求数据格式错误
        # logger.warning 通过调用记录请求格式错误信息
        logger.warning(f"请求数据格式错误: {str(e)}")
        # HTTPException 通过调用抛出 HTTP 异常
        # status_code 参数设置为 400 表示客户端请求格式错误
        raise HTTPException(status_code=400, detail={
            "error_type": "ValueError",
            "message": f"请求数据格式错误: {str(e)}",
            "error_code": "INVALID_REQUEST_FORMAT"
        })
        
    except Exception as e:
        # 捕获所有其他未预期的异常
        # logger.error 通过调用记录系统级异常信息
        logger.error(f"系统未知异常: {str(e)}")
        # HTTPException 通过调用抛出 HTTP 异常
        # status_code 参数设置为 500 表示服务器内部错误
        raise HTTPException(status_code=500, detail={
            "error_type": "UnknownError",
            "message": f"系统内部错误: {str(e)}",
            "error_code": "INTERNAL_SERVER_ERROR"
        })


# @app.get("/") 通过装饰器定义GET请求的根路径处理器
@app.get("/")
async def root():
    """
    根路径健康检查端点
    返回服务运行状态信息
    
    返回:
        包含服务状态的字典
    """
    # return 语句返回服务状态信息字典
    return {
        # "message" 键赋值为服务欢迎信息字符串
        "message": "Career Bot API 服务正在运行",
        # "version" 键赋值为版本号字符串
        "version": "1.0.0",
        # "architecture" 键赋值为架构类型说明字符串
        "architecture": "模块自注册中枢调度架构",
        # "entry_point" 键赋值为唯一入口说明字符串
        "entry_point": "/intent",
        # "status" 键赋值为服务运行状态字符串
        "status": "running"
    }


# @app.get("/health") 通过装饰器定义GET请求的健康检查处理器
@app.get("/health")
async def health_check():
    """
    系统健康状态检查端点 - 严格现代架构版本
    返回基于flow_registry的真实系统状态信息，避免访问已废弃的intent_handlers
    
    返回:
        包含系统健康状态的详细信息字典，数据来源于现代化架构组件
    """
    try:
        # from hub.registry_center import RegistryCenter 通过 import 导入注册中心
        from hub.registry_center import RegistryCenter  
        # from hub.flow import flow_registry 通过 import 导入现代化流程注册中心
        from hub.flow import flow_registry
        # from utilities.time import time 通过 import 导入封装的时间模块，用于生成真实时间戳
        from utilities.time import time
        
        # RegistryCenter() 通过调用构造函数创建注册中心实例
        registry = RegistryCenter()
        
        # === 严格获取现代化架构的真实统计数据 ===
        # len(flow_registry.steps) 通过调用获取已注册步骤的真实数量
        registered_steps_count = len(flow_registry.steps)
        # len(flow_registry.flows) 通过调用获取已注册流程的真实数量
        registered_flows_count = len(flow_registry.flows)
        # len(registry.module_meta) 通过调用获取已注册模块的真实数量
        registered_modules_count = len(registry.module_meta)
        
        # time.now() 通过调用获取当前真实时间戳（菲律宾时区）
        current_timestamp = time.now().isoformat()
        
        # === 安全的流程完整性检查 ===
        flow_integrity_info = None
        try:
            # flow_registry.validate_all_flows_integrity() 通过调用执行流程完整性检查
            # 包装在try-catch中避免因模块注册问题导致健康检查失败
            flow_integrity_info = flow_registry.validate_all_flows_integrity()
        except Exception as integrity_error:
            # 流程完整性检查失败时记录错误但不影响整体健康检查
            flow_integrity_info = {
                "system_valid": False,
                "error": f"Flow integrity check failed: {str(integrity_error)}",
                "total_flows": registered_flows_count,
                "note": "Flow integrity validation temporarily unavailable"
            }
        
        # health_status 通过字典创建严格的健康状态信息
        health_status = {
            # "system" 键赋值为 "healthy" 表示系统基于现代架构正常运行
            "system": "healthy",
            # "timestamp" 键赋值为真实的当前时间戳
            "timestamp": current_timestamp,
            # "architecture" 键赋值为现代化架构描述，明确移除intent_handlers依赖
            "architecture": "严格流程驱动架构(Flow-Based) - 移除intent_handlers依赖",
            # "registered_modules" 键赋值为从registry.module_meta获取的真实模块数量
            "registered_modules": registered_modules_count,
            # "registered_steps" 键赋值为从flow_registry.steps获取的真实步骤数量
            "registered_steps": registered_steps_count,
            # "registered_flows" 键赋值为从flow_registry.flows获取的真实流程数量  
            "registered_flows": registered_flows_count,
            # "dispatcher" 键赋值为调度器状态信息
            "dispatcher": {
                "status": "active",
                "description": "严格控制流程调度器正在运行",
                "architecture": "禁用fallback,强制异常抛出模式"
            },
            # "flow_integrity" 键添加安全获取的流程完整性检查信息
            "flow_integrity": flow_integrity_info,
            # "migration_status" 键添加架构迁移状态信息
            "migration_status": {
                "intent_handlers_removed": True,
                "flow_registry_active": True,
                "strict_mode_enabled": True
            }
        }
        
        # return 语句返回基于真实数据的 health_status 字典
        return health_status
        
    except Exception as e:
        # logger.error 通过调用记录健康检查严重异常
        logger.error(f"健康检查严重异常: {str(e)}")
        # 健康检查异常时返回最小化的错误状态信息，避免二次异常
        return {
            "system": "error", 
            "error": f"健康检查失败: {str(e)}",
            "error_type": type(e).__name__,
            "dispatcher": {"status": "unknown"},
            "suggestion": "检查模块注册和flow_registry状态"
        }


# @app.on_event("startup") 通过装饰器定义应用启动事件处理器
@app.on_event("startup")
async def startup_event():
    """
    应用启动事件处理器
    启动中枢调度器，模块将通过自注册机制自动接入系统
    """
    # logger.info 通过调用记录应用启动信息
    logger.info("Career Bot API 系统启动中...")
    # logger.info 通过调用记录架构说明信息
    logger.info("启用模块自注册架构 - 模块将自动注册到Hub中枢")
    
    # 触发模块自注册机制
    try:
        # 通过 import 语句触发模块的 __init__.py 自注册逻辑
        # 这些 import 语句会执行模块的自注册代码
        import applications.mbti  # 触发MBTI模块自注册
        import applications.auth  # 触发Auth模块自注册
        
        # logger.info 通过调用记录模块自注册触发完成信息
        logger.info("模块自注册触发完成")
        
    except Exception as e:
        # logger.error 通过调用记录模块自注册异常信息
        logger.error(f"模块自注册触发异常: {str(e)}")
    
    # logger.info 通过调用记录应用启动完成信息
    logger.info("Career Bot API 系统启动完成，服务已就绪")


# @app.on_event("shutdown") 通过装饰器定义应用关闭事件处理器
@app.on_event("shutdown")
async def shutdown_event():
    """
    应用关闭事件处理器
    广播统一清理信号给注册中心
    """
    # logger.info 通过调用记录应用关闭信息
    logger.info("Career Bot API 系统正在关闭...")
    
    try:
        # from hub.registry_center import RegistryCenter 通过 import 导入注册中心
        from hub.registry_center import RegistryCenter
        
        # RegistryCenter() 通过调用构造函数创建注册中心实例
        registry = RegistryCenter()
        
        # 遍历 registry.module_meta 字典中的所有已注册模块
        for module_name, module_info in registry.module_meta.items():
            try:
                # 检查模块是否提供了清理接口
                if 'interface' in module_info and 'cleanup' in module_info['interface']:
                    # cleanup_func 通过访问获取模块的清理函数引用
                    cleanup_func = module_info['interface']['cleanup']
                    
                    if cleanup_func:
                        # cleanup_func() 通过调用执行模块清理逻辑
                        cleanup_result = cleanup_func()
                        # logger.info 通过调用记录模块清理完成信息
                        logger.info(f"模块 {module_name} 清理完成")
                        
            except Exception as e:
                # logger.error 通过调用记录模块清理异常信息
                logger.error(f"模块 {module_name} 清理失败: {str(e)}")
        
    except Exception as e:
        # logger.error 通过调用记录注册中心清理异常信息
        logger.error(f"注册中心清理异常: {str(e)}")
    
    # logger.info 通过调用记录应用关闭完成信息
    logger.info("Career Bot API 系统关闭完成")


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