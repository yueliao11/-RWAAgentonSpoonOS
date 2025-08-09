"""
RWA Yield Analysis Agent - 专门用于分析真实世界资产收益的智能代理
"""

from typing import List, Dict, Any, Optional
from pydantic import Field
from spoon_ai.agents.toolcall import ToolCallAgent
from spoon_ai.tools import ToolManager
from spoon_ai.chat import ChatBot
from spoon_ai.schema import Message, Role
import logging

logger = logging.getLogger(__name__)

class RWAYieldAgent(ToolCallAgent):
    """RWA收益分析专家代理"""
    
    name: str = "rwa_yield_agent"
    description: str = "专门用于分析RWA（真实世界资产）和DeFi收益的智能代理"
    system_prompt: str = """你是一个专业的RWA收益分析专家。你的主要任务包括：

1. 收集和标准化不同RWA协议的收益数据
   - 支持的协议：Centrifuge, Goldfinch, Maple Finance, Credix等
   - 资产类型：代币化债券、房地产收益流、碳信用额度、发票融资等

2. 计算和比较统一的APY（年化收益率）指标
   - 考虑不同的计算方法：简单利息、复利、连续复利
   - 调整风险因素和协议特定的费用结构

3. 提供投资组合优化建议
   - 基于风险承受能力推荐资产配置
   - 考虑流动性、锁定期和最低投资要求

4. 预测收益趋势
   - 分析历史数据识别模式
   - 结合市场条件提供前瞻性分析

5. 生成专业的分析报告
   - 清晰的数据可视化建议
   - 可操作的投资建议
   - 风险警示和注意事项

请始终使用准确的数据，并以专业、客观的方式提供分析。当数据不足时，明确说明限制性因素。"""
    
    max_steps: int = 15
    
    # 自定义配置
    supported_protocols: List[str] = Field(
        default=["centrifuge", "goldfinch", "maple", "credix", "clearpool", "truefi"],
        description="支持的RWA协议列表"
    )
    
    asset_categories: List[str] = Field(
        default=["bonds", "real_estate", "carbon_credits", "invoices", "private_credit"],
        description="支持的资产类别"
    )
    
    risk_levels: Dict[str, float] = Field(
        default={
            "low": 0.2,
            "medium": 0.5,
            "high": 0.8,
            "very_high": 1.0
        },
        description="风险等级映射"
    )
    
    available_tools: ToolManager = Field(
        default_factory=lambda: ToolManager([
            # 这里将添加RWA相关工具
        ])
    )
    
    async def analyze_protocol_yields(self, protocol: str, timeframe: str = "30d") -> Dict[str, Any]:
        """分析特定协议的收益率"""
        prompt = f"""
        请分析{protocol}协议在过去{timeframe}的收益表现：
        1. 当前APY和历史APY趋势
        2. 主要资产池的表现
        3. 风险调整后的收益
        4. 与其他类似协议的比较
        """
        
        self.add_message("user", prompt)
        return await self.run(prompt)
    
    async def compare_yields(self, protocols: List[str], asset_type: Optional[str] = None) -> Dict[str, Any]:
        """比较多个协议的收益率"""
        asset_filter = f"针对{asset_type}类型资产" if asset_type else "所有资产类型"
        protocols_str = ", ".join(protocols)
        
        prompt = f"""
        请比较以下RWA协议的收益率（{asset_filter}）：
        协议列表：{protocols_str}
        
        请提供：
        1. 标准化的APY比较表
        2. 风险调整后收益（Sharpe比率）
        3. 流动性和锁定期对比
        4. 推荐的协议选择及理由
        """
        
        self.add_message("user", prompt)
        return await self.run(prompt)
    
    async def optimize_portfolio(
        self, 
        investment_amount: float,
        risk_tolerance: str,
        target_protocols: Optional[List[str]] = None,
        constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """优化RWA投资组合"""
        protocols = target_protocols or self.supported_protocols
        constraints_str = f"约束条件：{constraints}" if constraints else "无特殊约束"
        
        prompt = f"""
        请为以下投资需求优化RWA投资组合：
        - 投资金额：${investment_amount:,.2f}
        - 风险承受能力：{risk_tolerance}
        - 目标协议：{', '.join(protocols)}
        - {constraints_str}
        
        请提供：
        1. 推荐的资产配置方案
        2. 预期的组合收益率和风险指标
        3. 各资产的具体投资金额
        4. 再平衡建议和时间表
        5. 主要风险因素和缓解措施
        """
        
        self.add_message("user", prompt)
        return await self.run(prompt)
    
    async def forecast_yields(
        self,
        protocol: str,
        asset_type: str,
        forecast_period: str = "90d"
    ) -> Dict[str, Any]:
        """预测未来收益率"""
        prompt = f"""
        请预测{protocol}协议中{asset_type}类资产在未来{forecast_period}的收益表现：
        
        分析要点：
        1. 基于历史数据的趋势分析
        2. 市场条件对收益的潜在影响
        3. 协议特定因素（如新产品发布、治理变更等）
        4. 给出收益率的预测区间（乐观/基准/悲观情景）
        5. 影响预测准确性的关键因素
        """
        
        self.add_message("user", prompt)
        return await self.run(prompt)
    
    async def generate_yield_report(
        self,
        protocols: List[str],
        report_type: str = "comprehensive",
        format: str = "markdown"
    ) -> str:
        """生成收益分析报告"""
        report_types = {
            "comprehensive": "全面分析报告",
            "executive": "执行摘要",
            "technical": "技术深度分析",
            "risk": "风险评估报告"
        }
        
        prompt = f"""
        请生成一份{report_types.get(report_type, report_type)}，涵盖以下RWA协议：
        {', '.join(protocols)}
        
        报告要求：
        1. 格式：{format}
        2. 包含数据截止时间
        3. 关键指标仪表板
        4. 详细的收益分析
        5. 风险评估矩阵
        6. 投资建议和下一步行动
        
        请确保报告专业、数据准确、结论有据可依。
        """
        
        self.add_message("user", prompt)
        result = await self.run()
        return result
    
    def _calculate_risk_adjusted_return(self, apy: float, risk_score: float) -> float:
        """计算风险调整后的收益率"""
        risk_free_rate = 0.045  # 4.5%的无风险利率
        return (apy - risk_free_rate) / risk_score if risk_score > 0 else 0
    
    def _standardize_apy(self, raw_yield: float, compound_frequency: str = "daily") -> float:
        """标准化APY计算"""
        frequencies = {
            "daily": 365,
            "weekly": 52,
            "monthly": 12,
            "quarterly": 4,
            "annually": 1
        }
        
        n = frequencies.get(compound_frequency, 365)
        # 转换为年化复利收益率
        apy = (1 + raw_yield / n) ** n - 1
        return apy