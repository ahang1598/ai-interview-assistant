from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import tempfile
import os
import uuid

from ..database import get_db
from ..models.user import User
from ..models.knowledge_base import KnowledgeBase
from ..models.query_history import QueryHistory
from ..schemas.knowledge_base import (
    KnowledgeBaseCreate, 
    KnowledgeBaseUpdate, 
    KnowledgeBase as KnowledgeBaseSchema,
    KnowledgeBaseQuery,
    KnowledgeBaseSearch,
    KnowledgeBaseResponse
)
from ..schemas.query_history import QueryHistory as QueryHistorySchema
from ..core.multi_rag_pipeline import MultiRAGPipeline
from ..core.config import settings
from ..utils.resume_parser import parse_resume
from ..api.auth import get_current_active_user

router = APIRouter()

def get_rag_pipeline(collection_name: str):
    """获取多知识库RAG管道实例"""
    try:
        return MultiRAGPipeline(collection_name, settings.TONGYI_API_KEY)
    except ValueError:
        return None

@router.post("/knowledge-bases", response_model=KnowledgeBaseSchema)
async def create_knowledge_base(
    knowledge_base: KnowledgeBaseCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    为当前用户创建新的知识库
    """
    try:
        # 生成唯一的集合名称
        collection_name = f"user_{current_user.id}_kb_{uuid.uuid4().hex[:8]}"
        
        # 创建知识库记录
        db_knowledge_base = KnowledgeBase(
            user_id=current_user.id,
            name=knowledge_base.name,
            description=knowledge_base.description,
            collection_name=collection_name
        )
        
        db.add(db_knowledge_base)
        db.commit()
        db.refresh(db_knowledge_base)
        
        # 初始化向量数据库集合
        rag_pipeline = get_rag_pipeline(collection_name)
        if not rag_pipeline:
            raise HTTPException(status_code=500, detail="无法初始化RAG管道")
        
        return db_knowledge_base
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"创建知识库时出错: {str(e)}")

@router.get("/knowledge-bases", response_model=List[KnowledgeBaseSchema])
async def list_knowledge_bases(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的所有知识库
    """
    try:
        knowledge_bases = db.query(KnowledgeBase).filter(
            KnowledgeBase.user_id == current_user.id
        ).all()
        
        return knowledge_bases
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取知识库列表时出错: {str(e)}")

@router.get("/knowledge-bases/history/{kb_id}", response_model=List[QueryHistorySchema])
async def get_query_history(
    kb_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取指定知识库的查询历史
    """
    try:
        # 验证知识库属于当前用户
        knowledge_base = db.query(KnowledgeBase).filter(
            KnowledgeBase.id == kb_id,
            KnowledgeBase.user_id == current_user.id
        ).first()
        
        if not knowledge_base:
            raise HTTPException(status_code=404, detail="知识库未找到")
        
        # 获取查询历史
        history = db.query(QueryHistory).filter(
            QueryHistory.knowledge_base_id == kb_id
        ).order_by(QueryHistory.created_at.desc()).all()
        
        return history
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取查询历史时出错: {str(e)}")

@router.put("/knowledge-bases/{kb_id}", response_model=KnowledgeBaseSchema)
async def update_knowledge_base(
    kb_id: int,
    knowledge_base_update: KnowledgeBaseUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    更新知识库信息
    """
    try:
        # 查找知识库
        db_knowledge_base = db.query(KnowledgeBase).filter(
            KnowledgeBase.id == kb_id,
            KnowledgeBase.user_id == current_user.id
        ).first()
        
        if not db_knowledge_base:
            raise HTTPException(status_code=404, detail="知识库未找到")
        
        # 更新字段
        if knowledge_base_update.name is not None:
            db_knowledge_base.name = knowledge_base_update.name
        if knowledge_base_update.description is not None:
            db_knowledge_base.description = knowledge_base_update.description
        if knowledge_base_update.is_active is not None:
            db_knowledge_base.is_active = knowledge_base_update.is_active
            
        db.commit()
        db.refresh(db_knowledge_base)
        
        return db_knowledge_base
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新知识库时出错: {str(e)}")

@router.delete("/knowledge-bases/{kb_id}")
async def delete_knowledge_base(
    kb_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    删除知识库
    """
    try:
        # 查找知识库
        db_knowledge_base = db.query(KnowledgeBase).filter(
            KnowledgeBase.id == kb_id,
            KnowledgeBase.user_id == current_user.id
        ).first()
        
        if not db_knowledge_base:
            raise HTTPException(status_code=404, detail="知识库未找到")
        
        # 删除向量数据库中的集合
        rag_pipeline = get_rag_pipeline(db_knowledge_base.collection_name)
        if rag_pipeline:
            rag_pipeline.delete_collection()
        
        # 删除数据库记录
        db.delete(db_knowledge_base)
        db.commit()
        
        return {"status": "success", "message": "知识库已删除"}
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除知识库时出错: {str(e)}")

@router.post("/knowledge-bases/{kb_id}/documents/add")
async def add_documents_to_knowledge_base(
    kb_id: int,
    documents: List[str],
    metadatas: Optional[List[Dict[str, Any]]] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    向指定知识库中添加文档
    """
    try:
        # 查找知识库
        db_knowledge_base = db.query(KnowledgeBase).filter(
            KnowledgeBase.id == kb_id,
            KnowledgeBase.user_id == current_user.id
        ).first()
        
        if not db_knowledge_base:
            raise HTTPException(status_code=404, detail="知识库未找到")
        
        if not db_knowledge_base.is_active:
            raise HTTPException(status_code=400, detail="知识库未激活")
        
        # 获取RAG管道
        rag_pipeline = get_rag_pipeline(db_knowledge_base.collection_name)
        if not rag_pipeline:
            raise HTTPException(status_code=500, detail="RAG管道未初始化")
        
        # 添加文档
        rag_pipeline.add_documents(documents, metadatas)
        
        return {"status": "success", "message": "文档已添加到知识库"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"添加文档时出错: {str(e)}")

@router.post("/knowledge-bases/{kb_id}/documents/add_from_resume")
async def add_resume_to_knowledge_base(
    kb_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    从简历文件中提取信息并添加到指定知识库
    """
    try:
        # 查找知识库
        db_knowledge_base = db.query(KnowledgeBase).filter(
            KnowledgeBase.id == kb_id,
            KnowledgeBase.user_id == current_user.id
        ).first()
        
        if not db_knowledge_base:
            raise HTTPException(status_code=404, detail="知识库未找到")
        
        if not db_knowledge_base.is_active:
            raise HTTPException(status_code=400, detail="知识库未激活")
        
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
            
            # 获取RAG管道并添加到知识库
            rag_pipeline = get_rag_pipeline(db_knowledge_base.collection_name)
            if not rag_pipeline:
                raise HTTPException(status_code=500, detail="RAG管道未初始化")
            
            rag_pipeline.add_documents(documents, metadatas)
            
            return {"status": "success", "message": "简历信息已添加到知识库", "data": parsed_data}
        
        finally:
            # 删除临时文件
            os.unlink(tmp_file_path)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理简历时出错: {str(e)}")

@router.post("/knowledge-bases/{kb_id}/query", response_model=KnowledgeBaseResponse)
async def query_knowledge_base(
    kb_id: int,
    request: KnowledgeBaseQuery,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    查询指定知识库
    """
    try:
        # 查找知识库
        db_knowledge_base = db.query(KnowledgeBase).filter(
            KnowledgeBase.id == kb_id,
            KnowledgeBase.user_id == current_user.id
        ).first()
        
        if not db_knowledge_base:
            raise HTTPException(status_code=404, detail="知识库未找到")
        
        if not db_knowledge_base.is_active:
            raise HTTPException(status_code=400, detail="知识库未激活")
        
        # 获取RAG管道
        rag_pipeline = get_rag_pipeline(db_knowledge_base.collection_name)
        if not rag_pipeline:
            raise HTTPException(status_code=500, detail="RAG管道未初始化")

        # 查询知识库
        answer = rag_pipeline.query(request.question)
        
        # 进行相似性搜索获取源文档
        source_docs = rag_pipeline.similarity_search(request.question, k=3)
        
        # 保存查询历史
        similarity_score = min(source_docs, key=lambda x: x.score).score if source_docs else None
        
        query_history = QueryHistory(
            knowledge_base_id=kb_id,
            question=request.question,
            answer=answer,
            similarity_score=similarity_score
        )
        
        db.add(query_history)
        db.commit()
        
        return KnowledgeBaseResponse(
            answer=answer,
            source_documents=source_docs
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询知识库时出错: {str(e)}")

@router.post("/knowledge-bases/{kb_id}/search")
async def search_knowledge_base(
    kb_id: int,
    request: KnowledgeBaseSearch,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    在指定知识库中进行相似性搜索
    """
    try:
        # 查找知识库
        db_knowledge_base = db.query(KnowledgeBase).filter(
            KnowledgeBase.id == kb_id,
            KnowledgeBase.user_id == current_user.id
        ).first()
        
        if not db_knowledge_base:
            raise HTTPException(status_code=404, detail="知识库未找到")
        
        if not db_knowledge_base.is_active:
            raise HTTPException(status_code=400, detail="知识库未激活")
        
        # 获取RAG管道
        rag_pipeline = get_rag_pipeline(db_knowledge_base.collection_name)
        if not rag_pipeline:
            raise HTTPException(status_code=500, detail="RAG管道未初始化")

        results = rag_pipeline.similarity_search(request.query, request.k)
        return {"results": results}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"相似性搜索时出错: {str(e)}")