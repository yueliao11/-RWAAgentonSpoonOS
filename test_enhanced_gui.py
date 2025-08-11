#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test core functionality of enhanced GUI
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test all necessary imports"""
    try:
        import streamlit as st
        print("✅ Streamlit imported successfully")
        
        import plotly.express as px
        import plotly.graph_objects as go
        print("✅ Plotly imported successfully")
        
        from streamlit_option_menu import option_menu
        print("✅ streamlit-option-menu imported successfully")
        
        from services.data_service import RWADataService
        print("✅ RWADataService imported successfully")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_gui_functions():
    """Test GUI core functions"""
    try:
        # Import GUI module
        import gui_app_enhanced
        print("✅ GUI app enhanced imported successfully")
        
        # Test chart creation functions
        fig = gui_app_enhanced.create_gauge_chart(15.5, "Test APY", 20)
        print("✅ create_gauge_chart function works")
        
        # Test dynamic line chart
        test_data = {
            'protocol1': [10, 12, 11, 13, 12],
            'protocol2': [8, 9, 10, 9, 11]
        }
        fig2 = gui_app_enhanced.create_dynamic_line_chart(test_data, "Test Chart")
        print("✅ create_dynamic_line_chart function works")
        
        # Test 3D prediction chart
        predictions_data = {
            'gpt4': {
                'apy': [12.5, 13.0, 12.8],
                'confidence': [8.5, 8.2, 8.7],
                'risk': [0.3, 0.4, 0.35]
            }
        }
        fig3 = gui_app_enhanced.create_3d_prediction_chart(predictions_data)
        print("✅ create_3d_prediction_chart function works")
        
        return True
    except Exception as e:
        print(f"❌ GUI function error: {e}")
        return False

def test_data_service():
    """Test data service"""
    try:
        from services.data_service import RWADataService
        
        # Create data service instance
        data_service = RWADataService()
        print("✅ RWADataService instance created")
        
        # Test getting dashboard summary
        summary = data_service.get_dashboard_summary()
        print(f"✅ Dashboard summary retrieved: {len(summary.get('protocols', []))} protocols")
        
        return True
    except Exception as e:
        print(f"❌ Data service error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Testing Enhanced GUI Components...")
    print("=" * 50)
    
    # 测试导入
    print("\\n📦 Testing Imports...")
    imports_ok = test_imports()
    
    # 测试GUI函数
    print("\\n🎨 Testing GUI Functions...")
    gui_ok = test_gui_functions()
    
    # 测试数据服务
    print("\\n📊 Testing Data Service...")
    data_ok = test_data_service()
    
    # 总结
    print("\\n" + "=" * 50)
    print("📋 Test Summary:")
    print(f"   Imports: {'✅ PASS' if imports_ok else '❌ FAIL'}")
    print(f"   GUI Functions: {'✅ PASS' if gui_ok else '❌ FAIL'}")
    print(f"   Data Service: {'✅ PASS' if data_ok else '❌ FAIL'}")
    
    if imports_ok and gui_ok and data_ok:
        print("\\n🎉 All tests passed! Enhanced GUI is ready to launch.")
        print("\\n🚀 To start the enhanced GUI, run:")
        print("   ./start_enhanced_gui.sh")
        print("   or")
        print("   streamlit run gui_app_enhanced.py")
    else:
        print("\\n⚠️  Some tests failed. Please check the errors above.")
    
    return imports_ok and gui_ok and data_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)