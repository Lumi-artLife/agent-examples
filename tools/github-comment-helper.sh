#!/bin/bash
# GitHub Comment Optimizer - 基于数据验证的评论策略
# 用法: ./github-comment-helper.sh ISSUE_NUMBER

ISSUE=$1

if [ -z "$ISSUE" ]; then
    echo "Usage: $0 <issue_number>"
    echo ""
    echo "基于本周数据分析的最佳实践:"
    echo "  ✅ 发布后 5-10 分钟评论效果最佳"
    echo "  ✅ 代码/bug 类型 Issue 互动率更高"
    echo "  ✅ 具体代码建议 > 一般性反馈"
    exit 1
fi

# 获取 Issue 详情
echo "🔍 分析 Issue #$ISSUE..."
ISSUE_DATA=$(curl -s "https://api.github.com/repos/adenhq/hive/issues/$ISSUE")

TITLE=$(echo "$ISSUE_DATA" | jq -r '.title')
BODY=$(echo "$ISSUE_DATA" | jq -r '.body[0:200]')
CREATED=$(echo "$ISSUE_DATA" | jq -r '.created_at')
COMMENTS=$(echo "$ISSUE_DATA" | jq -r '.comments')
TYPE=$(echo "$ISSUE_DATA" | jq -r 'if .pull_request then "PR" else "Issue" end')
LABELS=$(echo "$ISSUE_DATA" | jq -r '.labels[].name' | tr '\n' ', ')

# 计算时间差
CREATED_EPOCH=$(date -j -f "%Y-%m-%dT%H:%M:%SZ" "$CREATED" "+%s" 2>/dev/null || date -d "$CREATED" "+%s")
NOW_EPOCH=$(date "+%s")
MINUTES_OLD=$(( (NOW_EPOCH - CREATED_EPOCH) / 60 ))

echo ""
echo "📊 Issue 分析"
echo "  标题: $TITLE"
echo "  类型: $TYPE"
echo "  标签: $LABELS"
echo "  创建: $CREATED ($MINUTES_OLD 分钟前)"
echo "  评论: $COMMENTS"
echo ""

# 评分系统
SCORE=0
REASON=""

# 时机评分 (基于数据分析)
if [ $MINUTES_OLD -ge 5 ] && [ $MINUTES_OLD -le 30 ]; then
    SCORE=$((SCORE + 40))
    REASON="$REASON✅ 时机优秀 (5-30分钟窗口)\n"
elif [ $MINUTES_OLD -lt 5 ]; then
    SCORE=$((SCORE + 20))
    REASON="$REASON⚠️  时机偏早 (建议等待至5分钟后)\n"
else
    SCORE=$((SCORE + 10))
    REASON="$REASON⚠️  时机偏晚 (热度可能下降)\n"
fi

# 类型评分
if echo "$LABELS" | grep -qi "bug\|fix"; then
    SCORE=$((SCORE + 30))
    REASON="$REASON✅ Bug/Fix 类型 - 高互动率\n"
elif echo "$LABELS" | grep -qi "enhancement\|feature"; then
    SCORE=$((SCORE + 20))
    REASON="$REASON✅ Feature 类型 - 中等互动率\n"
else
    SCORE=$((SCORE + 15))
    REASON="$REASON⚠️  其他类型\n"
fi

# 评论数评分
if [ "$COMMENTS" -eq 0 ]; then
    SCORE=$((SCORE + 30))
    REASON="$REASON✅ 0 评论 - 绝佳机会!\n"
elif [ "$COMMENTS" -lt 3 ]; then
    SCORE=$((SCORE + 20))
    REASON="$REASON✅ 较少评论 - 好机会\n"
else
    SCORE=$((SCORE + 5))
    REASON="$REASON⚠️  已有较多评论\n"
fi

echo "🎯 互动潜力评分: $SCORE/100"
echo ""
echo "$REASON"
echo ""

# 建议
if [ $SCORE -ge 80 ]; then
    echo "🟢 强烈推荐立即评论!"
    echo "   URL: https://github.com/adenhq/hive/issues/$ISSUE"
elif [ $SCORE -ge 60 ]; then
    echo "🟡 建议评论"
    echo "   URL: https://github.com/adenhq/hive/issues/$ISSUE"
else
    echo "🔴 优先级较低"
    echo "   建议寻找其他机会"
fi
