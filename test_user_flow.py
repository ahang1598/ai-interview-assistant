import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_user_flow():
    # 1. 注册用户
    print("1. 注册用户...")
    register_data = {
        "username": "ahang1",
        "email": "ahang1@example.com",
        "password": "123"
    }
    
    try:
        register_response = requests.post(
            f"{BASE_URL}/auth/register",
            headers={"Content-Type": "application/json"},
            data=json.dumps(register_data)
        )
        print(f"注册响应: {register_response.status_code}")
        print(f"注册内容: {register_response.text}")
    except Exception as e:
        print(f"注册异常: {e}")
    
    # 2. 登录
    print("\n2. 用户登录...")
    try:
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={"username": "ahang1", "password": "123"}
        )
        print(f"登录响应: {login_response.status_code}")
        login_data = login_response.json()
        print(f"登录内容: {login_data}")
        
        if login_response.status_code == 200:
            token = login_data["access_token"]
            print(f"获取到token: {token}")
            
            # 3. 获取用户信息
            print("\n3. 获取用户信息...")
            user_response = requests.get(
                f"{BASE_URL}/auth/users/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            print(f"用户信息响应: {user_response.status_code}")
            print(f"用户信息内容: {user_response.json()}")
            
            # 4. 修改密码
            print("\n4. 修改密码...")
            change_password_data = {
                "current_password": "123",
                "new_password": "newpassword123"
            }
            password_response = requests.put(
                f"{BASE_URL}/auth/users/me/password",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}"
                },
                data=json.dumps(change_password_data)
            )
            print(f"修改密码响应: {password_response.status_code}")
            print(f"修改密码内容: {password_response.json()}")
            
            # 5. 使用新密码登录
            print("\n5. 使用新密码登录...")
            new_login_response = requests.post(
                f"{BASE_URL}/auth/login",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data={"username": "ahang1", "password": "newpassword123"}
            )
            print(f"新密码登录响应: {new_login_response.status_code}")
            print(f"新密码登录内容: {new_login_response.json()}")
    except Exception as e:
        print(f"流程异常: {e}")

if __name__ == "__main__":
    test_user_flow()