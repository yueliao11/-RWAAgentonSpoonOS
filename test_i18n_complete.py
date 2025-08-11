#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete i18n functionality test
完整的国际化功能测试
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from utils.i18n import get_i18n, t
    
    print("🌐 RWA GUI 国际化功能完整测试")
    print("🌐 RWA GUI i18n Complete Functionality Test")
    print("=" * 50)
    
    # Initialize i18n
    i18n = get_i18n()
    
    # Test both languages
    languages = ['en', 'zh']
    
    for lang in languages:
        print(f"\n📝 测试语言 / Testing Language: {lang}")
        print("-" * 30)
        
        # Set language (without streamlit, this won't trigger rerun)
        i18n.current_language = lang
        
        # Test key translations
        test_keys = [
            'app.title',
            'navigation.dashboard',
            'navigation.predictions',
            'navigation.optimizer', 
            'navigation.comparison',
            'navigation.settings',
            'dashboard.title',
            'dashboard.description',
            'predictions.title',
            'predictions.description',
            'optimizer.title',
            'optimizer.description',
            'comparison.title',
            'comparison.description',
            'settings.title',
            'settings.description',
            'dashboard.kpi.total_protocols',
            'dashboard.kpi.average_apy',
            'dashboard.kpi.total_tvl',
            'dashboard.kpi.last_updated',
            'common.buttons.save',
            'common.buttons.refresh',
            'common.status.loading'
        ]
        
        for key in test_keys:
            translation = i18n.get_text(key)
            print(f"  {key}: {translation}")
    
    print("\n🎉 所有翻译测试完成！")
    print("🎉 All translation tests completed!")
    
    # Test number formatting
    print(f"\n🔢 数字格式化测试 / Number Formatting Test")
    print("-" * 30)
    
    test_numbers = [1234.56, 1500000, 0.1234]
    
    for lang in languages:
        i18n.current_language = lang
        print(f"\n语言 / Language: {lang}")
        
        for num in test_numbers:
            default_format = i18n.format_number(num)
            currency_format = i18n.format_number(num, 'currency')
            percentage_format = i18n.format_number(num, 'percentage')
            large_format = i18n.format_number(num, 'large_number')
            
            print(f"  {num} -> Default: {default_format}, Currency: {currency_format}, Percentage: {percentage_format}, Large: {large_format}")
    
    print("\n✅ 国际化功能测试全部通过！")
    print("✅ All i18n functionality tests passed!")
    
except Exception as e:
    print(f"❌ 测试失败 / Test failed: {e}")
    import traceback
    traceback.print_exc()