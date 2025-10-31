from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, status
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import tempfile
import os
from ..core.rag_pipeline import RAGPipeline
from ..core.user_rag_pipeline import UserRAGPipeline
from ..core.config import settings
from ..utils.resume_parser import parse_resume
from ..models.user import User
from ..api.auth import get_current_active_user

router = APIRouter()

class DocumentAddRequest(BaseModel):
    documents: List[str]
    metadatas: Optional[List[Dict[str, Any]]] = None

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    source_documents: List[Dict[str, Any]]

class SearchRequest(BaseModel):
    query: str
    k: int = 4

def get_rag_pipeline():
    """获取RAG管道实例"""
    try:
        return RAGPipeline(settings.TONGYI_API_KEY)
    except ValueError:
        return None

def get_user_rag_pipeline(current_user: User = Depends(get_current_active_user)):
    """获取用户专属RAG管道实例"""
    try:
        return UserRAGPipeline(current_user.id, settings.TONGYI_API_KEY)
    except ValueError:
        return None

@router.post("/documents/add")
async def add_documents(
    request: DocumentAddRequest,
    rag_pipeline: RAGPipeline = Depends(get_rag_pipeline)
):
    """
    向全局知识库中添加文档
    """
    try:
        if not rag_pipeline:
            raise HTTPException(status_code=500, detail="RAG管道未初始化")

        rag_pipeline.add_documents(request.documents, request.metadatas)
        return {"status": "success", "message": "文档已添加到知识库"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"添加文档时出错: {str(e)}")

@router.post("/user/documents/add")
async def add_user_documents(
    request: DocumentAddRequest,
    user_rag_pipeline: UserRAGPipeline = Depends(get_user_rag_pipeline)
):
    """
    向当前用户的知识库中添加文档
    """
    try:
        if not user_rag_pipeline:
            raise HTTPException(status_code=500, detail="用户RAG管道未初始化")

        user_rag_pipeline.add_documents(request.documents, request.metadatas)
        return {"status": "success", "message": "文档已添加到您的个人知识库"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"添加文档时出错: {str(e)}")

@router.post("/documents/add_from_resume")
async def add_documents_from_resume(
    file: UploadFile = File(...),
    rag_pipeline: RAGPipeline = Depends(get_rag_pipeline)
):
    """
    从简历文件中提取信息并添加到全局知识库
    """
    try:
        if not rag_pipeline:
            raise HTTPException(status_code=500, detail="RAG管道未初始化")

        # 检查文件类型
        if file.content_type not in ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
            raise HTTPException(status_code=400, detail="只支持PDF和DOCX格式的文件")

        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(await file.read())
            tmp_file_path = tmp_file.name

        try:
            # 解析简历
            parsed_data = parse_resume(tmp_file_path, file.content_type)
            
            # 构造文档内容
            documents = []
            
            # 添加基本信息
            basic_info = f"候选人姓名: {parsed_data.get('name', '未知')}\n"
            basic_info += f"邮箱: {parsed_data.get('email', '未知')}\n"
            basic_info += f"电话: {parsed_data.get('phone', '未知')}"
            documents.append(basic_info)
            
            # 添加技能信息
            if parsed_data.get('skills'):
                skills_info = "技能: " + ", ".join(parsed_data['skills'])
                documents.append(skills_info)
            
            # 添加工作经验
            if parsed_data.get('experience'):
                for exp in parsed_data['experience']:
                    exp_info = f"工作经验:\n公司: {exp.get('company', '未知')}\n"
                    exp_info += f"职位: {exp.get('position', '未知')}\n"
                    exp_info += f"时间: {exp.get('duration', '未知')}\n"
                    exp_info += f"描述: {exp.get('description', '无')}"
                    documents.append(exp_info)
            
            # 添加教育背景
            if parsed_data.get('education'):
                for edu in parsed_data['education']:
                    edu_info = f"教育背景:\n学校: {edu.get('institution', '未知')}\n"
                    edu_info += f"学位: {edu.get('degree', '未知')}\n"
                    edu_info += f"专业: {edu.get('field', '未知')}\n"
                    edu_info += f"时间: {edu.get('duration', '未知')}"
                    documents.append(edu_info)
            
            # 添加元数据
            metadatas = [{"source": "resume", "filename": file.filename} for _ in documents]
            
            # 添加到知识库
            rag_pipeline.add_documents(documents, metadatas)
            
            return {"status": "success", "message": "简历信息已添加到知识库", "data": parsed_data}
        
        finally:
            # 删除临时文件
            os.unlink(tmp_file_path)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理简历时出错: {str(e)}")

@router.post("/user/documents/add_from_resume")
async def add_user_documents_from_resume(
    file: UploadFile = File(...),
    user_rag_pipeline: UserRAGPipeline = Depends(get_user_rag_pipeline)
):
    """
    从简历文件中提取信息并添加到当前用户的个人知识库
    """
    try:
        if not user_rag_pipeline:
            raise HTTPException(status_code=500, detail="用户RAG管道未初始化")

        # 检查文件类型
        if file.content_type not in ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
            raise HTTPException(status_code=400, detail="只支持PDF和DOCX格式的文件")

        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(await file.read())
            tmp_file_path = tmp_file.name

        try:
            # 解析简历
            parsed_data = parse_resume(tmp_file_path, file.content_type)
            
            # 构造文档内容
            documents = []
            
            # 添加基本信息
            basic_info = f"候选人姓名: {parsed_data.get('name', '未知')}\n"
            basic_info += f"邮箱: {parsed_data.get('email', '未知')}\n"
            basic_info += f"电话: {parsed_data.get('phone', '未知')}"
            documents.append(basic_info)
            
            # 添加技能信息
            if parsed_data.get('skills'):
                skills_info = "技能: " + ", ".join(parsed_data['skills'])
                documents.append(skills_info)
            
            # 添加工作经验
            if parsed_data.get('experience'):
                for exp in parsed_data['experience']:
                    exp_info = f"工作经验:\n公司: {exp.get('company', '未知')}\n"
                    exp_info += f"职位: {exp.get('position', '未知')}\n"
                    exp_info += f"时间: {exp.get('duration', '未知')}\n"
                    exp_info += f"描述: {exp.get('description', '无')}"
                    documents.append(exp_info)
            
            # 添加教育背景
            if parsed_data.get('education'):
                for edu in parsed_data['education']:
                    edu_info = f"教育背景:\n学校: {edu.get('institution', '未知')}\n"
                    edu_info += f"学位: {edu.get('degree', '未知')}\n"
                    edu_info += f"专业: {edu.get('field', '未知')}\n"
                    edu_info += f"时间: {edu.get('duration', '未知')}"
                    documents.append(edu_info)
            
            # 添加元数据
            metadatas = [{"source": "resume", "filename": file.filename} for _ in documents]
            
            # 添加到用户知识库
            user_rag_pipeline.add_documents(documents, metadatas)
            
            return {"status": "success", "message": "简历信息已添加到您的个人知识库", "data": parsed_data}
        
        finally:
            # 删除临时文件
            os.unlink(tmp_file_path)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理简历时出错: {str(e)}")

@router.post("/query", response_model=QueryResponse)
async def query_knowledge(
    request: QueryRequest,
    rag_pipeline: RAGPipeline = Depends(get_rag_pipeline)
):
    """
    查询全局知识库
    """
    try:
        if not rag_pipeline:
            raise HTTPException(status_code=500, detail="RAG管道未初始化")

        # 创建检索QA链
        answer = rag_pipeline.query(request.question)
        
        # 进行相似性搜索获取源文档
        source_docs = rag_pipeline.similarity_search(request.question, k=3)
        
        return QueryResponse(
            answer=answer,
            source_documents=source_docs
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询知识库时出错: {str(e)}")

@router.post("/user/query", response_model=QueryResponse)
async def query_user_knowledge(
    request: QueryRequest,
    user_rag_pipeline: UserRAGPipeline = Depends(get_user_rag_pipeline)
):
    """
    查询当前用户的知识库
    """
    try:
        if not user_rag_pipeline:
            raise HTTPException(status_code=500, detail="用户RAG管道未初始化")

        # 创建检索QA链
        answer = user_rag_pipeline.query(request.question)
        
        # 进行相似性搜索获取源文档
        source_docs = user_rag_pipeline.similarity_search(request.question, k=3)
        
        return QueryResponse(
            answer=answer,
            source_documents=source_docs
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询用户知识库时出错: {str(e)}")

@router.post("/search")
async def search_similarity(
    request: SearchRequest,
    rag_pipeline: RAGPipeline = Depends(get_rag_pipeline)
):
    """
    在全局知识库中进行相似性搜索
    """
    try:
        if not rag_pipeline:
            raise HTTPException(status_code=500, detail="RAG管道未初始化")

        results = rag_pipeline.similarity_search(request.query, request.k)
        return {"results": results}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"相似性搜索时出错: {str(e)}")

@router.post("/user/search")
async def search_user_similarity(
    request: SearchRequest,
    user_rag_pipeline: UserRAGPipeline = Depends(get_user_rag_pipeline)
):
    """
    在当前用户的个人知识库中进行相似性搜索
    """
    try:
        if not user_rag_pipeline:
            raise HTTPException(status_code=500, detail="用户RAG管道未初始化")

        results = user_rag_pipeline.similarity_search(request.query, request.k)
        return {"results": results}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"相似性搜索时出错: {str(e)}")

@router.delete("/collection")
async def delete_collection(
    rag_pipeline: RAGPipeline = Depends(get_rag_pipeline)
):
    """
    删除整个知识库集合
    """
    try:
        if not rag_pipeline:
            raise HTTPException(status_code=500, detail="RAG管道未初始化")

        rag_pipeline.delete_collection()
        return {"status": "success", "message": "知识库集合已删除"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除知识库时出错: {str(e)}")