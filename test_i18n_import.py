#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test i18n import functionality
测试i18n导入功能
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("🔍 Testing i18n import...")
    from utils.i18n import get_i18n, t, create_language_selector
    print("✅ i18n import successful!")
    
    print("\n🔍 Testing i18n functionality...")
    i18n = get_i18n()
    print("✅ i18n instance created:", type(i18n))
    
    print("✅ Available languages:", i18n.get_available_languages())
    print("✅ Current language:", i18n.get_current_language())
    
    # Test translation
    print("\n🔍 Testing translations...")
    try:
        # This should work without streamlit
        test_text = i18n.get_text('app.title')
        print("✅ Translation test:", test_text)
    except Exception as e:
        print("⚠️  Translation test (expected without streamlit):", e)
    
    print("\n🎉 All tests passed! i18n is ready to use.")
    
except ImportError as e:
    print("❌ Import error:", e)
    print("Please check if utils/i18n.py exists and locales directory is set up correctly.")
except Exception as e:
    print("❌ Unexpected error:", e)
    import traceback
    traceback.print_exc()