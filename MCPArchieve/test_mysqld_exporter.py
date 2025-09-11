#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MysqldExporterProtocol数据库状态检测测试脚本
用于测试数据库监控功能的完整性和准确性
"""

import sys
import os
import json
from datetime import datetime

# 添加核心模块路径
current_dir = os.path.dirname(os.path.abspath(__file__))
core_dir = os.path.join(current_dir, 'core')
sys.path.insert(0, core_dir)

try:
    from mcp_protocols import MysqldExporterProtocol
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print(f"当前目录: {current_dir}")
    print(f"核心目录: {core_dir}")
    sys.exit(1)

class MysqldExporterTester:
    """MysqldExporterProtocol测试器"""
    
    def __init__(self):
        self.test_results = []
        self.start_time = datetime.now()
        
    def print_header(self, title):
        """打印测试标题"""
        print("\n" + "="*60)
        print(f"🧪 {title}")
        print("="*60)
        
    def print_subheader(self, title):
        """打印子标题"""
        print(f"\n📋 {title}")
        print("-" * 40)
        
    def save_test_result(self, test_name, result, description=""):
        """保存测试结果"""
        test_record = {
            "test_name": test_name,
            "timestamp": datetime.now().isoformat(),
            "result": result,
            "description": description,
            "status": result.get("status", "unknown")
        }
        self.test_results.append(test_record)
        
    def test_basic_functionality(self):
        """测试基本功能"""
        self.print_header("MysqldExporterProtocol 基本功能测试")
        
        # 测试1: 默认参数调用
        self.print_subheader("测试1: 默认参数调用")
        try:
            result = MysqldExporterProtocol.execute()
            self.save_test_result("default_call", result, "默认参数调用测试")
            
            print(f"✅ 调用状态: {result.get('status', 'unknown')}")
            print(f"📊 指标类型: {result.get('metric_type', 'N/A')}")
            print(f"⏰ 时间戳: {result.get('timestamp', 'N/A')}")
            
            if result.get('status') == 'success':
                summary = result.get('summary', {})
                print(f"📈 摘要数据项数: {len(summary)}")
                print(f"🔍 异常分析: {'存在' if result.get('anomaly_analysis') else '无'}")
                print(f"📋 原始数据: {'存在' if result.get('raw_data') else '无'}")
                
                # 输出关键指标
                if summary:
                    print("\n🔢 关键指标预览:")
                    for key, value in list(summary.items())[:5]:  # 只显示前5个
                        print(f"  • {key}: {value}")
                        
            else:
                print(f"❌ 错误信息: {result.get('message', 'N/A')}")
                
        except Exception as e:
            error_result = {"status": "error", "message": str(e)}
            self.save_test_result("default_call", error_result, f"默认调用异常: {str(e)}")
            print(f"❌ 测试异常: {e}")
            
    def test_different_metric_types(self):
        """测试不同指标类型"""
        self.print_header("不同指标类型测试")
        
        metric_types = [
            ("overview", "概览指标"),
            ("connections", "连接指标"), 
            ("queries", "查询指标"),
            ("performance", "性能指标"),
            ("replication", "复制指标")
        ]
        
        for metric_type, description in metric_types:
            self.print_subheader(f"测试: {description} ({metric_type})")
            try:
                params = {"metric_type": metric_type}
                result = MysqldExporterProtocol.execute(params)
                self.save_test_result(f"metric_type_{metric_type}", result, f"{description}测试")
                
                print(f"✅ 状态: {result.get('status', 'unknown')}")
                print(f"📊 指标类型: {result.get('metric_type', 'N/A')}")
                
                if result.get('status') == 'success':
                    summary = result.get('summary', {})
                    anomaly = result.get('anomaly_analysis', {})
                    
                    print(f"📈 摘要项数: {len(summary)}")
                    print(f"🚨 异常评分: {anomaly.get('anomaly_score', 'N/A')}")
                    print(f"⚠️  异常等级: {anomaly.get('risk_level', 'N/A')}")
                    
                    # 输出具体数据用于测试报告
                    if summary:
                        print(f"\n📋 {description}详细数据:")
                        for key, value in summary.items():
                            print(f"  • {key}: {value}")
                            
                    if anomaly.get('anomalies'):
                        print(f"\n🔍 检测到的异常:")
                        for anomaly_item in anomaly['anomalies'][:3]:  # 只显示前3个
                            print(f"  ⚠️  {anomaly_item}")
                            
                else:
                    print(f"❌ 错误: {result.get('message', 'N/A')}")
                    
            except Exception as e:
                error_result = {"status": "error", "message": str(e)}
                self.save_test_result(f"metric_type_{metric_type}", error_result, f"{description}测试异常: {str(e)}")
                print(f"❌ 测试异常: {e}")
                
    def test_error_handling(self):
        """测试错误处理"""
        self.print_header("错误处理能力测试")
        
        # 测试1: 无效参数
        self.print_subheader("测试: 无效参数处理")
        try:
            params = {"metric_type": "invalid_type", "invalid_param": "test"}
            result = MysqldExporterProtocol.execute(params)
            self.save_test_result("invalid_params", result, "无效参数测试")
            
            print(f"✅ 状态: {result.get('status', 'unknown')}")
            print(f"📝 消息: {result.get('message', 'N/A')}")
            
        except Exception as e:
            error_result = {"status": "error", "message": str(e)}
            self.save_test_result("invalid_params", error_result, f"无效参数测试异常: {str(e)}")
            print(f"❌ 测试异常: {e}")
            
    def test_performance_metrics(self):
        """测试性能指标输出"""
        self.print_header("性能指标详细测试")
        
        try:
            # 获取性能相关指标
            result = MysqldExporterProtocol.execute({"metric_type": "performance"})
            self.save_test_result("performance_detailed", result, "性能指标详细测试")
            
            if result.get('status') == 'success':
                raw_data = result.get('raw_data', {})
                summary = result.get('summary', {})
                anomaly = result.get('anomaly_analysis', {})
                
                print("📊 性能指标测试数据输出 (用于测试报告填写):")
                print("="*50)
                
                # 1. 连接相关指标
                print("\n🔗 数据库连接指标:")
                connection_metrics = [
                    'mysql_global_status_threads_connected',
                    'mysql_global_status_max_used_connections',
                    'mysql_global_status_threads_running'
                ]
                
                for metric in connection_metrics:
                    if metric in raw_data:
                        values = raw_data[metric]
                        if values:
                            print(f"  • {metric}: {values[0].get('value', 'N/A')}")
                
                # 2. 查询性能指标
                print("\n🔍 查询性能指标:")
                query_metrics = [
                    'mysql_global_status_queries',
                    'mysql_global_status_slow_queries', 
                    'mysql_global_status_select_scan'
                ]
                
                for metric in query_metrics:
                    if metric in raw_data:
                        values = raw_data[metric]
                        if values:
                            print(f"  • {metric}: {values[0].get('value', 'N/A')}")
                
                # 3. 缓存指标
                print("\n💾 缓存相关指标:")
                cache_metrics = [
                    'mysql_global_status_qcache_hits',
                    'mysql_global_status_qcache_inserts',
                    'mysql_global_status_key_buffer_fraction'
                ]
                
                for metric in cache_metrics:
                    if metric in raw_data:
                        values = raw_data[metric]
                        if values:
                            print(f"  • {metric}: {values[0].get('value', 'N/A')}")
                
                # 4. 异常分析结果
                print(f"\n🚨 异常检测结果:")
                print(f"  • 异常评分: {anomaly.get('anomaly_score', 'N/A')}/10")
                print(f"  • 风险等级: {anomaly.get('risk_level', 'N/A')}")
                print(f"  • 异常数量: {len(anomaly.get('anomalies', []))}")
                
                if anomaly.get('anomalies'):
                    print("  • 具体异常:")
                    for i, anomaly_detail in enumerate(anomaly['anomalies'][:5], 1):
                        print(f"    {i}. {anomaly_detail}")
                
                # 5. 汇总信息用于报告
                print(f"\n📋 测试数据汇总 (可直接用于测试报告):")
                print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"协议状态: {result.get('status', 'unknown')}")
                print(f"数据项数量: {len(raw_data)}")
                print(f"异常评分: {anomaly.get('anomaly_score', 'N/A')}")
                print(f"风险等级: {anomaly.get('risk_level', 'N/A')}")
                
            else:
                print(f"❌ 性能测试失败: {result.get('message', 'N/A')}")
                
        except Exception as e:
            error_result = {"status": "error", "message": str(e)}
            self.save_test_result("performance_detailed", error_result, f"性能测试异常: {str(e)}")
            print(f"❌ 性能测试异常: {e}")
            
    def generate_test_report(self):
        """生成测试报告"""
        self.print_header("测试报告生成")
        
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        # 统计测试结果
        total_tests = len(self.test_results)
        success_tests = len([r for r in self.test_results if r['status'] == 'success'])
        failed_tests = len([r for r in self.test_results if r['status'] == 'error'])
        
        print(f"📊 测试统计:")
        print(f"  • 总测试数: {total_tests}")
        print(f"  • 成功测试: {success_tests}")
        print(f"  • 失败测试: {failed_tests}")
        print(f"  • 成功率: {(success_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%")
        print(f"  • 测试耗时: {duration.total_seconds():.2f}秒")
        
        # 保存详细测试结果到文件
        report_data = {
            "test_summary": {
                "total_tests": total_tests,
                "success_tests": success_tests,
                "failed_tests": failed_tests,
                "success_rate": (success_tests/total_tests*100) if total_tests > 0 else 0,
                "duration_seconds": duration.total_seconds(),
                "start_time": self.start_time.isoformat(),
                "end_time": end_time.isoformat()
            },
            "test_details": self.test_results
        }
        
        report_file = f"mysqld_exporter_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
            print(f"\n💾 详细测试报告已保存: {report_file}")
        except Exception as e:
            print(f"❌ 保存测试报告失败: {e}")
        
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始 MysqldExporterProtocol 测试")
        print(f"⏰ 测试开始时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 执行各项测试
        self.test_basic_functionality()
        self.test_different_metric_types()
        self.test_error_handling()
        self.test_performance_metrics()
        
        # 生成测试报告
        self.generate_test_report()
        
        print("\n🏁 MysqldExporterProtocol 测试完成!")

def main():
    """主函数"""
    tester = MysqldExporterTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
