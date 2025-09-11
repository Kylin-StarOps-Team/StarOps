#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flet桌面应用启动脚本
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import flet as ft
from apps.flet_desktop_app import main

if __name__ == "__main__":
    print("🚀 正在启动 Flet 桌面应用...")
    print("📱 应用将在浏览器中打开...")
    
    try:
        # 启动 Flet 应用
        ft.app(target=main, view=ft.AppView.WEB_BROWSER)
        
    except KeyboardInterrupt:
        print("\n👋 应用已安全退出")
    except Exception as e:
        print(f"❌ 应用启动失败: {e}")
        print("请检查依赖是否安装完整")