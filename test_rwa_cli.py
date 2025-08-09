#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RWA Agent Test CLI Script
For testing RWA yield analysis and portfolio optimization functionality
"""

import asyncio
import logging
from spoon_ai.agents import RWAYieldAgent, PortfolioOptimizerAgent
from spoon_ai.chat import ChatBot
from spoon_ai.tools import ToolManager
from spoon_ai.tools import (
    RWAProtocolDataTool,
    YieldStandardizationTool,
    RWAPortfolioAnalysisTool
)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_rwa_yield_analysis():
    """Test RWA yield analysis functionality"""
    print("\n=== Testing RWA Yield Analysis ===\n")
    
    # Create tool manager
    tools = ToolManager([
        RWAProtocolDataTool(),
        YieldStandardizationTool(),
        RWAPortfolioAnalysisTool()
    ])
    
    # Create ChatBot instance (using mock mode for testing)
    chatbot = ChatBot(
        model_name="gpt-4",
        llm_provider="openai",
        chat_history=[]
    )
    
    # Create RWA yield analysis agent
    agent = RWAYieldAgent(
        llm=chatbot,
        available_tools=tools
    )
    
    # Test 1: Analyze specific protocol yields
    print("1. Analyzing Centrifuge protocol yields...")
    try:
        result = await agent.analyze_protocol_yields(
            protocol="centrifuge",
            timeframe="30d"
        )
        print(f"Analysis result: {result[:200]}...")  # Show only first 200 characters
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Compare multiple protocol yields
    print("\n2. Comparing multiple protocol yields...")
    try:
        result = await agent.compare_yields(
            protocols=["centrifuge", "goldfinch", "maple"],
            asset_type="private_credit"
        )
        print(f"Comparison result: {result[:200]}...")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Forecast yields
    print("\n3. Forecasting Goldfinch protocol future yields...")
    try:
        result = await agent.forecast_yields(
            protocol="goldfinch",
            asset_type="private_credit",
            forecast_period="90d"
        )
        print(f"Forecast result: {result[:200]}...")
    except Exception as e:
        print(f"Error: {e}")

async def test_portfolio_optimization():
    """Test portfolio optimization functionality"""
    print("\n=== Testing Portfolio Optimization ===\n")
    
    # Create ChatBot instance
    chatbot = ChatBot(
        model_name="gpt-4",
        llm_provider="openai",
        chat_history=[]
    )
    
    # Create portfolio optimizer agent
    agent = PortfolioOptimizerAgent(llm=chatbot)
    await agent.initialize()
    
    # Prepare initial state
    initial_state = {
        "investment_amount": 100000,
        "risk_tolerance": "medium",
        "target_protocols": ["centrifuge", "goldfinch", "maple"],
        "constraints": {},
        "user_preferences": {
            "optimization_goal": "balanced",
            "min_apy": 8.0,
            "max_risk_score": 0.6
        },
        "messages": [],
        "completed": False
    }
    
    print("Running portfolio optimization workflow...")
    try:
        # Run optimization workflow
        result = await agent.run_workflow(initial_state)
        
        # Display results
        print(f"\nOptimization results:")
        print(f"- Expected annual returns: {result.get('expected_returns', 0):.2f}%")
        print(f"- Portfolio risk score: {result.get('portfolio_risk', 0):.2f}")
        print(f"- Sharpe ratio: {result.get('sharpe_ratio', 0):.2f}")
        
        if result.get('optimized_portfolio'):
            print(f"\nRecommended asset allocation:")
            for pool_id, details in result['optimized_portfolio'].items():
                print(f"  - {details['name']}: ${details['allocation']:,.0f} ({details['weight']*100:.1f}%)")
        
        if result.get('recommendations'):
            print(f"\nInvestment recommendations:")
            for rec in result['recommendations'][:3]:
                print(f"  - {rec}")
                
    except Exception as e:
        print(f"Error: {e}")
        logger.error(f"Portfolio optimization error: {e}", exc_info=True)

async def test_rwa_tools():
    """Test RWA tools"""
    print("\n=== Testing RWA Tools ===\n")
    
    # Test protocol data tool
    print("1. Testing RWA protocol data tool...")
    tool = RWAProtocolDataTool()
    try:
        result = await tool.execute(
            protocol="centrifuge",
            asset_type="real_estate",
            timeframe="30d"
        )
        print(f"Centrifuge data:")
        print(f"  - Current APY: {result.get('current_apy', 0)}%")
        print(f"  - TVL: ${result.get('total_value_locked', 0):,.0f}")
        print(f"  - Active pools: {len(result.get('active_pools', []))}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test yield standardization tool
    print("\n2. Testing yield standardization tool...")
    tool = YieldStandardizationTool()
    try:
        result = await tool.execute(
            raw_yield_data={
                "rate": 0.095,
                "compound_frequency": "daily",
                "risk_score": 0.4
            },
            calculation_method="compound",
            risk_adjustment=True
        )
        print(f"Standardization results:")
        print(f"  - Standardized APY: {result.get('standardized_apy', 0)}%")
        print(f"  - Risk-adjusted APY: {result.get('risk_adjusted_apy', 0)}%")
        print(f"  - Sharpe ratio: {result.get('sharpe_ratio', 0)}")
    except Exception as e:
        print(f"Error: {e}")

async def main():
    """Main function"""
    print("RWA functionality testing started...\n")
    
    # Test RWA tools
    await test_rwa_tools()
    
    # Test RWA yield analysis
    await test_rwa_yield_analysis()
    
    # Test portfolio optimization
    await test_portfolio_optimization()
    
    print("\nTesting completed!")

if __name__ == "__main__":
    asyncio.run(main())