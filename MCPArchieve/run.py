#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能系统监控助手 - 智能启动脚本
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_dependencies():
    """检查依赖"""
    print("🔍 检查依赖...")
    
    try:
        import requests
        print("✅ requests 库可用")
    except ImportError:
        print("❌ 缺少 requests 库，请运行: pip3 install requests")
        return False
    
    try:
        import psutil
        print("✅ psutil 库可用")
    except ImportError:
        print("❌ 缺少 psutil 库，请运行: pip3 install psutil")
        return False
    
    return True

def check_gui_environment():
    """检查GUI环境"""
    try:
        from utils import UIUtils
        return UIUtils.check_gui_environment()
    except Exception:
        return False

def main():
    """主函数"""
    print("🚀 正在启动智能系统监控助手...")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 检查GUI环境
    if check_gui_environment():
        print("✅ GUI环境可用，启动桌面版本")
        print("=" * 50)
        print("功能特性:")
        print("• 智能系统监控 (CPU、内存、磁盘IO、网络等)")
        print("• 实时工具调用链显示")
        print("• 思考过程可视化")
        print("• 对话历史保存和加载")
        print("• 支持Windows IO监控和Prometheus监控")
        print("=" * 50)
        
        try:
            from apps.desktop_app import main as desktop_main
            desktop_main()
        except Exception as e:
            print(f"❌ 桌面版本启动失败: {e}")
            print("尝试启动命令行版本...")
            start_cli_version()
    else:
        print("⚠️ GUI环境不可用，启动命令行版本")
        start_cli_version()

def start_cli_version():
    """启动命令行版本"""
    print("=" * 50)
    print("启动命令行版本...")
    print("=" * 50)
    
    try:
        from apps.cli_app import main as cli_main
        cli_main()
    except Exception as e:
        print(f"❌ 命令行版本启动失败: {e}")
        print("请检查依赖和环境配置")
        sys.exit(1)

if __name__ == "__main__":
    main() 