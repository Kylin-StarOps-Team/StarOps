# Web应用配置优化检测系统

## 概述

Web应用配置优化检测系统是一个全面的Web应用配置分析和优化工具，能够自动检测Web应用及其运行环境的配置缺陷，并提供详细的优化建议。

## 功能特性

### 🔍 全面检测
- **系统级配置检测**: 文件句柄限制、网络参数、内存分配策略等
- **Web服务器配置检测**: Nginx、Apache配置优化
- **应用框架配置检测**: Spring Boot、Django、Flask、Tomcat、Gunicorn
- **安全配置检测**: HTTP安全头、TLS/SSL配置、访问控制
- **性能指标检测**: Lighthouse性能审计、系统资源监控

### 🎯 智能分析
- 基于最佳实践的配置规则库
- 银河麒麟OS特别优化建议
- 多维度问题严重性评估
- AI驱动的优化建议生成

### 📊 可视化报告
- HTML格式交互式报告
- Markdown格式技术报告
- 问题分类和过滤功能
- 实时性能指标展示

### ⚡ 自动化支持
- 定时检测任务调度
- 自动报告生成和清理
- 告警通知机制
- 容器化部署支持

## 快速开始

### 环境要求

- Python 3.8+
- Node.js 18+ (用于Lighthouse)
- 支持的操作系统: Linux (推荐Ubuntu/CentOS/银河麒麟)

### 安装依赖

```bash
# 安装Python依赖
pip install -r requirements.txt

# 安装Lighthouse (可选，用于性能检测)
npm install -g lighthouse
```

### 基本使用

```bash
# 运行完整检测
python main.py --url http://your-web-app.com

# 快速检测模式
python main.py --url http://your-web-app.com --mode quick

# 安全专项检查
python main.py --url http://your-web-app.com --mode security

# 性能专项检查
python main.py --url http://your-web-app.com --mode performance
```

### 部署方式选择

#### 方式1: 直接运行（推荐用于开发测试）
```bash
# 安装依赖
pip install -r requirements.txt
npm install -g lighthouse

# 运行检测
python main.py --url http://your-web-app.com
```

#### 方式2: Docker部署（推荐用于生产环境）
```bash
# 构建并运行
docker-compose up -d

# 查看报告
# HTML报告: http://localhost:8081
# Web应用: http://localhost:8080
```

**选择建议:**
- **开发测试**: 使用方式1，更简单直接
- **生产环境**: 使用方式2，更稳定可靠
- **团队协作**: 使用方式2，避免环境差异

## 详细使用说明

### 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--url` | 目标Web应用URL | http://localhost:8080 |
| `--mode` | 检测模式 (full/quick/security/performance) | full |
| `--output-dir` | 输出目录 | ./reports |
| `--no-report` | 不生成详细报告 | False |

### 检测模式说明

#### 1. 完整检测模式 (full)
- 收集所有配置信息
- 进行全面分析
- 生成HTML和Markdown报告
- 包含Lighthouse性能审计

#### 2. 快速检测模式 (quick)
- 收集配置信息
- 生成分析摘要
- 不生成详细报告
- 适合CI/CD集成

#### 3. 安全专项检查 (security)
- 检查HTTP安全头
- 分析Web服务器安全配置
- 计算安全评分
- 生成安全告警

#### 4. 性能专项检查 (performance)
- 分析性能相关配置
- 运行Lighthouse审计
- 监控系统资源
- 生成性能优化建议

### 定时任务

```bash
# 启动定时调度器
python scheduler.py --url http://your-web-app.com

# 自定义调度时间
python scheduler.py \
  --url http://your-web-app.com \
  --daily-time "02:00" \
  --weekly-day "sunday" \
  --retention-days 30
```

### 环境变量配置

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `TARGET_URL` | 目标Web应用URL | http://localhost:8080 |
| `SCHEDULE_DAILY` | 启用每日检测 | true |
| `SCHEDULE_TIME` | 每日检测时间 | 01:00 |
| `SCHEDULE_WEEKLY` | 启用每周检测 | false |
| `SCHEDULE_WEEKLY_DAY` | 每周检测日期 | sunday |
| `RETENTION_DAYS` | 报告保留天数 | 30 |

## 检测内容详解

### 系统级配置检测

| 检测项 | 说明 | 优化建议 |
|--------|------|----------|
| 文件句柄限制 | 检查ulimit -n值 | 建议设置为65536或更高 |
| Swappiness | 检查内存交换策略 | 建议设置为1-10 |
| Somaxconn | 检查TCP连接队列大小 | 建议设置为1024或更高 |
| NTP服务 | 检查时间同步状态 | 建议启用NTP服务 |

### Web服务器配置检测

#### Nginx配置
- `worker_processes`: 工作进程数优化
- `keepalive_timeout`: 连接保持时间
- `gzip`: 压缩配置
- `security_headers`: 安全头配置
- `ssl_certificate`: HTTPS配置

#### Apache配置
- `MaxRequestWorkers`: 最大请求工作进程
- `KeepAliveTimeout`: 连接保持超时
- `EnableSendfile`: 文件传输优化
- `EnableMMAP`: 内存映射优化

### 应用框架配置检测

#### Spring Boot
- `server.tomcat.max-threads`: Tomcat线程池大小
- `spring.datasource.hikari.maximum-pool-size`: 数据库连接池大小
- `server.port`: 服务端口配置

#### Django
- `DEBUG`: 调试模式检查
- `CONN_MAX_AGE`: 数据库连接复用
- `SESSION_COOKIE_SECURE`: 安全Cookie配置

#### Flask
- `DEBUG`: 调试模式检查
- `MAX_CONTENT_LENGTH`: 文件上传大小限制
- `SECRET_KEY`: 密钥配置

### 安全配置检测

#### HTTP安全头
- `Content-Security-Policy`: 内容安全策略
- `X-Frame-Options`: 点击劫持防护
- `X-Content-Type-Options`: MIME类型嗅探防护
- `Strict-Transport-Security`: HTTPS强制传输
- `X-XSS-Protection`: XSS防护
- `Referrer-Policy`: 引用策略
- `Permissions-Policy`: 权限策略

#### 安全评分计算
- 关键安全头 (CSP, X-Frame-Options, HSTS): 每个20分
- 其他安全头: 每个8分
- 总分: 100分

### 性能配置检测

#### Lighthouse性能指标
- `First Contentful Paint`: 首次内容绘制
- `Largest Contentful Paint`: 最大内容绘制
- `First Input Delay`: 首次输入延迟
- `Cumulative Layout Shift`: 累积布局偏移
- `Total Blocking Time`: 总阻塞时间

#### 系统性能指标
- CPU使用率
- 内存使用率
- 磁盘使用率
- 网络连接数
- Web进程状态

## 报告说明

### HTML报告特性
- 响应式设计，支持移动端
- 交互式问题过滤
- 实时问题统计
- 详细的解决方案说明
- 配置对比展示

### Markdown报告特性
- 技术文档格式
- 按严重性分组
- 便于版本控制
- 支持自动化处理

### 报告文件说明
- `web_config_report_YYYYMMDD_HHMMSS.json`: 原始配置数据
- `web_config_analysis_YYYYMMDD_HHMMSS.json`: 分析结果
- `web_config_report_YYYYMMDD_HHMMSS.html`: HTML可视化报告
- `web_config_report_YYYYMMDD_HHMMSS.md`: Markdown技术报告

## 银河麒麟OS特别支持

### 国产CPU优化
- 龙芯架构特定优化建议
- 工作进程亲和性配置
- 事件驱动模型优化

### 麒麟安全模块集成
- 自动检测麒麟安全模块状态
- 安全模块启用建议
- 国产化安全配置

### 国产浏览器兼容性
- 麒麟安全浏览器前缀
- 奇安信浏览器前缀
- 兼容性优化建议

## 最佳实践

### 部署建议
1. 在生产环境使用Docker部署
2. 配置定时任务进行定期检测
3. 设置告警阈值和通知机制
4. 定期清理旧报告文件

### 配置优化优先级
1. **危急问题**: 立即修复，如安全漏洞
2. **高危问题**: 优先处理，如性能瓶颈
3. **中等问题**: 计划修复，如配置优化
4. **低危问题**: 可选修复，如最佳实践

### 持续集成
```yaml
# .gitlab-ci.yml 示例
web_config_check:
  stage: test
  image: python:3.9
  script:
    - pip install -r requirements.txt
    - python main.py --url $CI_ENVIRONMENT_URL --mode quick
  artifacts:
    paths:
      - reports/
    expire_in: 1 week
```

## 故障排除

### 常见问题

#### 1. Lighthouse安装失败
```bash
# 解决方案
npm install -g lighthouse --unsafe-perm=true --allow-root
```

#### 2. 权限不足
```bash
# 解决方案
sudo chmod +x *.py
sudo chown -R $USER:$USER .
```

#### 3. 依赖安装失败
```bash
# 解决方案
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

#### 4. 容器启动失败
```bash
# 解决方案
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### 日志查看
```bash
# 查看检测日志
tail -f web_config_detection.log

# 查看调度器日志
tail -f scheduler.log

# 查看Docker日志
docker-compose logs -f web-optimizer
```

## 贡献指南

### 开发环境设置
```bash
# 克隆代码
git clone <repository-url>
cd web配置优化检测

# 安装开发依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 运行测试
python -m pytest tests/
```

### 代码规范
- 遵循PEP 8编码规范
- 添加类型注解
- 编写单元测试
- 更新文档说明

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交Issue
- 发送邮件
- 参与讨论

---

**注意**: 本工具仅用于配置检测和优化建议，请在生产环境中谨慎使用，并确保遵循相关安全策略。 