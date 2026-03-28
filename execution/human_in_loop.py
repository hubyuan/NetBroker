import logging
import asyncio

logger = logging.getLogger(__name__)

class HumanInTheLoop:
    """
    处理超越了硬编码安全垫边界外的异常流，强制挂起并申请人工 Webhook 回调指令。
    """
    @classmethod
    async def request_human_approval(cls, hole_id: str, risk_reason: str) -> bool:
        """
        悬挂当前套利洞记录，通过异步 API 推送至工单后台 (这里为 MOCK)。
        由于系统依靠 asyncio 非阻塞，个别洞的等待不会导致其他机会抓取停摆。
        """
        logger.critical(f"👨‍💻 [HITL REQUIRED] Escalating Arbitration ID {hole_id} details due to limits.")
        logger.critical(f"👨‍💻 Escalate Reason: {risk_reason}")
        
        logger.info("Pushing Webhook notification to Slack/Feishu ... waiting for supervisor callback.")
        
        # 挂起模拟人类阅读并审阅代码的用时
        await asyncio.sleep(2.0)
        
        # 降级：默认退回所有高危资产
        logger.warning(f"👨‍💻 [HITL RESPONSE] Human ignored or rejected Arbitrage ID {hole_id}.")
        return False
