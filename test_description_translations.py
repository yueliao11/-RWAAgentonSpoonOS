#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test description translations specifically
测试描述文本的翻译功能
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from utils.i18n import get_i18n, t
    
    print("🌐 描述文本翻译测试")
    print("🌐 Description Translation Test")
    print("=" * 60)
    
    # Initialize i18n
    i18n = get_i18n()
    
    # Test description keys
    description_keys = [
        'settings.description',
        'predictions.description', 
        'dashboard.description',
        'optimizer.description',
        'comparison.description'
    ]
    
    # Test both languages
    languages = ['en', 'zh']
    
    for lang in languages:
        print(f"\n📝 测试语言 / Testing Language: {lang.upper()}")
        print("-" * 50)
        
        i18n.current_language = lang
        
        for key in description_keys:
            translation = i18n.get_text(key)
            
            if translation.startswith('[Missing:') or translation.startswith('[Error:'):
                print(f"  ❌ {key}: {translation}")
            else:
                print(f"  ✅ {key}:")
                print(f"     {translation}")
                print()
    
    print(f"\n🔧 测试 t() 函数调用 / Testing t() function calls:")
    print("-" * 50)
    
    # Test with English
    i18n.current_language = 'en'
    print(f"EN - Settings Description:")
    print(f"🔑 {t('settings.description')}")
    print()
    print(f"EN - Predictions Description:")
    print(f"🧠 {t('predictions.description')}")
    print()
    print(f"EN - Dashboard Description:")
    print(f"📊 {t('dashboard.description')}")
    print()
    
    # Test with Chinese
    i18n.current_language = 'zh'
    print(f"ZH - Settings Description:")
    print(f"🔑 {t('settings.description')}")
    print()
    print(f"ZH - Predictions Description:")
    print(f"🧠 {t('predictions.description')}")
    print()
    print(f"ZH - Dashboard Description:")
    print(f"📊 {t('dashboard.description')}")
    print()
    
    print(f"✅ 描述文本翻译测试完成！")
    print(f"✅ Description translation test completed!")

except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请确保 utils/i18n.py 文件存在且正确配置")
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()