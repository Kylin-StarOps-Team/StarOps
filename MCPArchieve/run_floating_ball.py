#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能系统监控助手 - PyQt悬浮球应用启动脚本
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_pyqt5():
    """检查PyQt5是否可用"""
    try:
        from PyQt5.QtWidgets import QApplication
        return True
    except ImportError:
        return False

def run_demo_version():
    """运行简化演示版本"""
    try:
        from apps.simple_floating_ball_demo import main as demo_main
        print("🎯 启动简化演示版本")
        demo_main()
    except Exception as e:
        print(f"❌ 演示版本启动失败: {e}")
        sys.exit(1)

def run_full_version():
    """运行完整版本"""
    try:
        from apps.floating_ball_qt import main
        print("🚀 启动完整版本")
        main()
    except Exception as e:
        print(f"❌ 完整版本启动失败: {e}")
        print("🔄 尝试启动演示版本...")
        run_demo_version()

if __name__ == "__main__":
    print("🎯 智能系统监控助手 - PyQt悬浮球版本")
    print("=" * 50)
    
    # 检查PyQt5环境
    if not check_pyqt5():
        print("❌ PyQt5未安装或不可用")
        print("💡 请安装PyQt5依赖:")
        print("   pip install PyQt5")
        print("   或")
        print("   pip install -r requirements_pyqt.txt")
        sys.exit(1)
    
    # 检查核心模块
    try:
        from core import SmartMonitor
        from utils import Config, HistoryManager
        print("✅ 核心模块检查通过")
    except ImportError as e:
        print(f"⚠️ 核心模块导入警告: {e}")
        print("🔄 将启动简化演示版本")
        run_demo_version()
        sys.exit(0)
    
    print("📱 悬浮球将出现在屏幕右侧")
    print("🖱️ 点击悬浮球展开聊天界面")
    print("🖼️ 右键点击系统托盘图标查看更多选项")
    print("⚠️ 关闭聊天界面后悬浮球会重新显示")
    print("-" * 50)
    
    # 启动应用
    run_full_version()
