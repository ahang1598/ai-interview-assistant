import unittest
from ..app.utils import resume_parser

class TestResumeParser(unittest.TestCase):
    def test_extract_info_from_text(self):
        # 测试信息提取功能
        sample_text = """
        John Doe
        john.doe@example.com
        +1 234 567 8900
        
        Skills: Python, JavaScript, React, Node.js
        5 years of experience
        """
        
        result = resume_parser._extract_info_from_text(sample_text)
        
        self.assertEqual(result["name"], "John Doe")
        self.assertEqual(result["email"], "john.doe@example.com")
        self.assertEqual(result["phone"], "+1 234 567 8900")
        self.assertIn("Python", result["skills"])
        self.assertEqual(result["experience_years"], "5")

    def test_analyze_resume(self):
        # 测试简历分析功能
        sample_data = {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "+1 234 567 8900",
            "skills": ["Python", "JavaScript", "React"],
            "experience_years": "5",
            "raw_text": "Sample text"
        }
        
        analysis = resume_parser.analyze_resume(sample_data)
        
        self.assertEqual(analysis["skills_count"], 3)
        self.assertTrue(analysis["has_contact_info"])

if __name__ == "__main__":
    unittest.main()