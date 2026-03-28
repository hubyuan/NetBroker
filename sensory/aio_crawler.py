import aiohttp
import logging
from typing import Optional

from core.rate_limiter import AsyncTokenBucket

logger = logging.getLogger(__name__)

class AioCrawler:
    """
    负责在 A/B 域进行安全的网络信息抓取。
    内置注入全局 AsyncTokenBucket 防止并发访问过多导致 IP 被封禁。
    """
    def __init__(self, rate_limiter: AsyncTokenBucket):
        self.rate_limiter = rate_limiter
        self.headers = {
            "User-Agent": "NetBroker-Engine/v2.0 (Mozilla/5.0 compatible; AI-Research-Crawler)"
        }

    async def fetch_text(self, url: str) -> Optional[str]:
        """
        通过受到全局限流保护的通道抓取 URL 的文本内容
        """
        # 抓取前必须申请令箭
        await self.rate_limiter.consume(1)
        
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        return await response.text()
                    else:
                        logger.warning(f"Failed to fetch {url}: HTTP {response.status}")
                        return None
        except asyncio.TimeoutError:
            logger.warning(f"Timeout while fetching {url}")
            return None
        except Exception as e:
            logger.error(f"Crawler error on {url}: {str(e)}")
            return None
