            #!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web应用配置优化报告生成器
负责生成HTML格式的可视化报告
"""

import os
import json
import subprocess
from datetime import datetime
from typing import Dict, Any, List
import logging
from jinja2 import Template

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WebConfigReportGenerator:
    """Web应用配置优化报告生成器"""
    
    def __init__(self):
        self.html_template = self._get_html_template()
    
    def _get_html_template(self) -> str:
        """获取HTML报告模板"""
        return """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Web应用配置优化报告</title>
    <style>
        :root {
            --critical: #e74c3c;
            --high: #e67e22;
            --medium: #f1c40f;
            --low: #2ecc71;
            --bg-light: #f8f9fa;
            --border-color: #dee2e6;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: var(--bg-light);
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px 0;
            text-align: center;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .summary-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: white;
            padding: 25px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s;
        }
        
        .stat-card:hover {
            transform: translateY(-2px);
        }
        
        .critical-bg { 
            background: linear-gradient(135deg, #ff6b6b, #ee5a52);
            color: white;
        }
        
        .high-bg { 
            background: linear-gradient(135deg, #ffa726, #ff9800);
            color: white;
        }
        
        .medium-bg { 
            background: linear-gradient(135deg, #ffd54f, #ffc107);
            color: #333;
        }
        
        .low-bg { 
            background: linear-gradient(135deg, #66bb6a, #4caf50);
            color: white;
        }
        
        .stat-value {
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .stat-label {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .issues-container {
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        .issues-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 2px solid var(--border-color);
        }
        
        .issues-header h2 {
            font-size: 1.8em;
            color: #2c3e50;
        }
        
        .filter-buttons {
            display: flex;
            gap: 10px;
        }
        
        .filter-btn {
            padding: 8px 16px;
            border: none;
            border-radius: 20px;
            cursor: pointer;
            font-size: 0.9em;
            transition: all 0.2s;
        }
        
        .filter-btn.active {
            color: white;
        }
        
        .filter-btn.critical.active { background-color: var(--critical); }
        .filter-btn.high.active { background-color: var(--high); }
        .filter-btn.medium.active { background-color: var(--medium); }
        .filter-btn.low.active { background-color: var(--low); }
        
        .issue-card {
            background: white;
            border-radius: 8px;
            margin-bottom: 20px;
            border-left: 5px solid;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            transition: transform 0.2s;
        }
        
        .issue-card:hover {
            transform: translateX(5px);
        }
        
        .issue-card.critical { border-color: var(--critical); }
        .issue-card.high { border-color: var(--high); }
        .issue-card.medium { border-color: var(--medium); }
        .issue-card.low { border-color: var(--low); }
        
        .issue-header {
            padding: 20px;
            background: #f8f9fa;
            border-bottom: 1px solid var(--border-color);
        }
        
        .issue-title {
            font-size: 1.3em;
            font-weight: bold;
            margin-bottom: 8px;
            color: #2c3e50;
        }
        
        .issue-meta {
            display: flex;
            gap: 20px;
            font-size: 0.9em;
            color: #666;
        }
        
        .severity-badge {
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 0.8em;
            font-weight: bold;
            text-transform: uppercase;
        }
        
        .severity-badge.critical { background-color: var(--critical); color: white; }
        .severity-badge.high { background-color: var(--high); color: white; }
        .severity-badge.medium { background-color: var(--medium); color: #333; }
        .severity-badge.low { background-color: var(--low); color: white; }
        
        .issue-content {
            padding: 20px;
        }
        
        .config-comparison {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 15px;
        }
        
        .config-item {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
        }
        
        .config-label {
            font-weight: bold;
            color: #666;
            margin-bottom: 5px;
        }
        
        .config-value {
            font-size: 1.1em;
            color: #333;
        }
        
        .solution {
            background: #e8f5e8;
            border: 1px solid #4caf50;
            border-radius: 5px;
            padding: 15px;
            margin-top: 15px;
        }
        
        .solution h4 {
            color: #2e7d32;
            margin-bottom: 10px;
        }
        
        .solution pre {
            background: #f5f5f5;
            padding: 10px;
            border-radius: 3px;
            overflow-x: auto;
            font-size: 0.9em;
            line-height: 1.4;
        }
        
        .footer {
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            color: #666;
            border-top: 1px solid var(--border-color);
        }
        
        .no-issues {
            text-align: center;
            padding: 40px;
            color: #666;
        }
        
        .no-issues h3 {
            color: var(--low);
            margin-bottom: 10px;
        }
        
        @media (max-width: 768px) {
            .container { padding: 10px; }
            .summary-stats { grid-template-columns: repeat(2, 1fr); }
            .config-comparison { grid-template-columns: 1fr; }
            .filter-buttons { flex-wrap: wrap; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Web应用配置优化报告</h1>
            <p>生成时间: {{ timestamp }}</p>
            <p>目标URL: {{ target_url }}</p>
        </div>
        
        <div class="summary-stats">
            <div class="stat-card critical-bg">
                <div class="stat-value">{{ critical_count }}</div>
                <div class="stat-label">危急问题</div>
            </div>
            <div class="stat-card high-bg">
                <div class="stat-value">{{ high_count }}</div>
                <div class="stat-label">高危问题</div>
            </div>
            <div class="stat-card medium-bg">
                <div class="stat-value">{{ medium_count }}</div>
                <div class="stat-label">中等问题</div>
            </div>
            <div class="stat-card low-bg">
                <div class="stat-value">{{ low_count }}</div>
                <div class="stat-label">低危问题</div>
            </div>
        </div>
        
        <div class="issues-container">
            <div class="issues-header">
                <h2>优化建议</h2>
                <div class="filter-buttons">
                    <button class="filter-btn critical active" onclick="filterIssues('all')">全部</button>
                    <button class="filter-btn critical" onclick="filterIssues('critical')">危急</button>
                    <button class="filter-btn high" onclick="filterIssues('high')">高危</button>
                    <button class="filter-btn medium" onclick="filterIssues('medium')">中等</button>
                    <button class="filter-btn low" onclick="filterIssues('low')">低危</button>
                </div>
            </div>
            
            {% if suggestions %}
                {% for issue in suggestions %}
                <div class="issue-card {{ issue.severity }}" data-severity="{{ issue.severity }}">
                    <div class="issue-header">
                        <div class="issue-title">{{ issue.category }} · {{ issue.issue }}</div>
                        <div class="issue-meta">
                            <span class="severity-badge {{ issue.severity }}">{{ issue.severity }}</span>
                        </div>
                    </div>
                    <div class="issue-content">
                        {% if issue.current and issue.recommended %}
                        <div class="config-comparison">
                            <div class="config-item">
                                <div class="config-label">当前配置</div>
                                <div class="config-value">{{ issue.current }}</div>
                            </div>
                            <div class="config-item">
                                <div class="config-label">推荐配置</div>
                                <div class="config-value">{{ issue.recommended }}</div>
                            </div>
                        </div>
                        {% endif %}
                        
                        {% if issue.solution %}
                        <div class="solution">
                            <h4>解决方案:</h4>
                            <pre>{{ issue.solution }}</pre>
                        </div>
                        {% endif %}
                    </div>
                </div>
                {% endfor %}
            {% else %}
                <div class="no-issues">
                    <h3>🎉 恭喜！</h3>
                    <p>未发现需要优化的配置问题，您的Web应用配置已经很完善了！</p>
                </div>
            {% endif %}
        </div>
        
        <div class="footer">
            <p>本报告由Web应用配置优化检测工具生成</p>
            <p>建议定期运行检测以保持最佳配置状态</p>
        </div>
    </div>
    
    <script>
        function filterIssues(severity) {
            const issues = document.querySelectorAll('.issue-card');
            const buttons = document.querySelectorAll('.filter-btn');
            
            // 更新按钮状态
            buttons.forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            // 过滤问题
            issues.forEach(issue => {
                if (severity === 'all' || issue.dataset.severity === severity) {
                    issue.style.display = 'block';
                } else {
                    issue.style.display = 'none';
                }
            });
        }
        
        // 页面加载时高亮严重问题
        document.addEventListener('DOMContentLoaded', function() {
            const criticalIssues = document.querySelectorAll('.issue-card.critical');
            criticalIssues.forEach(issue => {
                issue.style.animation = 'pulse 2s infinite';
            });
        });
        
        // 添加脉冲动画
        const style = document.createElement('style');
        style.textContent = `
            @keyframes pulse {
                0% { box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); }
                50% { box-shadow: 0 2px 20px rgba(231, 76, 60, 0.3); }
                100% { box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); }
            }
        `;
        document.head.appendChild(style);
    </script>
</body>
</html>
        """
    
    def generate_html_report(self, analysis_data: Dict[str, Any], 
                           config_data: Dict[str, Any] = None) -> str:
        """生成HTML格式的报告"""
        logger.info("生成HTML报告...")
        
        try:
            # 准备模板数据
            template_data = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "target_url": config_data.get('target_url', '未知') if config_data else '未知',
                "critical_count": analysis_data.get('summary', {}).get('critical', 0),
                "high_count": analysis_data.get('summary', {}).get('high', 0),
                "medium_count": analysis_data.get('summary', {}).get('medium', 0),
                "low_count": analysis_data.get('summary', {}).get('low', 0),
                "suggestions": analysis_data.get('suggestions', [])
            }
            
            # 渲染模板
            template = Template(self.html_template)
            html_content = template.render(**template_data)
            
            return html_content
            
        except Exception as e:
            logger.error(f"生成HTML报告失败: {e}")
            raise
    
    def save_html_report(self, html_content: str, output_file: str = "web_config_report.html"):
        """保存HTML报告"""
        try:
            with open(output_file, "w", encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"HTML报告已保存到: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"保存HTML报告失败: {e}")
            raise
    
    def generate_markdown_report(self, analysis_data: Dict[str, Any], 
                               config_data: Dict[str, Any] = None) -> str:
        """生成Markdown格式的报告"""
        logger.info("生成Markdown报告...")
        
        try:
            summary = analysis_data.get('summary', {})
            suggestions = analysis_data.get('suggestions', [])
            
            markdown_content = f"""# Web应用配置优化报告

**生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**目标URL**: {config_data.get('target_url', '未知') if config_data else '未知'}

## 问题统计

| 严重性 | 数量 |
|--------|------|
| 危急 | {summary.get('critical', 0)} |
| 高危 | {summary.get('high', 0)} |
| 中等 | {summary.get('medium', 0)} |
| 低危 | {summary.get('low', 0)} |
| **总计** | **{summary.get('total', 0)}** |

## 优化建议

"""
            
            if suggestions:
                # 按严重性分组
                severity_groups = {
                    'critical': [],
                    'high': [],
                    'medium': [],
                    'low': []
                }
                
                for suggestion in suggestions:
                    severity = suggestion.get('severity', 'medium')
                    severity_groups[severity].append(suggestion)
                
                # 按严重性顺序输出
                for severity in ['critical', 'high', 'medium', 'low']:
                    group_suggestions = severity_groups[severity]
                    if group_suggestions:
                        severity_names = {
                            'critical': '危急',
                            'high': '高危',
                            'medium': '中等',
                            'low': '低危'
                        }
                        
                        markdown_content += f"\n### {severity_names[severity]}问题\n\n"
                        
                        for i, suggestion in enumerate(group_suggestions, 1):
                            markdown_content += f"#### {i}. {suggestion['category']} - {suggestion['issue']}\n\n"
                            
                            if suggestion.get('current') and suggestion.get('recommended'):
                                markdown_content += f"**当前配置**: {suggestion['current']}  \n"
                                markdown_content += f"**推荐配置**: {suggestion['recommended']}  \n\n"
                            
                            if suggestion.get('solution'):
                                markdown_content += f"**解决方案**:\n```\n{suggestion['solution']}\n```\n\n"
                            
                            markdown_content += "---\n\n"
            else:
                markdown_content += "\n🎉 **恭喜！未发现需要优化的配置问题，您的Web应用配置已经很完善了！**\n"
            
            return markdown_content
            
        except Exception as e:
            logger.error(f"生成Markdown报告失败: {e}")
            raise
    
    def save_markdown_report(self, markdown_content: str, output_file: str = "web_config_report.md"):
        """保存Markdown报告"""
        try:
            with open(output_file, "w", encoding='utf-8') as f:
                f.write(markdown_content)
            
            logger.info(f"Markdown报告已保存到: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"保存Markdown报告失败: {e}")
            raise

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Web应用配置优化报告生成器')
    parser.add_argument('--analysis', default='web_config_analysis.json',
                       help='分析报告文件')
    parser.add_argument('--config', default='web_config_report.json',
                       help='配置报告文件')
    parser.add_argument('--html-output', default='web_config_report.html',
                       help='HTML报告输出文件名')
    parser.add_argument('--markdown-output', default='web_config_report.md',
                       help='Markdown报告输出文件名')
    
    args = parser.parse_args()
    
    # 读取分析数据
    if not os.path.exists(args.analysis):
        print(f"错误: 分析报告文件不存在: {args.analysis}")
        return
    
    with open(args.analysis, 'r', encoding='utf-8') as f:
        analysis_data = json.load(f)
    
    # 读取配置数据（如果存在）
    config_data = None
    if os.path.exists(args.config):
        with open(args.config, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
    
    # 创建报告生成器
    generator = WebConfigReportGenerator()
    
    # 生成HTML报告
    html_content = generator.generate_html_report(analysis_data, config_data)
    generator.save_html_report(html_content, args.html_output)
    
    # 生成Markdown报告
    markdown_content = generator.generate_markdown_report(analysis_data, config_data)
    generator.save_markdown_report(markdown_content, args.markdown_output)
    
    print(f"报告生成完成！")
    print(f"HTML报告: {args.html_output}")
    print(f"Markdown报告: {args.markdown_output}")

if __name__ == "__main__":
    main() 