from pydantic import BaseModel, Field
from typing import List

class CognitiveDecisionOutput(BaseModel):
    """
    负责约束并承接由大语言模型（LLM）执行分析后产出的强制 JSON。
    映射自《产品需求文档 (PRD)》 3.3，将模糊的 AI 判断转化为具备业务实操性的数据实体。
    """
    compliance_status: bool = Field(
        ..., 
        description="合规状态判定，结合内部许可与代码特征推断是否允许商用"
    )
    pitch_script: str = Field(
        ..., 
        description="针对 B 域商业客户的电梯演讲或推销话术 (内涵核心增量)"
    )
    expected_margin: float = Field(
        ..., 
        description="根据套利信息差计算预期利润率溢价评估 (%)"
    )
    max_drawdown: float = Field(
        ..., 
        description="预测变现场景最大回撤风险 (%)，过高时将触发 Human-in-the-Loop 熔断工单"
    )
    execution_steps: List[str] = Field(
        ..., 
        description="面向工程端或变现端的自动化执行流程序列清单"
    )
