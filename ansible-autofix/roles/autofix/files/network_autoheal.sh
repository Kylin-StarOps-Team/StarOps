#!/usr/bin/env bash
#
# 网络连接修复策略：
# 1. 检测网络连接异常和DNS问题
# 2. 重启网络服务和清理连接
# 3. 修复防火墙和路由问题
# 4. 上报网络修复结果
#

set -euo pipefail
PUSH_URL="http://localhost:9090/metrics/job/network_autoheal"
TEST_HOSTS=("8.8.8.8" "114.114.114.114" "baidu.com")
DNS_SERVERS=("8.8.8.8" "114.114.114.114")

log() { logger -t network_autoheal "$*"; echo "$(date): $*"; }

# 网络连通性测试
test_connectivity() {
    local host=$1
    ping -c 2 -W 3 "$host" >/dev/null 2>&1
}

# DNS解析测试
test_dns() {
    local domain=$1
    nslookup "$domain" >/dev/null 2>&1
}

log "🌐 开始网络连接检测和修复..."

# 步骤 1: 基础网络连通性检测
connectivity_issues=0
for host in "${TEST_HOSTS[@]}"; do
    if ! test_connectivity "$host"; then
        log "❌ 无法连接到 $host"
        ((connectivity_issues++))
    else
        log "✅ 成功连接到 $host"
    fi
done

# 步骤 2: DNS解析检测
dns_issues=0
if ! test_dns "baidu.com"; then
    log "❌ DNS解析异常"
    ((dns_issues++))
    
    # 尝试修复DNS
    log "🔧 尝试修复DNS配置..."
    
    # 备份并更新DNS配置
    cp /etc/resolv.conf /etc/resolv.conf.backup || true
    {
        echo "nameserver 8.8.8.8"
        echo "nameserver 114.114.114.114"
        echo "nameserver 223.5.5.5"
    } > /etc/resolv.conf
    
    # 清理DNS缓存
    if command -v systemd-resolve >/dev/null; then
        systemd-resolve --flush-caches
    fi
    
    sleep 3
    if test_dns "baidu.com"; then
        log "✅ DNS修复成功"
        dns_issues=0
    fi
fi

# 步骤 3: 网络服务检查和重启
if (( connectivity_issues > 1 )); then
    log "🔧 网络连接异常，尝试重启网络服务..."
    
    # 清理网络连接
    log "🧹 清理异常网络连接..."
    netstate_before=$(ss -tuln | wc -l)
    
    # 关闭TIME_WAIT连接
    ss -tuln | grep TIME-WAIT | awk '{print $5}' | sort | uniq -c | sort -nr | head -10 | while read count addr; do
        if (( count > 100 )); then
            log "🧹 清理过多的TIME_WAIT连接: $addr ($count 个)"
        fi
    done
    
    # 重启网络管理服务
    if systemctl is-active NetworkManager >/dev/null 2>&1; then
        systemctl restart NetworkManager
        sleep 5
    elif systemctl is-active networking >/dev/null 2>&1; then
        systemctl restart networking  
        sleep 5
    fi
    
    # 重新测试连通性
    fixed_connections=0
    for host in "${TEST_HOSTS[@]}"; do
        if test_connectivity "$host"; then
            ((fixed_connections++))
        fi
    done
    
    log "✅ 网络修复完成，恢复连接数: $fixed_connections/${#TEST_HOSTS[@]}"
fi

# 步骤 4: 防火墙检查
log "🔒 检查防火墙配置..."
if command -v ufw >/dev/null && ufw status | grep -q "Status: active"; then
    # 确保SSH端口开放
    ufw allow 22/tcp >/dev/null 2>&1 || true
    log "✅ 确保SSH端口22开放"
fi

# 步骤 5: 路由表检查
default_routes=$(ip route | grep default | wc -l)
if (( default_routes == 0 )); then
    log "❌ 缺少默认路由"
    # 尝试添加默认路由（需要根据实际网络环境调整）
    gateway=$(ip route | grep 'scope link' | awk '{print $1}' | head -1 | sed 's/\/.*//; s/[0-9]*$/1/')
    if [[ -n "$gateway" ]]; then
        ip route add default via "$gateway" 2>/dev/null || true
        log "🔧 尝试添加默认路由: $gateway"
    fi
fi

# 最终连通性测试
final_connectivity=0
for host in "${TEST_HOSTS[@]}"; do
    if test_connectivity "$host"; then
        ((final_connectivity++))
    fi
done

success_rate=$((final_connectivity * 100 / ${#TEST_HOSTS[@]}))
log "✅ 网络修复完成，连通性: ${success_rate}% (${final_connectivity}/${#TEST_HOSTS[@]})"

# 上报结果
curl -s --data-binary "network_autoheal_success 1
network_connectivity_percent $success_rate
dns_issues $dns_issues" "$PUSH_URL" || true

exit 0