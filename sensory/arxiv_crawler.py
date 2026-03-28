import xml.etree.ElementTree as ET
import logging
from typing import List, Dict

from sensory.aio_crawler import AioCrawler
from core.rate_limiter import AsyncTokenBucket

logger = logging.getLogger(__name__)

class ArxivCrawler(AioCrawler):
    """
    专门针对 arXiv API 的实盘探针实现。
    由于继承了 AioCrawler，底层网络访问自动被 global AsyncTokenBucket 限流。
    """
    def __init__(self, rate_limiter: AsyncTokenBucket):
        super().__init__(rate_limiter)
        # arXiv 的特定防 ban Header
        self.headers = {
            "User-Agent": "NetBroker-Engine/v2.0 (mailto:admin@example.com)" 
        }

    async def fetch_latest_ai_papers(self, max_results: int = 5) -> List[Dict[str, str]]:
        # 查询最近提交的关于计算机科学AI领域的论文，按时间倒序
        url = f"http://export.arxiv.org/api/query?search_query=cat:cs.AI&sortBy=lastUpdatedDate&sortOrder=descending&max_results={max_results}"
        logger.info(f"🔍 Crawling latest AI papers from arXiv API...")
        
        xml_data = await self.fetch_text(url)
        if not xml_data:
            return []
            
        return self._parse_arxiv_xml(xml_data)

    def _parse_arxiv_xml(self, xml_data: str) -> List[Dict[str, str]]:
        papers = []
        try:
            root = ET.fromstring(xml_data)
            # arXiv API 采用 Atom XML 命名空间
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            for entry in root.findall('atom:entry', ns):
                paper = {
                    "id": entry.find('atom:id', ns).text,
                    "title": entry.find('atom:title', ns).text.replace('\n', ' ').strip(),
                    "summary": entry.find('atom:summary', ns).text.strip(),
                    "published": entry.find('atom:published', ns).text,
                    "link": entry.find('atom:id', ns).text
                }
                papers.append(paper)
        except Exception as e:
            logger.error(f"Failed to parse arXiv XML payload: {e}")
        return papers
