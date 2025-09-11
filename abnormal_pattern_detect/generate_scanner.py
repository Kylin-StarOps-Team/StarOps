#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
扫描器生成模块 - 根据异常模式自动生成检测脚本
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
from jinja2 import Template


class ScannerGenerator:
    """扫描器代码生成器"""
    
    def __init__(self, output_dir: str = "data", scanners_dir: str = "/home/denerate/abnormal_pattern_detect/scanners"):
        """初始化扫描器生成器"""
        self.output_dir = Path(output_dir)
        self.scanners_dir = Path(scanners_dir)
        self.scanners_dir.mkdir(exist_ok=True)
        
        # 输入文件
        self.patterns_file = self.output_dir / "extracted_patterns.json"
        
        # 扫描器模板
        self.scanner_templates = self._load_scanner_templates()
        
        # 设置日志
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def _load_scanner_templates(self) -> Dict[str, str]:
        """加载扫描器模板"""
        templates = {}
        
        # 基础扫描器模板
        templates['base_scanner'] = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动生成的{{ service_name }}扫描器
生成时间: {{ generation_time }}
基于模式: {{ pattern_id }}
"""

import psutil
import time
import json
import logging
import re
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path


class {{ class_name }}Scanner:
    """{{ service_name }}异常扫描器 - 基于异常模式检测"""
    
    def __init__(self, config_file: str = None):
        """初始化扫描器"""
        self.service_name = "{{ service_name }}"
        self.pattern_id = "{{ pattern_id }}"
        self.severity = "{{ severity }}"
        self.confidence = {{ confidence }}
        
        # 检测阈值（基于异常模式）
        self.thresholds = {{ thresholds }}
        
        # 日志关键词（基于异常模式）
        self.error_keywords = {{ error_keywords }}
        
        # 日志文件路径
        self.log_paths = {{ log_paths }}
        
        # 检测规则（基于异常模式）
        self.detection_rules = {{ detection_rules }}
        
        # 设置日志
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # 扫描结果
        self.scan_results = []
        
        # 异常模式统计
        self.pattern_statistics = {
            'total_checks': 0,
            'anomalies_detected': 0,
            'pattern_matches': 0
        }
    
    def check_process_metrics(self) -> Dict[str, Any]:
        """检查进程指标"""
        results = {
            'process_found': False,
            'metrics': {},
            'anomalies': [],
            'status': 'normal'
        }
        
        try:
            # 查找目标进程
            target_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    if "{{ service_name }}" in proc.info['name'].lower():
                        target_processes.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if not target_processes:
                results['status'] = 'service_not_found'
                return results
            
            results['process_found'] = True
            
            # 检查每个进程
            for proc in target_processes:
                try:
                    proc_info = proc.info
                    proc_obj = psutil.Process(proc_info['pid'])
                    
                    # 获取详细指标
                    cpu_percent = proc_obj.cpu_percent()
                    memory_percent = proc_obj.memory_percent()
                    memory_rss = proc_obj.memory_info().rss
                    
                    try:
                        connections = len(proc_obj.connections())
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        connections = 0
                    
                    process_metrics = {
                        'pid': proc_info['pid'],
                        'name': proc_info['name'],
                        'cpu_percent': cpu_percent,
                        'memory_percent': memory_percent,
                        'memory_rss': memory_rss,
                        'connections': connections,
                        'status': proc_obj.status()
                    }
                    
                    results['metrics'][proc_info['pid']] = process_metrics
                    
                    # 检查异常条件
                    anomalies = self._check_metric_anomalies(process_metrics)
                    if anomalies:
                        results['anomalies'].extend(anomalies)
                        results['status'] = 'anomaly_detected'
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    self.logger.warning(f"无法访问进程 {proc_info.get('pid')}: {e}")
                    continue
        
        except Exception as e:
            self.logger.error(f"检查进程指标失败: {e}")
            results['status'] = 'check_failed'
        
        return results
    
    def check_system_metrics(self) -> Dict[str, Any]:
        """检查系统指标"""
        results = {
            'metrics': {},
            'anomalies': [],
            'status': 'normal'
        }
        
        try:
            # 收集系统指标
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            net_connections = len(psutil.net_connections())
            
            system_metrics = {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'disk_usage_percent': disk.percent,
                'network_connections': net_connections,
                'timestamp': datetime.now().isoformat()
            }
            
            results['metrics'] = system_metrics
            
            # 检查系统异常
            anomalies = self._check_system_anomalies(system_metrics)
            if anomalies:
                results['anomalies'].extend(anomalies)
                results['status'] = 'anomaly_detected'
        
        except Exception as e:
            self.logger.error(f"检查系统指标失败: {e}")
            results['status'] = 'check_failed'
        
        return results
    
    def check_log_anomalies(self) -> Dict[str, Any]:
        """检查日志异常"""
        results = {
            'logs_checked': [],
            'anomalies': [],
            'status': 'normal'
        }
        
        # 保存日志分析结果供其他方法使用
        self.log_analysis_results = []
        
        for log_path in self.log_paths:
            try:
                if not Path(log_path).exists():
                    continue
                
                log_result = self._analyze_log_file(log_path)
                # 精简日志结果，只保留关键信息
                simplified_log_result = {
                    'log_path': log_result.get('log_path', ''),
                    'lines_checked': log_result.get('lines_checked', 0),
                    'pattern_matches': log_result.get('pattern_matches', 0),
                    'status': log_result.get('status', 'unknown'),
                    'recent_errors_count': len(log_result.get('recent_errors', [])),
                    'anomalies_count': len(log_result.get('anomalies', []))
                }
                results['logs_checked'].append(simplified_log_result)
                self.log_analysis_results.append(simplified_log_result)
                
                if log_result.get('anomalies'):
                    results['anomalies'].extend(log_result['anomalies'])
                    results['status'] = 'anomaly_detected'
            
            except Exception as e:
                self.logger.error(f"分析日志文件失败 {log_path}: {e}")
        
        return results
    
    def _check_metric_anomalies(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """基于异常模式检查指标异常"""
        anomalies = []
        self.pattern_statistics['total_checks'] += 1
        
        # 基于异常模式的阈值检查
        for metric_name, current_value in metrics.items():
            if metric_name in self.thresholds:
                threshold = self.thresholds[metric_name]
                
                # 检查是否超过阈值
                if current_value > threshold:
                    anomaly = {
                        'type': f'{metric_name}_threshold_exceeded',
                        'metric': metric_name,
                        'current_value': current_value,
                        'threshold': threshold,
                        'severity': 'high' if current_value > threshold * 1.5 else 'medium',
                        'pattern_based': True,
                        'description': f'{metric_name} 超过异常模式阈值: {current_value} > {threshold}'
                    }
                    anomalies.append(anomaly)
                    self.pattern_statistics['anomalies_detected'] += 1
                    self.pattern_statistics['pattern_matches'] += 1
        
        # 基于检测规则的复合检查
        for rule in self.detection_rules:
            if self._evaluate_detection_rule(rule, metrics):
                anomaly = {
                    'type': 'pattern_rule_triggered',
                    'rule': rule.get('name', 'unknown'),
                    'severity': rule.get('severity', 'medium'),
                    'pattern_based': True,
                    'description': f'触发异常模式规则: {rule.get("description", "未知规则")}'
                }
                anomalies.append(anomaly)
                self.pattern_statistics['anomalies_detected'] += 1
                self.pattern_statistics['pattern_matches'] += 1
        
        return anomalies
    
    def _evaluate_detection_rule(self, rule: Dict[str, Any], metrics: Dict[str, Any]) -> bool:
        """评估检测规则"""
        try:
            rule_type = rule.get('type', 'threshold')
            
            if rule_type == 'threshold':
                metric_name = rule.get('metric')
                threshold = rule.get('threshold')
                operator = rule.get('operator', '>')
                
                if metric_name in metrics:
                    current_value = metrics[metric_name]
                    
                    if operator == '>':
                        return current_value > threshold
                    elif operator == '<':
                        return current_value < threshold
                    elif operator == '>=':
                        return current_value >= threshold
                    elif operator == '<=':
                        return current_value <= threshold
                    elif operator == '==':
                        return current_value == threshold
            
            elif rule_type == 'composite':
                conditions = rule.get('conditions', [])
                logic = rule.get('logic', 'AND')
                
                if logic == 'AND':
                    return all(self._evaluate_detection_rule(cond, metrics) for cond in conditions)
                elif logic == 'OR':
                    return any(self._evaluate_detection_rule(cond, metrics) for cond in conditions)
            
            return False
            
        except Exception as e:
            self.logger.error(f"评估检测规则失败: {e}")
            return False
        
        return anomalies
    
    def _check_system_anomalies(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """基于异常模式检查系统异常"""
        return self._check_metric_anomalies(metrics)
    
    def _analyze_log_file(self, log_path: str) -> Dict[str, Any]:
        """基于异常模式分析日志文件"""
        result = {
            'log_path': log_path,
            'lines_checked': 0,
            'recent_errors': [],
            'anomalies': [],
            'pattern_matches': 0
        }
        
        try:
            if not Path(log_path).exists():
                result['status'] = 'file_not_found'
                return result
            
            # 读取最近的日志行
            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                result['lines_checked'] = len(lines)
                
                # 检查最近的1000行
                recent_lines = lines[-1000:] if len(lines) > 1000 else lines
                
                for line in recent_lines:
                    # 基于异常模式的关键词检查（限制数量）
                    for keyword in self.error_keywords:
                        if keyword.lower() in line.lower():
                            error_info = {
                                'line': line.strip(),
                                'keyword': keyword,
                                'timestamp': datetime.now().isoformat(),
                                'pattern_based': True
                            }
                            result['recent_errors'].append(error_info)
                            result['pattern_matches'] += 1
                            
                            # 限制错误记录数量，避免文件过大
                            if len(result['recent_errors']) >= 50:
                                break
                    
                    # 基于异常模式的模式匹配
                    for rule in self.detection_rules:
                        if rule.get('type') == 'log_pattern':
                            pattern = rule.get('pattern', '')
                            if pattern and re.search(pattern, line, re.IGNORECASE):
                                anomaly = {
                                    'type': 'log_pattern_match',
                                    'rule': rule.get('name', 'unknown'),
                                    'line': line.strip(),
                                    'pattern': pattern,
                                    'severity': rule.get('severity', 'medium'),
                                    'pattern_based': True,
                                    'description': f'日志匹配异常模式: {rule.get("description", "未知模式")}'
                                }
                                result['anomalies'].append(anomaly)
                                result['pattern_matches'] += 1
            
            result['status'] = 'success'
            
        except Exception as e:
            self.logger.error(f"分析日志文件失败 {log_path}: {e}")
            result['status'] = 'error'
            result['error'] = str(e)
        
        return result
    
    def run_scan(self) -> Dict[str, Any]:
        """运行完整的异常模式扫描"""
        scan_start_time = datetime.now()
        
        self.logger.info(f"开始运行 {{ service_name }} 异常模式扫描...")
        
        # 重置统计
        self.pattern_statistics = {
            'total_checks': 0,
            'anomalies_detected': 0,
            'pattern_matches': 0
        }
        
        scan_results = {
            'service_name': self.service_name,
            'pattern_id': self.pattern_id,
            'scan_start_time': scan_start_time.isoformat(),
            'scan_end_time': None,
            'pattern_statistics': self.pattern_statistics,
            'results': {}
        }
        
        try:
            # 1. 检查系统指标
            self.logger.info("检查系统指标...")
            system_results = self.check_system_metrics()
            scan_results['results']['system_metrics'] = system_results
            
            # 2. 检查进程指标
            self.logger.info("检查进程指标...")
            process_results = self.check_process_metrics()
            scan_results['results']['process_metrics'] = process_results
            
            # 3. 检查日志异常
            self.logger.info("检查日志异常...")
            log_results = self.check_log_anomalies()
            scan_results['results']['log_anomalies'] = log_results
            
            # 4. 生成异常分析
            all_anomalies = []
            all_anomalies.extend(system_results.get('anomalies', []))
            all_anomalies.extend(process_results.get('anomalies', []))
            all_anomalies.extend(log_results.get('anomalies', []))
            
            # 计算严重程度评分
            severity_score = self._calculate_severity_score(all_anomalies)
            
            # 生成精简异常分析摘要
            anomaly_analysis = {
                'total_anomalies': len(all_anomalies),
                'severity_score': severity_score,
                'anomalies': all_anomalies[:10],  # 只保留前10个异常
                'pattern_based_detections': len([a for a in all_anomalies if a.get('pattern_based', False)]),
                'high_severity_count': len([a for a in all_anomalies if a.get('severity') == 'high']),
                'medium_severity_count': len([a for a in all_anomalies if a.get('severity') == 'medium']),
                'low_severity_count': len([a for a in all_anomalies if a.get('severity') == 'low'])
            }
            
            scan_results['results']['anomaly_analysis'] = anomaly_analysis
            
            # 5. 生成扫描摘要
            scan_results['summary'] = {
                'status': 'anomaly_detected' if all_anomalies else 'normal',
                'total_anomalies': len(all_anomalies),
                'severity_score': severity_score,
                'pattern_matches': self.pattern_statistics['pattern_matches'],
                'confidence': self.confidence,
                'recommendations': self._generate_recommendations(all_anomalies)
            }
            
        except Exception as e:
            self.logger.error(f"扫描过程中出错: {e}")
            scan_results['error'] = str(e)
            scan_results['summary'] = {
                'status': 'scan_failed',
                'error': str(e)
            }
        
        scan_results['scan_end_time'] = datetime.now().isoformat()
        
        self.logger.info(f"{{ service_name }} 扫描完成，发现 {len(all_anomalies) if 'all_anomalies' in locals() else 0} 个异常")
        
        return scan_results
    
    def _calculate_severity_score(self, anomalies: List[Dict[str, Any]]) -> float:
        """计算严重程度评分"""
        if not anomalies:
            return 0.0
        
        score = 0.0
        for anomaly in anomalies:
            severity = anomaly.get('severity', 'medium')
            if severity == 'critical':
                score += 10.0
            elif severity == 'high':
                score += 7.0
            elif severity == 'medium':
                score += 4.0
            elif severity == 'low':
                score += 1.0
        
        # 归一化到0-10分
        return min(10.0, score)
    
    def _generate_recommendations(self, anomalies: List[Dict[str, Any]]) -> List[str]:
        """基于异常生成建议"""
        recommendations = []
        
        if not anomalies:
            recommendations.append("系统运行正常，继续保持当前监控策略")
            return recommendations
        
        # 基于异常类型生成建议
        anomaly_types = [a.get('type', '') for a in anomalies]
        
        if 'cpu_threshold_exceeded' in anomaly_types:
            recommendations.append("CPU使用率异常，建议检查系统负载和进程资源使用情况")
        
        if 'memory_threshold_exceeded' in anomaly_types:
            recommendations.append("内存使用率异常，建议检查内存泄漏和优化内存配置")
        
        if 'log_pattern_match' in anomaly_types:
            recommendations.append("日志异常模式检测，建议检查服务配置和错误日志")
        
        if 'pattern_rule_triggered' in anomaly_types:
            recommendations.append("触发异常模式规则，建议根据规则描述进行相应处理")
        
        # 通用建议
        if len(anomalies) > 5:
            recommendations.append("检测到多个异常，建议进行全面的系统健康检查")
        
        return recommendations


def main():
    """主函数 - 运行扫描器"""
    scanner = {{ class_name }}Scanner()
    
    try:
        results = scanner.run_scan()
        
        # 输出结果
        print(json.dumps(results, ensure_ascii=False, indent=2))
        
        # 输出摘要
        summary = results.get('summary', {})
        print(f"\\n📊 扫描摘要:")
        print(f"  状态: {summary.get('status', 'unknown')}")
        print(f"  异常数: {summary.get('total_anomalies', 0)}")
        print(f"  严重度评分: {summary.get('severity_score', 0)}")
        print(f"  模式匹配: {summary.get('pattern_matches', 0)}")
        
        if 'recommendations' in summary:
            print(f"\\n💡 建议:")
            for rec in summary['recommendations']:
                print(f"  - {rec}")
        
        # 保存扫描结果到文件
        try:
            import os
            from pathlib import Path
            
            # 确保results目录存在
            results_dir = Path(__file__).parent / "results"
            results_dir.mkdir(exist_ok=True)
            
            # 生成文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"scan_results_{{ service_name }}_{timestamp}.json"
            filepath = results_dir / filename
            
            # 保存结果
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            print(f"\\n💾 扫描结果已保存到: {filepath}")
            
        except Exception as save_error:
            print(f"⚠️ 保存扫描结果失败: {save_error}")
        
    except Exception as e:
        print(f"❌ 扫描失败: {e}")


if __name__ == "__main__":
    main()
'''
        
        return templates
    
    def load_patterns(self) -> Dict[str, Any]:
        """加载异常模式"""
        try:
            if not self.patterns_file.exists():
                self.logger.warning("模式文件不存在")
                return {}
            
            with open(self.patterns_file, 'r', encoding='utf-8') as f:
                patterns = json.load(f)
            
            self.logger.info("异常模式加载成功")
            return patterns
            
        except Exception as e:
            self.logger.error(f"加载模式失败: {e}")
            return {}
    
    def generate_scanner_for_pattern(self, pattern: Dict[str, Any]) -> str:
        """为单个模式生成扫描器代码"""
        try:
            # 准备模板变量
            service_name = pattern.get('service', 'unknown')
            class_name = ''.join(word.capitalize() for word in service_name.split('_'))
            
            # 处理阈值
            thresholds = {}
            if 'metrics' in pattern:
                for metric_type, metric_data in pattern['metrics'].items():
                    if isinstance(metric_data, dict) and 'mean' in metric_data:
                        # 设置阈值为均值 + 标准差
                        threshold = metric_data.get('mean', 50) + metric_data.get('std', 10)
                        thresholds[metric_type] = round(threshold, 2)
            
            # 处理日志关键词 - 支持多种模式类型
            error_keywords = []
            if 'logs' in pattern and 'keywords' in pattern['logs']:
                keywords_data = pattern['logs']['keywords']
                if isinstance(keywords_data, list):
                    error_keywords = [kw.get('keyword', kw) if isinstance(kw, dict) else kw 
                                    for kw in keywords_data[:10]]  # 最多10个关键词
            elif 'top_keywords' in pattern:  # 日志模式
                keywords_data = pattern.get('top_keywords', [])
                if isinstance(keywords_data, list):
                    error_keywords = [kw.get('keyword', kw) if isinstance(kw, dict) else kw 
                                    for kw in keywords_data[:10]]  # 最多10个关键词
            
            # 设置默认日志路径
            log_paths = self._get_default_log_paths(service_name)
            
            # 生成检测规则
            detection_rules = self._generate_detection_rules(pattern)
            
            # 渲染模板
            template = Template(self.scanner_templates['base_scanner'])
            
            scanner_code = template.render(
                service_name=service_name,
                class_name=class_name,
                pattern_id=pattern.get('pattern_id', 'unknown'),
                generation_time=datetime.now().isoformat(),
                severity=pattern.get('severity', 'medium'),
                confidence=pattern.get('confidence', 0.7),
                thresholds=json.dumps(thresholds, indent=8),
                error_keywords=json.dumps(error_keywords, indent=8),
                log_paths=json.dumps(log_paths, indent=8),
                detection_rules=detection_rules
            )
            
            return scanner_code
            
        except Exception as e:
            self.logger.error(f"生成扫描器代码失败: {e}")
            return ""
    
    def _get_default_log_paths(self, service_name: str) -> List[str]:
        """获取服务的默认日志路径"""
        log_paths = []
        
        # 根据服务名推断日志路径
        if 'nginx' in service_name.lower():
            log_paths = [
                '/var/log/nginx/error.log',
                '/var/log/nginx/access.log',
                'C:/nginx/logs/error.log'
            ]
        elif 'mysql' in service_name.lower():
            log_paths = [
                '/var/log/mysql/error.log',
                '/var/log/mysqld.log',
                'C:/ProgramData/MySQL/MySQL Server 8.0/Data/mysqld.log'
            ]
        elif 'apache' in service_name.lower():
            log_paths = [
                '/var/log/apache2/error.log',
                '/var/log/httpd/error_log',
                'C:/Apache24/logs/error.log'
            ]
        elif 'redis' in service_name.lower():
            log_paths = [
                '/var/log/redis/redis-server.log',
                'C:/Redis/logs/redis.log'
            ]
        elif 'postgresql' in service_name.lower():
            log_paths = [
                '/var/log/postgresql/postgresql.log',
                'C:/Program Files/PostgreSQL/data/log/postgresql.log'
            ]
        else:
            # 通用日志路径
            log_paths = [
                f'/var/log/{service_name}.log',
                f'C:/logs/{service_name}.log'
            ]
        
        return log_paths
    
    def _generate_detection_rules(self, pattern: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成检测规则"""
        rules = []
        
        # 从条件中生成规则
        conditions = pattern.get('conditions', {})
        condition_rules = conditions.get('rules', [])
        
        for i, rule in enumerate(condition_rules):
            metric = rule.get('metric', '')
            operator = rule.get('operator', '>')
            value = rule.get('value', 0)
            weight = rule.get('weight', 0.5)
            
            # 构建条件字符串
            if metric == 'log_keywords':
                condition = f"any(keyword.lower() in line.lower() for keyword in self.error_keywords)"
                description = f"检测到日志关键词: {value}"
            else:
                condition = f"metrics.get('{metric}', 0) {operator} {value}"
                description = f"{metric} {operator} {value}"
            
            rules.append({
                'name': f'rule_{i+1}',
                'metric': f"metrics.get('{metric}', 0)",
                'condition': condition,
                'threshold': value,
                'description': description,
                'severity': 'high' if weight > 0.7 else 'medium'
            })
        
        # 为日志模式生成默认规则
        if pattern.get('pattern_type') == 'log_anomaly':
            error_count = pattern.get('error_count', 0)
            error_rate = pattern.get('error_rate', 0.0)
            
            # 错误数量规则
            if error_count > 0:
                rules.append({
                    'name': 'error_count_rule',
                    'metric': 'error_count',
                    'condition': f"error_count > {max(1, error_count // 2)}",
                    'threshold': max(1, error_count // 2),
                    'description': f"错误数量超过阈值: {max(1, error_count // 2)}",
                    'severity': pattern.get('severity', 'medium')
                })
            
            # 错误率规则
            if error_rate > 0:
                rules.append({
                    'name': 'error_rate_rule',
                    'metric': 'error_rate',
                    'condition': f"error_rate > {error_rate * 0.5}",
                    'threshold': error_rate * 0.5,
                    'description': f"错误率超过阈值: {error_rate * 0.5:.2%}",
                    'severity': pattern.get('severity', 'medium')
                })
        
        return rules
    
    def generate_all_scanners(self) -> Dict[str, str]:
        """生成所有扫描器"""
        self.logger.info("开始生成扫描器...")
        
        # 加载模式
        patterns_data = self.load_patterns()
        
        if not patterns_data:
            self.logger.warning("没有可用的模式数据")
            return {}
        
        generated_scanners = {}
        
        # 按服务分组模式
        service_patterns = self._group_patterns_by_service(patterns_data)
        
        # 为每个服务生成专门的扫描器
        for service_name, patterns in service_patterns.items():
            scanner_code = self.generate_service_scanner(service_name, patterns)
            
            if scanner_code:
                scanner_filename = f"scan_{service_name}.py"
                generated_scanners[scanner_filename] = scanner_code
                self.logger.info(f"为 {service_name} 生成专门扫描器: {scanner_filename}")
        
        return generated_scanners
    
    def _group_patterns_by_service(self, patterns_data: Dict[str, Any]) -> Dict[str, Dict[str, List]]:
        """按服务分组模式"""
        service_patterns = {}
        
        # 处理复合模式
        composite_patterns = patterns_data.get('composite_patterns', [])
        for pattern in composite_patterns:
            service_name = pattern.get('service', 'unknown')
            if service_name not in service_patterns:
                service_patterns[service_name] = {'composite': [], 'metric': [], 'log': []}
            service_patterns[service_name]['composite'].append(pattern)
        
        # 处理指标模式
        metric_patterns = patterns_data.get('metric_patterns', [])
        for pattern in metric_patterns:
            service_name = pattern.get('service', 'unknown')
            if service_name not in service_patterns:
                service_patterns[service_name] = {'composite': [], 'metric': [], 'log': []}
            service_patterns[service_name]['metric'].append(pattern)
        
        # 处理日志模式
        log_patterns = patterns_data.get('log_patterns', [])
        for pattern in log_patterns:
            service_name = pattern.get('service', 'unknown')
            if service_name not in service_patterns:
                service_patterns[service_name] = {'composite': [], 'metric': [], 'log': []}
            service_patterns[service_name]['log'].append(pattern)
        
        return service_patterns
    
    def generate_service_scanner(self, service_name: str, patterns: Dict[str, List]) -> str:
        """为特定服务生成专门的扫描器"""
        try:
            # 准备模板变量
            class_name = ''.join(word.capitalize() for word in service_name.split('_'))
            
            # 合并所有模式的检测规则
            all_detection_rules = []
            all_thresholds = {}
            all_error_keywords = []
            
            # 处理复合模式
            for pattern in patterns.get('composite', []):
                rules = self._generate_detection_rules(pattern)
                all_detection_rules.extend(rules)
                
                # 合并阈值
                if 'thresholds' in pattern:
                    all_thresholds.update(pattern['thresholds'])
                
                # 合并关键词
                if 'error_keywords' in pattern:
                    all_error_keywords.extend(pattern['error_keywords'])
            
            # 处理指标模式
            for pattern in patterns.get('metric', []):
                rules = self._generate_detection_rules(pattern)
                all_detection_rules.extend(rules)
                
                # 合并阈值
                if 'metrics' in pattern:
                    for metric_type, metric_data in pattern['metrics'].items():
                        if isinstance(metric_data, dict) and 'mean' in metric_data:
                            threshold = metric_data.get('mean', 50) + metric_data.get('std', 10)
                            all_thresholds[metric_type] = round(threshold, 2)
            
            # 处理日志模式
            for pattern in patterns.get('log', []):
                rules = self._generate_detection_rules(pattern)
                all_detection_rules.extend(rules)
                
                # 合并关键词
                if 'top_keywords' in pattern:
                    keywords_data = pattern.get('top_keywords', [])
                    if isinstance(keywords_data, list):
                        keywords = [kw.get('keyword', kw) if isinstance(kw, dict) else kw 
                                  for kw in keywords_data[:10]]
                        all_error_keywords.extend(keywords)
            
            # 去重
            all_error_keywords = list(set(all_error_keywords))
            
            # 设置默认日志路径
            log_paths = self._get_default_log_paths(service_name)
            
            # 渲染模板
            template = Template(self.scanner_templates['base_scanner'])
            
            scanner_code = template.render(
                service_name=service_name,
                class_name=class_name,
                pattern_id=f"{service_name}_comprehensive",
                generation_time=datetime.now().isoformat(),
                severity=self._determine_overall_severity(patterns),
                confidence=self._calculate_overall_confidence(patterns),
                thresholds=json.dumps(all_thresholds, indent=8),
                error_keywords=json.dumps(all_error_keywords, indent=8),
                log_paths=json.dumps(log_paths, indent=8),
                detection_rules=all_detection_rules
            )
            
            return scanner_code
            
        except Exception as e:
            self.logger.error(f"生成 {service_name} 扫描器失败: {e}")
            return ""
    
    def _determine_overall_severity(self, patterns: Dict[str, List]) -> str:
        """确定整体严重程度"""
        severities = []
        
        for pattern_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                severity = pattern.get('severity', 'medium')
                severities.append(severity)
        
        if not severities:
            return 'medium'
        
        # 如果有任何严重异常，返回严重
        if 'critical' in severities:
            return 'critical'
        elif 'high' in severities:
            return 'high'
        elif 'medium' in severities:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_overall_confidence(self, patterns: Dict[str, List]) -> float:
        """计算整体置信度"""
        confidences = []
        
        for pattern_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                confidence = pattern.get('confidence', 0.7)
                confidences.append(confidence)
        
        if not confidences:
            return 0.7
        
        return round(sum(confidences) / len(confidences), 2)
    
    def save_scanners(self, scanners: Dict[str, str]):
        """保存生成的扫描器文件"""
        try:
            for filename, code in scanners.items():
                scanner_path = self.scanners_dir / filename
                
                with open(scanner_path, 'w', encoding='utf-8') as f:
                    f.write(code)
                
                # 设置可执行权限（Unix系统）
                try:
                    scanner_path.chmod(0o755)
                except (AttributeError, OSError):
                    pass  # Windows系统或权限设置失败
                
                self.logger.info(f"扫描器已保存: {scanner_path}")
            
            # 生成扫描器索引文件
            self._generate_scanner_index(list(scanners.keys()))
            
        except Exception as e:
            self.logger.error(f"保存扫描器失败: {e}")
    
    def _generate_scanner_index(self, scanner_files: List[str]):
        """生成扫描器索引文件"""
        index_content = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
扫描器索引 - 管理所有生成的扫描器
生成时间: {datetime.now().isoformat()}
"""

import subprocess
import sys
from pathlib import Path


def run_scanner(scanner_name: str):
    """运行指定的扫描器"""
    scanner_path = Path(__file__).parent / f"{{scanner_name}}.py"
    
    if not scanner_path.exists():
        print(f"❌ 扫描器不存在: {{scanner_path}}")
        return False
    
    try:
        result = subprocess.run([sys.executable, str(scanner_path)], 
                              capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print(f"错误: {{result.stderr}}")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ 运行扫描器失败: {{e}}")
        return False


def run_all_scanners():
    """运行所有扫描器"""
    scanners = {scanner_files}
    
    print(f"🔍 开始运行 {{len(scanners)}} 个扫描器...")
    
    success_count = 0
    for scanner in scanners:
        scanner_name = scanner.replace('.py', '')
        print(f"\\n{'='*50}")
        print(f"运行扫描器: {{scanner_name}}")
        print(f"{'='*50}")
        
        if run_scanner(scanner_name):
            success_count += 1
    
    print(f"\\n📊 扫描完成: {{success_count}}/{{len(scanners)}} 个扫描器成功运行")


def list_scanners():
    """列出所有可用的扫描器"""
    scanners = {scanner_files}
    
    print("📋 可用的扫描器:")
    for i, scanner in enumerate(scanners, 1):
        scanner_name = scanner.replace('.py', '').replace('scan_', '')
        print(f"  {{i}}. {{scanner_name}} ({{scanner}})")


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
'''
        
        index_path = self.scanners_dir / "scanner_index.py"
        
        try:
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(index_content)
            
            # 设置可执行权限
            try:
                index_path.chmod(0o755)
            except (AttributeError, OSError):
                pass
            
            self.logger.info(f"扫描器索引已保存: {index_path}")
            
        except Exception as e:
            self.logger.error(f"生成扫描器索引失败: {e}")


def main():
    """主函数演示"""
    generator = ScannerGenerator(output_dir="data", scanners_dir="/home/denerate/abnormal_pattern_detect/scanners")
    
    print("🔧 开始生成扫描器...")
    
    try:
        # 生成所有扫描器
        scanners = generator.generate_all_scanners()
        
        if not scanners:
            print("⚠️ 没有生成任何扫描器，请先运行模式提取")
            return
        
        # 保存扫描器文件
        generator.save_scanners(scanners)
        
        # 显示摘要
        print(f"\n📊 扫描器生成摘要:")
        print(f"  - 生成扫描器数量: {len(scanners)}")
        print(f"  - 保存目录: {generator.scanners_dir}")
        
        print(f"\n🔧 生成的扫描器:")
        for filename in scanners.keys():
            service_name = filename.replace('scan_', '').replace('.py', '')
            print(f"  - {service_name}: {filename}")
        
        print(f"\n💡 使用方法:")
        print(f"  cd {generator.scanners_dir}")
        print(f"  python scanner_index.py list      # 查看所有扫描器")
        print(f"  python scanner_index.py run-all   # 运行所有扫描器")
        
    except Exception as e:
        print(f"❌ 生成扫描器失败: {e}")


if __name__ == "__main__":
    main() 