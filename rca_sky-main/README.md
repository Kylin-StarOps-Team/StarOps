# 微服务异常检测与根因分析系统

这是一个基于SkyWalking数据源和Ollama本地大模型的微服务异常检测与根因分析系统。

## 功能特性

- 🔍 **数据采集**: 从SkyWalking获取服务监控数据和调用链信息
- ⚠️ **异常检测**: 使用多种算法检测服务异常（统计方法、Z-Score、孤立森林）
- 🎯 **根因分析**: 基于服务拓扑和异常关联性进行根因分析
- 🤖 **AI智能分析**: 使用Ollama本地大模型进行智能分析和推理
- 📊 **结果输出**: 多格式输出分析结果（JSON、CSV、文本报告）

## 系统架构

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   SkyWalking    │───▶│   数据采集模块    │───▶│   异常检测模块   │
│   监控数据      │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   结果输出      │◀───│   AI智能分析     │◀───│   根因分析模块   │
│   (多格式)      │    │   (Ollama)       │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 环境要求

- Python 3.8+
- SkyWalking OAP服务
- Ollama（可选，用于AI分析）

## 快速开始

### 1. 环境准备

```bash
# 克隆或下载项目文件到本地
# 确保Python 3.8+已安装

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置系统

编辑 `config.yaml` 文件，配置SkyWalking和Ollama连接信息：

```yaml
# SkyWalking配置
skywalking:
  base_url: "http://localhost:12800"  # 修改为你的SkyWalking地址
  timeout: 30

# Ollama配置
ollama:
  base_url: "http://localhost:11434"  # 修改为你的Ollama地址
  model: "llama3.1"  # 修改为你使用的模型
  timeout: 60
```

### 3. 运行系统

#### 方式1: 使用运行脚本（推荐）

```bash
python run.py
```

#### 方式2: 直接运行主程序

```bash
python main.py
```

#### 方式3: 仅安装依赖后运行

```bash
python run.py --install-deps
```

## 配置说明

### 异常检测配置

```yaml
anomaly_detection:
  response_time_threshold: 1000      # 响应时间阈值(毫秒)
  error_rate_threshold: 5.0          # 错误率阈值(百分比)
  throughput_drop_threshold: 30.0    # 吞吐量下降阈值(百分比)
  time_window: 15                    # 检测窗口大小(分钟)
  algorithms:                        # 检测算法
    - "statistical"
    - "isolation_forest"
    - "z_score"
```

### 根因分析配置

```yaml
root_cause_analysis:
  max_depth: 5                       # 最大分析深度
  correlation_threshold: 0.7         # 关联性阈值
  time_correlation_window: 5         # 时间关联窗口(分钟)
```

## 输出结果

系统会在 `./results` 目录下生成以下文件：

- `summary_report_*.txt` - 人类可读的摘要报告
- `anomalies_*.json` - 异常检测详细结果
- `root_causes_*.json` - 根因分析详细结果
- `ai_analysis_*.json` - AI智能分析结果
- `comprehensive_report_*.json` - 综合报告
- `anomalies_summary_*.csv` - CSV格式的异常摘要
- `index_*.txt` - 文件索引

## 核心算法

### 异常检测算法

1. **统计方法**: 基于阈值的异常检测
2. **Z-Score**: 基于标准差的离群值检测
3. **孤立森林**: 基于机器学习的异常检测

### 根因分析算法

1. **服务关键性评估**: 基于PageRank和中心性分析
2. **异常关联性分析**: 计算异常间的相关性
3. **影响传播分析**: 分析故障在服务拓扑中的传播路径

## AI智能分析

使用Ollama本地大模型进行：

- 异常模式识别和分析
- 根因可信度评估
- 修复建议生成
- 综合故障报告生成

## 故障排除

### 1. SkyWalking连接失败

- 检查SkyWalking OAP服务是否正常运行
- 确认配置文件中的地址和端口正确
- 检查网络连接

### 2. Ollama连接失败

- 检查Ollama服务是否启动
- 确认模型是否已下载
- 可以在配置中禁用AI分析功能

### 3. 数据采集为空

- 确认SkyWalking中有监控数据
- 检查时间窗口设置是否合理
- 验证服务是否有调用链数据

## 扩展开发

系统采用模块化设计，可以轻松扩展：

- 添加新的异常检测算法
- 自定义根因分析逻辑
- 集成其他AI服务
- 添加新的输出格式

## 许可证

本项目使用MIT许可证。

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。
