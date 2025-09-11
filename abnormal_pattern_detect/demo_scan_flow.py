#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
演示扫描器完整流程
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

def main():
    """演示完整流程"""
    print("🚀 异常模式检测扫描器演示")
    print("=" * 50)
    
    # 1. 生成扫描器
    print("\n🔧 步骤1: 生成扫描器")
    print("-" * 30)
    
    try:
        result = subprocess.run([sys.executable, "generate_scanner.py"], 
                              capture_output=True, text=True, 
                              cwd="/home/denerate/abnormal_pattern_detect")
        
        if result.returncode == 0:
            print("✅ 扫描器生成成功")
            print(result.stdout)
        else:
            print("❌ 扫描器生成失败")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ 生成扫描器异常: {e}")
        return False
    
    # 2. 检查生成的扫描器
    print("\n📋 步骤2: 检查生成的扫描器")
    print("-" * 30)
    
    scanners_dir = Path("/home/denerate/abnormal_pattern_detect/scanners")
    if scanners_dir.exists():
        scanner_files = [f for f in scanners_dir.iterdir() if f.is_file() and f.name.startswith('scan_') and f.name.endswith('.py')]
        print(f"📁 找到 {len(scanner_files)} 个扫描器:")
        for scanner in scanner_files:
            print(f"  - {scanner.name}")
    else:
        print("❌ scanners目录不存在")
        return False
    
    # 3. 执行扫描器
    print("\n🔍 步骤3: 执行扫描器")
    print("-" * 30)
    
    results_dir = scanners_dir / "results"
    results_dir.mkdir(exist_ok=True)
    
    # 选择第一个扫描器进行演示
    if scanner_files:
        demo_scanner = scanner_files[0]
        print(f"🔍 执行演示扫描器: {demo_scanner.name}")
        
        try:
            result = subprocess.run([sys.executable, demo_scanner.name], 
                                  capture_output=True, text=True, 
                                  cwd=scanners_dir, timeout=60)
            
            if result.returncode == 0:
                print("✅ 扫描器执行成功")
                print("📄 扫描输出:")
                print(result.stdout[-500:])  # 显示最后500字符
            else:
                print("❌ 扫描器执行失败")
                print(f"错误: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("⏰ 扫描器执行超时")
            return False
        except Exception as e:
            print(f"❌ 扫描器执行异常: {e}")
            return False
    else:
        print("❌ 没有可用的扫描器")
        return False
    
    # 4. 检查扫描结果
    print("\n💾 步骤4: 检查扫描结果")
    print("-" * 30)
    
    result_files = [f for f in results_dir.iterdir() if f.is_file() and f.name.startswith('scan_results_') and f.name.endswith('.json')]
    
    if result_files:
        # 获取最新的结果文件
        latest_file = max(result_files, key=lambda x: x.stat().st_mtime)
        print(f"📄 最新扫描结果: {latest_file.name}")
        
        try:
            with open(latest_file, 'r', encoding='utf-8') as f:
                result_data = json.load(f)
            
            # 显示结果摘要
            summary = result_data.get('summary', {})
            print(f"📊 扫描摘要:")
            print(f"  服务名: {result_data.get('service_name', 'unknown')}")
            print(f"  扫描状态: {summary.get('status', 'unknown')}")
            print(f"  异常数量: {summary.get('total_anomalies', 0)}")
            print(f"  严重度评分: {summary.get('severity_score', 0)}")
            print(f"  模式匹配: {summary.get('pattern_matches', 0)}")
            
            # 显示建议
            recommendations = summary.get('recommendations', [])
            if recommendations:
                print(f"💡 建议:")
                for rec in recommendations:
                    print(f"  - {rec}")
            
        except Exception as e:
            print(f"❌ 读取结果文件失败: {e}")
            return False
    else:
        print("❌ 没有找到扫描结果文件")
        return False
    
    # 5. 演示MCP协议集成
    print("\n🔗 步骤5: MCP协议集成演示")
    print("-" * 30)
    
    try:
        # 模拟MCP协议调用
        sys.path.append('/home/denerate/MCPArchieve/core')
        from mcp_protocols import AnomalyPatternDetectionProtocol
        
        anomaly_detect_path = "/home/denerate/abnormal_pattern_detect"
        
        # 获取可用扫描器
        available_scanners = AnomalyPatternDetectionProtocol._list_available_scanners(anomaly_detect_path)
        print(f"📋 MCP可用扫描器: {available_scanners.get('scanners', [])}")
        
        # 解析扫描结果
        service_name = result_data.get('service_name', 'unknown')
        scan_data = AnomalyPatternDetectionProtocol._parse_scan_results(anomaly_detect_path, service_name)
        
        if scan_data:
            print(f"✅ MCP成功解析 {service_name} 扫描结果")
            print(f"  解析到的数据字段: {list(scan_data.keys())}")
        else:
            print(f"⚠️ MCP解析 {service_name} 扫描结果失败")
        
    except Exception as e:
        print(f"❌ MCP协议集成演示失败: {e}")
        return False
    
    # 6. 总结
    print("\n🎯 演示总结")
    print("-" * 30)
    print("✅ 扫描器生成成功")
    print("✅ 扫描器执行成功")
    print("✅ 结果保存成功")
    print("✅ MCP协议集成成功")
    print("\n🎉 完整流程演示完成！")
    print("\n💡 现在您可以通过以下方式使用:")
    print("  1. 运行 'python generate_scanner.py' 生成扫描器")
    print("  2. 运行 'cd scanners && python scan_xxx.py' 执行特定扫描器")
    print("  3. 在MCP协议中使用 'analyze_existing_risks' 分析现有风险")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 