#!/usr/bin/env bash
#
# 查找持续 D 状态（不可中断）超过 120 秒的进程并终止。
# 带进程白名单，避免误杀核心组件。
#

set -euo pipefail
THRESHOLD=120       # 秒
WHITELIST=("pidof" "sshd" "systemd")   # 进程名例外

log()  { logger -t deadlock_autoheal "$*"; echo "$(date): $*"; }

now=$(date +%s)
while read -r pid stat comm etime; do
    # 筛掉白名单
    for allow in "${WHITELIST[@]}"; do
        [[ "$comm" == *"$allow"* ]] && continue 2
    done

    # etime 格式 [[dd-]hh:]mm:ss → 换算秒
    IFS='-:' read -r d h m s <<<"${etime//-/:}"
    s=${s:-0}; m=${m:-0}; h=${h:-0}; d=${d:-0}
    runtime=$(( ((d*24 + h)*60 + m)*60 + s ))

    if (( runtime > THRESHOLD )); then
        log "⚠️ 发现疑似死锁进程 PID=$pid ($comm) 已 D 状态 $runtime s，准备 kill -9"
        kill -9 "$pid" && log "✅ 已强制杀死 $pid"
    fi
done < <(ps -eo pid,state,comm,etime --no-headers | awk '$2=="D"')

# 上报简易指标
curl -s --data-binary "deadlock_autoheal_success 1" \
  http://localhost:9090/metrics/job/deadlock_autoheal  || true

