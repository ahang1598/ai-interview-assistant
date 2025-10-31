from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class QueryHistoryBase(BaseModel):
    question: str
    answer: str
    similarity_score: Optional[float] = None


class QueryHistoryCreate(QueryHistoryBase):
    pass


class QueryHistory(QueryHistoryBase):
    id: int
    knowledge_base_id: int
    created_at: datetime
    
    class Config:
        orm_mode = True