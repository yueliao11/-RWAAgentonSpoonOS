#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for RWA Yield Optimizer GUI with i18n support
测试RWA收益优化器GUI的国际化功能
"""

import streamlit as st
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.i18n import get_i18n, t, create_language_selector

def test_i18n_functionality():
    """Test i18n functionality"""
    st.title("🌐 RWA GUI 国际化测试 / i18n Test")
    
    # Language selector
    st.markdown("### 语言选择 / Language Selection")
    i18n = get_i18n()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**选择语言 / Select Language:**")
        i18n.create_language_selector("test_language")
    
    with col2:
        st.markdown(f"**当前语言 / Current Language:** {i18n.get_current_language()}")
    
    st.markdown("---")
    
    # Test translations
    st.markdown("### 翻译测试 / Translation Test")
    
    # App info
    st.markdown("#### 应用信息 / App Information")
    st.write(f"**标题 / Title:** {t('app.title')}")
    st.write(f"**副标题 / Subtitle:** {t('app.subtitle')}")
    st.write(f"**描述 / Description:** {t('app.description')}")
    
    # Navigation
    st.markdown("#### 导航 / Navigation")
    nav_items = ['dashboard', 'predictions', 'optimizer', 'comparison', 'settings']
    for item in nav_items:
        st.write(f"**{item.title()}:** {t(f'navigation.{item}')}")
    
    # Dashboard
    st.markdown("#### 仪表盘 / Dashboard")
    st.write(f"**标题 / Title:** {t('dashboard.title')}")
    st.write(f"**描述 / Description:** {t('dashboard.description')}")
    
    # KPI metrics
    kpi_items = ['total_protocols', 'average_apy', 'total_tvl', 'last_updated']
    for item in kpi_items:
        st.write(f"**{item.replace('_', ' ').title()}:** {t(f'dashboard.kpi.{item}')}")
    
    # Settings
    st.markdown("#### 设置 / Settings")
    st.write(f"**标题 / Title:** {t('settings.title')}")
    st.write(f"**API配置 / API Config:** {t('settings.api.title')}")
    st.write(f"**应用设置 / App Settings:** {t('settings.application.title')}")
    
    # Common buttons
    st.markdown("#### 通用按钮 / Common Buttons")
    button_items = ['save', 'cancel', 'refresh', 'export', 'delete']
    for item in button_items:
        st.write(f"**{item.title()}:** {t(f'common.buttons.{item}')}")
    
    # Number formatting test
    st.markdown("### 数字格式化测试 / Number Formatting Test")
    
    test_numbers = [1234.56, 1234567.89, 12.34, 0.1234]
    
    for num in test_numbers:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.write(f"**原始 / Original:** {num}")
        with col2:
            st.write(f"**默认 / Default:** {i18n.format_number(num)}")
        with col3:
            st.write(f"**货币 / Currency:** {i18n.format_number(num, 'currency')}")
        with col4:
            st.write(f"**百分比 / Percentage:** {i18n.format_number(num, 'percentage')}")
    
    # Large numbers
    st.markdown("#### 大数字格式化 / Large Number Formatting")
    large_numbers = [1000, 1000000, 1000000000, 1500000000]
    
    for num in large_numbers:
        st.write(f"**{num:,}** → {i18n.format_number(num, 'large_number')}")
    
    # Language toggle test
    st.markdown("### 语言切换测试 / Language Toggle Test")
    
    if st.button("🔄 切换语言 / Toggle Language"):
        current_lang = i18n.get_current_language()
        new_lang = 'zh' if current_lang == 'en' else 'en'
        i18n.set_language(new_lang)
        st.success(f"语言已切换到 / Language switched to: {new_lang}")
    
    # Available languages
    st.markdown("#### 可用语言 / Available Languages")
    available_langs = i18n.get_available_languages()
    for code, name in available_langs.items():
        status = "✅ 当前 / Current" if code == i18n.get_current_language() else ""
        st.write(f"**{code}:** {name} {status}")
    
    # Error handling test
    st.markdown("### 错误处理测试 / Error Handling Test")
    
    # Test missing key
    missing_key_result = t('non.existent.key')
    st.write(f"**缺失键 / Missing Key:** {missing_key_result}")
    
    # Test with parameters
    if i18n.get_current_language() == 'en':
        param_test = t('dashboard.kpi.total_protocols')  # This should work
    else:
        param_test = t('dashboard.kpi.total_protocols')  # This should work in Chinese too
    
    st.write(f"**参数测试 / Parameter Test:** {param_test}")

def main():
    """Main function"""
    st.set_page_config(
        page_title="RWA GUI i18n Test",
        page_icon="🌐",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for better appearance
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .test-section {
        background: rgba(255, 255, 255, 0.05);
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    
    .success-message {
        background: rgba(16, 185, 129, 0.1);
        padding: 0.5rem;
        border-radius: 5px;
        border-left: 3px solid #10b981;
        color: #10b981;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🌐 RWA Yield Optimizer GUI</h1>
        <h2>国际化功能测试 / Internationalization Test</h2>
        <p>测试中英文切换功能 / Testing Chinese-English Language Switching</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Run tests
    test_i18n_functionality()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #888; padding: 1rem;">
        <p>🚀 RWA Yield Optimizer - Professional Real-World Assets Investment Analysis Platform</p>
        <p>RWA收益优化器 - 专业的实物资产投资分析平台</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()