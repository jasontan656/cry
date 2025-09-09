#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_complete_flow_step1_to_step5.py - 完整流程测试：用户从step1到step5的全流程模拟
测试目的：验证MBTI模块能否正确处理用户从开始到结束的完整测试流程
包括状态跟踪、数据传递和最终报告生成
"""

import sys
import os
import json
import asyncio
from typing import Dict, Any, List

# 添加项目根目录到路径，确保可以导入hub模块
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, project_root)

# 从hub.hub模块导入run函数，这是系统的主要调度入口
from hub.hub import run as dispatcher_handler


class MBTIFlowTestRunner:
    """
    MBTI流程测试执行器类
    负责管理完整的MBTI测试流程，跟踪状态变化和数据流转
    """
    
    def __init__(self, user_id: str):
        # user_id通过构造函数参数设置测试用户标识
        self.user_id = user_id
        # flow_id设置为标准MBTI流程标识符
        self.flow_id = "mbti_personality_test"
        # flow_state初始化为空字典，用于跟踪流程状态变化
        self.flow_state = {}
        # step_results初始化为空列表，用于存储每个步骤的执行结果
        self.step_results = []
        # current_step_number初始化为1，标识当前步骤编号
        self.current_step_number = 1
    
    async def execute_complete_flow(self) -> Dict[str, Any]:
        """
        execute_complete_flow方法通过异步执行完整的MBTI测试流程
        依次调用step1到step5，跟踪状态变化和数据传递
        
        Returns:
            Dict[str, Any]: 完整流程的执行结果汇总
        """
        print("=== 开始执行完整MBTI流程测试 ===")
        print(f"测试用户: {self.user_id}")
        print(f"流程ID: {self.flow_id}")
        
        flow_summary = {
            "user_id": self.user_id,
            "flow_id": self.flow_id,
            "total_steps": 5,
            "completed_steps": 0,
            "step_results": [],
            "overall_success": False,
            "final_mbti_type": None,
            "errors": []
        }
        
        try:
            # === Step 1: MBTI测试引导 ===
            step1_result = await self.execute_step1()
            flow_summary["step_results"].append(step1_result)
            
            if not step1_result.get("success"):
                flow_summary["errors"].append("Step1执行失败")
                return flow_summary
            
            flow_summary["completed_steps"] += 1
            print("✓ Step1 执行成功")
            
            # === Step 2: MBTI类型计算 ===
            step2_result = await self.execute_step2()
            flow_summary["step_results"].append(step2_result)
            
            if not step2_result.get("success"):
                flow_summary["errors"].append("Step2执行失败")
                return flow_summary
            
            flow_summary["completed_steps"] += 1
            print("✓ Step2 执行成功")
            
            # === Step 3: 反向问题生成 ===
            step3_result = await self.execute_step3()
            flow_summary["step_results"].append(step3_result)
            
            if not step3_result.get("success"):
                flow_summary["errors"].append("Step3执行失败")
                return flow_summary
            
            flow_summary["completed_steps"] += 1
            print("✓ Step3 执行成功")
            
            # === Step 4: 反向问题计分 ===
            step4_result = await self.execute_step4()
            flow_summary["step_results"].append(step4_result)
            
            if not step4_result.get("success"):
                flow_summary["errors"].append("Step4执行失败")
                return flow_summary
            
            flow_summary["completed_steps"] += 1
            print("✓ Step4 执行成功")
            
            # === Step 5: 最终报告生成 ===
            step5_result = await self.execute_step5()
            flow_summary["step_results"].append(step5_result)
            
            if not step5_result.get("success"):
                flow_summary["errors"].append("Step5执行失败")
                return flow_summary
            
            flow_summary["completed_steps"] += 1
            print("✓ Step5 执行成功")
            
            # === 流程完成验证 ===
            flow_summary["overall_success"] = True
            
            # 提取最终的MBTI类型结果
            final_mbti_type = self.extract_final_mbti_type()
            flow_summary["final_mbti_type"] = final_mbti_type
            
            print(f"🎉 完整流程执行成功！最终MBTI类型: {final_mbti_type}")
            
        except Exception as e:
            flow_summary["errors"].append(f"流程执行异常: {str(e)}")
            print(f"❌ 流程执行异常: {str(e)}")
        
        return flow_summary
    
    async def execute_step1(self) -> Dict[str, Any]:
        """
        execute_step1方法通过异步调用执行MBTI测试引导步骤
        
        Returns:
            Dict[str, Any]: Step1的执行结果
        """
        print("\n--- 执行 Step1: MBTI测试引导 ---")
        
        # 构建step1请求数据
        request_data = {
            "intent": "mbti_step1",
            "user_id": self.user_id,
            "request_id": f"2024-12-19T11:00:00+0800_step1-flow-test-{self.user_id[-4:]}-0001",
            "flow_id": self.flow_id,
            "test_scenario": "complete_flow_step1"
        }
        
        print("Step1 REQUEST:")
        print(json.dumps(request_data, indent=2, ensure_ascii=False))
        
        # dispatcher_handler通过await异步调用系统主调度器执行step1
        response = await dispatcher_handler(request_data)
        
        print("Step1 RESPONSE:")
        print(json.dumps(response, indent=2, ensure_ascii=False))
        
        # 提取并分析step1结果
        result = self.extract_step_result(response, "step1")
        
        # 更新流程状态
        if result.get("success"):
            self.flow_state["step1_completed"] = True
            self.flow_state["current_step"] = "mbti_step1"
            self.flow_state["next_step"] = result.get("next_step", "mbti_step2")
        
        return result
    
    async def execute_step2(self) -> Dict[str, Any]:
        """
        execute_step2方法通过异步调用执行MBTI类型初步计算步骤
        
        Returns:
            Dict[str, Any]: Step2的执行结果
        """
        print("\n--- 执行 Step2: MBTI类型计算 ---")
        
        # 构建模拟的MBTI问卷答案
        mock_responses = self.generate_mock_mbti_responses()
        
        # 构建step2请求数据
        request_data = {
            "intent": "mbti_step2",
            "user_id": self.user_id,
            "request_id": f"2024-12-19T11:05:00+0800_step2-flow-test-{self.user_id[-4:]}-0002",
            "flow_id": self.flow_id,
            "responses": mock_responses,  # 提供模拟的问卷答案
            "test_scenario": "complete_flow_step2"
        }
        
        print("Step2 REQUEST:")
        print(json.dumps(request_data, indent=2, ensure_ascii=False))
        
        # dispatcher_handler通过await异步调用系统主调度器执行step2
        response = await dispatcher_handler(request_data)
        
        print("Step2 RESPONSE:")
        print(json.dumps(response, indent=2, ensure_ascii=False))
        
        # 提取并分析step2结果
        result = self.extract_step_result(response, "step2")
        
        # 更新流程状态，保存MBTI计算结果
        if result.get("success"):
            self.flow_state["step2_completed"] = True
            self.flow_state["mbti_result"] = result.get("mbti_result")
            self.flow_state["analysis"] = result.get("analysis")
            self.flow_state["current_step"] = "mbti_step2"
        
        return result
    
    async def execute_step3(self) -> Dict[str, Any]:
        """
        execute_step3方法通过异步调用执行反向问题生成步骤
        
        Returns:
            Dict[str, Any]: Step3的执行结果
        """
        print("\n--- 执行 Step3: 反向问题生成 ---")
        
        # 从step2结果中获取MBTI结果作为step3的输入
        mbti_result = self.flow_state.get("mbti_result", {})
        
        # 构建step3请求数据
        request_data = {
            "intent": "mbti_step3",
            "user_id": self.user_id,
            "request_id": f"2024-12-19T11:10:00+0800_step3-flow-test-{self.user_id[-4:]}-0003",
            "flow_id": self.flow_id,
            "mbti_result": mbti_result,  # 传递step2的MBTI计算结果
            "test_scenario": "complete_flow_step3"
        }
        
        print("Step3 REQUEST:")
        print(json.dumps(request_data, indent=2, ensure_ascii=False))
        
        # dispatcher_handler通过await异步调用系统主调度器执行step3
        response = await dispatcher_handler(request_data)
        
        print("Step3 RESPONSE:")
        print(json.dumps(response, indent=2, ensure_ascii=False))
        
        # 提取并分析step3结果
        result = self.extract_step_result(response, "step3")
        
        # 更新流程状态，保存反向问题
        if result.get("success"):
            self.flow_state["step3_completed"] = True
            self.flow_state["reverse_questions"] = result.get("reverse_questions")
            self.flow_state["current_step"] = "mbti_step3"
        
        return result
    
    async def execute_step4(self) -> Dict[str, Any]:
        """
        execute_step4方法通过异步调用执行反向问题计分步骤
        
        Returns:
            Dict[str, Any]: Step4的执行结果
        """
        print("\n--- 执行 Step4: 反向问题计分 ---")
        
        # 基于step3的反向问题生成模拟答案
        reverse_responses = self.generate_mock_reverse_responses()
        
        # 构建step4请求数据
        request_data = {
            "intent": "mbti_step4",
            "user_id": self.user_id,
            "request_id": f"2024-12-19T11:15:00+0800_step4-flow-test-{self.user_id[-4:]}-0004",
            "flow_id": self.flow_id,
            "reverse_responses": reverse_responses,  # 提供反向问题答案
            "test_scenario": "complete_flow_step4"
        }
        
        print("Step4 REQUEST:")
        print(json.dumps(request_data, indent=2, ensure_ascii=False))
        
        # dispatcher_handler通过await异步调用系统主调度器执行step4
        response = await dispatcher_handler(request_data)
        
        print("Step4 RESPONSE:")
        print(json.dumps(response, indent=2, ensure_ascii=False))
        
        # 提取并分析step4结果
        result = self.extract_step_result(response, "step4")
        
        # 更新流程状态，保存确认的MBTI类型
        if result.get("success"):
            self.flow_state["step4_completed"] = True
            self.flow_state["confirmed_type"] = result.get("confirmed_type")
            self.flow_state["current_step"] = "mbti_step4"
        
        return result
    
    async def execute_step5(self) -> Dict[str, Any]:
        """
        execute_step5方法通过异步调用执行最终报告生成步骤
        
        Returns:
            Dict[str, Any]: Step5的执行结果
        """
        print("\n--- 执行 Step5: 最终报告生成 ---")
        
        # 从step4结果中获取确认的MBTI类型
        confirmed_type = self.flow_state.get("confirmed_type")
        
        # 构建step5请求数据
        request_data = {
            "intent": "mbti_step5",
            "user_id": self.user_id,
            "request_id": f"2024-12-19T11:20:00+0800_step5-flow-test-{self.user_id[-4:]}-0005",
            "flow_id": self.flow_id,
            "confirmed_type": confirmed_type,  # 传递确认的MBTI类型
            "test_scenario": "complete_flow_step5"
        }
        
        print("Step5 REQUEST:")
        print(json.dumps(request_data, indent=2, ensure_ascii=False))
        
        # dispatcher_handler通过await异步调用系统主调度器执行step5
        response = await dispatcher_handler(request_data)
        
        print("Step5 RESPONSE:")
        print(json.dumps(response, indent=2, ensure_ascii=False))
        
        # 提取并分析step5结果
        result = self.extract_step_result(response, "step5")
        
        # 更新流程状态，保存最终报告
        if result.get("success"):
            self.flow_state["step5_completed"] = True
            self.flow_state["final_report"] = result.get("final_report")
            self.flow_state["current_step"] = "mbti_step5"
            self.flow_state["flow_completed"] = True
        
        return result
    
    def extract_step_result(self, response: Dict[str, Any], step_name: str) -> Dict[str, Any]:
        """
        extract_step_result方法从系统响应中提取步骤执行结果
        
        Args:
            response: 系统响应数据
            step_name: 步骤名称
            
        Returns:
            Dict[str, Any]: 提取的步骤结果
        """
        # 默认结果结构
        result = {
            "step": step_name,
            "success": False,
            "raw_response": response
        }
        
        # 从响应中提取结果数据
        if "result" in response and isinstance(response["result"], dict):
            step_result = response["result"]
            result.update(step_result)
            
            # 判断执行是否成功
            result["success"] = step_result.get("success", False)
        elif "error" in response:
            result["error"] = response["error"]
            result["success"] = False
        else:
            # 如果没有明确的成功标识，根据响应内容判断
            result["success"] = True
        
        # 保存结果到步骤结果列表
        self.step_results.append(result)
        
        return result
    
    def generate_mock_mbti_responses(self) -> Dict[str, int]:
        """
        generate_mock_mbti_responses方法生成模拟的MBTI问卷答案
        
        Returns:
            Dict[str, int]: 模拟的问卷答案数据
        """
        # 生成一套完整的模拟MBTI答案（使用1-5量表）
        return {
            # E/I 维度题目 (外向/内向)
            "E1": 4, "E2": 3, "E3": 4, "E4": 3,
            "I1": 2, "I2": 3, "I3": 2, "I4": 3,
            
            # S/N 维度题目 (感觉/直觉)
            "S1": 3, "S2": 4, "S3": 3, "S4": 4,
            "N1": 4, "N2": 3, "N3": 4, "N4": 3,
            
            # T/F 维度题目 (思考/情感)
            "T1": 4, "T2": 3, "T3": 4, "T4": 3,
            "F1": 2, "F2": 3, "F3": 2, "F4": 3,
            
            # J/P 维度题目 (判断/感知)
            "J1": 4, "J2": 3, "J3": 4, "J4": 3,
            "P1": 2, "P2": 3, "P3": 2, "P4": 3
        }
    
    def generate_mock_reverse_responses(self) -> Dict[str, int]:
        """
        generate_mock_reverse_responses方法生成模拟的反向问题答案
        
        Returns:
            Dict[str, int]: 模拟的反向问题答案数据
        """
        # 生成反向问题的模拟答案
        return {
            "reverse_q1": 3,
            "reverse_q2": 4,
            "reverse_q3": 3,
            "reverse_q4": 4,
            "reverse_q5": 3
        }
    
    def extract_final_mbti_type(self) -> str:
        """
        extract_final_mbti_type方法从流程状态中提取最终的MBTI类型
        
        Returns:
            str: 最终确定的MBTI类型（如ENFP）
        """
        # 优先从step5的最终报告中提取
        if "final_report" in self.flow_state:
            final_report = self.flow_state["final_report"]
            if isinstance(final_report, dict):
                return final_report.get("mbti_type", "未确定")
        
        # 其次从step4的确认类型中提取
        if "confirmed_type" in self.flow_state:
            return str(self.flow_state["confirmed_type"])
        
        # 最后从step2的初步结果中提取
        if "mbti_result" in self.flow_state:
            mbti_result = self.flow_state["mbti_result"]
            if isinstance(mbti_result, dict):
                return mbti_result.get("mbti_type", "未确定")
        
        return "未确定"


async def test_complete_mbti_flow():
    """
    test_complete_mbti_flow函数执行完整的MBTI流程测试
    创建测试用户并运行完整的5步流程
    """
    print("=== 开始完整MBTI流程测试 ===")
    
    # 创建测试用户标识
    test_user_id = "complete_flow_test_user_2024"
    
    # 创建流程测试执行器
    flow_runner = MBTIFlowTestRunner(test_user_id)
    
    try:
        # 执行完整流程
        flow_summary = await flow_runner.execute_complete_flow()
        
        print("\n=== 流程测试总结 ===")
        print("FLOW SUMMARY:")
        print(json.dumps(flow_summary, indent=2, ensure_ascii=False))
        
        # 验证流程是否成功完成
        if flow_summary["overall_success"]:
            if flow_summary["completed_steps"] == 5:
                print("\n✓ 所有5个步骤均成功执行")
                print(f"✓ 最终MBTI类型: {flow_summary['final_mbti_type']}")
                test_result = "PASSED"
            else:
                print(f"\n✗ 只完成了 {flow_summary['completed_steps']}/5 个步骤")
                test_result = "FAILED"
        else:
            print(f"\n✗ 流程执行失败")
            print(f"错误信息: {flow_summary['errors']}")
            test_result = "FAILED"
            
    except Exception as e:
        print(f"\n❌ 流程测试异常: {str(e)}")
        test_result = "FAILED"
    
    print(f"\nFINAL RESULT: TEST {test_result}")
    return test_result


def main():
    """
    main函数通过asyncio.run执行完整流程测试
    """
    print("启动完整MBTI流程测试...")
    
    # asyncio.run通过调用运行异步完整流程测试
    result = asyncio.run(test_complete_mbti_flow())
    
    if result == "PASSED":
        print("\n🎉 测试通过：MBTI模块完整流程工作正常")
    else:
        print("\n❌ 测试失败：MBTI模块完整流程存在问题")
    
    return result


if __name__ == "__main__":
    main()
