import time
import logging
import networkx as nx
from graph.network_manager import GraphManager

logger = logging.getLogger(__name__)

class EdgePruner:
    """
    异步常驻后台执行的维护组件 (L2层附属)。
    定期依据 TTL 及最短路径极短化（衰减率超限）等指标剪除无价值的关联绑定。
    """
    def __init__(self, graph_manager: GraphManager):
        self.gm = graph_manager

    async def prune_expired_edges(self):
        """
        修剪超出生存周期 (TTL) 且未被爬虫刷新特征活跃度的陈旧边
        """
        edges = await self.gm.get_edges(data=True)
        now = time.time()
        to_remove = []

        for u, v, data in edges:
            last_seen = data.get('last_seen', 0.0)
            ttl = data.get('ttl', 259200.0)
            if now > last_seen + ttl:
                to_remove.append((u, v))

        if to_remove:
            await self.gm.remove_edges_from(to_remove)
            logger.info(f"Graph Pruning: Removed {len(to_remove)} expired edges due to TTL expiration.")

    async def check_decay_threshold(self, start_node: str, end_node: str, threshold: float = 0.5) -> bool:
        """
        测算结构洞两端跨域圈层节点的最短信息传播路径。
        若路径权重非常短，提示套利信息已被市场填平。
        :return: True 表示已经塌陷需要 MELTED，False 表示套利空间仍在安全距离。
        """
        async with self.gm._lock:
            try:
                # 按照 TDD/PRD 衡量路程折叠率
                path_length = nx.shortest_path_length(
                    self.gm._graph, 
                    source=start_node, 
                    target=end_node, 
                    weight='weight'
                )
                if path_length < threshold:
                    logger.warning(f"Structural hole between {start_node} & {end_node} melted! decay threshold triggers.")
                    return True
            except nx.NetworkXNoPath:
                # 仍存在信息隔离断带，非常安全
                pass
            except nx.NodeNotFound:
                # 节点已被回收
                return True
                
        return False
