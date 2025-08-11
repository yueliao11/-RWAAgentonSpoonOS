#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test GUI translations using Playwright
使用Playwright测试GUI翻译功能
"""

import sys
import os
import subprocess
import time
import signal

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def start_streamlit_app():
    """启动Streamlit应用"""
    print("🚀 启动Streamlit应用...")
    process = subprocess.Popen([
        'streamlit', 'run', 'gui_app_enhanced.py', 
        '--server.port', '8502',
        '--server.headless', 'true'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # 等待应用启动
    time.sleep(8)
    return process

def stop_streamlit_app(process):
    """停止Streamlit应用"""
    print("🛑 停止Streamlit应用...")
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()

def test_translations_with_playwright():
    """使用Playwright测试翻译"""
    from playwright.sync_api import sync_playwright
    
    print("🎭 启动Playwright测试...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            # 导航到应用
            print("📍 导航到应用...")
            page.goto("http://localhost:8502")
            page.wait_for_timeout(3000)
            
            # 截图
            page.screenshot(path="gui_translation_test.png", full_page=True)
            print("📸 截图已保存: gui_translation_test.png")
            
            # 获取页面内容
            content = page.content()
            
            # 检查是否包含未翻译的键
            untranslated_keys = [
                '{t("settings.description")}',
                '{t("predictions.description")}', 
                '{t("dashboard.description")}'
            ]
            
            found_issues = []
            for key in untranslated_keys:
                if key in content:
                    found_issues.append(key)
            
            if found_issues:
                print("❌ 发现未翻译的键:")
                for issue in found_issues:
                    print(f"  - {issue}")
                return False
            else:
                print("✅ 所有翻译键都已正确处理")
                return True
                
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            return False
        finally:
            browser.close()

def main():
    """主函数"""
    print("🌐 GUI翻译功能测试")
    print("=" * 50)
    
    # 检查是否安装了playwright
    try:
        import playwright
        print("✅ Playwright已安装")
    except ImportError:
        print("❌ 请先安装Playwright: pip install playwright")
        print("   然后运行: playwright install")
        return False
    
    # 启动应用
    app_process = start_streamlit_app()
    
    try:
        # 运行测试
        success = test_translations_with_playwright()
        
        if success:
            print("\n🎉 翻译测试通过！")
        else:
            print("\n❌ 翻译测试失败！")
            
        return success
        
    finally:
        # 停止应用
        stop_streamlit_app(app_process)

if __name__ == "__main__":
    main()