#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple RWA Agent Test
A minimal test script for RWA yield analysis functionality
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_basic_rwa_functionality():
    """Test basic RWA functionality without complex dependencies"""
    print("=== Simple RWA Agent Test ===\n")
    
    try:
        # Test 1: Basic imports
        print("1. Testing imports...")
        from spoon_ai.chat import ChatBot
        print("✓ ChatBot imported successfully")
        
        # Test 2: Create a basic chatbot instance
        print("\n2. Creating ChatBot instance...")
        chatbot = ChatBot(
            model_name="anthropic/claude-3.5-sonnet",
            llm_provider="openai",  # Using OpenAI-compatible API for OpenRouter
            base_url="https://openrouter.ai/api/v1"
        )
        print("✓ ChatBot instance created successfully")
        
        # Test 3: Test basic RWA analysis prompt
        print("\n3. Testing RWA yield analysis...")
        rwa_prompt = """
        You are an RWA (Real World Assets) yield analysis expert. Please analyze the following:
        
        1. Compare the typical yield ranges for these RWA protocols:
           - Centrifuge (tokenized real estate and invoices)
           - Goldfinch (private credit)
           - Maple Finance (institutional lending)
        
        2. Provide a brief risk assessment for each protocol
        
        3. Suggest a balanced portfolio allocation for $100,000 investment with medium risk tolerance
        
        Please provide specific APY ranges and allocation percentages.
        """
        
        # Make the API call
        response = await chatbot.chat(rwa_prompt)
        print("✓ RWA analysis completed")
        print("\n--- RWA Analysis Results ---")
        print(response)
        
        # Test 4: Portfolio optimization prompt
        print("\n\n4. Testing portfolio optimization...")
        portfolio_prompt = """
        Based on current market conditions, optimize a $50,000 RWA portfolio with these constraints:
        - Risk tolerance: Medium
        - Investment horizon: 12 months
        - Minimum APY target: 8%
        - Maximum single protocol allocation: 40%
        
        Consider these protocols:
        - Centrifuge (Real Estate): 7-12% APY, Medium risk
        - Goldfinch (Private Credit): 10-15% APY, Medium-High risk  
        - Maple Finance (Institutional): 6-10% APY, Low-Medium risk
        - TrueFi (Uncollateralized): 8-14% APY, High risk
        
        Provide specific dollar amounts for each allocation.
        """
        
        response = await chatbot.chat(portfolio_prompt)
        print("✓ Portfolio optimization completed")
        print("\n--- Portfolio Optimization Results ---")
        print(response)
        
        print("\n=== All tests completed successfully! ===")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("This might be due to missing dependencies.")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

async def test_rwa_agent_class():
    """Test the actual RWA agent class if available"""
    print("\n=== Testing RWA Agent Class ===\n")
    
    try:
        from spoon_ai.agents.rwa_yield_agent import RWAYieldAgent
        from spoon_ai.chat import ChatBot
        from spoon_ai.tools import ToolManager
        
        print("1. Creating RWA Yield Agent...")
        
        # Create ChatBot with OpenRouter configuration
        chatbot = ChatBot(
            model_name="anthropic/claude-3.5-sonnet",
            llm_provider="openai",
            base_url="https://openrouter.ai/api/v1"
        )
        
        # Create RWA agent with minimal tools
        agent = RWAYieldAgent(
            llm=chatbot,
            available_tools=ToolManager([])  # Empty tools for now
        )
        
        print("✓ RWA Yield Agent created successfully")
        
        # Test agent methods
        print("\n2. Testing agent analysis methods...")
        
        # Test protocol analysis
        result = await agent.analyze_protocol_yields("centrifuge", "30d")
        print("✓ Protocol analysis completed")
        print(f"Analysis result preview: {str(result)[:200]}...")
        
        # Test yield comparison
        result = await agent.compare_yields(
            protocols=["centrifuge", "goldfinch", "maple"],
            asset_type="private_credit"
        )
        print("✓ Yield comparison completed")
        print(f"Comparison result preview: {str(result)[:200]}...")
        
        print("\n=== RWA Agent tests completed successfully! ===")
        
    except ImportError as e:
        print(f"❌ Could not import RWA agent: {e}")
        print("Falling back to basic functionality test...")
        
    except Exception as e:
        print(f"❌ Error testing RWA agent: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Main test function"""
    print("Starting RWA Agent Testing...\n")
    
    # Test basic functionality first
    await test_basic_rwa_functionality()
    
    # Then test the actual agent class
    await test_rwa_agent_class()
    
    print("\n🎉 RWA Agent testing completed!")

if __name__ == "__main__":
    asyncio.run(main())