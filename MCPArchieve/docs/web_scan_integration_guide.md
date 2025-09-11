# Web配置检测集成使用指南

## 概述

本指南介绍如何在fletMCP应用中集成Web配置检测功能，实现通过自然语言查询自动调用web_config_check模块进行网站配置分析和安全检测。

## 功能特性

### 🔍 智能识别
- 自动识别用户查询中的网站配置检测需求
- 支持多种自然语言表达方式
- 自动提取目标URL
- 智能选择检测模式

### 🎯 检测模式
- **完整检测 (full)**: 全面分析网站配置、安全、性能
- **快速检测 (quick)**: 基础配置检查，适合快速评估
- **安全专项 (security)**: 专注于安全配置和漏洞检测
- **性能专项 (performance)**: 专注于性能优化和Lighthouse审计

### 📊 检测内容
- HTTP安全头配置
- SSL/TLS证书状态
- 网站性能指标
- 服务器配置优化
- 安全漏洞扫描
- 最佳实践检查

## 使用方法

### 1. 基本查询

用户可以通过以下自然语言方式查询：

```
"请检查网站 https://www.example.com 的配置"
"扫描 https://www.google.com 的安全漏洞"
"分析 https://www.github.com 的性能问题"
"快速检查网站配置"
"检查HTTP安全头配置"
"网站SSL证书有问题吗？"
"这个网站加载速度怎么样？"
"帮我优化网站性能"
```

### 2. 检测模式选择

系统会根据用户查询自动选择合适的检测模式：

- **提到"安全"、"漏洞"、"SSL"等**: 自动选择security模式
- **提到"性能"、"速度"、"优化"等**: 自动选择performance模式
- **提到"快速"、"简单"等**: 自动选择quick模式
- **其他情况**: 默认使用full模式

### 3. URL提取

系统支持多种URL格式：

- 完整URL: `https://www.example.com`
- 带路径URL: `https://www.example.com/path`
- 域名: `www.example.com` (自动添加https://)
- 从文本中提取: 在自然语言中嵌入URL

## 技术实现

### 1. MCP协议集成

WebScanProtocol已集成到MCP协议系统中：

```python
[MCP_CALL]{"protocol":"WebScanProtocol","params":{"url":"目标URL","mode":"检测模式"}}[/MCP_CALL]
```

### 2. AI模型提示词

系统提示词已更新，支持8种专业监控协议：

```python
8. 当用户询问Web应用配置、网站安全、网站性能、HTTP安全头、SSL配置、网站优化等相关问题时，生成Web配置检测MCP调用指令：
   - 网站配置检测: 当用户提到"检查网站"、"网站配置"、"Web配置"、"网站安全"、"网站性能"等时，提取URL并生成：
     [MCP_CALL]{"protocol":"WebScanProtocol","params":{"url":"目标URL","mode":"full"}}[/MCP_CALL]
   - 快速检测: 当用户提到"快速检查"、"简单检测"、"快速扫描"等时，生成：
     [MCP_CALL]{"protocol":"WebScanProtocol","params":{"url":"目标URL","mode":"quick"}}[/MCP_CALL]
   - 安全专项检查: 当用户提到"安全检查"、"安全漏洞"、"HTTP安全头"、"SSL证书"等时，生成：
     [MCP_CALL]{"protocol":"WebScanProtocol","params":{"url":"目标URL","mode":"security"}}[/MCP_CALL]
   - 性能专项检查: 当用户提到"性能优化"、"网站速度"、"加载速度"、"Lighthouse"等时，生成：
     [MCP_CALL]{"protocol":"WebScanProtocol","params":{"url":"目标URL","mode":"performance"}}[/MCP_CALL]
   - 从文本提取URL: 当用户提到网站但未明确URL时，从对话中提取URL：
     [MCP_CALL]{"protocol":"WebScanProtocol","params":{"text":"用户原始描述","mode":"full"}}[/MCP_CALL]
```

### 3. 模块路径配置

系统自动处理web_config_check模块的路径配置：

```python
# 从MCPArchieve目录向上两级到根目录，然后找到web_config_check
current_dir = os.path.dirname(__file__)  # core/
mcp_dir = os.path.dirname(current_dir)   # MCPArchieve/
root_dir = os.path.dirname(mcp_dir)      # 根目录
web_config_check_path = os.path.join(root_dir, 'web_config_check')
```

## 测试验证

### 1. 运行测试脚本

```bash
cd MCPArchieve
python3 test_web_scan_integration.py
```

### 2. 测试内容

测试脚本包含以下验证：

- **WebScanProtocol基本功能测试**
  - 完整扫描测试
  - 快速扫描测试
  - 安全专项测试
  - 性能专项测试
  - 文本提取URL测试

- **SmartMonitor集成测试**
  - MCP协议调用验证
  - 参数传递验证
  - 结果分析验证

- **自然语言查询识别测试**
  - 各种自然语言表达方式
  - URL提取功能
  - 检测模式自动选择

### 3. 预期结果

成功集成后，用户应该能够：

1. 通过自然语言查询触发Web配置检测
2. 系统自动识别并调用WebScanProtocol
3. 获得详细的配置分析报告
4. 查看安全评分和性能评分
5. 获得具体的优化建议

## 故障排除

### 1. 模块导入错误

如果遇到 `No module named 'web_config_collector'` 错误：

- 检查web_config_check目录是否存在
- 确认目录结构正确
- 验证Python路径配置

### 2. API调用失败

如果AI模型调用失败：

- 检查API密钥配置
- 确认网络连接正常
- 验证API服务可用性

### 3. 检测结果异常

如果检测结果不符合预期：

- 检查目标网站可访问性
- 确认网络连接正常
- 验证检测参数配置

## 最佳实践

### 1. 查询建议

- 使用清晰、具体的描述
- 明确指定目标URL
- 说明具体的检测需求

### 2. 结果解读

- 关注安全评分和性能评分
- 优先处理严重和高危问题
- 参考优化建议进行改进

### 3. 定期检测

- 建议定期进行网站配置检测
- 监控配置变化对安全性能的影响
- 建立配置管理最佳实践

## 更新日志

### v1.0.0 (2024-08-04)
- 初始版本发布
- 集成WebScanProtocol到MCP系统
- 更新AI模型提示词
- 添加自然语言查询支持
- 创建测试验证脚本

## 技术支持

如有问题或建议，请：

1. 查看测试日志输出
2. 检查错误信息详情
3. 验证环境配置
4. 参考故障排除指南

---

*本指南将随着功能更新持续完善* 