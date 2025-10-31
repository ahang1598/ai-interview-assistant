// API基础URL
const API_BASE_URL = 'http://localhost:8000';

// DOM元素
const userInfo = document.getElementById('user-info');
const usernameSpan = document.getElementById('username');
const logoutBtn = document.getElementById('logout-btn');
const kbTitle = document.getElementById('kb-title');
const historyList = document.getElementById('history-list');
const backBtn = document.getElementById('back-btn');

// 获取知识库ID
const urlParams = new URLSearchParams(window.location.search);
const kbId = urlParams.get('kb_id');

// 检查用户是否已登录
checkAuthStatus();

// 事件监听器
logoutBtn.addEventListener('click', handleLogout);
backBtn.addEventListener('click', handleBack);

/**
 * 检查用户认证状态
 */
function checkAuthStatus() {
    const token = localStorage.getItem('access_token');
    const username = localStorage.getItem('username');
    
    if (token && username) {
        // 用户已登录
        usernameSpan.textContent = username;
        if (kbId) {
            loadKnowledgeBaseInfo();
            loadQueryHistory();
        } else {
            historyList.innerHTML = '<p>无效的知识库ID</p>';
        }
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
 * 返回知识库详情
 */
function handleBack() {
    window.location.href = `kb-detail.html?id=${kbId}`;
}

/**
 * 加载知识库信息
 */
async function loadKnowledgeBaseInfo() {
    const token = localStorage.getItem('access_token');
    
    try {
        const response = await fetch(`${API_BASE_URL}/multi-knowledge/knowledge-bases`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const knowledgeBases = await response.json();
            const kb = knowledgeBases.find(k => k.id == kbId);
            
            if (kb) {
                kbTitle.textContent = `${kb.name} - 查询历史`;
            } else {
                kbTitle.textContent = '未找到指定的知识库';
            }
        } else {
            kbTitle.textContent = '加载知识库信息失败';
        }
    } catch (error) {
        console.error('加载知识库信息错误:', error);
        kbTitle.textContent = '加载知识库信息时出错';
    }
}

/**
 * 加载查询历史
 */
async function loadQueryHistory() {
    const token = localStorage.getItem('access_token');
    
    try {
        const response = await fetch(`${API_BASE_URL}/multi-knowledge/knowledge-bases/history/${kbId}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const history = await response.json();
            displayQueryHistory(history);
        } else {
            historyList.innerHTML = '<p>加载查询历史失败</p>';
        }
    } catch (error) {
        console.error('加载查询历史错误:', error);
        historyList.innerHTML = '<p>加载查询历史时出错</p>';
    }
}

/**
 * 显示查询历史
 */
function displayQueryHistory(history) {
    if (history.length === 0) {
        historyList.innerHTML = '<p>该知识库暂无查询历史</p>';
        return;
    }
    
    let html = '<div class="history-list">';
    
    history.forEach(item => {
        html += `
            <div class="history-item">
                <div class="history-question">
                    <strong>问题:</strong> ${item.question}
                </div>
                <div class="history-answer">
                    <strong>回答:</strong> ${item.answer}
                </div>
                <div class="history-meta">
                    <span>时间: ${new Date(item.created_at).toLocaleString()}</span>
                    ${item.similarity_score ? `<span>相似度: ${(1 - item.similarity_score).toFixed(2)}</span>` : ''}
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    historyList.innerHTML = html;
}