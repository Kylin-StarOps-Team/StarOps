#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志解析器 - 解析数据库和Web服务日志，提取关键字
"""

import re
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import os
from collections import defaultdict, Counter


class LogParser:
    """日志解析器"""
    
    def __init__(self, output_dir: str = "data"):
        """初始化日志解析器"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # 输出文件
        self.parsed_logs_file = self.output_dir / "parsed_logs.json"
        self.log_summary_file = self.output_dir / "log_summary.json"
        
        # 常见日志路径
        self.common_log_paths = {
            'nginx': [
                '/var/log/nginx/error.log',
                '/var/log/nginx/access.log',
                'C:/nginx/logs/error.log',
                'C:/nginx/logs/access.log'
            ],
            'mysql': [
                '/var/log/mysql/error.log',
                '/var/log/mysqld.log',
                '/var/log/mysqld_exporter_metrics.log',
                'C:/ProgramData/MySQL/MySQL Server 8.0/Data/*.err'
            ],
            'apache': [
                '/var/log/apache2/error.log',
                '/var/log/httpd/error_log',
                'C:/Apache24/logs/error.log'
            ],
            'redis': [
                '/var/log/redis/redis-server.log',
                'C:/Redis/logs/redis.log'
            ],
            'postgresql': [
                '/var/log/postgresql/postgresql.log',
                'C:/Program Files/PostgreSQL/*/data/log/*.log'
            ],
            'blackbox': [
                '/var/log/blackbox_exporter_metrics.log'
            ],
            'loki': [
                '/var/log/loki.log'
            ],
            'system': [
                '/var/log/messages-*'
            ],
            'node_exporter': [
                '/var/log/node_exporter_metrics.log'
            ],
            'promptail': [
                '/var/log/promtail.log'
            ],
            
        }
        
        # 关键词模式
        self.error_patterns = {
            'critical': [
                r'critical|fatal|emergency|panic',
                r'out of memory|memory leak|oom',
                r'segmentation fault|core dump',
                r'database.*corrupt|table.*corrupt',
                r'connection.*refused|connection.*failed'
            ],
            'error': [
                r'error|err|failed|failure',
                r'timeout|time.*out',
                r'502|503|504|500',
                r'upstream.*failed|backend.*failed',
                r'access denied|permission denied',
                r'cannot connect|connection lost'
            ],
            'warning': [
                r'warning|warn',
                r'slow query|slow.*log',
                r'high load|high.*usage',
                r'retry|retrying',
                r'deprecated|obsolete'
            ]
        }
        
        # 服务特定模式
        self.service_patterns = {
            'nginx': {
                'error_codes': r'(\d{3})\s+\d+',
                'upstream': r'upstream.*?(timeout|failed|error)',
                'client_errors': r'client.*?(closed|reset|timeout)',
                'response_time': r'request_time:(\d+\.\d+)'
            },
            'mysql': {
                'innodb_errors': r'InnoDB.*?(error|warning|corruption)',
                'connection_errors': r'connection.*?(failed|refused|timeout)',
                'query_errors': r'query.*?(error|failed|timeout)',
                'table_errors': r'table.*?(corrupt|crashed|error)'
            },
            'apache': {
                'mod_errors': r'mod_\w+.*?(error|failed)',
                'client_errors': r'client.*?(timeout|reset|denied)',
                'server_errors': r'server.*?(error|failed|timeout)'
            }
        }
        
        # 时间格式
        self.time_patterns = [
            r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})',  # MySQL: 2024-01-01 12:00:00
            r'(\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2})',   # Nginx: 01/Jan/2024:12:00:00
            r'(\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2})',   # 2024/01/01 12:00:00
            r'(\w{3} \d{2} \d{2}:\d{2}:\d{2})'          # Jan 01 12:00:00
        ]
        
        # 设置日志
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def find_log_files(self, service: str = None) -> Dict[str, List[str]]:
        """查找系统中的日志文件"""
        found_logs = defaultdict(list)
        
        # 如果指定了服务，只查找该服务的日志
        if service and service in self.common_log_paths:
            service_paths = {service: self.common_log_paths[service]}
        else:
            service_paths = self.common_log_paths
        
        for svc, paths in service_paths.items():
            for path_pattern in paths:
                try:
                    # 处理通配符路径
                    if '*' in path_pattern:
                        import glob
                        for path in glob.glob(path_pattern):
                            if os.path.exists(path) and os.path.isfile(path):
                                found_logs[svc].append(path)
                    else:
                        if os.path.exists(path_pattern) and os.path.isfile(path_pattern):
                            found_logs[svc].append(path_pattern)
                except Exception as e:
                    self.logger.debug(f"查找日志路径失败 {path_pattern}: {e}")
        
        return dict(found_logs)
    
    def extract_timestamp(self, line: str) -> Optional[datetime]:
        """从日志行中提取时间戳"""
        for pattern in self.time_patterns:
            match = re.search(pattern, line)
            if match:
                time_str = match.group(1)
                
                # 尝试解析不同格式的时间
                time_formats = [
                    '%Y-%m-%d %H:%M:%S',
                    '%d/%b/%Y:%H:%M:%S',
                    '%Y/%m/%d %H:%M:%S',
                    '%b %d %H:%M:%S'
                ]
                
                for fmt in time_formats:
                    try:
                        if fmt == '%b %d %H:%M:%S':
                            # 为没有年份的格式添加当前年份
                            time_str = f"{datetime.now().year} {time_str}"
                            fmt = '%Y %b %d %H:%M:%S'
                        return datetime.strptime(time_str, fmt)
                    except ValueError:
                        continue
        
        return None
    
    def classify_log_level(self, line: str) -> str:
        """分类日志级别"""
        line_lower = line.lower()
        
        # 检查critical级别
        for pattern in self.error_patterns['critical']:
            if re.search(pattern, line_lower):
                return 'critical'
        
        # 检查error级别
        for pattern in self.error_patterns['error']:
            if re.search(pattern, line_lower):
                return 'error'
        
        # 检查warning级别
        for pattern in self.error_patterns['warning']:
            if re.search(pattern, line_lower):
                return 'warning'
        
        return 'info'
    
    def extract_service_metrics(self, line: str, service: str) -> Dict[str, Any]:
        """提取服务特定的指标"""
        metrics = {}
        
        if service in self.service_patterns:
            patterns = self.service_patterns[service]
            
            for metric_name, pattern in patterns.items():
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    if metric_name == 'error_codes':
                        metrics['http_status'] = int(match.group(1))
                    elif metric_name == 'response_time':
                        metrics['response_time'] = float(match.group(1))
                    else:
                        metrics[metric_name] = match.group(0)
        
        return metrics
    
    def parse_log_file(self, file_path: str, service: str, 
                      lines_limit: int = 1000, 
                      time_window_hours: int = 24) -> Dict[str, Any]:
        """解析单个日志文件"""
        parsed_data = {
            'file_path': file_path,
            'service': service,
            'parse_time': datetime.now().isoformat(),
            'total_lines': 0,
            'parsed_lines': 0,
            'log_entries': [],
            'summary': {
                'by_level': Counter(),
                'by_hour': defaultdict(int),
                'error_keywords': Counter(),
                'service_metrics': defaultdict(list)
            }
        }
        
        # 计算时间窗口
        cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                parsed_data['total_lines'] = len(lines)
                
                # 从文件末尾开始读取，获取最新的日志
                for line in reversed(lines[-lines_limit:]):
                    line = line.strip()
                    if not line:
                        continue
                    
                    # 提取时间戳
                    timestamp = self.extract_timestamp(line)
                    if timestamp and timestamp < cutoff_time:
                        continue  # 跳过超出时间窗口的日志
                    
                    # 分类日志级别
                    log_level = self.classify_log_level(line)
                    
                    # 提取服务指标
                    service_metrics = self.extract_service_metrics(line, service)
                    
                    # 构建日志条目
                    log_entry = {
                        'timestamp': timestamp.isoformat() if timestamp else None,
                        'level': log_level,
                        'message': line,
                        'service_metrics': service_metrics
                    }
                    
                    parsed_data['log_entries'].append(log_entry)
                    parsed_data['parsed_lines'] += 1
                    
                    # 更新统计
                    parsed_data['summary']['by_level'][log_level] += 1
                    
                    if timestamp:
                        hour_key = timestamp.strftime('%Y-%m-%d %H:00')
                        parsed_data['summary']['by_hour'][hour_key] += 1
                    
                    # 提取错误关键词
                    if log_level in ['error', 'critical']:
                        words = line.lower().split()
                        for word in words:
                            if len(word) > 3:  # 过滤短词
                                parsed_data['summary']['error_keywords'][word] += 1
                    
                    # 记录服务指标
                    for metric, value in service_metrics.items():
                        parsed_data['summary']['service_metrics'][metric].append(value)
                
                # 倒序回正序
                parsed_data['log_entries'].reverse()
                
        except Exception as e:
            self.logger.error(f"解析日志文件失败 {file_path}: {e}")
            parsed_data['error'] = str(e)
        
        return parsed_data
    
    def parse_all_logs(self, time_window_hours: int = 24, 
                      lines_per_file: int = 1000) -> Dict[str, Any]:
        """解析所有找到的日志文件"""
        self.logger.info("开始解析日志文件...")
        
        # 查找日志文件
        found_logs = self.find_log_files()
        
        all_parsed_data = {
            'parse_time': datetime.now().isoformat(),
            'time_window_hours': time_window_hours,
            'services': {},
            'global_summary': {
                'total_files': 0,
                'total_lines': 0,
                'total_errors': 0,
                'total_warnings': 0,
                'total_criticals': 0,
                'top_error_keywords': [],
                'services_found': []
            }
        }
        
        if not found_logs:
            self.logger.warning("未找到任何日志文件")
            return all_parsed_data
        
        # 解析每个服务的日志
        for service, log_files in found_logs.items():
            self.logger.info(f"解析 {service} 服务日志，共 {len(log_files)} 个文件")
            
            service_data = {
                'service': service,
                'files': [],
                'summary': {
                    'total_lines': 0,
                    'by_level': Counter(),
                    'recent_errors': [],
                    'service_metrics': {}
                }
            }
            
            for log_file in log_files:
                file_data = self.parse_log_file(
                    log_file, service, lines_per_file, time_window_hours
                )
                service_data['files'].append(file_data)
                
                # 更新服务统计
                service_data['summary']['total_lines'] += file_data['parsed_lines']
                
                for level, count in file_data['summary']['by_level'].items():
                    service_data['summary']['by_level'][level] += count
                
                # 收集最近的错误
                for entry in file_data['log_entries']:
                    if entry['level'] in ['error', 'critical']:
                        service_data['summary']['recent_errors'].append({
                            'timestamp': entry['timestamp'],
                            'level': entry['level'],
                            'message': entry['message'][:200] + '...' if len(entry['message']) > 200 else entry['message']
                        })
                
                # 合并服务指标
                for metric, values in file_data['summary']['service_metrics'].items():
                    if metric not in service_data['summary']['service_metrics']:
                        service_data['summary']['service_metrics'][metric] = []
                    service_data['summary']['service_metrics'][metric].extend(values)
            
            # 限制recent_errors数量
            service_data['summary']['recent_errors'] = \
                service_data['summary']['recent_errors'][-50:]
            
            all_parsed_data['services'][service] = service_data
            all_parsed_data['global_summary']['services_found'].append(service)
        
        # 计算全局统计
        all_error_keywords = Counter()
        for service_data in all_parsed_data['services'].values():
            all_parsed_data['global_summary']['total_files'] += len(service_data['files'])
            all_parsed_data['global_summary']['total_lines'] += service_data['summary']['total_lines']
            
            for level, count in service_data['summary']['by_level'].items():
                if level == 'error':
                    all_parsed_data['global_summary']['total_errors'] += count
                elif level == 'warning':
                    all_parsed_data['global_summary']['total_warnings'] += count
                elif level == 'critical':
                    all_parsed_data['global_summary']['total_criticals'] += count
            
            # 收集错误关键词
            for file_data in service_data['files']:
                all_error_keywords.update(file_data['summary']['error_keywords'])
        
        # 提取顶级错误关键词
        all_parsed_data['global_summary']['top_error_keywords'] = \
            [{'keyword': word, 'count': count} 
             for word, count in all_error_keywords.most_common(20)]
        
        return all_parsed_data
    
    def save_parsed_logs(self, parsed_data: Dict[str, Any]):
        """保存解析结果"""
        try:
            # 保存详细数据
            with open(self.parsed_logs_file, 'w', encoding='utf-8') as f:
                json.dump(parsed_data, f, ensure_ascii=False, indent=2)
            
            # 保存摘要数据
            summary = {
                'parse_time': parsed_data['parse_time'],
                'global_summary': parsed_data['global_summary'],
                'services_summary': {}
            }
            
            for service, service_data in parsed_data['services'].items():
                summary['services_summary'][service] = {
                    'total_lines': service_data['summary']['total_lines'],
                    'by_level': dict(service_data['summary']['by_level']),
                    'files_count': len(service_data['files']),
                    'recent_errors_count': len(service_data['summary']['recent_errors'])
                }
            
            with open(self.log_summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"日志解析结果已保存到: {self.output_dir}")
            
        except Exception as e:
            self.logger.error(f"保存解析结果失败: {e}")
    
    def get_error_patterns(self, service: str = None) -> List[Dict[str, Any]]:
        """获取错误模式"""
        try:
            with open(self.parsed_logs_file, 'r', encoding='utf-8') as f:
                parsed_data = json.load(f)
            
            patterns = []
            
            # 如果指定服务，只返回该服务的模式
            if service and service in parsed_data['services']:
                services_to_check = {service: parsed_data['services'][service]}
            else:
                services_to_check = parsed_data['services']
            
            for svc, svc_data in services_to_check.items():
                for file_data in svc_data['files']:
                    # 分析错误和critical级别的日志
                    error_entries = [
                        entry for entry in file_data['log_entries']
                        if entry['level'] in ['error', 'critical']
                    ]
                    
                    if error_entries:
                        # 按小时分组错误
                        hourly_errors = defaultdict(list)
                        for entry in error_entries:
                            if entry['timestamp']:
                                hour = entry['timestamp'][:13] + ':00:00'  # 取到小时
                                hourly_errors[hour].append(entry)
                        
                        # 找出错误频繁的时段
                        for hour, entries in hourly_errors.items():
                            if len(entries) >= 3:  # 一小时内3个或以上错误
                                pattern = {
                                    'service': svc,
                                    'time_period': hour,
                                    'error_count': len(entries),
                                    'severity': 'high' if any(e['level'] == 'critical' for e in entries) else 'medium',
                                    'sample_messages': [e['message'][:100] for e in entries[:3]],
                                    'common_keywords': self._extract_common_keywords([e['message'] for e in entries])
                                }
                                patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"获取错误模式失败: {e}")
            return []
    
    def _extract_common_keywords(self, messages: List[str]) -> List[str]:
        """从消息列表中提取常见关键词"""
        all_words = []
        for msg in messages:
            words = re.findall(r'\b\w{4,}\b', msg.lower())  # 提取4字符以上的单词
            all_words.extend(words)
        
        word_counts = Counter(all_words)
        # 返回出现2次以上的词
        return [word for word, count in word_counts.items() if count >= 2]


def main():
    """主函数演示"""
    parser = LogParser(output_dir="data")
    
    print("🔍 开始日志解析...")
    
    try:
        # 查找日志文件
        found_logs = parser.find_log_files()
        print(f"📁 发现日志文件:")
        for service, files in found_logs.items():
            print(f"  - {service}: {len(files)} 个文件")
            for file_path in files[:3]:  # 只显示前3个
                print(f"    • {file_path}")
        
        if not found_logs:
            print("⚠️ 未找到任何日志文件")
            return
        
        # 解析所有日志
        parsed_data = parser.parse_all_logs(time_window_hours=24)
        
        # 保存结果
        parser.save_parsed_logs(parsed_data)
        
        # 显示摘要
        summary = parsed_data['global_summary']
        print(f"\n📊 解析摘要:")
        print(f"  - 处理文件数: {summary['total_files']}")
        print(f"  - 解析行数: {summary['total_lines']}")
        print(f"  - 错误数: {summary['total_errors']}")
        print(f"  - 警告数: {summary['total_warnings']}")
        print(f"  - 严重错误数: {summary['total_criticals']}")
        
        if summary['top_error_keywords']:
            print(f"\n🔑 常见错误关键词:")
            for kw in summary['top_error_keywords'][:5]:
                print(f"  - {kw['keyword']}: {kw['count']} 次")
        
        # 获取错误模式
        patterns = parser.get_error_patterns()
        if patterns:
            print(f"\n⚠️ 发现 {len(patterns)} 个错误模式:")
            for pattern in patterns[:3]:
                print(f"  - {pattern['service']} ({pattern['time_period']}): "
                      f"{pattern['error_count']} 个错误")
        
        print(f"\n💾 解析结果已保存到: {parser.output_dir}")
        
    except Exception as e:
        print(f"❌ 日志解析失败: {e}")


if __name__ == "__main__":
    main() 