#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时采集模块 - 收集系统资源数据、服务进程状态
"""

import psutil
import time
import json
import csv
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import os
from pathlib import Path


class MetricsCollector:
    """系统指标采集器"""
    
    def __init__(self, output_dir: str = "data", collect_interval: int = 30):
        """初始化指标采集器"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.collect_interval = collect_interval
        
        # 输出文件
        self.metrics_file = self.output_dir / "metrics.csv"
        self.process_file = self.output_dir / "processes.csv"
        self.services_file = self.output_dir / "services.json"
        
        # 关键服务列表
        self.key_services = [
            'mysqld', 'mysql', 'nginx', 'apache2', 'redis-server', 
            'postgresql', 'mongod', 'java', 'python'
        ]
        
        # 设置日志
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # 初始化CSV文件
        self._init_csv_files()
    
    def _init_csv_files(self):
        """初始化CSV文件头"""
        if not self.metrics_file.exists():
            with open(self.metrics_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'cpu_percent', 'memory_percent', 'memory_available',
                    'disk_usage_percent', 'network_connections', 'process_count'
                ])
        
        if not self.process_file.exists():
            with open(self.process_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'pid', 'name', 'cpu_percent', 'memory_percent',
                    'memory_rss', 'status', 'connections'
                ])
    
    def collect_system_metrics(self) -> Dict[str, Any]:
        """收集系统级别指标"""
        try:
            # 基础系统指标
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            net_connections = len(psutil.net_connections())
            process_count = len(psutil.pids())
            
            return {
                'timestamp': datetime.now().isoformat(),
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available': memory.available,
                'disk_usage_percent': disk.percent,
                'network_connections': net_connections,
                'process_count': process_count
            }
            
        except Exception as e:
            self.logger.error(f"采集系统指标失败: {e}")
            return {}
    
    def collect_process_metrics(self) -> List[Dict[str, Any]]:
        """收集关键进程指标"""
        process_metrics = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                proc_info = proc.info
                proc_name = proc_info['name'].lower()
                
                # 检查是否为关键服务
                if any(service in proc_name for service in self.key_services):
                    proc_obj = psutil.Process(proc_info['pid'])
                    
                    # 获取连接数（安全处理）
                    try:
                        connections = len(proc_obj.connections())
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        connections = 0
                    
                    # 获取内存信息
                    try:
                        memory_rss = proc_obj.memory_info().rss
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        memory_rss = 0
                    
                    process_metrics.append({
                        'timestamp': datetime.now().isoformat(),
                        'pid': proc_info['pid'],
                        'name': proc_info['name'],
                        'cpu_percent': proc_info['cpu_percent'] or 0,
                        'memory_percent': proc_info['memory_percent'] or 0,
                        'memory_rss': memory_rss,
                        'status': proc_obj.status(),
                        'connections': connections
                    })
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
            except Exception as e:
                self.logger.warning(f"采集进程指标失败: {e}")
        
        return process_metrics
    
    def collect_service_details(self) -> Dict[str, Any]:
        """收集服务详细信息"""
        services_info = {
            'timestamp': datetime.now().isoformat(),
            'services': {}
        }
        
        for service_pattern in self.key_services:
            service_processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    proc_info = proc.info
                    if service_pattern in proc_info['name'].lower():
                        proc_obj = psutil.Process(proc_info['pid'])
                        
                        service_processes.append({
                            'pid': proc_info['pid'],
                            'name': proc_info['name'],
                            'status': proc_obj.status(),
                            'cpu_percent': proc_obj.cpu_percent(),
                            'memory_percent': proc_obj.memory_percent(),
                            'create_time': proc_obj.create_time()
                        })
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if service_processes:
                services_info['services'][service_pattern] = service_processes
        
        return services_info
    
    def save_metrics(self, system_metrics: Dict, process_metrics: List[Dict]):
        """保存指标数据到文件"""
        try:
            # 保存系统指标
            if system_metrics:
                with open(self.metrics_file, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        system_metrics['timestamp'],
                        system_metrics['cpu_percent'],
                        system_metrics['memory_percent'],
                        system_metrics['memory_available'],
                        system_metrics['disk_usage_percent'],
                        system_metrics['network_connections'],
                        system_metrics['process_count']
                    ])
            
            # 保存进程指标
            if process_metrics:
                with open(self.process_file, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    for proc_metric in process_metrics:
                        writer.writerow([
                            proc_metric['timestamp'],
                            proc_metric['pid'],
                            proc_metric['name'],
                            proc_metric['cpu_percent'],
                            proc_metric['memory_percent'],
                            proc_metric['memory_rss'],
                            proc_metric['status'],
                            proc_metric['connections']
                        ])
            
            self.logger.info(f"保存指标: 系统 {'✓' if system_metrics else '✗'}, 进程 {len(process_metrics)}个")
            
        except Exception as e:
            self.logger.error(f"保存指标失败: {e}")
    
    def collect_once(self):
        """执行一次完整的数据采集"""
        self.logger.info("开始采集系统指标...")
        
        # 采集各类指标
        system_metrics = self.collect_system_metrics()
        process_metrics = self.collect_process_metrics()
        services_info = self.collect_service_details()
        
        # 保存数据
        self.save_metrics(system_metrics, process_metrics)
        
        # 保存服务详情
        try:
            with open(self.services_file, 'w', encoding='utf-8') as f:
                json.dump(services_info, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"保存服务详情失败: {e}")
        
        self.logger.info(f"采集完成: 发现 {len(process_metrics)} 个关键进程")
        
        return {
            'system_metrics': system_metrics,
            'process_metrics': process_metrics,
            'services_info': services_info
        }


def main():
    """主函数演示"""
    collector = MetricsCollector(output_dir="data")
    
    print("🔍 开始系统指标采集...")
    
    try:
        result = collector.collect_once()
        
        print(f"\n📊 采集结果:")
        sys_metrics = result['system_metrics']
        print(f"  - CPU使用率: {sys_metrics.get('cpu_percent', 0):.1f}%")
        print(f"  - 内存使用率: {sys_metrics.get('memory_percent', 0):.1f}%")
        print(f"  - 磁盘使用率: {sys_metrics.get('disk_usage_percent', 0):.1f}%")
        print(f"  - 网络连接数: {sys_metrics.get('network_connections', 0)}")
        print(f"  - 关键进程数: {len(result['process_metrics'])}")
        
        if result['process_metrics']:
            print(f"\n🔧 发现的关键服务:")
            for proc in result['process_metrics'][:5]:
                print(f"  - {proc['name']} (PID: {proc['pid']}): "
                      f"CPU {proc['cpu_percent']:.1f}%, MEM {proc['memory_percent']:.1f}%")
        
        print(f"\n💾 数据已保存到: {collector.output_dir}")
        
    except Exception as e:
        print(f"❌ 采集失败: {e}")


if __name__ == "__main__":
    main() 