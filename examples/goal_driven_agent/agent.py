"""
Goal-Driven Agent Example

Demonstrates an agent that operates based on declarative goals with:
- Weighted success criteria
- Hard constraints
- Progress tracking
- Adaptive behavior

This pattern is useful when the agent needs to optimize for multiple
objectives while respecting boundaries.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from enum import Enum
from datetime import datetime
import json


class ConstraintType(Enum):
    """Types of constraints."""
    HARD = "hard"  # Must not be violated
    SOFT = "soft"  # Should minimize violations


class GoalStatus(Enum):
    """Status of goal achievement."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    ACHIEVED = "achieved"
    FAILED = "failed"
    PARTIAL = "partial"


@dataclass
class SuccessCriterion:
    """
    A single criterion for goal success.
    
    Example: "response_time < 100ms" with weight 0.3
    """
    name: str
    target_value: Any
    current_value: Optional[Any] = None
    weight: float = 1.0  # Importance (0.0 to 1.0)
    tolerance: float = 0.1  # Acceptable deviation
    evaluator: Optional[Callable[[Any, Any], bool]] = None
    
    def is_satisfied(self) -> bool:
        """Check if criterion is satisfied."""
        if self.current_value is None:
            return False
        
        if self.evaluator:
            return self.evaluator(self.current_value, self.target_value)
        
        # Default: numeric comparison with tolerance
        try:
            diff = abs(float(self.current_value) - float(self.target_value))
            return diff <= self.target_value * self.tolerance
        except (ValueError, TypeError):
            return self.current_value == self.target_value
    
    def satisfaction_score(self) -> float:
        """Calculate satisfaction score (0.0 to 1.0)."""
        if self.is_satisfied():
            return 1.0
        
        if self.current_value is None:
            return 0.0
        
        # Calculate partial satisfaction
        try:
            target = float(self.target_value)
            current = float(self.current_value)
            
            if target == 0:
                return 1.0 if current == 0 else 0.0
            
            # Closer to target = higher score
            ratio = min(current / target, target / current)
            return max(0.0, ratio)
        except (ValueError, TypeError, ZeroDivisionError):
            return 0.0


@dataclass
class Constraint:
    """
    A constraint that limits the agent's actions.
    
    Example: "cost < $100" (hard constraint)
    """
    name: str
    limit: Any
    current: Optional[Any] = None
    constraint_type: ConstraintType = ConstraintType.HARD
    evaluator: Optional[Callable[[Any, Any], bool]] = None
    
    def is_violated(self) -> bool:
        """Check if constraint is violated."""
        if self.current is None:
            return False
        
        if self.evaluator:
            return not self.evaluator(self.current, self.limit)
        
        # Default: check if current exceeds limit
        try:
            return float(self.current) > float(self.limit)
        except (ValueError, TypeError):
            return self.current != self.limit
    
    def violation_severity(self) -> float:
        """Calculate violation severity (0.0 = no violation)."""
        if not self.is_violated():
            return 0.0
        
        try:
            limit = float(self.limit)
            current = float(self.current)
            
            if limit == 0:
                return 1.0
            
            return (current - limit) / limit
        except (ValueError, TypeError, ZeroDivisionError):
            return 1.0


@dataclass
class Goal:
    """
    A declarative goal with success criteria and constraints.
    
    Example: "Optimize customer support with <$100 cost and <2s response time"
    """
    id: str
    description: str
    success_criteria: List[SuccessCriterion] = field(default_factory=list)
    constraints: List[Constraint] = field(default_factory=list)
    status: GoalStatus = GoalStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    def overall_progress(self) -> float:
        """Calculate overall progress (0.0 to 1.0)."""
        if not self.success_criteria:
            return 0.0
        
        total_weight = sum(c.weight for c in self.success_criteria)
        weighted_score = sum(
            c.satisfaction_score() * c.weight 
            for c in self.success_criteria
        )
        
        return weighted_score / total_weight if total_weight > 0 else 0.0
    
    def is_achieved(self) -> bool:
        """Check if all success criteria are satisfied."""
        return all(c.is_satisfied() for c in self.success_criteria)
    
    def has_violations(self) -> bool:
        """Check if any hard constraints are violated."""
        return any(
            c.is_violated() and c.constraint_type == ConstraintType.HARD
            for c in self.constraints
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "description": self.description,
            "status": self.status.value,
            "progress": self.overall_progress(),
            "achieved": self.is_achieved(),
            "violations": self.has_violations(),
            "success_criteria": [
                {
                    "name": c.name,
                    "target": c.target_value,
                    "current": c.current_value,
                    "satisfied": c.is_satisfied(),
                    "score": c.satisfaction_score()
                }
                for c in self.success_criteria
            ],
            "constraints": [
                {
                    "name": c.name,
                    "limit": c.limit,
                    "current": c.current,
                    "violated": c.is_violated(),
                    "severity": c.violation_severity()
                }
                for c in self.constraints
            ]
        }


@dataclass
class Action:
    """An action the agent can take."""
    name: str
    description: str
    expected_impact: Dict[str, Any]  # Expected changes to criteria
    cost: float = 0.0
    risk: float = 0.0  # 0.0 to 1.0
    
    def predict_outcome(self, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Predict outcome of taking this action."""
        predicted = current_state.copy()
        for key, delta in self.expected_impact.items():
            if key in predicted:
                try:
                    predicted[key] = float(predicted[key]) + float(delta)
                except (ValueError, TypeError):
                    predicted[key] = delta
            else:
                predicted[key] = delta
        return predicted


class GoalDrivenAgent:
    """
    An agent that operates based on declarative goals.
    
    Key features:
    - Multiple weighted success criteria
    - Hard and soft constraints
    - Progress tracking
    - Action selection based on goal alignment
    """
    
    def __init__(self, name: str):
        self.name = name
        self.goals: Dict[str, Goal] = {}
        self.action_history: List[Dict[str, Any]] = []
        self.current_state: Dict[str, Any] = {}
    
    def add_goal(self, goal: Goal):
        """Add a goal for the agent to pursue."""
        self.goals[goal.id] = goal
        print(f"🎯 Added goal: {goal.description}")
    
    def update_state(self, measurements: Dict[str, Any]):
        """Update current state with new measurements."""
        self.current_state.update(measurements)
        
        # Update goal criteria and constraints
        for goal in self.goals.values():
            for criterion in goal.success_criteria:
                if criterion.name in measurements:
                    criterion.current_value = measurements[criterion.name]
            
            for constraint in goal.constraints:
                if constraint.name in measurements:
                    constraint.current = measurements[constraint.name]
    
    def evaluate_goals(self) -> Dict[str, Any]:
        """Evaluate all goals and return status."""
        results = {}
        
        for goal_id, goal in self.goals.items():
            # Check constraints first
            if goal.has_violations():
                goal.status = GoalStatus.FAILED
            elif goal.is_achieved():
                goal.status = GoalStatus.ACHIEVED
                if goal.completed_at is None:
                    goal.completed_at = datetime.utcnow()
            elif goal.overall_progress() > 0:
                goal.status = GoalStatus.IN_PROGRESS
            
            results[goal_id] = goal.to_dict()
        
        return results
    
    def select_action(self, available_actions: List[Action]) -> Optional[Action]:
        """
        Select the best action based on goal alignment.
        
        Strategy: Choose action that maximizes progress toward goals
        while minimizing constraint violations.
        """
        if not available_actions:
            return None
        
        best_action = None
        best_score = float('-inf')
        
        for action in available_actions:
            score = self._evaluate_action(action)
            
            if score > best_score:
                best_score = score
                best_action = action
        
        return best_action
    
    def _evaluate_action(self, action: Action) -> float:
        """Evaluate an action's expected value."""
        # Predict outcome
        predicted_state = action.predict_outcome(self.current_state)
        
        score = 0.0
        
        for goal in self.goals.values():
            # Calculate progress improvement
            current_progress = goal.overall_progress()
            
            # Temporarily update criteria with predicted values
            original_values = {}
            for criterion in goal.success_criteria:
                if criterion.name in predicted_state:
                    original_values[criterion.name] = criterion.current_value
                    criterion.current_value = predicted_state[criterion.name]
            
            predicted_progress = goal.overall_progress()
            
            # Restore original values
            for criterion in goal.success_criteria:
                if criterion.name in original_values:
                    criterion.current_value = original_values[criterion.name]
            
            # Add improvement weighted by criterion weights
            improvement = predicted_progress - current_progress
            score += improvement * sum(c.weight for c in goal.success_criteria)
            
            # Penalize constraint violations
            for constraint in goal.constraints:
                if constraint.name in predicted_state:
                    original = constraint.current
                    constraint.current = predicted_state[constraint.name]
                    
                    if constraint.is_violated():
                        severity = constraint.violation_severity()
                        if constraint.constraint_type == ConstraintType.HARD:
                            score -= severity * 1000  # Heavy penalty
                        else:
                            score -= severity * 10
                    
                    constraint.current = original
        
        # Consider cost and risk
        score -= action.cost * 0.1
        score -= action.risk * 5
        
        return score
    
    def execute_action(self, action: Action) -> Dict[str, Any]:
        """Execute an action and record the result."""
        print(f"⚡ Executing: {action.name}")
        print(f"   Expected impact: {action.expected_impact}")
        
        # In real implementation, this would actually execute the action
        # Here we simulate the effect
        self.update_state(action.expected_impact)
        
        execution_record = {
            "action": action.name,
            "timestamp": datetime.utcnow().isoformat(),
            "state_before": self.current_state.copy(),
            "expected_impact": action.expected_impact,
            "cost": action.cost,
            "risk": action.risk
        }
        
        self.action_history.append(execution_record)
        
        return execution_record
    
    def run(self, available_actions: List[Action], max_iterations: int = 10):
        """
        Run the agent until goals are achieved or max iterations reached.
        """
        print(f"\n🚀 Starting Goal-Driven Agent: {self.name}")
        print("=" * 60)
        
        for iteration in range(max_iterations):
            print(f"\n📊 Iteration {iteration + 1}/{max_iterations}")
            print("-" * 60)
            
            # Evaluate current state
            goal_status = self.evaluate_goals()
            
            # Check if all goals achieved
            all_achieved = all(
                g["status"] == "achieved" for g in goal_status.values()
            )
            
            if all_achieved:
                print("\n🎉 All goals achieved!")
                break
            
            # Print goal status
            for goal_id, status in goal_status.items():
                print(f"\n🎯 {status['description']}")
                print(f"   Progress: {status['progress']:.1%}")
                print(f"   Status: {status['status']}")
                
                if status['violations']:
                    print(f"   ⚠️  Constraint violations detected!")
            
            # Select and execute best action
            action = self.select_action(available_actions)
            
            if action is None:
                print("\n❌ No suitable action found")
                break
            
            self.execute_action(action)
        
        print("\n" + "=" * 60)
        print("Run complete!")
        print(f"Actions taken: {len(self.action_history)}")
        
        # Final goal status
        final_status = self.evaluate_goals()
        for goal_id, status in final_status.items():
            print(f"\n🎯 {status['description']}: {status['status']} ({status['progress']:.1%})")
        
        return final_status


# Example usage
def demo():
    """Demonstrate the goal-driven agent."""
    
    # Create agent
    agent = GoalDrivenAgent("Customer Support Optimizer")
    
    # Define goal: Optimize support with constraints
    goal = Goal(
        id="optimize_support",
        description="Optimize customer support: fast, cheap, high quality",
        success_criteria=[
            SuccessCriterion(
                name="response_time",
                target_value=2.0,  # 2 seconds
                weight=0.4,
                tolerance=0.2
            ),
            SuccessCriterion(
                name="cost_per_ticket",
                target_value=5.0,  # $5
                weight=0.3,
                tolerance=0.1
            ),
            SuccessCriterion(
                name="satisfaction_score",
                target_value=4.5,  # out of 5
                weight=0.3,
                tolerance=0.05
            )
        ],
        constraints=[
            Constraint(
                name="monthly_budget",
                limit=1000.0,  # $1000 hard limit
                constraint_type=ConstraintType.HARD
            ),
            Constraint(
                name="staff_count",
                limit=5,  # Max 5 staff
                constraint_type=ConstraintType.SOFT
            )
        ]
    )
    
    agent.add_goal(goal)
    
    # Initial state
    agent.update_state({
        "response_time": 10.0,  # Currently 10 seconds
        "cost_per_ticket": 15.0,  # Currently $15
        "satisfaction_score": 3.0,  # Currently 3/5
        "monthly_budget": 0.0,
        "staff_count": 2
    })
    
    # Available actions
    actions = [
        Action(
            name="Implement chatbot",
            description="Deploy AI chatbot for common queries",
            expected_impact={
                "response_time": -6.0,  # Reduces to 4s
                "cost_per_ticket": -8.0,  # Reduces to $7
                "satisfaction_score": 0.5,
                "monthly_budget": 300.0
            },
            cost=100.0,
            risk=0.2
        ),
        Action(
            name="Hire support staff",
            description="Add more human support agents",
            expected_impact={
                "response_time": -4.0,  # Reduces to 6s
                "cost_per_ticket": -2.0,  # Reduces to $13
                "satisfaction_score": 1.0,
                "monthly_budget": 500.0,
                "staff_count": 1
            },
            cost=200.0,
            risk=0.1
        ),
        Action(
            name="Optimize workflows",
            description="Improve internal processes",
            expected_impact={
                "response_time": -3.0,  # Reduces to 7s
                "cost_per_ticket": -5.0,  # Reduces to $10
                "satisfaction_score": 0.3,
                "monthly_budget": 100.0
            },
            cost=50.0,
            risk=0.05
        ),
        Action(
            name="Upgrade infrastructure",
            description="Faster servers and tools",
            expected_impact={
                "response_time": -7.0,  # Reduces to 3s
                "satisfaction_score": 0.8,
                "monthly_budget": 800.0  # High cost!
            },
            cost=300.0,
            risk=0.3
        )
    ]
    
    # Run agent
    final_status = agent.run(actions, max_iterations=5)
    
    return agent, final_status


if __name__ == "__main__":
    agent, status = demo()
