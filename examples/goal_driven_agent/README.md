# Goal-Driven Agent

An agent that operates based on declarative goals with weighted success criteria and constraints.

## 🎯 Use Case

**Scenario**: An AI agent needs to optimize for multiple objectives while respecting boundaries.

**Example**: "Optimize customer support with:
- Response time < 2 seconds (40% priority)
- Cost < $5 per ticket (30% priority)  
- Satisfaction score > 4.5/5 (30% priority)
- Hard constraint: Monthly budget < $1000"

**Challenge**: 
- Multiple competing objectives
- Different priorities
- Hard limits that must not be exceeded
- Need to track progress

**Solution**: Declarative goal specification with weighted criteria and constraint checking.

## 🏗️ Architecture

### Goal Structure

```python
Goal
├── id: str
├── description: str
├── success_criteria: List[SuccessCriterion]
│   ├── name
│   ├── target_value
│   ├── current_value
│   └── weight (0.0 - 1.0)
├── constraints: List[Constraint]
│   ├── name
│   ├── limit
│   ├── current
│   └── type (HARD/SOFT)
└── status: PENDING/IN_PROGRESS/ACHIEVED/FAILED
```

### Agent Behavior

```
┌──────────────┐
│  Set Goals   │
└──────┬───────┘
       ▼
┌──────────────┐
│ Update State │◄──────┐
└──────┬───────┘       │
       ▼               │
┌──────────────┐       │
│   Evaluate   │       │
│   Progress   │       │
└──────┬───────┘       │
       ▼               │
┌──────────────┐       │
│ All Goals    │───────┤
│ Achieved?    │  YES  │
└──────┬───────┘       │
   NO │                │
       ▼                │
┌──────────────┐       │
│   Select     │       │
│   Action     │       │
└──────┬───────┘       │
       ▼                │
┌──────────────┐       │
│   Execute    │───────┘
└──────────────┘
```

## 🚀 Usage

```python
from goal_driven_agent import GoalDrivenAgent, Goal, SuccessCriterion, Constraint

# Create agent
agent = GoalDrivenAgent("Support Optimizer")

# Define goal
goal = Goal(
    id="optimize_support",
    description="Fast, cheap, high-quality support",
    success_criteria=[
        SuccessCriterion(
            name="response_time",
            target_value=2.0,
            weight=0.4
        ),
        SuccessCriterion(
            name="cost",
            target_value=5.0,
            weight=0.3
        )
    ],
    constraints=[
        Constraint(
            name="budget",
            limit=1000.0,
            constraint_type=ConstraintType.HARD
        )
    ]
)

agent.add_goal(goal)

# Run
agent.update_state({
    "response_time": 10.0,
    "cost": 15.0
})

final_status = agent.run(available_actions)
```

## 📊 Evaluation

### Success Criteria Scoring

```python
# Weighted average of satisfaction scores
def overall_progress(goal):
    total_weight = sum(c.weight for c in goal.success_criteria)
    weighted_score = sum(
        c.satisfaction_score() * c.weight 
        for c in goal.success_criteria
    )
    return weighted_score / total_weight
```

### Constraint Violations

```python
# Hard constraints must not be violated
if constraint.is_violated() and constraint.type == HARD:
    goal.status = FAILED

# Soft constraints penalize but don't fail
if constraint.is_violated() and constraint.type == SOFT:
    score -= violation_severity * 10
```

## 🎓 Key Concepts

### 1. Weighted Success Criteria

Not all objectives are equal:
- Response time: 40% weight (critical)
- Cost: 30% weight (important)
- Quality: 30% weight (important)

### 2. Tolerance

Accept small deviations:
- Target: < 2 seconds
- Tolerance: 10%
- Acceptable: < 2.2 seconds

### 3. Constraint Types

**Hard constraints** (must not violate):
- Budget limits
- Legal requirements
- Safety limits

**Soft constraints** (should minimize):
- Resource usage
- Time estimates
- Staff count

### 4. Action Selection

Choose action that:
1. Maximizes progress toward goals
2. Minimizes constraint violations
3. Considers cost and risk

```python
score = progress_improvement
score -= hard_violation * 1000  # Heavy penalty
score -= soft_violation * 10    # Light penalty
score -= cost * 0.1
score -= risk * 5
```

## 📈 Example Output

```
🚀 Starting Goal-Driven Agent: Customer Support Optimizer
============================================================
🎯 Added goal: Optimize customer support: fast, cheap, high quality

📊 Iteration 1/5
------------------------------------------------------------

🎯 Optimize customer support: fast, cheap, high quality
   Progress: 23.3%
   Status: in_progress

⚡ Executing: Implement chatbot
   Expected impact: {'response_time': -6.0, 'cost_per_ticket': -8.0, ...}

📊 Iteration 2/5
------------------------------------------------------------

🎯 Optimize customer support: fast, cheap, high quality
   Progress: 67.5%
   Status: in_progress

⚡ Executing: Optimize workflows
   Expected impact: {'response_time': -3.0, 'cost_per_ticket': -5.0, ...}

📊 Iteration 3/5
------------------------------------------------------------

🎯 Optimize customer support: fast, cheap, high quality
   Progress: 91.2%
   Status: in_progress

⚡ Executing: Hire support staff
   Expected impact: {'response_time': -4.0, 'cost_per_ticket': -2.0, ...}

🎉 All goals achieved!

============================================================
Run complete!
Actions taken: 3

🎯 Optimize customer support: fast, cheap, high quality: achieved (100.0%)
```

## 🔧 Production Considerations

### Real Measurements

Connect to actual metrics:
```python
# Instead of simulated updates
agent.update_state({
    "response_time": metrics.get_average_response_time(),
    "satisfaction": survey.get_latest_score()
})
```

### Dynamic Goals

Goals can change over time:
```python
# Seasonal adjustments
if is_peak_season():
    goal.success_criteria[0].target_value = 1.0  # Stricter
```

### Multi-Goal Reasoning

When goals conflict:
```python
# Weight by business priority
for goal in agent.goals:
    if goal.id == "revenue":
        score += improvement * 2.0  # Higher priority
    else:
        score += improvement * 1.0
```

## 🎓 Comparison

| Pattern | Use Case | Decision Making |
|---------|----------|----------------|
| **Goal-Driven** | Multi-objective optimization | Weighted criteria + constraints |
| **Rule-Based** | Simple conditionals | If-then rules |
| **Utility-Based** | Preference optimization | Utility functions |
| **Constraint-Based** | Resource allocation | Constraint satisfaction |

## 📝 Files

- `agent.py` - Core implementation
- `test_agent.py` - Unit tests
- `README.md` - This file

## 🚀 Try It

```bash
cd examples/goal_driven_agent
python agent.py
```

---

**Pattern**: Declarative goals with weighted criteria  
**Use Case**: Multi-objective optimization with constraints  
**Complexity**: Medium-High
