// API基础URL
const API_BASE_URL = 'http://localhost:8000';

// DOM元素
const userInfo = document.getElementById('user-info');
const usernameSpan = document.getElementById('username');
const logoutBtn = document.getElementById('logout-btn');
const kbTitle = document.getElementById('kb-title');
const kbInfo = document.getElementById('kb-info');
const textTab = document.getElementById('text-tab');
const resumeTab = document.getElementById('resume-tab');
const textContent = document.getElementById('text-content');
const resumeContent = document.getElementById('resume-content');
const addTextForm = document.getElementById('add-text-form');
const documentTextInput = document.getElementById('document-text');
const addTextMessage = document.getElementById('add-text-message');
const addResumeForm = document.getElementById('add-resume-form');
const resumeFileInput = document.getElementById('resume-file');
const addResumeMessage = document.getElementById('add-resume-message');
const queryForm = document.getElementById('query-form');
const queryQuestionInput = document.getElementById('query-question');
const queryResults = document.getElementById('query-results');
const answerContent = document.getElementById('answer-content');
const sourceDocuments = document.getElementById('source-documents');
const historyBtn = document.getElementById('history-btn');

// 获取知识库ID
const urlParams = new URLSearchParams(window.location.search);
const kbId = urlParams.get('id');

// 检查用户是否已登录
checkAuthStatus();

// 事件监听器
logoutBtn.addEventListener('click', handleLogout);
textTab.addEventListener('click', () => switchTab('text'));
resumeTab.addEventListener('click', () => switchTab('resume'));
addTextForm.addEventListener('submit', handleAddTextDocument);
addResumeForm.addEventListener('submit', handleAddResumeDocument);
queryForm.addEventListener('submit', handleQuery);
historyBtn.addEventListener('click', handleViewHistory);

/**
 * 切换标签页
 */
function switchTab(tab) {
    if (tab === 'text') {
        textTab.classList.add('active');
        resumeTab.classList.remove('active');
        textContent.classList.remove('hidden');
        resumeContent.classList.add('hidden');
    } else {
        resumeTab.classList.add('active');
        textTab.classList.remove('active');
        resumeContent.classList.remove('hidden');
        textContent.classList.add('hidden');
    }
}

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
        } else {
            kbInfo.innerHTML = '<p>无效的知识库ID</p>';
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
 * 查看历史记录
 */
function handleViewHistory() {
    window.location.href = `history.html?kb_id=${kbId}`;
}

/**
 * 加载知识库信息
 */
async function loadKnowledgeBaseInfo() {
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
            const kb = knowledgeBases.find(k => k.id == kbId);
            
            if (kb) {
                kbTitle.textContent = kb.name;
                kbInfo.innerHTML = `
                    <p><strong>描述:</strong> ${kb.description || '无'}</p>
                    <p><strong>创建时间:</strong> ${kb.created_at ? new Date(kb.created_at).toLocaleString() : '未知'}</p>
                    <p><strong>状态:</strong> <span class="${kb.is_active ? 'status-active' : 'status-inactive'}">${kb.is_active ? '激活' : '未激活'}</span></p>
                `;
            } else {
                kbInfo.innerHTML = '<p>未找到指定的知识库</p>';
            }
        } else {
            kbInfo.innerHTML = '<p>加载知识库信息失败</p>';
        }
    } catch (error) {
        console.error('加载知识库信息错误:', error);
        kbInfo.innerHTML = '<p>加载知识库信息时出错</p>';
    }
}

/**
 * 处理添加文本文档
 */
async function handleAddTextDocument(event) {
    event.preventDefault();
    
    const token = localStorage.getItem('access_token');
    const documentText = documentTextInput.value.trim();
    
    if (!documentText) {
        showMessage(addTextMessage, '请输入文档内容', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/knowledge-bases/${kbId}/documents/add`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ documents: [documentText] })
        });
        
        if (response.ok) {
            showMessage(addTextMessage, '文档添加成功！', 'success');
            documentTextInput.value = '';
        } else {
            const errorData = await response.json();
            showMessage(addTextMessage, `添加失败: ${errorData.detail}`, 'error');
        }
    } catch (error) {
        showMessage(addTextMessage, `添加失败: ${error.message}`, 'error');
    }
}

/**
 * 处理从简历添加文档
 */
async function handleAddResumeDocument(event) {
    event.preventDefault();
    
    const token = localStorage.getItem('access_token');
    const file = resumeFileInput.files[0];
    
    if (!file) {
        showMessage(addResumeMessage, '请选择一个文件', 'error');
        return;
    }
    
    // 检查文件类型
    const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    if (!allowedTypes.includes(file.type)) {
        showMessage(addResumeMessage, '只支持PDF和DOCX格式的文件', 'error');
        return;
    }
    
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch(`${API_BASE_URL}/knowledge-bases/${kbId}/documents/add_from_resume`, {
            method: 'POST',
            body: formData,
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            showMessage(addResumeMessage, '简历内容已添加到知识库！', 'success');
            resumeFileInput.value = '';
        } else {
            const errorData = await response.json();
            showMessage(addResumeMessage, `添加失败: ${errorData.detail}`, 'error');
        }
    } catch (error) {
        showMessage(addResumeMessage, `添加失败: ${error.message}`, 'error');
    }
}

/**
 * 处理知识库查询
 */
async function handleQuery(event) {
    event.preventDefault();
    
    const token = localStorage.getItem('access_token');
    const question = queryQuestionInput.value.trim();
    
    if (!question) {
        alert('请输入问题');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/knowledge-bases/${kbId}/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ question: question })
        });
        
        if (response.ok) {
            const result = await response.json();
            displayQueryResults(result);
        } else {
            const errorData = await response.json();
            alert(`查询失败: ${errorData.detail}`);
        }
    } catch (error) {
        alert(`查询失败: ${error.message}`);
    }
}

/**
 * 显示查询结果
 */
function displayQueryResults(result) {
    queryResults.classList.remove('hidden');
    
    // 显示回答
    answerContent.innerHTML = `<p>${result.answer}</p>`;
    
    // 显示参考文档
    if (result.source_documents && result.source_documents.length > 0) {
        let documentsHtml = '';
        result.source_documents.forEach((doc, index) => {
            documentsHtml += `
                <div class="source-document">
                    <h4>参考文档 ${index + 1}</h4>
                    <p>${doc.content}</p>
                    <p class="document-meta">
                        相似度: ${(1 - doc.score).toFixed(2)}
                    </p>
                </div>
            `;
        });
        sourceDocuments.innerHTML = documentsHtml;
    } else {
        sourceDocuments.innerHTML = '<p>未找到相关参考文档</p>';
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
 * 返回知识库管理页面
 */
function goBack() {
    window.location.href = 'knowledge.html';
}