# 综合测试运行脚本
# 执行所有auth模块API测试并生成综合报告

import sys
import subprocess
import time
from datetime import datetime


class AuthTestRunner:
    """
    Auth模块测试运行器
    
    提供统一的测试执行接口，包含测试报告生成和结果统计功能。
    """
    
    def __init__(self):
        # test_modules 定义所有测试模块的文件名和描述
        self.test_modules = [
            {
                "file": "test_register_normal.py",
                "name": "正常邮箱注册流程",
                "description": "测试完整的邮箱验证码注册流程"
            },
            {
                "file": "test_register_duplicate_email.py", 
                "name": "重复邮箱注册处理",
                "description": "测试重复邮箱的各种处理场景"
            },
            {
                "file": "test_register_with_test_user.py",
                "name": "test_user模式注册",
                "description": "测试开发调试模式的快速注册"
            },
            {
                "file": "test_login_success.py",
                "name": "邮箱登录成功流程",
                "description": "测试正确凭证的登录流程和响应"
            },
            {
                "file": "test_login_wrong_password.py",
                "name": "邮箱登录失败处理",
                "description": "测试错误密码和各种登录失败场景"
            },
            {
                "file": "test_oauth_direct_login.py",
                "name": "OAuth直接登录流程",
                "description": "测试Google和Facebook的OAuth登录"
            },
            {
                "file": "test_oauth_then_register.py",
                "name": "OAuth后邮箱注册流程",
                "description": "测试OAuth用户的邮箱绑定逻辑"
            },
            {
                "file": "test_register_then_oauth.py",
                "name": "邮箱注册后OAuth流程",
                "description": "测试已注册用户的OAuth绑定逻辑"
            },
            {
                "file": "test_token_invalid.py",
                "name": "无效token处理",
                "description": "测试各种无效token的安全处理"
            }
        ]
        
        # test_results 存储每个测试的执行结果
        self.test_results = []
        # start_time 记录测试开始时间
        self.start_time = None
        # end_time 记录测试结束时间
        self.end_time = None
    
    def run_single_test(self, test_module: dict) -> dict:
        """
        运行单个测试模块
        
        执行指定的测试脚本并收集执行结果。
        
        参数:
            test_module: 测试模块字典，包含文件名和描述
            
        返回:
            dict: 测试执行结果，包含成功状态、执行时间等信息
        """
        print(f"\n{'='*80}")
        print(f"Test execution: {test_module['name']}")
        print(f"Test file: {test_module['file']}")
        print(f"Test description: {test_module['description']}")
        print(f"{'='*80}")
        
        # module_start_time 记录单个模块开始时间
        module_start_time = time.time()
        
        try:
            # result 通过 subprocess.run 执行测试脚本
            # 传入python解释器路径、脚本文件名，捕获输出和错误
            # timeout设置为300秒防止测试卡死
            result = subprocess.run(
                [sys.executable, test_module['file']],
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            # module_end_time 记录单个模块结束时间
            module_end_time = time.time()
            # execution_time 计算模块执行时间
            execution_time = module_end_time - module_start_time
            
            # Print test output data flow
            if result.stdout:
                print(f"\nTest stdout output:")
                print(f"Output length: {len(result.stdout)} characters")
                print(result.stdout)

            if result.stderr:
                print(f"\nTest stderr output:")
                print(f"Error output length: {len(result.stderr)} characters")
                print(result.stderr)

            # Determine test success based on return code
            success = result.returncode == 0
            output_size = len(result.stdout) + len(result.stderr)

            if success:
                print(f"\nTest result: PASS - execution time: {execution_time:.2f}s")
                print(f"Total output size: {output_size} characters")
            else:
                print(f"\nTest result: FAIL - execution time: {execution_time:.2f}s")
                print(f"Exit code: {result.returncode}")
                print(f"Error output present: {'YES' if result.stderr else 'NO'}")
            
            # 返回测试结果字典
            return {
                "module": test_module,
                "success": success,
                "execution_time": execution_time,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
        except subprocess.TimeoutExpired:
            # 处理测试超时的情况
            execution_time = time.time() - module_start_time
            
            print(f"\nTest timeout occurred - execution time: {execution_time:.2f}s")
            print(f"Timeout threshold: 300s")
            
            return {
                "module": test_module,
                "success": False,
                "execution_time": execution_time,
                "return_code": -1,
                "stdout": "",
                "stderr": "测试执行超时"
            }
            
        except Exception as e:
            # 处理其他异常情况
            execution_time = time.time() - module_start_time
            
            print(f"\nTest execution exception: {str(e)}")
            print(f"Exception type: {type(e).__name__}")
            
            return {
                "module": test_module,
                "success": False,
                "execution_time": execution_time,
                "return_code": -2,
                "stdout": "",
                "stderr": f"执行异常: {str(e)}"
            }
    
    def run_all_tests(self):
        """
        运行所有测试模块
        
        按顺序执行所有测试脚本并收集结果。
        """
        print(f"Starting Auth module API test suite execution")
        print(f"Execution start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Planned test modules: {len(self.test_modules)}")
        print(f"Test modules list: {[module['file'] for module in self.test_modules]}")
        
        # start_time 记录整体测试开始时间
        self.start_time = time.time()
        
        # 逐个执行每个测试模块
        for i, test_module in enumerate(self.test_modules, 1):
            print(f"\nTest execution step [{i+1}/{len(self.test_modules)}] - preparing next test...")

            # Execute single test module and get results
            result = self.run_single_test(test_module)

            # Add test result to results list
            self.test_results.append(result)

            # Wait 2 seconds between tests (except for last test)
            if i < len(self.test_modules):
                print(f"\nWaiting 2 seconds before next test...")
                print(f"Current test results count: {len(self.test_results)}")
                time.sleep(2)
        
        # end_time 记录整体测试结束时间
        self.end_time = time.time()
    
    def generate_report(self):
        """
        生成测试报告
        
        统计测试结果并生成详细的执行报告。
        """
        if not self.test_results:
            print(f"No test results available for report generation")
            return
        
        print("\n" + "="*100)
        print("[报告] Auth模块API测试报告")
        print("="*100)
        
        # 计算统计信息
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        total_time = self.end_time - self.start_time if self.end_time else 0
        
        print(f"Test execution statistics:")
        print(f"  Total tests: {total_tests}")
        print(f"  Passed tests: {passed_tests}")
        print(f"  Failed tests: {failed_tests}")
        print(f"  Success rate: {(passed_tests/total_tests*100):.1f}%")
        print(f"  Total execution time: {total_time:.2f}s")
        print(f"  Average execution time: {(total_time/total_tests):.2f}s per test")
        print(f"  Tests per second: {(total_tests/total_time):.2f}")
        
        print(f"\nDetailed test results:")

        # Display detailed information for each test result
        for i, result in enumerate(self.test_results, 1):
            module = result["module"]
            success = result["success"]
            exec_time = result["execution_time"]
            return_code = result["return_code"]
            has_stderr = bool(result["stderr"])
            stderr_length = len(result["stderr"]) if result["stderr"] else 0

            status_indicator = "PASS" if success else "FAIL"

            print(f"\n  {i}. {status_indicator} - {module['name']}")
            print(f"     File: {module['file']}")
            print(f"     Execution time: {exec_time:.2f}s")
            print(f"     Return code: {return_code}")
            print(f"     Has stderr: {has_stderr}")
            if has_stderr:
                print(f"     Stderr length: {stderr_length} characters")

            # Display brief error if test failed
            if not success and result["stderr"]:
                error_lines = result["stderr"].split('\n')[:2]  # Show first 2 error lines
                for error_line in error_lines:
                    if error_line.strip():
                        print(f"     Error: {error_line.strip()}")
        
        # Generate recommendations and summary
        print(f"\nTest execution recommendations:")

        if failed_tests == 0:
            print(f"  Status: ALL TESTS PASSED - Auth module API functions correctly")
            print(f"  Suggestion: Consider adding more edge cases and performance tests")
        elif failed_tests <= 2:
            print(f"  Status: MOSTLY SUCCESSFUL - some functions may need adjustment")
            print(f"  Suggestion: Review specific error details from failed tests")
        else:
            print(f"  Status: MULTIPLE FAILURES - investigate basic configuration and service status")
            print(f"  Suggestion: Check server status, database connections, and service availability")
        
        print(f"\nTest completion timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Return overall test success status
        overall_success = failed_tests == 0
        print(f"Overall test suite result: {'SUCCESS' if overall_success else 'FAILURE'}")
        return overall_success


def main():
    """
    主函数入口
    
    创建测试运行器并执行所有测试。
    """
    print(f"Auth module API test suite starting")
    print("="*80)

    # Check basic environment
    print(f"Environment check:")
    print(f"  Python version: {sys.version}")
    print(f"  Working directory: {sys.path[0]}")
    print(f"  Python executable: {sys.executable}")
    print(f"  Platform: {sys.platform}")
    
    try:
        # runner 通过 AuthTestRunner() 创建测试运行器实例
        runner = AuthTestRunner()
        
        # 执行所有测试
        runner.run_all_tests()
        
        # 生成并显示测试报告
        overall_success = runner.generate_report()
        
        # Set program exit code based on test results
        if overall_success:
            print(f"\nAll tests passed - normal program exit")
            print(f"Exit code: 0")
            sys.exit(0)
        else:
            print(f"\nSome tests failed - abnormal program exit")
            print(f"Exit code: 1")
            sys.exit(1)

    except KeyboardInterrupt:
        print(f"\n\nUser interrupted test execution")
        print(f"Exit code: 130")
        sys.exit(130)

    except Exception as e:
        print(f"\nTest runner exception occurred: {str(e)}")
        print(f"Exception type: {type(e).__name__}")
        print(f"Exit code: 1")
        sys.exit(1)


if __name__ == "__main__":
    main()
