// API基础URL
const API_BASE_URL = 'http://localhost:8000';

// DOM元素
const userInfo = document.getElementById('user-info');
const usernameSpan = document.getElementById('username');
const logoutBtn = document.getElementById('logout-btn');
const createKbForm = document.getElementById('create-kb-form');
const kbNameInput = document.getElementById('kb-name');
const kbDescriptionInput = document.getElementById('kb-description');
const createKbMessage = document.getElementById('create-kb-message');
const knowledgeBasesList = document.getElementById('knowledge-bases-list');

// 检查用户是否已登录
checkAuthStatus();

// 事件监听器
logoutBtn.addEventListener('click', handleLogout);
createKbForm.addEventListener('submit', handleCreateKnowledgeBase);

/**
 * 检查用户认证状态
 */
function checkAuthStatus() {
    const token = localStorage.getItem('access_token');
    const username = localStorage.getItem('username');
    
    if (token && username) {
        // 用户已登录
        usernameSpan.textContent = username;
        loadKnowledgeBases();
    } else {
        // 用户未登录，重定向到登录页面
        window.location.href = 'auth.html';
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
 * 加载用户的知识库列表
 */
async function loadKnowledgeBases() {
    const token = localStorage.getItem('access_token');
    
    try {
        const response = await fetch(`${API_BASE_URL}/knowledge-bases`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const knowledgeBases = await response.json();
            displayKnowledgeBases(knowledgeBases);
        } else {
            knowledgeBasesList.innerHTML = '<p>加载知识库列表失败</p>';
        }
    } catch (error) {
        console.error('加载知识库列表错误:', error);
        knowledgeBasesList.innerHTML = '<p>加载知识库列表时出错</p>';
    }
}

/**
 * 显示知识库列表
 */
function displayKnowledgeBases(knowledgeBases) {
    if (knowledgeBases.length === 0) {
        knowledgeBasesList.innerHTML = '<p>您还没有创建任何知识库</p>';
        return;
    }
    
    let html = '<div class="knowledge-bases-grid">';
    
    knowledgeBases.forEach(kb => {
        html += `
            <div class="knowledge-base-card">
                <h3>${kb.name}</h3>
                <p class="kb-description">${kb.description || '无描述'}</p>
                <p class="kb-meta">
                    <span>创建时间: ${kb.created_at ? new Date(kb.created_at).toLocaleString() : '未知'}</span>
                    <span class="kb-status ${kb.is_active ? 'active' : 'inactive'}">
                        ${kb.is_active ? '激活' : '未激活'}
                    </span>
                </p>
                <div class="kb-actions">
                    <button onclick="viewKnowledgeBase(${kb.id})" class="submit-btn">查看详情</button>
                    <button onclick="deleteKnowledgeBase(${kb.id})" class="delete-btn">删除</button>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    knowledgeBasesList.innerHTML = html;
}

/**
 * 处理创建知识库
 */
async function handleCreateKnowledgeBase(event) {
    event.preventDefault();
    
    const token = localStorage.getItem('access_token');
    const name = kbNameInput.value.trim();
    const description = kbDescriptionInput.value.trim();
    
    if (!name) {
        showMessage(createKbMessage, '请输入知识库名称', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/knowledge-bases`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ name, description })
        });
        
        if (response.ok) {
            showMessage(createKbMessage, '知识库创建成功！', 'success');
            createKbForm.reset();
            loadKnowledgeBases(); // 重新加载列表
        } else {
            const errorData = await response.json();
            showMessage(createKbMessage, `创建失败: ${errorData.detail}`, 'error');
        }
    } catch (error) {
        showMessage(createKbMessage, `创建失败: ${error.message}`, 'error');
    }
}

/**
 * 查看知识库详情
 */
function viewKnowledgeBase(kbId) {
    // 重定向到知识库详情页面
    window.location.href = `kb-detail.html?id=${kbId}`;
}

/**
 * 删除知识库
 */
async function deleteKnowledgeBase(kbId) {
    if (!confirm('确定要删除这个知识库吗？此操作不可撤销。')) {
        return;
    }
    
    const token = localStorage.getItem('access_token');
    
    try {
        const response = await fetch(`${API_BASE_URL}/knowledge-bases/${kbId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            loadKnowledgeBases(); // 重新加载列表
        } else {
            const errorData = await response.json();
            alert(`删除失败: ${errorData.detail}`);
        }
    } catch (error) {
        alert(`删除失败: ${error.message}`);
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

/**
 * 返回主页
 */
function goHome() {
    window.location.href = 'index.html';
}