#!/usr/bin/env bash
#
# CPU负载修复策略：
# 1. 查找CPU占用过高的进程并优化
# 2. 终止长时间占用CPU的非关键进程
# 3. 调整进程优先级
# 4. 上报CPU修复结果
#

set -euo pipefail
CPU_THRESHOLD=80       # %，CPU使用率超过即触发
HIGH_CPU_PROCESS_THRESHOLD=50  # %，单进程CPU占用超过即考虑处理
PUSH_URL="http://localhost:9090/metrics/job/cpu_autoheal"
WHITELIST=("systemd" "kernel" "sshd" "docker" "kubelet" "prometheus" "node_exporter")

log() { logger -t cpu_autoheal "$*"; echo "$(date): $*"; }

# 获取当前CPU使用率
get_cpu_usage() {
    top -bn1 | grep "Cpu(s)" | awk '{print $2}' | awk -F'%' '{print $1}'
}

cpu_usage=$(get_cpu_usage)

if (( $(echo "$cpu_usage < $CPU_THRESHOLD" | bc -l) )); then
    log "💚 CPU使用率 ${cpu_usage}%，低于阈值 ${CPU_THRESHOLD}%，无需处理。"
    exit 0
fi

log "🔥 CPU使用率 ${cpu_usage}%，开始CPU负载优化。"

# 步骤 1: 查找高CPU占用进程
log "🔍 查找高CPU占用进程..."
while read -r pid cpu_percent cmd; do
    # 检查白名单  
    skip=false
    for protected in "${WHITELIST[@]}"; do
        if [[ "$cmd" == *"$protected"* ]]; then
            skip=true
            break
        fi
    done
    
    if [[ "$skip" == "true" ]]; then
        log "⚪ 跳过受保护进程: $cmd (PID=$pid, CPU=${cpu_percent}%)"
        continue
    fi
    
    if (( $(echo "$cpu_percent > $HIGH_CPU_PROCESS_THRESHOLD" | bc -l) )); then
        log "⚠️ 发现高CPU占用进程: $cmd (PID=$pid, CPU=${cpu_percent}%)"
        
        # 先尝试降低优先级
        if renice +10 "$pid" >/dev/null 2>&1; then
            log "⬇️ 已降低进程 $pid 优先级"
            sleep 5
            
            # 检查效果，如果仍然很高则考虑终止
            current_cpu=$(ps -p "$pid" -o %cpu --no-headers 2>/dev/null || echo "0")
            if (( $(echo "$current_cpu > $HIGH_CPU_PROCESS_THRESHOLD" | bc -l) )); then
                log "⚠️ 进程 $pid 优先级调整后仍占用 ${current_cpu}% CPU，准备终止"
                if kill -15 "$pid" 2>/dev/null; then
                    sleep 3
                    if kill -0 "$pid" 2>/dev/null; then
                        kill -9 "$pid" 2>/dev/null && log "✅ 强制终止进程 $pid"
                    else
                        log "✅ 优雅终止进程 $pid"
                    fi
                fi
            fi
        fi
    fi
done < <(ps -eo pid,%cpu,cmd --no-headers --sort=-%cpu | head -15)

# 步骤 2: 系统调优
log "⚙️ 执行系统CPU调优..."

# 调整调度器参数
echo 'performance' > /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor 2>/dev/null || true

# 检查修复效果
sleep 5
after_cpu_usage=$(get_cpu_usage)
log "✅ CPU负载优化完成，使用率从 ${cpu_usage}% 降至 ${after_cpu_usage}%"

# 上报结果
cpu_reduction=$(echo "$cpu_usage - $after_cpu_usage" | bc)
curl -s --data-binary "cpu_autoheal_success 1
cpu_used_percent $after_cpu_usage
cpu_reduction_percent $cpu_reduction" "$PUSH_URL" || true

exit 0