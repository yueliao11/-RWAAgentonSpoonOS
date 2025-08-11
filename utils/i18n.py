# -*- coding: utf-8 -*-
"""
Internationalization (i18n) utility for RWA Yield Optimizer GUI
支持多语言的国际化工具
"""

import json
import os
from typing import Dict, Any, Optional

try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False
    # Mock streamlit session_state for testing
    class MockSessionState:
        def __init__(self):
            self._state = {}
        
        def __contains__(self, key):
            return key in self._state
        
        def __getitem__(self, key):
            return self._state[key]
        
        def __setitem__(self, key, value):
            self._state[key] = value
        
        def get(self, key, default=None):
            return self._state.get(key, default)
    
    class MockStreamlit:
        def __init__(self):
            self.session_state = MockSessionState()
        
        def selectbox(self, *args, **kwargs):
            return "English"
        
        def rerun(self):
            pass
    
    st = MockStreamlit()

class I18nManager:
    """国际化管理器 / Internationalization manager"""
    
    def __init__(self, default_language: str = 'en'):
        self.default_language = default_language
        self.current_language = default_language
        self.translations: Dict[str, Dict[str, Any]] = {}
        self.locales_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'locales')
        
        # 加载可用语言 / Load available languages
        self.load_all_languages()
        
        # 初始化会话状态 / Initialize session state for language
        if 'language' not in st.session_state:
            st.session_state.language = default_language
        
        self.current_language = st.session_state.language
    
    def load_all_languages(self):
        """加载所有可用的语言文件 / Load all available language files"""
        if not os.path.exists(self.locales_dir):
            os.makedirs(self.locales_dir)
            return
        
        for filename in os.listdir(self.locales_dir):
            if filename.endswith('.json'):
                language_code = filename[:-5]  # 移除.json扩展名
                self.load_language(language_code)
    
    def load_language(self, language_code: str) -> bool:
        """加载特定语言文件 / Load a specific language file"""
        try:
            file_path = os.path.join(self.locales_dir, f'{language_code}.json')
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.translations[language_code] = json.load(f)
                return True
            return False
        except Exception as e:
            print(f"Error loading language {language_code}: {str(e)}")
            return False
    
    def get_available_languages(self) -> Dict[str, str]:
        """获取可用语言列表 / Get list of available languages with their display names"""
        language_names = {
            'en': 'English',
            'zh': '中文',
            'es': 'Español',
            'fr': 'Français',
            'de': 'Deutsch',
            'ja': '日本語',
            'ko': '한국어'
        }
        
        available = {}
        for lang_code in self.translations.keys():
            available[lang_code] = language_names.get(lang_code, lang_code.upper())
        
        return available
    
    def set_language(self, language_code: str):
        """设置当前语言 / Set the current language"""
        if language_code in self.translations:
            self.current_language = language_code
            st.session_state.language = language_code
            # 强制重新运行以更新UI / Force rerun to update UI
            if HAS_STREAMLIT:
                st.rerun()
        else:
            print(f"Language {language_code} not available")
    
    def get_text(self, key_path: str, **kwargs) -> str:
        """通过键路径获取翻译文本 / Get translated text by key path (e.g., 'dashboard.title')"""
        try:
            # 获取当前语言翻译 / Get current language translations
            current_translations = self.translations.get(
                self.current_language, 
                self.translations.get(self.default_language, {})
            )
            
            # 通过嵌套键导航 / Navigate through nested keys
            keys = key_path.split('.')
            value = current_translations
            
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    # 回退到默认语言 / Fallback to default language
                    if self.current_language != self.default_language:
                        return self.get_text_from_language(key_path, self.default_language, **kwargs)
                    else:
                        return f"[Missing: {key_path}]"
            
            # 处理字符串格式化 / Handle string formatting
            if isinstance(value, str) and kwargs:
                try:
                    return value.format(**kwargs)
                except KeyError:
                    return value
            
            return str(value) if value is not None else f"[Missing: {key_path}]"
            
        except Exception as e:
            print(f"Error getting translation for {key_path}: {str(e)}")
            return f"[Error: {key_path}]"
    
    def get_text_from_language(self, key_path: str, language_code: str, **kwargs) -> str:
        """从特定语言获取文本 / Get text from a specific language"""
        try:
            translations = self.translations.get(language_code, {})
            keys = key_path.split('.')
            value = translations
            
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return f"[Missing: {key_path}]"
            
            if isinstance(value, str) and kwargs:
                try:
                    return value.format(**kwargs)
                except KeyError:
                    return value
            
            return str(value) if value is not None else f"[Missing: {key_path}]"
            
        except Exception:
            return f"[Error: {key_path}]"
    
    def t(self, key_path: str, **kwargs) -> str:
        """get_text的简写方法 / Shorthand method for get_text"""
        return self.get_text(key_path, **kwargs)
    
    def get_current_language(self) -> str:
        """获取当前语言代码 / Get current language code"""
        return self.current_language
    
    def create_language_selector(self, key: str = "language_selector") -> Optional[str]:
        """创建语言选择器组件 / Create a language selector widget"""
        if not HAS_STREAMLIT:
            return self.current_language
            
        available_languages = self.get_available_languages()
        
        if len(available_languages) <= 1:
            return None
        
        # 创建语言选择框 / Create selectbox for language selection
        language_names = list(available_languages.values())
        language_codes = list(available_languages.keys())
        
        try:
            current_index = language_codes.index(self.current_language)
        except ValueError:
            current_index = 0
        
        selected_name = st.selectbox(
            "🌐 Language / 语言",
            language_names,
            index=current_index,
            key=key
        )
        
        # 获取对应的语言代码 / Get the corresponding language code
        if selected_name:
            selected_code = language_codes[language_names.index(selected_name)]
            if selected_code != self.current_language:
                self.set_language(selected_code)
            return selected_code
        
        return self.current_language
    
    def format_number(self, number: float, format_type: str = 'default') -> str:
        """根据当前语言格式化数字 / Format numbers according to current language locale"""
        try:
            if format_type == 'currency':
                if self.current_language == 'zh':
                    return f"¥{number:,.2f}"
                else:
                    return f"${number:,.2f}"
            elif format_type == 'percentage':
                return f"{number:.2f}%"
            elif format_type == 'large_number':
                if number >= 1_000_000_000:
                    return f"{number/1_000_000_000:.1f}B"
                elif number >= 1_000_000:
                    return f"{number/1_000_000:.1f}M"
                elif number >= 1_000:
                    return f"{number/1_000:.1f}K"
                else:
                    return f"{number:,.0f}"
            else:
                return f"{number:,.2f}"
        except Exception:
            return str(number)

# 全局i18n实例 / Global i18n instance
_i18n_instance = None

def get_i18n() -> I18nManager:
    """获取全局i18n实例（单例模式）/ Get global i18n instance (singleton pattern)"""
    global _i18n_instance
    if _i18n_instance is None:
        _i18n_instance = I18nManager()
    return _i18n_instance

def t(key_path: str, **kwargs) -> str:
    """翻译的全局简写函数 / Global shorthand function for translations"""
    return get_i18n().get_text(key_path, **kwargs)

def set_language(language_code: str):
    """设置语言的全局函数 / Global function to set language"""
    get_i18n().set_language(language_code)

def get_current_language() -> str:
    """获取当前语言的全局函数 / Global function to get current language"""
    return get_i18n().get_current_language()

def create_language_selector(key: str = "language_selector") -> Optional[str]:
    """创建语言选择器的全局函数 / Global function to create language selector"""
    return get_i18n().create_language_selector(key)

def format_number(number: float, format_type: str = 'default') -> str:
    """格式化数字的全局函数 / Global function to format numbers"""
    return get_i18n().format_number(number, format_type)