#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动生成的loki扫描器
生成时间: 2025-08-13T02:09:27.885214
基于模式: loki_comprehensive
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


class LokiScanner:
    """loki异常扫描器 - 基于异常模式检测"""
    
    def __init__(self, config_file: str = None):
        """初始化扫描器"""
        self.service_name = "loki"
        self.pattern_id = "loki_comprehensive"
        self.severity = "critical"
        self.confidence = 0.7
        
        # 检测阈值（基于异常模式）
        self.thresholds = {}
        
        # 日志关键词（基于异常模式）
        self.error_keywords = [
        "185",
        "504",
        "132",
        "305",
        "502",
        "failed",
        "2025",
        "281",
        "192",
        "timeout",
        "318",
        "106",
        "334",
        "error",
        "503",
        "443",
        "500",
        "126",
        "107"
]
        
        # 日志文件路径
        self.log_paths = [
        "/var/log/loki.log",
        "C:/logs/loki.log"
]
        
        # 检测规则（基于异常模式）
        self.detection_rules = [{'name': 'error_count_rule', 'metric': 'error_count', 'condition': 'error_count > 143', 'threshold': 143, 'description': '错误数量超过阈值: 143', 'severity': 'high'}, {'name': 'error_rate_rule', 'metric': 'error_rate', 'condition': 'error_rate > 0.5', 'threshold': 0.5, 'description': '错误率超过阈值: 50.00%', 'severity': 'high'}, {'name': 'error_count_rule', 'metric': 'error_count', 'condition': 'error_count > 143', 'threshold': 143, 'description': '错误数量超过阈值: 143', 'severity': 'high'}, {'name': 'error_rate_rule', 'metric': 'error_rate', 'condition': 'error_rate > 0.5', 'threshold': 0.5, 'description': '错误率超过阈值: 50.00%', 'severity': 'high'}, {'name': 'error_count_rule', 'metric': 'error_count', 'condition': 'error_count > 143', 'threshold': 143, 'description': '错误数量超过阈值: 143', 'severity': 'high'}, {'name': 'error_rate_rule', 'metric': 'error_rate', 'condition': 'error_rate > 0.5', 'threshold': 0.5, 'description': '错误率超过阈值: 50.00%', 'severity': 'high'}, {'name': 'error_count_rule', 'metric': 'error_count', 'condition': 'error_count > 143', 'threshold': 143, 'description': '错误数量超过阈值: 143', 'severity': 'high'}, {'name': 'error_rate_rule', 'metric': 'error_rate', 'condition': 'error_rate > 0.5', 'threshold': 0.5, 'description': '错误率超过阈值: 50.00%', 'severity': 'high'}, {'name': 'error_count_rule', 'metric': 'error_count', 'condition': 'error_count > 13', 'threshold': 13, 'description': '错误数量超过阈值: 13', 'severity': 'high'}, {'name': 'error_rate_rule', 'metric': 'error_rate', 'condition': 'error_rate > 0.135', 'threshold': 0.135, 'description': '错误率超过阈值: 13.50%', 'severity': 'high'}, {'name': 'error_count_rule', 'metric': 'error_count', 'condition': 'error_count > 69', 'threshold': 69, 'description': '错误数量超过阈值: 69', 'severity': 'critical'}, {'name': 'error_rate_rule', 'metric': 'error_rate', 'condition': 'error_rate > 0.5', 'threshold': 0.5, 'description': '错误率超过阈值: 50.00%', 'severity': 'critical'}, {'name': 'error_count_rule', 'metric': 'error_count', 'condition': 'error_count > 69', 'threshold': 69, 'description': '错误数量超过阈值: 69', 'severity': 'critical'}, {'name': 'error_rate_rule', 'metric': 'error_rate', 'condition': 'error_rate > 0.5', 'threshold': 0.5, 'description': '错误率超过阈值: 50.00%', 'severity': 'critical'}, {'name': 'error_count_rule', 'metric': 'error_count', 'condition': 'error_count > 69', 'threshold': 69, 'description': '错误数量超过阈值: 69', 'severity': 'critical'}, {'name': 'error_rate_rule', 'metric': 'error_rate', 'condition': 'error_rate > 0.5', 'threshold': 0.5, 'description': '错误率超过阈值: 50.00%', 'severity': 'critical'}, {'name': 'error_count_rule', 'metric': 'error_count', 'condition': 'error_count > 69', 'threshold': 69, 'description': '错误数量超过阈值: 69', 'severity': 'critical'}, {'name': 'error_rate_rule', 'metric': 'error_rate', 'condition': 'error_rate > 0.5', 'threshold': 0.5, 'description': '错误率超过阈值: 50.00%', 'severity': 'critical'}]
        
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
                    if "loki" in proc.info['name'].lower():
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
        
        self.logger.info(f"开始运行 loki 异常模式扫描...")
        
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
        
        self.logger.info(f"loki 扫描完成，发现 {len(all_anomalies) if 'all_anomalies' in locals() else 0} 个异常")
        
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
    scanner = LokiScanner()
    
    try:
        results = scanner.run_scan()
        
        # 输出结果
        print(json.dumps(results, ensure_ascii=False, indent=2))
        
        # 输出摘要
        summary = results.get('summary', {})
        print(f"\n📊 扫描摘要:")
        print(f"  状态: {summary.get('status', 'unknown')}")
        print(f"  异常数: {summary.get('total_anomalies', 0)}")
        print(f"  严重度评分: {summary.get('severity_score', 0)}")
        print(f"  模式匹配: {summary.get('pattern_matches', 0)}")
        
        if 'recommendations' in summary:
            print(f"\n💡 建议:")
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
            filename = f"scan_results_loki_{timestamp}.json"
            filepath = results_dir / filename
            
            # 保存结果
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            print(f"\n💾 扫描结果已保存到: {filepath}")
            
        except Exception as save_error:
            print(f"⚠️ 保存扫描结果失败: {save_error}")
        
    except Exception as e:
        print(f"❌ 扫描失败: {e}")


if __name__ == "__main__":
    main()