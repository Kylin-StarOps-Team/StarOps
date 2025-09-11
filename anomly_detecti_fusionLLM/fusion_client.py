#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fusion_LogLLM 融合客户端
支持日志、SkyWalking和Prometheus指标的异常检测
模型已在服务器启动时自动加载，客户端可直接进行检测
支持新的Prometheus数据格式
"""

import requests
import json
import time
import os
from typing import List, Dict, Optional, Any, Union
from datetime import datetime

class FusionLogLLMClient:
    def __init__(self, server_url="http://localhost:8080"):
        self.server_url = server_url.rstrip('/')
        self.session = requests.Session()
        self.session.timeout = 300  # 5分钟超时
    
    def health_check(self) -> Dict:
        """健康检查"""
        try:
            response = self.session.get(f"{self.server_url}/health")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": f"连接失败: {str(e)}"}
    
    def detect_anomalies_fusion(self, 
                               logs: List[str], 
                               prometheus_data: Union[str, Dict] = None,
                               skywalking_data: List[Dict] = None,
                               window_size: int = 20, 
                               step_size: int = 10, 
                               batch_size: int = 32) -> Dict:
        """融合异常检测
        支持新的Prometheus数据格式：
        - 字符串格式（旧格式）
        - 字典格式（新格式）：{'blackbox_metrics': ..., 'mysql_metrics': ..., 'node_metrics': ...}
        """
        try:
            data = {
                "logs": logs,
                "prometheus_data": prometheus_data,
                "skywalking_data": skywalking_data
            }
            
            params = {
                "window_size": window_size,
                "step_size": step_size,
                "batch_size": batch_size
            }
            
            response = self.session.post(f"{self.server_url}/detect", json=data, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": f"检测失败: {str(e)}"}
    
    def detect_anomalies_file(self, file_path: str, 
                             prometheus_data: Union[str, Dict] = None,
                             skywalking_data: List[Dict] = None,
                             window_size: int = 20, 
                             step_size: int = 10, 
                             batch_size: int = 32) -> Dict:
        """通过文件上传进行异常检测"""
        try:
            if not os.path.exists(file_path):
                return {"error": f"文件不存在: {file_path}"}
            
            with open(file_path, 'rb') as f:
                files = {'file': f}
                params = {
                    "window_size": window_size,
                    "step_size": step_size,
                    "batch_size": batch_size
                }
                
                response = self.session.post(f"{self.server_url}/detect", files=files, params=params)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            return {"error": f"文件检测失败: {str(e)}"}
    
    def get_model_info(self) -> Dict:
        """获取模型信息"""
        try:
            response = self.session.get(f"{self.server_url}/model_info")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": f"获取模型信息失败: {str(e)}"}
    
    def get_gpu_info(self) -> Dict:
        """获取GPU信息"""
        try:
            response = self.session.get(f"{self.server_url}/gpu_info")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": f"获取GPU信息失败: {str(e)}"}
    
    def get_metrics_info(self) -> Dict:
        """获取指标处理信息"""
        try:
            response = self.session.get(f"{self.server_url}/metrics_info")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": f"获取指标信息失败: {str(e)}"}
    
    def get_config(self) -> Dict:
        """获取服务器配置信息"""
        try:
            response = self.session.get(f"{self.server_url}/config")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": f"获取配置信息失败: {str(e)}"}
    
    def test_metrics_parsing(self, prometheus_data: Union[str, Dict] = None, skywalking_data: List[Dict] = None) -> Dict:
        """测试指标数据解析"""
        try:
            data = {
                "prometheus_data": prometheus_data,
                "skywalking_data": skywalking_data
            }
            
            response = self.session.post(f"{self.server_url}/test_metrics_parsing", json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": f"指标解析测试失败: {str(e)}"}
    
    def load_prometheus_data(self, file_path: str) -> str:
        """加载Prometheus指标数据（旧格式，向后兼容）"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"加载Prometheus数据失败: {str(e)}")
            return None
    
    def load_prometheus_data_new_format(self, 
                                       blackbox_file: str = None,
                                       mysql_file: str = None,
                                       node_file: str = None) -> Dict[str, str]:
        """加载新的Prometheus数据格式
        
        Args:
            blackbox_file: blackbox_metrics.log文件路径
            mysql_file: mysql_metrics.log文件路径
            node_file: node_metrics.log文件路径
            
        Returns:
            包含各类型指标数据的字典
        """
        prometheus_data = {}
        
        # 加载blackbox_metrics
        if blackbox_file and os.path.exists(blackbox_file):
            try:
                with open(blackbox_file, 'r', encoding='utf-8') as f:
                    prometheus_data['blackbox_metrics'] = f.read()
                print(f"✅ 成功加载 blackbox_metrics: {blackbox_file}")
            except Exception as e:
                print(f"❌ 加载 blackbox_metrics 失败: {str(e)}")
        
        # 加载mysql_metrics
        if mysql_file and os.path.exists(mysql_file):
            try:
                with open(mysql_file, 'r', encoding='utf-8') as f:
                    prometheus_data['mysql_metrics'] = f.read()
                print(f"✅ 成功加载 mysql_metrics: {mysql_file}")
            except Exception as e:
                print(f"❌ 加载 mysql_metrics 失败: {str(e)}")
        
        # 加载node_metrics
        if node_file and os.path.exists(node_file):
            try:
                with open(node_file, 'r', encoding='utf-8') as f:
                    prometheus_data['node_metrics'] = f.read()
                print(f"✅ 成功加载 node_metrics: {node_file}")
            except Exception as e:
                print(f"❌ 加载 node_metrics 失败: {str(e)}")
        
        return prometheus_data
    
    def load_prometheus_data_from_directory(self, directory: str = ".") -> Dict[str, str]:
        """从指定目录加载Prometheus指标数据（新格式）
        
        Args:
            directory: 包含指标文件的目录路径
            
        Returns:
            包含各类型指标数据的字典
        """
        prometheus_data = {}
        
        # 默认文件名
        default_files = {
            'blackbox_metrics': '/var/log/blackbox_exporter_metrics.log',
            'mysql_metrics': '/var/log/mysqld_exporter_metrics.log',
            'node_metrics': '/var/log/node_exporter_metrics.log'
        }
        
        for metric_type, filename in default_files.items():
            file_path = os.path.join(directory, filename)
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        prometheus_data[metric_type] = f.read()
                    print(f"✅ 成功加载 {metric_type}: {file_path}")
                except Exception as e:
                    print(f"❌ 加载 {metric_type} 失败: {str(e)}")
            else:
                print(f"⚠️  文件不存在: {file_path}")
        
        return prometheus_data
    
    def create_prometheus_data_from_strings(self,
                                          blackbox_content: str = None,
                                          mysql_content: str = None,
                                          node_content: str = None) -> Dict[str, str]:
        """从字符串创建新的Prometheus数据格式
        
        Args:
            blackbox_content: blackbox指标内容
            mysql_content: mysql指标内容
            node_content: node指标内容
            
        Returns:
            包含各类型指标数据的字典
        """
        prometheus_data = {}
        
        if blackbox_content:
            prometheus_data['blackbox_metrics'] = blackbox_content
        if mysql_content:
            prometheus_data['mysql_metrics'] = mysql_content
        if node_content:
            prometheus_data['node_metrics'] = node_content
        
        return prometheus_data
    
    def load_skywalking_data(self, file_path: str) -> List[Dict]:
        """加载SkyWalking指标数据"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # 处理Python列表格式的数据
                if content.startswith('skywalking_active_nodes_metrics = ['):
                    # 提取JSON部分
                    json_start = content.find('[')
                    json_end = content.rfind(']') + 1
                    json_content = content[json_start:json_end]
                    return json.loads(json_content)
                else:
                    # 直接解析JSON
                    return json.loads(content)
        except Exception as e:
            print(f"加载SkyWalking数据失败: {str(e)}")
            return None
    
    def validate_prometheus_data(self, prometheus_data: Union[str, Dict]) -> Dict:
        """验证Prometheus数据格式
        
        Args:
            prometheus_data: Prometheus数据
            
        Returns:
            验证结果字典
        """
        result = {
            "valid": True,
            "format": "unknown",
            "details": {},
            "errors": []
        }
        
        try:
            if isinstance(prometheus_data, dict):
                result["format"] = "new_format"
                result["details"]["categories"] = list(prometheus_data.keys())
                result["details"]["category_count"] = len(prometheus_data)
                
                # 检查每个类别的数据
                for category, content in prometheus_data.items():
                    if content and isinstance(content, str):
                        result["details"][f"{category}_length"] = len(content)
                        result["details"][f"{category}_lines"] = content.count('\n') + 1
                    else:
                        result["errors"].append(f"{category} 数据为空或格式错误")
                        result["valid"] = False
                        
            elif isinstance(prometheus_data, str):
                result["format"] = "old_format"
                result["details"]["length"] = len(prometheus_data)
                result["details"]["lines"] = prometheus_data.count('\n') + 1
                
                # 检查是否包含各种指标类型
                if "mysql_global_status" in prometheus_data:
                    result["details"]["has_mysql"] = True
                if "node_" in prometheus_data:
                    result["details"]["has_node"] = True
                if "probe_" in prometheus_data:
                    result["details"]["has_blackbox"] = True
                    
            else:
                result["valid"] = False
                result["errors"].append("不支持的数据格式")
                
        except Exception as e:
            result["valid"] = False
            result["errors"].append(f"验证过程中发生错误: {str(e)}")
        
        return result
    
    def extract_anomaly_information(self, detection_result: Dict) -> Dict:
        """从检测结果中提取异常信息并整理到anomly_information变量中
        
        Args:
            detection_result: 异常检测的返回结果
            
        Returns:
            Dict: 包含异常信息的字典
        """
        anomly_information = {
            "global_info": {},
            "anomaly_windows": []
        }
        
        # 提取全局信息
        if "status" in detection_result:
            anomly_information["global_info"]["status"] = detection_result["status"]
        if "timestamp" in detection_result:
            anomly_information["global_info"]["timestamp"] = detection_result["timestamp"]
        if "total_sequences" in detection_result:
            anomly_information["global_info"]["total_sequences"] = detection_result["total_sequences"]
        if "anomaly_count" in detection_result:
            anomly_information["global_info"]["anomaly_count"] = detection_result["anomaly_count"]
        if "log_anomaly_count" in detection_result:
            anomly_information["global_info"]["log_anomaly_count"] = detection_result["log_anomaly_count"]
        if "metrics_anomaly_count" in detection_result:
            anomly_information["global_info"]["metrics_anomaly_count"] = detection_result["metrics_anomaly_count"]
        if "processing_time" in detection_result:
            anomly_information["global_info"]["processing_time"] = detection_result["processing_time"]
        print("windows======================================================================================")
        # 提取异常窗口信息
        if "results" in detection_result and isinstance(detection_result["results"], list):
            for window in detection_result["results"]:
                # print(window.get("log_is_anomaly"))
                if window.get("log_is_anomaly", False):  # 只提取异常窗口
                    anomaly_window = {
                        "sequence_id": window.get("sequence_id"),
                        "timestamp": window.get("timestamp"),
                        "anomaly_score": window.get("anomaly_score"),
                        "confidence": window.get("confidence"),
                        "fusion_weight": window.get("fusion_weight"),
                        "is_anomaly": window.get("is_anomaly"),
                        "log_anomaly_score": window.get("log_anomaly_score"),
                        "log_is_anomaly": window.get("log_is_anomaly"),
                        "log_raw_output": window.get("log_raw_output"),
                        "metrics_anomaly_score": window.get("metrics_anomaly_score"),
                        "mad_threshold": window.get("mad_threshold"),
                        "logs": window.get("logs", []),
                        "metrics_data": window.get("metrics_data", {})
                    }
                    anomly_information["anomaly_windows"].append(anomaly_window)
                    # 这里现在如果没有异常日志就会返回空，但是is_anomly及其有可能是true，代表指标其实有问题，那么对于所有窗口都正常的情况，我最终也会返回某一个窗口的指标数据"anomaly_score": 14.718360785692502,
    #   "confidence": 0.8,
    #   "fusion_weight": 0.3,
    #   "is_anomaly": true,
        return anomly_information

def convert_loki_to_bgl(log_file_path):
    """
    将Loki监控日志转换为BGL格式的日志
    
    参数:
        log_file_path (str): Loki日志文件路径
        
    返回:
        list: 转换后的BGL格式日志列表
    """
    bgl_logs = []
    
    # 定义默认值
    default_label = "-"
    default_id = ""
    default_date = datetime.now().strftime("%Y.%m.%d")
    default_code1 = "UNKNOWN"
    default_component1 = "RAS"
    default_component2 = "SYSTEM"
    default_level = "INFO"
    
    with open(log_file_path, 'r') as f:
        for line in f:
            try:
                # 解析JSON格式的日志行
                log_entry = json.loads(line.strip())
                log_content = log_entry.get("log", "")
                timestamp = log_entry.get("timestamp", "")
                
                # 解析时间戳
                try:
                    log_time = datetime.fromisoformat(timestamp.rstrip("Z")).strftime("%Y-%m-%d-%H.%M.%S.%f")[:-3]
                    log_date = datetime.fromisoformat(timestamp.rstrip("Z")).strftime("%Y.%m.%d")
                except:
                    log_time = datetime.now().strftime("%Y-%m-%d-%H.%M.%S.%f")[:-3]
                    log_date = datetime.now().strftime("%Y.%m.%d")
                
                # 确定日志级别
                if "ERROR" in log_content or "FATAL" in log_content or "无法将url解析为ip" in log_content:
                    level = "ERROR"
                elif "WARN" in log_content or "WARNING" in log_content:
                    level = "WARN"
                elif "INFO" in log_content:
                    level = "INFO"
                else:
                    level = default_level
                
                # 确定组件
                if "kylin_kms_daemon" in log_content:
                    component2 = "KMS"
                elif "systemd" in log_content:
                    component2 = "SYSTEMD"
                elif "kernel" in log_content:
                    component2 = "KERNEL"
                elif "network" in log_content:
                    component2 = "NETWORK"
                elif "memory" in log_content:
                    component2 = "MEMORY"
                elif "cpu" in log_content:
                    component2 = "CPU"
                elif "disk" in log_content:
                    component2 = "DISK"
                else:
                    component2 = default_component2
                
                # 构建BGL日志行
                bgl_line = f"{default_label} {default_id} {log_date} {default_code1} {log_time} {default_code1} {default_component1} {component2} {level} {log_content}"
                bgl_logs.append(bgl_line)
                
            except json.JSONDecodeError:
                # 如果行不是有效的JSON，跳过或处理原始行
                continue
    
    return bgl_logs

def load_metrics_files():
    """加载指标文件内容（向后兼容函数）"""
    try:
        # 加载blackbox_metrics.log
        with open('blackbox_metrics.log', 'r', encoding='utf-8') as f:
            blackbox_content = f.read()
        
        # 加载mysql_metrics.log
        with open('mysql_metrics.log', 'r', encoding='utf-8') as f:
            mysql_content = f.read()
        
        # 加载node_metrics.log
        with open('node_metrics.log', 'r', encoding='utf-8') as f:
            node_content = f.read()
        
        return blackbox_content, mysql_content, node_content
    except FileNotFoundError as e:
        print(f"指标文件未找到: {e}")
        return None, None, None

def main():
    """使用示例"""
    # 创建客户端
    client = FusionLogLLMClient("http://i-2.gpushare.com:25909")
    
    print("=" * 60)
    print("Fusion_LogLLM 融合异常检测客户端")
    print("模型已在服务器启动时自动加载，支持新的Prometheus数据格式")
    print("=" * 60)
    
    # 1. 健康检查
    print("1. 健康检查:")
    health = client.health_check()
    print(json.dumps(health, indent=2, ensure_ascii=False))
    print()
    
    # 检查模型是否已加载
    if not health.get('model_loaded', False):
        print("❌ 模型未加载，请检查服务器启动状态")
        return
    
    # 2. 获取配置信息
    print("2. 服务器配置:")
    config = client.get_config()
    print(json.dumps(config, indent=2, ensure_ascii=False))
    print()
    
    # 3. 获取GPU信息
    print("3. GPU信息:")
    gpu_info = client.get_gpu_info()
    print(json.dumps(gpu_info, indent=2, ensure_ascii=False))
    print()
    
    # 4. 获取指标处理信息
    print("4. 指标处理信息:")
    metrics_info = client.get_metrics_info()
    print(json.dumps(metrics_info, indent=2, ensure_ascii=False))
    print()
    
    # 5. 获取模型信息
    print("5. 模型信息:")
    model_info = client.get_model_info()
    print(json.dumps(model_info, indent=2, ensure_ascii=False))
    print()
    
    # 6. 准备测试数据
    print("6. 准备测试数据:")
    
    # 示例日志数据
    test_logs = [
        "2024-01-01 10:00:01 INFO [Service] Service started successfully",
        "2024-01-01 10:00:02 INFO [Service] Processing request 12345",
        "2024-01-01 10:00:03 ERROR [Service] Database connection failed",
        "2024-01-01 10:00:04 WARN [Service] Retrying connection...",
        "2024-01-01 10:00:05 INFO [Service] Connection restored",
        "2024-01-01 10:00:06 ERROR [Service] Memory usage exceeded threshold",
        "2024-01-01 10:00:07 INFO [Service] Memory cleanup completed",
        "2024-01-01 10:00:08 INFO [Service] Request 12345 completed"
    ]
    # from test_logs import get_test_logs_linux
    # test_logs_2 = get_test_logs_linux()
    bgl_logs = convert_loki_to_bgl('/var/log/loki_monitor_log.json')
    # 尝试加载真实的指标数据（新格式）
    print("尝试加载真实指标数据...")
    prometheus_data = client.load_prometheus_data_from_directory()
    
#     if not prometheus_data:
#         print("使用示例数据...")
#         # 使用示例数据（新格式）
#         prometheus_data = {
#             'blackbox_metrics': """
# {"timestamp": "2025-07-30T19:40:18.685018", "target": "https://www.baidu.com", "module": "http_2xx", "metric": "probe_success", "labels": {}, "value": 1.0}
# {"timestamp": "2025-07-30T19:40:18.688893", "target": "https://www.baidu.com", "module": "http_2xx", "metric": "probe_duration_seconds", "labels": {}, "value": 0.424565817}
# {"timestamp": "2025-07-30T19:40:18.689031", "target": "https://www.baidu.com", "module": "http_2xx", "metric": "probe_http_status_code", "labels": {}, "value": 200.0}
# """,
#             'mysql_metrics': """
# mysql_global_status_connections 11860.0
# mysql_global_status_queries 1365934.0
# mysql_global_status_slow_queries 5.0
# mysql_global_status_threads_connected 15.0
# mysql_global_status_threads_running 8.0
# """,
#             'node_metrics': """
# node_cpu_seconds_total{cpu="0",mode="idle"} 318.81
# node_load1 8.5
# node_load5 7.2
# node_load15 6.8
# node_memory_MemAvailable_bytes 2147483648
# """
#         }
    
    # 从JSON文件加载SkyWalking数据
    try:
        with open('/home/denerate/rca_sky-main/results/active_nodes_test.json', 'r', encoding='utf-8') as f:
            skywalking_json_data = json.load(f)
        
        # 将JSON数据转换为SkyWalking数据格式
        test_skywalking_data = [
            {
                "query_time": skywalking_json_data.get("query_time", ""),
                "active_nodes": skywalking_json_data.get("active_nodes", []),
                "summary": skywalking_json_data.get("summary", {}),
                "topology": skywalking_json_data.get("topology", {})
            }
        ]
        print(f"✅ 成功从 active_nodes_test.json 加载 SkyWalking 数据")
    except FileNotFoundError:
        print("❌ active_nodes_test.json 文件未找到，使用默认测试数据")
        test_skywalking_data = [
            {
                "query_time": "2024-01-01T10:00:00.000Z",
                "active_nodes": [
                    {
                        "service_name": "web-service",
                        "is_active": True,
                        "instances": [{"language": "JAVA", "status": "healthy"}]
                    },
                    {
                        "service_name": "database-service",
                        "is_active": True,
                        "instances": [{"language": "JAVA", "status": "warning"}]
                    }
                ],
                "summary": {
                    "total_active_nodes": 2,
                    "total_topology_nodes": 3,
                    "total_connections": 5
                }
            }
        ]
    except json.JSONDecodeError as e:
        print(f"❌ JSON 解析错误: {e}，使用默认测试数据")
        test_skywalking_data = [
            {
                "query_time": "2024-01-01T10:00:00.000Z",
                "active_nodes": [
                    {
                        "service_name": "web-service",
                        "is_active": True,
                        "instances": [{"language": "JAVA", "status": "healthy"}]
                    },
                    {
                        "service_name": "database-service",
                        "is_active": True,
                        "instances": [{"language": "JAVA", "status": "warning"}]
                    }
                ],
                "summary": {
                    "total_active_nodes": 2,
                    "total_topology_nodes": 3,
                    "total_connections": 5
                }
            }
        ]
    
    print(f"测试数据准备完成:")
    print(f"  - 日志数量: {len(bgl_logs)}")
    print(f"  - Prometheus指标类别: {len(prometheus_data)}")
    for key in prometheus_data.keys():
        print(f"    * {key}")
    print(f"  - SkyWalking记录: {len(test_skywalking_data)} 条")
    print()
    
    # 7. 验证数据格式
    print("7. 验证数据格式:")
    validation_result = client.validate_prometheus_data(prometheus_data)
    print(json.dumps(validation_result, indent=2, ensure_ascii=False))
    print()
    
    # 8. 测试指标解析
    print("8. 测试指标解析:")
    parse_test = client.test_metrics_parsing(prometheus_data, test_skywalking_data)
    print(json.dumps(parse_test, indent=2, ensure_ascii=False))
    print()
    
    # 9. 执行融合异常检测（新格式）
    print("9. 执行融合异常检测（新格式）:")
    detection_result = client.detect_anomalies_fusion(
        logs=bgl_logs,
        prometheus_data=prometheus_data,
        skywalking_data=test_skywalking_data,
        window_size=20,
        step_size=20,
        batch_size=32
    )
    print(json.dumps(detection_result, indent=2, ensure_ascii=False))
    anomly_information = client.extract_anomaly_information(detection_result)
    print(50*"=")
    print(anomly_information)
    print()
    
#     # 10. 对比测试（旧格式）
#     print("10. 对比测试（旧格式）:")
#     # 将新格式转换为旧格式
#     old_prometheus_data = f"""
# {prometheus_data.get('blackbox_metrics', '')}
# {prometheus_data.get('mysql_metrics', '')}
# {prometheus_data.get('node_metrics', '')}
# """
    
#     detection_result_old = client.detect_anomalies_fusion(
#         logs=test_logs,
#         prometheus_data=old_prometheus_data,
#         skywalking_data=test_skywalking_data,
#         window_size=3,
#         step_size=2,
#         batch_size=2
#     )
    
#     if 'error' not in detection_result_old:
#         print("✅ 旧格式检测成功")
#         print(f"  - 总序列数: {detection_result_old.get('total_sequences', 0)}")
#         print(f"  - 异常数量: {detection_result_old.get('anomaly_count', 0)}")
        
#         # 对比结果
#         new_time = detection_result.get('processing_time', 0)
#         old_time = detection_result_old.get('processing_time', 0)
#         if old_time > 0:
#             improvement = ((old_time - new_time) / old_time) * 100
#             print(f"  - 新格式性能提升: {improvement:.1f}%")
#     else:
#         print(f"❌ 旧格式检测失败: {detection_result_old['error']}")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    print("=" * 60)
    print("新功能总结:")
    print("1. ✅ 支持新的Prometheus数据格式")
    print("2. ✅ 提供多种数据加载方法")
    print("3. ✅ 数据格式验证功能")
    print("4. ✅ 向后兼容旧格式")
    print("5. ✅ 性能优化和对比")
    print("=" * 60)
    print("现在您可以多次调用 detect_anomalies_fusion() 进行异常检测")
    print("支持新的数据格式: {'blackbox_metrics': ..., 'mysql_metrics': ..., 'node_metrics': ...}")
    print("=" * 60)

if __name__ == "__main__":
    main() 