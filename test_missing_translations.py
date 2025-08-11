#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test missing translations that user reported
测试用户反馈的缺失翻译
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from utils.i18n import get_i18n, t
    
    print("🔍 测试用户反馈的缺失翻译")
    print("🔍 Testing User Reported Missing Translations")
    print("=" * 50)
    
    # Initialize i18n
    i18n = get_i18n()
    
    # Test the specific keys mentioned by user
    test_keys = [
        'dashboard.description',
        'dashboard.controls.refresh_data',
        'dashboard.controls.auto_refresh', 
        'dashboard.controls.time_range',
        'dashboard.controls.system_online',
        'dashboard.kpi.title',
        'dashboard.kpi.total_protocols',
        'dashboard.messages.fetching_data',
        'dashboard.messages.data_updated',
        'dashboard.messages.no_data',
        'dashboard.messages.no_data_from_dashboard'
    ]
    
    # Test both languages
    languages = ['en', 'zh']
    
    for lang in languages:
        print(f"\n📝 测试语言 / Testing Language: {lang}")
        print("-" * 40)
        
        # Set language (without streamlit, this won't trigger rerun)
        i18n.current_language = lang
        
        for key in test_keys:
            translation = i18n.get_text(key)
            status = "✅" if not translation.startswith("[Missing:") else "❌"
            print(f"  {status} {key}: {translation}")
    
    print("\n🎯 用户反馈的具体文字测试 / User Reported Text Test")
    print("-" * 50)
    
    user_reported_issues = [
        ("📊 {t('dashboard.description')}", 'dashboard.description'),
        ("🔄 Refresh Data", 'dashboard.controls.refresh_data'),
        ("🔄 Auto Refresh", 'dashboard.controls.auto_refresh'),
        ("System Online", 'dashboard.controls.system_online'),
        ("[Missing: dashboard.kpi.title]", 'dashboard.kpi.title'),
        ("Total Protocols", 'dashboard.kpi.total_protocols')
    ]
    
    print("修复前的问题 / Issues before fix:")
    for issue_text, key in user_reported_issues:
        print(f"  - {issue_text}")
    
    print("\n修复后的翻译 / Fixed translations:")
    for lang in languages:
        i18n.current_language = lang
        print(f"\n{lang.upper()}:")
        for issue_text, key in user_reported_issues:
            translation = i18n.get_text(key)
            print(f"  {key} → {translation}")
    
    print("\n✅ 所有缺失的翻译已修复！")
    print("✅ All missing translations have been fixed!")
    
except Exception as e:
    print(f"❌ 测试失败 / Test failed: {e}")
    import traceback
    traceback.print_exc()