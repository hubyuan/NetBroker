import asyncio
import json
import logging
import os
from google import genai
from google.genai import types

from cognitive.json_validator import CognitiveDecisionOutput

logger = logging.getLogger(__name__)

class GeminiGateway:
    """
    承接由 Graph 筛选出的高溢价结构洞数据，组装上下文 (Context) 构建 Prompt
    交由高并发的 Flash Lite 模型作出带有兜底性质的结构化定论。
    """
    def __init__(self, api_key: str = None):
        # 优先读取实例化传入的 key 或者退化到环境变量
        key = api_key or os.environ.get("GEMINI_API_KEY", "")
        if not key:
            logger.warning("No GEMINI_API_KEY detected! Gateway running in MOCKED mode.")
        
        self.client = genai.Client(api_key=key) if key else None
        
        # 选定根据 TDD 中指定的高频并发网关
        self.model_name = 'gemini-3.1-flash-lite-preview'

    async def evaluate_arbitrage_context(self, context_data: str) -> CognitiveDecisionOutput:
        """
        抛出包含上下文的任务让模型理解代码意图或套利标的，必须严格吐出 `CognitiveDecisionOutput` 框架。
        针对单进程高并发需求，运用 `asyncio.to_thread` 防止阻塞底层 I/O。
        """
        if not self.client:
            logger.error("Client not initialized. Sending dummy mock payload.")
            return CognitiveDecisionOutput(
                compliance_status=False,
                pitch_script="[MOCK] - API KEY MISSING, Cannot proceed execution.",
                expected_margin=0.0,
                max_drawdown=100.0,
                execution_steps=["Halt system", "Add API key"]
            )
            
        json_schema = json.dumps(CognitiveDecisionOutput.model_json_schema())
        
        # 将指令与 Schema 完全打平发送
        system_rules = (
            "You are an elite automated data broker and arbitrage engine. "
            f"You MUST format the response purely as a valid JSON object matching this JSON Schema: {json_schema} "
            "Do not include any external text or markdown block code wrappers like ```json"
        )
        user_prompt = f"{system_rules}\n\n基于以下我们在多域边缘探测到的结构洞数据组合，对其进行全面合规与套利价值分析并返回符合要求的 JSON：\n---\n{context_data}\n---"

        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2, # 逻辑计算，保持绝对严苛判断
        )

        try:
            logger.debug(f"Pinging Flash-Lite... context_size: {len(context_data)} bytes")
            # 通过 asyncio 把同步的 genai API 挂接到协程调度中
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_name,
                contents=user_prompt,
                config=config
            )
            
            # 严格解析
            text_body = response.text.strip()
            # 容错处理偶尔依然出现的 markdown 包装
            if text_body.startswith("```json"):
                text_body = text_body[7:-3].strip()
                
            return CognitiveDecisionOutput.model_validate_json(text_body)
            
        except Exception as e:
            logger.error(f"LLM Gateway extraction halted ungracefully: {e}")
            raise

    async def evaluate_arxiv_paper(self, paper: dict) -> CognitiveDecisionOutput:
        """
        专用版结构洞分析网络，聚焦于翻译、提炼和打分学术文章。
        """
        if not self.client:
            logger.warning("No API Key: Generating Mocked arXiv Evaluation")
            return CognitiveDecisionOutput(
                compliance_status=True,
                pitch_script=f"【Mock的中文翻译】论文原名: {paper.get('title')}",
                expected_margin=88.5,
                max_drawdown=10.0,
                execution_steps=["Mocked_LLM", "arXiv"]
            )
            
        json_schema = json.dumps(CognitiveDecisionOutput.model_json_schema())
        
        system_rules = (
            "You are an expert AI Research Analyst and strict English-to-Chinese Technical Translator. "
            f"You MUST format the response purely as a valid JSON object matching this schema: {json_schema}. "
            "Do NOT include the ```json markdown wrapper."
        )
        
        user_prompt = f"""
请分析以下最新的 arXiv 人工智能论文摘要，并将其结构化转换为符合 Obsidian 知识库索引原则的 JSON！

【论文源数据】
标题: {paper['title']}
摘要: {paper['summary']}

【你的转换与分析映射规则】
- compliance_status: 判断本篇论文是否公开可用 (针对开放获取库，通常应为 true)。
- pitch_script: ⭐ 核心诉求！请将"摘要"**翻译为您读过的最流畅的中文**，并提炼出核心突破点。以报告口吻书写，必须是纯中文！
- expected_margin: 根据论文颠覆性打分，代表其学术套利价值 (0-100 的浮点数)。
- max_drawdown: 评估普通开发者在实际落地复现该研究中的门槛阻力/难产风险 (0-100的浮点数，比如高算力高硬件独占=高风险)。
- execution_steps: 提取 3 至 5 个适合 Obsidian 知识库检索使用的英文词根技术标签 (例如 ["LLM", "Agent", "RAG"])。
"""

        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.3, # 翻译时增加一些活泼性
        )

        try:
            logger.debug(f"Pinging Flash-Lite... evaluating arXiv {paper.get('id')}")
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_name,
                contents=f"{system_rules}\n\n{user_prompt}",
                config=config
            )
            
            text_body = response.text.strip()
            if text_body.startswith("```json"):
                text_body = text_body[7:-3].strip()
                
            return CognitiveDecisionOutput.model_validate_json(text_body)
            
        except Exception as e:
            logger.error(f"ArXiv LLM translation evaluation crashed: {e}")
            raise
