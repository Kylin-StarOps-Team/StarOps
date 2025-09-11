"""
根因分析模块
基于服务拓扑和异常关联性进行根因分析
"""

import networkx as nx
import numpy as np
import pandas as pd
from typing import Dict, List, Set, Tuple, Any
from datetime import datetime, timedelta
import logging
from collections import defaultdict, deque


class RootCauseAnalyzer:
    """根因分析器"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        self.max_depth = config.get('max_depth', 5)
        self.correlation_threshold = config.get('correlation_threshold', 0.7)
        self.time_correlation_window = config.get('time_correlation_window', 5)
        
    def build_service_graph(self, topology_data: Dict) -> nx.DiGraph:
        """构建服务依赖图"""
        G = nx.DiGraph()
        id2name = {}
        # 添加节点
        nodes = topology_data.get("nodes", [])
        for node in nodes:
            node_id = node.get("id")
            node_name = node.get("name")
            if node_id and node_name:
                id2name[node_id] = node_name
                G.add_node(node_name, **node)
        
        # 添加边（调用关系）
        calls = topology_data.get("calls", [])
        for call in calls:
            source = call.get("source")
            target = call.get("target")
            if source and target:
                G.add_edge(id2name.get(source, source), id2name.get(target, target), **call)

        self.logger.info(f"构建服务图: {G.number_of_nodes()} 个节点, {G.number_of_edges()} 条边")
        return G
    
    def calculate_service_criticality(self, G: nx.DiGraph) -> Dict[str, float]:
        """计算服务关键性得分"""
        criticality_scores = {}
        
        if G.number_of_nodes() == 0:
            return criticality_scores
        
        # 基于页面排名算法计算重要性
        try:
            pagerank_scores = nx.pagerank(G)
        except:
            pagerank_scores = {node: 1.0 for node in G.nodes()}
        
        # 计算出入度中心性
        in_degree_centrality = nx.in_degree_centrality(G)
        out_degree_centrality = nx.out_degree_centrality(G)
        
        # 计算介数中心性
        try:
            betweenness_centrality = nx.betweenness_centrality(G)
        except:
            betweenness_centrality = {node: 0.0 for node in G.nodes()}
        
        # 综合计算关键性得分
        for node in G.nodes():
            criticality_scores[node] = (
                0.4 * pagerank_scores.get(node, 0) +
                0.3 * in_degree_centrality.get(node, 0) +
                0.2 * out_degree_centrality.get(node, 0) +
                0.1 * betweenness_centrality.get(node, 0)
            )
        
        return criticality_scores
    
    def find_upstream_services(self, G: nx.DiGraph, service: str, max_depth: int = None) -> Set[str]:
        """找到上游服务"""
        if max_depth is None:
            max_depth = self.max_depth
            
        upstream_services = set()
        
        # 检查节点是否在图中
        if not G.has_node(service):
            self.logger.warning(f"服务 {service} 不在拓扑图中")
            return upstream_services
            
        queue = deque([(service, 0)])
        visited = {service}
        
        while queue:
            current_service, depth = queue.popleft()
            
            if depth >= max_depth:
                continue
                
            # 获取所有调用当前服务的上游服务
            predecessors = list(G.predecessors(current_service))
            for predecessor in predecessors:
                if predecessor not in visited:
                    upstream_services.add(predecessor)
                    visited.add(predecessor)
                    queue.append((predecessor, depth + 1))
        
        return upstream_services
    
    def find_downstream_services(self, G: nx.DiGraph, service: str, max_depth: int = None) -> Set[str]:
        """找到下游服务"""
        if max_depth is None:
            max_depth = self.max_depth
            
        downstream_services = set()
        
        # 检查节点是否在图中
        if not G.has_node(service):
            self.logger.warning(f"服务 {service} 不在拓扑图中")
            return downstream_services
            
        queue = deque([(service, 0)])
        visited = {service}
        
        while queue:
            current_service, depth = queue.popleft()
            
            if depth >= max_depth:
                continue
                
            # 获取当前服务调用的所有下游服务
            successors = list(G.successors(current_service))
            for successor in successors:
                if successor not in visited:
                    downstream_services.add(successor)
                    visited.add(successor)
                    queue.append((successor, depth + 1))
        
        return downstream_services
    
    def calculate_anomaly_correlation(self, anomalies: List[Dict]) -> Dict[Tuple[str, str], float]:
        """计算异常之间的相关性"""
        correlations = {}
        
        # 按服务分组异常
        service_anomalies = defaultdict(list)
        for anomaly in anomalies:
            service_name = anomaly.get("service")
            if service_name:
                service_anomalies[service_name].append(anomaly)
        
        services = list(service_anomalies.keys())
        
        # 计算服务间异常的相关性
        for i, service1 in enumerate(services):
            for j, service2 in enumerate(services[i+1:], i+1):
                correlation = self._calculate_service_anomaly_correlation(
                    service_anomalies[service1],
                    service_anomalies[service2]
                )
                if correlation > 0:
                    correlations[(service1, service2)] = correlation
        
        return correlations
    
    def _calculate_service_anomaly_correlation(self, anomalies1: List[Dict], anomalies2: List[Dict]) -> float:
        """计算两个服务异常的相关性"""
        if not anomalies1 or not anomalies2:
            return 0.0
        
        # 基于异常类型的相似性
        types1 = set(anomaly.get("type", "") for anomaly in anomalies1)
        types2 = set(anomaly.get("type", "") for anomaly in anomalies2)
        
        if not types1 or not types2:
            return 0.0
        
        # Jaccard相似性
        intersection = len(types1 & types2)
        union = len(types1 | types2)
        type_similarity = intersection / union if union > 0 else 0
        
        # 基于严重程度的相似性
        severity_weight = {
            "HIGH": 3,
            "MEDIUM": 2,
            "LOW": 1
        }
        
        avg_severity1 = np.mean([severity_weight.get(anomaly.get("severity", "LOW"), 1) for anomaly in anomalies1])
        avg_severity2 = np.mean([severity_weight.get(anomaly.get("severity", "LOW"), 1) for anomaly in anomalies2])
        
        severity_similarity = 1 - abs(avg_severity1 - avg_severity2) / 3.0
        
        # 综合相关性
        correlation = 0.7 * type_similarity + 0.3 * severity_similarity
        
        return correlation
    
    def identify_root_causes(self, G: nx.DiGraph, anomalies_data: Dict) -> List[Dict]:
        """识别根因"""
        all_anomalies = []
        for priority_anomalies in anomalies_data.get("anomalies", {}).values():
            all_anomalies.extend(priority_anomalies)
        
        if not all_anomalies:
            return []
        
        self.logger.info(f"分析 {len(all_anomalies)} 个异常的根因")
        
        # 计算服务关键性
        criticality_scores = self.calculate_service_criticality(G)
        
        # 计算异常相关性
        anomaly_correlations = self.calculate_anomaly_correlation(all_anomalies)
        
        # 按服务分组异常
        service_anomalies = defaultdict(list)
        for anomaly in all_anomalies:
            service_name = anomaly.get("service")
            if service_name:
                service_anomalies[service_name].append(anomaly)
        
        root_causes = []
        
        for service, anomalies in service_anomalies.items():
            if not anomalies:
                continue
            
            # 计算根因得分
            root_cause_score = self._calculate_root_cause_score(
                service, anomalies, G, criticality_scores, anomaly_correlations
            )
            
            # 找到相关的上下游服务
            upstream_services = self.find_upstream_services(G, service, max_depth=2)
            downstream_services = self.find_downstream_services(G, service, max_depth=2)
            
            # 分析影响传播路径
            impact_analysis = self._analyze_impact_propagation(
                service, anomalies, G, service_anomalies
            )
            
            root_cause = {
                "root_service": service,
                "anomalies": anomalies,
                "root_cause_score": root_cause_score,
                "criticality_score": criticality_scores.get(service, 0),
                "upstream_services": list(upstream_services),
                "downstream_services": list(downstream_services),
                "impact_analysis": impact_analysis,
                "confidence": self._calculate_confidence(root_cause_score, anomalies),
                "recommendation": self._generate_recommendation(service, anomalies, impact_analysis)
            }
            
            root_causes.append(root_cause)
        
        # 按根因得分排序
        root_causes.sort(key=lambda x: x["root_cause_score"], reverse=True)
        
        return root_causes
    
    def _calculate_root_cause_score(self, service: str, anomalies: List[Dict], 
                                   G: nx.DiGraph, criticality_scores: Dict[str, float],
                                   anomaly_correlations: Dict[Tuple[str, str], float]) -> float:
        """计算根因得分"""
        # 基础异常严重程度得分
        severity_weight = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
        severity_score = sum(severity_weight.get(anomaly.get("severity", "LOW"), 1) for anomaly in anomalies)
        
        # 服务关键性得分
        criticality_score = criticality_scores.get(service, 0) * 10
        
        # 异常数量得分
        anomaly_count_score = len(anomalies)
        
        # 相关性得分（与其他服务异常的相关性）
        correlation_score = 0
        for (s1, s2), correlation in anomaly_correlations.items():
            if s1 == service or s2 == service:
                correlation_score += correlation
        
        # 拓扑位置得分（上游服务更可能是根因）
        topology_score = 0
        if G.has_node(service):
            # 出度高的服务更可能是根因
            out_degree = G.out_degree(service)
            in_degree = G.in_degree(service)
            if in_degree + out_degree > 0:
                topology_score = out_degree / (in_degree + out_degree) * 5
        
        # 综合根因得分
        total_score = (
            0.3 * severity_score +
            0.25 * criticality_score +
            0.2 * anomaly_count_score +
            0.15 * correlation_score +
            0.1 * topology_score
        )
        
        return total_score
    
    def _analyze_impact_propagation(self, root_service: str, anomalies: List[Dict], 
                                   G: nx.DiGraph, all_service_anomalies: Dict[str, List[Dict]]) -> Dict:
        """分析影响传播"""
        impact_analysis = {
            "affected_services": [],
            "propagation_paths": [],
            "impact_severity": "LOW"
        }
        
        if not G.has_node(root_service):
            return impact_analysis
        
        # 找到受影响的下游服务
        downstream_services = self.find_downstream_services(G, root_service, max_depth=3)
        
        affected_services = []
        max_severity_weight = 0
        
        for downstream_service in downstream_services:
            if downstream_service in all_service_anomalies:
                downstream_anomalies = all_service_anomalies[downstream_service]
                
                # 计算影响严重程度
                severity_weights = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
                avg_severity = np.mean([
                    severity_weights.get(anomaly.get("severity", "LOW"), 1) 
                    for anomaly in downstream_anomalies
                ])
                
                max_severity_weight = max(max_severity_weight, avg_severity)
                
                # 找到从根因到该服务的路径
                try:
                    path = nx.shortest_path(G, root_service, downstream_service)
                    impact_analysis["propagation_paths"].append({
                        "target": downstream_service,
                        "path": path,
                        "path_length": len(path) - 1
                    })
                except nx.NetworkXNoPath:
                    pass
                
                affected_services.append({
                    "service": downstream_service,
                    "anomaly_count": len(downstream_anomalies),
                    "avg_severity": avg_severity
                })
        
        impact_analysis["affected_services"] = affected_services
        
        # 确定整体影响严重程度
        if max_severity_weight >= 2.5:
            impact_analysis["impact_severity"] = "HIGH"
        elif max_severity_weight >= 1.5:
            impact_analysis["impact_severity"] = "MEDIUM"
        else:
            impact_analysis["impact_severity"] = "LOW"
        
        return impact_analysis
    
    def _calculate_confidence(self, root_cause_score: float, anomalies: List[Dict]) -> float:
        """计算置信度"""
        # 基于根因得分和异常一致性计算置信度
        score_confidence = min(root_cause_score / 20.0, 1.0)  # 归一化到0-1
        
        # 异常类型一致性
        anomaly_types = [anomaly.get("type", "") for anomaly in anomalies]
        unique_types = set(anomaly_types)
        type_consistency = len(unique_types) / len(anomaly_types) if anomaly_types else 0
        
        # 综合置信度
        confidence = 0.7 * score_confidence + 0.3 * (1 - type_consistency)
        return min(max(confidence, 0.0), 1.0)
    
    def _generate_recommendation(self, service: str, anomalies: List[Dict], 
                               impact_analysis: Dict) -> str:
        """生成修复建议"""
        recommendations = []
        
        # 基于异常类型生成建议
        anomaly_types = set(anomaly.get("type", "") for anomaly in anomalies)
        
        if "high_error_rate" in anomaly_types:
            recommendations.append(f"检查服务 {service} 的错误日志，排查导致错误率上升的问题")
        
        if "high_response_time" in anomaly_types:
            recommendations.append(f"分析服务 {service} 的性能瓶颈，可能需要优化代码或增加资源")
        
        if "low_sla" in anomaly_types:
            recommendations.append(f"检查服务 {service} 的可用性，确保服务正常运行")
        
        if "unstable_throughput" in anomaly_types:
            recommendations.append(f"检查服务 {service} 的负载均衡和资源分配")
        
        # 基于影响分析生成建议
        affected_count = len(impact_analysis.get("affected_services", []))
        if affected_count > 0:
            recommendations.append(f"优先处理服务 {service}，因为它影响了 {affected_count} 个下游服务")
        
        if impact_analysis.get("impact_severity") == "HIGH":
            recommendations.append("建议立即处理，影响严重程度较高")
        
        return " | ".join(recommendations) if recommendations else "建议进一步调查该服务的异常情况"
    
    def analyze(self, skywalking_data: Dict, anomalies_data: Dict) -> Dict:
        """执行根因分析"""
        self.logger.info("开始根因分析")
        
        # 构建服务依赖图
        topology_data = skywalking_data.get("topology", {})
        service_graph = self.build_service_graph(topology_data)
        
        # 识别根因
        root_causes = self.identify_root_causes(service_graph, anomalies_data)
        
        self.logger.info(f"识别出 {len(root_causes)} 个潜在根因")
        
        return {
            "analysis_timestamp": datetime.now().isoformat(),
            "root_causes": root_causes,
            "service_graph_stats": {
                "nodes": service_graph.number_of_nodes(),
                "edges": service_graph.number_of_edges()
            }
        }
