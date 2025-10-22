from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from ..core.langchain_integration import LangChainIntegration
from ..core.user_rag_pipeline import UserRAGPipeline
from ..core.config import settings
from ..models.user import User
from ..api.auth import get_current_active_user
import os

router = APIRouter()

class Message(BaseModel):
    role: str  # "user" 或 "assistant"
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    resume_data: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    message: Message

def get_langchain_integration():
    """获取LangChain集成实例"""
    try:
        return LangChainIntegration(settings.TONGYI_API_KEY)
    except ValueError:
        # 如果没有API密钥，返回None
        return None

@router.post("/completion", response_model=ChatResponse)
async def chat_completion(
    request: ChatRequest, 
    langchain: LangChainIntegration = Depends(get_langchain_integration),
    current_user: User = Depends(get_current_active_user)
):
    """
    AI对话接口，结合用户个人知识库
    """
    try:
        # 获取用户最新消息
        if not request.messages:
            raise HTTPException(status_code=400, detail="消息列表不能为空")
        
        # 初始化用户RAG管道
        user_rag_pipeline = None
        try:
            user_rag_pipeline = UserRAGPipeline(current_user.id, settings.TONGYI_API_KEY)
        except Exception as e:
            print(f"警告: 无法初始化用户RAG管道: {str(e)}")
        
        if langchain:
            # 使用真实的LangChain处理
            messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
            # 如果用户有个人知识库，则结合知识库内容进行回答
            if user_rag_pipeline:
                try:
                    # 查询用户知识库以获取相关上下文
                    user_context = user_rag_pipeline.query(
                        f"请提供与以下问题相关的背景信息: {messages[-1]['content']}"
                    )
                    # 将用户知识库上下文添加到消息中
                    enhanced_messages = messages.copy()
                    enhanced_messages.insert(0, {
                        "role": "system",
                        "content": f"以下是与用户相关的背景信息:\n{user_context}"
                    })
                    response_content = langchain.chat_completion(enhanced_messages, request.resume_data)
                except Exception as e:
                    print(f"警告: 查询用户知识库时出错: {str(e)}")
                    # 如果知识库查询失败，使用原始消息
                    response_content = langchain.chat_completion(messages, request.resume_data)
            else:
                response_content = langchain.chat_completion(messages, request.resume_data)
        else:
            # 模拟AI对话系统（实际项目中将替换为真实的LangChain实现）
            user_message = request.messages[-1].content
            
            # 尝试从用户知识库获取相关信息
            user_context = None
            if user_rag_pipeline:
                try:
                    user_context = user_rag_pipeline.query(
                        f"请提供与以下问题相关的背景信息: {user_message}"
                    )
                except Exception as e:
                    print(f"警告: 查询用户知识库时出错: {str(e)}")
            
            if user_context:
                response_content = f"基于您的个人资料: {user_context}\n\n回答您的问题: '{user_message}'。我是一个AI面试助手，可以根据您的简历进行面试问题的定制。"
            elif request.resume_data:
                # 如果提供了简历数据，可以基于此进行个性化回答
                response_content = f"我已经收到您的简历信息。您刚才说: '{user_message}'。我是一个AI面试助手，可以根据您的简历进行面试问题的定制。"
            else:
                # 通用回答
                response_content = f"您说: '{user_message}'。我是AI面试助手，可以帮您进行面试练习。请上传您的简历以获得更个性化的体验。"
            
            # 模拟一些面试相关的回答
            if "面试" in user_message or "interview" in user_message.lower():
                response_content += " 我可以帮您练习常见的面试问题，比如介绍一下您自己、您的优势和劣势等。"
        
        return ChatResponse(
            message=Message(
                role="assistant",
                content=response_content
            )
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理聊天请求时出错: {str(e)}")

@router.post("/interview_question", response_model=ChatResponse)
async def generate_interview_question(request: ChatRequest, langchain: LangChainIntegration = Depends(get_langchain_integration)):
    """
    根据简历生成面试问题
    """
    try:
        if langchain and request.resume_data:
            # 使用真实的LangChain生成面试问题
            response_content = langchain.generate_interview_question(request.resume_data)
        elif request.resume_data and request.resume_data.get("skills"):
            # 简单的基于技能的实现
            skills = request.resume_data["skills"]
            response_content = f"基于您的技能 {', '.join(skills[:3])}，这里有一个面试问题: 请描述一个您使用这些技术解决过的复杂问题。"
        else:
            # 通用实现
            response_content = "请提供您的简历信息，这样我可以为您生成更相关的面试问题。例如，您可以问关于Python、Java或前端开发的问题。"
        
        return ChatResponse(
            message=Message(
                role="assistant",
                content=response_content
            )
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成面试问题时出错: {str(e)}")