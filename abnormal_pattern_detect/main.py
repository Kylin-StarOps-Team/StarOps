#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能运维助手 - 异常模式检测主程序
实现从数据采集 → 异常检测 → 模式提取 → 扫描器生成的完整流程
"""

import time
import json
import logging
import argparse
import schedule
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# 导入各个模块
from collect_metrics import MetricsCollector
from parse_logs import LogParser
from detect_anomaly import AnomalyDetector
from extract_pattern import PatternExtractor
from generate_scanner import ScannerGenerator


class AnomalyDetectionSystem:
    """异常模式检测系统主控制器"""
    
    def __init__(self, data_dir: str = "data", scanners_dir: str = "scanners"):
        """初始化系统"""
        self.data_dir = Path(data_dir)
        self.scanners_dir = Path(scanners_dir)
        
        # 创建目录
        self.data_dir.mkdir(exist_ok=True)
        self.scanners_dir.mkdir(exist_ok=True)
        
        # 初始化各个模块
        self.metrics_collector = MetricsCollector(output_dir=str(self.data_dir))
        self.log_parser = LogParser(output_dir=str(self.data_dir))
        self.anomaly_detector = AnomalyDetector(output_dir=str(self.data_dir))
        self.pattern_extractor = PatternExtractor(output_dir=str(self.data_dir))
        self.scanner_generator = ScannerGenerator(
            output_dir=str(self.data_dir), 
            scanners_dir=str(self.scanners_dir)
        )
        
        # 系统状态文件
        self.status_file = self.data_dir / "system_status.json"
        
        # 设置日志
        self._setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # 加载系统状态
        self.system_status = self._load_system_status()
    
    def _setup_logging(self):
        """设置日志配置"""
        log_file = self.data_dir / "anomaly_detection.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
    
    def _load_system_status(self) -> Dict[str, Any]:
        """加载系统状态"""
        if self.status_file.exists():
            try:
                with open(self.status_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"加载系统状态失败: {e}")
        
        # 默认状态
        return {
            'last_collection_time': None,
            'last_pattern_extraction_time': None,
            'last_scanner_generation_time': None,
            'total_patterns_extracted': 0,
            'total_scanners_generated': 0,
            'system_initialized': False
        }
    
    def _save_system_status(self):
        """保存系统状态"""
        try:
            with open(self.status_file, 'w', encoding='utf-8') as f:
                json.dump(self.system_status, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"保存系统状态失败: {e}")
    
    def collect_data(self) -> Dict[str, Any]:
        """步骤1: 收集指标和日志数据"""
        self.logger.info("=" * 50)
        self.logger.info("步骤1: 开始数据收集")
        self.logger.info("=" * 50)
        
        collection_results = {
            'success': False,  # 添加顶层success字段
            'metrics_collection': {'success': False, 'error': None},
            'log_parsing': {'success': False, 'error': None},
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # 收集系统和进程指标
            self.logger.info("收集系统指标...")
            metrics_result = self.metrics_collector.collect_once()
            collection_results['metrics_collection'] = {
                'success': True,
                'metrics_count': len(metrics_result.get('process_metrics', [])),
                'services_found': len(metrics_result.get('services_info', {}).get('services', {}))
            }
            self.logger.info(f"指标收集完成: 发现 {collection_results['metrics_collection']['metrics_count']} 个进程")
            
        except Exception as e:
            self.logger.error(f"指标收集失败: {e}")
            collection_results['metrics_collection']['error'] = str(e)
        
        try:
            # 解析日志
            self.logger.info("解析系统日志...")
            log_result = self.log_parser.parse_all_logs(time_window_hours=24)
            self.log_parser.save_parsed_logs(log_result)
            
            collection_results['log_parsing'] = {
                'success': True,
                'services_analyzed': len(log_result.get('services', {})),
                'total_errors': log_result.get('global_summary', {}).get('total_errors', 0)
            }
            self.logger.info(f"日志解析完成: 分析了 {collection_results['log_parsing']['services_analyzed']} 个服务")
            
        except Exception as e:
            self.logger.error(f"日志解析失败: {e}")
            collection_results['log_parsing']['error'] = str(e)
        
        # 判断整体成功状态
        collection_results['success'] = (
            collection_results['metrics_collection']['success'] and 
            collection_results['log_parsing']['success']
        )
        
        # 更新系统状态
        self.system_status['last_collection_time'] = collection_results['timestamp']
        self._save_system_status()
        
        return collection_results
    
    def detect_anomalies(self) -> Dict[str, Any]:
        """步骤2: 检测异常"""
        self.logger.info("=" * 50)
        self.logger.info("步骤2: 开始异常检测")
        self.logger.info("=" * 50)
        
        try:
            # 运行异常检测
            anomaly_results = self.anomaly_detector.run_anomaly_detection(hours_back=24)
            
            # 保存结果
            self.anomaly_detector.save_anomaly_results(anomaly_results)
            
            summary = anomaly_results.get('summary', {})
            self.logger.info(f"异常检测完成: 发现 {summary.get('total_anomalies', 0)} 个异常")
            self.logger.info(f"  - 系统异常: {summary.get('by_type', {}).get('system', 0)}")
            self.logger.info(f"  - 进程异常: {summary.get('by_type', {}).get('process', 0)}")
            self.logger.info(f"  - 日志异常: {summary.get('by_type', {}).get('log', 0)}")
            
            return {
                'success': True,
                'total_anomalies': summary.get('total_anomalies', 0),
                'by_type': summary.get('by_type', {}),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"异常检测失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def extract_patterns(self) -> Dict[str, Any]:
        """步骤3: 提取异常模式"""
        self.logger.info("=" * 50)
        self.logger.info("步骤3: 开始模式提取")
        self.logger.info("=" * 50)
        
        try:
            # 提取异常模式
            patterns = self.pattern_extractor.extract_all_patterns()
            
            # 保存模式
            self.pattern_extractor.save_patterns(patterns)
            
            summary = patterns.get('summary', {})
            total_patterns = summary.get('total_patterns', 0)
            
            self.logger.info(f"模式提取完成: 提取了 {total_patterns} 个模式")
            self.logger.info(f"  - 指标模式: {summary.get('metric_patterns_count', 0)}")
            self.logger.info(f"  - 日志模式: {summary.get('log_patterns_count', 0)}")
            self.logger.info(f"  - 复合模式: {summary.get('composite_patterns_count', 0)}")
            
            # 更新系统状态
            self.system_status['last_pattern_extraction_time'] = datetime.now().isoformat()
            self.system_status['total_patterns_extracted'] = total_patterns
            self._save_system_status()
            
            return {
                'success': True,
                'total_patterns': total_patterns,
                'pattern_types': {
                    'metric': summary.get('metric_patterns_count', 0),
                    'log': summary.get('log_patterns_count', 0),
                    'composite': summary.get('composite_patterns_count', 0)
                },
                'services_analyzed': summary.get('services_analyzed', []),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"模式提取失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def generate_scanners(self) -> Dict[str, Any]:
        """步骤4: 生成扫描器"""
        self.logger.info("=" * 50)
        self.logger.info("步骤4: 开始生成扫描器")
        self.logger.info("=" * 50)
        
        try:
            # 生成扫描器代码
            scanners = self.scanner_generator.generate_all_scanners()
            
            if not scanners:
                self.logger.warning("没有生成任何扫描器，可能缺少足够的模式数据")
                return {
                    'success': False,
                    'error': '没有可用的模式数据生成扫描器',
                    'timestamp': datetime.now().isoformat()
                }
            
            # 保存扫描器文件
            self.scanner_generator.save_scanners(scanners)
            
            scanner_count = len(scanners)
            self.logger.info(f"扫描器生成完成: 生成了 {scanner_count} 个扫描器")
            
            for filename in scanners.keys():
                service_name = filename.replace('scan_', '').replace('.py', '')
                self.logger.info(f"  - {service_name}: {filename}")
            
            # 更新系统状态
            self.system_status['last_scanner_generation_time'] = datetime.now().isoformat()
            self.system_status['total_scanners_generated'] = scanner_count
            self._save_system_status()
            
            return {
                'success': True,
                'scanner_count': scanner_count,
                'scanner_files': list(scanners.keys()),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"扫描器生成失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def run_complete_pipeline(self) -> Dict[str, Any]:
        """运行完整的检测流程"""
        pipeline_start_time = datetime.now()
        
        self.logger.info("🚀 开始运行异常模式检测完整流程...")
        
        pipeline_results = {
            'start_time': pipeline_start_time.isoformat(),
            'steps': {}
        }
        
        # 步骤1: 数据收集
        step1_result = self.collect_data()
        pipeline_results['steps']['data_collection'] = step1_result
        
        # 步骤2: 异常检测
        step2_result = self.detect_anomalies()
        pipeline_results['steps']['anomaly_detection'] = step2_result
        
        # 只有在检测到异常时才继续
        if step2_result.get('success') and step2_result.get('total_anomalies', 0) > 0:
            # 步骤3: 模式提取
            step3_result = self.extract_patterns()
            pipeline_results['steps']['pattern_extraction'] = step3_result
            
            # 只有在提取到模式时才生成扫描器
            if step3_result.get('success') and step3_result.get('total_patterns', 0) > 0:
                # 步骤4: 生成扫描器
                step4_result = self.generate_scanners()
                pipeline_results['steps']['scanner_generation'] = step4_result
            else:
                self.logger.info("跳过扫描器生成: 没有提取到足够的模式")
        else:
            self.logger.info("跳过模式提取和扫描器生成: 没有检测到异常")
        
        # 计算总耗时
        pipeline_end_time = datetime.now()
        pipeline_results.update({
            'end_time': pipeline_end_time.isoformat(),
            'duration_seconds': (pipeline_end_time - pipeline_start_time).total_seconds(),
            'overall_success': all(
                step.get('success', False) 
                for step in pipeline_results['steps'].values()
            )
        })
        
        # 标记系统已初始化
        self.system_status['system_initialized'] = True
        self._save_system_status()
        
        self.logger.info(f"🎉 流程完成，总耗时: {pipeline_results['duration_seconds']:.2f}秒")
        
        return pipeline_results
    
    def run_scheduled_collection(self):
        """定期数据收集（用于持续监控）"""
        self.logger.info("⏰ 执行定期数据收集...")
        
        try:
            # 只收集数据，不做全流程处理
            self.collect_data()
            self.logger.info("✅ 定期数据收集完成")
        except Exception as e:
            self.logger.error(f"❌ 定期数据收集失败: {e}")
    
    def start_monitoring(self, collection_interval_minutes: int = 30):
        """启动持续监控模式"""
        self.logger.info(f"📡 启动持续监控模式，采集间隔: {collection_interval_minutes}分钟")
        
        # 安排定期任务
        schedule.every(collection_interval_minutes).minutes.do(self.run_scheduled_collection)
        
        # 每天重新分析一次模式
        schedule.every().day.at("02:00").do(self.run_complete_pipeline)
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次
                
        except KeyboardInterrupt:
            self.logger.info("⏹️ 停止监控模式")
    
    def show_system_status(self):
        """显示系统状态"""
        print("\n" + "=" * 60)
        print("🔍 智能运维助手 - 异常模式检测系统状态")
        print("=" * 60)
        
        print(f"📁 数据目录: {self.data_dir}")
        print(f"🔧 扫描器目录: {self.scanners_dir}")
        print(f"🟢 系统已初始化: {'是' if self.system_status.get('system_initialized') else '否'}")
        
        last_collection = self.system_status.get('last_collection_time')
        if last_collection:
            print(f"📊 最后数据收集: {last_collection}")
        
        last_pattern_extraction = self.system_status.get('last_pattern_extraction_time')
        if last_pattern_extraction:
            print(f"🔍 最后模式提取: {last_pattern_extraction}")
            print(f"📋 已提取模式数: {self.system_status.get('total_patterns_extracted', 0)}")
        
        last_scanner_generation = self.system_status.get('last_scanner_generation_time')
        if last_scanner_generation:
            print(f"🔧 最后扫描器生成: {last_scanner_generation}")
            print(f"🛠️ 已生成扫描器数: {self.system_status.get('total_scanners_generated', 0)}")
        
        # 检查文件存在情况
        print(f"\n📂 数据文件状态:")
        files_to_check = [
            ('metrics.csv', '系统指标'),
            ('processes.csv', '进程指标'),
            ('parsed_logs.json', '解析日志'),
            ('anomaly_summary.json', '异常检测结果'),
            ('extracted_patterns.json', '提取的模式')
        ]
        
        for filename, description in files_to_check:
            file_path = self.data_dir / filename
            status = "✅ 存在" if file_path.exists() else "❌ 不存在"
            print(f"  {description}: {status}")
        
        # 检查扫描器
        if self.scanners_dir.exists():
            scanner_files = list(self.scanners_dir.glob("scan_*.py"))
            print(f"\n🔧 可用扫描器 ({len(scanner_files)}个):")
            for scanner_file in scanner_files:
                service_name = scanner_file.stem.replace('scan_', '')
                print(f"  - {service_name}: {scanner_file.name}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='智能运维助手 - 异常模式检测系统')
    
    parser.add_argument('command', choices=[
        'run', 'monitor', 'collect', 'detect', 'extract', 'generate', 'status'
    ], help='要执行的命令')
    
    parser.add_argument('--data-dir', default='data', help='数据目录路径')
    parser.add_argument('--scanners-dir', default='/home/denerate/abnormal_pattern_detect/scanners', help='扫描器目录路径')
    parser.add_argument('--interval', type=int, default=30, help='监控模式下的数据收集间隔(分钟)')
    
    args = parser.parse_args()
    
    # 初始化系统
    system = AnomalyDetectionSystem(
        data_dir=args.data_dir,
        scanners_dir=args.scanners_dir
    )
    
    if args.command == 'run':
        # 运行完整流程
        print("🚀 开始运行异常模式检测完整流程...")
        results = system.run_complete_pipeline()
        
        print(f"\n📊 流程执行结果:")
        print(f"  - 总耗时: {results.get('duration_seconds', 0):.2f}秒")
        print(f"  - 整体成功: {'✅ 是' if results.get('overall_success') else '❌ 否'}")
        
        for step_name, step_result in results.get('steps', {}).items():
            success = "✅" if step_result.get('success') else "❌"
            print(f"  - {step_name}: {success}")
    
    elif args.command == 'monitor':
        # 启动持续监控
        system.start_monitoring(collection_interval_minutes=args.interval)
    
    elif args.command == 'collect':
        # 只执行数据收集
        print("📊 开始数据收集...")
        results = system.collect_data()
        print("✅ 数据收集完成")
    
    elif args.command == 'detect':
        # 只执行异常检测
        print("🔍 开始异常检测...")
        results = system.detect_anomalies()
        if results.get('success'):
            print(f"✅ 异常检测完成，发现 {results.get('total_anomalies', 0)} 个异常")
        else:
            print(f"❌ 异常检测失败: {results.get('error')}")
    
    elif args.command == 'extract':
        # 只执行模式提取
        print("📋 开始模式提取...")
        results = system.extract_patterns()
        if results.get('success'):
            print(f"✅ 模式提取完成，提取了 {results.get('total_patterns', 0)} 个模式")
        else:
            print(f"❌ 模式提取失败: {results.get('error')}")
    
    elif args.command == 'generate':
        # 只执行扫描器生成
        print("🔧 开始生成扫描器...")
        results = system.generate_scanners()
        if results.get('success'):
            print(f"✅ 扫描器生成完成，生成了 {results.get('scanner_count', 0)} 个扫描器")
        else:
            print(f"❌ 扫描器生成失败: {results.get('error')}")
    
    elif args.command == 'status':
        # 显示系统状态
        system.show_system_status()


if __name__ == "__main__":
    main() 