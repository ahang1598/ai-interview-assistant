from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class KnowledgeBaseBase(BaseModel):
    name: str
    description: Optional[str] = None

class KnowledgeBaseCreate(KnowledgeBaseBase):
    pass

class KnowledgeBaseUpdate(KnowledgeBaseBase):
    is_active: Optional[bool] = None

class KnowledgeBase(KnowledgeBaseBase):
    id: int
    user_id: int
    collection_name: str
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

class KnowledgeBaseQuery(BaseModel):
    question: str
    knowledge_base_id: int

class KnowledgeBaseSearch(BaseModel):
    query: str
    knowledge_base_id: int
    k: int = 4

class KnowledgeBaseResponse(BaseModel):
    answer: str
    source_documents: List[dict]