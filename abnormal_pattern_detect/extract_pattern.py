#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
异常模式提取模块 - 从异常数据中归纳故障特征组合
"""

import pandas as pd
import numpy as np
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
from collections import defaultdict, Counter
import re


class PatternExtractor:
    """异常模式提取器"""
    
    def __init__(self, output_dir: str = "data"):
        """初始化模式提取器"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # 输入文件
        self.anomalies_file = self.output_dir / "anomalies.csv"
        self.anomaly_summary_file = self.output_dir / "anomaly_summary.json"
        self.parsed_logs_file = self.output_dir / "parsed_logs.json"
        
        # 输出文件
        self.patterns_file = self.output_dir / "extracted_patterns.json"
        
        # 模式提取配置
        self.metric_thresholds = {
            'cpu_percent': {'high': 80, 'critical': 90},
            'memory_percent': {'high': 75, 'critical': 85},
            'disk_usage_percent': {'high': 80, 'critical': 90},
            'network_connections': {'high': 1000, 'critical': 2000}
        }
        
        # 关键词权重
        self.keyword_weights = {
            'critical': ['fatal', 'critical', 'emergency', 'panic', 'corrupt', 'crash'],
            'error': ['error', 'failed', 'failure', 'timeout', '502', '503', '504', '500'],
            'warning': ['warning', 'slow', 'retry', 'deprecated']
        }
        
        # 设置日志
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def load_anomaly_data(self) -> Dict[str, Any]:
        """加载异常检测数据"""
        anomaly_data = {}
        
        try:
            # 加载异常摘要
            if self.anomaly_summary_file.exists():
                with open(self.anomaly_summary_file, 'r', encoding='utf-8') as f:
                    anomaly_data = json.load(f)
                self.logger.info("异常数据加载成功")
            else:
                self.logger.warning("异常摘要文件不存在")
                
        except Exception as e:
            self.logger.error(f"加载异常数据失败: {e}")
        
        return anomaly_data
    
    def extract_metric_patterns(self, anomalies: List[Dict]) -> List[Dict[str, Any]]:
        """提取指标异常模式"""
        patterns = []
        
        if not anomalies:
            return patterns
        
        # 按服务分组
        by_service = defaultdict(list)
        for anomaly in anomalies:
            service = anomaly.get('service', 'system')
            by_service[service].append(anomaly)
        
        # 为每个服务提取模式
        for service, service_anomalies in by_service.items():
            if len(service_anomalies) < 2:  # 至少需要2个异常样本
                continue
            
            # 提取指标特征
            metrics_data = []
            for anomaly in service_anomalies:
                metrics = anomaly.get('metrics', {})
                if metrics:
                    metrics_data.append(metrics)
            
            if not metrics_data:
                continue
            
            # 计算统计特征
            pattern = self._calculate_metric_statistics(service, metrics_data)
            
            # 添加时间特征
            timestamps = [anomaly.get('timestamp') for anomaly in service_anomalies if anomaly.get('timestamp')]
            pattern['temporal_features'] = self._analyze_temporal_patterns(timestamps)
            
            # 添加严重程度分布
            severities = [anomaly.get('severity', 'medium') for anomaly in service_anomalies]
            pattern['severity_distribution'] = dict(Counter(severities))
            
            # 设置模式元数据
            pattern.update({
                'pattern_id': f"{service}_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'pattern_type': 'metric_anomaly',
                'service': service,
                'sample_count': len(service_anomalies),
                'extraction_time': datetime.now().isoformat()
            })
            
            patterns.append(pattern)
        
        return patterns
    
    def extract_log_patterns(self, log_anomalies: List[Dict]) -> List[Dict[str, Any]]:
        """提取日志异常模式"""
        patterns = []
        
        try:
            # 加载详细日志数据
            if not self.parsed_logs_file.exists():
                return patterns
            
            with open(self.parsed_logs_file, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
            
            # 按服务分析日志模式
            for service, service_data in log_data.get('services', {}).items():
                if service not in [anomaly.get('service') for anomaly in log_anomalies]:
                    continue  # 跳过没有异常的服务
                
                # 收集错误日志
                error_messages = []
                error_keywords = Counter()
                
                for file_data in service_data.get('files', []):
                    for entry in file_data.get('log_entries', []):
                        if entry.get('level') in ['error', 'critical']:
                            error_messages.append(entry.get('message', ''))
                            
                            # 提取关键词
                            keywords = self._extract_keywords_from_message(entry.get('message', ''))
                            error_keywords.update(keywords)
                
                if error_messages:
                    pattern = self._analyze_log_patterns(service, error_messages, error_keywords)
                    
                    # 查找对应的日志异常
                    service_log_anomaly = next(
                        (anomaly for anomaly in log_anomalies if anomaly.get('service') == service), 
                        {}
                    )
                    
                    pattern.update({
                        'pattern_id': f"{service}_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        'pattern_type': 'log_anomaly',
                        'service': service,
                        'error_count': len(error_messages),
                        'severity': service_log_anomaly.get('severity', 'medium'),
                        'extraction_time': datetime.now().isoformat()
                    })
                    
                    patterns.append(pattern)
        
        except Exception as e:
            self.logger.error(f"提取日志模式失败: {e}")
        
        return patterns
    
    def extract_composite_patterns(self, metric_patterns: List[Dict], log_patterns: List[Dict]) -> List[Dict[str, Any]]:
        """提取复合模式（指标+日志）"""
        composite_patterns = []
        
        # 按服务匹配指标和日志模式
        metric_by_service = {p['service']: p for p in metric_patterns}
        log_by_service = {p['service']: p for p in log_patterns}
        
        common_services = set(metric_by_service.keys()) & set(log_by_service.keys())
        
        for service in common_services:
            metric_pattern = metric_by_service[service]
            log_pattern = log_by_service[service]
            
            # 创建复合模式
            composite_pattern = {
                'pattern_id': f"{service}_composite_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'pattern_name': f"{service}综合异常模式",
                'pattern_type': 'composite_anomaly',
                'service': service,
                'extraction_time': datetime.now().isoformat(),
                
                # 指标特征
                'metrics': {
                    'cpu': metric_pattern.get('cpu_statistics', {}),
                    'memory': metric_pattern.get('memory_statistics', {}),
                    'thresholds': self._determine_thresholds(metric_pattern)
                },
                
                # 日志特征
                'logs': {
                    'keywords': log_pattern.get('top_keywords', []),
                    'patterns': log_pattern.get('common_patterns', []),
                    'frequency': log_pattern.get('error_frequency', 0),
                    'error_rate': log_pattern.get('error_rate', 0)
                },
                
                # 复合条件
                'conditions': self._generate_composite_conditions(metric_pattern, log_pattern),
                
                # 严重程度
                'severity': self._determine_composite_severity(metric_pattern, log_pattern),
                
                # 置信度
                'confidence': self._calculate_pattern_confidence(metric_pattern, log_pattern)
            }
            
            composite_patterns.append(composite_pattern)
        
        return composite_patterns
    
    def _calculate_metric_statistics(self, service: str, metrics_data: List[Dict]) -> Dict[str, Any]:
        """计算指标统计特征"""
        if not metrics_data:
            return {}
        
        df = pd.DataFrame(metrics_data)
        statistics = {}
        
        for metric in ['cpu_percent', 'memory_percent', 'disk_usage_percent', 'network_connections']:
            if metric in df.columns:
                values = df[metric].dropna()
                if len(values) > 0:
                    statistics[f'{metric.replace("_percent", "")}_statistics'] = {
                        'mean': float(np.mean(values)),
                        'std': float(np.std(values)),
                        'min': float(np.min(values)),
                        'max': float(np.max(values)),
                        'median': float(np.median(values)),
                        'samples': len(values)
                    }
        
        return statistics
    
    def _analyze_temporal_patterns(self, timestamps: List[str]) -> Dict[str, Any]:
        """分析时间模式"""
        if not timestamps:
            return {}
        
        # 解析时间戳
        parsed_times = []
        for ts in timestamps:
            if ts:
                try:
                    parsed_times.append(pd.to_datetime(ts))
                except:
                    continue
        
        if len(parsed_times) < 2:
            return {}
        
        # 计算时间间隔
        intervals = [(parsed_times[i+1] - parsed_times[i]).total_seconds() 
                    for i in range(len(parsed_times)-1)]
        
        # 分析小时分布
        hours = [t.hour for t in parsed_times]
        hour_distribution = dict(Counter(hours))
        
        return {
            'time_span_hours': (max(parsed_times) - min(parsed_times)).total_seconds() / 3600,
            'avg_interval_minutes': np.mean(intervals) / 60 if intervals else 0,
            'hour_distribution': hour_distribution,
            'peak_hours': [h for h, count in Counter(hours).most_common(3)]
        }
    
    def _extract_keywords_from_message(self, message: str) -> List[str]:
        """从日志消息中提取关键词"""
        if not message:
            return []
        
        # 转换为小写并提取单词
        words = re.findall(r'\b\w{3,}\b', message.lower())
        
        # 过滤常见词和提取关键词
        keywords = []
        for category, category_keywords in self.keyword_weights.items():
            for keyword in category_keywords:
                if keyword in message.lower():
                    keywords.append(keyword)
        
        # 添加其他重要词（数字、状态码等）
        numbers = re.findall(r'\b\d{3,}\b', message)
        keywords.extend(numbers)
        
        return list(set(keywords))  # 去重
    
    def _analyze_log_patterns(self, service: str, error_messages: List[str], 
                            error_keywords: Counter) -> Dict[str, Any]:
        """分析日志模式"""
        if not error_messages:
            return {}
        
        # 提取常见模式
        common_patterns = []
        
        # 查找重复的错误片段
        message_parts = defaultdict(int)
        for msg in error_messages:
            # 提取关键错误片段（去掉变量部分）
            pattern = re.sub(r'\d+', 'NUM', msg)  # 替换数字
            pattern = re.sub(r'\b\w+\.\w+\.\w+\.\w+\b', 'IP', pattern)  # 替换IP
            pattern = re.sub(r'/\w+/', '/PATH/', pattern)  # 替换路径
            
            if len(pattern) > 20:  # 只保留较长的模式
                message_parts[pattern] += 1
        
        # 找出出现频率高的模式
        for pattern, count in message_parts.items():
            if count >= max(2, len(error_messages) * 0.1):  # 至少出现2次或10%
                common_patterns.append({
                    'pattern': pattern[:100],  # 限制长度
                    'frequency': count,
                    'percentage': count / len(error_messages)
                })
        
        # 计算错误频率
        total_messages = len(error_messages)
        error_frequency = total_messages
        
        return {
            'total_errors': total_messages,
            'error_frequency': error_frequency,
            'top_keywords': [{'keyword': kw, 'count': count} 
                           for kw, count in error_keywords.most_common(10)],
            'common_patterns': common_patterns[:5],  # 最多5个常见模式
            'error_rate': min(1.0, total_messages / 100)  # 简化的错误率计算
        }
    
    def _determine_thresholds(self, metric_pattern: Dict) -> Dict[str, float]:
        """确定指标阈值"""
        thresholds = {}
        
        for metric_key, stats in metric_pattern.items():
            if metric_key.endswith('_statistics') and isinstance(stats, dict):
                metric_name = metric_key.replace('_statistics', '')
                
                # 基于统计数据设置阈值
                mean = stats.get('mean', 0)
                std = stats.get('std', 0)
                
                # 设置为均值 - 1个标准差作为异常阈值
                threshold = max(0, mean - std)
                
                # 应用默认阈值限制
                if metric_name in ['cpu', 'memory']:
                    threshold = max(threshold, self.metric_thresholds.get(f'{metric_name}_percent', {}).get('high', 80))
                
                thresholds[metric_name] = threshold
        
        return thresholds
    
    def _generate_composite_conditions(self, metric_pattern: Dict, log_pattern: Dict) -> Dict[str, Any]:
        """生成复合条件"""
        conditions = {
            'logical_operator': 'and',
            'rules': []
        }
        
        # 添加指标条件
        thresholds = self._determine_thresholds(metric_pattern)
        for metric, threshold in thresholds.items():
            conditions['rules'].append({
                'metric': f'{metric}_percent',
                'operator': '>',
                'value': threshold,
                'weight': 0.6
            })
        
        # 添加日志条件
        top_keywords = log_pattern.get('top_keywords', [])
        if top_keywords:
            main_keyword = top_keywords[0]['keyword']
            conditions['rules'].append({
                'metric': 'log_keywords',
                'operator': 'contains',
                'value': main_keyword,
                'weight': 0.4
            })
        
        return conditions
    
    def _determine_composite_severity(self, metric_pattern: Dict, log_pattern: Dict) -> str:
        """确定复合模式严重程度"""
        # 基于指标严重程度
        metric_severity = 'medium'
        for stats_key, stats in metric_pattern.items():
            if stats_key.endswith('_statistics') and isinstance(stats, dict):
                max_value = stats.get('max', 0)
                if max_value > 90:
                    metric_severity = 'critical'
                elif max_value > 80:
                    metric_severity = 'high'
        
        # 基于日志严重程度
        log_severity = 'medium'
        error_rate = log_pattern.get('error_rate', 0)
        if error_rate > 0.5:
            log_severity = 'critical'
        elif error_rate > 0.2:
            log_severity = 'high'
        
        # 取最高严重程度
        severity_levels = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
        max_severity_level = max(
            severity_levels.get(metric_severity, 2),
            severity_levels.get(log_severity, 2)
        )
        
        for severity, level in severity_levels.items():
            if level == max_severity_level:
                return severity
        
        return 'medium'
    
    def _calculate_pattern_confidence(self, metric_pattern: Dict, log_pattern: Dict) -> float:
        """计算模式置信度"""
        confidence_factors = []
        
        # 基于样本数量
        metric_samples = metric_pattern.get('sample_count', 0)
        if metric_samples >= 10:
            confidence_factors.append(0.9)
        elif metric_samples >= 5:
            confidence_factors.append(0.7)
        else:
            confidence_factors.append(0.5)
        
        # 基于日志错误数量
        log_errors = log_pattern.get('total_errors', 0)
        if log_errors >= 20:
            confidence_factors.append(0.9)
        elif log_errors >= 10:
            confidence_factors.append(0.7)
        else:
            confidence_factors.append(0.5)
        
        # 基于模式一致性
        common_patterns = log_pattern.get('common_patterns', [])
        if common_patterns and max(p.get('percentage', 0) for p in common_patterns) > 0.5:
            confidence_factors.append(0.8)
        else:
            confidence_factors.append(0.6)
        
        return min(0.95, np.mean(confidence_factors))
    
    def extract_all_patterns(self) -> Dict[str, Any]:
        """提取所有异常模式"""
        self.logger.info("开始提取异常模式...")
        
        # 加载异常数据
        anomaly_data = self.load_anomaly_data()
        
        if not anomaly_data:
            self.logger.warning("没有异常数据可用于模式提取")
            return {'patterns': [], 'summary': {}}
        
        # 提取指标模式
        system_anomalies = anomaly_data.get('system_anomalies', {}).get('anomalies', [])
        process_anomalies = anomaly_data.get('process_anomalies', {}).get('anomalies', [])
        all_metric_anomalies = system_anomalies + process_anomalies
        
        metric_patterns = self.extract_metric_patterns(all_metric_anomalies)
        
        # 提取日志模式
        log_anomalies = anomaly_data.get('log_anomalies', {}).get('anomalies', [])
        log_patterns = self.extract_log_patterns(log_anomalies)
        
        # 提取复合模式
        composite_patterns = self.extract_composite_patterns(metric_patterns, log_patterns)
        
        # 合并所有模式
        all_patterns = {
            'extraction_time': datetime.now().isoformat(),
            'metric_patterns': metric_patterns,
            'log_patterns': log_patterns,
            'composite_patterns': composite_patterns,
            'summary': {
                'total_patterns': len(metric_patterns) + len(log_patterns) + len(composite_patterns),
                'metric_patterns_count': len(metric_patterns),
                'log_patterns_count': len(log_patterns),
                'composite_patterns_count': len(composite_patterns),
                'services_analyzed': list(set(
                    [p.get('service') for p in metric_patterns + log_patterns + composite_patterns]
                ))
            }
        }
        
        return all_patterns
    
    def save_patterns(self, patterns: Dict[str, Any]):
        """保存提取的模式（支持追加模式）"""
        try:
            # 加载现有模式（如果存在）
            existing_patterns = {}
            if self.patterns_file.exists():
                try:
                    with open(self.patterns_file, 'r', encoding='utf-8') as f:
                        existing_patterns = json.load(f)
                    self.logger.info("加载现有模式文件")
                except Exception as e:
                    self.logger.warning(f"加载现有模式文件失败: {e}")
            
            # 合并模式
            merged_patterns = self._merge_patterns(existing_patterns, patterns)
            
            # 保存合并后的模式
            with open(self.patterns_file, 'w', encoding='utf-8') as f:
                json.dump(merged_patterns, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"异常模式已保存到: {self.patterns_file}")
            
        except Exception as e:
            self.logger.error(f"保存模式失败: {e}")
    
    def _merge_patterns(self, existing_patterns: Dict[str, Any], new_patterns: Dict[str, Any]) -> Dict[str, Any]:
        """合并现有模式和新模式"""
        merged = {
            'extraction_time': new_patterns.get('extraction_time', datetime.now().isoformat()),
            'metric_patterns': [],
            'log_patterns': [],
            'composite_patterns': [],
            'summary': {}
        }
        
        # 合并指标模式
        existing_metric = existing_patterns.get('metric_patterns', [])
        new_metric = new_patterns.get('metric_patterns', [])
        merged['metric_patterns'] = existing_metric + new_metric
        
        # 合并日志模式
        existing_log = existing_patterns.get('log_patterns', [])
        new_log = new_patterns.get('log_patterns', [])
        merged['log_patterns'] = existing_log + new_log
        
        # 合并复合模式
        existing_composite = existing_patterns.get('composite_patterns', [])
        new_composite = new_patterns.get('composite_patterns', [])
        merged['composite_patterns'] = existing_composite + new_composite
        
        # 更新摘要
        merged['summary'] = {
            'total_patterns': len(merged['metric_patterns']) + len(merged['log_patterns']) + len(merged['composite_patterns']),
            'metric_patterns_count': len(merged['metric_patterns']),
            'log_patterns_count': len(merged['log_patterns']),
            'composite_patterns_count': len(merged['composite_patterns']),
            'services_analyzed': list(set(
                [p.get('service') for p in merged['metric_patterns'] + merged['log_patterns'] + merged['composite_patterns']]
            ))
        }
        
        self.logger.info(f"模式合并完成: 现有{len(existing_metric + existing_log + existing_composite)}个，新增{len(new_metric + new_log + new_composite)}个")
        
        return merged


def main():
    """主函数演示"""
    extractor = PatternExtractor(output_dir="data")
    
    print("🔍 开始提取异常模式...")
    
    try:
        # 提取所有模式
        patterns = extractor.extract_all_patterns()
        
        # 保存模式
        extractor.save_patterns(patterns)
        
        # 显示摘要
        summary = patterns['summary']
        print(f"\n📊 模式提取摘要:")
        print(f"  - 总模式数: {summary['total_patterns']}")
        print(f"  - 指标模式: {summary['metric_patterns_count']}")
        print(f"  - 日志模式: {summary['log_patterns_count']}")
        print(f"  - 复合模式: {summary['composite_patterns_count']}")
        print(f"  - 分析服务: {', '.join(summary['services_analyzed'])}")
        
        # 显示复合模式详情
        if patterns['composite_patterns']:
            print(f"\n🔗 复合模式详情:")
            for pattern in patterns['composite_patterns'][:3]:
                print(f"  - {pattern['pattern_name']} ({pattern['service']})")
                print(f"    严重程度: {pattern['severity']}, 置信度: {pattern['confidence']:.2f}")
                
                conditions = pattern.get('conditions', {}).get('rules', [])
                if conditions:
                    print(f"    条件: {len(conditions)} 个规则")
        
        print(f"\n💾 模式已保存到: {extractor.patterns_file}")
        
    except Exception as e:
        print(f"❌ 模式提取失败: {e}")


if __name__ == "__main__":
    main() 