#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyQt悬浮球应用依赖安装脚本
"""

import subprocess
import sys
import os

def run_command(command, description):
    """运行命令并显示结果"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description}成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description}失败: {e}")
        if e.stdout:
            print(f"输出: {e.stdout}")
        if e.stderr:
            print(f"错误: {e.stderr}")
        return False

def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    print(f"🐍 Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 6):
        print("❌ 需要Python 3.6或更高版本")
        return False
    
    print("✅ Python版本检查通过")
    return True

def install_pyqt5():
    """安装PyQt5"""
    print("📦 开始安装PyQt5...")
    
    # 尝试不同的安装方法
    install_commands = [
        "pip install PyQt5==5.15.10",
        "pip3 install PyQt5==5.15.10",
        "python -m pip install PyQt5==5.15.10",
        "python3 -m pip install PyQt5==5.15.10"
    ]
    
    for cmd in install_commands:
        if run_command(cmd, f"执行 {cmd}"):
            return True
    
    print("❌ PyQt5安装失败，请手动安装")
    return False

def install_requirements():
    """安装requirements文件中的依赖"""
    requirements_file = "requirements_pyqt.txt"
    
    if not os.path.exists(requirements_file):
        print(f"⚠️ 找不到依赖文件: {requirements_file}")
        return False
    
    print(f"📋 安装依赖文件: {requirements_file}")
    
    install_commands = [
        f"pip install -r {requirements_file}",
        f"pip3 install -r {requirements_file}",
        f"python -m pip install -r {requirements_file}",
        f"python3 -m pip install -r {requirements_file}"
    ]
    
    for cmd in install_commands:
        if run_command(cmd, f"执行 {cmd}"):
            return True
    
    print("❌ 依赖安装失败")
    return False

def test_pyqt5():
    """测试PyQt5是否可用"""
    print("🧪 测试PyQt5...")
    try:
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QPainter
        print("✅ PyQt5测试通过")
        return True
    except ImportError as e:
        print(f"❌ PyQt5测试失败: {e}")
        return False

def test_markdown():
    """测试Markdown是否可用"""
    print("🧪 测试Markdown支持...")
    try:
        import markdown
        from markdown.extensions import codehilite, tables, toc
        print("✅ Markdown支持测试通过")
        return True
    except ImportError as e:
        print(f"⚠️ Markdown支持测试失败: {e}")
        print("💡 这不是必需的，应用仍可正常运行")
        return False

def install_markdown():
    """安装Markdown相关依赖"""
    print("📦 安装Markdown支持...")
    
    packages = ["markdown", "pygments"]
    
    for package in packages:
        install_commands = [
            f"pip install {package}",
            f"pip3 install {package}",
            f"python -m pip install {package}",
            f"python3 -m pip install {package}"
        ]
        
        success = False
        for cmd in install_commands:
            if run_command(cmd, f"安装 {package}"):
                success = True
                break
        
        if not success:
            print(f"⚠️ {package} 安装失败，Markdown功能可能受限")
            return False
    
    return True

def main():
    """主函数"""
    print("🚀 智能系统监控助手 - PyQt依赖安装")
    print("=" * 50)
    
    # 检查Python版本
    if not check_python_version():
        sys.exit(1)
    
    # 检查是否已安装PyQt5
    if test_pyqt5():
        print("✅ PyQt5已安装，跳过安装步骤")
    else:
        # 安装PyQt5
        if not install_pyqt5():
            print("❌ 安装失败，请手动安装PyQt5")
            print("💡 手动安装命令:")
            print("   pip install PyQt5")
            sys.exit(1)
    
    # 测试安装结果
    if not test_pyqt5():
        print("❌ PyQt5安装后测试失败")
        sys.exit(1)
    
    # 安装Markdown支持（可选）
    print("\n📦 安装Markdown支持...")
    markdown_success = install_markdown()
    if markdown_success:
        test_markdown()
    
    # 安装其他依赖（可选）
    print("\n📦 安装其他依赖...")
    install_requirements()
    
    print("\n🎉 安装完成！")
    print("✅ PyQt5: 已安装")
    if markdown_success:
        print("✅ Markdown支持: 已安装")
    else:
        print("⚠️ Markdown支持: 未安装（可选功能）")
    print("\n💡 现在可以运行应用:")
    print("   python run_floating_ball.py")

if __name__ == "__main__":
    main()
