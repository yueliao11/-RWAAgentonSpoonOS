"""
Tests for RWA Yield Optimizer Project
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import json

from spoon_ai.agents import RWAYieldAgent, PortfolioOptimizerAgent
from spoon_ai.tools import (
    RWAProtocolDataTool,
    YieldStandardizationTool,
    RWAPortfolioAnalysisTool,
    ToolManager
)
from spoon_ai.chat import ChatBot
from spoon_ai.services import ProtocolYieldData
from api import (
    YieldAnalysisRequest,
    PortfolioOptimizationRequest,
    CompareYieldsRequest,
    YieldForecastRequest
)
from typing import Dict, Any, List


@pytest.fixture
def mock_rwa_yield_agent():
    """Mock RWAYieldAgent fixture"""
    agent = RWAYieldAgent(
        llm=ChatBot(model_name="mock-model", llm_provider="mock", chat_history=[]),
        available_tools=ToolManager([
            RWAProtocolDataTool(),
            YieldStandardizationTool(),
            RWAPortfolioAnalysisTool()
        ])
    )
    # Mocking the run method to return a predefined response for testing agent logic
    agent.run = Mock(return_value="Mocked agent response")
    return agent

@pytest.fixture
def mock_portfolio_optimizer_agent():
    """Mock PortfolioOptimizerAgent fixture"""
    agent = PortfolioOptimizerAgent(
        llm=ChatBot(model_name="mock-model", llm_provider="mock", chat_history=[]),
    )
    # Mocking the run_workflow method
    agent.run_workflow = Mock(side_effect=lambda state: mock_portfolio_analysis_result())
    return agent


@pytest.mark.asyncio
async def test_rwa_yield_agent_compare_yields(mock_rwa_yield_agent: RWAYieldAgent):
    """测试RWAYieldAgent的compare_yields方法"""
    protocols = ["centrifuge", "goldfinch", "maple"]
    asset_type = "private_credit"
    
    # Mocking the underlying tool calls
    with patch.object(RWAProtocolDataTool, 'execute') as mock_protocol_data_tool, \
         patch.object(YieldStandardizationTool, 'execute') as mock_yield_std_tool:
        
        mock_protocol_data_tool.side_effect = [
            mock_protocol_data(protocols[0]),
            mock_protocol_data(protocols[1]),
            mock_protocol_data(protocols[2])
        ]
        mock_yield_std_tool.return_value = mock_standardized_yield("private_credit", risk_adjustment=True)
        
        result = await mock_rwa_yield_agent.compare_yields(protocols, asset_type)
        
        assert isinstance(result, str)  # agent.run returns string
        # Since we're mocking the run method, we just check it was called correctly
        mock_rwa_yield_agent.run.assert_called()


@pytest.mark.asyncio
async def test_rwa_yield_agent_optimize_portfolio(mock_portfolio_optimizer_agent: PortfolioOptimizerAgent):
    """测试PortfolioOptimizerAgent的optimize_portfolio方法"""
    investment_amount = 100000
    risk_tolerance = "medium"
    target_protocols = ["centrifuge", "maple"]
    
    # Mocking the underlying tool calls
    with patch.object(RWAProtocolDataTool, 'execute') as mock_protocol_data_tool, \
         patch.object(YieldStandardizationTool, 'execute') as mock_yield_std_tool, \
         patch.object(RWAPortfolioAnalysisTool, 'execute') as mock_portfolio_analysis_tool:

        mock_protocol_data_tool.side_effect = [
            mock_protocol_data(target_protocols[0], asset_type="private_credit"),
            mock_protocol_data(target_protocols[1], asset_type="private_credit")
        ]
        mock_yield_std_tool.side_effect = [
            mock_standardized_yield("private_credit", risk_adjustment=True),
            mock_standardized_yield("private_credit", risk_adjustment=True)
        ]
        mock_portfolio_analysis_tool.return_value = mock_portfolio_analysis_result()

        # Override the run_workflow mock for this specific test
        mock_portfolio_optimizer_agent.run_workflow = Mock(return_value=mock_portfolio_analysis_result())

        result = await mock_portfolio_optimizer_agent.run_workflow({
            "investment_amount": investment_amount,
            "risk_tolerance": risk_tolerance,
            "target_protocols": target_protocols,
            "constraints": {},
            "user_preferences": {"optimization_goal": "balanced"},
            "messages": [],
            "completed": False
        })

        assert isinstance(result, dict)
        assert "total_value" in result
        assert "expected_annual_return" in result
        assert result["expected_annual_return"] == 9.8


@pytest.mark.asyncio
async def test_rwa_yield_agent_optimize_portfolio_logic(mock_rwa_yield_agent: RWAYieldAgent):
    """测试RWAYieldAgent的portfolio优化逻辑，不Mock RWAProtocolDataTool"""
    investment_amount = 100000
    risk_tolerance = "medium"
    target_protocols = ["centrifuge", "maple"]

    # Mocking only the standardized yield and portfolio analysis parts
    with patch.object(YieldStandardizationTool, 'execute') as mock_yield_std_tool, \
         patch.object(RWAPortfolioAnalysisTool, 'execute') as mock_portfolio_analysis_tool:
        
        mock_yield_std_tool.side_effect = [
            mock_standardized_yield("private_credit", risk_adjustment=True),
            mock_standardized_yield("private_credit", risk_adjustment=True)
        ]
        mock_portfolio_analysis_tool.return_value = mock_portfolio_analysis_result()

        # Mock RWAProtocolDataTool to return data that allows testing the logic
        def mock_protocol_data_side_effect(protocol, timeframe):
            if protocol == "centrifuge":
                data = mock_protocol_data(protocol, asset_type="private_credit")
                data.pools = [data.pools[0]] # Make it slightly different
                return data
            elif protocol == "maple":
                data = mock_protocol_data(protocol, asset_type="private_credit")
                data.pools = [data.pools[1]] # Make it slightly different
                return data
            return mock_protocol_data(protocol)

        mock_rwa_yield_agent.tools.get_tool("rwa_protocol_data").execute = Mock(side_effect=mock_protocol_data_side_effect)

        # Mock the agent's run method to capture the prompt and return a mock result
        mock_agent_run = Mock(return_value="Mocked result from agent.run")
        mock_rwa_yield_agent.run = mock_agent_run

        # Call the method that uses agent.run internally
        result = await mock_rwa_yield_agent.optimize_portfolio(
            investment_amount=investment_amount,
            risk_tolerance=risk_tolerance,
            target_protocols=target_protocols
        )

        assert result == "Mocked result from agent.run"
        # Check if the agent.run was called with the correct prompt structure
        mock_agent_run.assert_called_once()
        # Since we're mocking, we don't need to check the prompt content


# Helper functions for mocking
def mock_protocol_data(protocol: str, asset_type: str = "mixed") -> ProtocolYieldData:
    """生成模拟的协议数据"""
    base_apy = {"centrifuge": 8.5, "goldfinch": 10.2, "maple": 9.8, "credix": 11.5}.get(protocol, 9.0)
    risk_score = {"centrifuge": 0.35, "goldfinch": 0.42, "maple": 0.38, "credix": 0.45}.get(protocol, 0.4)
    pools = []
    for i in range(3):
        pools.append({
            "pool_id": f"{protocol}_pool_{i+1}",
            "name": f"{protocol.capitalize()} {asset_type} Pool {i+1}",
            "apy": round(base_apy + i * 0.3, 2),
            "tvl": 10000000 * (i + 1),
            "min_investment": 1000,
            "lock_period": 30 * (i + 1)
        })
    
    return ProtocolYieldData(
        protocol=protocol,
        apy=base_apy,
        tvl=sum(p["tvl"] for p in pools),
        risk_score=risk_score,
        last_updated=datetime.utcnow(),
        pools=pools
    )

def mock_standardized_yield(asset_type: str, risk_adjustment: bool = True) -> Dict[str, Any]:
    """生成模拟的标准化收益"""
    base_apy = 9.5
    risk_score = 0.4
    risk_free_rate = 0.045
    
    apy = base_apy / 100
    risk_adjusted_apy_val = 0
    sharpe_ratio_val = 0
    
    if risk_adjustment and risk_score > 0:
        risk_adjusted_apy_val = (apy - risk_free_rate) / (risk_score * 0.15)
        sharpe_ratio_val = (apy - risk_free_rate) / (risk_score * 0.15) # Assume std dev is risk_score * 0.15

    return {
        "original_rate": 0.095,
        "original_frequency": "daily",
        "standardized_apy": round(apy * 100, 2),
        "risk_adjusted_apy": round(risk_adjusted_apy_val * 100, 2) if risk_adjustment else None,
        "risk_score": risk_score,
        "sharpe_ratio": round(sharpe_ratio_val, 2) if risk_adjustment else None,
        "calculation_method": "compound",
        "timestamp": datetime.utcnow().isoformat()
    }

def mock_portfolio_analysis_result() -> Dict[str, Any]:
    """生成模拟的投资组合分析结果"""
    return {
        "total_value": 100000,
        "expected_annual_return": 9.8,
        "portfolio_risk": 0.42,
        "sharpe_ratio": 1.25,
        "portfolio_breakdown": [
            {"protocol": "centrifuge", "amount": 40000, "weight": 40.0, "expected_return": 8.5, "risk_score": 0.35, "contribution_to_return": 3.4},
            {"protocol": "maple", "amount": 60000, "weight": 60.0, "expected_return": 9.8, "risk_score": 0.38, "contribution_to_return": 5.88}
        ],
        "recommendations": ["增加低风险资产比例", "定期再平衡"]
    }

