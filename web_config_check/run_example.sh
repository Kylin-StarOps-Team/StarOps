#!/bin/bash

# Web应用配置优化检测示例运行脚本

set -e

echo "=========================================="
echo "Web应用配置优化检测系统 - 示例运行"
echo "=========================================="

# 检查Python环境
echo "检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python 3.8+"
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "Python版本: $PYTHON_VERSION"

# 检查依赖
echo "检查依赖..."
if [ ! -f "requirements.txt" ]; then
    echo "错误: 未找到requirements.txt文件"
    exit 1
fi

# 安装依赖
echo "安装Python依赖..."
pip3 install -r requirements.txt

# 检查Lighthouse
echo "检查Lighthouse..."
if ! command -v lighthouse &> /dev/null; then
    echo "警告: 未找到Lighthouse，性能检测功能将受限"
    echo "建议安装: npm install -g lighthouse"
else
    echo "Lighthouse已安装"
fi

# 创建输出目录
echo "创建输出目录..."
mkdir -p reports

# 启动示例Web应用（如果不存在）
if [ ! -d "web-content" ]; then
    echo "创建示例Web应用..."
    mkdir -p web-content
    cat > web-content/index.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>示例Web应用</title>
    <meta charset="UTF-8">
</head>
<body>
    <h1>Web应用配置优化检测示例</h1>
    <p>这是一个用于测试的示例Web应用。</p>
    <p>当前时间: <span id="time"></span></p>
    <script>
        document.getElementById('time').textContent = new Date().toLocaleString();
    </script>
</body>
</html>
EOF
fi

# 启动Nginx容器作为示例Web应用
echo "启动示例Web应用..."
if ! docker ps | grep -q web-app-demo; then
    docker run -d --name web-app-demo -p 8080:80 -v $(pwd)/web-content:/usr/share/nginx/html nginx:alpine
    echo "等待Web应用启动..."
    sleep 5
else
    echo "Web应用已在运行"
fi

# 运行检测
echo "开始运行Web应用配置优化检测..."

# 1. 快速检测
echo "1. 运行快速检测..."
python3 main.py --url http://localhost:8080 --mode quick --output-dir reports

# 2. 安全专项检查
echo "2. 运行安全专项检查..."
python3 main.py --url http://localhost:8080 --mode security --output-dir reports

# 3. 性能专项检查
echo "3. 运行性能专项检查..."
python3 main.py --url http://localhost:8080 --mode performance --output-dir reports

# 4. 完整检测
echo "4. 运行完整检测..."
python3 main.py --url http://localhost:8080 --mode full --output-dir reports

echo "=========================================="
echo "检测完成！"
echo "=========================================="

# 显示生成的文件
echo "生成的文件:"
ls -la reports/

# 显示HTML报告位置
HTML_REPORT=$(find reports -name "*.html" | head -1)
if [ -n "$HTML_REPORT" ]; then
    echo ""
    echo "HTML报告位置: $HTML_REPORT"
    echo "可以使用浏览器打开查看详细报告"
fi

# 显示Markdown报告位置
MD_REPORT=$(find reports -name "*.md" | head -1)
if [ -n "$MD_REPORT" ]; then
    echo "Markdown报告位置: $MD_REPORT"
fi

echo ""
echo "示例运行完成！"
echo "==========================================" 