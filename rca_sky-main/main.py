"""
主程序入口
整合所有模块，执行完整的异常检测与根因分析流程
"""

import yaml
import logging
import sys
import os
from datetime import datetime
from typing import Dict, Any

# 导入自定义模块
from skywalking_collector import SkyWalkingCollector
from anomaly_detector import AnomalyDetector
from root_cause_analyzer import RootCauseAnalyzer
from ollama_analyzer import OllamaAnalyzer
from result_exporter import ResultExporter

is_ai_analysis = True

def setup_logging(log_level: str = "INFO") -> None:
    """设置日志配置"""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("sky_rca.log", encoding='utf-8')
        ]
    )


def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """加载配置文件"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config
    except FileNotFoundError:
        logging.error(f"配置文件 {config_path} 不存在")
        sys.exit(1)
    except yaml.YAMLError as e:
        logging.error(f"配置文件解析错误: {e}")
        sys.exit(1)


def check_dependencies(config: Dict[str, Any]) -> bool:
    """检查依赖服务的可用性"""
    logger = logging.getLogger(__name__)
    
    # 检查SkyWalking连接
    skywalking_config = config.get("skywalking", {})
    collector = SkyWalkingCollector(
        base_url=skywalking_config.get("base_url", "http://localhost:12800"),
        timeout=skywalking_config.get("timeout", 30)
    )
    
    if not collector.health_check():
        logger.error("SkyWalking连接失败，请检查服务是否正常运行")
        return False
    
    logger.info("SkyWalking连接正常")
    
    # 检查Ollama连接
    ollama_config = config.get("ollama", {})
    analyzer = OllamaAnalyzer(
        base_url=ollama_config.get("base_url", "http://localhost:11434"),
        model=ollama_config.get("model", "llama3.1"),
        timeout=ollama_config.get("timeout", 600)
    )
    
    # if not analyzer.health_check():
    #     logger.warning("Ollama连接失败，将跳过AI分析部分")
    #     return False
    
    logger.info("Ollama连接正常")
    return True


def main():
    """主函数"""
    print("🚀 启动微服务异常检测与根因分析系统...")
    
    # 加载配置
    config = load_config()
    
    # 设置日志
    setup_logging(config.get("output", {}).get("log_level", "INFO"))
    logger = logging.getLogger(__name__)
    
    logger.info("系统启动中...")
    
    # 检查依赖
    dependencies_ok = check_dependencies(config)
    
    try:
        # 初始化各个组件
        logger.info("初始化组件...")
        
        # SkyWalking数据采集器
        skywalking_config = config.get("skywalking", {})
        collector = SkyWalkingCollector(
            base_url=skywalking_config.get("base_url", "http://localhost:12800"),
            timeout=skywalking_config.get("timeout", 30)
        )
        
        # 异常检测器
        anomaly_config = config.get("anomaly_detection", {})
        anomaly_detector = AnomalyDetector(anomaly_config)
        
        # 根因分析器
        rca_config = config.get("root_cause_analysis", {})
        root_cause_analyzer = RootCauseAnalyzer(rca_config)
        
        # Ollama分析器（如果可用）
        ollama_analyzer = None
        if dependencies_ok:
            ollama_config = config.get("ollama", {})
            ollama_analyzer = OllamaAnalyzer(
                base_url=ollama_config.get("base_url", "http://localhost:11434"),
                model=ollama_config.get("model", "gemma3:12b-it-qat"),
                timeout=ollama_config.get("timeout", 600)
            )
        
        # 结果导出器
        output_config = config.get("output", {})
        result_exporter = ResultExporter(
            results_dir=output_config.get("results_dir", "./results")
        )
        
        # 第一步：数据采集
        logger.info("🔍 开始数据采集...")
        time_window = anomaly_config.get("time_window", 60)
        skywalking_data = collector.collect_all_data(time_window_minutes=time_window)
        
        # print("debug - ", skywalking_data)

        if not skywalking_data.get("services"):
            logger.warning("未采集到服务数据，请检查SkyWalking配置和数据")
            sys.exit(1)
        
        logger.info(f"✅ 数据采集完成，共采集 {len(skywalking_data['services'])} 个服务的数据")
        
        # 第二步：异常检测
        logger.info("🔍 开始异常检测...")
        anomalies_data = anomaly_detector.detect_anomalies(skywalking_data)
        
        total_anomalies = sum(len(anomalies) for anomalies in anomalies_data.get("anomalies", {}).values())
        logger.info(f"✅ 异常检测完成，发现 {total_anomalies} 个异常")

        if total_anomalies == 0:
            logger.info("系统未发现任何异常，分析结束。")
            print("\n✅ 系统运行正常，未发现任何异常。")
            sys.exit(0)

        # 第三步：根因分析
        logger.info("🎯 开始根因分析...")
        root_cause_data = root_cause_analyzer.analyze(skywalking_data, anomalies_data)
        
        root_causes_count = len(root_cause_data.get("root_causes", []))
        logger.info(f"✅ 根因分析完成，识别 {root_causes_count} 个潜在根因")
        
        if not is_ai_analysis:
            return

        # 第四步：AI智能分析（如果可用）
        ai_analysis = {}
        if ollama_analyzer:
            logger.info("🤖 开始AI智能分析...")
            
            try:
                # 异常分析
                anomaly_analysis = ollama_analyzer.analyze_anomalies(anomalies_data)
                ai_analysis["anomaly_analysis"] = anomaly_analysis
                
                # 根因分析
                root_cause_analysis = ollama_analyzer.analyze_root_causes(root_cause_data)
                ai_analysis["root_cause_analysis"] = root_cause_analysis
                
                # 综合报告
                comprehensive_report = ollama_analyzer.generate_comprehensive_report(
                    anomalies_data, root_cause_data, skywalking_data
                )
                ai_analysis["comprehensive_report"] = comprehensive_report
                
                logger.info("✅ AI智能分析完成")
                
            except Exception as e:
                logger.error(f"AI分析过程中发生错误: {str(e)}")
                ai_analysis = {"error": str(e)}
        else:
            logger.info("⏭️  跳过AI分析（Ollama不可用）")
        
        # 第五步：结果导出
        logger.info("📁 开始导出结果...")
        exported_files = result_exporter.export_all(
            skywalking_data, anomalies_data, root_cause_data, ai_analysis
        )
        
        logger.info("✅ 结果导出完成")
        
        # 输出摘要信息
        print("\n" + "=" * 60)
        print("📊 分析结果摘要")
        print("=" * 60)
        
        print(f"⏰ 分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔍 监控服务数: {len(skywalking_data.get('services', []))}")
        print(f"⚠ ️ 检测异常数: {total_anomalies}")
        
        # 按优先级分类异常
        anomalies = anomalies_data.get("anomalies", {})
        print(f"   - 高优先级: {len(anomalies.get('high_priority', []))}")
        print(f"   - 中优先级: {len(anomalies.get('medium_priority', []))}")
        print(f"   - 低优先级: {len(anomalies.get('low_priority', []))}")
        
        print(f"🎯 识别根因数: {root_causes_count}")
        
        if ai_analysis and "error" not in ai_analysis:
            ai_success_count = sum(1 for analysis in ai_analysis.values() 
                                 if isinstance(analysis, dict) and analysis.get("success"))
            print(f"🤖 AI分析项目: {ai_success_count}/{len(ai_analysis)}")
        
        print(f"📁 导出文件数: {len(exported_files)}")
        
        # 显示重要异常
        high_priority_anomalies = anomalies.get("high_priority", [])
        if high_priority_anomalies:
            print("\n🔴 高优先级异常:")
            for i, anomaly in enumerate(high_priority_anomalies[:3], 1):
                print(f"   {i}. {anomaly.get('service', 'unknown')}: {anomaly.get('type', 'unknown')}")
            if len(high_priority_anomalies) > 3:
                print(f"   ... 还有 {len(high_priority_anomalies) - 3} 个")
        
        # 显示主要根因
        root_causes = root_cause_data.get("root_causes", [])
        if root_causes:
            print("\n🎯 主要根因:")
            for i, root_cause in enumerate(root_causes[:3], 1):
                service = root_cause.get("root_service", "unknown")
                score = root_cause.get("root_cause_score", 0)
                print(f"   {i}. {service} (得分: {score:.2f})")
        
        print(f"\n📂 结果文件目录: {result_exporter.results_dir}")
        print("💡 查看 summary_report_*.txt 文件获取详细分析结果")
        
        print("\n✅ 分析完成！")
        
    except KeyboardInterrupt:
        logger.info("用户中断程序")
        print("\n❌ 程序被用户中断")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"程序执行过程中发生错误: {str(e)}", exc_info=True)
        print(f"\n❌ 程序执行失败: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    args = sys.argv
    if len(args) > 1 and args[1] == '--ai=false':
        is_ai_analysis = False
    main()
