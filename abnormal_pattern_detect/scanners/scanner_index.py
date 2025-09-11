#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
扫描器索引 - 管理所有生成的扫描器
生成时间: 2025-08-13T02:09:27.904752
"""

import subprocess
import sys
from pathlib import Path


def run_scanner(scanner_name: str):
    """运行指定的扫描器"""
    scanner_path = Path(__file__).parent / f"{scanner_name}.py"
    
    if not scanner_path.exists():
        print(f"❌ 扫描器不存在: {scanner_path}")
        return False
    
    try:
        result = subprocess.run([sys.executable, str(scanner_path)], 
                              capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print(f"错误: {result.stderr}")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ 运行扫描器失败: {e}")
        return False


def run_all_scanners():
    """运行所有扫描器"""
    scanners = ['scan_system.py', 'scan_mysqld.py', 'scan_nginx.py', 'scan_python3.py', 'scan_mysql.py', 'scan_loki.py', 'scan_node_exporter.py', 'scan_promptail.py']
    
    print(f"🔍 开始运行 {len(scanners)} 个扫描器...")
    
    success_count = 0
    for scanner in scanners:
        scanner_name = scanner.replace('.py', '')
        print(f"\n==================================================")
        print(f"运行扫描器: {scanner_name}")
        print(f"==================================================")
        
        if run_scanner(scanner_name):
            success_count += 1
    
    print(f"\n📊 扫描完成: {success_count}/{len(scanners)} 个扫描器成功运行")


def list_scanners():
    """列出所有可用的扫描器"""
    scanners = ['scan_system.py', 'scan_mysqld.py', 'scan_nginx.py', 'scan_python3.py', 'scan_mysql.py', 'scan_loki.py', 'scan_node_exporter.py', 'scan_promptail.py']
    
    print("📋 可用的扫描器:")
    for i, scanner in enumerate(scanners, 1):
        scanner_name = scanner.replace('.py', '').replace('scan_', '')
        print(f"  {i}. {scanner_name} ({scanner})")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python scanner_index.py list           # 列出所有扫描器")
        print("  python scanner_index.py run <name>     # 运行指定扫描器")
        print("  python scanner_index.py run-all        # 运行所有扫描器")
        return
    
    command = sys.argv[1]
    
    if command == 'list':
        list_scanners()
    elif command == 'run' and len(sys.argv) > 2:
        scanner_name = sys.argv[2]
        run_scanner(scanner_name)
    elif command == 'run-all':
        run_all_scanners()
    else:
        print("❌ 无效的命令")


if __name__ == "__main__":
    main()
