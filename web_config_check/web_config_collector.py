#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web应用配置采集器
负责收集系统级配置、Web服务器配置、应用框架配置等信息
"""

import os
import re
import subprocess
import requests
import configparser
import json
import yaml
import psutil
from datetime import datetime
from typing import Dict, Any, Optional, List
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WebConfigCollector:
    """Web应用配置采集器"""
    
    def __init__(self, target_url: str = "http://localhost:8080"):
        # 自动添加协议前缀
        if not target_url.startswith(('http://', 'https://')):
            self.target_url = 'https://' + target_url
        else:
            self.target_url = target_url
        self.collected_data = {}
        
    def collect_all_configs(self) -> Dict[str, Any]:
        """收集所有配置信息"""
        logger.info("开始收集Web应用配置信息...")
        
        try:
            self.collected_data = {
                "timestamp": datetime.now().isoformat(),
                "target_url": self.target_url,
                "system": self.collect_system_config(),
                "nginx": self.collect_nginx_config(),
                "apache": self.collect_apache_config(),
                "spring_boot": self.collect_spring_boot_config(),
                "django": self.collect_django_config(),
                "flask": self.collect_flask_config(),
                "tomcat": self.collect_tomcat_config(),
                "gunicorn": self.collect_gunicorn_config(),
                "security_headers": self.check_security_headers(),
                "lighthouse": self.run_lighthouse_audit(),
                "performance_metrics": self.collect_performance_metrics()
            }
            
            logger.info("配置信息收集完成")
            return self.collected_data
            
        except Exception as e:
            logger.error(f"配置收集过程中发生错误: {e}")
            raise
    
    def collect_system_config(self) -> Dict[str, Any]:
        """收集系统级配置"""
        logger.info("收集系统级配置...")
        
        try:
            system_config = {
                "cpu_count": os.cpu_count(),
                "memory_total": psutil.virtual_memory().total,
                "memory_available": psutil.virtual_memory().available,
                "disk_usage": psutil.disk_usage('/').percent,
                "load_average": os.getloadavg(),
                "file_handles": self._get_file_handles_limit(),
                "swappiness": self._get_swappiness(),
                "somaxconn": self._get_somaxconn(),
                "timezone": self._get_timezone(),
                "ntp_status": self._check_ntp_status(),
                "os_info": self._get_os_info()
            }
            
            return system_config
            
        except Exception as e:
            logger.error(f"系统配置收集失败: {e}")
            return {"error": str(e)}
    
    def _get_file_handles_limit(self) -> int:
        """获取文件句柄限制"""
        try:
            result = subprocess.run(['ulimit', '-n'], capture_output=True, text=True)
            return int(result.stdout.strip())
        except:
            return 1024
    
    def _get_swappiness(self) -> int:
        """获取swappiness值"""
        try:
            with open('/proc/sys/vm/swappiness', 'r') as f:
                return int(f.read().strip())
        except:
            return 60
    
    def _get_somaxconn(self) -> int:
        """获取somaxconn值"""
        try:
            result = subprocess.run(['sysctl', '-n', 'net.core.somaxconn'], 
                                  capture_output=True, text=True)
            return int(result.stdout.strip())
        except:
            return 128
    
    def _get_timezone(self) -> str:
        """获取时区信息"""
        try:
            return subprocess.getoutput('timedatectl show --property=Timezone --value')
        except:
            return "UTC"
    
    def _check_ntp_status(self) -> Dict[str, Any]:
        """检查NTP服务状态"""
        try:
            result = subprocess.run(['systemctl', 'is-active', 'systemd-timesyncd'], 
                                  capture_output=True, text=True)
            return {
                "status": result.stdout.strip(),
                "running": result.stdout.strip() == "active"
            }
        except:
            return {"status": "unknown", "running": False}
    
    def _get_os_info(self) -> Dict[str, str]:
        """获取操作系统信息"""
        try:
            with open('/etc/os-release', 'r') as f:
                lines = f.readlines()
                os_info = {}
                for line in lines:
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        os_info[key] = value.strip('"')
                return os_info
        except:
            return {"name": "Unknown", "version": "Unknown"}
    
    def collect_nginx_config(self, config_path: str = '/etc/nginx/nginx.conf') -> Optional[Dict[str, Any]]:
        """收集Nginx配置"""
        logger.info("收集Nginx配置...")
        
        if not os.path.exists(config_path):
            logger.warning(f"Nginx配置文件不存在: {config_path}")
            return None
        
        try:
            config = {}
            with open(config_path, 'r') as f:
                content = f.read()
            
            # 解析关键配置项
            config_patterns = {
                'worker_processes': r'worker_processes\s+(\d+|auto);',
                'worker_connections': r'worker_connections\s+(\d+);',
                'keepalive_timeout': r'keepalive_timeout\s+(\d+);',
                'client_max_body_size': r'client_max_body_size\s+(\d+[kmg]?);',
                'gzip': r'gzip\s+(\w+);',
                'gzip_types': r'gzip_types\s+([^;]+);',
                'sendfile': r'sendfile\s+(\w+);',
                'tcp_nopush': r'tcp_nopush\s+(\w+);',
                'tcp_nodelay': r'tcp_nodelay\s+(\w+);'
            }
            
            for key, pattern in config_patterns.items():
                match = re.search(pattern, content, re.IGNORECASE)
                config[key] = match.group(1) if match else "未配置"
            
            # 检查是否启用了HTTPS
            config['https_enabled'] = 'ssl_certificate' in content
            
            # 检查安全头配置
            security_headers = {
                'add_header X-Frame-Options': 'X-Frame-Options' in content,
                'add_header X-Content-Type-Options': 'X-Content-Type-Options' in content,
                'add_header X-XSS-Protection': 'X-XSS-Protection' in content,
                'add_header Strict-Transport-Security': 'Strict-Transport-Security' in content
            }
            config['security_headers'] = security_headers
            
            return config
            
        except Exception as e:
            logger.error(f"Nginx配置收集失败: {e}")
            return {"error": str(e)}
    
    def collect_apache_config(self, config_path: str = '/etc/apache2/apache2.conf') -> Optional[Dict[str, Any]]:
        """收集Apache配置"""
        logger.info("收集Apache配置...")
        
        if not os.path.exists(config_path):
            logger.warning(f"Apache配置文件不存在: {config_path}")
            return None
        
        try:
            config = {}
            with open(config_path, 'r') as f:
                content = f.read()
            
            # 解析关键配置项
            config_patterns = {
                'MaxRequestWorkers': r'MaxRequestWorkers\s+(\d+)',
                'KeepAliveTimeout': r'KeepAliveTimeout\s+(\d+)',
                'MaxKeepAliveRequests': r'MaxKeepAliveRequests\s+(\d+)',
                'EnableSendfile': r'EnableSendfile\s+(On|Off)',
                'EnableMMAP': r'EnableMMAP\s+(On|Off)'
            }
            
            for key, pattern in config_patterns.items():
                match = re.search(pattern, content, re.IGNORECASE)
                config[key] = match.group(1) if match else "未配置"
            
            return config
            
        except Exception as e:
            logger.error(f"Apache配置收集失败: {e}")
            return {"error": str(e)}
    
    def collect_spring_boot_config(self, prop_path: str = 'application.properties') -> Optional[Dict[str, Any]]:
        """收集Spring Boot配置"""
        logger.info("收集Spring Boot配置...")
        
        # 查找配置文件
        config_files = [
            'application.properties',
            'application.yml',
            'application.yaml',
            'src/main/resources/application.properties',
            'src/main/resources/application.yml'
        ]
        
        config = {}
        
        for config_file in config_files:
            if os.path.exists(config_file):
                try:
                    if config_file.endswith('.properties'):
                        config_parser = configparser.ConfigParser()
                        config_parser.read(config_file)
                        
                        # 提取关键配置
                        if 'server' in config_parser:
                            config['server.port'] = config_parser.get('server', 'port', fallback='8080')
                            config['server.tomcat.max-threads'] = config_parser.get('server.tomcat', 'max-threads', fallback='200')
                            config['server.tomcat.min-spare-threads'] = config_parser.get('server.tomcat', 'min-spare-threads', fallback='10')
                        
                        if 'spring.datasource.hikari' in config_parser:
                            config['spring.datasource.hikari.maximum-pool-size'] = config_parser.get(
                                'spring.datasource.hikari', 'maximum-pool-size', fallback='10'
                            )
                            config['spring.datasource.hikari.minimum-idle'] = config_parser.get(
                                'spring.datasource.hikari', 'minimum-idle', fallback='5'
                            )
                    
                    elif config_file.endswith(('.yml', '.yaml')):
                        with open(config_file, 'r') as f:
                            yaml_config = yaml.safe_load(f)
                            
                        if yaml_config and 'server' in yaml_config:
                            config['server.port'] = yaml_config['server'].get('port', '8080')
                            if 'tomcat' in yaml_config['server']:
                                config['server.tomcat.max-threads'] = yaml_config['server']['tomcat'].get('max-threads', '200')
                        
                        if yaml_config and 'spring' in yaml_config and 'datasource' in yaml_config['spring']:
                            if 'hikari' in yaml_config['spring']['datasource']:
                                config['spring.datasource.hikari.maximum-pool-size'] = yaml_config['spring']['datasource']['hikari'].get('maximum-pool-size', '10')
                    
                    break
                    
                except Exception as e:
                    logger.error(f"Spring Boot配置解析失败 {config_file}: {e}")
                    continue
        
        return config if config else None
    
    def collect_django_config(self, settings_path: str = 'settings.py') -> Optional[Dict[str, Any]]:
        """收集Django配置"""
        logger.info("收集Django配置...")
        
        if not os.path.exists(settings_path):
            logger.warning(f"Django配置文件不存在: {settings_path}")
            return None
        
        try:
            config = {}
            with open(settings_path, 'r') as f:
                content = f.read()
            
            # 解析关键配置项
            config_patterns = {
                'DEBUG': r'DEBUG\s*=\s*(True|False)',
                'ALLOWED_HOSTS': r'ALLOWED_HOSTS\s*=\s*\[([^\]]*)\]',
                'DATABASES': r'DATABASES\s*=\s*\{([^}]+)\}',
                'CONN_MAX_AGE': r'CONN_MAX_AGE\s*=\s*(\d+)',
                'SESSION_COOKIE_SECURE': r'SESSION_COOKIE_SECURE\s*=\s*(True|False)',
                'CSRF_COOKIE_SECURE': r'CSRF_COOKIE_SECURE\s*=\s*(True|False)'
            }
            
            for key, pattern in config_patterns.items():
                match = re.search(pattern, content, re.IGNORECASE)
                config[key] = match.group(1) if match else "未配置"
            
            return config
            
        except Exception as e:
            logger.error(f"Django配置收集失败: {e}")
            return {"error": str(e)}
    
    def collect_flask_config(self, app_path: str = 'app.py') -> Optional[Dict[str, Any]]:
        """收集Flask配置"""
        logger.info("收集Flask配置...")
        
        if not os.path.exists(app_path):
            logger.warning(f"Flask应用文件不存在: {app_path}")
            return None
        
        try:
            config = {}
            with open(app_path, 'r') as f:
                content = f.read()
            
            # 解析关键配置项
            config_patterns = {
                'MAX_CONTENT_LENGTH': r'MAX_CONTENT_LENGTH\s*=\s*(\d+)',
                'SECRET_KEY': r'SECRET_KEY\s*=\s*[\'"]([^\'"]+)[\'"]',
                'DEBUG': r'DEBUG\s*=\s*(True|False)',
                'TESTING': r'TESTING\s*=\s*(True|False)'
            }
            
            for key, pattern in config_patterns.items():
                match = re.search(pattern, content, re.IGNORECASE)
                config[key] = match.group(1) if match else "未配置"
            
            return config
            
        except Exception as e:
            logger.error(f"Flask配置收集失败: {e}")
            return {"error": str(e)}
    
    def collect_tomcat_config(self, server_xml_path: str = '/etc/tomcat/server.xml') -> Optional[Dict[str, Any]]:
        """收集Tomcat配置"""
        logger.info("收集Tomcat配置...")
        
        if not os.path.exists(server_xml_path):
            logger.warning(f"Tomcat配置文件不存在: {server_xml_path}")
            return None
        
        try:
            config = {}
            with open(server_xml_path, 'r') as f:
                content = f.read()
            
            # 解析关键配置项
            config_patterns = {
                'maxThreads': r'maxThreads\s*=\s*"(\d+)"',
                'minSpareThreads': r'minSpareThreads\s*=\s*"(\d+)"',
                'connectionTimeout': r'connectionTimeout\s*=\s*"(\d+)"',
                'maxHttpHeaderSize': r'maxHttpHeaderSize\s*=\s*"(\d+)"',
                'enableLookups': r'enableLookups\s*=\s*"(true|false)"'
            }
            
            for key, pattern in config_patterns.items():
                match = re.search(pattern, content, re.IGNORECASE)
                config[key] = match.group(1) if match else "未配置"
            
            return config
            
        except Exception as e:
            logger.error(f"Tomcat配置收集失败: {e}")
            return {"error": str(e)}
    
    def collect_gunicorn_config(self, config_path: str = 'gunicorn.conf.py') -> Optional[Dict[str, Any]]:
        """收集Gunicorn配置"""
        logger.info("收集Gunicorn配置...")
        
        if not os.path.exists(config_path):
            logger.warning(f"Gunicorn配置文件不存在: {config_path}")
            return None
        
        try:
            config = {}
            with open(config_path, 'r') as f:
                content = f.read()
            
            # 解析关键配置项
            config_patterns = {
                'workers': r'workers\s*=\s*(\d+)',
                'worker_class': r'worker_class\s*=\s*[\'"]([^\'"]+)[\'"]',
                'bind': r'bind\s*=\s*[\'"]([^\'"]+)[\'"]',
                'timeout': r'timeout\s*=\s*(\d+)',
                'keepalive': r'keepalive\s*=\s*(\d+)',
                'max_requests': r'max_requests\s*=\s*(\d+)',
                'max_requests_jitter': r'max_requests_jitter\s*=\s*(\d+)'
            }
            
            for key, pattern in config_patterns.items():
                match = re.search(pattern, content, re.IGNORECASE)
                config[key] = match.group(1) if match else "未配置"
            
            return config
            
        except Exception as e:
            logger.error(f"Gunicorn配置收集失败: {e}")
            return {"error": str(e)}
    
    def check_security_headers(self) -> Dict[str, str]:
        """检查HTTP安全头"""
        logger.info("检查HTTP安全头...")
        
        try:
            response = requests.get(self.target_url, timeout=10, verify=False)
            headers = response.headers
            
            security_headers = {
                'Content-Security-Policy': headers.get('Content-Security-Policy', '缺失'),
                'X-Frame-Options': headers.get('X-Frame-Options', '缺失'),
                'X-Content-Type-Options': headers.get('X-Content-Type-Options', '缺失'),
                'X-XSS-Protection': headers.get('X-XSS-Protection', '缺失'),
                'Strict-Transport-Security': headers.get('Strict-Transport-Security', '缺失'),
                'Referrer-Policy': headers.get('Referrer-Policy', '缺失'),
                'Permissions-Policy': headers.get('Permissions-Policy', '缺失'),
                'Cache-Control': headers.get('Cache-Control', '缺失'),
                'Server': headers.get('Server', '缺失')
            }
            
            return security_headers
            
        except Exception as e:
            logger.error(f"安全头检查失败: {e}")
            return {"error": str(e)}
    
    def run_lighthouse_audit(self) -> Optional[Dict[str, Any]]:
        """运行Lighthouse审计"""
        logger.info("运行Lighthouse审计...")
        
        try:
            # 检查Lighthouse是否安装
            result = subprocess.run(['lighthouse', '--version'], 
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.warning("Lighthouse未安装，跳过性能审计")
                return None
            
            # 生成报告文件名
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            report_file = f"lighthouse_report_{timestamp}.json"
            
            # 运行Lighthouse
            cmd = [
                'lighthouse', self.target_url,
                '--output=json',
                '--output-path=' + report_file,
                '--chrome-flags=--headless --no-sandbox --disable-gpu'
            ]
            
            subprocess.run(cmd, check=True)
            
            # 读取报告
            with open(report_file, 'r') as f:
                report_data = json.load(f)
            
            # 清理临时文件
            os.remove(report_file)
            
            return report_data
            
        except Exception as e:
            logger.error(f"Lighthouse审计失败: {e}")
            return None
    
    def collect_performance_metrics(self) -> Dict[str, Any]:
        """收集性能指标"""
        logger.info("收集性能指标...")
        
        try:
            # 系统性能指标
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # 网络连接数
            connections = len(psutil.net_connections())
            
            # 进程信息
            web_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_percent']):
                try:
                    if any(keyword in proc.info['name'].lower() for keyword in ['nginx', 'apache', 'tomcat', 'java', 'python']):
                        web_processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            metrics = {
                "cpu_usage": cpu_percent,
                "memory_usage": memory.percent,
                "disk_usage": disk.percent,
                "network_connections": connections,
                "web_processes": web_processes
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"性能指标收集失败: {e}")
            return {"error": str(e)}
    
    def save_report(self, output_file: str = "web_config_report.json"):
        """保存配置报告"""
        try:
            with open(output_file, "w", encoding='utf-8') as f:
                json.dump(self.collected_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"配置报告已保存到: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"保存报告失败: {e}")
            raise

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Web应用配置采集器')
    parser.add_argument('--url', default='http://localhost:8080', 
                       help='目标Web应用URL')
    parser.add_argument('--output', default='web_config_report.json',
                       help='输出报告文件名')
    
    args = parser.parse_args()
    
    # 创建采集器并执行
    collector = WebConfigCollector(args.url)
    collector.collect_all_configs()
    collector.save_report(args.output)
    
    print(f"Web配置报告已生成: {args.output}")

if __name__ == "__main__":
    main() 