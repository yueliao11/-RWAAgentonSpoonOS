#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test specific translation keys
测试特定的翻译键
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from utils.i18n import get_i18n, t
    
    print("🔍 测试特定翻译键")
    print("🔍 Testing Specific Translation Keys")
    print("=" * 40)
    
    # Initialize i18n
    i18n = get_i18n()
    
    # Test specific problematic keys
    test_keys = [
        'dashboard.kpi.title',
        'dashboard.messages.no_data',
        'dashboard.messages.no_data_from_dashboard'
    ]
    
    # Test both languages
    for lang in ['en', 'zh']:
        print(f"\n📝 语言 / Language: {lang}")
        print("-" * 20)
        
        i18n.current_language = lang
        
        for key in test_keys:
            translation = i18n.get_text(key)
            print(f"  {key}:")
            print(f"    → {translation}")
    
    # Test the translation loading
    print(f"\n🔍 翻译文件加载测试 / Translation File Loading Test")
    print("-" * 40)
    
    print(f"可用语言 / Available languages: {i18n.get_available_languages()}")
    print(f"当前语言 / Current language: {i18n.get_current_language()}")
    
    # Test direct access to translations
    print(f"\n📁 直接访问翻译数据 / Direct Translation Data Access")
    print("-" * 40)
    
    for lang in ['en', 'zh']:
        if lang in i18n.translations:
            print(f"\n{lang} 翻译数据:")
            dashboard_data = i18n.translations[lang].get('dashboard', {})
            kpi_data = dashboard_data.get('kpi', {})
            messages_data = dashboard_data.get('messages', {})
            
            print(f"  dashboard.kpi.title: {kpi_data.get('title', 'NOT FOUND')}")
            print(f"  dashboard.messages.no_data: {messages_data.get('no_data', 'NOT FOUND')}")
            print(f"  dashboard.messages.no_data_from_dashboard: {messages_data.get('no_data_from_dashboard', 'NOT FOUND')}")
        else:
            print(f"{lang}: 翻译数据未找到")
    
    print("\n✅ 测试完成！")
    print("✅ Test completed!")
    
except Exception as e:
    print(f"❌ 测试失败 / Test failed: {e}")
    import traceback
    traceback.print_exc()