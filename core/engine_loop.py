import asyncio
import logging

from core.rate_limiter import AsyncTokenBucket
from core.state_machine import ArbitrageState, StructuralHole

# 引入本场景专精探针及处理层
from sensory.arxiv_crawler import ArxivCrawler
from cognitive.llm_gateway import GeminiGateway
from execution.obsidian_writer import ObsidianWriter

logger = logging.getLogger(__name__)

class NetBrokerEngine:
    def __init__(self):
        # 放宽爬虫并发池
        self.token_bucket = AsyncTokenBucket(capacity=20, refill_rate=2)
        self.is_running = False
        
        # 激活本套利的实例集群
        self.crawler = ArxivCrawler(self.token_bucket)
        self.llm_gateway = GeminiGateway()
        self.obsidian_writer = ObsidianWriter("./ObsidianVault/Arxiv_Daily")
        
        # 缓存尚未跑完生命周期的结构洞 (论文)
        self.pending_holes: dict[str, StructuralHole] = {}

    async def start(self):
        """
        启动 NetBroker 主引擎的协程任务簇
        """
        self.is_running = True
        logger.info("🟢 NetBroker v2.0 Engine Starting...")
        
        # 集中派发所有的常驻后台协程
        await asyncio.gather(
            self._pruning_task(),
            self._crawler_task(),
            self._evaluation_task()
        )

    async def stop(self):
        self.is_running = False
        logger.info("🔴 NetBroker Engine Stopped.")

    async def _pruning_task(self):
        """
        常驻后台进程 (图谱计算层) : 定期修剪网络边、监控衰变率 TTL
        """
        while self.is_running:
            logger.debug("Pruning Task: Scanning NetworkX graph for expired edges...")
            # TODO: 调用 graph/edge_pruner 做清洗和 Burt 重算
            await asyncio.sleep(60) # 每60秒执行一轮大扫除

    async def _crawler_task(self):
        """
        常驻后台抓取进程
        """
        while self.is_running:
            logger.debug("Crawler Task: Polling arXiv API for new CS.AI publications...")
            
            # 抓取最近的 3 篇文献
            papers = await self.crawler.fetch_latest_ai_papers(max_results=3)
            
            for paper in papers:
                p_id = paper['id']
                if p_id not in self.pending_holes:
                    logger.info(f"✨ 发现新价值学术结构洞: {paper['title']}")
                    hole = StructuralHole(
                        hole_id=p_id,
                        source_node_id=p_id,
                        target_node_id="Obsidian_Vault_Local",
                        state=ArbitrageState.DISCOVERED,
                        context_data=paper
                    )
                    self.pending_holes[p_id] = hole
            
            # 休眠 30 秒再次轮询 (生产环境中可以设为数小时)
            await asyncio.sleep(30)

    async def _evaluation_task(self):
        """
        常驻后台认知决策进程，将学术文章转化为翻译后的中文简报。
        """
        while self.is_running:
            # list() 防止 dict 遍历变更报错
            for h_id, hole in list(self.pending_holes.items()):
                if hole.state == ArbitrageState.DISCOVERED:
                    logger.info(f"🤖 投入翻译流水线: {hole.context_data['title']} - {h_id}")
                    hole.transition_to(ArbitrageState.EVALUATING)
                    
                    try:
                        decision = await self.llm_gateway.evaluate_arxiv_paper(hole.context_data)
                        
                        # 同步模型产出
                        hole.compliance_status = decision.compliance_status
                        hole.expected_margin = decision.expected_margin
                        hole.max_drawdown = decision.max_drawdown
                        hole.pitch_script = decision.pitch_script
                        
                        # 因属于非代码内容，无需进 AST 及 Pytest，直接跃向变现端
                        hole.transition_to(ArbitrageState.EXECUTING)
                        
                        logger.info(f"📥 写入 Obsidian... 价值判断={decision.expected_margin}分")
                        self.obsidian_writer.write_daily_brief(
                            node_id=hole.hole_id,
                            title=hole.context_data['title'],
                            pitch_script=decision.pitch_script,
                            tags=decision.execution_steps,
                            link=hole.context_data['link']
                        )
                        
                        # 生命周期宣告闭环熔断，不再追踪
                        hole.transition_to(ArbitrageState.MELTED, "Successfully Arbitraged To Vault")
                        
                    except Exception as e:
                        logger.error(f"Evaluating {h_id} failed: {e}")
                        # 回退至待评估池做下一次重试安全网
                        hole.transition_to(ArbitrageState.DISCOVERED)
            
            # 定时轮询池子里的 DISCOVERED 机会
            await asyncio.sleep(5)

async def main_loop():
    """引擎入口启动封装"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    engine = NetBrokerEngine()
    try:
        await engine.start()
    except KeyboardInterrupt:
        await engine.stop()

if __name__ == "__main__":
    asyncio.run(main_loop())
