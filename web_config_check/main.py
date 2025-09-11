#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web应用配置优化检测主控制脚本
整合配置采集、分析、报告生成等功能
"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime
from typing import Dict, Any

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from web_config_collector import WebConfigCollector
from web_config_analyzer import WebConfigAnalyzer
from report_generator import WebConfigReportGenerator

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('web_config_detection.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class WebConfigDetectionSystem:
    """Web应用配置优化检测系统"""
    
    def __init__(self, target_url: str = "http://localhost:8080"):
        self.target_url = target_url
        self.collector = WebConfigCollector(target_url)
        self.analyzer = WebConfigAnalyzer()
        self.report_generator = WebConfigReportGenerator()
        
        # 输出文件配置
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.config_file = f"web_config_report_{self.timestamp}.json"
        self.analysis_file = f"web_config_analysis_{self.timestamp}.json"
        self.html_report = f"web_config_report_{self.timestamp}.html"
        self.markdown_report = f"web_config_report_{self.timestamp}.md"
    
    def run_full_detection(self) -> Dict[str, Any]:
        """运行完整的检测流程"""
        logger.info("开始Web应用配置优化检测...")
        
        try:
            # 步骤1: 收集配置信息
            logger.info("步骤1: 收集配置信息")
            config_data = self.collector.collect_all_configs()
            self.collector.save_report(self.config_file)
            logger.info(f"配置信息已保存到: {self.config_file}")
            
            # 步骤2: 分析配置并生成优化建议
            logger.info("步骤2: 分析配置并生成优化建议")
            suggestions = self.analyzer.analyze_config(config_data)
            self.analyzer.save_analysis_report(self.analysis_file)
            logger.info(f"分析报告已保存到: {self.analysis_file}")
            
            # 步骤3: 生成可视化报告
            logger.info("步骤3: 生成可视化报告")
            analysis_data = {
                "summary": self.analyzer.get_summary_stats(),
                "suggestions": suggestions
            }
            
            # 生成HTML报告
            html_content = self.report_generator.generate_html_report(analysis_data, config_data)
            self.report_generator.save_html_report(html_content, self.html_report)
            
            # 生成Markdown报告
            markdown_content = self.report_generator.generate_markdown_report(analysis_data, config_data)
            self.report_generator.save_markdown_report(markdown_content, self.markdown_report)
            
            logger.info("检测完成！")
            
            # 返回结果摘要
            result = {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "target_url": self.target_url,
                "files": {
                    "config": self.config_file,
                    "analysis": self.analysis_file,
                    "html_report": self.html_report,
                    "markdown_report": self.markdown_report
                },
                "summary": self.analyzer.get_summary_stats()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"检测过程中发生错误: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def run_quick_detection(self) -> Dict[str, Any]:
        """运行快速检测（仅收集和分析，不生成详细报告）"""
        logger.info("开始快速检测...")
        
        try:
            # 收集配置信息
            config_data = self.collector.collect_all_configs()
            
            # 分析配置
            suggestions = self.analyzer.analyze_config(config_data)
            
            # 返回摘要
            summary = self.analyzer.get_summary_stats()
            
            logger.info("快速检测完成！")
            
            return {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "target_url": self.target_url,
                "summary": summary,
                "critical_issues": [s for s in suggestions if s['severity'] == 'critical'],
                "high_issues": [s for s in suggestions if s['severity'] == 'high']
            }
            
        except Exception as e:
            logger.error(f"快速检测过程中发生错误: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def run_security_check(self) -> Dict[str, Any]:
        """运行安全专项检查"""
        logger.info("开始安全专项检查...")
        
        try:
            # 收集安全相关信息
            security_data = {
                "security_headers": self.collector.check_security_headers(),
                "nginx": self.collector.collect_nginx_config(),
                "apache": self.collector.collect_apache_config()
            }
            
            # 分析安全配置
            suggestions = self.analyzer.analyze_config({"security_headers": security_data["security_headers"]})
            
            # 过滤安全相关建议
            security_suggestions = [s for s in suggestions if '安全' in s['category']]
            
            logger.info("安全专项检查完成！")
            
            return {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "target_url": self.target_url,
                "security_headers": security_data["security_headers"],
                "security_issues": security_suggestions,
                "security_score": self._calculate_security_score(security_data["security_headers"])
            }
            
        except Exception as e:
            logger.error(f"安全专项检查过程中发生错误: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def run_performance_check(self) -> Dict[str, Any]:
        """运行性能专项检查"""
        logger.info("开始性能专项检查...")
        
        try:
            # 收集性能相关信息
            performance_data = {
                "system": self.collector.collect_system_config(),
                "nginx": self.collector.collect_nginx_config(),
                "apache": self.collector.collect_apache_config(),
                "spring_boot": self.collector.collect_spring_boot_config(),
                "performance_metrics": self.collector.collect_performance_metrics(),
                "lighthouse": self.collector.run_lighthouse_audit()
            }
            
            # 分析性能配置
            suggestions = self.analyzer.analyze_config(performance_data)
            
            # 过滤性能相关建议
            performance_suggestions = [s for s in suggestions if '性能' in s['category']]
            
            logger.info("性能专项检查完成！")
            
            return {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "target_url": self.target_url,
                "performance_metrics": performance_data["performance_metrics"],
                "performance_issues": performance_suggestions,
                "lighthouse_score": self._extract_lighthouse_score(performance_data["lighthouse"])
            }
            
        except Exception as e:
            logger.error(f"性能专项检查过程中发生错误: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _calculate_security_score(self, security_headers: Dict[str, str]) -> int:
        """计算安全评分（0-100）"""
        if not security_headers:
            return 0
        
        score = 0
        total_headers = 8  # 总的安全头数量
        
        # 检查关键安全头
        critical_headers = [
            'Content-Security-Policy',
            'X-Frame-Options',
            'Strict-Transport-Security'
        ]
        
        for header in critical_headers:
            if security_headers.get(header) != '缺失':
                score += 20  # 每个关键安全头20分
        
        # 检查其他安全头
        other_headers = [
            'X-Content-Type-Options',
            'X-XSS-Protection',
            'Referrer-Policy',
            'Permissions-Policy',
            'Cache-Control'
        ]
        
        for header in other_headers:
            if security_headers.get(header) != '缺失':
                score += 8  # 每个其他安全头8分
        
        return min(score, 100)
    
    def _extract_lighthouse_score(self, lighthouse_data: Dict[str, Any]) -> Dict[str, float]:
        """提取Lighthouse评分"""
        if not lighthouse_data or 'categories' not in lighthouse_data:
            return {}
        
        scores = {}
        categories = lighthouse_data['categories']
        
        for category_name, category_data in categories.items():
            if 'score' in category_data:
                scores[category_name] = category_data['score']
        
        return scores
    
    def print_summary(self, result: Dict[str, Any]):
        """打印检测结果摘要"""
        if result['status'] == 'error':
            print(f"❌ 检测失败: {result['error']}")
            return
        
        print("\n" + "="*60)
        print("Web应用配置优化检测结果摘要")
        print("="*60)
        print(f"目标URL: {result['target_url']}")
        print(f"检测时间: {result['timestamp']}")
        
        if 'summary' in result:
            summary = result['summary']
            print(f"\n问题统计:")
            print(f"  危急: {summary.get('critical', 0)}")
            print(f"  高危: {summary.get('high', 0)}")
            print(f"  中等: {summary.get('medium', 0)}")
            print(f"  低危: {summary.get('low', 0)}")
            print(f"  总计: {summary.get('total', 0)}")
        
        if 'files' in result:
            print(f"\n生成文件:")
            for file_type, filename in result['files'].items():
                print(f"  {file_type}: {filename}")
        
        if 'security_score' in result:
            print(f"\n安全评分: {result['security_score']}/100")
        
        if 'lighthouse_score' in result:
            print(f"\nLighthouse评分:")
            for category, score in result['lighthouse_score'].items():
                print(f"  {category}: {score:.2f}")
        
        print("="*60)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Web应用配置优化检测系统')
    parser.add_argument('--url', default='http://localhost:8080',
                       help='目标Web应用URL')
    parser.add_argument('--mode', choices=['full', 'quick', 'security', 'performance'],
                       default='full', help='检测模式')
    parser.add_argument('--output-dir', default='./reports',
                       help='输出目录')
    parser.add_argument('--no-report', action='store_true',
                       help='不生成详细报告（仅适用于full模式）')
    
    args = parser.parse_args()
    
    # 创建输出目录
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    
    # 切换到输出目录
    os.chdir(args.output_dir)
    
    # 创建检测系统
    detection_system = WebConfigDetectionSystem(args.url)
    
    # 根据模式运行检测
    if args.mode == 'full':
        if args.no_report:
            result = detection_system.run_quick_detection()
        else:
            result = detection_system.run_full_detection()
    elif args.mode == 'quick':
        result = detection_system.run_quick_detection()
    elif args.mode == 'security':
        result = detection_system.run_security_check()
    elif args.mode == 'performance':
        result = detection_system.run_performance_check()
    
    # 打印结果摘要
    detection_system.print_summary(result)
    
    # 返回状态码
    if result['status'] == 'error':
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main() 