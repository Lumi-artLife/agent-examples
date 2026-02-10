# HITL Approval Workflow Example

A production-ready Human-in-the-Loop (HITL) email approval system demonstrating all 5 input types.

## 🎯 Use Case

**Scenario**: Customer support agent drafts email responses, pauses for human approval before sending.

**Why This Matters**: Most teams won't deploy autonomous agents without approval gates. This example shows production-grade HITL implementation.

## 📋 HITL Input Types Demonstrated

1. **Free Text** - Open-ended feedback
2. **Structured Fields** - Form-like validation
3. **Selection List** - Approve/Reject/Modify options
4. **Approval Gate** - Binary yes/no with timeout
5. **Rich Content** - Attachments and formatting

## 🏗️ Architecture

```
┌─────────────────┐
│  Draft Email    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  HITL Pause     │ ← Human review point
│  (5 min timeout)│
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌───────┐ ┌─────────┐
│Approved│ │ Timeout │
└───┬───┘ └────┬────┘
    │          │
    ▼          ▼
┌───────┐ ┌─────────┐
│ Send  │ │ Escalate│
└───────┘ └─────────┘
```

## 🚀 Usage

```python
from hitl_approval_workflow import EmailApprovalAgent

# Initialize agent
agent = EmailApprovalAgent(
    timeout_minutes=5,
    escalation_email="manager@company.com"
)

# Draft and send for approval
result = agent.draft_and_send(
    customer_email="customer@example.com",
    subject="Issue Resolution",
    draft_content="Dear customer..."
)

# Handle human response
if result.status == "approved":
    print("Email sent successfully")
elif result.status == "rejected":
    print(f"Rejected with feedback: {result.feedback}")
elif result.status == "timeout":
    print("Approval timed out - escalated to manager")
```

## 📊 Configuration

```yaml
# config.yaml
hitl:
  timeout_minutes: 5
  escalation_enabled: true
  input_types:
    - free_text
    - structured_fields
    - selection_list
    - approval_gate
    - rich_content

notifications:
  slack_webhook: "${SLACK_WEBHOOK_URL}"
  email_enabled: true
```

## 🧪 Testing

```bash
# Run unit tests
pytest tests/

# Run integration test (requires Hive framework)
pytest tests/integration/ -v

# Test with mock HITL responses
python tests/test_with_mocks.py
```

## 🎓 Learning Points

### 1. Timeout Handling

```python
# What happens if human doesn't respond?
if elapsed_time > timeout:
    return EscalationResult(
        reason="timeout",
        original_task=task,
        fallback_action="notify_manager"
    )
```

### 2. Context Preservation

The agent maintains full context when escalating:
- Original draft content
- Customer history
- SLAs and urgency level
- Suggested modifications from human

### 3. Audit Trail

Every HITL interaction is logged:
```python
audit_log.record(
    event="hitl_response",
    user=human_user,
    decision=decision,
    timestamp=datetime.utcnow()
)
```

## 🔧 Customization

### Change Timeout Duration

```python
agent = EmailApprovalAgent(timeout_minutes=10)  # Longer for complex issues
```

### Add Custom Input Fields

```python
agent.add_input_field(
    name="priority",
    type="select",
    options=["low", "medium", "high", "urgent"]
)
```

### Modify Escalation Logic

```python
def custom_escalation(task, reason):
    if reason == "timeout" and task.urgency == "high":
        notify_slack("#urgent-approvals", task)
    else:
        notify_email("manager@company.com", task)

agent.set_escalation_handler(custom_escalation)
```

## 🚨 Error Handling

| Error | Handling |
|-------|----------|
| Invalid input | Re-prompt with validation message |
| Timeout | Escalate to manager |
| Service unavailable | Queue for retry |
| Human rejection | Log feedback and suggest alternatives |

## 📈 Production Considerations

- **Rate limiting**: Prevent spamming humans with too many approval requests
- **Batching**: Group similar approvals for efficiency
- **SLA monitoring**: Track approval times and escalate if SLAs breached
- **Analytics**: Measure approval rates and common rejection reasons

## 📝 Code Structure

```
hitl_approval_workflow/
├── __init__.py           # Package initialization
├── agent.py              # Main agent implementation
├── config.yaml           # Configuration
├── hitl_handler.py       # HITL interaction logic
├── email_service.py      # Email sending abstraction
├── models.py             # Data models
├── tests/
│   ├── test_agent.py
│   ├── test_hitl.py
│   └── test_integration.py
└── README.md             # This file
```

## 🔗 Integration with Hive

This example uses Hive's native HITL capabilities:

```python
from hive import Agent, HITLNode

class EmailApprovalAgent(Agent):
    def __init__(self):
        super().__init__()
        self.add_node(HITLNode(
            name="approval_gate",
            input_types=["text", "select", "approve"],
            timeout=timedelta(minutes=5)
        ))
```

## 📚 References

- [Hive HITL Documentation](https://docs.hive.com/hitl)
- [Related Hive Issue #4365](https://github.com/adenhq/hive/issues/4365) - Framework capability showcase
- [Related Hive Issue #4328](https://github.com/adenhq/hive/issues/4328) - Contract Evaluation Agent Template

---

**Status**: 🚧 In development  
**Last Updated**: 2026-02-10  
**Author**: Lumi
