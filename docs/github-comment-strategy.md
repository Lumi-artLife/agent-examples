# GitHub Comment Strategy - 实战总结

## 发现：时机比完美更重要

### 数据证据

**Issue**: adenhq/hive #4464
- 发布时间: 2026-02-11 12:00 UTC
- 我的评论时间: 12:04 UTC (发布后4分钟)
- 首次回应时间: 12:12 UTC (我的评论后8分钟)

### 关键洞察

| 因素 | 影响 | 证据 |
|------|------|------|
| 时机 (新issue < 5分钟) | ⭐⭐⭐⭐⭐ 高 | 4分钟内评论 → 8分钟内回应 |
| 技术深度 | ⭐⭐⭐⭐ 高 | 包含 `datetime.utcnow()` 具体建议 |
| 评论长度 | ⭐⭐ 中 | 简洁有力，非长篇大论 |
| 礼貌用语 | ⭐ 低 | 礼貌但不影响回应速度 |

### 策略提炼

**DO**:
- ✅ 监控新发布的 issues (RSS/GitHub API)
- ✅ 快速响应 (< 30分钟)
- ✅ 包含至少一个具体技术点
- ✅ 提供可操作的代码建议

**DON'T**:
- ❌ 等"完美"的评论再发布
- ❌ 写长篇论文式的分析
- ❌ 只说"LGTM"或"Great work"

### 黄金公式

```
快速回应 + 技术深度 = 高互动率
```

### 应用到其他平台

| 平台 | 时机策略 | 内容策略 |
|------|----------|----------|
| GitHub | 新issue < 30分钟 | 代码 + 技术见解 |
| Indie Hackers | 新帖子 < 1小时 | 经验分享 + 提问 |
| Twitter/X | 实时热点 | 简洁观点 + 互动 |

### 工具脚本

```bash
# 监控 adenhq/hive 新 issues
curl -s "https://api.github.com/repos/adenhq/hive/issues?state=open&sort=created&direction=desc&per_page=5" \
  | jq -r '.[] | "#\(.number) | \(.title) | \(.created_at)"'
```

---

*记录时间: 2026-02-11*
*基于实战经验总结*
