import asyncio
import time
import networkx as nx
from typing import Dict, Any, List, Tuple

class GraphManager:
    """
    基于 NetworkX (DiGraph) 维护网络实体节点拓扑分布。
    提供 Asyncio.Lock 的单例方法以避免在并发更新下触发 Dictionary Changed Iterate 异常。
    """
    def __init__(self):
        self._graph = nx.DiGraph()
        self._lock = asyncio.Lock()

    async def add_node(self, node_id: str, **attributes):
        """向图内安全注入新发现的实体节点"""
        async with self._lock:
            if not self._graph.has_node(node_id):
                self._graph.add_node(node_id, **attributes)
            else:
                self._graph.nodes[node_id].update(attributes)

    async def add_or_update_edge(self, u: str, v: str, weight: float, ttl: float = 259200):
        """
        向图注入路径或依存关系。
        :param ttl: 边的生命周期（默认 72 小时，单位：秒）
        """
        async with self._lock:
            now = time.time()
            if self._graph.has_edge(u, v):
                # 更新权重并且刷新最后活跃探测时间
                self._graph[u][v]['weight'] = weight
                self._graph[u][v]['last_seen'] = now
                # TTL 可重置
                self._graph[u][v]['ttl'] = ttl
            else:
                self._graph.add_edge(u, v, weight=weight, discovered_at=now, last_seen=now, ttl=ttl)

    async def get_edges(self, data: bool = True) -> List[Any]:
        """获取全量拓扑边的数据 Snapshot"""
        async with self._lock:
            return list(self._graph.edges(data=data))

    async def get_nodes(self, data: bool = True) -> List[Any]:
        """获取全量实体节点的数据 Snapshot"""
        async with self._lock:
            return list(self._graph.nodes(data=data))

    async def remove_edges_from(self, ebunch: List[Tuple[str, str]]):
        """基于剔除清单执行批量边销毁"""
        async with self._lock:
            self._graph.remove_edges_from(ebunch)
