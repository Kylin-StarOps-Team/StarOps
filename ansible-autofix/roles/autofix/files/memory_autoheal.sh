#!/usr/bin/env bash
#
# 内存清理策略：
# 1. 清理系统页面缓存和缓冲区
# 2. 查找并终止内存占用过高的进程（保护系统进程）
# 3. 压缩Swap使用，释放物理内存
# 4. 上报内存清理结果到监控系统
#

set -euo pipefail
MEMORY_THRESHOLD=85    # %，内存使用率超过即触发清理
HIGH_MEM_PROCESS_THRESHOLD=20  # %，单进程内存占用超过即考虑终止
PUSH_URL="http://localhost:9090/metrics/job/memory_autoheal"
WHITELIST=("systemd" "kernel" "sshd" "docker" "kubelet")   # 进程白名单

log() { logger -t memory_autoheal "$*"; echo "$(date): $*"; }

# 获取当前内存使用率
get_memory_usage() {
    free | awk 'NR==2{printf "%.0f", $3*100/$2}'
}

mem_usage=$(get_memory_usage)

if (( mem_usage < MEMORY_THRESHOLD )); then
    log "💚 内存使用率 ${mem_usage}%，低于阈值 ${MEMORY_THRESHOLD}%，无需处理。"  
    exit 0
fi

log "🔥 内存使用率 ${mem_usage}%，开始内存清理。"

# 步骤 1: 清理系统缓存
log "🧹 清理系统页面缓存和缓冲区..."
sync
echo 3 > /proc/sys/vm/drop_caches

# 步骤 2: 查找并终止高内存占用进程
log "🔍 查找高内存占用进程..."
while read -r pid mem_percent cmd; do
    # 检查白名单
    skip=false
    for protected in "${WHITELIST[@]}"; do
        if [[ "$cmd" == *"$protected"* ]]; then
            skip=true
            break
        fi
    done
    
    if [[ "$skip" == "true" ]]; then
        log "⚪ 跳过受保护进程: $cmd (PID=$pid, MEM=${mem_percent}%)"
        continue
    fi
    
    if (( $(echo "$mem_percent > $HIGH_MEM_PROCESS_THRESHOLD" | bc -l) )); then
        log "⚠️ 发现高内存占用进程: $cmd (PID=$pid, MEM=${mem_percent}%)，准备终止"
        if kill -15 "$pid" 2>/dev/null; then
            sleep 3
            if kill -0 "$pid" 2>/dev/null; then
                kill -9 "$pid" 2>/dev/null && log "✅ 强制终止进程 $pid"
            else 
                log "✅ 优雅终止进程 $pid"
            fi
        fi
    fi
done < <(ps -eo pid,%mem,cmd --no-headers --sort=-%mem | head -20)

# 步骤 3: Swap优化
if [[ -f /proc/swaps ]] && grep -q "partition" /proc/swaps; then
    log "💾 优化Swap使用..."
    swapoff -a && swapon -a
fi

# 检查清理效果
after_mem_usage=$(get_memory_usage)
log "✅ 内存清理完成，使用率从 ${mem_usage}% 降至 ${after_mem_usage}%"

# 上报结果到监控系统
freed_memory=$((mem_usage - after_mem_usage))
curl -s --data-binary "memory_autoheal_success 1
memory_used_percent $after_mem_usage
memory_freed_percent $freed_memory" "$PUSH_URL" || true

exit 0