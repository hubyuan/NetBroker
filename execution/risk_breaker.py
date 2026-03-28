import logging

logger = logging.getLogger(__name__)

class RiskBreaker:
    """
    负责监控认知层(LLM)产出的交易回撤风险参数。
    当且仅当该模块许可放行，流程才可直接输出；否则移交 Human in the Loop 处理。
    """
    # 当预估最大回撤 > 30% 时触发生死锁
    MAX_DRAWDOWN_THRESHOLD = 30.0

    @classmethod
    def should_trigger_breaker(cls, max_drawdown: float) -> bool:
        """
        判断是否应当主动切断自动化。
        """
        if max_drawdown > cls.MAX_DRAWDOWN_THRESHOLD:
            logger.warning(
                f"🚨 RISK BREAKER OPENED: Est. Max Drawdown ({max_drawdown}%) "
                f"exceeds safety threshold ({cls.MAX_DRAWDOWN_THRESHOLD}%)!"
            )
            return True
        return False
