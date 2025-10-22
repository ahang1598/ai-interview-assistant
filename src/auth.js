// 认证相关功能

// API基础URL
const API_BASE_URL = 'http://localhost:8000';

// DOM元素
const loginTab = document.getElementById('login-tab');
const registerTab = document.getElementById('register-tab');
const loginForm = document.getElementById('login-form');
const registerForm = document.getElementById('register-form');
const loginMessage = document.getElementById('login-message');
const registerMessage = document.getElementById('register-message');

// 切换标签
loginTab.addEventListener('click', () => switchTab('login'));
registerTab.addEventListener('click', () => switchTab('register'));

// 表单提交事件
loginForm.addEventListener('submit', handleLogin);
registerForm.addEventListener('submit', handleRegister);

/**
 * 切换标签页
 */
function switchTab(tab) {
    if (tab === 'login') {
        loginTab.classList.add('active');
        registerTab.classList.remove('active');
        loginForm.classList.remove('hidden');
        registerForm.classList.add('hidden');
        clearMessages();
    } else {
        registerTab.classList.add('active');
        loginTab.classList.remove('active');
        registerForm.classList.remove('hidden');
        loginForm.classList.add('hidden');
        clearMessages();
    }
}

/**
 * 清除消息
 */
function clearMessages() {
    loginMessage.className = 'message';
    loginMessage.style.display = 'none';
    registerMessage.className = 'message';
    registerMessage.style.display = 'none';
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

/**
 * 处理登录
 */
async function handleLogin(event) {
    event.preventDefault();
    
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: new URLSearchParams({
                username: username,
                password: password
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // 保存访问令牌到localStorage
            localStorage.setItem('access_token', data.access_token);
            localStorage.setItem('username', username);
            
            showMessage(loginMessage, '登录成功！正在跳转...', 'success');
            
            // 1秒后跳转到主页面
            setTimeout(() => {
                window.location.href = 'index.html';
            }, 1000);
        } else {
            showMessage(loginMessage, data.detail || '登录失败', 'error');
        }
    } catch (error) {
        showMessage(loginMessage, `登录失败: ${error.message}`, 'error');
    }
}

/**
 * 处理注册
 */
async function handleRegister(event) {
    event.preventDefault();
    
    const username = document.getElementById('register-username').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;
    const confirmPassword = document.getElementById('register-confirm-password').value;
    
    // 确认密码匹配
    if (password !== confirmPassword) {
        showMessage(registerMessage, '两次输入的密码不匹配', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: username,
                email: email,
                password: password
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage(registerMessage, '注册成功！请登录。', 'success');
            // 切换到登录标签
            setTimeout(() => {
                switchTab('login');
                // 填充用户名
                document.getElementById('login-username').value = username;
            }, 1500);
        } else {
            showMessage(registerMessage, data.detail || '注册失败', 'error');
        }
    } catch (error) {
        showMessage(registerMessage, `注册失败: ${error.message}`, 'error');
    }
}