#!/usr/bin/env python3
"""
运行脚本 - 快速启动异常检测与根因分析
"""

import subprocess
import sys
import os
import argparse


def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("❌ 需要Python 3.8或更高版本")
        sys.exit(1)
    print(f"✅ Python版本: {sys.version}")


def install_dependencies():
    """安装依赖包"""
    print("📦 安装依赖包...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ 依赖包安装完成")
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖包安装失败: {e}")
        sys.exit(1)


def check_config():
    """检查配置文件"""
    if not os.path.exists("config.yaml"):
        print("❌ 配置文件 config.yaml 不存在")
        sys.exit(1)
    print("✅ 配置文件检查通过")


def run_analysis():
    """运行分析程序"""
    print("🚀 启动分析程序...")
    try:
        subprocess.check_call([sys.executable, "main.py"])
    except subprocess.CalledProcessError as e:
        print(f"❌ 程序运行失败: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n❌ 用户中断程序")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="微服务异常检测与根因分析系统")
    parser.add_argument("--install-deps", action="store_true", help="安装依赖包")
    parser.add_argument("--skip-deps", action="store_true", help="跳过依赖检查")
    
    args = parser.parse_args()
    
    print("🎯 微服务异常检测与根因分析系统")
    print("=" * 50)
    
    # 检查Python版本
    check_python_version()
    
    # 安装依赖（如果需要）
    if args.install_deps or not args.skip_deps:
        install_dependencies()
    
    # 检查配置
    check_config()
    
    # 运行分析
    run_analysis()


if __name__ == "__main__":
    main()
