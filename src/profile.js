// API基础URL
const API_BASE_URL = 'http://localhost:8000';

// DOM元素
const userInfo = document.getElementById('user-info');
const usernameSpan = document.getElementById('username');
const logoutBtn = document.getElementById('logout-btn');
const profileInfo = document.getElementById('profile-info');
const changePasswordForm = document.getElementById('change-password-form');
const passwordMessage = document.getElementById('password-message');

// 检查用户是否已登录
checkAuthStatus();

// 事件监听器
logoutBtn.addEventListener('click', handleLogout);
changePasswordForm.addEventListener('submit', handleChangePassword);

/**
 * 检查用户认证状态
 */
function checkAuthStatus() {
    const token = localStorage.getItem('access_token');
    const username = localStorage.getItem('username');
    
    if (token && username) {
        // 用户已登录
        usernameSpan.textContent = username;
        loadProfileInfo();
    } else {
        // 用户未登录，重定向到登录页面
        window.location.href = 'auth.html';
    }
}

/**
 * 加载用户资料信息
 */
async function loadProfileInfo() {
    const token = localStorage.getItem('access_token');
    const username = localStorage.getItem('username');
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/users/me`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const userData = await response.json();
        
        if (response.ok) {
            // 显示用户信息
            profileInfo.innerHTML = `
                <div class="profile-field">
                    <strong>用户ID:</strong> ${userData.id}
                </div>
                <div class="profile-field">
                    <strong>用户名:</strong> ${userData.username}
                </div>
                <div class="profile-field">
                    <strong>邮箱:</strong> ${userData.email}
                </div>
                <div class="profile-field">
                    <strong>注册时间:</strong> ${userData.created_at || '未知'}
                </div>
                <div class="profile-field">
                    <strong>最后更新:</strong> ${userData.updated_at || '未知'}
                </div>
            `;
        } else {
            profileInfo.innerHTML = '<p>加载用户信息失败</p>';
        }
    } catch (error) {
        console.error('加载用户信息错误:', error);
        profileInfo.innerHTML = '<p>加载用户信息时出错</p>';
    }
}

/**
 * 处理用户退出
 */
function handleLogout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('username');
    window.location.href = 'auth.html';
}

/**
 * 处理修改密码
 */
async function handleChangePassword(event) {
    event.preventDefault();
    
    const token = localStorage.getItem('access_token');
    
    const currentPassword = document.getElementById('current-password').value;
    const newPassword = document.getElementById('new-password').value;
    const confirmNewPassword = document.getElementById('confirm-new-password').value;
    
    // 确认新密码匹配
    if (newPassword !== confirmNewPassword) {
        showMessage(passwordMessage, '两次输入的新密码不匹配', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/users/me/password`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                current_password: currentPassword,
                new_password: newPassword
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage(passwordMessage, '密码修改成功！', 'success');
            // 清空表单
            changePasswordForm.reset();
        } else {
            showMessage(passwordMessage, data.detail || '密码修改失败', 'error');
        }
    } catch (error) {
        showMessage(passwordMessage, `密码修改失败: ${error.message}`, 'error');
    }
}

/**
 * 显示消息
 */
function showMessage(element, message, type) {
    element.textContent = message;
    element.className = `message ${type}`;
    element.style.display = 'block';
    
    // 3秒后自动隐藏成功消息
    if (type === 'success') {
        setTimeout(() => {
            element.style.display = 'none';
        }, 3000);
    }
}