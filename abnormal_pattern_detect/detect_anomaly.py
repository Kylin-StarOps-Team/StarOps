#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
异常检测模块 - 使用PyOD库和Isolation Forest检测异常
"""

import pandas as pd
import numpy as np
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

try:
    from pyod.models.iforest import IForest
    from pyod.models.lof import LOF
    from pyod.models.knn import KNN
    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA
except ImportError as e:
    print(f"警告: 缺少依赖包 {e}")
    print("请运行: pip install pyod scikit-learn")


class AnomalyDetector:
    """异常检测器"""
    
    def __init__(self, output_dir: str = "data", contamination: float = 0.1):
        """
        初始化异常检测器
        
        Args:
            output_dir: 输出目录
            contamination: 异常比例估计（0.05-0.2）
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.contamination = contamination
        
        # 输入文件
        self.metrics_file = self.output_dir / "metrics.csv"
        self.process_file = self.output_dir / "processes.csv"
        self.parsed_logs_file = self.output_dir / "parsed_logs.json"
        
        # 输出文件
        self.anomalies_file = self.output_dir / "anomalies.csv"
        self.anomaly_summary_file = self.output_dir / "anomaly_summary.json"
        
        # 模型配置
        self.models = {
            'isolation_forest': IForest(contamination=contamination, random_state=42),
            'lof': LOF(contamination=contamination),
            'knn': KNN(contamination=contamination)
        }
        
        # 特征列定义
        self.system_features = [
            'cpu_percent', 'memory_percent', 'disk_usage_percent', 
            'network_connections', 'process_count'
        ]
        
        self.process_features = [
            'cpu_percent', 'memory_percent', 'memory_rss', 'connections'
        ]
        
        # 设置日志
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def load_metrics_data(self, hours_back: int = 24) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """加载指标数据"""
        try:
            # 加载系统指标
            if self.metrics_file.exists():
                system_df = pd.read_csv(self.metrics_file)
                system_df['timestamp'] = pd.to_datetime(system_df['timestamp'])
                self.logger.info(f"加载系统指标: {len(system_df)} 条记录")
            else:
                system_df = pd.DataFrame()
                self.logger.warning("系统指标文件不存在")
            
            # 加载进程指标
            if self.process_file.exists():
                process_df = pd.read_csv(self.process_file)
                process_df['timestamp'] = pd.to_datetime(process_df['timestamp'])
                self.logger.info(f"加载进程指标: {len(process_df)} 条记录")
            else:
                process_df = pd.DataFrame()
                self.logger.warning("进程指标文件不存在")
            
            # 过滤时间窗口
            if hours_back > 0:
                cutoff_time = datetime.now() - timedelta(hours=hours_back)
                if not system_df.empty:
                    system_df = system_df[system_df['timestamp'] > cutoff_time]
                if not process_df.empty:
                    process_df = process_df[process_df['timestamp'] > cutoff_time]
            
            return system_df, process_df
            
        except Exception as e:
            self.logger.error(f"加载指标数据失败: {e}")
            return pd.DataFrame(), pd.DataFrame()
    
    def preprocess_system_data(self, df: pd.DataFrame) -> Tuple[np.ndarray, pd.DataFrame]:
        """预处理系统数据"""
        if df.empty:
            return np.array([]), df
        
        # 选择特征列
        feature_df = df[self.system_features].copy()
        
        # 处理缺失值
        feature_df = feature_df.fillna(feature_df.mean())
        
        # 添加派生特征
        if len(feature_df) > 1:
            # 计算变化率
            feature_df['cpu_change'] = feature_df['cpu_percent'].diff().fillna(0)
            feature_df['memory_change'] = feature_df['memory_percent'].diff().fillna(0)
            
            # 计算移动平均
            window_size = min(5, len(feature_df))
            feature_df['cpu_ma'] = feature_df['cpu_percent'].rolling(window=window_size).mean().fillna(feature_df['cpu_percent'])
            feature_df['memory_ma'] = feature_df['memory_percent'].rolling(window=window_size).mean().fillna(feature_df['memory_percent'])
        
        # 标准化
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(feature_df)
        
        return features_scaled, feature_df
    
    def preprocess_process_data(self, df: pd.DataFrame) -> Tuple[Dict[str, np.ndarray], Dict[str, pd.DataFrame]]:
        """预处理进程数据（按服务分组）"""
        if df.empty:
            return {}, {}
        
        features_by_service = {}
        feature_dfs_by_service = {}
        
        # 按进程名分组
        for process_name in df['name'].unique():
            process_df = df[df['name'] == process_name].copy()
            
            if len(process_df) < 3:  # 数据点太少，跳过
                continue
            
            # 选择特征列
            feature_cols = [col for col in self.process_features if col in process_df.columns]
            feature_df = process_df[feature_cols].copy()
            
            # 处理缺失值
            feature_df = feature_df.fillna(feature_df.mean())
            
            # 添加派生特征
            if len(feature_df) > 1:
                feature_df['cpu_change'] = feature_df['cpu_percent'].diff().fillna(0)
                feature_df['memory_change'] = feature_df['memory_percent'].diff().fillna(0)
            
            # 标准化
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(feature_df)
            
            features_by_service[process_name] = features_scaled
            feature_dfs_by_service[process_name] = feature_df
        
        return features_by_service, feature_dfs_by_service
    
    def detect_system_anomalies(self, system_df: pd.DataFrame) -> Dict[str, Any]:
        """检测系统级异常"""
        if system_df.empty:
            return {'anomalies': [], 'summary': {'total': 0, 'by_model': {}}}
        
        features, feature_df = self.preprocess_system_data(system_df)
        
        if features.size == 0:
            return {'anomalies': [], 'summary': {'total': 0, 'by_model': {}}}
        
        anomaly_results = {
            'anomalies': [],
            'summary': {'total': 0, 'by_model': {}}
        }
        
        # 使用多个模型检测异常
        all_anomaly_scores = {}
        
        for model_name, model in self.models.items():
            try:
                # 检查样本数量是否足够
                if features.shape[0] < 2:
                    self.logger.warning(f"样本数量不足，跳过 {model_name} 模型")
                    continue
                
                # 对于需要邻居的模型，检查样本数量
                if model_name in ['lof', 'knn'] and features.shape[0] < 5:
                    self.logger.warning(f"样本数量不足，跳过 {model_name} 模型")
                    continue
                
                # 训练模型并预测
                anomaly_labels = model.fit_predict(features)
                anomaly_scores = model.decision_function(features)
                
                # 找出异常点
                anomaly_indices = np.where(anomaly_labels == 1)[0]
                
                all_anomaly_scores[model_name] = {
                    'labels': anomaly_labels,
                    'scores': anomaly_scores,
                    'anomaly_count': len(anomaly_indices)
                }
                
                anomaly_results['summary']['by_model'][model_name] = len(anomaly_indices)
                
                self.logger.info(f"{model_name} 检测到 {len(anomaly_indices)} 个系统异常")
                
            except Exception as e:
                self.logger.error(f"模型 {model_name} 检测失败: {e}")
                continue
        
        # 集成多个模型的结果（投票机制）
        if all_anomaly_scores:
            ensemble_anomalies = self._ensemble_anomaly_detection(all_anomaly_scores, features.shape[0])
            
            # 构建异常记录
            for idx in ensemble_anomalies:
                original_idx = system_df.index[idx]
                # 将Timestamp转换为ISO格式字符串
                timestamp = system_df.loc[original_idx, 'timestamp']
                if hasattr(timestamp, 'isoformat'):
                    timestamp_str = timestamp.isoformat()
                else:
                    timestamp_str = str(timestamp)
                
                anomaly_record = {
                    'timestamp': timestamp_str,
                    'type': 'system',
                    'anomaly_index': int(idx),
                    'metrics': {
                        'cpu_percent': float(system_df.loc[original_idx, 'cpu_percent']),
                        'memory_percent': float(system_df.loc[original_idx, 'memory_percent']),
                        'disk_usage_percent': float(system_df.loc[original_idx, 'disk_usage_percent']),
                        'network_connections': int(system_df.loc[original_idx, 'network_connections'])
                    },
                    'scores': {name: float(scores['scores'][idx]) for name, scores in all_anomaly_scores.items()},
                    'severity': self._calculate_severity(all_anomaly_scores, idx)
                }
                anomaly_results['anomalies'].append(anomaly_record)
            
            anomaly_results['summary']['total'] = len(ensemble_anomalies)
        
        return anomaly_results
    
    def detect_process_anomalies(self, process_df: pd.DataFrame) -> Dict[str, Any]:
        """检测进程级异常"""
        if process_df.empty:
            return {'anomalies': [], 'summary': {'total': 0, 'by_service': {}}}
        
        features_by_service, feature_dfs_by_service = self.preprocess_process_data(process_df)
        
        anomaly_results = {
            'anomalies': [],
            'summary': {'total': 0, 'by_service': {}}
        }
        
        for service_name, features in features_by_service.items():
            service_df = process_df[process_df['name'] == service_name].copy()
            
            try:
                # 检查样本数量是否足够
                if features.shape[0] < 2:
                    self.logger.warning(f"服务 {service_name} 样本数量不足，跳过异常检测")
                    continue
                
                # 使用Isolation Forest检测进程异常
                model = IForest(contamination=self.contamination, random_state=42)
                anomaly_labels = model.fit_predict(features)
                anomaly_scores = model.decision_function(features)
                
                anomaly_indices = np.where(anomaly_labels == 1)[0]
                
                anomaly_results['summary']['by_service'][service_name] = len(anomaly_indices)
                
                # 构建异常记录
                for idx in anomaly_indices:
                    original_idx = service_df.index[idx]
                    # 将Timestamp转换为ISO格式字符串
                    timestamp = service_df.loc[original_idx, 'timestamp']
                    if hasattr(timestamp, 'isoformat'):
                        timestamp_str = timestamp.isoformat()
                    else:
                        timestamp_str = str(timestamp)
                    
                    anomaly_record = {
                        'timestamp': timestamp_str,
                        'type': 'process',
                        'service': service_name,
                        'pid': int(service_df.loc[original_idx, 'pid']),
                        'anomaly_index': int(idx),
                        'metrics': {
                            'cpu_percent': float(service_df.loc[original_idx, 'cpu_percent']),
                            'memory_percent': float(service_df.loc[original_idx, 'memory_percent']),
                            'memory_rss': int(service_df.loc[original_idx, 'memory_rss']),
                            'connections': int(service_df.loc[original_idx, 'connections'])
                        },
                        'anomaly_score': float(anomaly_scores[idx]),
                        'severity': 'high' if anomaly_scores[idx] < -0.5 else 'medium'
                    }
                    anomaly_results['anomalies'].append(anomaly_record)
                
                self.logger.info(f"{service_name} 检测到 {len(anomaly_indices)} 个进程异常")
                
            except Exception as e:
                self.logger.error(f"检测 {service_name} 进程异常失败: {e}")
                continue
        
        anomaly_results['summary']['total'] = len(anomaly_results['anomalies'])
        return anomaly_results
    
    def integrate_log_anomalies(self) -> Dict[str, Any]:
        """整合日志异常信息"""
        log_anomalies = {
            'anomalies': [],
            'summary': {'total': 0, 'by_service': {}}
        }
        
        try:
            if not self.parsed_logs_file.exists():
                return log_anomalies
            
            with open(self.parsed_logs_file, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
            
            # 分析每个服务的日志异常
            for service, service_data in log_data.get('services', {}).items():
                error_count = 0
                critical_count = 0
                
                for file_data in service_data.get('files', []):
                    level_counts = file_data.get('summary', {}).get('by_level', {})
                    error_count += level_counts.get('error', 0)
                    critical_count += level_counts.get('critical', 0)
                
                total_anomalies = error_count + critical_count
                
                if total_anomalies > 0:
                    log_anomaly = {
                        'timestamp': log_data.get('parse_time'),
                        'type': 'log',
                        'service': service,
                        'metrics': {
                            'error_count': error_count,
                            'critical_count': critical_count,
                            'total_anomalies': total_anomalies
                        },
                        'severity': 'critical' if critical_count > 0 else 'high' if error_count > 10 else 'medium'
                    }
                    log_anomalies['anomalies'].append(log_anomaly)
                
                log_anomalies['summary']['by_service'][service] = total_anomalies
            
            log_anomalies['summary']['total'] = len(log_anomalies['anomalies'])
            
        except Exception as e:
            self.logger.error(f"整合日志异常失败: {e}")
        
        return log_anomalies
    
    def _ensemble_anomaly_detection(self, model_results: Dict, total_samples: int) -> List[int]:
        """集成多个模型的异常检测结果"""
        # 投票机制：至少两个模型认为是异常的点
        anomaly_votes = np.zeros(total_samples)
        
        for model_name, results in model_results.items():
            anomaly_indices = np.where(results['labels'] == 1)[0]
            anomaly_votes[anomaly_indices] += 1
        
        # 至少2个模型投票为异常
        ensemble_anomalies = np.where(anomaly_votes >= 2)[0]
        
        return ensemble_anomalies.tolist()
    
    def _calculate_severity(self, model_results: Dict, anomaly_idx: int) -> str:
        """计算异常严重程度"""
        scores = [results['scores'][anomaly_idx] for results in model_results.values()]
        avg_score = np.mean(scores)
        
        if avg_score < -0.6:
            return 'critical'
        elif avg_score < -0.3:
            return 'high'
        elif avg_score < 0:
            return 'medium'
        else:
            return 'low'
    
    def run_anomaly_detection(self, hours_back: int = 24) -> Dict[str, Any]:
        """运行完整的异常检测流程"""
        self.logger.info("开始异常检测...")
        
        # 加载数据
        system_df, process_df = self.load_metrics_data(hours_back)
        
        # 检测系统异常
        system_anomalies = self.detect_system_anomalies(system_df)
        
        # 检测进程异常
        process_anomalies = self.detect_process_anomalies(process_df)
        
        # 整合日志异常
        log_anomalies = self.integrate_log_anomalies()
        
        # 合并所有异常
        all_anomalies = {
            'detection_time': datetime.now().isoformat(),
            'time_window_hours': hours_back,
            'system_anomalies': system_anomalies,
            'process_anomalies': process_anomalies,
            'log_anomalies': log_anomalies,
            'summary': {
                'total_anomalies': (
                    system_anomalies['summary']['total'] + 
                    process_anomalies['summary']['total'] + 
                    log_anomalies['summary']['total']
                ),
                'by_type': {
                    'system': system_anomalies['summary']['total'],
                    'process': process_anomalies['summary']['total'],
                    'log': log_anomalies['summary']['total']
                }
            }
        }
        
        return all_anomalies
    
    def save_anomaly_results(self, anomaly_results: Dict[str, Any]):
        """保存异常检测结果"""
        try:
            print("=======================")
            print(anomaly_results)
            # 保存详细结果
            with open(self.anomaly_summary_file, 'w', encoding='utf-8') as f:
                json.dump(anomaly_results, f, ensure_ascii=False, indent=2)
            
            # 保存异常列表到CSV
            all_anomalies = []
            
            # 系统异常
            for anomaly in anomaly_results['system_anomalies']['anomalies']:
                all_anomalies.append({
                    'timestamp': anomaly['timestamp'],
                    'type': 'system',
                    'service': 'system',
                    'severity': anomaly['severity'],
                    'cpu_percent': anomaly['metrics']['cpu_percent'],
                    'memory_percent': anomaly['metrics']['memory_percent'],
                    'description': 'System resource anomaly detected'
                })
            
            # 进程异常
            for anomaly in anomaly_results['process_anomalies']['anomalies']:
                all_anomalies.append({
                    'timestamp': anomaly['timestamp'],
                    'type': 'process',
                    'service': anomaly['service'],
                    'severity': anomaly['severity'],
                    'cpu_percent': anomaly['metrics']['cpu_percent'],
                    'memory_percent': anomaly['metrics']['memory_percent'],
                    'description': f'Process anomaly detected for {anomaly["service"]}'
                })
            
            # 日志异常
            for anomaly in anomaly_results['log_anomalies']['anomalies']:
                all_anomalies.append({
                    'timestamp': anomaly['timestamp'],
                    'type': 'log',
                    'service': anomaly['service'],
                    'severity': anomaly['severity'],
                    'cpu_percent': 0,
                    'memory_percent': 0,
                    'description': f'Log anomaly: {anomaly["metrics"]["error_count"]} errors, {anomaly["metrics"]["critical_count"]} critical'
                })
            
            # 保存到CSV
            if all_anomalies:
                anomalies_df = pd.DataFrame(all_anomalies)
                anomalies_df.to_csv(self.anomalies_file, index=False)
            
            self.logger.info(f"异常检测结果已保存到: {self.output_dir}")
            
        except Exception as e:
            self.logger.error(f"保存异常检测结果失败: {e}")


def main():
    """主函数演示"""
    detector = AnomalyDetector(output_dir="data", contamination=0.1)
    
    print("🔍 开始异常检测...")
    
    try:
        # 运行异常检测
        results = detector.run_anomaly_detection(hours_back=24)
        
        # 保存结果
        detector.save_anomaly_results(results)
        
        # 显示摘要
        summary = results['summary']
        print(f"\n📊 异常检测摘要:")
        print(f"  - 总异常数: {summary['total_anomalies']}")
        print(f"  - 系统异常: {summary['by_type']['system']}")
        print(f"  - 进程异常: {summary['by_type']['process']}")
        print(f"  - 日志异常: {summary['by_type']['log']}")
        
        # 显示系统异常详情
        if results['system_anomalies']['anomalies']:
            print(f"\n⚠️ 系统异常:")
            for anomaly in results['system_anomalies']['anomalies'][:3]:
                print(f"  - {anomaly['timestamp'][:19]} ({anomaly['severity']}): "
                      f"CPU {anomaly['metrics']['cpu_percent']:.1f}%, "
                      f"MEM {anomaly['metrics']['memory_percent']:.1f}%")
        
        # 显示进程异常详情
        if results['process_anomalies']['anomalies']:
            print(f"\n🔧 进程异常:")
            for anomaly in results['process_anomalies']['anomalies'][:3]:
                print(f"  - {anomaly['service']} ({anomaly['timestamp'][:19]}): "
                      f"CPU {anomaly['metrics']['cpu_percent']:.1f}%, "
                      f"MEM {anomaly['metrics']['memory_percent']:.1f}%")
        
        print(f"\n💾 结果已保存到: {detector.output_dir}")
        
    except Exception as e:
        print(f"❌ 异常检测失败: {e}")


if __name__ == "__main__":
    main() 