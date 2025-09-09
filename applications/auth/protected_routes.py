# 受保护路由处理模块
# 实现需要JWT认证才能访问的路由逻辑

from typing import Dict, Any
from .auth_middleware import AuthenticatedUser
from .schemas import UserProfileResponse, UserSettingsUpdateRequest, RefreshTokenRequest, LogoutResponse
from .tokens import refresh_access_token
from .repository import get_user_by_username, update_user_data
from .hashing import verify_password, hash_password
from .exceptions import InvalidCredentialsError, InvalidInputError


def handle_get_user_profile(current_user: AuthenticatedUser) -> dict:
    """
    处理获取用户信息请求

    根据当前认证用户的信息，返回用户的详细信息。
    这是一个受保护的路由，需要有效的JWT访问令牌。

    参数:
        current_user: 当前已认证的用户对象

    返回:
        dict: 响应字典，包含success状态和用户信息
    """
    try:
        # get_user_by_username() 通过调用从数据库获取用户完整信息
        # 传入当前用户的用户名，返回用户数据字典或空字典
        # 赋值给 user_data 变量存储完整用户数据
        user_data = get_user_by_username(current_user.username)
        
        # if 条件判断检查用户数据是否存在
        if not user_data:
            # return 语句返回失败响应，表示用户不存在
            return {
                "success": False,
                "error": "用户不存在",
                "error_type": "USER_NOT_FOUND"
            }
        
        # UserProfileResponse() 通过调用创建用户信息响应对象
        # user_id 参数传入用户ID
        # email 参数传入用户邮箱
        # username 参数传入用户名
        # created_at 参数从用户数据获取创建时间，如果不存在则为None
        # updated_at 参数从用户数据获取更新时间，如果不存在则为None
        # 返回包含用户信息的响应对象
        user_profile = UserProfileResponse(
            user_id=current_user.user_id,
            email=current_user.email,
            username=current_user.username,
            created_at=user_data.get("created_at"),
            updated_at=user_data.get("updated_at")
        )
        
        # return 语句返回成功响应，包含用户信息
        return {
            "success": True,
            "data": user_profile.model_dump(),
            "message": "获取用户信息成功"
        }
    
    except Exception as e:
        # return 语句返回失败响应，表示获取用户信息时发生错误
        return {
            "success": False,
            "error": "获取用户信息失败",
            "error_type": "GET_PROFILE_ERROR"
        }


def handle_update_user_settings(request_data: dict, current_user: AuthenticatedUser) -> dict:
    """
    处理更新用户设置请求

    允许用户更新邮箱地址和密码。需要提供当前密码进行身份验证。
    这是一个受保护的路由，需要有效的JWT访问令牌。

    参数:
        request_data: HTTP请求的数据字典，包含设置更新信息
        current_user: 当前已认证的用户对象

    返回:
        dict: 响应字典，包含success状态和更新结果
    """
    try:
        # UserSettingsUpdateRequest() 通过调用创建用户设置更新请求对象
        # 传入请求数据字典，验证数据格式和类型
        # 赋值给 update_request 变量存储验证后的请求数据
        update_request = UserSettingsUpdateRequest(**request_data)
        
        # get_user_by_username() 通过调用从数据库获取当前用户完整信息
        # 传入当前用户的用户名，返回用户数据字典
        # 赋值给 user_data 变量存储用户数据
        user_data = get_user_by_username(current_user.username)
        
        # if 条件判断检查用户数据是否存在
        if not user_data:
            # return 语句返回失败响应，表示用户不存在
            return {
                "success": False,
                "error": "用户不存在",
                "error_type": "USER_NOT_FOUND"
            }
        
        # user_data.get() 通过调用获取存储的加密密码哈希
        # 传入 "hashed_password" 键名，返回密码哈希字符串
        # 赋值给 stored_hashed_password 变量
        stored_hashed_password = user_data.get("hashed_password")
        
        # verify_password() 通过调用验证当前密码是否正确
        # 传入请求中的当前密码和存储的密码哈希
        # 返回验证结果布尔值，赋值给 is_current_password_valid 变量
        is_current_password_valid = verify_password(
            update_request.current_password, 
            stored_hashed_password
        )
        
        # if 条件判断检查当前密码验证是否失败
        if not is_current_password_valid:
            # return 语句返回失败响应，表示当前密码错误
            return {
                "success": False,
                "error": "当前密码错误",
                "error_type": "INVALID_CURRENT_PASSWORD"
            }
        
        # updated_fields 通过字典创建需要更新的字段集合
        updated_fields = {}
        
        # if 条件判断检查是否需要更新邮箱
        if update_request.email and update_request.email != current_user.email:
            # updated_fields["email"] 通过字典赋值设置新邮箱
            updated_fields["email"] = update_request.email
            # updated_fields["username"] 通过字典赋值设置新用户名（使用邮箱）
            updated_fields["username"] = update_request.email
        
        # if 条件判断检查是否需要更新密码
        if update_request.new_password:
            # hash_password() 通过调用对新密码进行哈希加密
            # 传入新密码字符串，返回加密后的密码哈希
            # 赋值给 updated_fields["hashed_password"] 字典项
            updated_fields["hashed_password"] = hash_password(update_request.new_password)
        
        # if 条件判断检查是否有需要更新的字段
        if not updated_fields:
            # return 语句返回失败响应，表示没有提供更新数据
            return {
                "success": False,
                "error": "没有提供需要更新的信息",
                "error_type": "NO_UPDATE_DATA"
            }
        
        # update_user_data() 通过调用更新数据库中的用户数据
        # 传入当前用户名和更新字段字典
        # 返回更新结果布尔值，赋值给 update_result 变量
        update_result = update_user_data(current_user.username, updated_fields)
        
        # if 条件判断检查更新操作是否成功
        if update_result:
            # return 语句返回成功响应
            return {
                "success": True,
                "message": "用户设置更新成功",
                "updated_fields": list(updated_fields.keys())
            }
        else:
            # return 语句返回失败响应，表示数据库更新失败
            return {
                "success": False,
                "error": "设置更新失败",
                "error_type": "UPDATE_FAILED"
            }
    
    except InvalidInputError as e:
        # return 语句返回失败响应，处理输入数据无效的异常
        return {
            "success": False,
            "error": str(e),
            "error_type": "INVALID_INPUT"
        }
    
    except Exception as e:
        # return 语句返回失败响应，处理其他未预期的异常
        return {
            "success": False,
            "error": "更新用户设置失败",
            "error_type": "UPDATE_SETTINGS_ERROR"
        }


def handle_refresh_token(request_data: dict) -> dict:
    """
    处理刷新令牌请求

    使用有效的刷新令牌生成新的访问令牌和刷新令牌对。
    这个路由不需要访问令牌认证，但需要有效的刷新令牌。

    参数:
        request_data: HTTP请求的数据字典，包含刷新令牌

    返回:
        dict: 响应字典，包含success状态和新的令牌对
    """
    try:
        # RefreshTokenRequest() 通过调用创建刷新令牌请求对象
        # 传入请求数据字典，验证数据格式和类型
        # 赋值给 refresh_request 变量存储验证后的请求数据
        refresh_request = RefreshTokenRequest(**request_data)
        
        # refresh_access_token() 通过调用使用刷新令牌生成新的令牌对
        # 传入刷新令牌字符串，返回包含新令牌的字典
        # 赋值给 new_tokens 变量存储新生成的令牌对
        new_tokens = refresh_access_token(refresh_request.refresh_token)
        
        # return 语句返回成功响应，包含新的令牌对
        return {
            "success": True,
            "data": {
                "access_token": new_tokens["access_token"],
                "refresh_token": new_tokens["refresh_token"],
                "token_type": "Bearer"
            },
            "message": "令牌刷新成功"
        }
    
    except ValueError as e:
        # ValueError 抛出认证错误异常，让上层转换为401状态码
        from .exceptions import InvalidCredentialsError
        raise InvalidCredentialsError("刷新令牌无效或已过期")
    
    except Exception as e:
        # Exception 对于其他异常，包装为系统错误重新抛出
        raise RuntimeError(f"令牌刷新失败: {str(e)}")


def handle_logout(current_user: AuthenticatedUser) -> dict:
    """
    处理用户登出请求

    执行用户登出操作。在简单实现中，只是返回成功响应。
    在生产环境中，可以将令牌添加到黑名单或执行其他清理操作。
    这是一个受保护的路由，需要有效的JWT访问令牌。

    参数:
        current_user: 当前已认证的用户对象

    返回:
        dict: 响应字典，包含success状态和登出消息
    """
    try:
        # 在生产环境中，这里可以添加以下功能：
        # 1. 将当前访问令牌添加到黑名单
        # 2. 清理用户的活跃会话记录
        # 3. 记录登出日志
        # 4. 通知其他服务用户已登出
        
        # LogoutResponse() 通过调用创建登出响应对象
        # success 参数设置为 True 表示登出成功
        # message 参数设置为成功消息字符串
        # 返回包含登出结果的响应对象
        logout_response = LogoutResponse(
            success=True,
            message=f"用户 {current_user.username} 已成功登出"
        )
        
        # return 语句返回成功响应，包含登出信息
        return {
            "success": True,
            "data": logout_response.model_dump(),
            "message": "登出成功"
        }
    
    except Exception as e:
        # return 语句返回失败响应，处理登出过程中的异常
        return {
            "success": False,
            "error": "登出过程中发生错误",
            "error_type": "LOGOUT_ERROR"
        }
