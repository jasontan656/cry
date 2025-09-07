"""
MBTI性格测试中心模块路由处理器
职责：路由编排，根据步骤参数路由请求到对应步骤子模块
"""

# asyncio 通过 import 导入异步编程模块，用于支持协程和异步操作
import asyncio
# typing 通过 from...import 导入类型注解模块
# Dict、Union 被导入用于定义字典和联合类型
from typing import Dict, Union, Optional

# RequestData 通过 Dict 构造类型别名，包含字符串、整数、布尔值、空值类型的联合类型
# 赋值给 RequestData 作为请求数据类型定义
RequestData = Dict[str, Union[str, int, bool, None]]
# ResponseData 通过 Dict 构造类型别名，包含字符串、布尔值、整数类型的联合类型
# 赋值给 ResponseData 作为响应数据类型定义
ResponseData = Dict[str, Union[str, bool, int]]

# import 语句通过模块名导入 step1 模块
# 使用绝对导入方式，支持测试环境和独立运行环境
# 赋值给 step1 变量，用于后续调用 step1.process() 方法
import step1
# import 语句通过模块名导入 step2 模块
# 使用绝对导入方式，支持测试环境和独立运行环境
# 赋值给 step2 变量，用于后续调用 step2.process() 方法
import step2
# import 语句通过模块名导入 step3 模块
# 使用绝对导入方式，支持测试环境和独立运行环境
# 赋值给 step3 变量，用于后续调用 step3.process() 方法
import step3
# import 语句通过模块名导入 step4 模块
# 使用绝对导入方式，支持测试环境和独立运行环境
# 赋值给 step4 变量，用于后续调用 step4.process() 方法
import step4
# import 语句通过模块名导入 step5 模块
# 使用绝对导入方式，支持测试环境和独立运行环境
# 赋值给 step5 变量，用于后续调用 step5.process() 方法
import step5


class MBTIRouter:
    """
    MBTI测试路由器
    职责：根据步骤参数路由请求到对应处理器
    """
    
    # __init__ 方法通过 def 定义实例初始化方法，接收 self 参数
    # 在 MBTIRouter 类实例创建时自动调用
    def __init__(self):
        # self.intent_handlers 通过字典创建intent处理器映射表
        # "mbti_step1" 键映射到 self._handle_mbti_step1 方法引用
        # "mbti_step2" 键映射到 self._handle_mbti_step2 方法引用
        # "mbti_step3" 键映射到 self._handle_mbti_step3 方法引用
        # "mbti_step4" 键映射到 self._handle_mbti_step4 方法引用
        # "mbti_step5" 键映射到 self._handle_mbti_step5 方法引用
        # 赋值给 self.intent_handlers 实例变量存储
        self.intent_handlers = {
            "mbti_step1": self._handle_mbti_step1,
            "mbti_step2": self._handle_mbti_step2,
            "mbti_step3": self._handle_mbti_step3,
            "mbti_step4": self._handle_mbti_step4,
            "mbti_step5": self._handle_mbti_step5
        }
    
    # process 方法通过 async def 定义异步处理方法，接收 self 和 request 参数
    # request 参数类型为 RequestData，返回类型为 ResponseData
    async def process(self, request: RequestData) -> ResponseData:
        # try 块开始异常处理，捕获可能出现的异常情况
        try:
            # current_intent 通过 request.get() 方法获取 "intent" 键对应的值
            # 传入 "intent" 字符串作为键参数，默认值为空
            # 赋值给 current_intent 变量存储当前意图标识
            current_intent = request.get("intent")

            # if 条件判断语句检查 current_intent 是否存在且在 self.intent_handlers 字典中
            if current_intent and current_intent in self.intent_handlers:
                # handler 通过 self.intent_handlers[current_intent] 从映射表获取处理器方法引用
                # current_intent 作为字典键传入，得到对应的方法对象
                # 赋值给 handler 变量存储
                handler = self.intent_handlers[current_intent]
                # result 通过 await 调用 handler 方法，传入 request 参数
                # handler 是异步方法，需要 await 等待执行完成
                # 返回的结果赋值给 result 变量
                result = await handler(request)
                # 通过 return 返回 result 变量的值作为方法结果
                return result
            else:
                # error_result 通过 self._create_error_response() 调用错误响应创建方法
                # request.get("request_id") 获取请求ID作为第一个参数
                # "INTENT_INVALID" 字符串作为错误类型传入
                # f"不支持的intent: {current_intent}" 格式化字符串作为错误描述传入
                # 返回的错误响应字典赋值给 error_result 变量
                error_result = self._create_error_response(
                    request.get("request_id"),
                    "INTENT_INVALID",
                    f"不支持的intent: {current_intent}"
                )
                # 通过 return 返回 error_result 变量的值作为方法结果
                return error_result

        # except 捕获 Exception 异常类及其子类的异常实例
        # 异常对象赋值给变量 e
        except Exception as e:
            # 通过 return 调用 self._create_error_response() 方法
            # request.get("request_id", "unknown") 获取请求ID，默认值为 "unknown"
            # "SYSTEM_ERROR" 字符串作为错误类型传入
            # f"系统处理异常: {str(e)}" 将异常对象转换为字符串后格式化
            # 返回错误响应字典作为方法结果
            return self._create_error_response(
                request.get("request_id", "unknown"),
                "SYSTEM_ERROR",
                f"系统处理异常: {str(e)}"
            )
    
    # _handle_mbti_step1 方法通过 async def 定义异步处理方法，接收 self 和 request 参数
    # request 参数类型为 RequestData，返回类型为 ResponseData
    async def _handle_mbti_step1(self, request: RequestData) -> ResponseData:
        # 通过 return 调用 await step1.process() 方法
        # 传入 request 参数到 step1.process() 方法
        # await 等待异步执行完成后返回结果作为方法返回值
        return await step1.process(request)

    # _handle_mbti_step2 方法通过 async def 定义异步处理方法，接收 self 和 request 参数
    # request 参数类型为 RequestData，返回类型为 ResponseData
    async def _handle_mbti_step2(self, request: RequestData) -> ResponseData:
        # 通过 return 调用 await step2.process() 方法
        # 传入 request 参数到 step2.process() 方法
        # await 等待异步执行完成后返回结果作为方法返回值
        return await step2.process(request)

    # _handle_mbti_step3 方法通过 async def 定义异步处理方法，接收 self 和 request 参数
    # request 参数类型为 RequestData，返回类型为 ResponseData
    async def _handle_mbti_step3(self, request: RequestData) -> ResponseData:
        # 通过 return 调用 await step3.process() 方法
        # 传入 request 参数到 step3.process() 方法
        # await 等待异步执行完成后返回结果作为方法返回值
        return await step3.process(request)

    # _handle_mbti_step4 方法通过 async def 定义异步处理方法，接收 self 和 request 参数
    # request 参数类型为 RequestData，返回类型为 ResponseData
    async def _handle_mbti_step4(self, request: RequestData) -> ResponseData:
        # 通过 return 调用 await step4.process() 方法
        # 传入 request 参数到 step4.process() 方法
        # await 等待异步执行完成后返回结果作为方法返回值
        return await step4.process(request)

    # _handle_mbti_step5 方法通过 async def 定义异步处理方法，接收 self 和 request 参数
    # request 参数类型为 RequestData，返回类型为 ResponseData
    async def _handle_mbti_step5(self, request: RequestData) -> ResponseData:
        # 通过 return 调用 await step5.process() 方法
        # 传入 request 参数到 step5.process() 方法
        # await 等待异步执行完成后返回结果作为方法返回值
        return await step5.process(request)
    
    # _create_error_response 方法通过 def 定义错误响应创建方法
    # 接收 self、request_id、error_code、error_message 参数
    # 所有参数类型为 str，返回类型为 ResponseData
    def _create_error_response(self, request_id: str, error_code: str, error_message: str) -> ResponseData:
        # 通过 return 返回字典对象作为方法结果
        # "request_id" 键赋值为 request_id 参数值
        # "success" 键赋值为 False 布尔值
        # "step" 键赋值为 "error" 字符串
        # "error_message" 键赋值为 error_message 参数值
        # "error_code" 键赋值为 error_code 参数值
        return {
            "request_id": request_id,
            "success": False,
            "step": "error",
            "error_message": error_message,
            "error_code": error_code
        }


# router 通过 MBTIRouter() 调用类构造函数创建实例对象
# 不传入任何参数，使用默认初始化
# 赋值给 router 变量存储路由器实例
router = MBTIRouter()

# process_mbti_request 函数通过 async def 定义异步处理函数
# 接收 request 参数，类型为 RequestData，返回类型为 ResponseData
async def process_mbti_request(request: RequestData) -> ResponseData:
    # 通过 return 调用 await router.process() 方法
    # 传入 request 参数到 router.process() 方法
    # await 等待异步执行完成后返回结果作为函数返回值
    return await router.process(request)

