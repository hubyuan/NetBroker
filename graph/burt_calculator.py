import networkx as nx
from typing import Dict, List
from graph.network_manager import GraphManager

class BurtCalculator:
    """
    负责计算图中实体节点的 Burt Constraint（伯特约束指数）。
    挖掘处于低聚合中心度却担任两域之间桥梁的核心节点 (潜在高溢价结构洞)。
    """
    def __init__(self, graph_manager: GraphManager):
        self.gm = graph_manager

    async def calculate_all_constraints(self) -> Dict[str, float]:
        """
        内部算法：直接调用内置 networkx 的数学推论包求解全局 constraints。
        (由 C_i = sum_j ( p_ij + sum_q p_iq * p_qj ) ^ 2 推导)
        """
        async with self.gm._lock:
            try:
                # weight 字段为我们定义的链接紧密强度
                constraints_map = nx.constraint(self.gm._graph, weight='weight')
                return constraints_map
            except Exception as e:
                # 若因当前图拓扑破碎无法运算则容错返回
                return {}

    async def find_top_structural_holes(self, top_n: int = 5) -> List[str]:
        """
        对外接口: 输出图谱里最具有跨域套利潜力的 Top 节点。
        返回值以列表形式返回 node_id
        """
        constraints = await self.calculate_all_constraints()
        if not constraints:
            return []
            
        # 根据结构洞理论（Structural Hole Theory）：
        # Constraint（约束指数）值越低，该节点越处于网络连接的桥梁开放地位，不易被某社群垄断。
        sorted_holes = sorted(constraints.items(), key=lambda item: item[1])
        
        # 截取前 top_n 名
        return [node_id for node_id, _val in sorted_holes[:top_n]]
