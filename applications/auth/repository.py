# 用户数据仓库层
# 封装对数据库的操作，通过调用 utilities.database 中的方法实现

import uuid
from utilities.database import DatabaseOperations
from .schemas import UserData
from .exceptions import UserAlreadyExistsError


def check_user_exists(email: str) -> bool:
    """
    检查用户是否已存在

    通过邮箱查询数据库，判断用户是否已经注册。
    由于现在使用邮箱作为用户名，只需要检查邮箱是否存在。

    参数:
        email: 要检查的邮箱（同时作为用户名）

    返回:
        bool: 用户存在返回True，否则返回False
    """
    # 创建 DatabaseOperations 实例
    db = DatabaseOperations()

    # 构建查询条件：邮箱匹配（邮箱同时作为用户名）
    filter_condition = {"email": email}

    # 调用 DatabaseOperations.find() 方法查询用户是否存在
    # 传入集合名 "user_profiles" 和查询条件 filter_condition
    # 得到查询结果列表，赋值给 existing_users
    existing_users = db.find("user_profiles", filter_condition)

    # 检查查询结果列表长度，如果大于0表示用户已存在
    return len(existing_users) > 0


def create_user(username: str, email: str, hashed_password: str) -> str:
    """
    创建新用户记录

    生成唯一的user_id，将用户信息插入到数据库中。
    由于现在使用邮箱作为用户名，username 参数实际上就是邮箱。

    参数:
        username: 用户名（实际上是邮箱）
        email: 邮箱地址
        hashed_password: 加密后的密码

    返回:
        str: 新创建用户的user_id

    异常:
        UserAlreadyExistsError: 邮箱已存在
    """
    # 先检查用户是否已存在（通过邮箱检查）
    if check_user_exists(email):
        raise UserAlreadyExistsError("邮箱已存在")

    # 生成唯一的用户ID
    user_id = str(uuid.uuid4())

    # 创建 UserData 对象，包含用户完整信息
    user_data = UserData(
        user_id=user_id,
        username=username,
        email=email,
        hashed_password=hashed_password
    )

    # 将 UserData 对象转换为字典格式用于数据库存储
    user_dict = user_data.model_dump()

    # 创建 DatabaseOperations 实例
    db = DatabaseOperations()

    # 调用 DatabaseOperations.insert() 方法插入用户数据
    # 传入集合名 "user_profiles" 和用户数据字典 user_dict
    # 得到插入操作结果，赋值给 result
    result = db.insert("user_profiles", user_dict)

    # 返回新创建用户的user_id
    return user_id


def get_user_by_id(user_id: str) -> dict:
    """
    根据用户ID获取用户信息

    通过user_id查询用户基本信息，用于返回注册成功的用户信息。

    参数:
        user_id: 用户唯一标识符

    返回:
        dict: 用户信息字典，包含user_id, email（不再返回username）
    """
    # 创建 DatabaseOperations 实例
    db = DatabaseOperations()

    # 构建查询条件：根据user_id查找
    filter_condition = {"user_id": user_id}

    # 指定返回字段：只返回user_id, email（不再返回username）
    projection = {"user_id": 1, "email": 1, "_id": 0}

    # 调用 DatabaseOperations.find() 方法查询用户信息
    # 传入集合名 "user_profiles"、查询条件 filter_condition 和字段投影 projection
    # 得到查询结果列表，赋值给 users
    users = db.find("user_profiles", filter_condition, projection)

    # 如果找到用户，返回第一个结果，否则返回空字典
    return users[0] if users else {}


def get_user_by_username(username: str) -> dict:
    """
    根据用户名获取用户信息

    通过用户名（实际上是邮箱）查询用户的完整信息，包括加密密码，用于登录验证。

    参数:
        username: 用户名字符串（实际上是邮箱）

    返回:
        dict: 用户完整信息字典，包含user_id, username, email, hashed_password
    """
    # 创建 DatabaseOperations 实例
    db = DatabaseOperations()

    # 构建查询条件：根据用户名查找
    filter_condition = {"username": username}

    # 指定返回字段：返回所有字段，包括密码哈希
    projection = {"user_id": 1, "username": 1, "email": 1, "hashed_password": 1, "_id": 0}

    # 调用 DatabaseOperations.find() 方法查询用户信息
    # 传入集合名 "user_profiles"、查询条件 filter_condition 和字段投影 projection
    # 得到查询结果列表，赋值给 users
    users = db.find("user_profiles", filter_condition, projection)

    # 如果找到用户，返回第一个结果，否则返回空字典
    return users[0] if users else {}


def get_user_by_email(email: str) -> dict:
    """
    根据邮箱获取用户信息

    通过邮箱地址查询用户的完整信息，用于重置密码等功能。

    参数:
        email: 用户邮箱地址字符串

    返回:
        dict: 用户完整信息字典，包含user_id, username, email, hashed_password
    """
    # 创建 DatabaseOperations 实例
    db = DatabaseOperations()

    # 构建查询条件：根据邮箱查找
    filter_condition = {"email": email}

    # 指定返回字段：返回所有字段，包括密码哈希
    projection = {"user_id": 1, "username": 1, "email": 1, "hashed_password": 1, "_id": 0}

    # 调用 DatabaseOperations.find() 方法查询用户信息
    # 传入集合名 "user_profiles"、查询条件 filter_condition 和字段投影 projection
    # 得到查询结果列表，赋值给 users
    users = db.find("user_profiles", filter_condition, projection)

    # 如果找到用户，返回第一个结果，否则返回空字典
    return users[0] if users else {}


def link_oauth_to_existing_email(email: str, provider: str, oauth_id: str) -> None:
    """
    将OAuth账户绑定到现有邮箱用户

    为已存在的邮箱用户添加OAuth账户绑定信息。
    用于在用户先通过邮箱注册，后通过OAuth登录时的账户合并。

    参数:
        email: 现有用户的邮箱地址字符串
        provider: OAuth提供商名称（如"google"、"facebook"）
        oauth_id: OAuth平台的用户ID字符串

    异常:
        ValueError: 当邮箱不存在时抛出异常
    """
    # 创建 DatabaseOperations 实例
    db = DatabaseOperations()

    # 构建查询条件：根据邮箱查找现有用户
    filter_condition = {"email": email}

    # 定义需要更新的OAuth绑定字段名
    oauth_field = f"oauth_{provider}_id"

    # 构建更新数据：添加OAuth ID字段
    update_data = {oauth_field: oauth_id}

    # 调用 DatabaseOperations.update() 方法更新用户信息
    # 传入集合名 "user_profiles"、查询条件 filter_condition 和更新数据 update_data
    # 结果赋值给 update_result，用于检查更新是否成功
    update_result = db.update("user_profiles", filter_condition, update_data)

    # 检查更新是否成功（至少匹配到一个文档）
    if update_result.matched_count == 0:
        raise ValueError(f"邮箱 {email} 不存在，无法绑定OAuth账户")


def set_user_password_by_email(email: str, hashed_password: str) -> str:
    """
    为指定邮箱的用户设置密码

    用于OAuth用户首次设置密码，或重置现有用户的密码。
    通过邮箱查找用户并更新密码哈希。

    参数:
        email: 用户邮箱地址字符串
        hashed_password: bcrypt加密后的密码哈希字符串

    返回:
        str: 用户的user_id字符串

    异常:
        ValueError: 当邮箱不存在时抛出异常
    """
    # 创建 DatabaseOperations 实例
    db = DatabaseOperations()

    # 第一步：通过邮箱查找用户，获取user_id
    # 调用 get_user_by_email 函数通过邮箱查找用户信息
    # 传入邮箱地址，得到用户数据字典或None
    user_data = get_user_by_email(email)
    if not user_data:
        raise ValueError(f"邮箱 {email} 不存在，无法设置密码")

    # 从用户数据中提取user_id，用于数据库更新操作
    user_id = user_data["user_id"]

    # 第二步：使用user_id作为查询条件更新密码
    # 构建查询条件：根据user_id查找用户（满足数据库归档要求）
    filter_condition = {"user_id": user_id}

    # 构建更新数据：设置新的密码哈希
    update_data = {"hashed_password": hashed_password}

    # 调用 DatabaseOperations.update() 方法更新用户密码
    # 传入集合名 "user_profiles"、user_id查询条件和更新数据
    # 结果赋值给 update_result，用于检查更新是否成功
    update_result = db.update("user_profiles", filter_condition, update_data)

    # 检查更新是否成功（至少匹配到一个文档）
    if update_result.matched_count == 0:
        raise ValueError(f"用户 {user_id} 密码更新失败")

    # 返回用户的user_id
    return user_id


def update_user_data(username: str, updated_fields: dict) -> bool:
    """
    更新用户数据

    根据用户名更新数据库中的用户信息，支持更新邮箱、用户名、密码等字段。
    用于用户设置更新功能。

    参数:
        username: 用户名字符串（实际上是邮箱）
        updated_fields: 需要更新的字段字典

    返回:
        bool: 更新成功返回True，失败返回False
    """
    # DatabaseOperations() 通过调用创建数据库操作实例
    # 赋值给 db 变量，用于执行数据库查询和更新操作
    db = DatabaseOperations()

    # filter_condition 通过字典创建查询条件
    # "username" 键赋值为传入的用户名，用于定位特定用户记录
    filter_condition = {"username": username}

    try:
        # db.update() 通过调用更新数据库中的用户记录
        # 传入集合名 "user_profiles"、查询条件 filter_condition 和更新字段字典 updated_fields
        # 返回更新结果对象，赋值给 update_result 变量
        update_result = db.update("user_profiles", filter_condition, updated_fields)

        # update_result.modified_count 通过属性访问获取实际更新的文档数量
        # > 0 条件判断检查是否有文档被更新
        # 返回布尔值表示更新是否成功
        return update_result.modified_count > 0

    except Exception as e:
        # 异常处理，当数据库更新操作失败时返回False
        return False


def check_user_is_oauth_only(email: str) -> bool:
    """
    检查用户是否为纯OAuth用户（没有设置密码）

    通过检查用户的密码哈希是否为OAuth自动生成的虚拟密码来判断。
    用于区分OAuth用户和完整注册用户。

    参数:
        email: 用户邮箱地址字符串

    返回:
        bool: 如果用户只有OAuth登录方式返回True，否则返回False
    """
    # get_user_by_username() 通过调用根据邮箱获取用户信息
    # 传入邮箱地址，返回用户数据字典或空字典
    # 赋值给 user_data 变量存储用户信息
    user_data = get_user_by_username(email)

    # if 条件判断检查用户是否存在
    if not user_data:
        # return 语句返回False，表示用户不存在
        return False

    # user_data.get() 通过调用获取用户的密码哈希字段
    # 传入 "hashed_password" 键名和默认值空字符串
    # 返回密码哈希字符串，赋值给 hashed_password 变量
    hashed_password = user_data.get("hashed_password", "")

    # if 条件判断检查密码哈希是否为空或长度异常
    if not hashed_password or len(hashed_password) < 10:
        # return 语句返回True，表示是OAuth用户
        return True

    # 可以在这里添加更复杂的逻辑来识别虚拟密码
    # 例如：检查密码哈希是否符合OAuth自动生成密码的特征

    # return 语句返回False，表示是完整注册用户
    return False
