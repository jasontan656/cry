from typing import Dict, Any, Optional, Callable


class RegistryCenter:
    """
    RegistryCenter 类作为模块能力与字段注册的核心容器
    负责收集和索引所有模块的注册信息，统一管理模块的元信息、意图处理器、字段结构和依赖关系
    """

    # __init__ 方法初始化 RegistryCenter 类的实例
    # 创建五个核心数据结构用于存储模块注册信息
    def __init__(self):
        # module_meta 初始化为空字典，用于记录模块元信息
        # 键为模块名，值为包含 name、version、capabilities 等信息的字典
        self.module_meta: Dict[str, Dict[str, Any]] = {}

        # intent_handlers 初始化为空字典，用于存储意图名称到处理函数的映射
        # 键为意图字符串，值为对应的模块处理函数引用
        self.intent_handlers: Dict[str, Callable] = {}

        # intent_to_module 初始化为空字典，用于存储意图名称到模块名的直接映射
        # 键为意图字符串，值为对应的模块名，实现100%的注册后映射
        self.intent_to_module: Dict[str, str] = {}

        # module_fields 初始化为空字典，用于存储模块名称到字段结构的映射
        # 键为模块名，值为包含 field_types 和 field_groups 的字段结构字典
        self.module_fields: Dict[str, Dict[str, Any]] = {}

        # dependencies 初始化为空字典，用于存储模块名称到依赖模块列表的映射
        # 键为模块名，值为该模块声明的依赖模块名称列表
        self.dependencies: Dict[str, list] = {}

    def register_module(self, module_info: Dict[str, Any]) -> None:
        """
        register_module 方法采用完全自主注册策略，中枢只做编排不了解业务
        模块通过register_function完全自主控制注册过程，中枢被动接收注册信息
        注册完成后建立intent到module的直接映射，实现100%注册后映射
        """
        # 从 module_info 中提取模块名称，作为存储键
        module_name = module_info.get('name')

        # 只有当模块名称存在时才继续处理注册
        if module_name:
            # 检查模块是否提供了自主注册函数
            if 'register_function' in module_info:
                # 通过 _register_via_function 方法执行模块提供的自主注册函数
                # 传入 module_name 和 module_info 参数，让模块完全自主控制注册过程
                self._register_via_function(module_name, module_info)

                # 注册完成后，建立intent到module的直接映射
                # 从 module_info 中获取模块声明的意图列表
                supported_intents = module_info.get('orchestrate_info', {}).get('supported_intents', [])

                # 为每个已注册的intent建立到模块名的直接映射
                # 实现100%的注册后映射，只有注册时登记的intent才能被匹配
                for intent in supported_intents:
                    # intent 作为键，module_name 作为值
                    # 存储到 intent_to_module 字典中，建立直接映射关系
                    self.intent_to_module[intent] = module_name

    def _register_via_function(self, module_name: str, module_info: Dict[str, Any]) -> None:
        """
        _register_via_function 方法通过模块提供的自主注册函数进行注册
        这是最纯粹的照单全收方式，模块完全自主控制注册过程，中枢被动接收
        """
        # 从 module_info 中获取模块提供的注册函数
        register_func = module_info.get('register_function')

        # 检查注册函数是否有效且可调用
        if register_func and callable(register_func):
            # 调用模块提供的注册函数，传入注册中心实例和模块信息
            # 让模块完全自主控制注册过程，注册中心不做任何预设或干预
            register_func(self, module_name, module_info)


    def get_handler_for_intent(self, intent: str) -> Optional[Callable]:
        """
        get_handler_for_intent 方法根据意图名称获取对应的处理函数
        供外部调用执行具体的意图处理逻辑

        通过 intent 参数传入意图名称字符串
        从 intent_handlers 字典中查找对应的处理函数
        如果找到则返回处理函数，否则返回 None
        """
        # 使用 intent 作为键从 intent_handlers 字典中获取处理函数
        # 如果意图不存在则返回 None
        return self.intent_handlers.get(intent)

    def get_module_for_intent(self, intent: str) -> Optional[str]:
        """
        get_module_for_intent 方法根据意图名称直接获取对应的模块名
        实现100%的注册后映射，只有模块注册时登记的intent才能被匹配

        通过 intent 参数传入意图名称字符串
        从 intent_to_module 字典中直接查找对应的模块名
        如果意图未注册则返回 None，没有兜底机制
        """
        # 使用 intent 作为键从 intent_to_module 字典中直接获取模块名
        # 如果意图未在注册时登记，则返回 None
        return self.intent_to_module.get(intent)

    def get_module_fields(self, module_name: str) -> Dict[str, Any]:
        """
        get_module_fields 方法获取某个模块的字段结构定义
        用于查看特定模块的输入输出字段配置

        通过 module_name 参数传入模块名称字符串
        从 module_fields 字典中查找对应的字段结构
        如果找到则返回字段结构字典，否则返回空字典
        """
        # 使用 module_name 作为键从 module_fields 字典中获取字段结构
        # 如果模块不存在则返回空字典
        return self.module_fields.get(module_name, {})

    def get_dependencies(self, module_name: str) -> list:
        """
        get_dependencies 方法获取某个模块声明的依赖模块列表
        用于分析模块间的依赖关系和执行顺序

        通过 module_name 参数传入模块名称字符串
        从 dependencies 字典中查找对应的依赖列表
        如果找到则返回依赖模块列表，否则返回空列表
        """
        # 使用 module_name 作为键从 dependencies 字典中获取依赖列表
        # 如果模块不存在则返回空列表
        return self.dependencies.get(module_name, [])

    def get_all_fields(self) -> Dict[str, Dict[str, Any]]:
        """
        get_all_fields 方法返回所有模块的字段结构总览
        用于中枢系统获取完整的字段信息索引

        不需要传入参数，直接返回 module_fields 字典的副本
        防止外部直接修改内部数据结构
        """
        # 返回 module_fields 字典的浅拷贝
        # 避免外部代码直接修改内部的字段数据
        return self.module_fields.copy()
