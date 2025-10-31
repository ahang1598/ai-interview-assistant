import os
import sys
import json
import re
from dotenv import load_dotenv

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# 加载环境变量
load_dotenv()

# 导入配置以确保环境变量被加载
config_path = os.path.join(os.path.dirname(__file__), 'backend', 'app', 'core')
sys.path.append(config_path)
try:
    from config import settings
except ImportError:
    # 如果无法从模块导入，则直接设置环境变量
    env_file_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_file_path):
        with open(env_file_path, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

def _extract_with_traditional_methods(text: str) -> dict:
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

# 创建一个测试简历文本文件
test_resume_content = """
张三
电话：13812345678
邮箱：zhangsan@example.com

专业技能：
- 精通Python编程语言
- 熟悉机器学习和深度学习框架如TensorFlow和PyTorch
- 有丰富的Web开发经验，使用Django和Flask框架
- 熟练使用数据库如MySQL和MongoDB
- 熟悉云计算平台AWS和阿里云

工作经历：
软件工程师 | ABC科技有限公司 | 2020年1月 - 至今
- 负责开发和维护公司的核心产品
- 使用Python和Django框架构建后端服务
- 设计和实现机器学习模型用于数据分析

初级开发工程师 | XYZ互联网公司 | 2018年6月 - 2019年12月
- 参与Web应用的开发和维护
- 使用Flask框架开发RESTful API
- 协助团队进行数据库设计和优化

教育背景：
计算机科学与技术学士 | 清华大学 | 2014年9月 - 2018年6月
- 主修课程：数据结构、算法设计、数据库原理、人工智能导论
"""

# 将测试内容写入文件
with open("test_resume.txt", "w", encoding="utf-8") as f:
    f.write(test_resume_content)

print("测试简历文件已创建")

# 测试解析功能
try:
    # 读取文件内容
    with open("test_resume.txt", "r", encoding="utf-8") as f:
        content = f.read()
    
    print("\n原始简历内容:")
    print(content)
    
    # 直接测试解析函数
    try:
        result = _extract_with_traditional_methods(content)
        print("\n传统方法解析结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        # 如果环境变量中有API密钥，则测试AI模型方法
        api_key = os.getenv("TONGYI_API_KEY")
        if api_key:
            print("\n正在测试AI模型解析...")
            # 尝试导入AI模型
            try:
                sys.path.append(os.path.join(os.path.dirname(__file__), 'backend/app/utils'))
                from resume_parser import _extract_with_ai_model
                ai_result = _extract_with_ai_model(content)
                print("\nAI模型解析结果:")
                print(json.dumps(ai_result, ensure_ascii=False, indent=2))
            except Exception as e:
                print(f"\nAI模型测试过程中出现错误: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("\n未设置TONGYI_API_KEY环境变量，跳过AI模型测试")
            
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        
except Exception as e:
    print(f"读取文件时出现错误: {e}")

# 创建一个更复杂的测试案例
complex_test_resume = """
李四

联系方式：lisi@gmail.com | 13987654321

技术技能：
编程语言：Python, Java, JavaScript, Go
框架和工具：Django, Flask, React, Vue.js, Docker, Kubernetes
数据库：MySQL, PostgreSQL, MongoDB, Redis
云平台：AWS, Google Cloud Platform, 阿里云
其他：机器学习, 数据分析, DevOps, 敏捷开发

工作经历：
高级软件工程师 | 腾讯科技 | 2021年3月 - 至今
- 负责微信支付后端服务架构设计和开发
- 使用Go和Python构建高并发微服务
- 引入Docker容器化部署，提升部署效率50%

软件工程师 | 百度在线网络技术有限公司 | 2019年7月 - 2021年2月
- 参与百度搜索推荐系统的开发
- 使用机器学习算法优化搜索结果排序
- 协助团队完成系统重构，性能提升30%

教育背景：
硕士学位 | 计算机科学与技术 | 北京大学 | 2017年9月 - 2019年6月

学士学位 | 软件工程 | 华中科技大学 | 2013年9月 - 2017年6月
"""

# 测试复杂简历解析
try:
    print("\n\n=== 复杂简历测试 ===")
    
    # 使用传统方法测试解析
    complex_result = _extract_with_traditional_methods(complex_test_resume)
    print("\n复杂简历传统方法解析结果:")
    print(json.dumps(complex_result, ensure_ascii=False, indent=2))
    
    # 如果环境变量中有API密钥，则测试AI模型方法
    api_key = os.getenv("TONGYI_API_KEY")
    if api_key:
        print("\n正在测试复杂简历AI模型解析...")
        try:
            # 尝试导入AI模型
            sys.path.append(os.path.join(os.path.dirname(__file__), 'backend/app/utils'))
            from resume_parser import _extract_with_ai_model
            complex_ai_result = _extract_with_ai_model(complex_test_resume)
            print("\n复杂简历AI模型解析结果:")
            print(json.dumps(complex_ai_result, ensure_ascii=False, indent=2))
        except Exception as e:
            print(f"\n复杂简历AI模型测试过程中出现错误: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("\n未设置TONGYI_API_KEY环境变量，跳过AI模型测试")
        
except Exception as e:
    print(f"复杂简历测试过程中出现错误: {e}")
    import traceback
    traceback.print_exc()

# 清理测试文件
if os.path.exists("test_resume.txt"):
    os.remove("test_resume.txt")
    print("\n测试文件已清理")