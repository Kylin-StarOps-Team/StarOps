#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web应用配置优化检测定时调度器
支持定期检测和自动报告生成
"""

import os
import sys
import time
import schedule
import logging
import subprocess
from datetime import datetime
from typing import Dict, Any

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import WebConfigDetectionSystem

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class WebConfigScheduler:
    """Web应用配置优化检测调度器"""
    
    def __init__(self):
        self.target_url = os.getenv('TARGET_URL', 'http://localhost:8080')
        self.detection_system = WebConfigDetectionSystem(self.target_url)
        self.schedule_daily = os.getenv('SCHEDULE_DAILY', 'true').lower() == 'true'
        self.schedule_time = os.getenv('SCHEDULE_TIME', '01:00')
        self.schedule_weekly = os.getenv('SCHEDULE_WEEKLY', 'false').lower() == 'true'
        self.schedule_weekly_day = os.getenv('SCHEDULE_WEEKLY_DAY', 'sunday')
        self.retention_days = int(os.getenv('RETENTION_DAYS', '30'))
        
    def run_daily_detection(self):
        """运行每日检测"""
        logger.info("开始执行每日检测任务...")
        
        try:
            result = self.detection_system.run_full_detection()
            
            if result['status'] == 'success':
                logger.info("每日检测完成")
                self._cleanup_old_reports()
                self._send_notification(result)
            else:
                logger.error(f"每日检测失败: {result.get('error', '未知错误')}")
                
        except Exception as e:
            logger.error(f"每日检测执行异常: {e}")
    
    def run_weekly_detection(self):
        """运行每周检测"""
        logger.info("开始执行每周深度检测任务...")
        
        try:
            # 运行完整检测
            result = self.detection_system.run_full_detection()
            
            if result['status'] == 'success':
                logger.info("每周检测完成")
                
                # 生成周报摘要
                self._generate_weekly_summary(result)
                self._cleanup_old_reports()
                self._send_notification(result, is_weekly=True)
            else:
                logger.error(f"每周检测失败: {result.get('error', '未知错误')}")
                
        except Exception as e:
            logger.error(f"每周检测执行异常: {e}")
    
    def run_security_check(self):
        """运行安全专项检查"""
        logger.info("开始执行安全专项检查...")
        
        try:
            result = self.detection_system.run_security_check()
            
            if result['status'] == 'success':
                logger.info("安全专项检查完成")
                
                # 如果安全评分低于阈值，发送告警
                security_score = result.get('security_score', 100)
                if security_score < 70:
                    self._send_security_alert(result)
            else:
                logger.error(f"安全专项检查失败: {result.get('error', '未知错误')}")
                
        except Exception as e:
            logger.error(f"安全专项检查执行异常: {e}")
    
    def run_performance_check(self):
        """运行性能专项检查"""
        logger.info("开始执行性能专项检查...")
        
        try:
            result = self.detection_system.run_performance_check()
            
            if result['status'] == 'success':
                logger.info("性能专项检查完成")
                
                # 如果性能评分低于阈值，发送告警
                lighthouse_scores = result.get('lighthouse_score', {})
                performance_score = lighthouse_scores.get('performance', 1.0)
                if performance_score < 0.8:
                    self._send_performance_alert(result)
            else:
                logger.error(f"性能专项检查失败: {result.get('error', '未知错误')}")
                
        except Exception as e:
            logger.error(f"性能专项检查执行异常: {e}")
    
    def _cleanup_old_reports(self):
        """清理旧报告文件"""
        logger.info("开始清理旧报告文件...")
        
        try:
            import glob
            from datetime import datetime, timedelta
            
            # 计算截止日期
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)
            
            # 查找旧文件
            old_files = []
            for pattern in ['web_config_*.json', 'web_config_*.html', 'web_config_*.md']:
                files = glob.glob(pattern)
                for file in files:
                    try:
                        # 尝试从文件名提取日期
                        file_date_str = file.split('_')[-1].split('.')[0]
                        file_date = datetime.strptime(file_date_str, '%Y%m%d')
                        
                        if file_date < cutoff_date:
                            old_files.append(file)
                    except:
                        # 如果无法解析日期，跳过
                        continue
            
            # 删除旧文件
            for file in old_files:
                try:
                    os.remove(file)
                    logger.info(f"已删除旧文件: {file}")
                except Exception as e:
                    logger.warning(f"删除文件失败 {file}: {e}")
            
            logger.info(f"清理完成，共删除 {len(old_files)} 个旧文件")
            
        except Exception as e:
            logger.error(f"清理旧文件时发生错误: {e}")
    
    def _generate_weekly_summary(self, result: Dict[str, Any]):
        """生成周报摘要"""
        try:
            summary_file = f"weekly_summary_{datetime.now().strftime('%Y%m%d')}.md"
            
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(f"# Web应用配置优化周报\n\n")
                f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"**目标URL**: {result['target_url']}\n\n")
                
                if 'summary' in result:
                    summary = result['summary']
                    f.write(f"## 本周问题统计\n\n")
                    f.write(f"- 危急问题: {summary.get('critical', 0)}\n")
                    f.write(f"- 高危问题: {summary.get('high', 0)}\n")
                    f.write(f"- 中等问题: {summary.get('medium', 0)}\n")
                    f.write(f"- 低危问题: {summary.get('low', 0)}\n")
                    f.write(f"- 总计: {summary.get('total', 0)}\n\n")
                
                f.write(f"## 建议\n\n")
                f.write(f"1. 优先处理危急和高危问题\n")
                f.write(f"2. 定期检查安全配置\n")
                f.write(f"3. 监控性能指标变化\n")
                f.write(f"4. 保持配置最佳实践\n")
            
            logger.info(f"周报摘要已生成: {summary_file}")
            
        except Exception as e:
            logger.error(f"生成周报摘要失败: {e}")
    
    def _send_notification(self, result: Dict[str, Any], is_weekly: bool = False):
        """发送通知"""
        try:
            # 这里可以集成邮件、钉钉、企业微信等通知方式
            # 示例：发送到日志文件
            notification_file = f"notification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            
            with open(notification_file, 'w', encoding='utf-8') as f:
                f.write(f"检测类型: {'周报' if is_weekly else '日报'}\n")
                f.write(f"检测时间: {result['timestamp']}\n")
                f.write(f"目标URL: {result['target_url']}\n")
                f.write(f"检测状态: {result['status']}\n")
                
                if 'summary' in result:
                    summary = result['summary']
                    f.write(f"问题统计: 危急{summary.get('critical', 0)} 高危{summary.get('high', 0)} 中等{summary.get('medium', 0)} 低危{summary.get('low', 0)}\n")
                
                if result['status'] == 'error':
                    f.write(f"错误信息: {result.get('error', '未知错误')}\n")
            
            logger.info(f"通知已发送: {notification_file}")
            
        except Exception as e:
            logger.error(f"发送通知失败: {e}")
    
    def _send_security_alert(self, result: Dict[str, Any]):
        """发送安全告警"""
        try:
            alert_file = f"security_alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            
            with open(alert_file, 'w', encoding='utf-8') as f:
                f.write(f"🚨 安全告警\n")
                f.write(f"检测时间: {result['timestamp']}\n")
                f.write(f"目标URL: {result['target_url']}\n")
                f.write(f"安全评分: {result.get('security_score', 0)}/100\n")
                f.write(f"安全评分过低，请立即检查安全配置！\n")
            
            logger.warning(f"安全告警已发送: {alert_file}")
            
        except Exception as e:
            logger.error(f"发送安全告警失败: {e}")
    
    def _send_performance_alert(self, result: Dict[str, Any]):
        """发送性能告警"""
        try:
            alert_file = f"performance_alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            
            with open(alert_file, 'w', encoding='utf-8') as f:
                f.write(f"⚠️ 性能告警\n")
                f.write(f"检测时间: {result['timestamp']}\n")
                f.write(f"目标URL: {result['target_url']}\n")
                
                lighthouse_scores = result.get('lighthouse_score', {})
                for category, score in lighthouse_scores.items():
                    f.write(f"{category}: {score:.2f}\n")
                
                f.write(f"性能评分过低，请检查性能配置！\n")
            
            logger.warning(f"性能告警已发送: {alert_file}")
            
        except Exception as e:
            logger.error(f"发送性能告警失败: {e}")
    
    def setup_schedule(self):
        """设置定时任务"""
        logger.info("设置定时任务...")
        
        # 每日检测
        if self.schedule_daily:
            schedule.every().day.at(self.schedule_time).do(self.run_daily_detection)
            logger.info(f"已设置每日检测任务，时间: {self.schedule_time}")
        
        # 每周检测
        if self.schedule_weekly:
            getattr(schedule.every(), self.schedule_weekly_day).at("03:00").do(self.run_weekly_detection)
            logger.info(f"已设置每周检测任务，时间: {self.schedule_weekly_day} 03:00")
        
        # 安全专项检查（每天上午10点）
        schedule.every().day.at("10:00").do(self.run_security_check)
        logger.info("已设置安全专项检查任务，时间: 10:00")
        
        # 性能专项检查（每天下午3点）
        schedule.every().day.at("15:00").do(self.run_performance_check)
        logger.info("已设置性能专项检查任务，时间: 15:00")
    
    def run(self):
        """运行调度器"""
        logger.info("启动Web应用配置优化检测调度器...")
        
        # 设置定时任务
        self.setup_schedule()
        
        # 启动时立即运行一次检测
        logger.info("启动时执行初始检测...")
        self.run_daily_detection()
        
        # 运行调度循环
        logger.info("调度器已启动，等待定时任务...")
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次
            except KeyboardInterrupt:
                logger.info("收到中断信号，正在停止调度器...")
                break
            except Exception as e:
                logger.error(f"调度器运行异常: {e}")
                time.sleep(60)  # 异常后等待1分钟再继续
        
        logger.info("调度器已停止")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Web应用配置优化检测调度器')
    parser.add_argument('--url', default=os.getenv('TARGET_URL', 'http://localhost:8080'),
                       help='目标Web应用URL')
    parser.add_argument('--daily-time', default=os.getenv('SCHEDULE_TIME', '01:00'),
                       help='每日检测时间')
    parser.add_argument('--weekly-day', default=os.getenv('SCHEDULE_WEEKLY_DAY', 'sunday'),
                       help='每周检测日期')
    parser.add_argument('--retention-days', type=int, default=int(os.getenv('RETENTION_DAYS', '30')),
                       help='报告保留天数')
    
    args = parser.parse_args()
    
    # 创建调度器
    scheduler = WebConfigScheduler()
    
    # 更新配置
    scheduler.target_url = args.url
    scheduler.schedule_time = args.daily_time
    scheduler.schedule_weekly_day = args.weekly_day
    scheduler.retention_days = args.retention_days
    
    # 运行调度器
    scheduler.run()

if __name__ == "__main__":
    main() 