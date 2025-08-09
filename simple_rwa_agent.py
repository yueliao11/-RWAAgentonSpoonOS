#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple RWA Agent Implementation
A working RWA agent with basic functionality
"""

import asyncio
import os
import json
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

class RWAProtocolData(BaseModel):
    """RWA Protocol data model"""
    protocol: str
    current_apy: float
    risk_score: float
    asset_type: str
    tvl: float
    active_pools: int = 0
    min_investment: float = 1000
    lock_period: str = "flexible"

class PortfolioAllocation(BaseModel):
    """Portfolio allocation model"""
    protocol: str
    allocation_amount: float
    allocation_percentage: float
    expected_apy: float
    risk_score: float

class SimpleRWAAgent:
    """Simple RWA Yield Analysis Agent"""
    
    def __init__(self):
        self.name = "enhanced_rwa_agent"
        self.supported_protocols = ["centrifuge", "goldfinch", "maple", "credix", "truefi"]
        
        # Initialize real data connectors with error handling
        try:
            from defillama_integration import DeFiLlamaRWAConnector
            from multi_model_predictor import MultiModelYieldPredictor
            
            self.data_connector = DeFiLlamaRWAConnector()
            self.ai_predictor = MultiModelYieldPredictor()
            self.real_data_available = True
            print("✅ Enhanced RWA Agent initialized with real data connectors")
        except ImportError as e:
            print(f"⚠️  Real data connectors not available: {e}")
            self.data_connector = None
            self.ai_predictor = None
            self.real_data_available = False
        
        # Fallback mock data (in case APIs fail)
        self.fallback_data = {
            "centrifuge": RWAProtocolData(
                protocol="centrifuge",
                current_apy=9.5,
                risk_score=0.4,
                asset_type="Real Estate Invoices",
                tvl=45000000,
                active_pools=12,
                min_investment=1000,
                lock_period="flexible"
            ),
            "goldfinch": RWAProtocolData(
                protocol="goldfinch",
                current_apy=12.3,
                risk_score=0.6,
                asset_type="Private Credit",
                tvl=28000000,
                active_pools=8,
                min_investment=5000,
                lock_period="6-12 months"
            ),
            "maple": RWAProtocolData(
                protocol="maple",
                current_apy=8.7,
                risk_score=0.3,
                asset_type="Institutional Loans",
                tvl=67000000,
                active_pools=15,
                min_investment=10000,
                lock_period="3-6 months"
            ),
            "credix": RWAProtocolData(
                protocol="credix",
                current_apy=11.2,
                risk_score=0.5,
                asset_type="Emerging Market Credit",
                tvl=15000000,
                active_pools=6,
                min_investment=2500,
                lock_period="flexible"
            ),
            "truefi": RWAProtocolData(
                protocol="truefi",
                current_apy=10.1,
                risk_score=0.4,
                asset_type="Uncollateralized Loans",
                tvl=32000000,
                active_pools=10,
                min_investment=1000,
                lock_period="flexible"
            )
        }
    
    async def get_protocol_data(self, protocol: str) -> Optional[RWAProtocolData]:
        """Get REAL data for a specific protocol from DeFiLlama"""
        if self.real_data_available and self.data_connector:
            try:
                # Try to get real data first
                real_data = await self.data_connector.get_protocol_tvl(protocol)
                yield_data = await self.data_connector.get_yield_data(protocol)
                
                if (isinstance(real_data, dict) and "error" not in real_data and 
                    isinstance(yield_data, dict) and "error" not in yield_data):
                    
                    tvl = real_data.get("tvl", 0)
                    if not isinstance(tvl, (int, float)):
                        tvl = 0
                    
                    return RWAProtocolData(
                        protocol=protocol,
                        current_apy=yield_data["estimated_apy"],
                        risk_score=self._estimate_risk_from_tvl_change(real_data.get("change_7d", 0)),
                        asset_type=self._get_asset_type(protocol),
                        tvl=float(tvl),
                        active_pools=self._estimate_pools_from_tvl(float(tvl)),
                        min_investment=self._get_min_investment(protocol),
                        lock_period=self._get_lock_period(protocol)
                    )
            except Exception as e:
                print(f"⚠️  Using fallback data for {protocol}: {e}")
        
        # Fallback to mock data
        return self.fallback_data.get(protocol.lower())
    
    def _estimate_risk_from_tvl_change(self, change_7d: float) -> float:
        """Estimate risk score from TVL volatility"""
        abs_change = abs(change_7d)
        if abs_change < 5:
            return 0.3  # Low risk
        elif abs_change < 15:
            return 0.5  # Medium risk
        else:
            return 0.7  # High risk
    
    def _get_asset_type(self, protocol: str) -> str:
        """Get asset type for protocol"""
        asset_types = {
            "centrifuge": "Real Estate Invoices",
            "goldfinch": "Private Credit",
            "maple": "Institutional Loans",
            "credix": "Emerging Market Credit",
            "truefi": "Uncollateralized Loans"
        }
        return asset_types.get(protocol.lower(), "Mixed Assets")
    
    def _estimate_pools_from_tvl(self, tvl: float) -> int:
        """Estimate number of active pools from TVL"""
        if tvl > 50000000:
            return 15
        elif tvl > 25000000:
            return 10
        elif tvl > 10000000:
            return 6
        else:
            return 3
    
    def _get_min_investment(self, protocol: str) -> float:
        """Get minimum investment for protocol"""
        min_investments = {
            "centrifuge": 1000,
            "goldfinch": 5000,
            "maple": 10000,
            "credix": 2500,
            "truefi": 1000
        }
        return min_investments.get(protocol.lower(), 1000)
    
    def _get_lock_period(self, protocol: str) -> str:
        """Get typical lock period for protocol"""
        lock_periods = {
            "centrifuge": "flexible",
            "goldfinch": "6-12 months",
            "maple": "3-6 months",
            "credix": "flexible",
            "truefi": "flexible"
        }
        return lock_periods.get(protocol.lower(), "flexible")
    
    async def analyze_protocol_yields(self, protocol: str, timeframe: str = "30d") -> str:
        """Analyze a specific protocol's yield potential"""
        protocol_data = await self.get_protocol_data(protocol)
        
        if not protocol_data:
            return f"❌ Protocol {protocol} not found"
        
        # Calculate risk-adjusted APY
        risk_adjusted_apy = protocol_data.current_apy / (1 + protocol_data.risk_score)
        
        # Determine risk level
        if protocol_data.risk_score < 0.4:
            risk_level = "Low"
        elif protocol_data.risk_score < 0.6:
            risk_level = "Medium"
        else:
            risk_level = "High"
        
        # Generate analysis report
        report = f"""
RWA Protocol Analysis: {protocol.upper()}
{'=' * 50}

Key Metrics:
- Current APY: {protocol_data.current_apy}%
- Risk Score: {protocol_data.risk_score}/1.0 ({risk_level})
- Risk-Adjusted APY: {risk_adjusted_apy:.1f}%
- Asset Type: {protocol_data.asset_type}
- Total Value Locked: ${protocol_data.tvl:,.0f}
- Active Pools: {protocol_data.active_pools}
- Minimum Investment: ${protocol_data.min_investment:,.0f}
- Lock Period: {protocol_data.lock_period}

Analysis Summary:
- Risk Profile: {risk_level} risk investment
- Yield Competitiveness: {"Competitive" if protocol_data.current_apy > 8 else "Below Average"}
- Liquidity: {"High" if protocol_data.lock_period == "flexible" else "Medium"}
- Suitable for: {"Conservative" if protocol_data.risk_score < 0.4 else "Balanced" if protocol_data.risk_score < 0.6 else "Aggressive"} investors

Risk Considerations:
- Standard DeFi risks apply

Investment Recommendation:
{"Good for balanced portfolios. Consider 15-30% allocation." if risk_level == "Medium" else "Conservative choice for stable returns." if risk_level == "Low" else "High-risk, high-reward option. Limit to 5-10% allocation."}
        """
        
        return report.strip()
    
    async def compare_protocols(self, protocols: List[str] = None) -> str:
        """Compare multiple RWA protocols"""
        if not protocols:
            protocols = self.supported_protocols
        
        comparison_data = []
        for protocol in protocols:
            data = await self.get_protocol_data(protocol)
            if data:
                comparison_data.append(data)
        
        if not comparison_data:
            return "❌ No protocol data available"
        
        # Sort by risk-adjusted APY
        comparison_data.sort(key=lambda x: x.current_apy / (1 + x.risk_score), reverse=True)
        
        report = """
RWA Protocol Comparison
{'=' * 50}

Ranked by Risk-Adjusted APY:
"""
        
        for i, data in enumerate(comparison_data, 1):
            risk_adjusted = data.current_apy / (1 + data.risk_score)
            report += f"""
{i}. {data.protocol.upper()}
   - APY: {data.current_apy}% | Risk-Adj: {risk_adjusted:.1f}%
   - TVL: ${data.tvl:,.0f} | Risk: {data.risk_score:.1f}
   - Asset: {data.asset_type}
"""
        
        return report.strip()
    
    async def optimize_portfolio(self, investment_amount: float, risk_tolerance: str = "medium") -> str:
        """Optimize portfolio allocation across RWA protocols"""
        
        # Get all protocol data
        all_protocols = []
        for protocol in self.supported_protocols:
            data = await self.get_protocol_data(protocol)
            if data:
                all_protocols.append(data)
        
        if not all_protocols:
            return "❌ No protocol data available for optimization"
        
        # Filter by risk tolerance
        if risk_tolerance.lower() == "low":
            filtered_protocols = [p for p in all_protocols if p.risk_score < 0.4]
        elif risk_tolerance.lower() == "high":
            filtered_protocols = [p for p in all_protocols if p.risk_score > 0.5]
        else:  # medium
            filtered_protocols = all_protocols
        
        if not filtered_protocols:
            return f"❌ No protocols match {risk_tolerance} risk tolerance"
        
        # Simple optimization: weight by risk-adjusted APY
        total_weight = sum(p.current_apy / (1 + p.risk_score) for p in filtered_protocols)
        
        allocations = []
        for protocol in filtered_protocols:
            weight = (protocol.current_apy / (1 + protocol.risk_score)) / total_weight
            allocation_amount = investment_amount * weight
            
            allocations.append(PortfolioAllocation(
                protocol=protocol.protocol,
                allocation_amount=allocation_amount,
                allocation_percentage=weight * 100,
                expected_apy=protocol.current_apy,
                risk_score=protocol.risk_score
            ))
        
        # Calculate portfolio metrics
        weighted_apy = sum(a.expected_apy * a.allocation_percentage / 100 for a in allocations)
        weighted_risk = sum(a.risk_score * a.allocation_percentage / 100 for a in allocations)
        expected_return = investment_amount * weighted_apy / 100
        
        # Generate report
        report = f"""
RWA Portfolio Optimization
=========================
Investment Amount: ${investment_amount:,.0f}
Risk Tolerance: {risk_tolerance.title()}

Recommended Allocation:
"""
        
        for allocation in sorted(allocations, key=lambda x: x.allocation_percentage, reverse=True):
            report += f"- {allocation.protocol.title()}: ${allocation.allocation_amount:,.0f} ({allocation.allocation_percentage:.0f}%) - {allocation.expected_apy}% APY\n"
        
        report += f"""
Portfolio Metrics:
- Expected Weighted APY: {weighted_apy:.1f}%
- Expected Annual Return: ${expected_return:,.0f}
- Portfolio Risk Score: {weighted_risk:.2f}/1.0
- Sharpe Ratio: {weighted_apy / (weighted_risk * 10):.2f}
- Diversification Score: {min(len(allocations) * 2, 10)}/10

Risk Assessment:
{"Low risk portfolio with stable returns" if weighted_risk < 0.4 else "Moderate risk portfolio with balanced risk/reward profile" if weighted_risk < 0.6 else "High risk portfolio with potential for higher returns"}

Next Steps:
1. Review individual protocol documentation and terms
2. Start with smaller test amounts if new to RWA investing
3. Monitor performance and rebalance quarterly
4. Consider dollar-cost averaging for large investments
5. Keep 10-20% in liquid assets for opportunities

Additional Recommendations:
{"Portfolio allocation looks well-balanced" if len(allocations) >= 3 else "Consider diversifying across more protocols for better risk distribution"}
        """
        
        return report.strip()
    
    async def get_ai_yield_prediction(self, protocol: str, timeframe: str = "90d") -> str:
        """Get AI-powered yield prediction"""
        if not self.real_data_available or not self.ai_predictor:
            return self._get_mock_ai_prediction(protocol, timeframe)
        
        try:
            protocol_data = await self.get_protocol_data(protocol)
            if not protocol_data:
                return f"❌ Protocol {protocol} not found"
            
            # Convert to dict for AI predictor
            data_dict = {
                "protocol": protocol,
                "tvl": protocol_data.tvl,
                "change_7d": 0,  # Would be real from API
                "estimated_apy": protocol_data.current_apy
            }
            
            prediction = await self.ai_predictor.ensemble_prediction(data_dict, timeframe)
            return self.ai_predictor.format_prediction_report(prediction)
            
        except Exception as e:
            print(f"⚠️  AI prediction error: {e}")
            return self._get_mock_ai_prediction(protocol, timeframe)
    
    def _get_mock_ai_prediction(self, protocol: str, timeframe: str) -> str:
        """Generate mock AI prediction when real AI is not available"""
        protocol_data = self.fallback_data.get(protocol.lower())
        if not protocol_data:
            return f"❌ Protocol {protocol} not found"
        
        base_apy = protocol_data.current_apy
        
        return f"""
AI Yield Prediction: {protocol.upper()} (Demo Mode)
{'=' * 50}

Ensemble Results:
- Predicted APY: {base_apy + 0.3:.1f}%
- Prediction Range: {base_apy - 0.5:.1f}% - {base_apy + 1.1:.1f}%
- Standard Deviation: ±0.8%
- Average Confidence: 7.2/10
- Models Used: 3/3 (Demo)

Individual Model Predictions:
- GPT-4: {base_apy + 0.2:.1f}% (confidence: 7/10)
  Reasoning: Market trends suggest stable growth potential...
- CLAUDE: {base_apy + 0.5:.1f}% (confidence: 8/10)
  Reasoning: Protocol fundamentals support yield sustainability...
- GEMINI: {base_apy + 0.2:.1f}% (confidence: 7/10)
  Reasoning: Risk-adjusted projections indicate moderate upside...

Key Risk Factors:
- Market volatility
- Protocol governance changes
- Regulatory developments
- Liquidity conditions
- Competitive pressure

Note: This is a demonstration of AI prediction capabilities.
    Real predictions would use live API data and model inference.
        """

async def main():
    """Interactive RWA Agent CLI"""
    agent = SimpleRWAAgent()
    
    print("Welcome to RWA Yield Analysis Agent")
    print("=" * 50)
    print(f"Available protocols: {', '.join(agent.supported_protocols)}")
    
    while True:
        print("\nOptions:")
        print("1. Analyze Protocol (Real Data)")
        print("2. Compare Protocols")
        print("3. Optimize Portfolio")
        print("4. AI Yield Prediction (Multi-Model)")
        print("5. Exit")
        
        choice = input("Select option (1-5): ").strip()
        
        if choice == "1":
            protocol = input("Enter protocol name: ").strip().lower()
            timeframe = input("Enter timeframe (default: 30d): ").strip() or "30d"
            
            result = await agent.analyze_protocol_yields(protocol, timeframe)
            print(result)
            
        elif choice == "2":
            result = await agent.compare_protocols()
            print(result)
            
        elif choice == "3":
            try:
                amount = float(input("Enter investment amount ($): "))
                risk = input("Risk tolerance (low/medium/high, default: medium): ").strip().lower() or "medium"
                
                result = await agent.optimize_portfolio(amount, risk)
                print(result)
            except ValueError:
                print("❌ Invalid amount entered")
                
        elif choice == "4":
            protocol = input("Enter protocol for AI prediction: ").strip().lower()
            timeframe = input("Prediction timeframe (default: 90d): ").strip() or "90d"
            
            print(f"Getting AI predictions for {protocol}...")
            result = await agent.get_ai_yield_prediction(protocol, timeframe)
            print(result)
            
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("❌ Invalid option")

if __name__ == "__main__":
    asyncio.run(main())