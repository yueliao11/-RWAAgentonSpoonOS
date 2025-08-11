#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RWA Yield Optimizer GUI i18n Test Runner
RWA收益优化器GUI国际化测试运行器

This script provides a simple way to test the i18n functionality
本脚本提供了一个简单的方式来测试国际化功能
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_dependencies():
    """检查依赖项 / Check dependencies"""
    required_packages = [
        'streamlit',
        'plotly', 
        'pandas',
        'numpy'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} - 已安装 / Installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - 缺失 / Missing")
    
    if missing_packages:
        print(f"\n⚠️  缺失依赖项 / Missing dependencies: {', '.join(missing_packages)}")
        print("请运行 / Please run: pip install " + " ".join(missing_packages))
        return False
    
    return True

def check_i18n_files():
    """检查i18n文件 / Check i18n files"""
    required_files = [
        'locales/en.json',
        'locales/zh.json',
        'utils/i18n.py'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} - 存在 / Exists")
        else:
            missing_files.append(file_path)
            print(f"❌ {file_path} - 缺失 / Missing")
    
    if missing_files:
        print(f"\n⚠️  缺失文件 / Missing files: {', '.join(missing_files)}")
        return False
    
    return True

def validate_translation_files():
    """验证翻译文件 / Validate translation files"""
    try:
        # Check English translations
        with open('locales/en.json', 'r', encoding='utf-8') as f:
            en_data = json.load(f)
        print("✅ locales/en.json - JSON格式正确 / Valid JSON format")
        
        # Check Chinese translations  
        with open('locales/zh.json', 'r', encoding='utf-8') as f:
            zh_data = json.load(f)
        print("✅ locales/zh.json - JSON格式正确 / Valid JSON format")
        
        # Basic structure validation
        required_sections = ['app', 'navigation', 'dashboard', 'settings', 'common']
        
        for section in required_sections:
            if section in en_data and section in zh_data:
                print(f"✅ {section} - 两种语言都存在 / Present in both languages")
            else:
                print(f"⚠️  {section} - 可能缺失某种语言 / May be missing in some language")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON格式错误 / JSON format error: {e}")
        return False
    except Exception as e:
        print(f"❌ 验证错误 / Validation error: {e}")
        return False

def run_i18n_test():
    """运行i18n测试 / Run i18n test"""
    print("🚀 启动i18n测试页面 / Starting i18n test page...")
    print("📝 测试页面将在浏览器中打开 / Test page will open in browser")
    print("🔄 使用Ctrl+C停止服务器 / Use Ctrl+C to stop server")
    print("-" * 50)
    
    try:
        # Run streamlit app
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 
            'test_i18n_gui.py',
            '--server.port=8502',
            '--server.headless=false'
        ])
    except KeyboardInterrupt:
        print("\n👋 测试结束 / Test completed")
    except Exception as e:
        print(f"❌ 运行错误 / Runtime error: {e}")

def run_full_gui():
    """运行完整GUI / Run full GUI"""
    print("🚀 启动完整RWA GUI应用 / Starting full RWA GUI application...")
    print("📝 应用将在浏览器中打开 / Application will open in browser")
    print("🔄 使用Ctrl+C停止服务器 / Use Ctrl+C to stop server")
    print("-" * 50)
    
    try:
        # Run streamlit app
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 
            'gui_app_enhanced.py',
            '--server.port=8501',
            '--server.headless=false'
        ])
    except KeyboardInterrupt:
        print("\n👋 应用结束 / Application completed")
    except Exception as e:
        print(f"❌ 运行错误 / Runtime error: {e}")

def show_menu():
    """显示菜单 / Show menu"""
    print("=" * 60)
    print("🌐 RWA Yield Optimizer GUI - i18n Test Runner")
    print("🌐 RWA收益优化器GUI - 国际化测试运行器")
    print("=" * 60)
    print()
    print("请选择操作 / Please select an option:")
    print("1. 🧪 运行i18n功能测试 / Run i18n functionality test")
    print("2. 🚀 运行完整GUI应用 / Run full GUI application")
    print("3. 🔍 检查系统状态 / Check system status")
    print("4. 📖 查看帮助信息 / View help information")
    print("5. ❌ 退出 / Exit")
    print()

def check_system_status():
    """检查系统状态 / Check system status"""
    print("🔍 检查系统状态 / Checking system status...")
    print("-" * 40)
    
    # Check dependencies
    print("📦 检查依赖项 / Checking dependencies:")
    deps_ok = check_dependencies()
    print()
    
    # Check i18n files
    print("📁 检查i18n文件 / Checking i18n files:")
    files_ok = check_i18n_files()
    print()
    
    # Validate translation files
    print("🌐 验证翻译文件 / Validating translation files:")
    translations_ok = validate_translation_files()
    print()
    
    # Overall status
    if deps_ok and files_ok and translations_ok:
        print("✅ 系统状态良好，可以运行测试 / System status good, ready to run tests")
    else:
        print("⚠️  系统存在问题，请先解决上述问题 / System has issues, please resolve above problems first")

def show_help():
    """显示帮助信息 / Show help information"""
    print("📖 帮助信息 / Help Information")
    print("-" * 40)
    print()
    print("🌐 国际化功能说明 / i18n Functionality:")
    print("• 支持中英文切换 / Supports Chinese-English switching")
    print("• JSON配置文件 / JSON configuration files")
    print("• 智能翻译回退 / Smart translation fallback")
    print("• 数字格式化 / Number formatting")
    print()
    print("📁 重要文件 / Important Files:")
    print("• locales/en.json - 英文翻译 / English translations")
    print("• locales/zh.json - 中文翻译 / Chinese translations")
    print("• utils/i18n.py - i18n工具类 / i18n utility class")
    print("• test_i18n_gui.py - 测试页面 / Test page")
    print("• gui_app_enhanced.py - 主应用 / Main application")
    print()
    print("🚀 快速开始 / Quick Start:")
    print("1. 确保所有依赖已安装 / Ensure all dependencies are installed")
    print("2. 运行选项1测试i18n功能 / Run option 1 to test i18n functionality")
    print("3. 运行选项2使用完整应用 / Run option 2 to use full application")
    print()
    print("🐛 故障排除 / Troubleshooting:")
    print("• 检查Python版本 >= 3.7 / Check Python version >= 3.7")
    print("• 安装缺失的依赖项 / Install missing dependencies")
    print("• 确保文件路径正确 / Ensure file paths are correct")

def main():
    """主函数 / Main function"""
    while True:
        show_menu()
        
        try:
            choice = input("请输入选择 / Enter your choice (1-5): ").strip()
            
            if choice == '1':
                print("\n🧪 准备运行i18n测试 / Preparing to run i18n test...")
                if check_system_status():
                    input("\n按Enter继续 / Press Enter to continue...")
                    run_i18n_test()
                else:
                    input("\n请先解决系统问题，按Enter返回菜单 / Please resolve system issues first, press Enter to return to menu...")
                    
            elif choice == '2':
                print("\n🚀 准备运行完整GUI / Preparing to run full GUI...")
                if check_system_status():
                    input("\n按Enter继续 / Press Enter to continue...")
                    run_full_gui()
                else:
                    input("\n请先解决系统问题，按Enter返回菜单 / Please resolve system issues first, press Enter to return to menu...")
                    
            elif choice == '3':
                print()
                check_system_status()
                input("\n按Enter返回菜单 / Press Enter to return to menu...")
                
            elif choice == '4':
                print()
                show_help()
                input("\n按Enter返回菜单 / Press Enter to return to menu...")
                
            elif choice == '5':
                print("\n👋 再见！/ Goodbye!")
                break
                
            else:
                print("\n❌ 无效选择，请输入1-5 / Invalid choice, please enter 1-5")
                input("按Enter继续 / Press Enter to continue...")
                
        except KeyboardInterrupt:
            print("\n\n👋 程序被中断，再见！/ Program interrupted, goodbye!")
            break
        except Exception as e:
            print(f"\n❌ 发生错误 / Error occurred: {e}")
            input("按Enter继续 / Press Enter to continue...")

if __name__ == "__main__":
    main()