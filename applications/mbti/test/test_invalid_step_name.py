#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_invalid_step_name.py - 测试提交非法步骤名称时的跳转校验异常
测试目的：验证当请求包含无效的步骤名称（如mbti_step99）时，系统是否能正确检测并返回错误响应
"""

import sys
import os
import json
import asyncio
from typing import Dict, Any

# 添加项目根目录到路径，确保可以导入hub模块
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, project_root)

# 从hub.hub模块导入run函数，这是系统的主要调度入口
from hub.hub import run as dispatcher_handler


async def test_invalid_step_name_validation():
    """
    测试非法步骤名称的校验异常
    模拟用户请求包含不存在的步骤名称的情况
    """
    print("=== 开始测试：非法步骤名称的跳转校验异常 ===")
    
    # 构建包含非法步骤名称的请求数据
    # intent设置为不存在的mbti_step99，应该被系统拒绝
    request_data = {
        "intent": "mbti_step99",  # 非法的步骤名称，系统中只有step1到step5
        "user_id": "test_user_invalid_step",
        "request_id": "2024-12-19T10:05:00+0800_87654321-4321-4123-8123-fedcba987654",
        "flow_id": "mbti_personality_test",
        "test_scenario": "invalid_step_validation"
    }
    
    print("REQUEST DATA:")
    # json.dumps通过调用格式化请求数据为可读的JSON字符串
    print(json.dumps(request_data, indent=2, ensure_ascii=False))
    
    try:
        print("\n=== 通过系统主入口调用dispatcher_handler ===")
        # dispatcher_handler通过await异步调用系统主调度器
        # 传入包含非法步骤名称的request_data参数
        response = await dispatcher_handler(request_data)
        
        print("\nRESPONSE DATA:")
        # json.dumps通过调用格式化响应数据为可读的JSON字符串
        print(json.dumps(response, indent=2, ensure_ascii=False))
        
        # 验证系统是否正确识别并拒绝非法步骤名称
        # 预期系统应该返回错误信息，说明该intent不被支持
        if "error" in response:
            error_message = str(response.get("error", ""))
            if ("No handler" in error_message and "mbti_step99" in error_message) or \
               ("handler_not_found" in response.get("status", "")) or \
               ("不支持的intent" in error_message):
                print("\n✓ 系统成功检测到非法步骤名称")
                print("✓ 返回了适当的错误消息")
                print(f"✓ 错误类型: {response.get('status', 'N/A')}")
                test_result = "PASSED"
            else:
                print("\n✗ 系统返回了错误但错误类型不符合预期")
                print(f"错误信息: {error_message}")
                print(f"错误状态: {response.get('status', 'N/A')}")
                test_result = "FAILED"
        else:
            print("\n✗ 系统未检测到非法步骤名称")
            print("✗ 系统错误地接受了无效的intent")
            test_result = "FAILED"
        
        # 额外验证：检查是否有流程上下文信息
        if "flow_context" in response:
            print(f"✓ 响应包含流程上下文信息: {response['flow_context']}")
        
    except Exception as e:
        print(f"\nEXCEPTION:")
        print(f"测试执行异常: {str(e)}")
        print(f"异常类型: {type(e).__name__}")
        
        # 检查异常是否为预期的路由异常
        if "handler" in str(e).lower() or "intent" in str(e).lower():
            print("✓ 异常符合预期，系统正确拒绝了非法步骤")
            test_result = "PASSED"
        else:
            test_result = "FAILED"
    
    print(f"\nFINAL RESULT: TEST {test_result}")
    return test_result


async def test_boundary_step_names():
    """
    测试边界情况的步骤名称
    验证系统对各种形式的无效步骤名称的处理
    """
    print("\n=== 开始边界测试：多种非法步骤名称 ===")
    
    # 测试用例：包含多种无效步骤名称的测试数据
    boundary_test_cases = [
        {
            "intent": "",  # 空字符串
            "description": "空字符串intent"
        },
        {
            "intent": "mbti_step0",  # 不存在的step0
            "description": "不存在的step0"  
        },
        {
            "intent": "MBTI_STEP1",  # 大写版本
            "description": "大写版本的步骤名"
        },
        {
            "intent": "mbti_step_1",  # 下划线格式
            "description": "下划线格式的步骤名"
        }
    ]
    
    passed_count = 0
    total_count = len(boundary_test_cases)
    
    for i, test_case in enumerate(boundary_test_cases, 1):
        print(f"\n--- 边界测试 {i}/{total_count}: {test_case['description']} ---")
        
        request_data = {
            "intent": test_case["intent"],
            "user_id": f"test_user_boundary_{i}",
            "request_id": f"2024-12-19T10:{i:02d}:00+0800_boundary-test-{i:04d}-{i:04d}-{i:04d}-{i:012d}",
            "flow_id": "mbti_personality_test"
        }
        
        print(f"测试intent: '{test_case['intent']}'")
        
        try:
            # dispatcher_handler通过await异步调用测试每个边界情况
            response = await dispatcher_handler(request_data)
            
            # 验证是否返回了适当的错误响应
            if "error" in response or response.get("status") == "handler_not_found":
                print(f"✓ 正确拒绝了无效intent: {test_case['intent']}")
                passed_count += 1
            else:
                print(f"✗ 错误地接受了无效intent: {test_case['intent']}")
                
        except Exception as e:
            print(f"✓ 通过异常正确拒绝了无效intent: {str(e)}")
            passed_count += 1
    
    print(f"\n边界测试结果: {passed_count}/{total_count} 通过")
    return passed_count == total_count


def main():
    """
    main函数通过asyncio.run执行异步测试函数
    包含主要测试和边界测试
    """
    print("启动非法步骤名称测试...")
    
    # asyncio.run通过调用运行异步测试函数
    result1 = asyncio.run(test_invalid_step_name_validation())
    result2 = asyncio.run(test_boundary_step_names())
    
    # 综合评估测试结果
    overall_result = "PASSED" if (result1 == "PASSED" and result2) else "FAILED"
    
    if overall_result == "PASSED":
        print("\n🎉 测试通过：系统正确处理了所有非法步骤名称")
    else:
        print("\n❌ 测试失败：系统未能正确处理部分非法步骤名称")
    
    print(f"\nFINAL RESULT: TEST {overall_result}")
    return overall_result


if __name__ == "__main__":
    main()
