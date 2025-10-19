import PyPDF2
from docx import Document
import re
from typing import Dict, Any, List

def parse_resume(file_path: str, content_type: str) -> Dict[str, Any]:
    """
    解析简历文件，提取基本信息
    """
    if content_type == "application/pdf":
        return _parse_pdf(file_path)
    elif content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return _parse_docx(file_path)
    else:
        raise ValueError("不支持的文件类型")

def _parse_pdf(file_path: str) -> Dict[str, Any]:
    """
    解析PDF格式的简历
    """
    text = ""
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text()
    
    return _extract_info_from_text(text)

def _parse_docx(file_path: str) -> Dict[str, Any]:
    """
    解析DOCX格式的简历
    """
    doc = Document(file_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    
    return _extract_info_from_text(text)

def _extract_info_from_text(text: str) -> Dict[str, Any]:
    """
    从文本中提取简历信息
    """
    # 提取姓名（假设在文档开头）
    name_match = re.search(r'^([A-Z][a-z]+\s+[A-Z][a-z]+)', text)
    name = name_match.group(1) if name_match else "未知"
    
    # 提取邮箱
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    email = email_match.group(0) if email_match else "未知"
    
    # 提取电话号码
    phone_match = re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
    phone = phone_match.group(0) if phone_match else "未知"
    
    # 提取技能（简单示例）
    skills_keywords = ["Python", "Java", "JavaScript", "React", "Vue", "Node.js", "SQL", "MongoDB", 
                      "Docker", "Kubernetes", "AWS", "Azure", "Git", "Linux", "HTML", "CSS"]
    found_skills = [skill for skill in skills_keywords if skill.lower() in text.lower()]
    
    # 提取工作经验（简单示例）
    experience_match = re.search(r'(\d+)\s*\+?\s*years?\s+of\s+experience', text, re.IGNORECASE)
    experience = experience_match.group(1) if experience_match else "未知"
    
    return {
        "name": name,
        "email": email,
        "phone": phone,
        "skills": found_skills,
        "experience_years": experience,
        "raw_text": text[:500] + "..." if len(text) > 500 else text  # 只返回前500个字符
    }

def analyze_resume(parsed_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    分析简历并提供反馈
    """
    analysis = {
        "skills_count": len(parsed_data.get("skills", [])),
        "has_contact_info": bool(parsed_data.get("email") != "未知" or parsed_data.get("phone") != "未知"),
        "suggestions": []
    }
    
    # 提供建议
    if analysis["skills_count"] < 5:
        analysis["suggestions"].append("建议在简历中添加更多技能关键词")
    
    if not analysis["has_contact_info"]:
        analysis["suggestions"].append("简历中缺少联系方式，请添加邮箱或电话")
    
    if parsed_data.get("experience_years") == "未知":
        analysis["suggestions"].append("建议明确标注工作年限")
    
    # 如果没有建议，则给出正面反馈
    if not analysis["suggestions"]:
        analysis["suggestions"].append("简历信息完整，格式良好")
    
    return analysis