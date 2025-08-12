#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minimal RWA Agent Test
A basic test without external dependencies
"""

import asyncio
import os
import sys

# Set environment variables from environment (fallback to empty if not set)
os.environ['ANTHROPIC_API_KEY'] = os.getenv('ANTHROPIC_API_KEY', '')
os.environ['ANTHROPIC_BASE_URL'] = os.getenv('ANTHROPIC_BASE_URL', 'https://openrouter.ai/api/v1')
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY', '')
os.environ['OPENAI_BASE_URL'] = 'https://openrouter.ai/api/v1'

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class MockRWAAgent:
    """Mock RWA Agent for testing purposes"""
    
    def __init__(self):
        self.name = "rwa_yield_agent"
        self.protocols = ["centrifuge", "goldfinch", "maple", "credix"]
        
    async def analyze_protocol_yields(self, protocol: str, timeframe: str = "30d"):
        """Mock protocol analysis"""
        mock_data = {
            "centrifuge": {
                "current_apy": 9.5,
                "risk_score": 0.4,
                "asset_type": "real_estate_invoices",
                "tvl": 45000000
            },
            "goldfinch": {
                "current_apy": 12.3,
                "risk_score": 0.6,
                "asset_type": "private_credit",
                "tvl": 78000000
            },
            "maple": {
                "current_apy": 8.7,
                "risk_score": 0.3,
                "asset_type": "institutional_lending",
                "tvl": 120000000
            }
        }
        
        data = mock_data.get(protocol, {"error": "Protocol not found"})
        
        return f"""
RWA Protocol Analysis - {protocol.upper()}
=====================================
Current APY: {data.get('current_apy', 'N/A')}%
Risk Score: {data.get('risk_score', 'N/A')}/1.0
Asset Type: {data.get('asset_type', 'N/A')}
Total Value Locked: ${data.get('tvl', 0):,}
Timeframe: {timeframe}

Analysis Summary:
- Protocol shows {'stable' if data.get('risk_score', 0) < 0.5 else 'moderate'} risk profile
- APY is {'competitive' if data.get('current_apy', 0) > 8 else 'conservative'} in current market
- Suitable for {'conservative' if data.get('risk_score', 0) < 0.4 else 'balanced'} investors
        """
    
    async def compare_yields(self, protocols: list, asset_type: str = None):
        """Mock yield comparison"""
        comparison_data = []
        
        for protocol in protocols:
            result = await self.analyze_protocol_yields(protocol)
            comparison_data.append(result)
        
        return f"""
RWA Yield Comparison Report
==========================
Asset Type Filter: {asset_type or 'All Types'}
Protocols Analyzed: {', '.join(protocols)}

{chr(10).join(comparison_data)}

Recommendation:
- For conservative investors: Focus on Maple Finance (lower risk)
- For balanced portfolios: Mix of Centrifuge and Maple
- For higher yields: Consider Goldfinch (higher risk/reward)

Optimal allocation for medium risk tolerance:
- Maple Finance: 40% ($40,000)
- Centrifuge: 35% ($35,000) 
- Goldfinch: 25% ($25,000)
        """
    
    async def optimize_portfolio(self, investment_amount: float, risk_tolerance: str):
        """Mock portfolio optimization"""
        
        allocations = {
            "low": {"maple": 0.6, "centrifuge": 0.4, "goldfinch": 0.0},
            "medium": {"maple": 0.4, "centrifuge": 0.35, "goldfinch": 0.25},
            "high": {"maple": 0.2, "centrifuge": 0.3, "goldfinch": 0.5}
        }
        
        allocation = allocations.get(risk_tolerance, allocations["medium"])
        
        portfolio_details = []
        total_expected_apy = 0
        
        protocol_apys = {"maple": 8.7, "centrifuge": 9.5, "goldfinch": 12.3}
        
        for protocol, weight in allocation.items():
            if weight > 0:
                amount = investment_amount * weight
                apy = protocol_apys[protocol]
                total_expected_apy += apy * weight
                portfolio_details.append(f"- {protocol.title()}: ${amount:,.0f} ({weight*100:.0f}%) - {apy}% APY")
        
        return f"""
RWA Portfolio Optimization
=========================
Investment Amount: ${investment_amount:,.0f}
Risk Tolerance: {risk_tolerance.title()}

Recommended Allocation:
{chr(10).join(portfolio_details)}

Portfolio Metrics:
- Expected Weighted APY: {total_expected_apy:.1f}%
- Expected Annual Return: ${investment_amount * total_expected_apy / 100:,.0f}
- Risk Score: {0.3 if risk_tolerance == 'low' else 0.5 if risk_tolerance == 'medium' else 0.7}/1.0

Next Steps:
1. Review protocol documentation and risks
2. Consider starting with smaller amounts for testing
3. Monitor performance and rebalance quarterly
        """

async def test_mock_rwa_agent():
    """Test the mock RWA agent"""
    print("=== Mock RWA Agent Test ===\n")
    
    # Create mock agent
    agent = MockRWAAgent()
    print("✓ Mock RWA Agent created")
    
    # Test 1: Analyze single protocol
    print("\n1. Testing protocol analysis...")
    result = await agent.analyze_protocol_yields("centrifuge", "30d")
    print(result)
    
    # Test 2: Compare multiple protocols
    print("\n2. Testing yield comparison...")
    result = await agent.compare_yields(
        protocols=["centrifuge", "goldfinch", "maple"],
        asset_type="private_credit"
    )
    print(result)
    
    # Test 3: Portfolio optimization
    print("\n3. Testing portfolio optimization...")
    result = await agent.optimize_portfolio(100000, "medium")
    print(result)
    
    print("\n=== Mock RWA Agent tests completed! ===")

async def test_real_agent_if_available():
    """Try to test the real RWA agent if dependencies are available"""
    print("\n=== Attempting Real RWA Agent Test ===\n")
    
    try:
        # Try to import the real agent
        from spoon_ai.agents.rwa_yield_agent import RWAYieldAgent
        from spoon_ai.chat import ChatBot
        from spoon_ai.tools import ToolManager
        
        print("✓ Real RWA agent imports successful")
        
        # Create real agent
        chatbot = ChatBot(
            model_name="anthropic/claude-3.5-sonnet",
            llm_provider="openai",
            base_url="https://openrouter.ai/api/v1"
        )
        
        agent = RWAYieldAgent(
            llm=chatbot,
            available_tools=ToolManager([])
        )
        
        print("✓ Real RWA agent created")
        
        # Test basic functionality
        print("\nTesting real agent analysis...")
        result = await agent.analyze_protocol_yields("centrifuge")
        print(f"Real agent result preview: {str(result)[:300]}...")
        
        print("\n✓ Real RWA agent test completed!")
        
    except ImportError as e:
        print(f"❌ Could not import real agent: {e}")
        print("This is expected if dependencies are not installed.")
        
    except Exception as e:
        print(f"❌ Error with real agent: {e}")

async def main():
    """Main test function"""
    print("🚀 Starting RWA Agent Testing...\n")
    
    # Always test the mock agent first
    await test_mock_rwa_agent()
    
    # Try to test real agent if available
    await test_real_agent_if_available()
    
    print("\n🎉 RWA Agent testing completed!")
    print("\nNext steps:")
    print("1. Install project dependencies: pip install -r requirements.txt")
    print("2. Configure API keys in .env file")
    print("3. Run the full test suite: python3 test_rwa_cli.py")

if __name__ == "__main__":
    asyncio.run(main())