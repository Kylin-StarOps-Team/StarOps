# StarOps 故障排除指南

## 🚨 常见启动错误和解决方案

### 错误1: X11授权问题
```
Authorization required, but no authorization protocol specified
```

**原因**: 使用sudo运行应用导致X11显示权限冲突

**解决方案**:
```bash
# 方案1: 使用普通用户运行（推荐）
su - denerate  # 切换到普通用户
cd /home/denerate/MCPArchieve/frontend
./start.sh

# 方案2: 如果必须使用root，需要设置X11权限
xhost +local:root  # 允许root用户访问X11（不安全，不推荐）
```

### 错误2: GPU渲染库权限问题
```
Failed to load GLES library: Permission denied
```

**原因**: 硬件加速库访问权限不足

**解决方案**: 已在新版本中通过添加`--disable-gpu`参数禁用硬件加速

### 错误3: DBus连接失败
```
Failed to connect to the bus: Could not parse server address
```

**原因**: 系统总线服务不可用或权限问题

**解决方案**: 这个错误通常不影响应用运行，已通过启动参数优化

## 🔧 正确的启动方式

### 1. 使用普通用户（推荐）

```bash
# 切换到普通用户
su - denerate

# 进入应用目录
cd /home/denerate/MCPArchieve/frontend

# 启动应用
./start.sh          # 生产模式
./start.sh dev      # 开发模式（带调试信息）
```

### 2. 环境检查

运行启动脚本前，确保：

```bash
# 检查X11显示
echo $DISPLAY  # 应输出 :0 或类似值
xset q         # 测试X11连接

# 检查用户权限
whoami         # 确认当前用户

# 检查文件权限
ls -la /home/denerate/MCPArchieve/frontend/
```

## 🛠 已优化的启动参数

新版本已添加以下启动参数来解决常见问题：

- `--no-sandbox`: 禁用沙箱，解决权限问题
- `--disable-gpu`: 禁用GPU硬件加速，避免库文件权限问题
- `--disable-dev-shm-usage`: 禁用共享内存，提高兼容性
- `--disable-setuid-sandbox`: 禁用setuid沙箱，解决权限冲突

## 🔍 环境诊断

### 检查命令

```bash
# 1. 检查Node.js环境
node --version
npm --version

# 2. 检查X11环境
echo $DISPLAY
xeyes &  # 应显示眼睛窗口，如果显示说明X11正常

# 3. 检查Python环境
python3 --version
python3 -c "import sys; print('Python路径:', sys.executable)"

# 4. 检查用户权限
whoami
id

# 5. 检查应用文件
ls -la /home/denerate/MCPArchieve/frontend/
```

### 常见环境问题

**问题**: 远程SSH连接无法显示图形界面
```bash
# 解决方案: 启用X11转发
ssh -X username@hostname
# 或
ssh -Y username@hostname  # 信任的X11转发
```

**问题**: DISPLAY变量未设置
```bash
# 解决方案: 设置显示变量
export DISPLAY=:0
```

**问题**: 权限被拒绝
```bash
# 解决方案: 检查文件权限
sudo chown -R denerate:denerate /home/denerate/MCPArchieve/frontend/
chmod +x /home/denerate/MCPArchieve/frontend/start.sh
```

## 📋 启动检查清单

在启动应用前，请确认：

- [ ] ✅ 使用普通用户（非root）
- [ ] ✅ DISPLAY环境变量已设置
- [ ] ✅ X11显示服务正常
- [ ] ✅ Node.js和npm已安装
- [ ] ✅ 应用文件权限正确
- [ ] ✅ 依赖包已安装（node_modules存在）

## 🚀 推荐启动流程

```bash
# 1. 切换到正确用户
su - denerate

# 2. 进入应用目录
cd /home/denerate/MCPArchieve/frontend

# 3. 检查环境
echo "DISPLAY: $DISPLAY"
echo "用户: $(whoami)"
echo "X11测试: $(timeout 3 xset q &>/dev/null && echo '正常' || echo '异常')"

# 4. 启动应用
./start.sh
```

## 💡 性能优化建议

### 对于服务器环境
```bash
# 如果是无头服务器，可以使用虚拟显示
sudo apt-get install xvfb
export DISPLAY=:99
Xvfb :99 -screen 0 1024x768x24 &
```

### 对于低配置机器
```bash
# 增加启动参数以减少资源使用
export ELECTRON_EXTRA_ARGS="--disable-background-timer-throttling --disable-renderer-backgrounding"
```

## 🔧 故障恢复

如果应用完全无法启动：

1. **重新安装依赖**
   ```bash
   cd /home/denerate/MCPArchieve/frontend
   rm -rf node_modules package-lock.json
   npm install
   ```

2. **检查系统依赖**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install libnss3-dev libatk-bridge2.0-dev libdrm2 libxkbcommon0 libxss1 libgconf-2-4 libxrandr2 libxcomposite1 libxdamage1 libxfixes3
   ```

3. **重置权限**
   ```bash
   sudo chown -R denerate:denerate /home/denerate/MCPArchieve/
   chmod +x /home/denerate/MCPArchieve/frontend/start.sh
   ```

## 📞 获取帮助

如果以上方案都无法解决问题：

1. 收集详细错误信息：
   ```bash
   ./start.sh dev 2>&1 | tee starops-error.log
   ```

2. 检查系统环境：
   ```bash
   uname -a
   cat /etc/os-release
   echo $DESKTOP_SESSION
   ```

3. 提供完整的错误日志和系统信息以获取技术支持。
