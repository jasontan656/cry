#!/usr/bin/env python3
"""
Hub Tests HTTP Client Configuration
统一的 httpx 客户端配置工厂，解决测试层性能问题

根据《Invalid Intent Slowpath Deep Dive Analysis》报告修复：
- DNS 解析延迟问题：使用 127.0.0.1 替代 localhost
- 连接池初始化开销：复用客户端实例，优化连接配置
- 超时策略：明确各阶段超时时间
- 环境干扰：禁用系统代理和环境变量影响
"""

import httpx
from typing import Optional
from contextlib import contextmanager, asynccontextmanager

# 强制使用 loopback IP 避免 DNS 解析延迟
BASE_URL = "http://127.0.0.1:8000"

# 全局客户端实例（类级单例）
_sync_client: Optional[httpx.Client] = None
_async_client: Optional[httpx.AsyncClient] = None


def get_sync_client() -> httpx.Client:
    """
    获取统一配置的同步 httpx 客户端
    
    配置要点：
    - base_url: 强制直连 loopback，避免 localhost DNS 干扰
    - timeout: 分段超时配置，避免默认超时策略问题
    - limits: 优化连接池，减少连接建立开销
    - trust_env: 禁用系统代理/环境变量影响
    - transport: 禁用 HTTP/2，强制 HTTP/1.1，禁用重试
    
    Returns:
        配置优化的 httpx.Client 实例
    """
    global _sync_client
    if _sync_client is None:
        _sync_client = httpx.Client(
            base_url=BASE_URL,
            timeout=httpx.Timeout(
                connect=1.0,    # 连接超时 1s
                read=4.0,       # 读取超时 4s
                write=4.0,      # 写入超时 4s
                pool=4.0        # 连接池超时 4s
            ),
            limits=httpx.Limits(
                max_keepalive_connections=20,  # 保持连接数
                max_connections=50             # 最大连接数
            ),
            trust_env=False,  # 禁用系统代理/环境变量影响
            transport=httpx.HTTPTransport(
                http1=True,    # 强制 HTTP/1.1
                http2=False,   # 禁用 HTTP/2
                retries=0      # 禁用重试
            )
        )
    return _sync_client


def get_async_client() -> httpx.AsyncClient:
    """
    获取统一配置的异步 httpx 客户端
    
    配置要点同 get_sync_client()，但使用 AsyncHTTPTransport
    
    Returns:
        配置优化的 httpx.AsyncClient 实例
    """
    global _async_client
    if _async_client is None:
        _async_client = httpx.AsyncClient(
            base_url=BASE_URL,
            timeout=httpx.Timeout(
                connect=1.0,
                read=4.0,
                write=4.0,
                pool=4.0
            ),
            limits=httpx.Limits(
                max_keepalive_connections=20,
                max_connections=50
            ),
            trust_env=False,
            transport=httpx.AsyncHTTPTransport(
                http1=True,
                http2=False,
                retries=0
            )
        )
    return _async_client


@contextmanager
def sync_client_context():
    """
    同步客户端上下文管理器
    确保客户端在测试类生命周期内复用
    """
    client = get_sync_client()
    try:
        yield client
    finally:
        # 不在这里关闭，保持复用
        pass


@asynccontextmanager
async def async_client_context():
    """
    异步客户端上下文管理器
    确保客户端在测试类生命周期内复用
    """
    client = get_async_client()
    try:
        yield client
    finally:
        # 不在这里关闭，保持复用
        pass


def close_all_clients():
    """
    关闭所有全局客户端实例
    在测试套件结束时调用
    """
    global _sync_client, _async_client
    
    if _sync_client:
        _sync_client.close()
        _sync_client = None
    
    if _async_client:
        import asyncio
        try:
            # 如果在异步环境中，异步关闭
            loop = asyncio.get_running_loop()
            loop.create_task(_async_client.aclose())
        except RuntimeError:
            # 如果不在异步环境中，创建新事件循环
            asyncio.run(_async_client.aclose())
        _async_client = None


def safe_request_with_timeout_details(client: httpx.Client, method: str, url: str, **kwargs):
    """
    带详细超时错误处理的安全请求函数
    
    Args:
        client: httpx.Client 实例
        method: HTTP 方法
        url: 请求 URL
        **kwargs: 其他请求参数
        
    Returns:
        tuple: (response, error_details)
        response: httpx.Response 对象或 None
        error_details: 错误详情字典或 None
    """
    try:
        response = client.request(method, url, **kwargs)
        return response, None
    except httpx.TimeoutException as e:
        # 分析具体的超时类型
        timeout_type = "unknown"
        if hasattr(e, '__context__') and e.__context__:
            context_type = type(e.__context__).__name__
            if "connect" in context_type.lower():
                timeout_type = "connect"
            elif "read" in context_type.lower():
                timeout_type = "read"
            elif "write" in context_type.lower():
                timeout_type = "write"
            elif "pool" in context_type.lower():
                timeout_type = "pool"
        
        error_details = {
            "error_type": "timeout",
            "timeout_phase": timeout_type,
            "message": str(e),
            "url": url,
            "method": method
        }
        return None, error_details
    except httpx.ConnectError as e:
        error_details = {
            "error_type": "connect",
            "timeout_phase": "connect",
            "message": str(e),
            "url": url,
            "method": method
        }
        return None, error_details
    except Exception as e:
        error_details = {
            "error_type": type(e).__name__,
            "timeout_phase": "unknown",
            "message": str(e),
            "url": url,
            "method": method
        }
        return None, error_details


async def safe_async_request_with_timeout_details(client: httpx.AsyncClient, method: str, url: str, **kwargs):
    """
    异步版本的带详细超时错误处理的安全请求函数
    """
    try:
        response = await client.request(method, url, **kwargs)
        return response, None
    except httpx.TimeoutException as e:
        timeout_type = "unknown"
        if hasattr(e, '__context__') and e.__context__:
            context_type = type(e.__context__).__name__
            if "connect" in context_type.lower():
                timeout_type = "connect"
            elif "read" in context_type.lower():
                timeout_type = "read"
            elif "write" in context_type.lower():
                timeout_type = "write"
            elif "pool" in context_type.lower():
                timeout_type = "pool"
        
        error_details = {
            "error_type": "timeout", 
            "timeout_phase": timeout_type,
            "message": str(e),
            "url": url,
            "method": method
        }
        return None, error_details
    except httpx.ConnectError as e:
        error_details = {
            "error_type": "connect",
            "timeout_phase": "connect", 
            "message": str(e),
            "url": url,
            "method": method
        }
        return None, error_details
    except Exception as e:
        error_details = {
            "error_type": type(e).__name__,
            "timeout_phase": "unknown",
            "message": str(e),
            "url": url,
            "method": method
        }
        return None, error_details
