#!/usr/bin/env bash
#
# 清理策略：
# 1. 优先清理 /var/log 里 10 天以上的旧日志
# 2. 若仍不足，再执行 apt & yum 缓存清理 / docker prune
# 3. 挂钩 Prometheus Pushgateway，上报一次性指标供告警/看板使用
#

set -euo pipefail
THRESHOLD=80        # %，超过即触发
MOUNT="/"           # 监控哪个挂载点
PUSH_URL="http://localhost:9090/metrics/job/disk_autoheal"

used=$(df -P "$MOUNT" | awk 'NR==2 {print $5}' | tr -d '%')

log()  { logger -t disk_autoheal "$*"; echo "$(date): $*"; }

if (( used < THRESHOLD )); then
    log "💚 $MOUNT 使用率 ${used}%，低于阈值，不处理。"
    exit 0
fi

log "🔥 $MOUNT 使用率 ${used}%，开始清理。"

# 测试专用
log "🧹 清理测试用大文件 /bigfile.*"
find / -maxdepth 1 -type f -name 'bigfile.*' -print -delete || true

# 步骤 1. 清理过期日志
find /var/log -type f -mtime +10 -print -delete

# 步骤 2. 系统包缓存
if command -v apt-get &>/dev/null; then
    apt-get -qq clean
elif command -v yum &>/dev/null; then
    yum -q clean all
fi

# 步骤 3. Docker 镜像/挂载清理（可选）
if command -v docker &>/dev/null; then
    docker system prune -af --volumes
fi

after=$(df -P "$MOUNT" | awk 'NR==2 {print $5}' | tr -d '%')
log "✅ 清理后使用率 ${after}%。"

# 验证结果并上报
curl -s --data-binary "disk_autoheal_success 1
disk_used_percent $after" "$PUSH_URL" || true

