#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_missing_intent.py - 测试缺失intent字段时的系统响应
测试目的：验证当请求数据中缺少intent字段时，系统是否能正确捕获并返回适当的错误响应
"""

import sys
import os
import json
import asyncio
from typing import Dict, Any

# 添加项目根目录到路径，确保可以导入hub模块
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, project_root)

# 先导入MBTI模块以触发自注册机制
import applications.mbti

# 导入Time类用于生成正确格式的Request ID  
from utilities.time import Time

# 从hub.hub模块导入run函数，这是系统的主要调度入口
from hub.hub import run as dispatcher_handler


async def test_missing_intent_field():
    """
    测试缺失intent字段时的系统响应行为
    模拟用户请求中缺少intent字段的异常情况
    """
    print("=== 开始测试：缺失intent字段的系统响应 ===")
    
    # 构建缺失intent字段的请求数据
    # 包含user_id、request_id等正常字段，但故意省略intent字段
    request_data = {
        "user_id": "test_user_missing_intent",
        "request_id": Time.timestamp(),
        "flow_id": "mbti_personality_test",
        "test_scenario": "missing_intent_validation"
    }
    
    print("REQUEST DATA:")
    # json.dumps通过调用格式化请求数据为可读的JSON字符串
    print(json.dumps(request_data, indent=2, ensure_ascii=False))
    
    try:
        print("\n=== 通过系统主入口调用dispatcher_handler ===")
        # dispatcher_handler通过await异步调用系统主调度器
        # 传入request_data参数，模拟真实的请求处理流程
        response = await dispatcher_handler(request_data)
        
        print("\nRESPONSE DATA:")
        # json.dumps通过调用格式化响应数据为可读的JSON字符串
        print(json.dumps(response, indent=2, ensure_ascii=False))
        
        # 验证响应是否包含预期的错误信息
        # 系统应该检测到intent字段缺失并返回相应的错误响应
        if "error" in response:
            if "Missing intent" in str(response.get("error", "")):
                print("\n✓ 系统成功检测到intent字段缺失")
                print("✓ 返回了适当的错误消息")
                test_result = "PASSED"
            else:
                print("\n✗ 系统返回了错误但错误消息不符合预期")
                print(f"预期包含: 'Missing intent'")
                print(f"实际收到: {response.get('error', 'N/A')}")
                test_result = "FAILED"
        else:
            print("\n✗ 系统未检测到intent字段缺失")
            print("✗ 响应中缺少错误信息")
            test_result = "FAILED"
            
    except Exception as e:
        print(f"\nEXCEPTION:")
        print(f"测试执行异常: {str(e)}")
        print(f"异常类型: {type(e).__name__}")
        
        # 对于缺失intent字段，抛出InvalidIntentError或相关异常是期望的安全行为
        if "Missing intent field" in str(e) or "InvalidIntentError" in str(type(e).__name__):
            print("✓ 异常符合预期，系统正确拒绝了缺失intent的请求")
            test_result = "PASSED"
        else:
            test_result = "FAILED"
    
    print(f"\nFINAL RESULT: TEST {test_result}")
    return test_result


def main():
    """
    main函数通过asyncio.run执行异步测试函数
    确保测试在异步环境下正确运行
    """
    print("启动缺失intent字段异常测试...")
    # asyncio.run通过调用运行异步测试函数
    result = asyncio.run(test_missing_intent_field())
    
    if result == "PASSED":
        print("\n🎉 测试通过：系统正确处理了intent字段缺失的情况")
    else:
        print("\n❌ 测试失败：系统未能正确处理intent字段缺失的情况")
    
    return result


if __name__ == "__main__":
    main()
