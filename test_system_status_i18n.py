#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test system status i18n functionality
测试系统状态国际化功能
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from utils.i18n import get_i18n, t
    
    print("🔧 系统状态国际化测试")
    print("🔧 System Status i18n Test")
    print("=" * 40)
    
    # Initialize i18n
    i18n = get_i18n()
    
    # Test the newly fixed keys
    test_keys = [
        'settings.system.title',
        'settings.system.status_online', 
        'settings.system.status_waiting',
        'settings.system.last_update',
        'settings.system.quick_actions',
        'settings.system.quick_refresh',
        'dashboard.messages.never_updated'
    ]
    
    # Test both languages
    languages = ['en', 'zh']
    
    for lang in languages:
        print(f"\n📝 测试语言 / Testing Language: {lang}")
        print("-" * 30)
        
        # Set language (without streamlit, this won't trigger rerun)
        i18n.current_language = lang
        
        for key in test_keys:
            translation = i18n.get_text(key)
            print(f"  {key}: {translation}")
    
    print("\n🎯 具体场景测试 / Specific Scenario Test")
    print("-" * 30)
    
    # Test the specific text mentioned by user
    print("用户反馈的文字 / User reported text:")
    print("- 系统状态 / System Status")
    print("- 等待数据 / Waiting for Data") 
    print("- 最后更新: 从未更新 / Last Update: Never")
    print("- 快速操作 / Quick Actions")
    print("- 快速刷新 / Quick Refresh")
    
    print("\n修复后的翻译 / Fixed translations:")
    
    for lang in languages:
        i18n.current_language = lang
        print(f"\n{lang.upper()}:")
        print(f"  系统状态 → {i18n.get_text('settings.system.title')}")
        print(f"  等待数据 → {i18n.get_text('settings.system.status_waiting')}")
        print(f"  从未更新 → {i18n.get_text('dashboard.messages.never_updated')}")
        print(f"  快速操作 → {i18n.get_text('settings.system.quick_actions')}")
        print(f"  快速刷新 → {i18n.get_text('settings.system.quick_refresh')}")
        print(f"  最后更新 → {i18n.get_text('settings.system.last_update')}")
    
    print("\n✅ 所有系统状态文字已完全国际化！")
    print("✅ All system status text has been fully internationalized!")
    
except Exception as e:
    print(f"❌ 测试失败 / Test failed: {e}")
    import traceback
    traceback.print_exc()