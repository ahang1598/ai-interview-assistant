import re
from typing import Dict, Any, List
import PyPDF2
from docx import Document
import os
import json

# 只有在有TONGYI_API_KEY时才导入Tongyi
if os.getenv("TONGYI_API_KEY"):
    try:
        from langchain_community.llms import Tongyi
    except ImportError:
        Tongyi = None
else:
    Tongyi = None

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
    # 首先尝试使用AI模型提取信息
    try:
        extracted_info = _extract_with_ai_model(text)
        return extracted_info
    except Exception as e:
        print(f"AI模型提取失败，使用传统方法: {str(e)}")
        # 如果AI模型提取失败，使用传统方法
        return _extract_with_traditional_methods(text)

def _extract_with_ai_model(text: str) -> Dict[str, Any]:
    """使用AI模型从文本中提取信息"""
    api_key = os.getenv("TONGYI_API_KEY")
    if not api_key:
        raise ValueError("缺少TONGYI_API_KEY环境变量")
    
    # 检查Tongyi是否可用
    if Tongyi is None:
        raise ValueError("Tongyi模型不可用")
    
    llm = Tongyi(
        dashscope_api_key=api_key,
        model_name="qwen-plus"
    )
    
    prompt = """
    请从以下简历文本中提取信息，并以JSON格式返回。如果某些信息无法提取，请使用空值或空列表。

    提取的信息应包括：
    - name: 姓名（字符串）
    - email: 邮箱地址（字符串）
    - phone: 电话号码（字符串）
    - skills: 技能列表（字符串数组）
    - experience: 工作经验列表，每个经验包含company(公司), position(职位), duration(工作时间), description(工作描述)（对象数组）
    - education: 教育背景列表，每个教育背景包含institution(学校), degree(学位), field(专业), duration(时间)（对象数组）

    简历文本:
    {resume_text}

    请严格按照以下JSON格式返回，不要包含其他文本：
    {{
        "name": "姓名",
        "email": "邮箱",
        "phone": "电话",
        "skills": ["技能1", "技能2", ...],
        "experience": [
            {{
                "company": "公司名称",
                "position": "职位",
                "duration": "工作时间",
                "description": "工作描述"
            }}
        ],
        "education": [
            {{
                "institution": "学校名称",
                "degree": "学位",
                "field": "专业",
                "duration": "时间"
            }}
        ]
    }}
    """.format(resume_text=text[:3000])  # 限制文本长度以避免超出模型限制
    
    response = llm.invoke(prompt)
    
    # 清理响应文本，确保它是有效的JSON
    response = response.strip()
    if response.startswith("```json"):
        response = response[7:]
    if response.endswith("```"):
        response = response[:-3]
    
    try:
        result = json.loads(response)
        # 确保所有必需的字段都存在
        required_fields = ["name", "email", "phone", "skills", "experience", "education"]
        for field in required_fields:
            if field not in result:
                result[field] = "" if field in ["name", "email", "phone"] else []
        return result
    except json.JSONDecodeError:
        # 如果JSON解析失败，抛出异常让传统方法处理
        raise ValueError("AI模型返回的不是有效的JSON格式")

def _extract_with_traditional_methods(text: str) -> Dict[str, Any]:
    """使用传统方法从文本中提取信息"""
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
        r'姓名[:：]\s*(.+)',
        r'Name[:：]\s*(.+)',
        r'^([\\u4e00-\\u9fa5]{2,4})$',  # 中文姓名
        r'^([A-Z][a-z]+ [A-Z][a-z]+)$'  # 英文姓名
    ]
    
    lines = text.strip().split('\n')
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        # 检查是否是姓名
        for pattern in name_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                result["name"] = match.group(1).strip()
                break
    
    # 如果还没找到姓名，尝试从行中提取
    if not result["name"]:
        for i, line in enumerate(lines[:5]):  # 在前5行中查找
            line = line.strip()
            # 姓名通常在简历开头，不包含特殊符号
            if not re.search(r'[@:：\d\|]', line) and 2 <= len(line) <= 4 and re.search(r'[\\u4e00-\\u9fa5]', line):
                result["name"] = line
                break
    
    # 提取邮箱
    email_pattern = r'\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b'
    emails = re.findall(email_pattern, text)
    if emails:
        result["email"] = emails[0]  # 取第一个邮箱
    
    # 提取电话号码
    phone_patterns = [
        r'(1[3-9]\\d{9})',  # 中国手机号
        r'(\\d{3}-\\d{3}-\\d{4})',  # 美国格式
        r'(\\d{2,4}-\\d{7,8})',  # 座机号
        r'(1[3-9]\\d[-\\s]?\\d{4}[-\\s]?\\d{4})',  # 带分隔符的手机号
    ]
    
    for pattern in phone_patterns:
        phone_matches = re.findall(pattern, text)
        if phone_matches:
            result["phone"] = phone_matches[0]
            break
    
    # 提取技能（更灵活的关键词匹配）
    # 先查找"技能"相关标题行
    skills_section_lines = []
    in_skills_section = False
    
    skill_indicators = ['技能', '技术', '专长', '能力', 'skills', 'technologies', 'expertise']
    next_section_indicators = ['经历', '经验', '教育', '项目', '工作', 'education', 'experience', 'project', 'work']
    
    for line in lines:
        line_lower = line.strip().lower()
        
        # 检查是否进入技能部分
        if any(indicator in line_lower for indicator in skill_indicators):
            in_skills_section = True
            continue
            
        # 检查是否离开技能部分
        if in_skills_section and any(indicator in line_lower for indicator in next_section_indicators):
            break
            
        # 收集技能部分的内容
        if in_skills_section:
            skills_section_lines.append(line.strip())
    
    # 从技能区域提取技能
    if skills_section_lines:
        for line in skills_section_lines:
            if not line or '：' in line or ':' in line:
                continue
                
            # 提取可能的技能词
            # 移除常见的前缀和符号
            clean_line = re.sub(r'^[\\d\\-\\.\*\\s]*', '', line)
            if len(clean_line) > 1 and not re.search(r'[,，:：]', clean_line):
                # 检查是否是技能关键词
                if re.search(r'[A-Za-z]+|前端|后端|开发|设计|分析|管理|测试|运维|算法|架构', clean_line):
                    # 进一步清理，去除可能的动词
                    skill = re.sub(r'^(精通|熟悉|了解|掌握|使用|运用)', '', clean_line).strip()
                    if skill and skill not in result["skills"]:
                        result["skills"].append(skill)
    else:
        # 如果没有找到明确的技能区域，使用关键词匹配
        skill_keywords = [
            'Python', 'Java', 'JavaScript', 'React', 'Vue', 'Node.js', 'Spring',
            'Docker', 'Kubernetes', 'MySQL', 'PostgreSQL', 'MongoDB', 'Redis',
            'Git', 'Linux', 'AWS', 'Azure', 'GCP', '机器学习', '深度学习',
            '自然语言处理', '计算机视觉', '数据分析', '大数据', '人工智能',
            '前端', '后端', '全栈', '移动开发', '安卓', 'iOS', '微服务', 'DevOps'
        ]
        
        for keyword in skill_keywords:
            if re.search(r'\\b' + re.escape(keyword) + r'\\b', text, re.IGNORECASE):
                if keyword not in result["skills"]:
                    result["skills"].append(keyword)
    
    # 提取工作经历
    exp_entries = []
    exp_indicators = ['工作经历', '工作经验', '工作背景', 'employment', 'experience', '工作']
    
    for i, line in enumerate(lines):
        line_lower = line.strip().lower()
        if any(indicator in line_lower for indicator in exp_indicators):
            # 找到工作经历部分，开始解析
            j = i + 1
            while j < len(lines):
                line = lines[j].strip()
                line_lower = line.lower()
                
                # 遇到下一节则停止
                if any(indicator in line_lower for indicator in ['教育', 'education', '项目', 'project', '技能', 'skill']):
                    break
                    
                # 解析工作条目（通常是这种格式：职位 | 公司 | 时间）
                if '|' in line or '｜' in line:
                    parts = re.split(r'[|｜]', line)
                    if len(parts) >= 2:
                        exp_entry = {
                            "position": parts[0].strip(),
                            "company": parts[1].strip() if len(parts) > 1 else "",
                            "duration": parts[2].strip() if len(parts) > 2 else "",
                            "description": ""
                        }
                        
                        # 查找职责描述
                        k = j + 1
                        descriptions = []
                        while k < len(lines) and lines[k].strip().startswith(('-', '•', '*')):
                            descriptions.append(re.sub(r'^[-•*\s]+', '', lines[k].strip()))  # 去掉前面的符号
                            k += 1
                        
                        if descriptions:
                            exp_entry["description"] = " ".join(descriptions)
                            
                        exp_entries.append(exp_entry)
                        j = k  # 跳过已处理的描述行
                        continue
                        
                j += 1
            break
    
    result["experience"] = exp_entries
    
    # 提取教育背景
    edu_entries = []
    edu_indicators = ['教育背景', '教育经历', '学历', 'education', 'academic', 'edu']
    
    for i, line in enumerate(lines):
        line_lower = line.strip().lower()
        if any(indicator in line_lower for indicator in edu_indicators):
            # 找到教育背景部分，开始解析
            j = i + 1
            while j < len(lines):
                line = lines[j].strip()
                line_lower = line.lower()
                
                # 遇到下一节则停止
                if any(indicator in line_lower for indicator in ['工作', 'experience', '项目', 'project', '技能', 'skill', '工作']):
                    break
                    
                # 解析教育条目
                if '|' in line or '｜' in line or re.search(r'(大学|学院|学士|硕士|博士)', line):
                    edu_entry = {
                        "institution": "",
                        "degree": "",
                        "field": "",
                        "duration": ""
                    }
                    
                    if '|' in line or '｜' in line:
                        parts = re.split(r'[|｜]', line)
                        # 根据内容判断各部分含义
                        for part in parts:
                            part = part.strip()
                            if re.search(r'(大学|学院)', part):
                                edu_entry["institution"] = part
                            elif re.search(r'(学士|硕士|博士)', part):
                                edu_entry["degree"] = part
                            elif re.search(r'\\d{4}', part):  # 包含年份
                                edu_entry["duration"] = part
                            elif not edu_entry["field"] and re.search(r'(计算机|软件|电子|通信|数学)', part):  # 可能的专业
                                edu_entry["field"] = part
                    else:
                        # 处理无分隔符的情况
                        # 尝试识别不同部分
                        if re.search(r'(大学|学院)', line):
                            edu_entry["institution"] = re.search(r'(.*?(大学|学院))', line).group(1)
                        if re.search(r'(学士|硕士|博士)', line):
                            edu_entry["degree"] = re.search(r'(学士|硕士|博士).*?学位?', line).group(0)
                        if re.search(r'\\d{4}.*?\\d{4}', line):
                            edu_entry["duration"] = re.search(r'\\d{4}.*?\\d{4}', line).group(0)
                        if re.search(r'(计算机|软件|电子|通信|数学)', line):
                            edu_entry["field"] = re.search(r'(计算机|软件|电子|通信|数学).*?(专业)?', line).group(0)
                    
                    edu_entries.append(edu_entry)
                j += 1
            break
    
    result["education"] = edu_entries
    
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