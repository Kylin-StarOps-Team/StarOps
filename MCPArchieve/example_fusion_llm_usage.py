#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fusion LLM异常检测使用示例
"""

import sys
import os
import json

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core import SmartMonitor
from utils import Config

def example_comprehensive_anomaly_detection():
    """示例：全面异常检测"""
    print("=" * 60)
    print("🔍 示例：全面异常检测")
    print("=" * 60)
    
    config = Config()
    monitor = SmartMonitor(config.api_key)
    
    question = "请帮我进行全面的异常检测分析，包括日志、指标和系统状态"
    
    print(f"🤔 用户问题: {question}")
    print("🤖 AI正在分析...")
    
    result = monitor.smart_query(question)
    
    if result["type"] == "mcp_analysis":
        mcp_result = result["mcp_result"]
        if mcp_result.get("status") == "success":
            analysis_result = mcp_result.get("analysis_result", {})
            
            print(f"\n📊 检测结果:")
            print(f"  摘要: {analysis_result.get('detection_summary', 'N/A')}")
            print(f"  风险等级: {analysis_result.get('overall_risk_level', 'N/A')}")
            
            statistics = analysis_result.get('statistics', {})
            print(f"\n📈 统计信息:")
            print(f"  总序列数: {statistics.get('total_sequences', 0)}")
            print(f"  异常数量: {statistics.get('anomaly_count', 0)}")
            print(f"  日志异常: {statistics.get('log_anomaly_count', 0)}")
            print(f"  指标异常: {statistics.get('metrics_anomaly_count', 0)}")
            print(f"  处理时间: {statistics.get('processing_time', 0):.2f}秒")
            
            recommendations = analysis_result.get('recommendations', [])
            print(f"\n💡 建议:")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")
            
            # 显示异常详情
            anomaly_details = analysis_result.get('anomaly_details', {})
            high_severity = anomaly_details.get('high_severity', [])
            medium_severity = anomaly_details.get('medium_severity', [])
            low_severity = anomaly_details.get('low_severity', [])
            
            if high_severity:
                print(f"\n🚨 高风险异常 ({len(high_severity)}个):")
                for anomaly in high_severity[:3]:  # 只显示前3个
                    print(f"  - 序列{anomaly.get('sequence_id')}: 分数{anomaly.get('anomaly_score', 0):.2f}")
            
            if medium_severity:
                print(f"\n⚠️ 中风险异常 ({len(medium_severity)}个):")
                for anomaly in medium_severity[:3]:  # 只显示前3个
                    print(f"  - 序列{anomaly.get('sequence_id')}: 分数{anomaly.get('anomaly_score', 0):.2f}")
        else:
            print(f"❌ 检测失败: {mcp_result.get('message', '未知错误')}")
    else:
        print(f"❌ 未检测到异常检测调用")

def example_logs_only_detection():
    """示例：仅日志异常检测"""
    print("\n" + "=" * 60)
    print("📝 示例：仅日志异常检测")
    print("=" * 60)
    
    config = Config()
    monitor = SmartMonitor(config.api_key)
    
    question = "请检测日志中的异常情况，分析错误模式和异常行为"
    
    print(f"🤔 用户问题: {question}")
    print("🤖 AI正在分析...")
    
    result = monitor.smart_query(question)
    
    if result["type"] == "mcp_analysis":
        mcp_result = result["mcp_result"]
        if mcp_result.get("status") == "success":
            analysis_result = mcp_result.get("analysis_result", {})
            
            print(f"\n📊 日志异常检测结果:")
            print(f"  摘要: {analysis_result.get('detection_summary', 'N/A')}")
            print(f"  风险等级: {analysis_result.get('overall_risk_level', 'N/A')}")
            
            statistics = analysis_result.get('statistics', {})
            print(f"\n📈 日志统计:")
            print(f"  总序列数: {statistics.get('total_sequences', 0)}")
            print(f"  日志异常: {statistics.get('log_anomaly_count', 0)}")
            print(f"  处理时间: {statistics.get('processing_time', 0):.2f}秒")
            
            recommendations = analysis_result.get('recommendations', [])
            print(f"\n💡 日志分析建议:")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")
        else:
            print(f"❌ 日志检测失败: {mcp_result.get('message', '未知错误')}")
    else:
        print(f"❌ 未检测到日志异常检测调用")

def example_metrics_only_detection():
    """示例：仅指标异常检测"""
    print("\n" + "=" * 60)
    print("📊 示例：仅指标异常检测")
    print("=" * 60)
    
    config = Config()
    monitor = SmartMonitor(config.api_key)
    
    question = "请分析性能指标的异常，包括CPU、内存、磁盘和网络指标"
    
    print(f"🤔 用户问题: {question}")
    print("🤖 AI正在分析...")
    
    result = monitor.smart_query(question)
    
    if result["type"] == "mcp_analysis":
        mcp_result = result["mcp_result"]
        if mcp_result.get("status") == "success":
            analysis_result = mcp_result.get("analysis_result", {})
            
            print(f"\n📊 指标异常检测结果:")
            print(f"  摘要: {analysis_result.get('detection_summary', 'N/A')}")
            print(f"  风险等级: {analysis_result.get('overall_risk_level', 'N/A')}")
            
            statistics = analysis_result.get('statistics', {})
            print(f"\n📈 指标统计:")
            print(f"  总序列数: {statistics.get('total_sequences', 0)}")
            print(f"  指标异常: {statistics.get('metrics_anomaly_count', 0)}")
            print(f"  处理时间: {statistics.get('processing_time', 0):.2f}秒")
            
            recommendations = analysis_result.get('recommendations', [])
            print(f"\n💡 指标分析建议:")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")
        else:
            print(f"❌ 指标检测失败: {mcp_result.get('message', '未知错误')}")
    else:
        print(f"❌ 未检测到指标异常检测调用")

def example_ai_anomaly_detection():
    """示例：AI智能异常检测"""
    print("\n" + "=" * 60)
    print("🤖 示例：AI智能异常检测")
    print("=" * 60)
    
    config = Config()
    monitor = SmartMonitor(config.api_key)
    
    question = "使用AI进行智能异常检测，帮我找出系统中的潜在问题"
    
    print(f"🤔 用户问题: {question}")
    print("🤖 AI正在分析...")
    
    result = monitor.smart_query(question)
    
    if result["type"] == "mcp_analysis":
        mcp_result = result["mcp_result"]
        if mcp_result.get("status") == "success":
            analysis_result = mcp_result.get("analysis_result", {})
            
            print(f"\n🤖 AI智能异常检测结果:")
            print(f"  摘要: {analysis_result.get('detection_summary', 'N/A')}")
            print(f"  风险等级: {analysis_result.get('overall_risk_level', 'N/A')}")
            
            # 显示异常详情
            anomaly_details = analysis_result.get('anomaly_details', {})
            high_severity = anomaly_details.get('high_severity', [])
            medium_severity = anomaly_details.get('medium_severity', [])
            low_severity = anomaly_details.get('low_severity', [])
            
            print(f"\n📊 异常分布:")
            print(f"  高风险: {len(high_severity)}个")
            print(f"  中风险: {len(medium_severity)}个")
            print(f"  低风险: {len(low_severity)}个")
            
            if high_severity:
                print(f"\n🚨 高风险异常详情:")
                for anomaly in high_severity[:2]:  # 显示前2个
                    print(f"  - 序列{anomaly.get('sequence_id')}:")
                    print(f"    异常分数: {anomaly.get('anomaly_score', 0):.2f}")
                    print(f"    置信度: {anomaly.get('confidence', 0):.2f}")
                    print(f"    时间戳: {anomaly.get('timestamp', 'N/A')}")
            
            recommendations = analysis_result.get('recommendations', [])
            print(f"\n💡 AI建议:")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")
        else:
            print(f"❌ AI检测失败: {mcp_result.get('message', '未知错误')}")
    else:
        print(f"❌ 未检测到AI异常检测调用")

def main():
    """主函数"""
    print("🚀 Fusion LLM异常检测使用示例")
    print("本示例展示了如何使用Fusion LLM异常检测功能")
    
    try:
        # 示例1: 全面异常检测
        example_comprehensive_anomaly_detection()
        
        # 示例2: 仅日志异常检测
        example_logs_only_detection()
        
        # 示例3: 仅指标异常检测
        example_metrics_only_detection()
        
        # 示例4: AI智能异常检测
        example_ai_anomaly_detection()
        
        print("\n" + "=" * 60)
        print("✅ 所有示例执行完成")
        print("=" * 60)
        print("\n📝 使用提示:")
        print("1. 在对话中使用'异常检测'、'全面异常检测分析'等关键词")
        print("2. 系统会自动调用Fusion LLM进行智能异常检测")
        print("3. 检测结果包含详细的风险分析和处理建议")
        print("4. 支持全面检测、仅日志检测、仅指标检测等多种模式")
        
    except Exception as e:
        print(f"❌ 示例执行失败: {str(e)}")
        print("请检查配置和依赖是否正确")

if __name__ == "__main__":
    main() 