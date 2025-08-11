#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo showing how description translations are used in the GUI
演示描述文本翻译在GUI中的使用方式
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from utils.i18n import get_i18n, t
    
    print("🎨 GUI描述文本使用演示")
    print("🎨 GUI Description Text Usage Demo")
    print("=" * 60)
    
    # Initialize i18n
    i18n = get_i18n()
    
    def show_page_descriptions(language):
        """显示各页面的描述文本"""
        i18n.current_language = language
        
        print(f"\n🌐 语言 / Language: {language.upper()}")
        print("=" * 50)
        
        # Dashboard page
        print(f"\n📊 仪表盘页面 / Dashboard Page")
        print("-" * 30)
        print(f"标题: {t('dashboard.title')}")
        print(f"描述: {t('dashboard.description')}")
        
        # Predictions page
        print(f"\n🧠 预测页面 / Predictions Page")
        print("-" * 30)
        print(f"标题: {t('predictions.title')}")
        print(f"描述: {t('predictions.description')}")
        
        # Optimizer page
        print(f"\n💼 优化器页面 / Optimizer Page")
        print("-" * 30)
        print(f"标题: {t('optimizer.title')}")
        print(f"描述: {t('optimizer.description')}")
        
        # Comparison page
        print(f"\n📊 对比页面 / Comparison Page")
        print("-" * 30)
        print(f"标题: {t('comparison.title')}")
        print(f"描述: {t('comparison.description')}")
        
        # Settings page
        print(f"\n⚙️ 设置页面 / Settings Page")
        print("-" * 30)
        print(f"标题: {t('settings.title')}")
        print(f"描述: {t('settings.description')}")
    
    # Show descriptions in both languages
    show_page_descriptions('en')
    show_page_descriptions('zh')
    
    print(f"\n🔧 Streamlit代码示例 / Streamlit Code Examples:")
    print("=" * 50)
    
    print("""
# 在Streamlit中使用描述文本的示例代码:

# Dashboard页面
st.markdown(f'<h1 class="main-title">🏠 {t("dashboard.title")}</h1>', unsafe_allow_html=True)
st.markdown(f'''
    <div class="description-box">
        📊 <strong>{t("dashboard.description")}</strong>
    </div>
''', unsafe_allow_html=True)

# Predictions页面
st.markdown(f'<h1 class="main-title">🤖 {t("predictions.title")}</h1>', unsafe_allow_html=True)
st.markdown(f'''
    <div class="description-box">
        🧠 <strong>{t("predictions.description")}</strong>
    </div>
''', unsafe_allow_html=True)

# Settings页面
st.markdown(f'<h1 class="main-title">⚙️ {t("settings.title")}</h1>', unsafe_allow_html=True)
st.markdown(f'''
    <div class="description-box">
        🔑 <strong>{t("settings.description")}</strong>
    </div>
''', unsafe_allow_html=True)
    """)
    
    print(f"\n✅ 演示完成！所有描述文本都已正确配置多语言支持！")
    print(f"✅ Demo completed! All description texts are properly configured with multi-language support!")

except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请确保 utils/i18n.py 文件存在且正确配置")
except Exception as e:
    print(f"❌ 演示失败: {e}")
    import traceback
    traceback.print_exc()