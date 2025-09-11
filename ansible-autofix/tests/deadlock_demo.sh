#!/usr/bin/env bash
# 演示：打开 FIFO 管道后不读写 -> 进程卡在 D 状态
tmp=/tmp/lockfifo.$$
mkfifo "$tmp"
( exec 3<>"$tmp"; cat <&3 & );      # 子进程读 FIFO
sleep 1                             # 主进程未写，子进程阻塞
ps -o pid,state,comm,etime | grep cat
echo "现在 you can watch ps -eo state,pid,comm,etime | grep D"
echo "⚠️ 记得 pkill -f lockfifo 或 rm -f $tmp 清理"

