# 用户数据仓库层
# 封装对数据库的操作，通过调用 utilities.mongodb_connector 中的方法实现

import uuid
from utilities.mongodb_connector import DatabaseOperations
from utilities.time import Time
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

    生成唯一的user_id，将用户静态信息插入到user_profiles，动态状态信息插入到user_status。
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

    # 创建 DatabaseOperations 实例
    db = DatabaseOperations()

    # 准备用户静态画像数据（存储到 user_profiles）
    profile_data = {
        "user_id": user_id,
        "username": username,
        "email": email
    }

    # 准备用户动态状态数据（存储到 user_status）
    status_data = {
        "user_id": user_id,
        "hashed_password": hashed_password
    }

    # 调用 DatabaseOperations.insert() 方法插入用户画像数据
    # 传入集合名 "user_profiles" 和画像数据字典 profile_data
    # 得到插入操作结果，赋值给 profile_result
    profile_result = db.insert("user_profiles", profile_data)

    # 调用 DatabaseOperations.insert() 方法插入用户状态数据
    # 传入集合名 "user_status" 和状态数据字典 status_data
    # 得到插入操作结果，赋值给 status_result
    status_result = db.insert("user_status", status_data)

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
    从user_profiles获取静态信息，从user_status获取动态状态信息。

    参数:
        username: 用户名字符串（实际上是邮箱）

    返回:
        dict: 用户完整信息字典，包含user_id, username, email, hashed_password
    """
    # 创建 DatabaseOperations 实例
    db = DatabaseOperations()

    # 构建查询条件：根据用户名查找
    filter_condition = {"username": username}

    # 指定返回字段：返回画像字段（不含密码）
    projection = {"user_id": 1, "username": 1, "email": 1, "_id": 0}

    # 调用 DatabaseOperations.find() 方法查询用户画像信息
    # 传入集合名 "user_profiles"、查询条件 filter_condition 和字段投影 projection
    # 得到查询结果列表，赋值给 users
    users = db.find("user_profiles", filter_condition, projection)

    # 如果没有找到用户，返回空字典
    if not users:
        return {}

    # 获取用户基础信息
    user_info = users[0]
    user_id = user_info["user_id"]

    # 构建查询条件：根据user_id查找状态信息
    status_filter = {"user_id": user_id}

    # 指定返回字段：返回密码哈希和OAuth字段
    status_projection = {"hashed_password": 1, "oauth_google_id": 1, "oauth_facebook_id": 1, "_id": 0}

    # 调用 DatabaseOperations.find() 方法查询用户状态信息
    # 传入集合名 "user_status"、查询条件 status_filter 和字段投影 status_projection
    # 得到查询结果列表，赋值给 status_list
    status_list = db.find("user_status", status_filter, status_projection)

    # 合并画像信息和状态信息
    if status_list:
        user_info.update(status_list[0])

    return user_info


def get_user_by_email(email: str) -> dict:
    """
    根据邮箱获取用户信息

    通过邮箱地址查询用户的完整信息，用于重置密码等功能。
    从user_profiles获取静态信息，从user_status获取动态状态信息。

    参数:
        email: 用户邮箱地址字符串

    返回:
        dict: 用户完整信息字典，包含user_id, username, email, hashed_password
    """
    # 创建 DatabaseOperations 实例
    db = DatabaseOperations()

    # 构建查询条件：根据邮箱查找
    filter_condition = {"email": email}

    # 指定返回字段：返回画像字段（不含密码）
    projection = {"user_id": 1, "username": 1, "email": 1, "_id": 0}

    # 调用 DatabaseOperations.find() 方法查询用户画像信息
    # 传入集合名 "user_profiles"、查询条件 filter_condition 和字段投影 projection
    # 得到查询结果列表，赋值给 users
    users = db.find("user_profiles", filter_condition, projection)

    # 如果没有找到用户，返回空字典
    if not users:
        return {}

    # 获取用户基础信息
    user_info = users[0]
    user_id = user_info["user_id"]

    # 构建查询条件：根据user_id查找状态信息
    status_filter = {"user_id": user_id}

    # 指定返回字段：返回密码哈希和OAuth字段
    status_projection = {"hashed_password": 1, "oauth_google_id": 1, "oauth_facebook_id": 1, "_id": 0}

    # 调用 DatabaseOperations.find() 方法查询用户状态信息
    # 传入集合名 "user_status"、查询条件 status_filter 和字段投影 status_projection
    # 得到查询结果列表，赋值给 status_list
    status_list = db.find("user_status", status_filter, status_projection)

    # 合并画像信息和状态信息
    if status_list:
        user_info.update(status_list[0])

    return user_info


def link_oauth_to_existing_email(email: str, provider: str, oauth_id: str) -> None:
    """
    将OAuth账户绑定到现有邮箱用户

    为已存在的邮箱用户添加OAuth账户绑定信息到user_status集合。
    用于在用户先通过邮箱注册，后通过OAuth登录时的账户合并。
    OAuth绑定信息属于动态状态，归档旧状态字段到user_archive。

    参数:
        email: 现有用户的邮箱地址字符串
        provider: OAuth提供商名称（如"google"、"facebook"）
        oauth_id: OAuth平台的用户ID字符串

    异常:
        ValueError: 当邮箱不存在时抛出异常
    """
    # 创建 DatabaseOperations 实例
    db = DatabaseOperations()

    # 构建查询条件：根据邮箱查找现有用户（从user_profiles获取user_id）
    profile_filter = {"email": email}

    # 调用 DatabaseOperations.find() 方法查询用户画像信息
    # 传入集合名 "user_profiles"、查询条件 profile_filter 和空投影
    # 得到查询结果列表，赋值给 users
    users = db.find("user_profiles", profile_filter, {"user_id": 1, "_id": 0})

    # 检查用户是否存在
    if not users:
        raise ValueError(f"邮箱 {email} 不存在，无法绑定OAuth账户")

    # 获取用户ID
    user_id = users[0]["user_id"]

    # 构建查询条件：根据user_id更新状态信息
    filter_condition = {"user_id": user_id}

    # 定义需要更新的OAuth绑定字段名
    oauth_field = f"oauth_{provider}_id"

    # 构建更新数据：添加OAuth ID字段
    update_data = {oauth_field: oauth_id}

    # 调用 DatabaseOperations.update() 方法更新用户状态信息
    # 传入集合名 "user_status"、查询条件 filter_condition 和更新数据 update_data
    # 该方法内置归档功能，旧OAuth字段值会自动归档到user_archive
    # 归档旧状态字段到 user_archive，原字段已更新
    update_result = db.update("user_status", filter_condition, update_data)

    # 检查更新是否成功（至少匹配到一个文档）
    if update_result.matched_count == 0:
        raise ValueError(f"用户 {user_id} OAuth绑定更新失败")


def set_user_password_by_email(email: str, hashed_password: str) -> str:
    """
    为指定邮箱的用户设置密码

    用于OAuth用户首次设置密码，或重置现有用户的密码。
    通过邮箱查找用户并更新user_status中的密码哈希。
    密码属于动态状态，归档旧状态字段到user_archive。

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
    # 构建查询条件：根据邮箱查找用户（从user_profiles获取user_id）
    profile_filter = {"email": email}

    # 调用 DatabaseOperations.find() 方法查询用户画像信息
    # 传入集合名 "user_profiles"、查询条件 profile_filter 和投影
    # 得到查询结果列表，赋值给 users
    users = db.find("user_profiles", profile_filter, {"user_id": 1, "_id": 0})

    # 检查用户是否存在
    if not users:
        raise ValueError(f"邮箱 {email} 不存在，无法设置密码")

    # 从用户数据中提取user_id，用于数据库更新操作
    user_id = users[0]["user_id"]

    # 第二步：使用user_id作为查询条件更新密码
    # 构建查询条件：根据user_id查找用户状态信息（满足数据库归档要求）
    filter_condition = {"user_id": user_id}

    # 构建更新数据：设置新的密码哈希
    update_data = {"hashed_password": hashed_password}

    # 调用 DatabaseOperations.update() 方法更新用户密码状态
    # 传入集合名 "user_status"、user_id查询条件和更新数据
    # 该方法内置归档功能，旧密码哈希会自动归档到user_archive
    # 归档旧状态字段到 user_archive，原字段已更新
    update_result = db.update("user_status", filter_condition, update_data)

    # 检查更新是否成功（至少匹配到一个文档）
    if update_result.matched_count == 0:
        raise ValueError(f"用户 {user_id} 密码更新失败")

    # 返回用户的user_id
    return user_id


def update_user_data(username: str, updated_fields: dict) -> bool:
    """
    更新用户数据

    根据用户名更新数据库中的用户信息，支持更新邮箱、用户名、密码等字段。
    静态字段（email, username）更新user_profiles，动态字段（hashed_password, oauth_*_id）更新user_status。
    用于用户设置更新功能，动态状态字段归档旧状态字段到user_archive。

    参数:
        username: 用户名字符串（实际上是邮箱）
        updated_fields: 需要更新的字段字典

    返回:
        bool: 更新成功返回True，失败返回False
    """
    # DatabaseOperations() 通过调用创建数据库操作实例
    # 赋值给 db 变量，用于执行数据库查询和更新操作
    db = DatabaseOperations()

    try:
        # 第一步：获取用户ID
        # 构建查询条件：根据用户名查找用户（从user_profiles获取user_id）
        profile_filter = {"username": username}

        # 调用 DatabaseOperations.find() 方法查询用户画像信息
        # 传入集合名 "user_profiles"、查询条件 profile_filter 和投影
        # 得到查询结果列表，赋值给 users
        users = db.find("user_profiles", profile_filter, {"user_id": 1, "_id": 0})

        # 检查用户是否存在
        if not users:
            return False

        # 从用户数据中提取user_id
        user_id = users[0]["user_id"]

        # 第二步：分离静态字段和动态字段
        # 定义动态状态字段列表
        status_fields = ["hashed_password", "oauth_google_id", "oauth_facebook_id"]

        # 分离静态画像字段和动态状态字段
        profile_updates = {}
        status_updates = {}

        for field, value in updated_fields.items():
            if field in status_fields:
                status_updates[field] = value
            else:
                profile_updates[field] = value

        # 第三步：更新静态画像字段
        if profile_updates:
            # filter_condition 通过字典创建查询条件
            # "username" 键赋值为传入的用户名，用于定位特定用户记录
            filter_condition = {"username": username}

            # db.update() 通过调用更新数据库中的用户画像记录
            # 传入集合名 "user_profiles"、查询条件 filter_condition 和更新字段字典 profile_updates
            # 返回更新结果对象，赋值给 profile_result 变量
            profile_result = db.update("user_profiles", filter_condition, profile_updates)

        # 第四步：更新动态状态字段
        if status_updates:
            # 构建查询条件：根据user_id更新状态信息
            status_filter = {"user_id": user_id}

            # db.update() 通过调用更新数据库中的用户状态记录
            # 传入集合名 "user_status"、查询条件 status_filter 和更新字段字典 status_updates
            # 该方法内置归档功能，旧状态字段值会自动归档到user_archive
            # 归档旧状态字段到 user_archive，原字段已更新
            status_result = db.update("user_status", status_filter, status_updates)

        # 判断更新是否成功
        success = True
        if profile_updates:
            success = success and (profile_result.modified_count > 0 or profile_result.matched_count > 0)
        if status_updates:
            success = success and (status_result.modified_count > 0 or status_result.matched_count > 0)

        return success

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
