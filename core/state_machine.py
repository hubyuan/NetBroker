from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class ArbitrageState(str, Enum):
    """
    结构洞生命周期状态
    """
    DISCOVERED = "DISCOVERED"  # 发现低 Burt 指数节点 (初筛)
    EVALUATING = "EVALUATING"  # 合规分析与 LLM 认知抽取中
    VERIFIED = "VERIFIED"      # 许可合规通过，并经过工程 AST/Pytest 测试
    EXECUTING = "EXECUTING"    # 变现封装执行中
    MELTED = "MELTED"          # 因风控或回撤熔断销毁

class StructuralHole(BaseModel):
    """
    结构洞节点的核心记录模型载体
    """
    hole_id: str = Field(..., description="结构洞的 UUID 或者 URN")
    source_node_id: str
    target_node_id: str
    
    state: ArbitrageState = ArbitrageState.DISCOVERED
    context_data: Dict[str, Any] = Field(default_factory=dict, description="抓取到的上下文/代码片段")
    
    # AI 认知决断的输出物
    compliance_status: Optional[bool] = None
    expected_margin: Optional[float] = None
    max_drawdown: Optional[float] = None
    pitch_script: Optional[str] = None
    
    # 工程增信层输出物
    test_passed: bool = False
    
    # 生命周期与衰变监控
    v_decay_rate: float = 0.0

    def transition_to(self, new_state: ArbitrageState, reason: str = ""):
        """
        执行状态跃迁，可扩展注入日志逻辑
        """
        _old_state = self.state
        self.state = new_state
        # 可以用 logging 或 event_bus 广播状态转移
        # print(f"Hole {self.hole_id}: {_old_state} -> {self.state} ({reason})")
