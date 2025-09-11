#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web应用配置分析器
负责分析配置数据并生成优化建议
"""

import os
import json
import subprocess
import re
from typing import Dict, Any, List, Optional
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WebConfigAnalyzer:
    """Web应用配置分析器"""
    
    def __init__(self):
        self.suggestions = []
        self.critical_count = 0
        self.high_count = 0
        self.medium_count = 0
        self.low_count = 0
    
    def analyze_config(self, config_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """分析配置数据并生成优化建议"""
        logger.info("开始分析Web应用配置...")
        
        self.suggestions = []
        self.critical_count = 0
        self.high_count = 0
        self.medium_count = 0
        self.low_count = 0
        
        try:
            # 系统级配置分析
            if config_data.get('system'):
                self._analyze_system_config(config_data['system'])
            
            # Nginx配置分析
            if config_data.get('nginx'):
                self._analyze_nginx_config(config_data['nginx'], config_data.get('system', {}))
            
            # Apache配置分析
            if config_data.get('apache'):
                self._analyze_apache_config(config_data['apache'])
            
            # Spring Boot配置分析
            if config_data.get('spring_boot'):
                self._analyze_spring_boot_config(config_data['spring_boot'])
            
            # Django配置分析
            if config_data.get('django'):
                self._analyze_django_config(config_data['django'])
            
            # Flask配置分析
            if config_data.get('flask'):
                self._analyze_flask_config(config_data['flask'])
            
            # Tomcat配置分析
            if config_data.get('tomcat'):
                self._analyze_tomcat_config(config_data['tomcat'])
            
            # Gunicorn配置分析
            if config_data.get('gunicorn'):
                self._analyze_gunicorn_config(config_data['gunicorn'])
            
            # 安全头分析
            if config_data.get('security_headers'):
                self._analyze_security_headers(config_data['security_headers'])
            
            # Lighthouse性能分析
            if config_data.get('lighthouse'):
                self._analyze_lighthouse_results(config_data['lighthouse'])
            
            # 性能指标分析
            if config_data.get('performance_metrics'):
                self._analyze_performance_metrics(config_data['performance_metrics'])
            
            # 银河麒麟OS特别分析
            self._analyze_kylin_optimizations()
            
            logger.info(f"配置分析完成，共生成 {len(self.suggestions)} 条优化建议")
            return self.suggestions
            
        except Exception as e:
            logger.error(f"配置分析过程中发生错误: {e}")
            raise
    
    def _analyze_system_config(self, system_config: Dict[str, Any]):
        """分析系统级配置"""
        logger.info("分析系统级配置...")
        
        # 文件句柄限制检查
        file_handles = system_config.get('file_handles', 1024)
        if file_handles < 65536:
            self._add_suggestion(
                category="系统性能",
                issue="文件句柄限制过低",
                severity="high",
                current=f"{file_handles}",
                recommended="65536或更高",
                solution="在/etc/security/limits.conf中添加:\n* soft nofile 65536\n* hard nofile 65536"
            )
        
        # Swappiness检查
        swappiness = system_config.get('swappiness', 60)
        if swappiness > 10:
            self._add_suggestion(
                category="系统性能",
                issue="Swappiness值过高",
                severity="medium",
                current=f"{swappiness}",
                recommended="1-10",
                solution="临时设置: echo 1 > /proc/sys/vm/swappiness\n永久设置: 在/etc/sysctl.conf中添加 vm.swappiness=1"
            )
        
        # Somaxconn检查
        somaxconn = system_config.get('somaxconn', 128)
        if somaxconn < 1024:
            self._add_suggestion(
                category="网络性能",
                issue="TCP连接队列大小不足",
                severity="medium",
                current=f"{somaxconn}",
                recommended="1024或更高",
                solution="在/etc/sysctl.conf中添加: net.core.somaxconn = 1024"
            )
        
        # NTP服务检查
        ntp_status = system_config.get('ntp_status', {})
        if not ntp_status.get('running', False):
            self._add_suggestion(
                category="系统稳定性",
                issue="NTP时间同步服务未运行",
                severity="medium",
                solution="启用NTP服务:\nsudo systemctl enable systemd-timesyncd\nsudo systemctl start systemd-timesyncd"
            )
        
        # 内存使用检查
        memory_available = system_config.get('memory_available', 0)
        memory_total = system_config.get('memory_total', 1)
        memory_usage_percent = (1 - memory_available / memory_total) * 100
        
        if memory_usage_percent > 80:
            self._add_suggestion(
                category="系统性能",
                issue="内存使用率过高",
                severity="high",
                current=f"{memory_usage_percent:.1f}%",
                recommended="<80%",
                solution="检查内存泄漏进程或增加系统内存"
            )
    
    def _analyze_nginx_config(self, nginx_config: Dict[str, Any], system_config: Dict[str, Any]):
        """分析Nginx配置"""
        logger.info("分析Nginx配置...")
        
        # 工作进程数检查
        worker_processes = nginx_config.get('worker_processes', 'auto')
        cpu_count = system_config.get('cpu_count', 4)
        
        if worker_processes != 'auto' and worker_processes.isdigit():
            worker_count = int(worker_processes)
            if worker_count < cpu_count:
                self._add_suggestion(
                    category="Nginx性能",
                    issue="工作进程数不足",
                    severity="high",
                    current=f"{worker_count}",
                    recommended=f"{cpu_count}或auto",
                    solution="在nginx.conf中设置: worker_processes auto;"
                )
        
        # KeepAlive超时检查
        keepalive_timeout = nginx_config.get('keepalive_timeout', '未配置')
        if keepalive_timeout != '未配置':
            timeout_value = int(keepalive_timeout)
            if timeout_value < 60:
                self._add_suggestion(
                    category="Nginx性能",
                    issue="KeepAlive超时过短",
                    severity="medium",
                    current=f"{timeout_value}秒",
                    recommended="60-120秒",
                    solution="在nginx.conf中设置: keepalive_timeout 75;"
                )
        
        # Gzip压缩检查
        gzip_enabled = nginx_config.get('gzip', 'off')
        if gzip_enabled == 'off':
            self._add_suggestion(
                category="Nginx性能",
                issue="未启用Gzip压缩",
                severity="medium",
                solution="在nginx.conf中启用gzip:\ngzip on;\ngzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;"
            )
        
        # 安全头检查
        security_headers = nginx_config.get('security_headers', {})
        for header, enabled in security_headers.items():
            if not enabled:
                header_name = header.replace('add_header ', '')
                self._add_suggestion(
                    category="Nginx安全",
                    issue=f"缺少{header_name}安全头",
                    severity="high",
                    solution=f"在nginx配置中添加:\n{header} DENY;"
                )
        
        # HTTPS检查
        https_enabled = nginx_config.get('https_enabled', False)
        if not https_enabled:
            self._add_suggestion(
                category="Nginx安全",
                issue="未启用HTTPS",
                severity="critical",
                solution="配置SSL证书并启用HTTPS"
            )
    
    def _analyze_apache_config(self, apache_config: Dict[str, Any]):
        """分析Apache配置"""
        logger.info("分析Apache配置...")
        
        # MaxRequestWorkers检查
        max_workers = apache_config.get('MaxRequestWorkers', '未配置')
        if max_workers != '未配置':
            worker_count = int(max_workers)
            if worker_count < 150:
                self._add_suggestion(
                    category="Apache性能",
                    issue="最大请求工作进程数不足",
                    severity="medium",
                    current=f"{worker_count}",
                    recommended="150或更高",
                    solution="在apache2.conf中增加: MaxRequestWorkers 150"
                )
        
        # KeepAliveTimeout检查
        keepalive_timeout = apache_config.get('KeepAliveTimeout', '未配置')
        if keepalive_timeout != '未配置':
            timeout_value = int(keepalive_timeout)
            if timeout_value < 5:
                self._add_suggestion(
                    category="Apache性能",
                    issue="KeepAlive超时过短",
                    severity="medium",
                    current=f"{timeout_value}秒",
                    recommended="5-15秒",
                    solution="在apache2.conf中设置: KeepAliveTimeout 5"
                )
        
        # EnableSendfile检查
        sendfile_enabled = apache_config.get('EnableSendfile', '未配置')
        if sendfile_enabled == 'Off':
            self._add_suggestion(
                category="Apache性能",
                issue="未启用Sendfile",
                severity="medium",
                solution="在apache2.conf中启用: EnableSendfile On"
            )
    
    def _analyze_spring_boot_config(self, spring_config: Dict[str, Any]):
        """分析Spring Boot配置"""
        logger.info("分析Spring Boot配置...")
        
        # Tomcat线程池检查
        max_threads = spring_config.get('server.tomcat.max-threads', '200')
        if max_threads != '未配置':
            thread_count = int(max_threads)
            if thread_count < 200:
                self._add_suggestion(
                    category="Spring Boot性能",
                    issue="Tomcat线程池过小",
                    severity="high",
                    current=f"{thread_count}",
                    recommended="200-500",
                    solution="在application.properties中设置: server.tomcat.max-threads=250"
                )
        
        # 数据库连接池检查
        max_pool_size = spring_config.get('spring.datasource.hikari.maximum-pool-size', '10')
        if max_pool_size != '未配置':
            pool_size = int(max_pool_size)
            if pool_size < 10:
                self._add_suggestion(
                    category="Spring Boot性能",
                    issue="数据库连接池过小",
                    severity="medium",
                    current=f"{pool_size}",
                    recommended="10-50",
                    solution="在application.properties中设置: spring.datasource.hikari.maximum-pool-size=20"
                )
    
    def _analyze_django_config(self, django_config: Dict[str, Any]):
        """分析Django配置"""
        logger.info("分析Django配置...")
        
        # DEBUG模式检查
        debug_mode = django_config.get('DEBUG', '未配置')
        if debug_mode == 'True':
            self._add_suggestion(
                category="Django安全",
                issue="生产环境启用了DEBUG模式",
                severity="critical",
                solution="在settings.py中设置: DEBUG = False"
            )
        
        # 数据库连接复用检查
        conn_max_age = django_config.get('CONN_MAX_AGE', '未配置')
        if conn_max_age != '未配置':
            max_age = int(conn_max_age)
            if max_age < 60:
                self._add_suggestion(
                    category="Django性能",
                    issue="数据库连接复用时间过短",
                    severity="medium",
                    current=f"{max_age}秒",
                    recommended="60-300秒",
                    solution="在settings.py中设置: CONN_MAX_AGE = 300"
                )
        
        # 安全Cookie检查
        session_secure = django_config.get('SESSION_COOKIE_SECURE', '未配置')
        if session_secure == 'False':
            self._add_suggestion(
                category="Django安全",
                issue="未启用安全Cookie",
                severity="high",
                solution="在settings.py中设置: SESSION_COOKIE_SECURE = True"
            )
    
    def _analyze_flask_config(self, flask_config: Dict[str, Any]):
        """分析Flask配置"""
        logger.info("分析Flask配置...")
        
        # DEBUG模式检查
        debug_mode = flask_config.get('DEBUG', '未配置')
        if debug_mode == 'True':
            self._add_suggestion(
                category="Flask安全",
                issue="生产环境启用了DEBUG模式",
                severity="critical",
                solution="在app.py中设置: DEBUG = False"
            )
        
        # 文件上传大小限制检查
        max_content_length = flask_config.get('MAX_CONTENT_LENGTH', '未配置')
        if max_content_length != '未配置':
            max_size = int(max_content_length)
            if max_size > 16 * 1024 * 1024:  # 16MB
                self._add_suggestion(
                    category="Flask安全",
                    issue="文件上传大小限制过大",
                    severity="medium",
                    current=f"{max_size / (1024*1024):.1f}MB",
                    recommended="<16MB",
                    solution="在app.py中设置: MAX_CONTENT_LENGTH = 16 * 1024 * 1024"
                )
    
    def _analyze_tomcat_config(self, tomcat_config: Dict[str, Any]):
        """分析Tomcat配置"""
        logger.info("分析Tomcat配置...")
        
        # 最大线程数检查
        max_threads = tomcat_config.get('maxThreads', '未配置')
        if max_threads != '未配置':
            thread_count = int(max_threads)
            if thread_count < 200:
                self._add_suggestion(
                    category="Tomcat性能",
                    issue="最大线程数不足",
                    severity="high",
                    current=f"{thread_count}",
                    recommended="200-500",
                    solution="在server.xml中设置: maxThreads=\"250\""
                )
        
        # 连接超时检查
        connection_timeout = tomcat_config.get('connectionTimeout', '未配置')
        if connection_timeout != '未配置':
            timeout_value = int(connection_timeout)
            if timeout_value < 20000:  # 20秒
                self._add_suggestion(
                    category="Tomcat性能",
                    issue="连接超时过短",
                    severity="medium",
                    current=f"{timeout_value}ms",
                    recommended="20000-60000ms",
                    solution="在server.xml中设置: connectionTimeout=\"30000\""
                )
    
    def _analyze_gunicorn_config(self, gunicorn_config: Dict[str, Any]):
        """分析Gunicorn配置"""
        logger.info("分析Gunicorn配置...")
        
        # 工作进程数检查
        workers = gunicorn_config.get('workers', '未配置')
        if workers != '未配置':
            worker_count = int(workers)
            if worker_count < 2:
                self._add_suggestion(
                    category="Gunicorn性能",
                    issue="工作进程数不足",
                    severity="medium",
                    current=f"{worker_count}",
                    recommended="2-4",
                    solution="在gunicorn.conf.py中设置: workers = 3"
                )
        
        # 超时设置检查
        timeout = gunicorn_config.get('timeout', '未配置')
        if timeout != '未配置':
            timeout_value = int(timeout)
            if timeout_value < 30:
                self._add_suggestion(
                    category="Gunicorn性能",
                    issue="请求超时过短",
                    severity="medium",
                    current=f"{timeout_value}秒",
                    recommended="30-120秒",
                    solution="在gunicorn.conf.py中设置: timeout = 60"
                )
    
    def _analyze_security_headers(self, security_headers: Dict[str, str]):
        """分析安全头配置"""
        logger.info("分析安全头配置...")
        
        # 内容安全策略检查
        csp = security_headers.get('Content-Security-Policy', '缺失')
        if csp == '缺失':
            self._add_suggestion(
                category="安全",
                issue="缺少内容安全策略(CSP)头",
                severity="critical",
                solution="添加Content-Security-Policy响应头，例如:\nContent-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'"
            )
        
        # X-Frame-Options检查
        x_frame_options = security_headers.get('X-Frame-Options', '缺失')
        if x_frame_options == '缺失':
            self._add_suggestion(
                category="安全",
                issue="缺少X-Frame-Options头",
                severity="high",
                solution="添加X-Frame-Options响应头: X-Frame-Options: DENY"
            )
        
        # X-Content-Type-Options检查
        x_content_type = security_headers.get('X-Content-Type-Options', '缺失')
        if x_content_type == '缺失':
            self._add_suggestion(
                category="安全",
                issue="缺少X-Content-Type-Options头",
                severity="medium",
                solution="添加X-Content-Type-Options响应头: X-Content-Type-Options: nosniff"
            )
        
        # HSTS检查
        hsts = security_headers.get('Strict-Transport-Security', '缺失')
        if hsts == '缺失':
            self._add_suggestion(
                category="安全",
                issue="缺少HSTS头",
                severity="high",
                solution="添加Strict-Transport-Security响应头: Strict-Transport-Security: max-age=31536000; includeSubDomains"
            )
        
        # Server信息泄露检查
        server = security_headers.get('Server', '缺失')
        if server != '缺失' and server not in ['nginx', 'Apache']:
            self._add_suggestion(
                category="安全",
                issue="Server头可能泄露敏感信息",
                severity="medium",
                solution="隐藏或修改Server响应头"
            )
    
    def _analyze_lighthouse_results(self, lighthouse_data: Dict[str, Any]):
        """分析Lighthouse性能结果"""
        logger.info("分析Lighthouse性能结果...")
        
        if not lighthouse_data or 'audits' not in lighthouse_data:
            return
        
        audits = lighthouse_data['audits']
        
        # 检查关键性能指标
        key_metrics = {
            'first-contentful-paint': '首次内容绘制',
            'largest-contentful-paint': '最大内容绘制',
            'first-meaningful-paint': '首次有意义绘制',
            'speed-index': '速度指数',
            'cumulative-layout-shift': '累积布局偏移',
            'total-blocking-time': '总阻塞时间',
            'time-to-interactive': '可交互时间'
        }
        
        for metric_id, metric_name in key_metrics.items():
            if metric_id in audits:
                audit = audits[metric_id]
                score = audit.get('score')
                
                # 检查score是否为有效数值
                if score is not None and isinstance(score, (int, float)):
                    if score < 0.9:
                        severity = "critical" if score < 0.5 else "high" if score < 0.7 else "medium"
                        self._add_suggestion(
                            category="性能",
                            issue=f"{metric_name}性能不佳",
                            severity=severity,
                            current=f"得分: {score:.2f}",
                            recommended=">0.9",
                            solution=audit.get('description', '需要优化页面性能')
                        )
        
        # 检查具体优化建议
        for audit_id, audit in audits.items():
            score = audit.get('score')
            if score is not None and isinstance(score, (int, float)) and score < 0.9 and audit.get('details'):
                self._add_suggestion(
                    category="性能",
                    issue=audit.get('title', '性能优化建议'),
                    severity="medium",
                    solution=audit.get('description', '')
                )
    
    def _analyze_performance_metrics(self, metrics: Dict[str, Any]):
        """分析性能指标"""
        logger.info("分析性能指标...")
        
        # CPU使用率检查
        cpu_usage = metrics.get('cpu_usage', 0)
        if cpu_usage > 80:
            self._add_suggestion(
                category="系统性能",
                issue="CPU使用率过高",
                severity="high",
                current=f"{cpu_usage:.1f}%",
                recommended="<80%",
                solution="检查高CPU使用率进程或优化应用性能"
            )
        
        # 内存使用率检查
        memory_usage = metrics.get('memory_usage', 0)
        if memory_usage > 85:
            self._add_suggestion(
                category="系统性能",
                issue="内存使用率过高",
                severity="high",
                current=f"{memory_usage:.1f}%",
                recommended="<85%",
                solution="检查内存泄漏或增加系统内存"
            )
        
        # 磁盘使用率检查
        disk_usage = metrics.get('disk_usage', 0)
        if disk_usage > 90:
            self._add_suggestion(
                category="系统性能",
                issue="磁盘使用率过高",
                severity="critical",
                current=f"{disk_usage:.1f}%",
                recommended="<90%",
                solution="清理磁盘空间或扩展存储"
            )
    
    def _analyze_kylin_optimizations(self):
        """银河麒麟OS特别优化分析"""
        logger.info("分析银河麒麟OS特别优化...")
        
        # 检查是否为银河麒麟OS
        if not os.path.exists('/etc/kylin-release'):
            return
        
        try:
            # 检查CPU架构
            cpu_arch = subprocess.getoutput("uname -m")
            if cpu_arch in ['loongarch64', 'mips64']:
                self._add_suggestion(
                    category="银河麒麟优化",
                    issue="未启用龙芯特定优化",
                    severity="medium",
                    solution="在Nginx配置中添加:\nworker_cpu_affinity auto;\nuse epoll;"
                )
            
            # 检查麒麟安全模块
            try:
                sec_status = subprocess.getoutput("kylin-secure status nginx")
                if "disabled" in sec_status:
                    self._add_suggestion(
                        category="银河麒麟安全",
                        issue="麒麟安全模块未启用",
                        severity="high",
                        solution="执行: sudo kylin-secure enable nginx"
                    )
            except:
                pass
            
            # 国产浏览器兼容性建议
            self._add_suggestion(
                category="银河麒麟兼容性",
                issue="国产浏览器兼容性优化",
                severity="low",
                solution="添加浏览器特定CSS前缀:\n-moz-kylin- 麒麟安全浏览器\n-webkit-kb- 奇安信浏览器"
            )
            
        except Exception as e:
            logger.warning(f"银河麒麟优化分析失败: {e}")
    
    def _add_suggestion(self, category: str, issue: str, severity: str, 
                       current: str = None, recommended: str = None, solution: str = ""):
        """添加优化建议"""
        suggestion = {
            "category": category,
            "issue": issue,
            "severity": severity,
            "solution": solution
        }
        
        if current:
            suggestion["current"] = current
        if recommended:
            suggestion["recommended"] = recommended
        
        self.suggestions.append(suggestion)
        
        # 统计严重性级别
        if severity == "critical":
            self.critical_count += 1
        elif severity == "high":
            self.high_count += 1
        elif severity == "medium":
            self.medium_count += 1
        elif severity == "low":
            self.low_count += 1
    
    def get_summary_stats(self) -> Dict[str, int]:
        """获取统计摘要"""
        return {
            "total": len(self.suggestions),
            "critical": self.critical_count,
            "high": self.high_count,
            "medium": self.medium_count,
            "low": self.low_count
        }
    
    def save_analysis_report(self, output_file: str = "web_config_analysis.json"):
        """保存分析报告"""
        try:
            report = {
                "summary": self.get_summary_stats(),
                "suggestions": self.suggestions,
                "timestamp": subprocess.getoutput("date -Iseconds")
            }
            
            with open(output_file, "w", encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"分析报告已保存到: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"保存分析报告失败: {e}")
            raise

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Web应用配置分析器')
    parser.add_argument('--input', default='web_config_report.json',
                       help='输入配置文件')
    parser.add_argument('--output', default='web_config_analysis.json',
                       help='输出分析报告文件名')
    
    args = parser.parse_args()
    
    # 读取配置数据
    if not os.path.exists(args.input):
        print(f"错误: 配置文件不存在: {args.input}")
        return
    
    with open(args.input, 'r', encoding='utf-8') as f:
        config_data = json.load(f)
    
    # 创建分析器并执行
    analyzer = WebConfigAnalyzer()
    suggestions = analyzer.analyze_config(config_data)
    analyzer.save_analysis_report(args.output)
    
    # 打印摘要
    stats = analyzer.get_summary_stats()
    print(f"分析完成！共发现 {stats['total']} 个问题:")
    print(f"  危急: {stats['critical']}")
    print(f"  高危: {stats['high']}")
    print(f"  中等: {stats['medium']}")
    print(f"  低危: {stats['low']}")
    print(f"详细报告已保存到: {args.output}")

if __name__ == "__main__":
    main() 