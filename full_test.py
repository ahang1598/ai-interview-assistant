import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_full_user_flow():
    print("=== AI面试助手用户系统完整测试 ===\n")
    
    # 1. 注册新用户
    print("1. 注册新用户...")
    register_data = {
        "username": "fulltestuser",
        "email": "fulltest@example.com",
        "password": "initialpassword"
    }
    
    try:
        register_response = requests.post(
            f"{BASE_URL}/auth/register",
            headers={"Content-Type": "application/json"},
            data=json.dumps(register_data)
        )
        print(f"   状态码: {register_response.status_code}")
        if register_response.status_code == 200:
            print("   ✓ 用户注册成功")
            user_data = register_response.json()
            print(f"   用户信息: ID={user_data['id']}, 用户名={user_data['username']}")
        elif register_response.status_code == 400:
            print("   ! 用户已存在，继续测试")
        else:
            print(f"   ✗ 注册失败: {register_response.text}")
            return
    except Exception as e:
        print(f"   ✗ 注册异常: {e}")
        return
    
    # 2. 用户登录
    print("\n2. 用户登录...")
    try:
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={"username": "fulltestuser", "password": "initialpassword"}
        )
        print(f"   状态码: {login_response.status_code}")
        if login_response.status_code == 200:
            login_data = login_response.json()
            token = login_data["access_token"]
            print("   ✓ 登录成功")
            print(f"   Token: {token[:30]}...")
        else:
            print(f"   ✗ 登录失败: {login_response.text}")
            return
    except Exception as e:
        print(f"   ✗ 登录异常: {e}")
        return
    
    # 3. 获取用户信息
    print("\n3. 获取用户信息...")
    try:
        user_response = requests.get(
            f"{BASE_URL}/auth/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        print(f"   状态码: {user_response.status_code}")
        if user_response.status_code == 200:
            user_info = user_response.json()
            print("   ✓ 获取用户信息成功")
            print(f"   用户详情: ID={user_info['id']}, 用户名={user_info['username']}, 邮箱={user_info['email']}")
            print(f"   创建时间: {user_info['created_at']}")
        else:
            print(f"   ✗ 获取用户信息失败: {user_response.text}")
    except Exception as e:
        print(f"   ✗ 获取用户信息异常: {e}")
    
    # 4. 修改密码
    print("\n4. 修改密码...")
    try:
        change_password_data = {
            "current_password": "initialpassword",
            "new_password": "newsecurepassword"
        }
        password_response = requests.put(
            f"{BASE_URL}/auth/users/me/password",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            },
            data=json.dumps(change_password_data)
        )
        print(f"   状态码: {password_response.status_code}")
        if password_response.status_code == 200:
            print("   ✓ 密码修改成功")
            updated_user = password_response.json()
            print(f"   更新后的用户信息: ID={updated_user['id']}, 用户名={updated_user['username']}")
        else:
            print(f"   ✗ 密码修改失败: {password_response.text}")
    except Exception as e:
        print(f"   ✗ 密码修改异常: {e}")
    
    # 5. 使用新密码登录
    print("\n5. 使用新密码登录...")
    try:
        new_login_response = requests.post(
            f"{BASE_URL}/auth/login",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={"username": "fulltestuser", "password": "newsecurepassword"}
        )
        print(f"   状态码: {new_login_response.status_code}")
        if new_login_response.status_code == 200:
            new_login_data = new_login_response.json()
            new_token = new_login_data["access_token"]
            print("   ✓ 新密码登录成功")
            print(f"   新Token: {new_token[:30]}...")
        else:
            print(f"   ✗ 新密码登录失败: {new_login_response.text}")
    except Exception as e:
        print(f"   ✗ 新密码登录异常: {e}")
    
    # 6. 验证旧密码已失效
    print("\n6. 验证旧密码已失效...")
    try:
        old_login_response = requests.post(
            f"{BASE_URL}/auth/login",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={"username": "fulltestuser", "password": "initialpassword"}
        )
        print(f"   状态码: {old_login_response.status_code}")
        if old_login_response.status_code == 401:
            print("   ✓ 旧密码已失效（预期结果）")
        else:
            print(f"   ! 旧密码仍然有效（异常情况）: {old_login_response.text}")
    except Exception as e:
        print(f"   ✗ 验证旧密码异常: {e}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_full_user_flow()