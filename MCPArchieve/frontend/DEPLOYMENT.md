# StarOps Desktop 部署指南

## 环境要求

### 基础要求
- Linux 操作系统 (Ubuntu 18.04+, CentOS 7+, 或其他主流发行版)
- Node.js 16.0 或更高版本
- npm 或 yarn 包管理器
- X11 图形界面环境 (必需)
- Python 3.8+ (用于AI后端功能)

### 系统包依赖
在某些Linux发行版上，可能需要安装额外的系统包：

```bash
# Ubuntu/Debian
sudo apt-get install -y libnss3-dev libatk-bridge2.0-dev libdrm2 libxkbcommon0 libxss1 libgconf-2-4 libxrandr2 libxcomposite1 libxdamage1 libxfixes3

# CentOS/RHEL
sudo yum install -y atk gtk3 libXScrnSaver nss
```

## 部署步骤

### 1. 下载和安装依赖

```bash
# 克隆或复制项目文件到目标目录
cd /path/to/MCPArchieve/frontend

# 安装Node.js依赖
npm install

# 验证安装
npm list
```

### 2. 配置权限

```bash
# 给启动脚本添加执行权限
chmod +x start.sh

# 如果需要创建桌面快捷方式
cp starops.desktop ~/Desktop/
chmod +x ~/Desktop/starops.desktop
```

### 3. 环境变量配置

确保Python后端可以正常访问：

```bash
# 验证Python环境
python3 --version
python3 -c "import sys; print(sys.path)"

# 确保StarOps后端模块可用
cd ../  # 回到MCPArchieve根目录
python3 -c "from core.smart_monitor import SmartMonitor; print('✅ 后端模块加载成功')"
```

### 4. 启动应用

```bash
# 方式1: 使用启动脚本（推荐）
./start.sh

# 方式2: 直接使用npm
npm start

# 方式3: 开发模式（包含调试信息）
npm run dev
```

## 部署验证

### 检查应用是否正常启动

1. **悬浮球出现**: 应用启动后应在屏幕右上角看到蓝紫色渐变的圆形悬浮球，上面显示"StarOps"
2. **悬浮球功能**: 悬浮球应该可以拖拽移动，双击应该能打开主界面
3. **主界面**: 主界面应显示三个标签页：AI对话、Web检测报告、MySQL优化报告
4. **AI功能**: 在AI对话界面输入测试问题，应该能看到分析过程和响应

### 功能测试

```bash
# 测试AI对话功能
输入: "系统状态如何？"
预期: 应显示分析过程并尝试调用监控协议

# 测试报告查看功能
切换到报告标签页，应能看到现有报告列表
```

## 故障排除

### 常见问题和解决方案

#### 1. 应用无法启动 - X11显示错误
**错误**: `Missing X server or $DISPLAY`

**解决方案**:
```bash
# 确认X11服务正在运行
echo $DISPLAY
# 应输出类似 :0 或 :1

# 如果为空，尝试设置
export DISPLAY=:0

# 测试X11是否工作
xeyes &  # 应显示一个眼睛跟踪鼠标的窗口
```

#### 2. 权限错误
**错误**: `Running as root without --no-sandbox is not supported`

**解决方案**: 已在package.json中添加--no-sandbox标志，如果仍有问题：
```bash
# 使用非root用户运行
su - normaluser
cd /path/to/frontend
npm start
```

#### 3. Python后端调用失败
**错误**: AI功能无响应或报错

**解决方案**:
```bash
# 检查Python路径
which python3

# 验证模块导入
cd ../  # 回到MCPArchieve根目录
python3 -c "
import sys
sys.path.insert(0, '.')
from core.smart_monitor import SmartMonitor
print('后端模块正常')
"

# 检查配置文件
ls -la utils/config.py
python3 -c "from utils.config import Config; c=Config(); print('API Key配置:', '已配置' if c.api_key else '未配置')"
```

#### 4. 报告查看功能异常
**错误**: 报告列表为空或无法打开

**解决方案**:
```bash
# 检查报告目录
ls -la ../reports/
ls -la ../mysql_report/

# 确认报告文件权限
chmod 644 ../reports/*.html
chmod 644 ../mysql_report/*.html
```

#### 5. 依赖包安装失败
**错误**: npm install 失败

**解决方案**:
```bash
# 清理缓存
npm cache clean --force

# 删除node_modules重新安装
rm -rf node_modules package-lock.json
npm install

# 或使用yarn替代
npm install -g yarn
yarn install
```

## 性能优化

### 建议配置

1. **内存**: 建议至少2GB可用内存
2. **存储**: 预留至少500MB磁盘空间
3. **网络**: 确保AI API访问网络畅通

### 系统优化

```bash
# 提高文件描述符限制
ulimit -n 8192

# 对于大量报告文件的情况，可以配置logrotate
echo "/path/to/reports/*.html {
    size 100M
    rotate 10
    compress
    delaycompress
    missingok
    notifempty
}" | sudo tee /etc/logrotate.d/starops
```

## 生产环境部署

### 自启动配置

创建systemd服务文件：

```bash
sudo tee /etc/systemd/system/starops.service << EOF
[Unit]
Description=StarOps AI Desktop Application
After=graphical-session.target

[Service]
Type=simple
User=starops  # 替换为实际用户名
WorkingDirectory=/path/to/MCPArchieve/frontend
ExecStart=/path/to/MCPArchieve/frontend/start.sh
Restart=on-failure
Environment=DISPLAY=:0

[Install]
WantedBy=graphical-session.target
EOF

# 启用服务
sudo systemctl enable starops.service
sudo systemctl start starops.service
```

### 安全考虑

1. **运行用户**: 不要使用root用户运行应用
2. **文件权限**: 确保配置文件权限正确(600或644)
3. **网络访问**: 限制API访问来源
4. **日志管理**: 定期清理应用日志

## 更新和维护

### 更新应用

```bash
# 备份配置
cp -r /path/to/MCPArchieve/frontend /path/to/backup/

# 更新代码
git pull  # 或重新部署文件

# 更新依赖
npm install

# 重启应用
./start.sh
```

### 监控和日志

```bash
# 查看应用日志
journalctl -u starops.service -f

# 监控进程
ps aux | grep electron

# 监控资源使用
top -p $(pgrep -f "electron.*starops")
```
