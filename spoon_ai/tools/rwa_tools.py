"""
RWA Tools - 用于收集和分析RWA协议数据的工具集
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import aiohttp
import asyncio
import json
from decimal import Decimal
from spoon_ai.tools.base import BaseTool
import os
import logging

logger = logging.getLogger(__name__)

class RWAProtocolDataTool(BaseTool):
    """获取各种RWA协议的收益数据"""
    
    name: str = "rwa_protocol_data"
    description: str = "获取RWA协议的收益数据、资产池信息和历史表现"
    parameters: dict = {
        "type": "object",
        "properties": {
            "protocol": {
                "type": "string",
                "description": "RWA协议名称",
                "enum": ["centrifuge", "goldfinch", "maple", "credix", "clearpool", "truefi"]
            },
            "asset_type": {
                "type": "string",
                "description": "资产类型（可选）",
                "enum": ["bonds", "real_estate", "carbon_credits", "invoices", "private_credit"]
            },
            "timeframe": {
                "type": "string",
                "description": "时间范围",
                "enum": ["24h", "7d", "30d", "90d", "1y"],
                "default": "30d"
            }
        },
        "required": ["protocol"]
    }
    
    def __init__(self):
        super().__init__()
        self.protocol_endpoints = {
            "centrifuge": os.getenv("CENTRIFUGE_API_URL", "https://api.centrifuge.io/v1"),
            "goldfinch": os.getenv("GOLDFINCH_SUBGRAPH_URL"),
            "maple": os.getenv("MAPLE_API_URL", "https://api.maple.finance/v1"),
            "credix": os.getenv("CREDIX_API_URL", "https://api.credix.finance/v1"),
            "clearpool": "https://api.clearpool.finance/v1",
            "truefi": "https://api.truefi.io/v1"
        }
        
        self.api_keys = {
            "centrifuge": os.getenv("CENTRIFUGE_API_KEY"),
            "goldfinch": os.getenv("GOLDFINCH_API_KEY"),
            "maple": os.getenv("MAPLE_API_KEY"),
            "credix": os.getenv("CREDIX_API_KEY")
        }
    
    async def execute(self, protocol: str, asset_type: Optional[str] = None, timeframe: str = "30d") -> Dict[str, Any]:
        """执行数据获取"""
        try:
            if protocol == "centrifuge":
                return await self._fetch_centrifuge_data(asset_type, timeframe)
            elif protocol == "goldfinch":
                return await self._fetch_goldfinch_data(asset_type, timeframe)
            elif protocol == "maple":
                return await self._fetch_maple_data(asset_type, timeframe)
            elif protocol == "credix":
                return await self._fetch_credix_data(asset_type, timeframe)
            else:
                # 返回模拟数据用于开发
                return self._get_mock_data(protocol, asset_type, timeframe)
                
        except Exception as e:
            logger.error(f"Error fetching data for {protocol}: {str(e)}")
            return {
                "error": str(e),
                "protocol": protocol,
                "fallback_data": self._get_mock_data(protocol, asset_type, timeframe)
            }
    
    async def _fetch_centrifuge_data(self, asset_type: Optional[str], timeframe: str) -> Dict[str, Any]:
        """获取Centrifuge协议数据"""
        endpoint = self.protocol_endpoints["centrifuge"]
        headers = {"Authorization": f"Bearer {self.api_keys['centrifuge']}"} if self.api_keys["centrifuge"] else {}
        
        async with aiohttp.ClientSession() as session:
            # 获取池子列表
            pools_url = f"{endpoint}/pools"
            async with session.get(pools_url, headers=headers) as response:
                if response.status == 200:
                    pools_data = await response.json()
                else:
                    return self._get_mock_data("centrifuge", asset_type, timeframe)
        
        # 实际实现时需要解析真实API响应
        return self._process_centrifuge_response(pools_data, asset_type, timeframe)
    
    async def _fetch_goldfinch_data(self, asset_type: Optional[str], timeframe: str) -> Dict[str, Any]:
        """获取Goldfinch协议数据（通过TheGraph）"""
        if not self.protocol_endpoints["goldfinch"]:
            return self._get_mock_data("goldfinch", asset_type, timeframe)
            
        query = """
        query GetPools($first: Int!, $orderBy: String!) {
            tranches(first: $first, orderBy: $orderBy, orderDirection: desc) {
                id
                principalDeposited
                principalSharePrice
                interestSharePrice
                estimatedTotalAssets
            }
            poolStatuses {
                pool {
                    id
                    totalDeposited
                    estimatedAPY
                    termInSeconds
                }
            }
        }
        """
        
        variables = {
            "first": 20,
            "orderBy": "principalDeposited"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.protocol_endpoints["goldfinch"],
                json={"query": query, "variables": variables}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._process_goldfinch_response(data, asset_type, timeframe)
                else:
                    return self._get_mock_data("goldfinch", asset_type, timeframe)
    
    def _get_mock_data(self, protocol: str, asset_type: Optional[str], timeframe: str) -> Dict[str, Any]:
        """获取模拟数据用于开发和测试"""
        base_apy = {
            "centrifuge": 8.5,
            "goldfinch": 10.2,
            "maple": 9.8,
            "credix": 11.5,
            "clearpool": 9.2,
            "truefi": 8.8
        }
        
        # 根据资产类型调整收益率
        asset_multipliers = {
            "bonds": 0.9,
            "real_estate": 1.1,
            "carbon_credits": 0.8,
            "invoices": 1.2,
            "private_credit": 1.0
        }
        
        apy = base_apy.get(protocol, 9.0)
        if asset_type:
            apy *= asset_multipliers.get(asset_type, 1.0)
        
        return {
            "protocol": protocol,
            "asset_type": asset_type or "mixed",
            "timeframe": timeframe,
            "current_apy": round(apy, 2),
            "historical_apy": self._generate_historical_apy(apy, timeframe),
            "total_value_locked": self._generate_tvl(protocol),
            "active_pools": self._generate_pool_data(protocol, asset_type),
            "risk_metrics": {
                "default_rate": round(0.02 + (apy - 8) * 0.01, 4),
                "liquidity_score": round(0.7 + (10 - apy) * 0.03, 2),
                "diversification_score": 0.85
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _generate_historical_apy(self, current_apy: float, timeframe: str) -> List[Dict]:
        """生成历史APY数据"""
        days = {
            "24h": 1,
            "7d": 7,
            "30d": 30,
            "90d": 90,
            "1y": 365
        }.get(timeframe, 30)
        
        historical = []
        for i in range(min(days, 30)):  # 最多返回30个数据点
            date = (datetime.utcnow() - timedelta(days=i)).isoformat()
            # 添加一些随机波动
            variation = (i % 5 - 2) * 0.1
            apy = round(current_apy + variation, 2)
            historical.append({
                "date": date,
                "apy": apy
            })
        
        return historical
    
    def _generate_tvl(self, protocol: str) -> float:
        """生成TVL数据"""
        base_tvl = {
            "centrifuge": 250000000,
            "goldfinch": 180000000,
            "maple": 320000000,
            "credix": 150000000,
            "clearpool": 120000000,
            "truefi": 200000000
        }
        return base_tvl.get(protocol, 100000000)
    
    def _generate_pool_data(self, protocol: str, asset_type: Optional[str]) -> List[Dict]:
        """生成池子数据"""
        pools = []
        pool_count = 3 if asset_type else 5
        
        for i in range(pool_count):
            pools.append({
                "pool_id": f"{protocol}_pool_{i+1}",
                "name": f"{protocol.capitalize()} {asset_type or 'Diversified'} Pool {i+1}",
                "apy": round(8 + i * 0.5, 2),
                "tvl": round(10000000 + i * 5000000, 2),
                "available_liquidity": round(5000000 + i * 2000000, 2),
                "min_investment": 1000,
                "lock_period_days": 30 * (i + 1)
            })
        
        return pools
    
    def _process_centrifuge_response(self, data: Dict, asset_type: Optional[str], timeframe: str) -> Dict[str, Any]:
        """处理Centrifuge API响应"""
        # 实际实现需要根据真实API响应格式
        return self._get_mock_data("centrifuge", asset_type, timeframe)
    
    def _process_goldfinch_response(self, data: Dict, asset_type: Optional[str], timeframe: str) -> Dict[str, Any]:
        """处理Goldfinch GraphQL响应"""
        # 实际实现需要根据真实API响应格式
        return self._get_mock_data("goldfinch", asset_type, timeframe)


class YieldStandardizationTool(BaseTool):
    """标准化不同协议的收益率计算"""
    
    name: str = "yield_standardization"
    description: str = "将不同协议的收益率标准化为统一的APY格式，支持风险调整"
    parameters: dict = {
        "type": "object",
        "properties": {
            "raw_yield_data": {
                "type": "object",
                "description": "原始收益数据，包含rate和compound_frequency"
            },
            "calculation_method": {
                "type": "string",
                "description": "计算方法",
                "enum": ["simple", "compound", "continuous"],
                "default": "compound"
            },
            "risk_adjustment": {
                "type": "boolean",
                "description": "是否进行风险调整",
                "default": False
            }
        },
        "required": ["raw_yield_data"]
    }
    
    async def execute(
        self, 
        raw_yield_data: Dict[str, Any], 
        calculation_method: str = "compound",
        risk_adjustment: bool = False
    ) -> Dict[str, Any]:
        """执行收益率标准化"""
        try:
            # 提取原始数据
            rate = float(raw_yield_data.get("rate", 0))
            frequency = raw_yield_data.get("compound_frequency", "daily")
            risk_score = float(raw_yield_data.get("risk_score", 0.5))
            
            # 计算标准化APY
            if calculation_method == "simple":
                apy = rate
            elif calculation_method == "compound":
                apy = self._calculate_compound_apy(rate, frequency)
            else:  # continuous
                apy = self._calculate_continuous_apy(rate)
            
            # 风险调整
            risk_adjusted_apy = apy
            sharpe_ratio = 0
            if risk_adjustment and risk_score > 0:
                risk_free_rate = float(os.getenv("RISK_FREE_RATE", "0.045"))
                risk_adjusted_apy = apy - (risk_score * (apy - risk_free_rate))
                sharpe_ratio = (apy - risk_free_rate) / (risk_score * 0.15)  # 假设15%的标准差
            
            return {
                "original_rate": rate,
                "original_frequency": frequency,
                "standardized_apy": round(apy * 100, 2),  # 转换为百分比
                "risk_adjusted_apy": round(risk_adjusted_apy * 100, 2),
                "risk_score": risk_score,
                "sharpe_ratio": round(sharpe_ratio, 2),
                "calculation_method": calculation_method,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error standardizing yield: {str(e)}")
            return {
                "error": str(e),
                "original_data": raw_yield_data
            }
    
    def _calculate_compound_apy(self, rate: float, frequency: str) -> float:
        """计算复利APY"""
        frequencies = {
            "daily": 365,
            "weekly": 52,
            "monthly": 12,
            "quarterly": 4,
            "semi-annually": 2,
            "annually": 1
        }
        
        n = frequencies.get(frequency.lower(), 365)
        # APY = (1 + r/n)^n - 1
        apy = (1 + rate / n) ** n - 1
        return apy
    
    def _calculate_continuous_apy(self, rate: float) -> float:
        """计算连续复利APY"""
        import math
        # APY = e^r - 1
        apy = math.exp(rate) - 1
        return apy


class RWAPortfolioAnalysisTool(BaseTool):
    """RWA投资组合分析工具"""
    
    name: str = "rwa_portfolio_analysis"
    description: str = "分析RWA投资组合的风险收益特征，提供优化建议"
    parameters: dict = {
        "type": "object",
        "properties": {
            "portfolio": {
                "type": "array",
                "description": "投资组合，包含协议、金额和权重",
                "items": {
                    "type": "object",
                    "properties": {
                        "protocol": {"type": "string"},
                        "amount": {"type": "number"},
                        "weight": {"type": "number"}
                    }
                }
            },
            "analysis_type": {
                "type": "string",
                "description": "分析类型",
                "enum": ["risk_return", "correlation", "optimization", "stress_test"],
                "default": "risk_return"
            }
        },
        "required": ["portfolio"]
    }
    
    async def execute(
        self,
        portfolio: List[Dict[str, Any]],
        analysis_type: str = "risk_return"
    ) -> Dict[str, Any]:
        """执行投资组合分析"""
        try:
            if analysis_type == "risk_return":
                return await self._analyze_risk_return(portfolio)
            elif analysis_type == "correlation":
                return await self._analyze_correlation(portfolio)
            elif analysis_type == "optimization":
                return await self._optimize_portfolio(portfolio)
            else:  # stress_test
                return await self._stress_test_portfolio(portfolio)
                
        except Exception as e:
            logger.error(f"Error analyzing portfolio: {str(e)}")
            return {
                "error": str(e),
                "portfolio": portfolio
            }
    
    async def _analyze_risk_return(self, portfolio: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析投资组合的风险收益特征"""
        total_value = sum(p["amount"] for p in portfolio)
        weighted_apy = 0
        weighted_risk = 0
        
        # 模拟的协议风险收益数据
        protocol_data = {
            "centrifuge": {"apy": 0.085, "risk": 0.15},
            "goldfinch": {"apy": 0.102, "risk": 0.18},
            "maple": {"apy": 0.098, "risk": 0.16},
            "credix": {"apy": 0.115, "risk": 0.22},
            "clearpool": {"apy": 0.092, "risk": 0.17},
            "truefi": {"apy": 0.088, "risk": 0.14}
        }
        
        portfolio_breakdown = []
        for asset in portfolio:
            protocol = asset["protocol"]
            amount = asset["amount"]
            weight = amount / total_value
            
            data = protocol_data.get(protocol, {"apy": 0.09, "risk": 0.16})
            weighted_apy += data["apy"] * weight
            weighted_risk += data["risk"] * weight
            
            portfolio_breakdown.append({
                "protocol": protocol,
                "amount": amount,
                "weight": round(weight * 100, 2),
                "expected_return": round(data["apy"] * 100, 2),
                "risk_score": round(data["risk"], 2),
                "contribution_to_return": round(data["apy"] * weight * 100, 2)
            })
        
        risk_free_rate = 0.045
        sharpe_ratio = (weighted_apy - risk_free_rate) / weighted_risk if weighted_risk > 0 else 0
        
        return {
            "total_value": total_value,
            "expected_annual_return": round(weighted_apy * 100, 2),
            "portfolio_risk": round(weighted_risk, 3),
            "sharpe_ratio": round(sharpe_ratio, 2),
            "risk_adjusted_return": round((weighted_apy - weighted_risk * 0.5) * 100, 2),
            "portfolio_breakdown": portfolio_breakdown,
            "recommendations": self._generate_recommendations(weighted_apy, weighted_risk),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _generate_recommendations(self, apy: float, risk: float) -> List[str]:
        """生成投资组合建议"""
        recommendations = []
        
        if risk > 0.18:
            recommendations.append("考虑增加低风险协议的配置以降低整体风险")
        if apy < 0.09:
            recommendations.append("当前收益率偏低，可以适度增加高收益协议的配置")
        if risk < 0.14:
            recommendations.append("组合风险较低，如果风险承受能力允许，可以增加高收益资产")
        
        recommendations.append("定期再平衡以维持目标配置比例")
        recommendations.append("关注各协议的流动性状况和锁定期要求")
        
        return recommendations
    
    async def _analyze_correlation(self, portfolio: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析投资组合相关性"""
        # 简化实现，实际需要历史数据计算相关性矩阵
        return {
            "correlation_matrix": "需要历史数据计算",
            "diversification_score": 0.75,
            "concentration_risk": "medium",
            "recommendations": [
                "增加不同类型RWA资产以提高分散化",
                "考虑加入与现有资产相关性较低的协议"
            ]
        }
    
    async def _optimize_portfolio(self, portfolio: List[Dict[str, Any]]) -> Dict[str, Any]:
        """优化投资组合配置"""
        # 简化的优化建议
        return {
            "optimized_weights": {
                "centrifuge": 0.25,
                "goldfinch": 0.20,
                "maple": 0.30,
                "credix": 0.15,
                "clearpool": 0.10
            },
            "expected_improvement": {
                "return_increase": "1.2%",
                "risk_reduction": "8%",
                "sharpe_improvement": "0.15"
            },
            "rebalancing_trades": [
                {"action": "reduce", "protocol": "credix", "amount": 5000},
                {"action": "increase", "protocol": "maple", "amount": 5000}
            ]
        }
    
    async def _stress_test_portfolio(self, portfolio: List[Dict[str, Any]]) -> Dict[str, Any]:
        """对投资组合进行压力测试"""
        scenarios = {
            "market_crash": -0.30,
            "interest_rate_hike": -0.15,
            "liquidity_crisis": -0.25,
            "protocol_hack": -0.40
        }
        
        stress_results = []
        for scenario, impact in scenarios.items():
            portfolio_impact = sum(p["amount"] * impact for p in portfolio)
            stress_results.append({
                "scenario": scenario,
                "impact_percentage": round(impact * 100, 1),
                "portfolio_loss": round(portfolio_impact, 2),
                "recovery_time_estimate": f"{abs(int(impact * 12))} months"
            })
        
        return {
            "stress_test_results": stress_results,
            "var_95": round(sum(p["amount"] for p in portfolio) * 0.15, 2),
            "max_drawdown": round(sum(p["amount"] for p in portfolio) * 0.25, 2),
            "risk_mitigation": [
                "设置止损限制",
                "保持部分现金储备",
                "考虑购买保险产品",
                "分批进入和退出头寸"
            ]
        }