#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
异常模式检测使用示例
演示如何通过智能监控器调用异常模式检测功能
"""

import sys
import os
import json
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.smart_monitor import SmartMonitor

def simulate_user_queries():
    """模拟用户查询异常模式检测相关的问题"""
    
    # 创建智能监控器实例
    monitor = SmartMonitor("your_api_key_here")
    
    # 示例查询列表
    queries = [
        "帮我检测MySQL服务的异常模式",
        "检查系统是否有异常行为",
        "扫描Nginx服务的日志异常",
        "查看可用的异常检测扫描器",
        "运行完整的异常模式检测流程",
        "分析Loki日志系统的异常情况"
    ]
    
    print("🤖 异常模式检测功能演示")
    print("=" * 60)
    print("时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print()
    
    for i, query in enumerate(queries, 1):
        print(f"📝 用户查询 {i}: {query}")
        print("-" * 50)
        
        try:
            # 调用智能监控器处理查询
            response = monitor.smart_query(query)
            
            # 检查是否触发了MCP协议调用
            if "[MCP_CALL]" in response:
                print("✅ 检测到MCP协议调用")
                # 提取协议调用信息
                import re
                mcp_match = re.search(r'\[MCP_CALL\](\{.*?\})\[/MCP_CALL\]', response, re.DOTALL)
                if mcp_match:
                    mcp_data = json.loads(mcp_match.group(1))
                    protocol = mcp_data.get("protocol")
                    params = mcp_data.get("params", {})
                    print(f"🔧 协议: {protocol}")
                    print(f"📋 参数: {json.dumps(params, ensure_ascii=False, indent=2)}")
                    
                    # 执行协议
                    if protocol == "AnomalyPatternDetectionProtocol":
                        result = monitor._execute_mcp_protocol(protocol, params)
                        print(f"📊 执行结果: {result['status']}")
                        if result['status'] == 'success':
                            if 'anomaly_analysis' in result:
                                analysis = result['anomaly_analysis']
                                print(f"🚨 异常评分: {analysis['severity_score']}/10")
                                print(f"⚠️ 异常等级: {analysis['severity_level']}")
                                print(f"🔍 异常数量: {analysis['total_anomalies']}")
                            elif 'summary' in result:
                                summary = result['summary']
                                if 'scanners_available' in summary:
                                    print(f"📁 可用扫描器: {summary['scanners_available']}")
                                if 'patterns_extracted' in summary:
                                    print(f"🔍 提取模式: {summary['patterns_extracted']}")
                        else:
                            print(f"❌ 执行失败: {result['message']}")
            else:
                print("💬 AI响应: 未触发MCP协议调用")
                print(f"回复: {response[:200]}...")
                
        except Exception as e:
            print(f"❌ 处理查询时出错: {str(e)}")
        
        print("\n" + "=" * 60 + "\n")

def demonstrate_direct_protocol_calls():
    """演示直接调用异常模式检测协议"""
    
    from core.mcp_protocols import AnomalyPatternDetectionProtocol
    
    print("🔧 直接协议调用演示")
    print("=" * 60)
    
    # 演示1: 获取系统状态
    print("📊 1. 获取异常模式检测系统状态")
    result = AnomalyPatternDetectionProtocol.execute({"action": "status"})
    print(f"状态: {result['status']}")
    if result['status'] == 'success':
        files = result['generated_files']
        print(f"数据文件: {len(files.get('data', []))} 个")
        print(f"扫描器: {len(files.get('scanners', []))} 个")
    
    print()
    
    # 演示2: 列出可用扫描器
    print("🔍 2. 列出可用扫描器")
    result = AnomalyPatternDetectionProtocol.execute({"action": "list_scanners"})
    print(f"状态: {result['status']}")
    if result['status'] == 'success':
        print(f"总扫描器数量: {result['total_scanners']}")
        for scanner in result['scanners'][:3]:  # 显示前3个
            print(f"  - {scanner['file']} ({scanner['service']})")
    
    print()
    
    # 演示3: 运行MySQL扫描器
    print("🔍 3. 运行MySQL服务扫描器")
    result = AnomalyPatternDetectionProtocol.execute({
        "action": "run_scanner",
        "service": "mysql",
        "scanner_type": "logs"
    })
    print(f"状态: {result['status']}")
    if result['status'] == 'success':
        analysis = result['anomaly_analysis']
        print(f"异常评分: {analysis['severity_score']}/10")
        print(f"异常等级: {analysis['severity_level']}")
        print(f"异常数量: {analysis['total_anomalies']}")
    else:
        print(f"错误: {result['message']}")

def show_integration_summary():
    """显示集成总结"""
    
    print("\n📋 异常模式检测集成总结")
    print("=" * 60)
    
    print("✅ 已完成的集成:")
    print("  1. 新增 AnomalyPatternDetectionProtocol 协议")
    print("  2. 注册到智能监控器")
    print("  3. 支持多种操作类型")
    print("  4. 提供异常分析评分")
    print("  5. 创建测试和文档")
    
    print("\n🔧 支持的操作:")
    print("  - run_pipeline: 运行完整流程")
    print("  - run_scanner: 运行特定扫描器")
    print("  - status: 获取系统状态")
    print("  - list_scanners: 列出可用扫描器")
    
    print("\n🎯 支持的服务:")
    print("  - MySQL 数据库")
    print("  - Nginx Web服务器")
    print("  - System 系统服务")
    print("  - Loki 日志系统")
    print("  - Promtail 日志收集器")
    print("  - Node Exporter 监控代理")
    
    print("\n📁 相关文件:")
    print("  - core/mcp_protocols.py: 协议实现")
    print("  - core/smart_monitor.py: 智能监控器")
    print("  - test_anomaly_detection_integration.py: 测试脚本")
    print("  - ANOMALY_DETECTION_INTEGRATION.md: 集成文档")
    print("  - example_anomaly_detection_usage.py: 使用示例")

if __name__ == "__main__":
    print("🚀 异常模式检测功能演示")
    print("=" * 60)
    
    # 选择演示模式
    print("请选择演示模式:")
    print("1. 模拟用户查询 (智能监控器自动调用)")
    print("2. 直接协议调用演示")
    print("3. 显示集成总结")
    print("4. 全部演示")
    
    try:
        choice = input("请输入选择 (1-4): ").strip()
        
        if choice == "1":
            simulate_user_queries()
        elif choice == "2":
            demonstrate_direct_protocol_calls()
        elif choice == "3":
            show_integration_summary()
        elif choice == "4":
            simulate_user_queries()
            print("\n" + "=" * 60 + "\n")
            demonstrate_direct_protocol_calls()
            print("\n" + "=" * 60 + "\n")
            show_integration_summary()
        else:
            print("无效选择，运行默认演示...")
            demonstrate_direct_protocol_calls()
            
    except KeyboardInterrupt:
        print("\n\n👋 演示已取消")
    except Exception as e:
        print(f"\n❌ 演示过程中出错: {str(e)}")
    
    print("\n🎉 演示完成！") 