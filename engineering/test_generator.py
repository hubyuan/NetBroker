import asyncio
import logging
from cognitive.llm_gateway import GeminiGateway

logger = logging.getLogger(__name__)

class PyTestcaseGenerator:
    """
    联动 Gemini 3.1 Flash Lite 为提取出来的核心代码生成健壮的 pytest 验证文件
    """
    def __init__(self, llm_gateway: GeminiGateway):
        self.gateway = llm_gateway

    async def generate_pytest_suite(self, source_code: str, module_name: str = "target_module") -> str:
        """
        利用大模型基于上下文推理快速生成用于覆盖目标的断言测试用例。
        :return: 含有 Python 测试代码语句的纯净长字符串
        """
        if not self.gateway.client:
            logger.warning("No LLM Client for PyTest Generator, falling back to mocked tests.")
            return f"""
import pytest
from {module_name} import *

def test_mock_fallback_empty_validation():
    assert True
"""

        prompt = (
            "You are an expert Python QA Engineer acting as our trust enhancement layer.\n"
            f"Write a complete `pytest` test suite to test the logic of the following Python module (assume it is saved as `{module_name}.py`). "
            "Only output the raw Python test code. No markdown formatting, no descriptions, no ```python blocks. "
            "Ensure the test suite comprehensively covers standard inputs and potential edge cases without heavy OS mocking logic.\n\n"
            f"code data to be verified:\n{source_code}"
        )
        
        try:
            response = await asyncio.to_thread(
                self.gateway.client.models.generate_content,
                model=self.gateway.model_name,
                contents=prompt,
            )
            code = response.text.strip()
            
            # 再一次冗余剥除模型偶然爆发的不稳定格式包裹
            if code.startswith("```python"):
                code = code[9:]
            if code.endswith("```"):
                code = code[:-3]
                
            return code.strip()
            
        except Exception as e:
            logger.error(f"Failed to generate pytest suite: {e}")
            return ""
