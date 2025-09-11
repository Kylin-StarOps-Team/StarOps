"""
Ollama智能分析模块
使用本地部署的大模型进行智能分析和推理
"""

import requests
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime


class OllamaAnalyzer:
    """Ollama智能分析器"""
    
    def __init__(self, base_url: str, model: str, timeout: int = 600):
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
        self.api_key = "sk-2f6db3ed3478476e81fddb0aaa570ee4"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
    def _send_request(self, prompt: str, system_prompt: str = None) -> Optional[str]:
        """发送请求到Ollama"""
        try:
            url = self.base_url
            # url = f"{self.base_url}/api/generate"
            
            # payload = {
            #     "model": self.model,
            #     "prompt": prompt,
            #     "stream": False,
            #     "options": {
            #         "temperature": 0.3,  # 降低随机性，提高分析的一致性
            #         "top_p": 0.9,
            #         "num_predict": 2048
            #     }
            # }

            messages = [{"role": "system", "content": system_prompt}]
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.3,
                "max_tokens": 800
            }
            
            if system_prompt:
                payload["system"] = system_prompt
            
            response = requests.post(
                url,
                json=payload,
                headers=self.headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")
            else:
                self.logger.error(f"Ollama请求失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"发送Ollama请求时发生错误: {str(e)}")
            return None
    
    def analyze_anomalies(self, anomalies_data: Dict) -> Dict[str, Any]:
        """分析异常数据"""
        system_prompt = """你是一个专业的微服务异常分析专家。请基于提供的异常检测数据，进行深入分析并提供专业见解。
        
        分析要求：
        1. 识别异常的严重程度和紧急程度
        2. 分析异常之间的潜在关联性
        3. 预测可能的影响范围
        4. 提供优先级建议
        5. 给出可能的原因分析
        
        请以结构化的方式回答，包含：
        - 关键发现
        - 风险评估
        - 优先级排序
        - 建议措施"""
        
        # 构建提示词
        prompt = f"""请分析以下微服务异常检测结果：

检测时间: {anomalies_data.get('detection_timestamp', 'unknown')}

异常统计:
- 总服务数: {anomalies_data.get('metrics_summary', {}).get('total_services', 0)}
- 异常服务数: {anomalies_data.get('metrics_summary', {}).get('services_with_anomalies', 0)}

高优先级异常:
"""
        
        anomalies = anomalies_data.get("anomalies", {})
        
        # 添加高优先级异常
        high_priority = anomalies.get("high_priority", [])
        if high_priority:
            for i, anomaly in enumerate(high_priority[:10]):  # 限制数量避免prompt过长
                prompt += f"{i+1}. 服务: {anomaly.get('service', 'unknown')}\n"
                prompt += f"   类型: {anomaly.get('type', 'unknown')}\n"
                prompt += f"   描述: {anomaly.get('description', 'unknown')}\n"
                if 'value' in anomaly:
                    prompt += f"   数值: {anomaly['value']}\n"
                prompt += "\n"
        else:
            prompt += "无高优先级异常\n\n"
        
        # 添加中优先级异常
        prompt += "中优先级异常:\n"
        medium_priority = anomalies.get("medium_priority", [])
        if medium_priority:
            for i, anomaly in enumerate(medium_priority[:5]):  # 限制数量
                prompt += f"{i+1}. 服务: {anomaly.get('service', 'unknown')}\n"
                prompt += f"   类型: {anomaly.get('type', 'unknown')}\n"
                prompt += f"   描述: {anomaly.get('description', 'unknown')}\n\n"
        else:
            prompt += "无中优先级异常\n\n"
        
        prompt += "请进行详细分析并提供专业建议。"
        
        self.logger.info("正在分析异常数据...")
        response = self._send_request(prompt, system_prompt)
        
        return {
            "analysis_type": "anomaly_analysis",
            "timestamp": datetime.now().isoformat(),
            "input_summary": {
                "total_anomalies": len(high_priority) + len(medium_priority) + len(anomalies.get("low_priority", [])),
                "high_priority_count": len(high_priority),
                "medium_priority_count": len(medium_priority)
            },
            "ai_analysis": response,
            "success": response is not None
        }
    
    def analyze_root_causes(self, root_cause_data: Dict) -> Dict[str, Any]:
        """分析根因数据"""
        system_prompt = """你是一个微服务架构和故障排除专家。请基于根因分析结果，提供深入的技术分析和解决方案。

        分析要求：
        1. 评估根因分析的准确性和可信度
        2. 识别最可能的真实根因
        3. 分析故障传播路径的合理性
        4. 提供具体的修复建议和预防措施
        5. 评估修复的紧急程度和复杂度
        
        请提供：
        - 根因可信度评估
        - 修复优先级排序
        - 详细的解决方案
        - 预防措施建议"""
        
        # 构建提示词
        prompt = f"""请分析以下根因分析结果：

分析时间: {root_cause_data.get('analysis_timestamp', 'unknown')}
服务图统计: {root_cause_data.get('service_graph_stats', {})}

根因分析结果:
"""
        
        root_causes = root_cause_data.get("root_causes", [])
        
        for i, root_cause in enumerate(root_causes[:5]):  # 限制数量
            prompt += f"\n根因 {i+1}:\n"
            prompt += f"- 根因服务: {root_cause.get('root_service', 'unknown')}\n"
            prompt += f"- 根因得分: {root_cause.get('root_cause_score', 0):.2f}\n"
            prompt += f"- 置信度: {root_cause.get('confidence', 0):.2f}\n"
            prompt += f"- 关键性得分: {root_cause.get('criticality_score', 0):.2f}\n"
            
            anomalies = root_cause.get('anomalies', [])
            if anomalies:
                prompt += f"- 异常数量: {len(anomalies)}\n"
                prompt += "- 主要异常类型: "
                anomaly_types = list(set(anomaly.get('type', '') for anomaly in anomalies))
                prompt += ", ".join(anomaly_types[:3]) + "\n"
            
            impact = root_cause.get('impact_analysis', {})
            affected_services = impact.get('affected_services', [])
            if affected_services:
                prompt += f"- 影响的下游服务数: {len(affected_services)}\n"
                prompt += f"- 影响严重程度: {impact.get('impact_severity', 'unknown')}\n"
            
            upstream = root_cause.get('upstream_services', [])
            if upstream:
                prompt += f"- 上游服务: {', '.join(upstream[:3])}\n"
            
            recommendation = root_cause.get('recommendation', '')
            if recommendation:
                prompt += f"- 当前建议: {recommendation}\n"
        
        prompt += "\n请基于以上信息提供专业的根因分析评估和详细的解决方案。"
        
        self.logger.info("正在分析根因数据...")
        response = self._send_request(prompt, system_prompt)
        
        return {
            "analysis_type": "root_cause_analysis",
            "timestamp": datetime.now().isoformat(),
            "input_summary": {
                "total_root_causes": len(root_causes),
                "analyzed_root_causes": min(len(root_causes), 5)
            },
            "ai_analysis": response,
            "success": response is not None
        }
    
    def generate_comprehensive_report(self, anomalies_data: Dict, root_cause_data: Dict, 
                                    skywalking_data: Dict) -> Dict[str, Any]:
        """生成综合分析报告"""
        system_prompt = """你是一个资深的DevOps和微服务架构专家。请基于异常检测、根因分析和监控数据，生成一份完整的故障分析报告。

        报告要求：
        1. 执行摘要 - 简洁明了的问题概述
        2. 技术分析 - 详细的技术问题分析
        3. 影响评估 - 业务和技术影响分析
        4. 解决方案 - 具体的修复步骤
        5. 预防措施 - 避免类似问题的建议
        6. 监控建议 - 改进监控和告警的建议
        
        请以专业、清晰的方式撰写报告。"""
        
        # 构建综合提示词
        prompt = f"""请基于以下完整的微服务监控和分析数据生成综合故障分析报告：

=== 监控数据概览 ===
数据采集时间: {skywalking_data.get('timestamp', 'unknown')}
监控的服务数量: {len(skywalking_data.get('services', []))}

=== 异常检测结果 ===
检测时间: {anomalies_data.get('detection_timestamp', 'unknown')}
检测到的异常总数: {sum(len(anomalies) for anomalies in anomalies_data.get('anomalies', {}).values())}

高优先级异常数: {len(anomalies_data.get('anomalies', {}).get('high_priority', []))}
中优先级异常数: {len(anomalies_data.get('anomalies', {}).get('medium_priority', []))}

=== 根因分析结果 ===
分析时间: {root_cause_data.get('analysis_timestamp', 'unknown')}
识别的根因数量: {len(root_cause_data.get('root_causes', []))}

前3个根因服务:
"""
        
        root_causes = root_cause_data.get("root_causes", [])
        for i, root_cause in enumerate(root_causes[:3]):
            prompt += f"{i+1}. {root_cause.get('root_service', 'unknown')} (得分: {root_cause.get('root_cause_score', 0):.2f})\n"
        
        prompt += "\n=== 服务拓扑信息 ===\n"
        topology = skywalking_data.get('topology', {})
        prompt += f"服务节点数: {len(topology.get('nodes', []))}\n"
        prompt += f"服务调用关系数: {len(topology.get('calls', []))}\n"
        
        prompt += """

请生成一份专业的故障分析报告，包含执行摘要、技术分析、影响评估、解决方案、预防措施和监控建议。
报告应该适合向技术团队和管理层汇报。"""
        
        self.logger.info("正在生成综合分析报告...")
        response = self._send_request(prompt, system_prompt)
        
        return {
            "analysis_type": "comprehensive_report",
            "timestamp": datetime.now().isoformat(),
            "report_sections": [
                "executive_summary",
                "technical_analysis", 
                "impact_assessment",
                "solutions",
                "preventive_measures",
                "monitoring_recommendations"
            ],
            "ai_report": response,
            "success": response is not None
        }
    
    # def health_check(self) -> bool:
    #     """检查Ollama连接状态"""
    #     try:
    #         url = "https://api.deepseek.com/user/balance"
    #         response = requests.get(url, timeout=10, headers=self.headers)
            
    #         if response.status_code == 200:
    #             models = response.json().get("models", [])
    #             model_names = [model.get("name", "") for model in models]
                
    #             # 检查指定模型是否存在
    #             model_exists = any(self.model in name for name in model_names)
                
    #             if not model_exists:
    #                 self.logger.warning(f"指定模型 {self.model} 不存在，可用模型: {model_names}")
    #                 return False
                
    #             return True
    #         else:
    #             self.logger.error(f"Ollama健康检查失败: {response.status_code}")
    #             return False
                
    #     except Exception as e:
    #         self.logger.error(f"Ollama健康检查异常: {str(e)}")
    #         return False
