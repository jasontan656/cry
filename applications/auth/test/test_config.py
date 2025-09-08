# API 测试配置文件
# 定义测试环境的基础配置和工具函数

import requests
import json
from typing import Dict, Any

# 测试服务器基础URL配置
# BASE_URL 设置为本地开发服务器地址
BASE_URL = "http://localhost:8000"

# 测试用邮箱前缀，避免与生产环境冲突
TEST_EMAIL_PREFIX = "test+"

# 请求超时时间设置为30秒
REQUEST_TIMEOUT = 30


class TestClient:
    """
    测试客户端类，封装HTTP请求功能
    
    提供统一的API请求接口，包含错误处理和响应格式化。
    模拟真实用户的HTTP请求行为。
    """
    
    def __init__(self, base_url: str = BASE_URL):
        # base_url 通过构造函数参数设置API服务器地址
        self.base_url = base_url
        # session 通过 requests.Session() 创建会话对象
        # 用于保持连接复用和cookie状态
        self.session = requests.Session()
        
        # 设置默认请求头，指定内容类型为JSON
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    
    def post(self, endpoint: str, data: Dict[Any, Any] = None) -> Dict[Any, Any]:
        """
        发送POST请求
        
        将endpoint与base_url拼接成完整URL，
        将data字典序列化为JSON格式发送请求，
        返回解析后的响应数据字典。
        
        参数:
            endpoint: API路径，如 "/auth/login"
            data: 请求体数据字典
            
        返回:
            Dict: 响应数据字典，包含status_code和parsed_response
        """
        # url 通过 self.base_url 和 endpoint 拼接成完整请求地址
        url = f"{self.base_url}{endpoint}"
        
        try:
            # response 通过 session.post 发送POST请求
            # 传入url、json格式的data、超时时间timeout
            # 得到HTTP响应对象
            response = self.session.post(
                url=url,
                json=data or {},
                timeout=REQUEST_TIMEOUT
            )
            
            # 尝试解析响应为JSON格式
            try:
                # parsed_data 通过 response.json() 解析响应体为字典
                parsed_data = response.json()
            except json.JSONDecodeError:
                # 如果JSON解析失败，使用响应文本创建错误数据
                parsed_data = {
                    "error": "响应格式不是有效的JSON",
                    "raw_response": response.text
                }
            
            # 返回包含状态码和解析数据的完整响应字典
            return {
                "status_code": response.status_code,
                "data": parsed_data,
                "headers": dict(response.headers)
            }
            
        except requests.exceptions.RequestException as e:
            # 处理网络请求异常，返回错误信息
            return {
                "status_code": 0,
                "data": {
                    "error": f"请求失败: {str(e)}",
                    "error_type": "NETWORK_ERROR"
                },
                "headers": {}
            }
    
    def get(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[Any, Any]:
        """
        发送GET请求
        
        将endpoint与base_url拼接成完整URL，
        将params作为查询参数发送GET请求，
        返回解析后的响应数据字典。
        
        参数:
            endpoint: API路径，如 "/auth/google"
            params: 查询参数字典
            
        返回:
            Dict: 响应数据字典，包含status_code和parsed_response
        """
        # url 通过 self.base_url 和 endpoint 拼接成完整请求地址
        url = f"{self.base_url}{endpoint}"
        
        try:
            # response 通过 session.get 发送GET请求
            # 传入url、查询参数params、超时时间timeout
            # 得到HTTP响应对象
            response = self.session.get(
                url=url,
                params=params or {},
                timeout=REQUEST_TIMEOUT
            )
            
            # 尝试解析响应为JSON格式
            try:
                # parsed_data 通过 response.json() 解析响应体为字典
                parsed_data = response.json()
            except json.JSONDecodeError:
                # 如果JSON解析失败，使用响应文本创建错误数据
                parsed_data = {
                    "error": "响应格式不是有效的JSON",
                    "raw_response": response.text
                }
            
            # 返回包含状态码和解析数据的完整响应字典
            return {
                "status_code": response.status_code,
                "data": parsed_data,
                "headers": dict(response.headers)
            }
            
        except requests.exceptions.RequestException as e:
            # 处理网络请求异常，返回错误信息
            return {
                "status_code": 0,
                "data": {
                    "error": f"请求失败: {str(e)}",
                    "error_type": "NETWORK_ERROR"
                },
                "headers": {}
            }


def generate_test_email(identifier: str) -> str:
    """
    生成测试用邮箱地址
    
    使用固定前缀、标识符和时间戳生成测试邮箱，
    确保每次生成的邮箱都是唯一的，避免与真实邮箱冲突。
    
    参数:
        identifier: 邮箱标识符，如 "register001"
        
    返回:
        str: 完整的测试邮箱地址
    """
    import time
    # 通过 time.time() 获取当前时间戳，确保邮箱唯一性
    # 通过 TEST_EMAIL_PREFIX、identifier、时间戳和域名拼接生成测试邮箱
    timestamp = int(time.time())
    return f"{TEST_EMAIL_PREFIX}{identifier}_{timestamp}@example.com"


def print_test_result(test_name: str, response: Dict[Any, Any], expected_status: int = 200, request_data: Dict[Any, Any] = None):
    """
    Print test result data flow
    
    Display test execution data flow including request data, response data, and key variables.
    Used for debugging and analyzing data flow through test scenarios.
    
    Args:
        test_name: Test name description
        response: API response data dictionary
        expected_status: Expected HTTP status code
        request_data: Request data dictionary (for debugging)
    """
    print(f"\n{'='*80}")
    print(f"Test execution: {test_name}")
    print(f"{'='*80}")
    
    # Print request data flow
    if request_data:
        print(f"Request payload size: {len(json.dumps(request_data))}")
        print(f"Request data structure:")
        print(json.dumps(request_data, indent=2, ensure_ascii=False))
        print(f"{'-'*40}")
    
    # Extract key response variables
    status_code = response.get("status_code", 0)
    data = response.get("data", {})
    headers = response.get("headers", {})
    
    print(f"HTTP status code: {status_code} (expected: {expected_status})")
    print(f"Status validation: {'PASS' if status_code == expected_status else 'FAIL'}")
    
    # Print response data structure and content
    print(f"Response data size: {len(json.dumps(data))}")
    print(f"Response structure:")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    
    # Print important headers data
    if headers:
        important_headers = {k: v for k, v in headers.items() if k.lower() in ['content-type', 'content-length', 'server']}
        if important_headers:
            print(f"Response headers:")
            print(json.dumps(important_headers, indent=2, ensure_ascii=False))
    
    # Business logic validation data
    if "success" in data:
        success = data.get("success", False)
        print(f"Business success flag: {success}")
        
        if not success:
            error_message = data.get("error", "")
            error_type = data.get("error_type", "")
            print(f"Error message content: {error_message}")
            print(f"Error type classification: {error_type}")
    
    # Print response data analysis
    if isinstance(data, dict):
        print(f"Response keys count: {len(data.keys())}")
        print(f"Response top-level keys: {list(data.keys())}")
    
    print(f"{'='*80}")
