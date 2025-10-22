from langchain_community.llms import Tongyi
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from typing import List, Dict, Any
import os

class LangChainIntegration:
    def __init__(self, tongyi_api_key: str = None):
        """
        初始化LangChain集成，使用阿里云Qwen模型
        """
        api_key = tongyi_api_key or os.getenv("TONGYI_API_KEY")
        if not api_key:
            raise ValueError("需要阿里云API密钥")
        
        # 初始化语言模型（使用阿里云Qwen）
        self.llm = Tongyi(
            dashscope_api_key=api_key,
            model_name="qwen-plus"  # 可以根据需要更换为 qwen-turbo 或 qwen-max
        )
        
        # 定义面试助手的系统提示
        self.system_prompt = """你是一个专业的技术面试官和职业顾问。你的任务是：
        1. 根据候选人的简历提出相关的面试问题
        2. 对候选人的回答提供反馈和建议
        3. 模拟真实的面试对话
        4. 保持专业和友好的态度
        
        请记住：
        - 问题应该与候选人的经验和技能相关
        - 提供有建设性的反馈
        - 避免过于简单或过于困难的问题
        - 鼓励候选人详细阐述他们的经验和技能
        """
        
    def generate_interview_question(self, resume_data: Dict[str, Any]) -> str:
        """
        根据简历数据生成面试问题
        """
        prompt = PromptTemplate(
            input_variables=["name", "skills", "experience"],
            template="""
            基于以下候选人信息生成一个相关的面试问题：
            
            姓名: {name}
            技能: {skills}
            工作经验: {experience}年
            
            请提出一个技术问题或行为问题，帮助评估候选人的技能和经验。
            """
        )
        
        # 提取简历关键信息
        name = resume_data.get("name", "候选人")
        skills = ", ".join(resume_data.get("skills", []))
        experience = resume_data.get("experience_years", "未知")
        
        # 创建链
        chain = LLMChain(llm=self.llm, prompt=prompt)
        
        # 生成问题
        response = chain.run({
            "name": name,
            "skills": skills,
            "experience": experience
        })
        
        return response
    
    def evaluate_answer(self, question: str, answer: str, resume_data: Dict[str, Any]) -> str:
        """
        评估候选人对面试问题的回答
        """
        prompt = PromptTemplate(
            input_variables=["question", "answer", "skills"],
            template="""
            作为一个技术面试官，请评估候选人对以下问题的回答：
            
            面试问题: {question}
            候选人回答: {answer}
            候选人技能: {skills}
            
            请提供以下内容：
            1. 回答的评分（1-10分）
            2. 优点
            3. 改进建议
            4. 如果适用，提供更完整的答案示例
            """
        )
        
        skills = ", ".join(resume_data.get("skills", []))
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        
        response = chain.run({
            "question": question,
            "answer": answer,
            "skills": skills
        })
        
        return response
    
    def chat_completion(self, messages: List[Dict[str, str]], resume_data: Dict[str, Any] = None) -> str:
        """
        处理多轮对话
        """
        # 转换消息格式
        langchain_messages = [SystemMessage(content=self.system_prompt)]
        
        for msg in messages:
            if msg["role"] == "user":
                langchain_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                langchain_messages.append(AIMessage(content=msg["content"]))
        
        # 获取响应
        response = self.llm.invoke(langchain_messages)
        # 检查response是否为字符串，如果是则直接返回，否则返回content属性
        if isinstance(response, str):
            return response
        else:
            return response.content