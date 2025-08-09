"""
Portfolio Optimizer Agent - 使用图工作流优化RWA投资组合
"""

from typing import TypedDict, List, Dict, Any, Optional, Annotated
import operator
from datetime import datetime
import asyncio
import logging

from spoon_ai.agents.graph_agent import GraphAgent
from spoon_ai.graph import StateGraph, Command
from spoon_ai.llm.manager import get_llm_manager
from spoon_ai.schema import Message
from spoon_ai.tools import ToolManager
from spoon_ai.tools.rwa_tools import (
    RWAProtocolDataTool,
    YieldStandardizationTool,
    RWAPortfolioAnalysisTool
)

logger = logging.getLogger(__name__)

class PortfolioState(TypedDict):
    """投资组合优化状态"""
    # 用户输入
    user_preferences: Dict[str, Any]
    investment_amount: float
    risk_tolerance: str  # low, medium, high
    target_protocols: List[str]
    constraints: Dict[str, Any]
    
    # 分析数据
    available_assets: List[Dict[str, Any]]
    protocol_yields: Dict[str, Any]
    risk_scores: Dict[str, float]
    correlation_matrix: Optional[Dict[str, Any]]
    
    # 优化结果
    optimized_portfolio: Dict[str, Any]
    expected_returns: float
    portfolio_risk: float
    sharpe_ratio: float
    
    # 预测和建议
    yield_forecast: Dict[str, Any]
    rebalancing_schedule: List[Dict[str, Any]]
    risk_warnings: List[str]
    recommendations: List[str]
    
    # 工作流控制
    messages: Annotated[List[Message], operator.add]
    current_step: str
    error: Optional[str]
    completed: bool


class PortfolioOptimizerAgent(GraphAgent):
    """RWA投资组合优化代理"""
    
    name: str = "portfolio_optimizer"
    description: str = "使用先进的图工作流和多步骤分析优化RWA投资组合"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tools = ToolManager([
            RWAProtocolDataTool(),
            YieldStandardizationTool(),
            RWAPortfolioAnalysisTool()
        ])
        self.llm_manager = None
    
    async def initialize(self):
        """初始化LLM管理器"""
        if not self.llm_manager:
            self.llm_manager = get_llm_manager()
    
    def build_graph(self) -> StateGraph:
        """构建投资组合优化工作流图"""
        # 创建状态图
        graph = StateGraph(PortfolioState)
        
        # 添加节点
        graph.add_node("collect_preferences", self.collect_user_preferences)
        graph.add_node("fetch_protocol_data", self.fetch_protocol_data)
        graph.add_node("analyze_yields", self.analyze_yields)
        graph.add_node("calculate_risks", self.calculate_risk_metrics)
        graph.add_node("check_constraints", self.check_constraints)
        graph.add_node("optimize_allocation", self.optimize_allocation)
        graph.add_node("forecast_performance", self.forecast_performance)
        graph.add_node("generate_recommendations", self.generate_recommendations)
        graph.add_node("finalize_portfolio", self.finalize_portfolio)
        
        # 添加边（定义工作流）
        graph.add_edge("collect_preferences", "fetch_protocol_data")
        graph.add_edge("fetch_protocol_data", "analyze_yields")
        graph.add_edge("analyze_yields", "calculate_risks")
        graph.add_edge("calculate_risks", "check_constraints")
        
        # 添加条件边
        graph.add_conditional_edges(
            "check_constraints",
            self.should_proceed_with_optimization,
            {
                "optimize": "optimize_allocation",
                "adjust": "collect_preferences",  # 返回调整偏好
                "error": "finalize_portfolio"
            }
        )
        
        graph.add_edge("optimize_allocation", "forecast_performance")
        graph.add_edge("forecast_performance", "generate_recommendations")
        graph.add_edge("generate_recommendations", "finalize_portfolio")
        
        # 设置入口点
        graph.set_entry_point("collect_preferences")
        
        return graph
    
    async def collect_user_preferences(self, state: PortfolioState) -> Dict[str, Any]:
        """收集用户偏好"""
        logger.info("Collecting user preferences")
        
        # 如果偏好已经存在，验证它们
        if state.get("user_preferences"):
            return {
                "current_step": "preferences_collected",
                "messages": [Message(
                    role="assistant",
                    content="用户偏好已收集完成"
                )]
            }
        
        # 默认偏好
        default_preferences = {
            "min_apy": 8.0,
            "max_risk_score": 0.7,
            "diversification_required": True,
            "esg_compliant": False,
            "liquidity_preference": "medium",
            "investment_horizon": "12_months"
        }
        
        return {
            "user_preferences": default_preferences,
            "current_step": "preferences_collected",
            "messages": [Message(
                role="assistant",
                content=f"已设置投资偏好：最低APY {default_preferences['min_apy']}%，风险承受度：{state.get('risk_tolerance', 'medium')}"
            )]
        }
    
    async def fetch_protocol_data(self, state: PortfolioState) -> Dict[str, Any]:
        """获取协议数据"""
        logger.info(f"Fetching data for protocols: {state.get('target_protocols', [])}")
        
        protocol_data_tool = self.tools.get_tool("rwa_protocol_data")
        protocols = state.get("target_protocols", ["centrifuge", "goldfinch", "maple"])
        
        protocol_yields = {}
        available_assets = []
        
        # 并行获取所有协议数据
        tasks = []
        for protocol in protocols:
            tasks.append(protocol_data_tool.execute(protocol=protocol, timeframe="30d"))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for protocol, result in zip(protocols, results):
            if isinstance(result, Exception):
                logger.error(f"Error fetching {protocol} data: {result}")
                continue
                
            protocol_yields[protocol] = result
            
            # 提取可用资产池
            if "active_pools" in result:
                for pool in result["active_pools"]:
                    available_assets.append({
                        "protocol": protocol,
                        "pool_id": pool["pool_id"],
                        "name": pool["name"],
                        "apy": pool["apy"],
                        "tvl": pool["tvl"],
                        "min_investment": pool["min_investment"],
                        "lock_period": pool["lock_period_days"]
                    })
        
        return {
            "protocol_yields": protocol_yields,
            "available_assets": available_assets,
            "current_step": "data_fetched",
            "messages": [Message(
                role="assistant",
                content=f"已获取 {len(protocol_yields)} 个协议的数据，发现 {len(available_assets)} 个可投资产池"
            )]
        }
    
    async def analyze_yields(self, state: PortfolioState) -> Dict[str, Any]:
        """分析和标准化收益率"""
        logger.info("Analyzing and standardizing yields")
        
        standardization_tool = self.tools.get_tool("yield_standardization")
        available_assets = state.get("available_assets", [])
        
        # 标准化所有资产的收益率
        for asset in available_assets:
            raw_yield_data = {
                "rate": asset["apy"] / 100,  # 转换为小数
                "compound_frequency": "daily",
                "risk_score": 0.5  # 默认风险分数，后续会更新
            }
            
            result = await standardization_tool.execute(
                raw_yield_data=raw_yield_data,
                risk_adjustment=True
            )
            
            # 更新资产信息
            asset["standardized_apy"] = result["standardized_apy"]
            asset["risk_adjusted_apy"] = result["risk_adjusted_apy"]
        
        # 按风险调整后收益率排序
        available_assets.sort(key=lambda x: x["risk_adjusted_apy"], reverse=True)
        
        return {
            "available_assets": available_assets,
            "current_step": "yields_analyzed",
            "messages": [Message(
                role="assistant",
                content=f"收益率分析完成，最高风险调整后APY: {available_assets[0]['risk_adjusted_apy']}%"
            )]
        }
    
    async def calculate_risk_metrics(self, state: PortfolioState) -> Dict[str, Any]:
        """计算风险指标"""
        logger.info("Calculating risk metrics")
        
        risk_scores = {}
        protocol_yields = state.get("protocol_yields", {})
        
        # 基于协议数据计算风险分数
        for protocol, data in protocol_yields.items():
            risk_metrics = data.get("risk_metrics", {})
            
            # 综合风险分数计算
            default_rate = risk_metrics.get("default_rate", 0.02)
            liquidity_score = risk_metrics.get("liquidity_score", 0.7)
            diversification = risk_metrics.get("diversification_score", 0.85)
            
            # 加权风险分数（0-1，越高风险越大）
            risk_score = (
                default_rate * 10 * 0.4 +  # 违约率权重40%
                (1 - liquidity_score) * 0.3 +  # 流动性权重30%
                (1 - diversification) * 0.3  # 分散化权重30%
            )
            
            risk_scores[protocol] = min(risk_score, 1.0)
        
        # 更新资产的风险分数
        for asset in state.get("available_assets", []):
            asset["risk_score"] = risk_scores.get(asset["protocol"], 0.5)
        
        return {
            "risk_scores": risk_scores,
            "current_step": "risks_calculated",
            "messages": [Message(
                role="assistant",
                content=f"风险评估完成，平均风险分数: {sum(risk_scores.values())/len(risk_scores):.2f}"
            )]
        }
    
    async def check_constraints(self, state: PortfolioState) -> Dict[str, Any]:
        """检查投资约束"""
        logger.info("Checking investment constraints")
        
        constraints = state.get("constraints", {})
        available_assets = state.get("available_assets", [])
        investment_amount = state.get("investment_amount", 100000)
        
        warnings = []
        
        # 检查最小投资金额
        min_total_investment = sum(asset["min_investment"] for asset in available_assets[:5])
        if min_total_investment > investment_amount:
            warnings.append(f"投资金额可能不足，建议至少 ${min_total_investment:,.0f}")
        
        # 检查流动性约束
        liquidity_pref = state.get("user_preferences", {}).get("liquidity_preference", "medium")
        if liquidity_pref == "high":
            # 过滤掉锁定期太长的资产
            available_assets = [a for a in available_assets if a["lock_period"] <= 90]
        
        # 检查风险约束
        risk_tolerance = state.get("risk_tolerance", "medium")
        max_risk = {"low": 0.4, "medium": 0.6, "high": 0.8}.get(risk_tolerance, 0.6)
        available_assets = [a for a in available_assets if a.get("risk_score", 0.5) <= max_risk]
        
        if len(available_assets) < 3:
            warnings.append("符合约束条件的资产较少，建议放宽部分约束")
        
        return {
            "available_assets": available_assets,
            "risk_warnings": warnings,
            "current_step": "constraints_checked"
        }
    
    def should_proceed_with_optimization(self, state: PortfolioState) -> str:
        """决定是否继续优化"""
        if state.get("error"):
            return "error"
        
        available_assets = state.get("available_assets", [])
        if len(available_assets) < 2:
            return "adjust"  # 需要调整参数
        
        return "optimize"
    
    async def optimize_allocation(self, state: PortfolioState) -> Dict[str, Any]:
        """优化资产配置"""
        logger.info("Optimizing portfolio allocation")
        
        available_assets = state.get("available_assets", [])
        investment_amount = state.get("investment_amount", 100000)
        risk_tolerance = state.get("risk_tolerance", "medium")
        
        # 简化的优化算法
        # 实际应用中应使用更复杂的优化算法（如马科维茨模型）
        
        # 根据风险承受度设置配置策略
        if risk_tolerance == "low":
            # 保守策略：更多配置在低风险资产
            max_assets = 5
            risk_weight = 0.7
            return_weight = 0.3
        elif risk_tolerance == "high":
            # 激进策略：追求高收益
            max_assets = 8
            risk_weight = 0.3
            return_weight = 0.7
        else:
            # 平衡策略
            max_assets = 6
            risk_weight = 0.5
            return_weight = 0.5
        
        # 计算综合得分
        for asset in available_assets:
            risk_score = asset.get("risk_score", 0.5)
            return_score = asset["risk_adjusted_apy"] / 100
            asset["optimization_score"] = (
                return_weight * return_score - 
                risk_weight * risk_score
            )
        
        # 选择得分最高的资产
        selected_assets = sorted(
            available_assets,
            key=lambda x: x["optimization_score"],
            reverse=True
        )[:max_assets]
        
        # 分配权重（简化版本，可以使用更复杂的算法）
        total_score = sum(a["optimization_score"] for a in selected_assets)
        
        portfolio = {}
        total_allocated = 0
        
        for i, asset in enumerate(selected_assets):
            if i == len(selected_assets) - 1:
                # 最后一个资产获得剩余金额
                allocation = investment_amount - total_allocated
            else:
                # 根据得分比例分配
                weight = asset["optimization_score"] / total_score
                allocation = int(investment_amount * weight)
                
                # 确保满足最小投资要求
                allocation = max(allocation, asset["min_investment"])
            
            total_allocated += allocation
            
            portfolio[asset["pool_id"]] = {
                "protocol": asset["protocol"],
                "name": asset["name"],
                "allocation": allocation,
                "weight": allocation / investment_amount,
                "expected_apy": asset["risk_adjusted_apy"],
                "lock_period": asset["lock_period"]
            }
        
        # 计算组合指标
        portfolio_apy = sum(
            p["weight"] * p["expected_apy"] 
            for p in portfolio.values()
        )
        
        portfolio_risk = sum(
            p["weight"] * available_assets[i].get("risk_score", 0.5)
            for i, p in enumerate(portfolio.values())
        )
        
        risk_free_rate = 4.5
        sharpe_ratio = (portfolio_apy - risk_free_rate) / (portfolio_risk * 15) if portfolio_risk > 0 else 0
        
        return {
            "optimized_portfolio": portfolio,
            "expected_returns": portfolio_apy,
            "portfolio_risk": portfolio_risk,
            "sharpe_ratio": sharpe_ratio,
            "current_step": "allocation_optimized",
            "messages": [Message(
                role="assistant",
                content=f"优化完成：预期年化收益 {portfolio_apy:.1f}%，夏普比率 {sharpe_ratio:.2f}"
            )]
        }
    
    async def forecast_performance(self, state: PortfolioState) -> Dict[str, Any]:
        """预测投资组合表现"""
        logger.info("Forecasting portfolio performance")
        
        portfolio = state.get("optimized_portfolio", {})
        investment_amount = state.get("investment_amount", 100000)
        
        # 生成不同时间段的预测
        forecasts = {}
        time_horizons = [30, 90, 180, 365]  # 天数
        
        for days in time_horizons:
            # 简化的预测模型
            annual_return = state.get("expected_returns", 10) / 100
            period_return = annual_return * (days / 365)
            
            # 添加一些波动性
            best_case = period_return * 1.2
            worst_case = period_return * 0.8
            
            forecasts[f"{days}d"] = {
                "expected_value": investment_amount * (1 + period_return),
                "best_case": investment_amount * (1 + best_case),
                "worst_case": investment_amount * (1 + worst_case),
                "expected_return": period_return * 100
            }
        
        # 生成再平衡计划
        rebalancing_schedule = [
            {
                "date": "30天后",
                "action": "检查各资产表现，微调配置",
                "threshold": "任何资产偏离目标权重超过5%"
            },
            {
                "date": "90天后",
                "action": "全面审查和再平衡",
                "threshold": "根据市场条件调整策略"
            },
            {
                "date": "180天后",
                "action": "评估是否需要调整风险等级",
                "threshold": "如果整体收益偏离预期超过10%"
            }
        ]
        
        return {
            "yield_forecast": forecasts,
            "rebalancing_schedule": rebalancing_schedule,
            "current_step": "performance_forecasted"
        }
    
    async def generate_recommendations(self, state: PortfolioState) -> Dict[str, Any]:
        """生成投资建议"""
        logger.info("Generating recommendations")
        
        recommendations = []
        
        # 基于组合特征生成建议
        portfolio_risk = state.get("portfolio_risk", 0.5)
        expected_returns = state.get("expected_returns", 10)
        sharpe_ratio = state.get("sharpe_ratio", 1.0)
        
        # 风险相关建议
        if portfolio_risk > 0.6:
            recommendations.append("考虑增加稳定收益类资产以降低整体风险")
        elif portfolio_risk < 0.3:
            recommendations.append("当前组合较为保守，可适度增加高收益资产配置")
        
        # 收益相关建议
        if expected_returns < 8:
            recommendations.append("当前预期收益偏低，建议重新评估资产选择标准")
        elif expected_returns > 15:
            recommendations.append("预期收益较高，请确保充分了解相关风险")
        
        # 夏普比率相关建议
        if sharpe_ratio < 0.5:
            recommendations.append("风险调整后收益偏低，建议优化资产配置")
        elif sharpe_ratio > 1.5:
            recommendations.append("当前组合效率较高，建议保持现有策略")
        
        # 通用建议
        recommendations.extend([
            "定期监控各协议的安全审计报告和治理更新",
            "保持5-10%的现金储备以应对突发流动性需求",
            "关注宏观经济环境变化对RWA市场的影响",
            "考虑使用DeFi保险协议对冲智能合约风险"
        ])
        
        # 添加风险警告
        risk_warnings = state.get("risk_warnings", [])
        risk_warnings.extend([
            "RWA代币可能面临监管风险",
            "智能合约漏洞可能导致资金损失",
            "部分资产可能存在流动性不足的问题"
        ])
        
        return {
            "recommendations": recommendations,
            "risk_warnings": risk_warnings,
            "current_step": "recommendations_generated"
        }
    
    async def finalize_portfolio(self, state: PortfolioState) -> Dict[str, Any]:
        """完成投资组合优化"""
        logger.info("Finalizing portfolio optimization")
        
        # 生成最终报告
        final_message = self._generate_final_report(state)
        
        return {
            "completed": True,
            "current_step": "completed",
            "messages": [Message(
                role="assistant",
                content=final_message
            )]
        }
    
    def _generate_final_report(self, state: PortfolioState) -> str:
        """生成最终报告"""
        portfolio = state.get("optimized_portfolio", {})
        investment_amount = state.get("investment_amount", 100000)
        expected_returns = state.get("expected_returns", 10)
        portfolio_risk = state.get("portfolio_risk", 0.5)
        sharpe_ratio = state.get("sharpe_ratio", 1.0)
        
        report = f"""
# RWA投资组合优化报告

## 投资概览
- **投资金额**: ${investment_amount:,.0f}
- **风险承受度**: {state.get('risk_tolerance', 'medium')}
- **预期年化收益**: {expected_returns:.1f}%
- **组合风险评分**: {portfolio_risk:.2f}
- **夏普比率**: {sharpe_ratio:.2f}

## 资产配置
"""
        
        for pool_id, details in portfolio.items():
            report += f"""
### {details['name']}
- **协议**: {details['protocol']}
- **配置金额**: ${details['allocation']:,.0f} ({details['weight']*100:.1f}%)
- **预期APY**: {details['expected_apy']:.1f}%
- **锁定期**: {details['lock_period']}天
"""
        
        report += f"""
## 风险提示
"""
        for warning in state.get("risk_warnings", []):
            report += f"- {warning}\n"
        
        report += f"""
## 投资建议
"""
        for rec in state.get("recommendations", [])[:5]:
            report += f"- {rec}\n"
        
        report += f"""
## 再平衡计划
"""
        for schedule in state.get("rebalancing_schedule", []):
            report += f"- **{schedule['date']}**: {schedule['action']}\n"
        
        report += f"""
---
*报告生成时间: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC*
"""
        
        return report