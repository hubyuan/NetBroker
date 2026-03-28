import asyncio
import logging
from dotenv import load_dotenv

from core.engine_loop import NetBrokerEngine

# 全局载入 .env 文件中的环境变量配置
load_dotenv()

# 配置带有模块路径格式的高级日志
logging.basicConfig(
    level=logging.INFO, # 可以修改为 DEBUG 获得更多内脏输出
    format='%(asctime)s | %(name)-18s | %(levelname)-7s | %(message)s'
)

async def main():
    """
    单一入口
    """
    engine = NetBrokerEngine()
    try:
        # 挂起主事件循环，直到守护进程死除
        await engine.start()
    except KeyboardInterrupt:
        # 优雅退出
        await engine.stop()

if __name__ == "__main__":
    asyncio.run(main())
