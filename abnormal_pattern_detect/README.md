# 智能运维助手 - 异常模式检测子系统

## 🎯 项目概述

本系统是一个部署在单台服务器上的本地运维助手，具备以下核心能力：

- 📊 **持续监控**：实时采集系统资源、进程状态和服务日志
- 🔍 **异常检测**：使用机器学习算法自动识别系统异常
- 📋 **模式提取**：从异常数据中归纳总结可复用的故障特征
- 🔧 **扫描器生成**：自动生成针对特定异常模式的检测脚本
- ⚡ **预防性预警**：定期运行扫描器，提前发现潜在风险

## 🏗️ 系统架构

```
          +------------------+
          | 实时采集模块     |   ← collect_metrics.py + parse_logs.py
          +--------+---------+
                   |
                   ↓
          +--------v---------+
          | 异常检测模块     |   ← detect_anomaly.py (PyOD + Isolation Forest)
          +--------+---------+
                   |
                   ↓
          +--------v---------+
          | 模式提取模块     |   ← extract_pattern.py (聚类 + 关键词提取)
          +--------+---------+
                   |
                   ↓
          +--------v---------+
          | 扫描器生成模块   |   ← generate_scanner.py (模板 + AI组合)
          +--------+---------+
                   |
                   ↓
          +--------v---------+
          | 本地扫描执行模块 |   ← scan_*.py (定期运行 + 报告/告警)
          +------------------+
```

## 📦 文件结构

```
异常模式检测/
├── main.py                    # 主程序，协调各模块运行
├── collect_metrics.py         # 系统指标采集器
├── parse_logs.py             # 日志解析器
├── detect_anomaly.py         # 异常检测器
├── extract_pattern.py        # 异常模式提取器
├── generate_scanner.py       # 扫描器代码生成器
├── scan_mysql.py            # MySQL异常扫描器示例
├── scan_nginx.py            # Nginx异常扫描器示例
├── pattern_template.json     # 异常模式模板结构
├── requirements.txt          # Python依赖包清单
├── README.md                # 本文档
├── data/                    # 数据目录
│   ├── metrics.csv          # 系统指标数据
│   ├── processes.csv        # 进程指标数据
│   ├── parsed_logs.json     # 解析的日志数据
│   ├── anomaly_summary.json # 异常检测结果
│   └── extracted_patterns.json # 提取的异常模式
└── scanners/               # 生成的扫描器目录
    ├── scanner_index.py    # 扫描器管理工具
    ├── scan_mysql.py      # 自动生成的MySQL扫描器
    └── scan_nginx.py      # 自动生成的Nginx扫描器
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 安装Python依赖
pip install -r requirements.txt

# 或者使用conda
conda install psutil pandas numpy scikit-learn pyod jinja2 schedule
```

### 2. 运行完整检测流程

```bash
# 运行完整的异常模式检测流程
python main.py run

# 查看系统状态
python main.py status

# 启动持续监控模式（30分钟间隔）
python main.py monitor --interval 30
```

### 3. 分步执行

```bash
# 只收集数据
python main.py collect

# 只进行异常检测
python main.py detect

# 只提取异常模式
python main.py extract

# 只生成扫描器
python main.py generate
```

## 📋 详细功能说明

### 1. 实时采集模块 (`collect_metrics.py`)

**功能**：

- 使用 `psutil` 收集CPU、内存、磁盘、网络指标
- 监控关键服务进程状态（MySQL、Nginx、Redis等）
- 保存为CSV格式供后续分析

**使用示例**：

```python
from collect_metrics import MetricsCollector

collector = MetricsCollector(output_dir="data")
result = collector.collect_once()  # 执行一次采集
```

### 2. 日志解析模块 (`parse_logs.py`)

**功能**：

- 自动查找常见服务日志文件
- 提取错误关键词和异常模式
- 按时间窗口分析日志趋势

**支持的服务**：

- Nginx (`/var/log/nginx/error.log`)
- MySQL (`/var/log/mysql/error.log`)
- Apache (`/var/log/apache2/error.log`)
- Redis、PostgreSQL等

**使用示例**：

```python
from parse_logs import LogParser

parser = LogParser(output_dir="data")
parsed_data = parser.parse_all_logs(time_window_hours=24)
```

### 3. 异常检测模块 (`detect_anomaly.py`)

**功能**：

- 使用多种机器学习算法（Isolation Forest、LOF、KNN）
- 集成多模型结果提高检测准确性
- 结合指标异常和日志异常

**检测算法**：

- **Isolation Forest**：适合高维数据异常检测
- **LOF (Local Outlier Factor)**：基于密度的异常检测
- **KNN**：基于距离的异常检测

**使用示例**：

```python
from detect_anomaly import AnomalyDetector

detector = AnomalyDetector(output_dir="data", contamination=0.1)
results = detector.run_anomaly_detection(hours_back=24)
```

### 4. 模式提取模块 (`extract_pattern.py`)

**功能**：

- 从异常数据中计算统计特征（均值、标准差、阈值）
- 提取日志关键词和错误模式
- 生成结构化的异常模式模板

**模式类型**：

- **指标模式**：基于系统资源异常
- **日志模式**：基于日志错误特征
- **复合模式**：综合指标和日志的异常模式

**使用示例**：

```python
from extract_pattern import PatternExtractor

extractor = PatternExtractor(output_dir="data")
patterns = extractor.extract_all_patterns()
```

### 5. 扫描器生成模块 (`generate_scanner.py`)

**功能**：

- 基于Jinja2模板自动生成Python扫描器代码
- 根据异常模式设置检测阈值和规则
- 生成可执行的独立扫描脚本

**生成的扫描器特点**：

- 独立运行，无需依赖原系统
- 包含完整的检测逻辑和建议生成
- 支持多种通知方式

**使用示例**：

```python
from generate_scanner import ScannerGenerator

generator = ScannerGenerator(output_dir="data", scanners_dir="scanners")
scanners = generator.generate_all_scanners()
generator.save_scanners(scanners)
```

## 🔧 扫描器使用

### 运行单个扫描器

```bash
# 运行MySQL扫描器
python scanners/scan_mysql.py

# 运行Nginx扫描器  
python scanners/scan_nginx.py
```

### 批量运行扫描器

```bash
cd scanners

# 查看所有扫描器
python scanner_index.py list

# 运行指定扫描器
python scanner_index.py run mysql

# 运行所有扫描器
python scanner_index.py run-all
```

## 📊 示例场景

### 场景1：MySQL内存泄漏检测

**异常特征**：

- MySQL进程内存占用 > 80%
- 日志中出现 "Out of memory" 或 "InnoDB" 错误

**生成的检测逻辑**：

```python
if process_memory_percent > 80 and "Out of memory" in mysql_error_log:
    print("⚠️ 检测到MySQL内存泄漏风险")
    print("💡 建议：检查innodb_buffer_pool_size配置")
```

### 场景2：Nginx响应失败

**异常特征**：

- CPU使用率 > 90%
- 502错误率 > 15%
- 日志包含 "upstream timeout"

**生成的检测逻辑**：

```python
if nginx_502_rate > 0.15 and "upstream timeout" in nginx_error_log:
    print("⚠️ Web服务可能过载")
    print("💡 建议：检查上游服务状态，优化负载均衡")
```

## ⚙️ 配置说明

### 1. 异常检测配置

```python
# 在 detect_anomaly.py 中调整
contamination = 0.1  # 异常比例估计（5%-20%）
```

### 2. 模式提取配置

```python
# 在 extract_pattern.py 中调整阈值
metric_thresholds = {
    'cpu_percent': {'high': 80, 'critical': 90},
    'memory_percent': {'high': 75, 'critical': 85}
}
```

### 3. 监控配置

```python
# 在 main.py 中调整监控间隔
collection_interval_minutes = 30  # 数据收集间隔
pattern_analysis_schedule = "02:00"  # 每天模式分析时间
```

## 📈 监控模式

系统支持两种运行模式：

### 1. 一次性分析模式

```bash
python main.py run
```

- 执行完整的检测流程
- 适合初始化或手动分析

### 2. 持续监控模式

```bash
python main.py monitor --interval 30
```

- 每30分钟收集一次数据
- 每天凌晨2点重新分析模式
- 适合生产环境长期运行

## 🔍 故障排查

### 常见问题

1. **没有检测到异常**

   - 检查数据收集是否正常
   - 调整 contamination 参数（降低到0.05）
   - 确保系统有足够的历史数据
2. **没有生成扫描器**

   - 确保先检测到异常
   - 检查模式提取是否成功
   - 查看日志文件了解详细错误
3. **权限问题**

   - 确保有读取日志文件的权限
   - 部分系统指标需要管理员权限

### 日志文件

查看详细日志：

```bash
tail -f data/anomaly_detection.log
```

## 🚀 性能优化

### 1. 大规模环境优化

- 调整数据收集间隔
- 限制日志文件读取行数
- 使用数据库存储历史数据

### 2. 内存优化

- 设置数据文件大小限制
- 定期清理历史数据
- 使用流式处理大文件

## 🔮 扩展功能

### 1. 添加新的服务监控

编辑 `collect_metrics.py`：

```python
self.key_services.append('your_service_name')
```

### 2. 自定义异常检测算法

继承 `AnomalyDetector` 类并实现自定义检测逻辑

### 3. 集成外部通知

在生成的扫描器中添加：

- 邮件通知
- Slack/钉钉通知
- 短信告警

## 📞 技术支持

如有问题，请检查：

1. **系统状态**：`python main.py status`
2. **日志文件**：`data/anomaly_detection.log`
3. **依赖安装**：确保所有required包已安装
4. **权限设置**：确保有足够的系统访问权限

---

**系统实现了从"异常发生" → "自动总结规律" → "构建诊断工具" → "提前预警"的完整闭环！** 🎉
