class RegistryCenter:
    """
    RegistryCenter 类负责管理整个 CareerBot 系统中的模块注册信息
    作为单例模式实现，用于收集和索引所有模块的注册信息
    """

    # _instance 被设置为类属性，用于存储单例实例
    # 初始化为 None，表示尚未创建实例
    _instance = None

    # module_meta 被初始化为空字典，用于存储各模块的元信息
    # 键为模块名，值为包含 name、version、capabilities、needs_frontend 等信息的字典
    module_meta = {}

    # intent_handlers 被初始化为空字典，用于存储意图与处理函数的映射关系
    # 键为意图字符串，值为对应的处理函数引用
    intent_handlers = {}

    # field_definitions 被初始化为空字典，用于存储模块定义的输入输出字段结构
    # 键为模块名，值为字段定义字典
    field_definitions = {}

    def __new__(cls):
        # __new__ 方法在创建实例时被调用，用于实现单例模式
        # 如果 _instance 为 None，则创建新实例并赋值给 _instance
        # 否则直接返回已存在的实例
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def register_module(self, module_info: dict):
        """
        register_module 方法接受模块主动上报的 MODULE_INFO 字典
        用于记录模块的元信息、意图处理器和字段定义

        通过 module_info 参数传入模块注册信息字典
        解析其中的 name、capabilities、intents、entrypoint、fields、needs_frontend 等字段
        并分别存储到对应的数据结构中
        """
        # 从 module_info 字典中提取模块名称，作为后续存储的键
        module_name = module_info.get('name')

        # 如果 module_name 存在，则继续处理注册信息
        if module_name:
            # 将模块的元信息存储到 module_meta 字典中
            # 包含 name、version、capabilities、needs_frontend 等字段
            self.module_meta[module_name] = {
                'name': module_info.get('name'),
                'version': module_info.get('version'),
                'capabilities': module_info.get('capabilities', []),
                'needs_frontend': module_info.get('needs_frontend', False)
            }

            # 从 module_info 中获取 intents 字段，默认为空列表
            intents = module_info.get('intents', [])

            # 遍历 intents 列表，为每个意图注册对应的处理函数
            for intent_info in intents:
                # 从 intent_info 中提取意图名称和对应的处理函数
                intent_name = intent_info.get('intent')
                handler_func = intent_info.get('handler')

                # 如果意图名称和处理函数都存在，则存储到 intent_handlers 字典中
                if intent_name and handler_func:
                    self.intent_handlers[intent_name] = handler_func

            # 从 module_info 中获取 fields 字段，存储模块的字段定义
            fields = module_info.get('fields', {})

            # 将字段定义存储到 field_definitions 字典中，以模块名作为键
            self.field_definitions[module_name] = fields

    def get_handler_for_intent(self, intent: str):
        """
        get_handler_for_intent 方法根据意图名称返回对应的处理函数
        供中枢系统调用具体的意图处理逻辑

        通过 intent 参数传入意图字符串
        从 intent_handlers 字典中查找对应的处理函数
        如果找到则返回处理函数，否则返回 None
        """
        # 通过 intent 作为键，从 intent_handlers 字典中获取对应的处理函数
        # 如果意图不存在，则返回 None
        return self.intent_handlers.get(intent)

    def get_fields(self, module_name: str):
        """
        get_fields 方法根据模块名称返回该模块的字段定义
        用于获取特定模块的输入输出字段结构

        通过 module_name 参数传入模块名称字符串
        从 field_definitions 字典中查找对应的字段定义
        如果找到则返回字段定义字典，否则返回空字典
        """
        # 通过 module_name 作为键，从 field_definitions 字典中获取字段定义
        # 如果模块不存在，则返回空字典
        return self.field_definitions.get(module_name, {})

    def get_all_fields(self):
        """
        get_all_fields 方法返回所有模块的字段定义
        用于获取系统中所有模块的输入输出字段结构总览

        不需要传入参数，直接返回 field_definitions 字典的副本
        避免外部直接修改内部数据结构
        """
        # 返回 field_definitions 字典的浅拷贝
        # 防止外部代码直接修改内部的字段定义数据
        return self.field_definitions.copy()
