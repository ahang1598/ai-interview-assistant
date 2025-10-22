import re
from typing import Dict, Any, List
import PyPDF2
from docx import Document

def parse_resume(file_path: str, content_type: str) -> Dict[str, Any]:
    """
    解析简历文件，提取基本信息
    
    Args:
        file_path: 文件路径
        content_type: 文件类型
        
    Returns:
        解析后的简历数据
    """
    # 根据文件类型选择解析方法
    if content_type == "application/pdf":
        text = _extract_text_from_pdf(file_path)
    elif content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        text = _extract_text_from_docx(file_path)
    else:
        raise ValueError("不支持的文件格式")
    
    # 从文本中提取信息
    return _extract_info_from_text(text)

def _extract_text_from_pdf(file_path: str) -> str:
    """从PDF文件中提取文本"""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
    except Exception as e:
        raise Exception(f"PDF解析失败: {str(e)}")

def _extract_text_from_docx(file_path: str) -> str:
    """从DOCX文件中提取文本"""
    try:
        doc = Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        raise Exception(f"DOCX解析失败: {str(e)}")

def _extract_info_from_text(text: str) -> Dict[str, Any]:
    """从文本中提取简历信息"""
    result = {
        "name": "",
        "email": "",
        "phone": "",
        "skills": [],
        "experience": [],
        "education": []
    }
    
    # 提取姓名（简单的正则匹配，实际应用中可能需要更复杂的逻辑）
    name_patterns = [
        r'姓名[:：]\s*(\S+)',
        r'Name[:：]\s*(\S+)',
        r'^(\S+\s+\S+)',  # 假设第一行是姓名
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            result["name"] = match.group(1).strip()
            break
    
    # 提取邮箱
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email_match = re.search(email_pattern, text)
    if email_match:
        result["email"] = email_match.group()
    
    # 提取电话号码
    phone_patterns = [
        r'\b1[3-9]\d{9}\b',  # 中国手机号
        r'\b\d{3}-\d{3}-\d{4}\b',  # 美国格式
        r'\b\d{2,4}-\d{7,8}\b',  # 座机号
    ]
    
    for pattern in phone_patterns:
        phone_match = re.search(pattern, text)
        if phone_match:
            result["phone"] = phone_match.group()
            break
    
    # 提取技能（简单的关键词匹配）
    skill_keywords = [
        'Python', 'Java', 'JavaScript', 'React', 'Vue', 'Node.js', 'Spring',
        'Docker', 'Kubernetes', 'MySQL', 'PostgreSQL', 'MongoDB', 'Redis',
        'Git', 'Linux', 'AWS', 'Azure', 'GCP', '机器学习', '深度学习',
        '自然语言处理', '计算机视觉', '数据分析', '大数据'
    ]
    
    for keyword in skill_keywords:
        if re.search(r'\b' + re.escape(keyword) + r'\b', text, re.IGNORECASE):
            result["skills"].append(keyword)
    
    # 简化的工作经验和教育背景提取
    # 在实际应用中，这里需要更复杂的逻辑来解析结构化的经历信息
    
    return result

def analyze_resume(resume_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    分析简历数据，提供评估
    
    Args:
        resume_data: 解析后的简历数据
        
    Returns:
        分析结果
    """
    analysis = {
        "skills_count": len(resume_data.get("skills", [])),
        "has_contact_info": bool(resume_data.get("name") and resume_data.get("email")),
        "skills_analysis": "",
        "overall_score": 0
    }
    
    # 简单的技能分析
    if analysis["skills_count"] > 5:
        analysis["skills_analysis"] = "技能丰富"
        analysis["overall_score"] += 30
    elif analysis["skills_count"] > 2:
        analysis["skills_analysis"] = "技能适中"
        analysis["overall_score"] += 20
    else:
        analysis["skills_analysis"] = "技能较少"
        analysis["overall_score"] += 10
    
    # 联系信息评分
    if analysis["has_contact_info"]:
        analysis["overall_score"] += 20
    
    return analysis