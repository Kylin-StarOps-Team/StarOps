#!/usr/bin/env bash
#
# 系统综合修复策略：
# 1. 系统负载分析和进程清理
# 2. 系统服务状态检查和恢复
# 3. 系统资源综合优化
# 4. 上报系统修复结果
#

set -euo pipefail
LOAD_THRESHOLD=5.0     # 系统负载超过即触发
PUSH_URL="http://localhost:9090/metrics/job/system_autoheal"
CRITICAL_SERVICES=("sshd" "systemd-networkd" "cron")

log() { logger -t system_autoheal "$*"; echo "$(date): $*"; }

# 获取系统负载
get_load_average() {
    uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | tr -d ','
}

# 检查服务状态
check_service() {
    local service=$1
    systemctl is-active "$service" >/dev/null 2>&1
}

log "🔧 开始系统综合检查和修复..."

# 步骤 1: 系统负载检查
current_load=$(get_load_average)
if (( $(echo "$current_load > $LOAD_THRESHOLD" | bc -l) )); then
    log "⚠️ 系统负载过高: $current_load，开始负载优化..."
    
    # 查找负载高的进程
    log "🔍 分析高负载进程..."
    ps -eo pid,ppid,pcpu,pmem,stat,comm --sort=-pcpu | head -20 | while read -r pid ppid pcpu pmem stat comm; do
        if [[ "$pid" != "PID" ]] && (( $(echo "$pcpu > 10" | bc -l) )); then
            log "📊 高负载进程: PID=$pid CMD=$comm CPU=${pcpu}% MEM=${pmem}% STAT=$stat"
        fi
    done
    
    # 优化系统参数
    log "⚙️ 优化系统参数..."
    echo 3 > /proc/sys/vm/drop_caches  # 清理缓存
    sync
else
    log "💚 系统负载正常: $current_load"
fi

# 步骤 2: 关键服务检查
log "🔍 检查关键系统服务..."
failed_services=()
for service in "${CRITICAL_SERVICES[@]}"; do
    if ! check_service "$service"; then
        log "❌ 关键服务异常: $service"
        failed_services+=("$service")
        
        # 尝试重启服务
        log "🔧 尝试重启服务: $service"
        if systemctl restart "$service" 2>/dev/null; then
            sleep 3
            if check_service "$service"; then
                log "✅ 服务恢复成功: $service"
            else
                log "❌ 服务恢复失败: $service"
            fi
        fi
    else
        log "✅ 服务运行正常: $service"
    fi
done

# 步骤 3: 系统资源优化
log "🔧 执行系统资源优化..."

# 清理系统日志（保留最近7天）
if [[ -d /var/log ]]; then
    find /var/log -name "*.log" -type f -mtime +7 -delete 2>/dev/null || true
    find /var/log -name "*.log.*" -type f -mtime +7 -delete 2>/dev/null || true
    log "🧹 清理过期系统日志"
fi

# 清理临时文件
if [[ -d /tmp ]]; then
    find /tmp -type f -mtime +3 -delete 2>/dev/null || true
    log "🧹 清理临时文件"
fi

# 步骤 4: 系统进程优化
log "⚙️ 优化系统进程..."

# 查找僵尸进程
zombie_count=$(ps aux | awk '$8 ~ /^Z/ { count++ } END { print count+0 }')
if (( zombie_count > 0 )); then
    log "⚠️ 发现 $zombie_count 个僵尸进程"
    # 尝试清理僵尸进程（通过信号给父进程）
    ps -eo pid,ppid,stat,comm | awk '$3 ~ /^Z/ { print $2 }' | sort -u | while read -r ppid; do
        if kill -CHLD "$ppid" 2>/dev/null; then
            log "🧹 向父进程 $ppid 发送SIGCHLD信号清理僵尸进程"
        fi
    done
fi

# 步骤 5: 磁盘IO优化
log "💾 检查磁盘IO状态..."
io_wait=$(top -bn1 | grep "Cpu(s)" | awk '{print $10}' | awk -F'%' '{print $1}')
if (( $(echo "$io_wait > 20" | bc -l) )); then
    log "⚠️ 磁盘IO等待过高: ${io_wait}%"
    # 同步文件系统
    sync
    log "🔧 执行文件系统同步"
fi

# 步骤 6: 内存碎片整理
log "🧠 检查内存碎片..."
if [[ -f /proc/buddyinfo ]]; then
    # 触发内存压缩
    echo 1 > /proc/sys/vm/compact_memory 2>/dev/null || true
    log "🔧 执行内存碎片整理"
fi

# 最终系统状态检查
final_load=$(get_load_average)
uptime_info=$(uptime)
memory_info=$(free -h | grep Mem)

log "✅ 系统修复完成"
log "📊 最终状态 - 负载: $final_load，运行时间: $uptime_info"
log "💾 内存状态: $memory_info"

# 计算修复效果
load_improvement=$(echo "scale=2; $current_load - $final_load" | bc)
failed_services_count=${#failed_services[@]}

# 上报结果
curl -s --data-binary "system_autoheal_success 1
system_load $final_load
load_improvement $load_improvement
failed_services_count $failed_services_count
zombie_processes $zombie_count" "$PUSH_URL" || true

exit 0