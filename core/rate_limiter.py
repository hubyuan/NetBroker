import asyncio
import time

class AsyncTokenBucket:
    """
    全局令牌桶限流器，用于控制爬虫或API请求速率，防止被封禁。
    支持 asyncio 高并发下的协程安全拿取。
    """
    def __init__(self, capacity: float, refill_rate: float):
        """
        :param capacity: 桶的最大容量 (最大突发并发数)
        :param refill_rate: 每秒补充的 Token 数 (Tokens/sec)
        """
        self.capacity = float(capacity)
        self.refill_rate = float(refill_rate)
        self.tokens = float(capacity)
        self.last_refill_time = time.monotonic()
        self.lock = asyncio.Lock()

    def _refill(self):
        """
        基于当前时间增量充值 Token
        """
        now = time.monotonic()
        elapsed = now - self.last_refill_time
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill_time = now

    async def consume(self, amount: float = 1.0):
        """
        消费指定数量的 Token。如果 Token 不足，则挂起当前协程等待。
        """
        while True:
            async with self.lock:
                self._refill()
                if self.tokens >= amount:
                    self.tokens -= amount
                    return
                # 如果 Token 不够，计算需要休眠的时间
                wait_time = (amount - self.tokens) / self.refill_rate
            
            # 释放锁并在外部 sleep，让出控制权让其他协程也可以争取/执行
            await asyncio.sleep(wait_time)
