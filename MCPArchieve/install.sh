
# MCPArchieve 智能系统监控助手 - 自动化安装脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检测操作系统
detect_os() {
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        OS=$NAME
    elif type lsb_release >/dev/null 2>&1; then
        OS=$(lsb_release -si)
    else
        OS=$(uname -s)
    fi
    log_info "检测到操作系统: $OS"
}

# 安装系统依赖
install_system_deps() {
    log_info "安装系统依赖..."
    
    if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
        sudo apt update
        sudo apt install -y python3 python3-pip python3-venv git curl wget
        sudo apt install -y build-essential libssl-dev libffi-dev python3-dev
    elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]]; then
        sudo yum update -y
        sudo yum install -y python3 python3-pip git curl wget
        sudo yum groupinstall -y "Development Tools"
        sudo yum install -y openssl-devel libffi-devel python3-devel
    elif [[ "$OS" == *"Darwin"* ]]; then
        if ! command -v brew &> /dev/null; then
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        fi
        brew install python3 git curl wget
    fi
}

# 检查Python版本
check_python() {
    if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 7) else 1)"; then
        log_error "Python版本过低，需要3.7+"
        exit 1
    fi
    log_success "Python版本检查通过"
}

# 创建虚拟环境
setup_venv() {
    log_info "创建Python虚拟环境..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip setuptools wheel
}

# 安装Python依赖
install_python_deps() {
    log_info "安装Python依赖..."
    pip install -r requirements_flet.txt
    
    read -p "是否安装PyQt悬浮球版本? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pip install -r requirements_pyqt.txt
    fi
}

# 安装Trivy
install_trivy() {
    log_info "安装Trivy安全扫描工具..."
    
    if command -v trivy &> /dev/null; then
        log_warning "Trivy已安装"
        return
    fi
    
    if [[ "$OS" == *"Darwin"* ]]; then
        brew install trivy
    else
        LATEST_VERSION=$(curl -sL https://api.github.com/repos/aquasecurity/trivy/releases/latest | grep tag_name | cut -d '"' -f 4)
        wget https://github.com/aquasecurity/trivy/releases/download/${LATEST_VERSION}/trivy_${LATEST_VERSION#v}_Linux-64bit.tar.gz
        tar -xzf trivy_*.tar.gz
        sudo install trivy /usr/local/bin/
        rm trivy_*.tar.gz
    fi
    
    echo 'export TRIVY_DB_REPOSITORY=ghcr.nju.edu.cn/aquasecurity/trivy-db' >> ~/.bashrc
    trivy image --download-db-only
}

# 创建配置文件
create_config() {
    log_info "创建配置文件..."
    cat > config.json << EOF
{
  "api_key": "your-openai-api-key-here",
  "prometheus_url": "http://localhost:9090",
  "max_history_length": 20,
  "ui": {
    "window_width": 1200,
    "window_height": 800,
    "font_family": "Microsoft YaHei",
    "font_size": 12
  }
}
EOF
}

# 创建日志文件
setup_logs() {
    log_info "创建监控日志文件..."
    sudo mkdir -p /var/log/monitoring
    
    sudo tee /var/log/node_exporter_metrics.log > /dev/null << EOF
# HELP node_cpu_seconds_total Seconds the CPUs spent in each mode.
node_cpu_seconds_total{cpu="0",mode="idle"} 123456.78
node_cpu_seconds_total{cpu="0",mode="user"} 12345.67
EOF

    sudo chmod 644 /var/log/monitoring/*.log
}

# 验证安装
verify_installation() {
    log_info "验证安装..."
    python3 -c "import flet, requests, psutil; print('✅ Python依赖检查通过')"
    
    if command -v trivy &> /dev/null; then
        log_success "✅ Trivy检查通过"
    fi
    
    if [[ -f "config.json" ]]; then
        log_success "✅ 配置文件检查通过"
    fi
}

# 显示使用说明
show_usage() {
    echo
    echo "🎉 MCPArchieve 安装完成!"
    echo "================================"
    echo "📋 下一步操作:"
    echo "1. 编辑 config.json 文件，配置您的API密钥"
    echo "2. 运行: python3 run.py"
    echo
    echo "🚀 启动方式:"
    echo "• 智能启动: python3 run.py"
    echo "• Flet应用: python3 run_flet_app.py"
    echo "• PyQt悬浮球: python3 run_floating_ball.py"
    echo "• 命令行: python3 apps/cli_app.py"
    echo
    echo "📚 文档: INSTALLATION_GUIDE.md"
}

# 主函数
main() {
    echo "🚀 MCPArchieve 智能系统监控助手 - 自动化安装脚本"
    echo "=================================================="
    
    detect_os
    install_system_deps
    check_python
    setup_venv
    install_python_deps
    install_trivy
    create_config
    setup_logs
    verify_installation
    show_usage
}

main "$@"
#!/bin/bash

