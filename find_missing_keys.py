#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Find missing translation keys
查找缺失的翻译键
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
    print("🔍 查找缺失的翻译键")
    print("🔍 Finding Missing Translation Keys")
    print("=" * 50)
    
    # 从GUI代码中提取翻译键
    gui_file = "gui_app_enhanced.py"
    used_keys = extract_translation_keys_from_file(gui_file)
    
    # 加载翻译文件
    en_data = load_translation_file("locales/en.json")
    zh_data = load_translation_file("locales/zh.json")
    
    # 获取翻译文件中的所有键
    en_keys = get_nested_keys(en_data)
    zh_keys = get_nested_keys(zh_data)
    
    # 检查缺失的键
    missing_en = used_keys - en_keys
    missing_zh = used_keys - zh_keys
    
    print(f"📊 统计信息:")
    print(f"  - 代码中使用的键: {len(used_keys)}")
    print(f"  - 英文翻译文件中的键: {len(en_keys)}")
    print(f"  - 中文翻译文件中的键: {len(zh_keys)}")
    
    print(f"\n🔍 缺失的翻译键:")
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
    
    # 生成需要添加的键
    all_missing = missing_en | missing_zh
    
    if all_missing:
        print(f"\n🔧 需要添加的翻译键 ({len(all_missing)} 个):")
        print("-" * 40)
        
        for key in sorted(all_missing):
            # 根据键名推测可能的翻译
            key_parts = key.split('.')
            last_part = key_parts[-1]
            
            # 简单的翻译建议
            suggestions = {
                'title': ('Title', '标题'),
                'description': ('Description', '描述'),
                'name': ('Name', '名称'),
                'value': ('Value', '值'),
                'status': ('Status', '状态'),
                'type': ('Type', '类型'),
                'amount': ('Amount', '金额'),
                'date': ('Date', '日期'),
                'time': ('Time', '时间'),
                'user': ('User', '用户'),
                'data': ('Data', '数据'),
                'info': ('Information', '信息'),
                'error': ('Error', '错误'),
                'success': ('Success', '成功'),
                'warning': ('Warning', '警告'),
                'loading': ('Loading', '加载中'),
                'save': ('Save', '保存'),
                'cancel': ('Cancel', '取消'),
                'delete': ('Delete', '删除'),
                'edit': ('Edit', '编辑'),
                'add': ('Add', '添加'),
                'remove': ('Remove', '移除'),
                'update': ('Update', '更新'),
                'create': ('Create', '创建'),
                'submit': ('Submit', '提交'),
                'confirm': ('Confirm', '确认'),
                'close': ('Close', '关闭'),
                'open': ('Open', '打开'),
                'settings': ('Settings', '设置'),
                'config': ('Configuration', '配置'),
                'options': ('Options', '选项'),
                'parameters': ('Parameters', '参数'),
                'results': ('Results', '结果'),
                'analysis': ('Analysis', '分析'),
                'report': ('Report', '报告'),
                'export': ('Export', '导出'),
                'import': ('Import', '导入'),
            }
            
            en_suggestion = suggestions.get(last_part, ('', ''))[0] or f"[需要英文翻译 for {key}]"
            zh_suggestion = suggestions.get(last_part, ('', ''))[1] or f"[需要中文翻译 for {key}]"
            
            print(f"  {key}:")
            print(f"    EN: {en_suggestion}")
            print(f"    ZH: {zh_suggestion}")
    
    print(f"\n📈 翻译覆盖率:")
    print(f"  - 英文: {((len(used_keys) - len(missing_en)) / len(used_keys) * 100):.1f}%")
    print(f"  - 中文: {((len(used_keys) - len(missing_zh)) / len(used_keys) * 100):.1f}%")

if __name__ == "__main__":
    main()