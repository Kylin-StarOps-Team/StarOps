# MCPArchieve - 智能系统监控助手

基于MCP（Model Context Protocol）构建的新一代智能系统监控解决方案，集成7种专业监控协议，提供全方位的系统监控、安全扫描、数据库监控和日志分析功能。支持图形界面和命令行两种交互方式，具备AI智能体交互、异常检测、十级制评分和对话历史管理等先进特性。

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-2.0-orange.svg)](CHANGELOG.md)

## 🎯 功能特性

### 核心功能
- **🔍 智能系统监控**: 支持8种专业监控协议，涵盖系统、网络、数据库、日志、安全、异常检测等全方位监控
- **🤖 AI智能交互**: 自然语言问答，智能选择合适的监控协议
- **📊 异常检测分析**: 十级制异常评分系统，提供详细的异常分析和解决建议
- **⚡ 实时工具调用链**: 可视化显示工具调用过程、参数和执行结果
- **🧠 思考过程展示**: 实时显示AI的思考过程和决策逻辑
- **💾 对话历史管理**: 智能保存和加载对话上下文，支持历史查询
- **🚀 多线程处理**: 界面响应流畅，支持并发处理
- **📱 多版本支持**: 
  - 现代化Flet桌面应用（推荐）
  - 传统Tkinter桌面应用
  - 命令行CLI版本
- **📁 日志文件读取**: 从系统日志文件直接读取监控数据，无需额外配置

### 🛡️ 支持的监控协议 (8种)

#### 系统监控协议
1. **WindowsIOMonitorProtocol** - 磁盘IO监控
   - 磁盘IO状态实时监控
   - 读写字节统计分析
   - 分区使用率分析

2. **PrometheusMonitorProtocol** - 系统指标监控
   - CPU使用率和负载监控
   - 内存使用率监控
   - 网络流量监控
   - 磁盘使用率监控
   - 系统运行时间监控

3. **NodeExporterProtocol** - 系统级指标采集 🆕
   - 全面的系统硬件指标
   - CPU、内存、磁盘、网络详细监控
   - 系统负载和进程统计
   - 从 `/var/log/node_exporter_metrics.log` 读取数据

#### 网络监控协议
4. **BlackboxExporterProtocol** - 黑盒探测监控 🆕
   - HTTP/HTTPS网站可用性检测
   - TCP端口连通性测试
   - ICMP ping检测
   - DNS解析监控
   - 从 `/var/log/blackbox_exporter_metrics.log` 读取数据

#### 数据库监控协议
5. **MysqldExporterProtocol** - MySQL数据库监控 🆕
   - 数据库连接数和性能监控
   - 查询执行统计和慢查询分析
   - 复制状态和延迟监控
   - 锁等待和事务统计
   - 从 `/var/log/mysqld_exporter_metrics.log` 读取数据

#### 日志分析协议
6. **LokiPromtailProtocol** - 日志收集和分析 🆕
   - 系统日志实时收集
   - 错误日志模式匹配
   - 日志级别统计分析
   - 异常日志趋势检测
   - 从 `/var/log/loki_monitor_log.json` 读取数据

#### 安全扫描协议
7. **TrivySecurityProtocol** - 安全漏洞扫描
   - 容器镜像安全漏洞扫描
   - 文件系统和项目目录安全扫描
   - Git仓库安全漏洞扫描
   - Kubernetes集群安全扫描
   - 配置文件(IaC)安全扫描
   - 软件物料清单(SBOM)安全扫描
   - 敏感信息泄露检测

#### 异常模式检测协议 🆕
8. **AnomalyPatternDetectionProtocol** - 智能异常模式检测
   - 多服务异常模式自动检测（MySQL、Nginx、System、Loki等）
   - 数据采集 → 异常检测 → 模式提取 → 扫描器生成的完整流程
   - 自动生成针对性的异常检测扫描器
   - 十级制异常评分和详细分析报告
   - 支持实时扫描和历史数据分析



## 📁 项目结构

```
MCPArchieve/
├── core/                    # 🧠 核心模块
│   ├── __init__.py         # 模块导出定义
│   ├── ai_model.py         # AI模型接口和提示词管理
│   ├── smart_monitor.py    # 智能监控器核心逻辑
│   ├── mcp_protocols.py    # 7种MCP协议实现
│   └── monitor_utils.py    # 监控工具函数
├── utils/                   # 🛠️ 工具模块
│   ├── __init__.py
│   ├── config.py           # 配置管理和环境变量处理
│   ├── history_manager.py  # 对话历史管理和持久化
│   └── ui_utils.py         # UI工具和界面组件
├── apps/                    # 📱 应用层
│   ├── desktop_app.py      # 桌面GUI应用（Tkinter）
│   ├── flet_desktop_app.py # 现代化桌面应用（Flet）
│   └── cli_app.py          # 命令行CLI应用
├── docs/                    # 📚 文档中心
│   ├── README.md           # 文档导航
│   ├── user-guide/         # 用户指南
│   ├── integration/        # 集成文档
│   └── development/        # 开发文档
├── run.py                   # 🚀 智能启动脚本
├── run_flet_app.py          # Flet应用启动脚本
├── requirements_flet.txt    # Flet应用依赖文件
├── config.json              # ⚙️ 配置文件
├── conversation_history.json # 💾 对话历史文件
├── test_integration.py      # 🧪 集成测试脚本
├── test_new_protocols.py    # 新协议测试脚本
├── app_sync_summary.md      # 应用同步报告
├── REFACTOR_SUMMARY.md      # 项目重构报告
└── README.md               # 📖 项目说明
```

## 🚀 快速开始

### 环境要求
- Python 3.7+
- tkinter (通常随Python安装) - 用于传统桌面应用
- flet>=0.28.0 - 用于现代化桌面应用
- requests库
- psutil库
- Trivy (用于安全扫描功能)


### 安装依赖
```bash
# 安装Python依赖（传统应用）
pip3 install requests psutil

# 安装Flet依赖（现代化桌面应用）
pip3 install -r requirements_flet.txt
# 或单独安装
pip3 install flet>=0.28.0 requests psutil

# 安装Trivy (可选，用于安全扫描功能)
# 获取最新版本号
LATEST_VERSION=$(curl -sL https://api.github.com/repos/aquasecurity/trivy/releases/latest | grep tag_name | cut -d '"' -f 4)

# 下载并安装
wget https://github.com/aquasecurity/trivy/releases/download/${LATEST_VERSION}/trivy_${LATEST_VERSION#v}_Linux-64bit.tar.gz
tar -xzf trivy_*.tar.gz
sudo install trivy /usr/local/bin/

# 验证安装
trivy --version


```

### 运行应用
```bash
# 智能启动（推荐）- 自动选择合适版本
python3 run.py

# 直接启动桌面版本（Tkinter）
python3 apps/desktop_app.py

# 启动现代化Flet桌面应用（推荐）
python3 run_flet_app.py
# 或直接运行
python3 apps/flet_desktop_app.py

# 直接启动命令行版本
python3 apps/cli_app.py


```

## ✨ Flet现代化桌面应用特色

### 界面优势
- **现代化设计**: 基于Flutter技术栈，提供精美的原生UI体验
- **响应式布局**: 自适应窗口大小调整，完美支持多种分辨率
- **实时交互**: 流畅的动画效果和即时的界面反馈
- **可视化展示**: 分区域显示聊天、思考过程和工具调用链

### 功能特色
- **双窗格设计**: 左侧为对话区域，右侧为AI思考过程和工具调用链
- **实时状态显示**: 底部状态栏显示当前处理状态和操作按钮
- **智能消息样式**: 用户和AI消息采用不同颜色和图标区分
- **工具调用可视化**: 清晰展示协议名称、参数和执行结果
- **思考过程追踪**: 实时显示AI的思考和决策过程
- **历史对话管理**: 支持加载、保存和清空对话历史

### 性能优化
- **多线程处理**: UI线程与业务逻辑分离，确保界面流畅
- **异步响应**: 支持并发处理，提升用户体验
- **内存管理**: 智能清理和历史长度限制

## 💡 使用指南

### 💬 智能对话示例

#### 系统监控类问题
```
• "我的CPU使用率怎么样？" → NodeExporterProtocol
• "系统内存使用情况如何？" → NodeExporterProtocol  
• "磁盘IO状态如何？" → WindowsIOMonitorProtocol
• "系统负载高吗？" → PrometheusMonitorProtocol
• "给我一个系统整体状况的概览" → NodeExporterProtocol
• "网络流量怎么样？" → PrometheusMonitorProtocol
```

#### 网络连通性检测
```
• "百度网站能访问吗？" → BlackboxExporterProtocol
• "检查Google的HTTP响应时间" → BlackboxExporterProtocol
• "测试数据库服务器的TCP连接" → BlackboxExporterProtocol
• "ping一下服务器看看网络延迟" → BlackboxExporterProtocol
```

#### 数据库监控
```
• "MySQL数据库连接数多少？" → MysqldExporterProtocol
• "数据库有慢查询吗？" → MysqldExporterProtocol
• "检查数据库复制状态" → MysqldExporterProtocol
• "数据库性能怎么样？" → MysqldExporterProtocol
```

#### 日志分析
```
• "有什么错误日志？" → LokiPromtailProtocol
• "最近有异常日志吗？" → LokiPromtailProtocol
• "分析系统日志趋势" → LokiPromtailProtocol
• "查找包含'error'的日志" → LokiPromtailProtocol
```

#### 安全扫描
```
• "扫描这个Docker镜像的安全漏洞" → TrivySecurityProtocol
• "检查当前项目目录的安全风险" → TrivySecurityProtocol
• "扫描这个Git仓库的安全问题" → TrivySecurityProtocol
• "检查Kubernetes集群的安全配置" → TrivySecurityProtocol
• "扫描Terraform配置文件的安全问题" → TrivySecurityProtocol
• "检测敏感信息泄露" → TrivySecurityProtocol
```



### 📟 命令行版本命令
```
/help     - 显示帮助信息和协议列表
/history  - 显示对话历史
/clear    - 清空当前对话
/save     - 保存对话到文件
/status   - 显示系统状态和支持的协议
/quit     - 退出应用
```

### 📊 异常评分系统
MCPArchieve采用十级制异常评分系统，为每个监控结果提供量化的风险评估：

| 评分等级 | 描述 | 颜色标识 | 建议措施 |
|---------|------|---------|---------|
| **0级** | 正常 | 🟢 绿色 | 继续监控 |
| **1-3级** | 轻微异常 | 🟡 黄色 | 关注趋势 |
| **4-6级** | 中等异常 | 🟠 橙色 | 需要处理 |
| **7-8级** | 严重异常 | 🔴 红色 | 立即处理 |
| **9-10级** | 危急异常 | 🚨 闪烁红色 | 紧急处理 |

### 🗂️ 日志文件配置
确保以下日志文件存在并具有读取权限：
```bash
/var/log/node_exporter_metrics.log      # Node Exporter系统指标
/var/log/blackbox_exporter_metrics.log  # Blackbox网络探测数据
/var/log/mysqld_exporter_metrics.log    # MySQL数据库指标
/var/log/loki_monitor_log.json          # Loki日志分析数据
```

## ⚙️ 配置说明

### 配置文件 (config.json)
```json
{
  "api_key": "your-api-key-here",
  "prometheus_url": "http://your-prometheus-server:9090",
  "max_history_length": 20,
  "default_interval": 1,
  "default_count": 3,
  "default_time_range": "5m",
  "ui": {
    "window_width": 1200,
    "window_height": 800,
    "font_family": "Consolas",
    "font_size": 10
  }
}
```

### 环境变量
- `API_KEY`: AI模型API密钥
- `PROMETHEUS_URL`: Prometheus服务器地址

## 🔧 技术架构

### 核心组件
1. **SmartMonitor**: 智能监控器，处理7种MCP协议调用和协议注册
2. **OnlineModel**: AI模型接口，处理对话生成和协议选择
3. **MCP协议集合**: 7种专业监控协议的完整实现
   - 系统监控: Windows IO、Prometheus、Node Exporter
   - 网络监控: Blackbox Exporter
   - 数据库监控: Mysqld Exporter
   - 日志分析: Loki Promtail
   - 安全扫描: Trivy Security
4. **HistoryManager**: 对话历史管理和持久化存储
5. **Config**: 配置管理和环境变量处理
6. **异常检测引擎**: 十级制评分系统和智能异常分析

### 🔄 数据流程
1. **用户输入**: 自然语言问题或命令
2. **AI智能分析**: 解析问题意图，选择合适的MCP协议
3. **协议执行**: 从对应的日志文件读取监控数据
4. **数据解析**: 根据数据格式（JSON/Prometheus文本）解析指标
5. **异常检测**: 应用检测规则，生成十级制评分
6. **智能分析**: AI基于监控数据生成详细分析报告
7. **结果展示**: 在界面中显示结果、异常评分和工具调用过程
8. **历史保存**: 自动保存对话历史和分析结果

### 🏗️ 架构特点
- **模块化设计**: 核心、工具、应用三层架构，职责清晰
- **插件化协议**: 支持动态注册新的MCP协议
- **多数据源**: 支持HTTP API、日志文件、系统调用等多种数据源
- **智能路由**: AI自动选择最适合的监控协议
- **异步处理**: 支持并发执行多个监控任务
- **容错机制**: 完善的错误处理和优雅降级

## 🛠️ 开发指南

### 🔧 添加新的MCP协议
```python
# 1. 在 core/mcp_protocols.py 中实现新协议
class NewMonitorProtocol:
    @staticmethod
    def execute(params=None):
        # 实现监控逻辑
        return {
            "status": "success",
            "summary": {...},
            "anomaly_analysis": {...},
            "raw_data": {...}
        }

# 2. 在 core/smart_monitor.py 中注册
self.mcp_protocols["NewMonitorProtocol"] = NewMonitorProtocol

# 3. 在 core/ai_model.py 中添加提示词规则
```

### 🎨 自定义界面
支持多种界面定制选项：
- **主题切换**: 修改`utils/ui_utils.py`中的颜色配置
- **布局调整**: 调整窗口大小和组件布局
- **字体设置**: 自定义字体家族和大小
- **颜色配置**: 自定义消息颜色和状态指示器

### 🚀 扩展功能
- **监控协议扩展**: 支持更多监控系统（如Grafana、InfluxDB等）
- **数据可视化**: 集成图表库，提供监控数据可视化
- **AI模型集成**: 支持更多AI模型（GPT、Claude、本地模型等）
- **插件系统**: 开发插件接口，支持第三方扩展
- **告警系统**: 集成邮件、短信、钉钉等告警通道
- **数据存储**: 支持监控数据持久化存储

### 📊 性能优化建议
- **缓存机制**: 实现监控数据缓存，减少重复读取
- **批量处理**: 支持批量执行多个监控任务
- **内存管理**: 及时清理大型数据结构
- **并发优化**: 使用异步处理提升响应速度

## 🐛 故障排除

### 🔍 常见问题及解决方案

#### 启动问题
| 问题 | 症状 | 解决方案 |
|------|------|---------|
| **导入错误** | `ModuleNotFoundError` | 检查依赖安装: `pip3 install -r requirements_flet.txt` |
| **API错误** | `API key not found` | 在`config.json`中配置有效的API密钥 |
| **GUI环境错误** | `TclError: no display` | 使用命令行版本: `python3 apps/cli_app.py` |

#### 监控问题
| 问题 | 症状 | 解决方案 |
|------|------|---------|
| **日志文件不存在** | `FileNotFoundError` | 确保日志文件存在并有读取权限 |
| **数据解析失败** | `JSON decode error` | 检查日志文件格式是否正确 |
| **协议调用失败** | `Protocol execution failed` | 查看具体错误信息，检查数据源 |

#### 性能问题
| 问题 | 症状 | 解决方案 |
|------|------|---------|
| **界面响应慢** | UI卡顿 | 检查是否有长时间运行的监控任务 |
| **内存占用高** | 内存不断增长 | 重启应用或清空对话历史 |

### 📋 日志和调试
应用提供详细的执行日志：
```bash
# 启用详细日志
export DEBUG=1
python3 run.py

# 日志内容包括：
• 🔧 工具调用过程和参数
• ❌ 错误信息和堆栈跟踪  
• ⏱️ 处理时间统计
• 📊 异常检测结果
• 🧠 AI思考过程
```

### 🧪 测试和验证
```bash
# 运行集成测试
python3 test_integration.py

# 测试新协议功能
python3 test_new_protocols.py


```

## 📄 许可证

本项目基于MIT许可证开源。

## 🤝 贡献

欢迎提交Issue和Pull Request来改进项目。

## 📚 文档和支持

### 📖 完整文档
- **[文档中心](docs/README.md)** - 完整的文档导航
- **[用户指南](docs/user-guide/)** - 安装、配置和使用指南
- **[集成文档](docs/integration/)** - MCP协议集成和应用同步报告
- **[开发文档](docs/development/)** - 架构设计和开发指南

### 🔗 快速链接
- **[项目重构报告](REFACTOR_SUMMARY.md)** - 了解项目架构演进
- **[应用同步报告](app_sync_summary.md)** - 新协议集成详情
- **[集成测试报告](test_integration.py)** - 功能验证和测试结果

### 🆕 版本更新
- **v2.0** - 集成4个新监控协议，支持异常检测和十级制评分
- **v1.5** - 重构项目架构，模块化设计
- **v1.0** - 基础MCP协议支持

### 🤝 社区支持
- **GitHub Issues** - 问题报告和功能请求
- **Pull Requests** - 代码贡献和改进建议
- **Discussions** - 技术讨论和经验分享

### 📞 获取帮助
遇到问题时的处理步骤：
1. **查看文档** - 先查阅相关文档和FAQ
2. **运行测试** - 使用测试脚本诊断问题
3. **检查日志** - 查看详细的错误日志
4. **提交Issue** - 提供详细的问题描述和环境信息

---

## 🎉 总结

MCPArchieve是一个功能强大的智能系统监控解决方案，具备以下核心优势：

### ✨ 核心亮点
- **🔥 7种专业监控协议** - 覆盖系统、网络、数据库、日志、安全全方位监控
- **🤖 AI智能交互** - 自然语言问答，智能选择合适的监控工具
- **📊 十级制异常评分** - 量化风险评估，提供具体的解决建议
- **🚀 多应用支持** - 命令行、传统GUI、现代化Flet三种交互方式
- **📁 日志文件集成** - 直接从系统日志读取数据，无需额外配置

### 🎯 适用场景
- **系统运维** - 全面的服务器和应用监控
- **DevOps** - 集成到CI/CD流程的监控检查
- **安全审计** - 容器镜像和代码安全扫描
- **数据库管理** - MySQL性能监控和优化
- **日志分析** - 智能日志分析和异常检测

### 🚀 开始使用
```bash
# 克隆项目
git clone <repository-url>
cd MCPArchieve

# 安装依赖
pip3 install -r requirements_flet.txt

# 配置API密钥
# 编辑 config.json 文件

# 启动应用
python3 run.py
```

立即开始体验智能化的系统监控！🎊 