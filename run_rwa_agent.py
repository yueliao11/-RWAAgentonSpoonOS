#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RWA Agent Runner
Direct execution of RWA agent functionality
"""

import asyncio
import os
import sys

# Set environment variables (read from system environment)
os.environ['ANTHROPIC_API_KEY'] = os.getenv('ANTHROPIC_API_KEY', '')
os.environ['ANTHROPIC_BASE_URL'] = os.getenv('ANTHROPIC_BASE_URL', 'https://openrouter.ai/api/v1')
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY', '')
os.environ['OPENAI_BASE_URL'] = os.getenv('OPENAI_BASE_URL', 'https://openrouter.ai/api/v1')

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def run_rwa_analysis():
    """Run RWA analysis with real or mock agent"""
    print("🏦 RWA Yield Analysis Agent")
    print("=" * 50)
    
    try:
        # Try to use the real SpoonOS framework
        print("Attempting to load SpoonOS RWA Agent...")
        
        # Import required modules
        from spoon_ai.agents.rwa_yield_agent import RWAYieldAgent
        from spoon_ai.chat import ChatBot
        from spoon_ai.tools import ToolManager
        
        print("✓ SpoonOS modules loaded successfully")
        
        # Create ChatBot with OpenRouter configuration
        chatbot = ChatBot(
            model_name="anthropic/claude-3.5-sonnet",
            llm_provider="openai",  # Use OpenAI-compatible interface
            base_url="https://openrouter.ai/api/v1"
        )
        print("✓ ChatBot configured with OpenRouter")
        
        # Create RWA agent
        agent = RWAYieldAgent(
            llm=chatbot,
            available_tools=ToolManager([])  # Start with empty tools
        )
        print("✓ RWA Yield Agent created")
        
        # Interactive menu
        while True:
            print("\n" + "=" * 50)
            print("RWA Agent Options:")
            print("1. Analyze Protocol Yields")
            print("2. Compare Multiple Protocols")
            print("3. Optimize Portfolio")
            print("4. Forecast Yields")
            print("5. Generate Report")
            print("6. Exit")
            print("=" * 50)
            
            choice = input("Select option (1-6): ").strip()
            
            if choice == "1":
                await analyze_protocol(agent)
            elif choice == "2":
                await compare_protocols(agent)
            elif choice == "3":
                await optimize_portfolio(agent)
            elif choice == "4":
                await forecast_yields(agent)
            elif choice == "5":
                await generate_report(agent)
            elif choice == "6":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid option. Please try again.")
                
    except ImportError as e:
        print(f"❌ Could not load SpoonOS modules: {e}")
        print("Running with mock functionality...")
        await run_mock_rwa_analysis()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

async def analyze_protocol(agent):
    """Analyze a specific protocol"""
    print("\n📊 Protocol Analysis")
    print("-" * 30)
    
    protocols = ["centrifuge", "goldfinch", "maple", "credix", "truefi"]
    print("Available protocols:", ", ".join(protocols))
    
    protocol = input("Enter protocol name: ").strip().lower()
    timeframe = input("Enter timeframe (default: 30d): ").strip() or "30d"
    
    print(f"\n🔍 Analyzing {protocol} for {timeframe}...")
    
    try:
        result = await agent.analyze_protocol_yields(protocol, timeframe)
        print("\n📈 Analysis Results:")
        print("-" * 40)
        print(result)
    except Exception as e:
        print(f"❌ Error analyzing protocol: {e}")

async def compare_protocols(agent):
    """Compare multiple protocols"""
    print("\n⚖️  Protocol Comparison")
    print("-" * 30)
    
    protocols_input = input("Enter protocols (comma-separated): ").strip()
    protocols = [p.strip().lower() for p in protocols_input.split(",")]
    
    asset_type = input("Enter asset type (optional): ").strip() or None
    
    print(f"\n🔍 Comparing protocols: {', '.join(protocols)}")
    
    try:
        result = await agent.compare_yields(protocols, asset_type)
        print("\n📊 Comparison Results:")
        print("-" * 40)
        print(result)
    except Exception as e:
        print(f"❌ Error comparing protocols: {e}")

async def optimize_portfolio(agent):
    """Optimize investment portfolio"""
    print("\n💼 Portfolio Optimization")
    print("-" * 30)
    
    try:
        amount = float(input("Investment amount ($): "))
        risk = input("Risk tolerance (low/medium/high): ").strip().lower()
        
        protocols_input = input("Target protocols (comma-separated, optional): ").strip()
        target_protocols = [p.strip().lower() for p in protocols_input.split(",")] if protocols_input else None
        
        print(f"\n🔍 Optimizing ${amount:,.0f} portfolio with {risk} risk...")
        
        result = await agent.optimize_portfolio(
            investment_amount=amount,
            risk_tolerance=risk,
            target_protocols=target_protocols
        )
        print("\n💰 Optimization Results:")
        print("-" * 40)
        print(result)
        
    except ValueError:
        print("❌ Invalid amount. Please enter a number.")
    except Exception as e:
        print(f"❌ Error optimizing portfolio: {e}")

async def forecast_yields(agent):
    """Forecast future yields"""
    print("\n🔮 Yield Forecasting")
    print("-" * 30)
    
    protocol = input("Protocol name: ").strip().lower()
    asset_type = input("Asset type: ").strip()
    period = input("Forecast period (default: 90d): ").strip() or "90d"
    
    print(f"\n🔍 Forecasting {protocol} yields for {period}...")
    
    try:
        result = await agent.forecast_yields(protocol, asset_type, period)
        print("\n📈 Forecast Results:")
        print("-" * 40)
        print(result)
    except Exception as e:
        print(f"❌ Error forecasting yields: {e}")

async def generate_report(agent):
    """Generate comprehensive report"""
    print("\n📄 Report Generation")
    print("-" * 30)
    
    protocols_input = input("Protocols for report (comma-separated): ").strip()
    protocols = [p.strip().lower() for p in protocols_input.split(",")]
    
    report_type = input("Report type (comprehensive/executive/technical/risk): ").strip() or "comprehensive"
    
    print(f"\n🔍 Generating {report_type} report for {', '.join(protocols)}...")
    
    try:
        result = await agent.generate_yield_report(protocols, report_type)
        print("\n📋 Generated Report:")
        print("-" * 40)
        print(result)
    except Exception as e:
        print(f"❌ Error generating report: {e}")

async def run_mock_rwa_analysis():
    """Run mock RWA analysis when real agent is not available"""
    print("\n🎭 Running Mock RWA Analysis")
    print("(Real agent not available - showing demo functionality)")
    
    # Import our mock agent
    sys.path.append(os.path.dirname(__file__))
    from minimal_rwa_test import MockRWAAgent
    
    agent = MockRWAAgent()
    
    print("\n1. Protocol Analysis Demo:")
    result = await agent.analyze_protocol_yields("centrifuge")
    print(result)
    
    print("\n2. Yield Comparison Demo:")
    result = await agent.compare_yields(["centrifuge", "goldfinch", "maple"])
    print(result)
    
    print("\n3. Portfolio Optimization Demo:")
    result = await agent.optimize_portfolio(100000, "medium")
    print(result)

if __name__ == "__main__":
    asyncio.run(run_rwa_analysis())