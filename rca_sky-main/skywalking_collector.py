"""
SkyWalking数据采集模块
负责从SkyWalking获取服务监控数据和调用链信息
"""

import pytz
import requests
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import pandas as pd

# 设置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SkyWalkingCollector:
    """SkyWalking数据采集器"""
    
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        # print("debug - ", self.base_url)
        self.graphql_url = f"{self.base_url}/graphql"
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
        
    def _execute_graphql_query(self, query: str, variables: Dict = None) -> Optional[Dict]:
        """执行GraphQL查询"""
        try:
            payload = {
                "query": query,
                "variables": variables or {}
            }
            
            headers = {
                "Content-Type": "application/json",
            }
            
            response = requests.post(
                self.graphql_url,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                if "errors" in result:
                    self.logger.error(f"GraphQL查询错误: {result['errors']}")
                    return None
                return result.get("data")
            else:
                self.logger.error(f"HTTP请求失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"执行GraphQL查询时发生错误: {str(e)}")
            return None
    
    def get_services(self, hours_ago: int = 24) -> List[Dict]:
        """获取所有服务列表"""
        # 获取时间范围
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours_ago)
        
        query = """
        query queryServices($duration: Duration!) {
            services: getAllServices(duration: $duration) {
                key: id
                label: name
            }
        }
        """
        
        variables = {
            "duration": {
                "start": start_time.strftime("%Y-%m-%d %H%M"),
                "end": end_time.strftime("%Y-%m-%d %H%M"),
                "step": "MINUTE"
            }
        }
        
        result = self._execute_graphql_query(query, variables)
        if result and result.get("services"):
            # 转换格式以保持兼容性
            formatted_services = []
            for service in result["services"]:
                formatted_services.append({
                    "id": service.get("key"),
                    "name": service.get("label"),
                    "shortName": service.get("label"),
                    "group": ""
                })
            return formatted_services
        return []

    def get_service_metrics_once(self, service_name: str, start_time: datetime, end_time: datetime) -> Dict:
        """获取服务指标数据 - 一次性获取所有指标"""
        start_str = start_time.strftime("%Y-%m-%d %H%M")
        end_str = end_time.strftime("%Y-%m-%d %H%M")
        
        duration = {
            "start": start_str,
            "end": end_str,
            "step": "MINUTE"
        }
        
        entity = {
            "serviceName": service_name,
            "normal": True
        }
        
        # 一次性查询所有指标的GraphQL
        query = """
        query queryAllMetrics($duration: Duration!, $entity: Entity!, $cpm: String!, $sla: String!, $respTime: String!) {
            cpmMetrics: execExpression(expression: $cpm, entity: $entity, duration: $duration) {
                type
                results {
                    metric {
                        labels {
                            key
                            value
                        }
                    }
                    values {
                        name: id
                        value
                        refId: traceID
                        owner {
                            scope
                            serviceID
                            serviceName
                            normal
                            serviceInstanceID
                            serviceInstanceName
                            endpointID
                            endpointName
                        }
                    }
                }
                error
            }
            slaMetrics: execExpression(expression: $sla, entity: $entity, duration: $duration) {
                type
                results {
                    metric {
                        labels {
                            key
                            value
                        }
                    }
                    values {
                        name: id
                        value
                        refId: traceID
                        owner {
                            scope
                            serviceID
                            serviceName
                            normal
                            serviceInstanceID
                            serviceInstanceName
                            endpointID
                            endpointName
                        }
                    }
                }
                error
            }
            respTimeMetrics: execExpression(expression: $respTime, entity: $entity, duration: $duration) {
                type
                results {
                    metric {
                        labels {
                            key
                            value
                        }
                    }
                    values {
                        name: id
                        value
                        refId: traceID
                        owner {
                            scope
                            serviceID
                            serviceName
                            normal
                            serviceInstanceID
                            serviceInstanceName
                            endpointID
                            endpointName
                        }
                    }
                }
                error
            }
        }
        """
        
        variables = {
            "duration": duration,
            "entity": entity,
            "cpm": "service_cpm",
            "sla": "service_sla",
            "respTime": "service_resp_time"
        }
        
        try:
            result = self._execute_graphql_query(query, variables)
            
            if result:
                metrics_result = {}
                
                # 处理CPM指标
                if result.get("cpmMetrics") and not result["cpmMetrics"].get("error"):
                    metrics_result['service_cpm'] = self._format_expression_result(result["cpmMetrics"])
                else:
                    metrics_result['service_cpm'] = {"label": "", "values": {"values": []}}
                
                # 处理SLA指标
                if result.get("slaMetrics") and not result["slaMetrics"].get("error"):
                    metrics_result['service_sla'] = self._format_expression_result(result["slaMetrics"])
                else:
                    metrics_result['service_sla'] = {"label": "", "values": {"values": []}}
                
                # 处理响应时间指标
                if result.get("respTimeMetrics") and not result["respTimeMetrics"].get("error"):
                    metrics_result['service_resp_time'] = self._format_expression_result(result["respTimeMetrics"])
                else:
                    metrics_result['service_resp_time'] = {"label": "", "values": {"values": []}}
                
                return metrics_result
            else:
                # 如果查询失败，返回空数据
                return {
                    'service_cpm': {"label": "", "values": {"values": []}},
                    'service_sla': {"label": "", "values": {"values": []}},
                    'service_resp_time': {"label": "", "values": {"values": []}}
                }
                
        except Exception as e:
            self.logger.warning(f"获取服务 {service_name} 指标失败: {str(e)}")
            return {
                'service_cpm': {"label": "", "values": {"values": []}},
                'service_sla': {"label": "", "values": {"values": []}},
                'service_resp_time': {"label": "", "values": {"values": []}}
            }

    def _format_expression_result(self, expression_result: Dict) -> Dict:
        """将execExpression的结果格式化为与原来readMetricsValues相同的格式"""
        if not expression_result or not expression_result.get("results"):
            return {"label": "", "values": {"values": []}}
        
        # 提取values数据
        values = []
        for result in expression_result["results"]:
            if result.get("values"):
                for value_item in result["values"]:
                    values.append({"value": int(value_item.get("value")) if value_item.get("value") is not None else None})

        return {
            "label": "",  # execExpression结果中通常不包含label
            "values": {"values": values}
        }
    
    def get_trace_data(self, service_id: str = None, start_time: datetime = None, end_time: datetime = None, 
                      min_duration: int = 100, limit: int = 50) -> List[Dict]:
        """获取调用链数据"""
        if start_time is None:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=1)
        
        start_str = start_time.strftime("%Y-%m-%d %H%M")
        end_str = end_time.strftime("%Y-%m-%d %H%M")
        
        query = """
        query queryTraces($condition: TraceQueryCondition!) {
            traces: queryBasicTraces(condition: $condition) {
                traces {
                    segmentId
                    endpointNames
                    duration
                    start
                    isError
                    traceIds
                }
            }
        }
        """
        
        condition = {
            "queryDuration": {
                "start": start_str,
                "end": end_str,
                "step": "MINUTE"
            },
            "traceState": "ALL",
            "queryOrder": "BY_DURATION",
            "paging": {
                "pageNum": 1,
                "pageSize": limit
            }
        }
        
        if service_id:
            condition["serviceId"] = service_id
        variables = {"condition": condition}
        
        try:
            result = self._execute_graphql_query(query, variables)
            if result and "traces" in result:
                traces = result["traces"].get("traces", [])
                
                return traces
        except Exception as e:
            self.logger.warning(f"获取调用链数据失败: {str(e)}")
        
        return []
    
    def get_service_topology(self, start_time: datetime, end_time: datetime) -> Dict:
        """获取服务拓扑图"""
        # 先获取服务列表
        services = self.get_services(hours_ago=24)
        if not services:
            return {"nodes": [], "calls": []}
        
        service_ids = [service['id'] for service in services if service.get('id')]
        
        if not service_ids:
            return {"nodes": [], "calls": []}
        
        start_str = start_time.strftime("%Y-%m-%d %H%M")
        end_str = end_time.strftime("%Y-%m-%d %H%M")
        # print(f"获取拓扑图，时间范围: {start_str} - {end_str}, 服务数量: {len(service_ids)}")
        
        query = """
        query queryTopology($serviceIds: [ID!]!, $duration: Duration!) {
            topology: getServicesTopology(serviceIds: $serviceIds, duration: $duration) {
                nodes {
                    id
                    name
                    type
                    isReal
                }
                calls {
                    source
                    target
                    detectPoints
                }
            }
        }
        """
        
        variables = {
            "serviceIds": service_ids,
            "duration": {
                "start": start_str,
                "end": end_str,
                "step": "MINUTE"
            }
        }
        
        result = self._execute_graphql_query(query, variables)
        # print(result)
        if result and result.get("topology"):
            return result["topology"]
        return {"nodes": [], "calls": []}
    
    def get_service_instances(self, service_name: str, start_time: datetime, end_time: datetime) -> List[Dict]:
        """获取服务实例信息"""
        # 1. 先根据服务名称找到服务ID
        # 我们复用 get_services 方法来获取所有服务，然后从中查找
        # 注意：为了效率，更优的做法是实现一个 findService(serviceName:...) 的GraphQL查询
        all_services = self.get_services(hours_ago=24)
        service_id = None
        for service in all_services:
            if service.get("name") == service_name:
                service_id = service.get("id")
                break
        
        if not service_id:
            self.logger.warning(f"未能找到服务 '{service_name}' 的ID，无法查询实例列表。")
            return []

        # 2. 根据服务ID查询实例
        start_str = start_time.strftime("%Y-%m-%d %H%M")
        end_str = end_time.strftime("%Y-%m-%d %H%M")

        query = """
        query getInstances($serviceId: ID!, $duration: Duration!) {
            instances: getServiceInstances(serviceId: $serviceId, duration: $duration) {
                id
                name
                language
                instanceUUID
                attributes {
                    name
                    value
                }
            }
        }
        """
        
        variables = {
            "serviceId": service_id,
            "duration": {
                "start": start_str,
                "end": end_str,
                "step": "MINUTE"
            }
        }

        result = self._execute_graphql_query(query, variables)
        if result and result.get("instances"):
            return result["instances"]
        
        self.logger.warning(f"未能获取到服务 '{service_name}' (ID: {service_id}) 的实例信息。")
        return []
    
    def get_active_nodes(self, query_time: datetime = None, time_window_minutes: int = 5) -> List[Dict]:
        """获取指定时间活跃的节点
        
        Args:
            query_time: 查询时间点，默认为当前时间
            time_window_minutes: 时间窗口（分钟），默认5分钟
        
        Returns:
            List[Dict]: 活跃节点列表，包含节点基本信息和活动状态
        """
        if query_time is None:
            query_time = datetime.now(pytz.timezone('UTC'))
        
        # 设置查询时间窗口
        start_time = query_time - timedelta(minutes=time_window_minutes // 2)
        end_time = query_time + timedelta(minutes=time_window_minutes // 2)
        
        start_str = start_time.strftime("%Y-%m-%d %H%M")
        end_str = end_time.strftime("%Y-%m-%d %H%M")
        
        self.logger.info(f"查询活跃节点，时间窗口: {start_str} - {end_str}")
        
        # 获取服务列表（活跃服务）
        services = self.get_services(hours_ago=24)
        if not services:
            return []
        
        active_nodes = []
        
        for service in services:
            service_name = service.get("name")
            service_id = service.get("id")
            
            if not service_name or not service_id:
                continue
            
            try:
                # 检查服务是否有指标数据（判断是否活跃）
                metrics = self.get_service_metrics_once(service_name, start_time, end_time)
                
                # 检查是否有非空的指标数据
                has_activity = False
                if metrics:
                    for metric_name, metric_data in metrics.items():
                        if (metric_data.get("values", {}).get("values") and 
                            any(v.get("value") is not None for v in metric_data["values"]["values"])):
                            has_activity = True
                            break
                
                # 如果有活动，获取服务实例信息
                instances = []
                if has_activity:
                    instances = self.get_service_instances(service_name, start_time, end_time)
                
                # 构建节点信息
                node_info = {
                    "service_id": service_id,
                    "service_name": service_name,
                    "is_active": has_activity,
                    "query_time": query_time.isoformat(),
                    "time_window": {
                        "start": start_time.isoformat(),
                        "end": end_time.isoformat()
                    },
                    "instances": instances,
                    # "metrics_summary": self._summarize_metrics(metrics) if has_activity else {}
                }
                
                # 只返回活跃的节点，或者根据需要返回所有节点
                if has_activity:
                    active_nodes.append(node_info)
                    
            except Exception as e:
                self.logger.warning(f"检查服务 {service_name} 活动状态时出错: {str(e)}")
                continue
        
        self.logger.info(f"发现 {len(active_nodes)} 个活跃节点")
        return active_nodes

    def _summarize_metrics(self, metrics: Dict) -> Dict:
        """汇总指标数据，提取关键信息"""
        summary = {}
        
        for metric_name, metric_data in metrics.items():
            if not metric_data or not metric_data.get("values", {}).get("values"):
                continue
                
            values = [v.get("value") for v in metric_data["values"]["values"] if v.get("value") is not None]
            
            if values:
                summary[metric_name] = {
                    "latest_value": values[-1] if values else None,
                    "avg_value": sum(values) / len(values) if values else 0,
                    "max_value": max(values) if values else 0,
                    "min_value": min(values) if values else 0,
                    "data_points": len(values)
                }
        
        return summary

    def get_active_nodes_with_topology(self, query_time: datetime = None, time_window_minutes: int = 5) -> Dict:
        """获取指定时间活跃的节点及其拓扑关系
        
        Args:
            query_time: 查询时间点，默认为当前时间
            time_window_minutes: 时间窗口（分钟），默认5分钟
        
        Returns:
            Dict: 包含活跃节点列表和拓扑关系
        """
        if query_time is None:
            query_time = datetime.now(pytz.timezone('UTC'))
        
        # 获取活跃节点
        active_nodes = self.get_active_nodes(query_time, time_window_minutes)
        
        # 设置拓扑查询时间窗口
        start_time = query_time - timedelta(minutes=time_window_minutes // 2)
        end_time = query_time + timedelta(minutes=time_window_minutes // 2)
        
        # 获取拓扑信息
        topology = self.get_service_topology(start_time, end_time)
        
        # 过滤拓扑，只保留活跃节点相关的连接
        active_service_ids = {node["service_id"] for node in active_nodes}
        
        filtered_topology = {
            "nodes": [node for node in topology.get("nodes", []) 
                    if node.get("id") in active_service_ids],
            "calls": [call for call in topology.get("calls", [])
                    if call.get("source") in active_service_ids or call.get("target") in active_service_ids]
        }
        
        return {
            "query_time": query_time.isoformat(),
            "time_window": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat()
            },
            "active_nodes": active_nodes,
            "topology": filtered_topology,
            "summary": {
                "total_active_nodes": len(active_nodes),
                "total_topology_nodes": len(filtered_topology["nodes"]),
                "total_connections": len(filtered_topology["calls"])
            }
        }

    def collect_all_data(self, time_window_minutes: int = 15) -> Dict:
        """收集所有相关数据"""
        server_timezone = pytz.timezone('UTC')
        end_time = datetime.now(server_timezone)
        start_time = end_time - timedelta(minutes=time_window_minutes)
        
        self.logger.info(f"开始收集数据，时间范围: {start_time} - {end_time}")
        
        # 获取服务列表
        services = self.get_services(hours_ago=1)  # 使用更短的时间范围获取活跃服务
        self.logger.info(f"发现 {len(services)} 个服务")
        # print(services)
        
        # 获取拓扑信息
        topology = self.get_service_topology(start_time, end_time)
        
        # 收集每个服务的详细数据
        services_data = []
        for service in services:
            service_name = service.get("name")
            if not service_name:
                continue
                
            self.logger.info(f"收集服务 {service_name} 的数据")
            
            # 获取服务指标
            metrics = self.get_service_metrics_once(service_name, start_time, end_time)
            # print('--' * 50)
            # self.logger.info(f"服务 {service_name} 指标: {json.dumps(metrics, indent=2, ensure_ascii=False)}")
            
            # 获取调用链数据
            traces = self.get_trace_data(service_id=service.get("id"), start_time=start_time, end_time=end_time)
            # print('--' * 50)
            # self.logger.info(f"服务 {service_name} 调用链数据: {json.dumps(traces, indent=2, ensure_ascii=False)}")
            
            # 获取服务实例
            instances = self.get_service_instances(service_name, start_time, end_time)
            # print('--' * 50)
            # self.logger.info(f"服务 {service_name} 实例: {json.dumps(instances, indent=2, ensure_ascii=False)}")

            services_data.append({
                "service": service,
                "metrics": metrics,
                "traces": traces,
                "instances": instances
            })
        
        return {
            "timestamp": end_time.isoformat(),
            "time_range": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat()
            },
            "topology": topology,
            "services": services_data
        }
    
    def health_check(self) -> bool:
        """检查SkyWalking连接状态"""
        try:
            # 使用简单的服务查询来检查连接
            services = self.get_services(hours_ago=1)
            return len(services) >= 0  # 即使没有服务，只要查询成功就说明连接正常
        except Exception as e:
            self.logger.error(f"健康检查失败: {str(e)}")
            return False


if __name__ == "__main__":
    collector = SkyWalkingCollector("http://1.92.124.5:8080")
    if collector.health_check():
        print("SkyWalking连接正常")
        server_timezone = pytz.timezone('UTC') 
        data = collector.get_active_nodes(query_time=datetime.now(server_timezone), time_window_minutes=15)
        with open('results/active_nodes.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print("SkyWalking连接异常，请检查配置和服务状态")