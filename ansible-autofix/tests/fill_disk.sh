#!/usr/bin/env bash
# 连续写入 100 MB 文件，直到磁盘剩余 <5% 就停止
while :; do
  avail=$(df --output=pcent / | tail -1 | tr -d ' %')
  (( avail <= 5 )) && break

  # 先生成文件名
  filename="/bigfile.$(date +%s)"
  # 写入 100MB
  dd if=/dev/zero of="$filename" bs=1M count=100 status=none

  # 获取文件大小（人类可读格式）
  size=$(du -h "$filename" | awk '{print $1}')
  # 输出文件路径和大小
  echo "Wrote file: $filename (size: $size)"

  sleep 1
done
#!/usr/bin/env bash
