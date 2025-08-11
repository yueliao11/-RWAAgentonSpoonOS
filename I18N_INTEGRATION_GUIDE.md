# RWA Yield Optimizer GUI 国际化集成指南
# RWA Yield Optimizer GUI Internationalization Integration Guide

## 概述 / Overview

本指南详细介绍了如何在RWA收益优化器GUI中实现和使用国际化(i18n)功能，支持中英文无缝切换。

This guide provides detailed instructions on implementing and using internationalization (i18n) features in the RWA Yield Optimizer GUI, supporting seamless Chinese-English language switching.

## 🌟 主要特性 / Key Features

### ✅ 已实现功能 / Implemented Features

1. **多语言支持 / Multi-language Support**
   - 🇨🇳 中文 (Chinese)
   - 🇺🇸 English
   - 🔧 可扩展支持更多语言 / Extensible for more languages

2. **JSON配置文件 / JSON Configuration Files**
   - `locales/en.json` - 英文翻译
   - `locales/zh.json` - 中文翻译
   - 结构化的嵌套键值对 / Structured nested key-value pairs

3. **智能翻译系统 / Smart Translation System**
   - 自动回退到默认语言 / Automatic fallback to default language
   - 缺失键的错误处理 / Error handling for missing keys
   - 参数化翻译支持 / Parameterized translation support

4. **语言选择器 / Language Selector**
   - 下拉选择框 / Dropdown selector
   - 简单切换按钮 / Simple toggle button
   - 会话状态保持 / Session state persistence

5. **数字格式化 / Number Formatting**
   - 货币格式 / Currency formatting
   - 百分比格式 / Percentage formatting
   - 大数字简化 / Large number abbreviation
   - 本地化数字显示 / Localized number display

## 📁 文件结构 / File Structure

```
project/
├── locales/                    # 语言文件目录 / Language files directory
│   ├── en.json                # 英文翻译 / English translations
│   └── zh.json                # 中文翻译 / Chinese translations
├── utils/
│   └── i18n.py                # 国际化工具类 / i18n utility class
├── gui_app_enhanced.py        # 主GUI应用(已集成i18n) / Main GUI app (i18n integrated)
├── test_i18n_gui.py          # i18n功能测试 / i18n functionality test
└── I18N_INTEGRATION_GUIDE.md # 本指南 / This guide
```

## 🚀 快速开始 / Quick Start

### 1. 安装依赖 / Install Dependencies

```bash
pip install streamlit plotly pandas numpy
```

### 2. 测试i18n功能 / Test i18n Functionality

```bash
# 运行i18n测试页面 / Run i18n test page
streamlit run test_i18n_gui.py

# 运行完整GUI应用 / Run full GUI application
streamlit run gui_app_enhanced.py
```

### 3. 语言切换 / Language Switching

- 在设置页面选择语言 / Select language in Settings page
- 使用语言选择器 / Use language selector
- 系统会自动重新加载界面 / System will automatically reload interface

## 💻 使用方法 / Usage

### 基本翻译 / Basic Translation

```python
from utils.i18n import t

# 简单翻译 / Simple translation
title = t('dashboard.title')

# 带参数的翻译 / Translation with parameters
message = t('dashboard.messages.data_updated', count=5)
```

### 语言管理 / Language Management

```python
from utils.i18n import get_i18n, set_language

# 获取i18n实例 / Get i18n instance
i18n = get_i18n()

# 切换语言 / Switch language
set_language('zh')  # 切换到中文 / Switch to Chinese
set_language('en')  # 切换到英文 / Switch to English

# 获取当前语言 / Get current language
current_lang = i18n.get_current_language()
```

### 创建语言选择器 / Create Language Selector

```python
from utils.i18n import create_language_selector

# 在Streamlit中创建语言选择器 / Create language selector in Streamlit
create_language_selector("my_language_selector")
```

### 数字格式化 / Number Formatting

```python
from utils.i18n import format_number

# 货币格式 / Currency format
price = format_number(1234.56, 'currency')  # $1,234.56 or ¥1,234.56

# 百分比格式 / Percentage format
rate = format_number(12.34, 'percentage')   # 12.34%

# 大数字格式 / Large number format
tvl = format_number(1500000000, 'large_number')  # 1.5B
```

## 📝 翻译文件结构 / Translation File Structure

### JSON文件格式 / JSON File Format

```json
{
  "app": {
    "title": "RWA Yield Optimizer",
    "subtitle": "Professional Real-World Assets Investment Analysis Platform"
  },
  "navigation": {
    "dashboard": "Real-Time Dashboard",
    "predictions": "AI Predictions"
  },
  "dashboard": {
    "title": "Real-Time Dashboard",
    "kpi": {
      "total_protocols": "Total Protocols",
      "average_apy": "Average APY"
    }
  }
}
```

### 键值命名规范 / Key Naming Convention

- 使用点号分隔的层级结构 / Use dot-separated hierarchical structure
- 小写字母和下划线 / Lowercase letters and underscores
- 描述性的键名 / Descriptive key names

示例 / Examples:
- `dashboard.title` - 仪表盘标题
- `settings.api.save_keys` - 设置页面API保存按钮
- `common.buttons.refresh` - 通用刷新按钮

## 🔧 高级配置 / Advanced Configuration

### 添加新语言 / Adding New Languages

1. **创建新的语言文件 / Create new language file**
   ```bash
   # 例如添加西班牙语 / For example, adding Spanish
   cp locales/en.json locales/es.json
   ```

2. **翻译内容 / Translate content**
   ```json
   {
     "app": {
       "title": "Optimizador de Rendimiento RWA"
     }
   }
   ```

3. **更新语言名称映射 / Update language name mapping**
   ```python
   # 在 utils/i18n.py 中添加 / Add in utils/i18n.py
   language_names = {
       'en': 'English',
       'zh': '中文',
       'es': 'Español'  # 新增 / New addition
   }
   ```

### 自定义格式化 / Custom Formatting

```python
class CustomI18nManager(I18nManager):
    def format_currency(self, amount, currency='USD'):
        """自定义货币格式化 / Custom currency formatting"""
        if self.current_language == 'zh':
            return f"¥{amount:,.2f}"
        elif currency == 'EUR':
            return f"€{amount:,.2f}"
        else:
            return f"${amount:,.2f}"
```

## 🧪 测试 / Testing

### 运行测试 / Run Tests

```bash
# 运行i18n功能测试 / Run i18n functionality test
streamlit run test_i18n_gui.py
```

### 测试内容 / Test Coverage

- ✅ 语言切换 / Language switching
- ✅ 翻译准确性 / Translation accuracy
- ✅ 缺失键处理 / Missing key handling
- ✅ 数字格式化 / Number formatting
- ✅ 会话状态保持 / Session state persistence

## 🐛 故障排除 / Troubleshooting

### 常见问题 / Common Issues

1. **翻译不显示 / Translations not showing**
   ```python
   # 检查语言文件是否存在 / Check if language files exist
   import os
   print(os.path.exists('locales/zh.json'))
   print(os.path.exists('locales/en.json'))
   ```

2. **语言切换不生效 / Language switching not working**
   ```python
   # 检查会话状态 / Check session state
   import streamlit as st
   print(st.session_state.get('language', 'Not set'))
   ```

3. **缺失翻译键 / Missing translation keys**
   ```python
   # 使用默认值 / Use default values
   text = t('missing.key', default='Default Text')
   ```

### 调试模式 / Debug Mode

```python
# 启用调试模式 / Enable debug mode
import logging
logging.basicConfig(level=logging.DEBUG)

# 查看翻译加载过程 / View translation loading process
i18n = get_i18n()
print(f"Available languages: {i18n.get_available_languages()}")
print(f"Current language: {i18n.get_current_language()}")
```

## 📈 性能优化 / Performance Optimization

### 翻译缓存 / Translation Caching

```python
from functools import lru_cache

class OptimizedI18nManager(I18nManager):
    @lru_cache(maxsize=1000)
    def get_text_cached(self, key_path: str) -> str:
        """缓存翻译结果 / Cache translation results"""
        return self.get_text(key_path)
```

### 延迟加载 / Lazy Loading

```python
def lazy_load_translations():
    """延迟加载翻译文件 / Lazy load translation files"""
    if not hasattr(st.session_state, 'i18n_loaded'):
        get_i18n()  # 初始化i18n / Initialize i18n
        st.session_state.i18n_loaded = True
```

## 🔮 未来计划 / Future Plans

### 待实现功能 / Planned Features

1. **更多语言支持 / More Language Support**
   - 🇪🇸 西班牙语 / Spanish
   - 🇫🇷 法语 / French
   - 🇩🇪 德语 / German
   - 🇯🇵 日语 / Japanese

2. **高级功能 / Advanced Features**
   - 复数形式处理 / Plural form handling
   - 日期时间本地化 / Date/time localization
   - RTL语言支持 / RTL language support
   - 翻译管理界面 / Translation management UI

3. **集成改进 / Integration Improvements**
   - 自动翻译检测 / Automatic translation detection
   - 翻译质量检查 / Translation quality checks
   - 批量翻译工具 / Batch translation tools

## 📞 支持 / Support

如果您在使用过程中遇到问题，请：
If you encounter issues during usage, please:

1. 查看本指南的故障排除部分 / Check the troubleshooting section of this guide
2. 运行测试文件验证功能 / Run test files to verify functionality
3. 检查控制台错误信息 / Check console error messages
4. 提交Issue到项目仓库 / Submit issues to the project repository

## 📄 许可证 / License

本项目采用MIT许可证 / This project is licensed under the MIT License.

---

**最后更新 / Last Updated:** 2024-01-10
**版本 / Version:** 1.0.0
**作者 / Author:** RWA Development Team