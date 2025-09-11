"""
结果输出模块
负责将分析结果输出到文件中
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, Any
import pandas as pd


class ResultExporter:
    """结果导出器"""
    
    def __init__(self, results_dir: str = "./results"):
        self.results_dir = results_dir
        self.logger = logging.getLogger(__name__)
        
        # 确保输出目录存在
        os.makedirs(results_dir, exist_ok=True)
        
    def _generate_filename(self, prefix: str, extension: str = "json") -> str:
        """生成带时间戳的文件名"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_{timestamp}.{extension}"
    
    def export_anomalies(self, anomalies_data: Dict, filename: str = None) -> str:
        """导出异常检测结果"""
        if filename is None:
            filename = self._generate_filename("anomalies")
        
        filepath = os.path.join(self.results_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(anomalies_data, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"异常检测结果已导出到: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"导出异常检测结果失败: {str(e)}")
            raise
    
    def export_root_causes(self, root_cause_data: Dict, filename: str = None) -> str:
        """导出根因分析结果"""
        if filename is None:
            filename = self._generate_filename("root_causes")
        
        filepath = os.path.join(self.results_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(root_cause_data, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"根因分析结果已导出到: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"导出根因分析结果失败: {str(e)}")
            raise
    
    def export_ai_analysis(self, ai_analysis_data: Dict, filename: str = None) -> str:
        """导出AI分析结果"""
        if filename is None:
            filename = self._generate_filename("ai_analysis")
        
        filepath = os.path.join(self.results_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(ai_analysis_data, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"AI分析结果已导出到: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"导出AI分析结果失败: {str(e)}")
            raise
    
    def export_comprehensive_report(self, all_data: Dict, filename: str = None) -> str:
        """导出综合报告"""
        if filename is None:
            filename = self._generate_filename("comprehensive_report")
        
        filepath = os.path.join(self.results_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"综合报告已导出到: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"导出综合报告失败: {str(e)}")
            raise
    
    def export_summary_report(self, all_data: Dict, filename: str = None) -> str:
        """导出摘要报告（人类可读格式）"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"summary_report_{timestamp}.txt"
        
        filepath = os.path.join(self.results_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                self._write_summary_report(f, all_data)
            
            self.logger.info(f"摘要报告已导出到: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"导出摘要报告失败: {str(e)}")
            raise
    
    def _write_summary_report(self, file, all_data: Dict):
        """写入摘要报告内容"""
        file.write("=" * 80 + "\n")
        file.write("微服务异常检测与根因分析报告\n")
        file.write("=" * 80 + "\n\n")
        
        # 基本信息
        file.write("🕐 报告生成时间: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
        
        skywalking_data = all_data.get("skywalking_data", {})
        if skywalking_data:
            file.write(f"📊 数据采集时间: {skywalking_data.get('timestamp', 'N/A')}\n")
            file.write(f"🔍 监控服务数量: {len(skywalking_data.get('services', []))}\n")
        
        file.write("\n" + "=" * 50 + "\n")
        file.write("异常检测结果\n")
        file.write("=" * 50 + "\n\n")
        
        # 异常检测结果
        anomalies_data = all_data.get("anomalies_data", {})
        if anomalies_data:
            anomalies = anomalies_data.get("anomalies", {})
            high_priority = anomalies.get("high_priority", [])
            medium_priority = anomalies.get("medium_priority", [])
            low_priority = anomalies.get("low_priority", [])
            
            total_anomalies = len(high_priority) + len(medium_priority) + len(low_priority)
            
            file.write(f"📈 检测到异常总数: {total_anomalies}\n")
            file.write(f"🔴 高优先级异常: {len(high_priority)}\n")
            file.write(f"🟡 中优先级异常: {len(medium_priority)}\n")
            file.write(f"🟢 低优先级异常: {len(low_priority)}\n\n")
            
            # 高优先级异常详情
            if high_priority:
                file.write("🔴 高优先级异常详情:\n")
                file.write("-" * 40 + "\n")
                for i, anomaly in enumerate(high_priority, 1):
                    file.write(f"{i}. 服务: {anomaly.get('service', 'unknown')}\n")
                    file.write(f"   类型: {anomaly.get('type', 'unknown')}\n")
                    file.write(f"   描述: {anomaly.get('description', 'unknown')}\n")
                    if 'value' in anomaly:
                        file.write(f"   数值: {anomaly['value']}\n")
                    file.write("\n")
            
            # 中优先级异常详情
            if medium_priority:
                file.write("🟡 中优先级异常详情:\n")
                file.write("-" * 40 + "\n")
                for i, anomaly in enumerate(medium_priority[:5], 1):  # 限制显示数量
                    file.write(f"{i}. 服务: {anomaly.get('service', 'unknown')}\n")
                    file.write(f"   类型: {anomaly.get('type', 'unknown')}\n")
                    file.write(f"   描述: {anomaly.get('description', 'unknown')}\n\n")
                
                if len(medium_priority) > 5:
                    file.write(f"   ... 还有 {len(medium_priority) - 5} 个中优先级异常\n\n")
        
        file.write("\n" + "=" * 50 + "\n")
        file.write("根因分析结果\n")
        file.write("=" * 50 + "\n\n")
        
        # 根因分析结果
        root_cause_data = all_data.get("root_cause_data", {})
        if root_cause_data:
            root_causes = root_cause_data.get("root_causes", [])
            
            file.write(f"🎯 识别根因数量: {len(root_causes)}\n\n")
            
            if root_causes:
                file.write("🎯 根因分析详情:\n")
                file.write("-" * 40 + "\n")
                
                for i, root_cause in enumerate(root_causes[:3], 1):  # 显示前3个根因
                    file.write(f"{i}. 根因服务: {root_cause.get('root_service', 'unknown')}\n")
                    file.write(f"   根因得分: {root_cause.get('root_cause_score', 0):.2f}\n")
                    file.write(f"   置信度: {root_cause.get('confidence', 0):.2f}\n")
                    
                    anomalies = root_cause.get('anomalies', [])
                    if anomalies:
                        file.write(f"   相关异常数: {len(anomalies)}\n")
                        anomaly_types = list(set(anomaly.get('type', '') for anomaly in anomalies))
                        file.write(f"   异常类型: {', '.join(anomaly_types[:3])}\n")
                    
                    impact = root_cause.get('impact_analysis', {})
                    affected_services = impact.get('affected_services', [])
                    if affected_services:
                        file.write(f"   影响服务数: {len(affected_services)}\n")
                        file.write(f"   影响严重程度: {impact.get('impact_severity', 'unknown')}\n")
                    
                    recommendation = root_cause.get('recommendation', '')
                    if recommendation:
                        file.write(f"   建议措施: {recommendation}\n")
                    
                    file.write("\n")
                
                if len(root_causes) > 3:
                    file.write(f"   ... 还有 {len(root_causes) - 3} 个根因\n\n")
        
        file.write("\n" + "=" * 50 + "\n")
        file.write("AI智能分析\n")
        file.write("=" * 50 + "\n\n")
        
        # AI分析结果
        ai_analysis = all_data.get("ai_analysis", {})
        if ai_analysis:
            # 异常分析
            anomaly_analysis = ai_analysis.get("anomaly_analysis", {})
            if anomaly_analysis and anomaly_analysis.get("success"):
                file.write("🤖 异常智能分析:\n")
                file.write("-" * 40 + "\n")
                ai_response = anomaly_analysis.get("ai_analysis", "")
                if ai_response:
                    file.write(ai_response + "\n\n")
            
            # 根因分析
            root_cause_analysis = ai_analysis.get("root_cause_analysis", {})
            if root_cause_analysis and root_cause_analysis.get("success"):
                file.write("🤖 根因智能分析:\n")
                file.write("-" * 40 + "\n")
                ai_response = root_cause_analysis.get("ai_analysis", "")
                if ai_response:
                    file.write(ai_response + "\n\n")
            
            # 综合报告
            comprehensive_report = ai_analysis.get("comprehensive_report", {})
            if comprehensive_report and comprehensive_report.get("success"):
                file.write("🤖 综合智能报告:\n")
                file.write("-" * 40 + "\n")
                ai_report = comprehensive_report.get("ai_report", "")
                if ai_report:
                    file.write(ai_report + "\n\n")
        
        file.write("\n" + "=" * 50 + "\n")
        file.write("技术统计信息\n")
        file.write("=" * 50 + "\n\n")
        
        # 技术统计
        if skywalking_data:
            topology = skywalking_data.get('topology', {})
            file.write(f"🔗 服务拓扑节点数: {len(topology.get('nodes', []))}\n")
            file.write(f"🔗 服务调用关系数: {len(topology.get('calls', []))}\n")
        
        if root_cause_data:
            graph_stats = root_cause_data.get('service_graph_stats', {})
            file.write(f"📊 分析图节点数: {graph_stats.get('nodes', 0)}\n")
            file.write(f"📊 分析图边数: {graph_stats.get('edges', 0)}\n")
        
        file.write("\n" + "=" * 80 + "\n")
        file.write("报告结束\n")
        file.write("=" * 80 + "\n")
    
    def export_csv_summary(self, all_data: Dict, filename: str = None) -> str:
        """导出CSV格式的摘要数据"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"anomalies_summary_{timestamp}.csv"
        
        filepath = os.path.join(self.results_dir, filename)
        
        try:
            # 提取异常数据
            anomalies_data = all_data.get("anomalies_data", {})
            all_anomalies = []
            
            for priority, anomalies in anomalies_data.get("anomalies", {}).items():
                for anomaly in anomalies:
                    anomaly_record = {
                        "priority": priority,
                        "service": anomaly.get("service", ""),
                        "type": anomaly.get("type", ""),
                        "severity": anomaly.get("severity", ""),
                        "description": anomaly.get("description", ""),
                        "value": anomaly.get("value", ""),
                        "threshold": anomaly.get("threshold", ""),
                        "detection_timestamp": anomalies_data.get("detection_timestamp", "")
                    }
                    all_anomalies.append(anomaly_record)
            
            if all_anomalies:
                df = pd.DataFrame(all_anomalies)
                df.to_csv(filepath, index=False, encoding='utf-8-sig')
                self.logger.info(f"CSV摘要已导出到: {filepath}")
            else:
                self.logger.warning("没有异常数据可导出为CSV")
            
            return filepath
            
        except Exception as e:
            self.logger.error(f"导出CSV摘要失败: {str(e)}")
            raise
    
    def export_all(self, skywalking_data: Dict, anomalies_data: Dict, 
                   root_cause_data: Dict, ai_analysis: Dict) -> Dict[str, str]:
        """导出所有结果"""
        exported_files = {}
        
        # 合并所有数据
        all_data = {
            "skywalking_data": skywalking_data,
            "anomalies_data": anomalies_data,
            "root_cause_data": root_cause_data,
            "ai_analysis": ai_analysis,
            "export_timestamp": datetime.now().isoformat()
        }
        
        try:
            # 导出各个组件的结果
            exported_files["anomalies"] = self.export_anomalies(anomalies_data)
            exported_files["root_causes"] = self.export_root_causes(root_cause_data)
            exported_files["ai_analysis"] = self.export_ai_analysis(ai_analysis)
            exported_files["comprehensive_report"] = self.export_comprehensive_report(all_data)
            exported_files["summary_report"] = self.export_summary_report(all_data)
            exported_files["csv_summary"] = self.export_csv_summary(all_data)
            
            # 创建索引文件
            index_filename = self._generate_filename("index", "txt")
            index_filepath = os.path.join(self.results_dir, index_filename)
            
            with open(index_filepath, 'w', encoding='utf-8') as f:
                f.write("微服务异常检测与根因分析 - 文件索引\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                for file_type, filepath in exported_files.items():
                    filename = os.path.basename(filepath)
                    f.write(f"{file_type}: {filename}\n")
            
            exported_files["index"] = index_filepath
            
            self.logger.info(f"所有结果已导出，共 {len(exported_files)} 个文件")
            return exported_files
            
        except Exception as e:
            self.logger.error(f"导出所有结果时发生错误: {str(e)}")
            raise
