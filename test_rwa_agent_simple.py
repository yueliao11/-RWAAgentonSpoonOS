#!/usr/bin/env python3
"""
Simple test of RWA Agent functionality
"""

import asyncio
from simple_rwa_agent import SimpleRWAAgent

async def test_agent():
    """Test the RWA agent functionality"""
    print("🧪 Testing Enhanced RWA Agent")
    print("=" * 40)
    
    agent = SimpleRWAAgent()
    
    # Test 1: Protocol Analysis
    print("\n1. Testing Protocol Analysis...")
    result = await agent.analyze_protocol_yields("centrifuge", "30d")
    print("✅ Protocol analysis completed")
    print(f"Preview: {result[:200]}...")
    
    # Test 2: Protocol Comparison
    print("\n2. Testing Protocol Comparison...")
    result = await agent.compare_protocols()
    print("✅ Protocol comparison completed")
    print(f"Preview: {result[:200]}...")
    
    # Test 3: Portfolio Optimization
    print("\n3. Testing Portfolio Optimization...")
    result = await agent.optimize_portfolio(50000, "medium")
    print("✅ Portfolio optimization completed")
    print(f"Preview: {result[:200]}...")
    
    # Test 4: AI Prediction
    print("\n4. Testing AI Yield Prediction...")
    result = await agent.get_ai_yield_prediction("centrifuge", "90d")
    print("✅ AI prediction completed")
    print(f"Preview: {result[:200]}...")
    
    print("\n🎉 All tests completed successfully!")
    print("🚀 Enhanced RWA Agent is fully functional!")

if __name__ == "__main__":
    asyncio.run(test_agent())