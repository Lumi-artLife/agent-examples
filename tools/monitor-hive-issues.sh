#!/bin/bash
# GitHub Issue Monitor - 新 Issue 自动检测
# 用法: ./monitor-hive-issues.sh

REPO="adenhq/hive"
INTERVAL="300"  # 5分钟检查一次
SEEN_FILE="$HOME/.hive_issues_seen"

# 初始化 seen 文件
touch "$SEEN_FILE"

echo "🔍 监控 $REPO 的新 Issues..."
echo "按 Ctrl+C 停止"
echo ""

while true; do
    # 获取最新 5 个 open issues
    curl -s "https://api.github.com/repos/$REPO/issues?state=open\u0026sort=created\u0026direction=desc\u0026per_page=5" | \
    jq -r '.[] | "\(.number)|\(.title)|\(.created_at)|\(.comments)|\(.user.login)"' 2>/dev/null | \
    while IFS='|' read -r number title created comments author; do
        # 检查是否已看过
        if ! grep -q "^$number$" "$SEEN_FILE"; then
            # 标记为已看
            echo "$number" >> "$SEEN_FILE"
            
            # 只显示 0 评论的 issues（机会！）
            if [ "$comments" -eq 0 ]; then
                echo "🎯 新机会! Issue #$number"
                echo "   标题: $title"
                echo "   作者: $author"
                echo "   时间: $created"
                echo "   URL:  https://github.com/$REPO/issues/$number"
                echo ""
            fi
        fi
    done
    
    sleep $INTERVAL
done
