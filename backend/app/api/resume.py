from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any
from ..utils import resume_parser
import os
import tempfile

router = APIRouter()

@router.post("/parse")
async def parse_resume(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    解析上传的简历文件(PDF或DOCX格式)
    """
    # 检查文件类型
    if file.content_type not in ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        raise HTTPException(status_code=400, detail="只支持PDF和DOCX格式的文件")
    
    try:
        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(await file.read())
            tmp_file_path = tmp_file.name
        
        # 解析简历
        parsed_data = resume_parser.parse_resume(tmp_file_path, file.content_type)
        
        # 删除临时文件
        os.unlink(tmp_file_path)
        
        return {"status": "success", "data": parsed_data}
    
    except Exception as e:
        # 确保临时文件被删除
        if 'tmp_file_path' in locals():
            os.unlink(tmp_file_path)
        raise HTTPException(status_code=500, detail=f"解析简历时出错: {str(e)}")

@router.post("/analyze")
async def analyze_resume(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    解析并分析简历，提供技能评估和建议
    """
    # 检查文件类型
    if file.content_type not in ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        raise HTTPException(status_code=400, detail="只支持PDF和DOCX格式的文件")
    
    try:
        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(await file.read())
            tmp_file_path = tmp_file.name
        
        # 解析简历
        parsed_data = resume_parser.parse_resume(tmp_file_path, file.content_type)
        
        # 分析简历
        analysis = resume_parser.analyze_resume(parsed_data)
        
        # 删除临时文件
        os.unlink(tmp_file_path)
        
        return {"status": "success", "data": {"resume": parsed_data, "analysis": analysis}}
    
    except Exception as e:
        # 确保临时文件被删除
        if 'tmp_file_path' in locals():
            os.unlink(tmp_file_path)
        raise HTTPException(status_code=500, detail=f"分析简历时出错: {str(e)}")