"""
异常检测模块
实现多种异常检测算法，识别微服务中的异常行为
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from scipy import stats
import logging
from typing import Dict, List, Tuple, Any
from datetime import datetime, timedelta


class AnomalyDetector:
    """异常检测器"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # 阈值配置
        self.response_time_threshold = config.get('response_time_threshold', 1000)
        self.error_rate_threshold = config.get('error_rate_threshold', 5.0)
        self.throughput_drop_threshold = config.get('throughput_drop_threshold', 30.0)
        
        # 检测算法
        self.algorithms = config.get('algorithms', ['statistical', 'isolation_forest'])
        
    def extract_metrics_from_skywalking_data(self, data: Dict) -> pd.DataFrame:
        """从SkyWalking数据中提取指标"""
        metrics_list = []
        
        for service_data in data.get("services", []):
            service_name = service_data["service"].get("name", "unknown")
            metrics = service_data.get("metrics", {})
            traces = service_data.get("traces", [])
            
            # 提取基础指标
            service_metrics = {
                "service_name": service_name,
                "timestamp": data.get("timestamp"),
            }
            
            # 处理CPM（每分钟调用次数）
            cpm_data = metrics.get("service_cpm", {})
            if cpm_data and "values" in cpm_data:
                cpm_values = []
                values_data = cpm_data["values"]
                if isinstance(values_data, dict) and "values" in values_data:
                    # 新格式：values是一个包含values数组的字典
                    for v in values_data["values"]:
                        if isinstance(v, dict) and v.get("value") is not None:
                            cpm_values.append(float(v["value"]))
                elif isinstance(values_data, list):
                    # 旧格式：values是一个数组
                    for value_group in values_data:
                        if isinstance(value_group, dict) and "values" in value_group:
                            for v in value_group["values"]:
                                if isinstance(v, dict) and v.get("value") is not None:
                                    cpm_values.append(float(v["value"]))
                
                service_metrics.update({
                    "avg_cpm": np.mean(cpm_values) if cpm_values else 0,
                    "max_cpm": np.max(cpm_values) if cpm_values else 0,
                    "min_cpm": np.min(cpm_values) if cpm_values else 0,
                    "std_cpm": np.std(cpm_values) if cpm_values else 0
                })
            else:
                service_metrics.update({
                    "avg_cpm": 0, "max_cpm": 0, "min_cpm": 0, "std_cpm": 0
                })
            
            # 处理SLA（服务水平协议）
            sla_data = metrics.get("service_sla", {})
            if sla_data and "values" in sla_data:
                sla_values = []
                values_data = sla_data["values"]
                if isinstance(values_data, dict) and "values" in values_data:
                    # 新格式
                    for v in values_data["values"]:
                        if isinstance(v, dict) and v.get("value") is not None:
                            sla_values.append(float(v["value"]))
                elif isinstance(values_data, list):
                    # 旧格式
                    for value_group in values_data:
                        if isinstance(value_group, dict) and "values" in value_group:
                            for v in value_group["values"]:
                                if isinstance(v, dict) and v.get("value") is not None:
                                    sla_values.append(float(v["value"]))
                
                service_metrics["avg_sla"] = np.mean(sla_values) if sla_values else 100
                service_metrics["min_sla"] = np.min(sla_values) if sla_values else 100
            else:
                service_metrics.update({"avg_sla": 100, "min_sla": 100})
            
            # 处理响应时间
            resp_time_data = metrics.get("service_resp_time", {})
            if resp_time_data and "values" in resp_time_data:
                resp_time_values = []
                values_data = resp_time_data["values"]
                if isinstance(values_data, dict) and "values" in values_data:
                    # 新格式
                    for v in values_data["values"]:
                        if isinstance(v, dict) and v.get("value") is not None:
                            resp_time_values.append(float(v["value"]))
                elif isinstance(values_data, list):
                    # 旧格式
                    for value_group in values_data:
                        if isinstance(value_group, dict) and "values" in value_group:
                            for v in value_group["values"]:
                                if isinstance(v, dict) and v.get("value") is not None:
                                    resp_time_values.append(float(v["value"]))
                
                service_metrics.update({
                    "avg_response_time": np.mean(resp_time_values) if resp_time_values else 0,
                    "max_response_time": np.max(resp_time_values) if resp_time_values else 0,
                    "p95_response_time": np.percentile(resp_time_values, 95) if resp_time_values else 0,
                    "std_response_time": np.std(resp_time_values) if resp_time_values else 0
                })
            else:
                service_metrics.update({
                    "avg_response_time": 0,
                    "max_response_time": 0, 
                    "p95_response_time": 0,
                    "std_response_time": 0
                })
            
            # 处理trace数据
            if traces:
                trace_durations = [trace.get("duration", 0) for trace in traces]
                error_traces = [trace for trace in traces if trace.get("isError", False)]
                
                service_metrics.update({
                    "trace_count": len(traces),
                    "error_count": len(error_traces),
                    "error_rate": (len(error_traces) / len(traces)) * 100 if traces else 0,
                    "avg_trace_duration": np.mean(trace_durations) if trace_durations else 0,
                    "max_trace_duration": np.max(trace_durations) if trace_durations else 0
                })
            else:
                service_metrics.update({
                    "trace_count": 0,
                    "error_count": 0,
                    "error_rate": 0,
                    "avg_trace_duration": 0,
                    "max_trace_duration": 0
                })
            
            metrics_list.append(service_metrics)
        
        return pd.DataFrame(metrics_list)
    
    def statistical_anomaly_detection(self, df: pd.DataFrame) -> Dict[str, List[Dict]]:
        """基于统计的异常检测"""
        anomalies = {"high_priority": [], "medium_priority": [], "low_priority": []}
        
        for _, row in df.iterrows():
            service_name = row["service_name"]
            
            # 高优先级异常：错误率过高
            if row["error_rate"] > self.error_rate_threshold:
                anomalies["high_priority"].append({
                    "service": service_name,
                    "type": "high_error_rate",
                    "value": row["error_rate"],
                    "threshold": self.error_rate_threshold,
                    "severity": "HIGH",
                    "description": f"服务 {service_name} 错误率过高: {row['error_rate']:.2f}%"
                })
            
            # 高优先级异常：响应时间过长
            if row["avg_response_time"] > self.response_time_threshold:
                anomalies["high_priority"].append({
                    "service": service_name,
                    "type": "high_response_time",
                    "value": row["avg_response_time"],
                    "threshold": self.response_time_threshold,
                    "severity": "HIGH",
                    "description": f"服务 {service_name} 平均响应时间过长: {row['avg_response_time']:.2f}ms"
                })
            
            # 中优先级异常：SLA下降
            if row["avg_sla"] < 95.0:
                anomalies["medium_priority"].append({
                    "service": service_name,
                    "type": "low_sla",
                    "value": row["avg_sla"],
                    "threshold": 95.0,
                    "severity": "MEDIUM",
                    "description": f"服务 {service_name} SLA下降: {row['avg_sla']:.2f}%"
                })
            
            # 中优先级异常：吞吐量异常
            if row["std_cpm"] > 0 and row["avg_cpm"] > 0:
                cv = row["std_cpm"] / row["avg_cpm"]  # 变异系数
                if cv > 0.5:  # 变异系数过大表示不稳定
                    anomalies["medium_priority"].append({
                        "service": service_name,
                        "type": "unstable_throughput",
                        "value": cv,
                        "threshold": 0.5,
                        "severity": "MEDIUM",
                        "description": f"服务 {service_name} 吞吐量不稳定，变异系数: {cv:.2f}"
                    })
        
        return anomalies
    
    def z_score_anomaly_detection(self, df: pd.DataFrame, threshold: float = 2.0) -> Dict[str, List[Dict]]:
        """基于Z-Score的异常检测"""
        anomalies = {"high_priority": [], "medium_priority": [], "low_priority": []}
        
        # 需要检测的数值列
        numeric_columns = [
            "avg_response_time", "max_response_time", "error_rate", 
            "avg_cpm", "avg_trace_duration"
        ]
        
        for col in numeric_columns:
            if col in df.columns and len(df[col].dropna()) > 1:
                z_scores = stats.zscore(df[col].dropna())
                outlier_indices = np.where(np.abs(z_scores) > threshold)[0]
                
                for idx in outlier_indices:
                    actual_idx = df[col].dropna().index[idx]
                    row = df.loc[actual_idx]
                    
                    severity = "HIGH" if abs(z_scores[idx]) > 3.0 else "MEDIUM"
                    priority = "high_priority" if severity == "HIGH" else "medium_priority"
                    
                    anomalies[priority].append({
                        "service": row["service_name"],
                        "type": f"z_score_outlier_{col}",
                        "value": row[col],
                        "z_score": z_scores[idx],
                        "threshold": threshold,
                        "severity": severity,
                        "description": f"服务 {row['service_name']} 在指标 {col} 上出现异常，Z-Score: {z_scores[idx]:.2f}"
                    })
        
        return anomalies
    
    def isolation_forest_anomaly_detection(self, df: pd.DataFrame, contamination: float = 0.1) -> Dict[str, List[Dict]]:
        """基于孤立森林的异常检测"""
        anomalies = {"high_priority": [], "medium_priority": [], "low_priority": []}
        
        # 选择特征列
        feature_columns = [
            "avg_response_time", "max_response_time", "error_rate",
            "avg_cpm", "avg_sla", "trace_count", "avg_trace_duration"
        ]
        
        # 过滤存在的列
        available_columns = [col for col in feature_columns if col in df.columns]
        
        if len(available_columns) < 2 or len(df) < 2:
            self.logger.warning("数据不足，无法进行孤立森林异常检测")
            return anomalies
        
        # 准备数据
        feature_data = df[available_columns].fillna(0)
        
        # 标准化
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(feature_data)
        
        # 孤立森林
        iso_forest = IsolationForest(contamination=contamination, random_state=42)
        outlier_labels = iso_forest.fit_predict(scaled_data)
        anomaly_scores = iso_forest.score_samples(scaled_data)
        
        # 识别异常
        for i, (label, score) in enumerate(zip(outlier_labels, anomaly_scores)):
            if label == -1:  # 异常点
                row = df.iloc[i]
                
                # 根据异常得分确定严重程度
                severity = "HIGH" if score < -0.5 else "MEDIUM"
                priority = "high_priority" if severity == "HIGH" else "medium_priority"
                
                anomalies[priority].append({
                    "service": row["service_name"],
                    "type": "isolation_forest_outlier",
                    "anomaly_score": score,
                    "severity": severity,
                    "description": f"服务 {row['service_name']} 被孤立森林算法识别为异常，异常得分: {score:.3f}"
                })
        
        return anomalies
    
    def detect_anomalies(self, skywalking_data: Dict) -> Dict:
        """执行异常检测"""
        self.logger.info("开始异常检测")
        
        # 提取指标
        df = self.extract_metrics_from_skywalking_data(skywalking_data)
        
        if df.empty:
            self.logger.warning("没有可用的指标数据")
            return {"anomalies": {"high_priority": [], "medium_priority": [], "low_priority": []}}
        
        self.logger.info(f"提取了 {len(df)} 个服务的指标数据")
        
        # 合并所有异常检测结果
        all_anomalies = {"high_priority": [], "medium_priority": [], "low_priority": []}
        
        # 统计异常检测
        if "statistical" in self.algorithms:
            stat_anomalies = self.statistical_anomaly_detection(df)
            for priority in all_anomalies:
                all_anomalies[priority].extend(stat_anomalies[priority])
        
        # Z-Score异常检测
        if "z_score" in self.algorithms:
            zscore_anomalies = self.z_score_anomaly_detection(df)
            for priority in all_anomalies:
                all_anomalies[priority].extend(zscore_anomalies[priority])
        
        # 孤立森林异常检测
        if "isolation_forest" in self.algorithms:
            iso_anomalies = self.isolation_forest_anomaly_detection(df)
            for priority in all_anomalies:
                all_anomalies[priority].extend(iso_anomalies[priority])
        
        # 统计结果
        total_anomalies = sum(len(anomalies) for anomalies in all_anomalies.values())
        self.logger.info(f"检测到 {total_anomalies} 个异常")
        
        return {
            "detection_timestamp": datetime.now().isoformat(),
            "metrics_summary": {
                "total_services": len(df),
                "services_with_anomalies": len(set(
                    anomaly["service"] for anomalies in all_anomalies.values() 
                    for anomaly in anomalies
                ))
            },
            "anomalies": all_anomalies,
            "raw_metrics": df.to_dict("records")
        }
