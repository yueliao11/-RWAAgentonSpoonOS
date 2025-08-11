#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract all translation keys from GUI code and check which ones are missing
从GUI代码中提取所有翻译键并检查哪些缺失
"""

import re
import json
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def extract_translation_keys_from_file(file_path):
    """从文件中提取所有翻译键"""
    keys = set()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 匹配 t("key") 和 t('key') 格式
        patterns = [
            r't\(["\']([^"\']+)["\']\)',  # t("key") or t('key')
            r't\(["\']([^"\']+)["\']\s*,',  # t("key", ...) with parameters
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            keys.update(matches)
        
        return keys
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return set()

def load_translation_file(file_path):
    """加载翻译文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return {}

def get_nested_keys(data, prefix=""):
    """递归获取嵌套字典的所有键"""
    keys = set()
    
    for key, value in data.items():
        full_key = f"{prefix}.{key}" if prefix else key
        keys.add(full_key)
        
        if isinstance(value, dict):
            keys.update(get_nested_keys(value, full_key))
    
    return keys

def main():
    print("🔍 提取翻译键并检查缺失项")
    print("🔍 Extracting Translation Keys and Checking Missing Items")
    print("=" * 60)
    
    # 从GUI代码中提取翻译键
    gui_file = "gui_app_enhanced.py"
    used_keys = extract_translation_keys_from_file(gui_file)
    
    print(f"📝 从 {gui_file} 中找到 {len(used_keys)} 个翻译键:")
    for key in sorted(used_keys):
        print(f"  - {key}")
    
    print("\n" + "=" * 60)
    
    # 加载翻译文件
    en_data = load_translation_file("locales/en.json")
    zh_data = load_translation_file("locales/zh.json")
    
    # 获取翻译文件中的所有键
    en_keys = get_nested_keys(en_data)
    zh_keys = get_nested_keys(zh_data)
    
    print(f"📁 英文翻译文件中有 {len(en_keys)} 个键")
    print(f"📁 中文翻译文件中有 {len(zh_keys)} 个键")
    
    # 检查缺失的键
    missing_en = used_keys - en_keys
    missing_zh = used_keys - zh_keys
    
    print("\n🔍 缺失的翻译键分析:")
    print("-" * 40)
    
    if missing_en:
        print(f"❌ 英文翻译文件中缺失 {len(missing_en)} 个键:")
        for key in sorted(missing_en):
            print(f"  - {key}")
    else:
        print("✅ 英文翻译文件完整")
    
    print()
    
    if missing_zh:
        print(f"❌ 中文翻译文件中缺失 {len(missing_zh)} 个键:")
        for key in sorted(missing_zh):
            print(f"  - {key}")
    else:
        print("✅ 中文翻译文件完整")
    
    # 检查多余的键
    extra_en = en_keys - used_keys
    extra_zh = zh_keys - used_keys
    
    print("\n📊 多余的翻译键分析:")
    print("-" * 40)
    
    if extra_en:
        print(f"ℹ️  英文翻译文件中有 {len(extra_en)} 个未使用的键:")
        for key in sorted(extra_en):
            print(f"  - {key}")
    else:
        print("✅ 英文翻译文件无多余键")
    
    print()
    
    if extra_zh:
        print(f"ℹ️  中文翻译文件中有 {len(extra_zh)} 个未使用的键:")
        for key in sorted(extra_zh):
            print(f"  - {key}")
    else:
        print("✅ 中文翻译文件无多余键")
    
    # 生成缺失键的建议
    if missing_en or missing_zh:
        print("\n🔧 修复建议:")
        print("-" * 40)
        
        all_missing = missing_en | missing_zh
        
        print("需要添加的翻译键:")
        for key in sorted(all_missing):
            print(f"  {key}:")
            print(f"    EN: [需要英文翻译]")
            print(f"    ZH: [需要中文翻译]")
    
    print(f"\n📈 总结:")
    print(f"  - 代码中使用的键: {len(used_keys)}")
    print(f"  - 英文翻译覆盖率: {((len(used_keys) - len(missing_en)) / len(used_keys) * 100):.1f}%")
    print(f"  - 中文翻译覆盖率: {((len(used_keys) - len(missing_zh)) / len(used_keys) * 100):.1f}%")

if __name__ == "__main__":
    main()