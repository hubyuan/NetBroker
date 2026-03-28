import re
from typing import List

class DataCleaner:
    """
    内置快速轻量级正则与 NLP 工具，负责净化非结构化源数据用于喂给 LLM 网关
    """
    @staticmethod
    def strip_html_tags(text: str) -> str:
        """剥离包含 HTML 或 XML 标记的内容"""
        clean_re = re.compile('<.*?>')
        return re.sub(clean_re, '', text)
        
    @staticmethod
    def extract_code_blocks(markdown_text: str) -> List[str]:
        """提取带栅栏格式的 Markdown 文本内的独立代码块"""
        # 匹配 ```python \n code... \n ```
        pattern = r"```(?:\w+\n)?(.*?)```" # 非贪婪匹配
        blocks = re.findall(pattern, markdown_text, flags=re.DOTALL)
        return [block.strip() for block in blocks]

    @staticmethod
    def normalize_spaces(text: str) -> str:
        """移除多余换行与制表空格，防止过度无意义消耗 LLM Tokens"""
        text = re.sub(r'\n+', '\n', text)
        return re.sub(r'[ \t]+', ' ', text).strip()
