// API基础URL
const API_BASE_URL = 'http://localhost:8000';

// DOM元素
const authRequiredSection = document.getElementById('auth-required');
const uploadSection = document.getElementById('upload-section');
const analysisSection = document.getElementById('analysis-section');
const chatSection = document.getElementById('chat-section');
const userInfo = document.getElementById('user-info');
const usernameSpan = document.getElementById('username');
const logoutBtn = document.getElementById('logout-btn');
const loginLink = document.getElementById('login-link');
const resumeUploadForm = document.getElementById('resume-upload-form');
const uploadStatus = document.getElementById('upload-status');
const analysisResults = document.getElementById('analysis-results');
const chatHistory = document.getElementById('chat-history');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');

// 简历数据
let resumeData = null;

// 检查用户是否已登录
checkAuthStatus();

// 事件监听器
loginLink.addEventListener('click', () => {
    window.location.href = 'auth.html';
});

logoutBtn.addEventListener('click', handleLogout);
resumeUploadForm.addEventListener('submit', handleResumeUpload);
chatForm.addEventListener('submit', handleChatSubmit);

/**
 * 检查用户认证状态
 */
function checkAuthStatus() {
    const token = localStorage.getItem('access_token');
    const username = localStorage.getItem('username');
    
    if (token && username) {
        // 用户已登录
        authRequiredSection.classList.add('hidden');
        uploadSection.classList.remove('hidden');
        usernameSpan.textContent = username;
        userInfo.classList.remove('hidden');
    } else {
        // 用户未登录
        authRequiredSection.classList.remove('hidden');
        uploadSection.classList.add('hidden');
        userInfo.classList.add('hidden');
    }
}

/**
 * 处理用户退出
 */
function handleLogout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('username');
    checkAuthStatus();
    // 清空聊天历史
    chatHistory.innerHTML = '';
}

/**
 * 处理简历上传
 */
async function handleResumeUpload(event) {
    event.preventDefault();
    
    const token = localStorage.getItem('access_token');
    if (!token) {
        showUploadStatus('请先登录', 'error');
        return;
    }
    
    const fileInput = document.getElementById('resume-file');
    const file = fileInput.files[0];
    
    if (!file) {
        showUploadStatus('请选择一个文件', 'error');
        return;
    }
    
    // 检查文件类型
    const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    if (!allowedTypes.includes(file.type)) {
        showUploadStatus('只支持PDF和DOCX格式的文件', 'error');
        return;
    }
    
    // 创建FormData对象
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        // 显示上传中状态
        showUploadStatus('正在上传和分析简历...', 'info');
        
        // 发送请求到后端
        const response = await fetch(`${API_BASE_URL}/resume/parse`, {
            method: 'POST',
            body: formData,
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        // 同时将简历添加到用户个人知识库
        const knowledgeResponse = await fetch(`${API_BASE_URL}/knowledge/user/documents/add_from_resume`, {
            method: 'POST',
            body: formData,
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const knowledgeResult = await knowledgeResponse.json();
        if (!knowledgeResponse.ok) {
            console.error('添加到知识库失败:', knowledgeResult.detail);
        }
        
        const result = await response.json();
        
        if (response.ok) {
            // 保存简历数据
            resumeData = result.data;
            
            // 显示分析结果
            displayAnalysisResults(result.data);
            
            // 显示聊天区域
            chatSection.classList.remove('hidden');
            
            // 显示成功状态
            showUploadStatus('简历上传和分析成功!', 'success');
        } else {
            if (response.status === 401) {
                showUploadStatus('认证已过期，请重新登录', 'error');
                setTimeout(() => {
                    handleLogout();
                }, 1500);
            } else {
                showUploadStatus(`错误: ${result.detail}`, 'error');
            }
        }
    } catch (error) {
        console.error('上传错误:', error);
        showUploadStatus(`上传失败: ${error.message}`, 'error');
    }
}

/**
 * 显示上传状态
 */
function showUploadStatus(message, type) {
    uploadStatus.textContent = message;
    uploadStatus.className = '';
    uploadStatus.classList.add('status', type);
}

/**
 * 显示分析结果
 */
function displayAnalysisResults(data) {
    let html = '';
    
    // 基本信息
    if (data.name || data.email || data.phone) {
        html += `
            <div class="analysis-section">
                <h3>基本信息</h3>
                <p><strong>姓名:</strong> ${data.name || '未提供'}</p>
                <p><strong>邮箱:</strong> ${data.email || '未提供'}</p>
                <p><strong>电话:</strong> ${data.phone || '未提供'}</p>
            </div>
        `;
    }
    
    // 技能
    if (data.skills && data.skills.length > 0) {
        html += `
            <div class="analysis-section">
                <h3>技能</h3>
                <div>
                    ${data.skills.map(skill => `<span class="skill-tag">${skill}</span>`).join('')}
                </div>
            </div>
        `;
    }
    
    // 工作经验
    if (data.experience && data.experience.length > 0) {
        html += `
            <div class="analysis-section">
                <h3>工作经验</h3>
                ${data.experience.map(exp => `
                    <div>
                        <p><strong>${exp.position || '职位未提供'}</strong> at ${exp.company || '公司未提供'}</p>
                        <p>${exp.duration || ''}</p>
                        <p>${exp.description || ''}</p>
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    // 教育背景
    if (data.education && data.education.length > 0) {
        html += `
            <div class="analysis-section">
                <h3>教育背景</h3>
                ${data.education.map(edu => `
                    <div>
                        <p><strong>${edu.degree || '学位未提供'}</strong> in ${edu.field || '专业未提供'}</p>
                        <p>${edu.institution || '院校未提供'} (${edu.duration || ''})</p>
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    analysisResults.innerHTML = html;
    analysisSection.classList.remove('hidden');
}

/**
 * 处理聊天提交
 */
async function handleChatSubmit(event) {
    event.preventDefault();
    
    const token = localStorage.getItem('access_token');
    if (!token) {
        addMessageToChat('assistant', '请先登录');
        return;
    }
    
    const message = userInput.value.trim();
    if (!message) return;
    
    // 添加用户消息到聊天历史
    addMessageToChat('user', message);
    
    // 清空输入框
    userInput.value = '';
    
    try {
        // 准备消息历史
        const messages = [];
        const chatMessages = chatHistory.querySelectorAll('.message');
        chatMessages.forEach(msgElement => {
            const role = msgElement.classList.contains('user') ? 'user' : 'assistant';
            const content = msgElement.querySelector('.message-content').textContent;
            messages.push({ role, content });
        });
        
        // 准备请求数据
        const requestData = {
            messages: [...messages, { role: 'user', content: message }],
            resume_data: resumeData
        };
        
        // 同时将对话内容添加到用户个人知识库
        try {
            const knowledgeResponse = await fetch(`${API_BASE_URL}/knowledge/user/documents/add`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    documents: [message]
                })
            });
            
            if (!knowledgeResponse.ok) {
                const knowledgeResult = await knowledgeResponse.json();
                console.error('添加到知识库失败:', knowledgeResult.detail);
            }
        } catch (knowledgeError) {
            console.error('添加到知识库时出错:', knowledgeError);
        }
        
        // 发送请求到后端
        const response = await fetch(`${API_BASE_URL}/chat/completion`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(requestData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            // 添加AI回复到聊天历史
            addMessageToChat('assistant', result.message.content);
        } else {
            if (response.status === 401) {
                addMessageToChat('assistant', '认证已过期，请重新登录');
                setTimeout(() => {
                    handleLogout();
                }, 1500);
            } else {
                addMessageToChat('assistant', `错误: ${result.detail}`);
            }
        }
    } catch (error) {
        console.error('聊天错误:', error);
        addMessageToChat('assistant', `请求失败: ${error.message}`);
    }
}

/**
 * 添加消息到聊天历史
 */
function addMessageToChat(role, content) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', role);
    
    const now = new Date();
    const timeString = `${now.getHours()}:${String(now.getMinutes()).padStart(2, '0')}`;
    
    messageDiv.innerHTML = `
        <div class="message-header">${role === 'user' ? '您' : 'AI助手'} - ${timeString}</div>
        <div class="message-content">${content}</div>
    `;
    
    chatHistory.appendChild(messageDiv);
    
    // 滚动到底部
    chatHistory.scrollTop = chatHistory.scrollHeight;
}