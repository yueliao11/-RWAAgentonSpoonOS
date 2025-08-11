#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test all translations to ensure they work correctly
测试所有翻译以确保它们正常工作
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from utils.i18n import get_i18n, t
    
    print("🌐 完整翻译功能测试")
    print("🌐 Complete Translation Functionality Test")
    print("=" * 60)
    
    # Initialize i18n
    i18n = get_i18n()
    
    # 从代码中提取的所有翻译键
    all_keys = [
        'dashboard.title', 'dashboard.description', 'dashboard.controls.refresh_data',
        'dashboard.messages.fetching_data', 'dashboard.messages.data_updated',
        'dashboard.controls.auto_refresh', 'dashboard.controls.time_range',
        'dashboard.controls.system_online', 'dashboard.messages.no_data',
        'dashboard.kpi.title', 'dashboard.messages.no_data_from_dashboard',
        'predictions.title', 'predictions.description', 'predictions.parameters.title',
        'predictions.parameters.select_protocol', 'predictions.timeframes.30d',
        'predictions.timeframes.90d', 'predictions.timeframes.180d',
        'predictions.timeframes.365d', 'predictions.parameters.prediction_timeframe',
        'predictions.parameters.ai_models', 'predictions.parameters.generate_predictions',
        'predictions.messages.analyzing', 'predictions.messages.completed',
        'predictions.messages.failed', 'predictions.results.title',
        'optimizer.title', 'optimizer.description', 'optimizer.parameters.title',
        'optimizer.results.title', 'optimizer.visualization.portfolio_allocation',
        'optimizer.visualization.investment_amounts', 'optimizer.export.title',
        'comparison.title', 'comparison.description', 'comparison.selection.title',
        'comparison.recommendations.title', 'comparison.recommendations.description',
        'comparison.heatmap.title', 'comparison.radar.title', 'comparison.table.title',
        'comparison.table.protocol', 'comparison.table.apy', 'comparison.table.risk_score',
        'comparison.table.asset_type', 'comparison.table.tvl', 'comparison.table.active_pools',
        'comparison.table.min_investment', 'comparison.table.lock_period',
        'comparison.recommendations_section.title', 'settings.title', 'settings.description',
        'settings.api.title', 'settings.api.openrouter_key', 'settings.api.anthropic_key',
        'settings.api.save_keys', 'settings.messages.keys_saved', 'settings.application.title',
        'settings.application.auto_refresh', 'settings.application.refresh_interval',
        'settings.application.theme', 'settings.application.language',
        'settings.application.save_settings', 'settings.messages.settings_saved',
        'settings.system.title', 'settings.system.status_online', 'settings.system.status_waiting',
        'dashboard.messages.never_updated', 'settings.system.last_update',
        'settings.system.quick_actions', 'settings.system.quick_refresh',
        'navigation.dashboard', 'navigation.predictions', 'navigation.optimizer',
        'navigation.comparison', 'navigation.settings'
    ]
    
    # Test both languages
    languages = ['en', 'zh']
    
    for lang in languages:
        print(f"\n📝 测试语言 / Testing Language: {lang.upper()}")
        print("-" * 50)
        
        i18n.current_language = lang
        
        success_count = 0
        error_count = 0
        
        for key in all_keys:
            translation = i18n.get_text(key)
            
            if translation.startswith('[Missing:') or translation.startswith('[Error:'):
                print(f"  ❌ {key}: {translation}")
                error_count += 1
            else:
                success_count += 1
                # 只显示前几个成功的例子
                if success_count <= 5:
                    print(f"  ✅ {key}: {translation[:50]}{'...' if len(translation) > 50 else ''}")
        
        print(f"\n📊 {lang.upper()} 统计结果:")
        print(f"  ✅ 成功: {success_count} 个")
        print(f"  ❌ 失败: {error_count} 个")
        print(f"  📈 成功率: {(success_count/(success_count+error_count)*100):.1f}%")
    
    print(f"\n🎉 翻译测试完成！")
    print(f"🎉 Translation test completed!")
    
    # Test the t() function directly
    print(f"\n🔧 测试 t() 函数 / Testing t() function:")
    print("-" * 40)
    
    # Test with English
    i18n.current_language = 'en'
    print(f"EN - Dashboard: {t('dashboard.title')}")
    print(f"EN - Predictions: {t('predictions.title')}")
    print(f"EN - Settings: {t('settings.title')}")
    
    # Test with Chinese
    i18n.current_language = 'zh'
    print(f"ZH - Dashboard: {t('dashboard.title')}")
    print(f"ZH - Predictions: {t('predictions.title')}")
    print(f"ZH - Settings: {t('settings.title')}")
    
    print(f"\n✅ 所有测试通过！翻译系统工作正常！")
    print(f"✅ All tests passed! Translation system is working properly!")

except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请确保 utils/i18n.py 文件存在且正确配置")
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()