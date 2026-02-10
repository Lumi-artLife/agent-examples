"""
Unit tests for Goal-Driven Agent.
"""

import unittest
from goal_driven_agent import (
    GoalDrivenAgent,
    Goal,
    SuccessCriterion,
    Constraint,
    ConstraintType,
    GoalStatus,
    Action
)


class TestSuccessCriterion(unittest.TestCase):
    """Test SuccessCriterion class."""
    
    def test_satisfaction_exact_match(self):
        """Test satisfaction with exact match."""
        criterion = SuccessCriterion(
            name="response_time",
            target_value=2.0,
            current_value=2.0
        )
        self.assertTrue(criterion.is_satisfied())
        self.assertEqual(criterion.satisfaction_score(), 1.0)
    
    def test_satisfaction_within_tolerance(self):
        """Test satisfaction within tolerance."""
        criterion = SuccessCriterion(
            name="response_time",
            target_value=2.0,
            current_value=2.1,
            tolerance=0.1  # 10% tolerance
        )
        self.assertTrue(criterion.is_satisfied())
    
    def test_satisfaction_partial(self):
        """Test partial satisfaction."""
        criterion = SuccessCriterion(
            name="response_time",
            target_value=2.0,
            current_value=4.0
        )
        self.assertFalse(criterion.is_satisfied())
        self.assertEqual(criterion.satisfaction_score(), 0.5)  # 2.0/4.0


class TestConstraint(unittest.TestCase):
    """Test Constraint class."""
    
    def test_hard_constraint_not_violated(self):
        """Test hard constraint not violated."""
        constraint = Constraint(
            name="budget",
            limit=1000.0,
            current=500.0,
            constraint_type=ConstraintType.HARD
        )
        self.assertFalse(constraint.is_violated())
        self.assertEqual(constraint.violation_severity(), 0.0)
    
    def test_hard_constraint_violated(self):
        """Test hard constraint violated."""
        constraint = Constraint(
            name="budget",
            limit=1000.0,
            current=1500.0,
            constraint_type=ConstraintType.HARD
        )
        self.assertTrue(constraint.is_violated())
        self.assertEqual(constraint.violation_severity(), 0.5)  # (1500-1000)/1000


class TestGoal(unittest.TestCase):
    """Test Goal class."""
    
    def test_goal_creation(self):
        """Test basic goal creation."""
        goal = Goal(
            id="test_goal",
            description="Test goal"
        )
        self.assertEqual(goal.id, "test_goal")
        self.assertEqual(goal.status, GoalStatus.PENDING)
    
    def test_overall_progress(self):
        """Test overall progress calculation."""
        goal = Goal(
            id="test",
            description="Test",
            success_criteria=[
                SuccessCriterion(
                    name="c1",
                    target_value=100,
                    current_value=100,
                    weight=0.5
                ),
                SuccessCriterion(
                    name="c2",
                    target_value=50,
                    current_value=25,
                    weight=0.5
                )
            ]
        )
        # First criterion: 100% satisfied
        # Second criterion: 50% satisfied
        # Weighted average: (1.0 * 0.5 + 0.5 * 0.5) = 0.75
        self.assertEqual(goal.overall_progress(), 0.75)
    
    def test_is_achieved(self):
        """Test goal achievement check."""
        goal = Goal(
            id="test",
            description="Test",
            success_criteria=[
                SuccessCriterion(
                    name="c1",
                    target_value=100,
                    current_value=100
                ),
                SuccessCriterion(
                    name="c2",
                    target_value=50,
                    current_value=50
                )
            ]
        )
        self.assertTrue(goal.is_achieved())
    
    def test_has_violations(self):
        """Test constraint violation detection."""
        goal = Goal(
            id="test",
            description="Test",
            constraints=[
                Constraint(
                    name="budget",
                    limit=100,
                    current=150,
                    constraint_type=ConstraintType.HARD
                )
            ]
        )
        self.assertTrue(goal.has_violations())


class TestAction(unittest.TestCase):
    """Test Action class."""
    
    def test_predict_outcome(self):
        """Test outcome prediction."""
        action = Action(
            name="test_action",
            description="Test",
            expected_impact={
                "response_time": -2.0,
                "cost": -5.0
            }
        )
        
        current_state = {
            "response_time": 10.0,
            "cost": 20.0
        }
        
        predicted = action.predict_outcome(current_state)
        
        self.assertEqual(predicted["response_time"], 8.0)
        self.assertEqual(predicted["cost"], 15.0)


class TestGoalDrivenAgent(unittest.TestCase):
    """Test GoalDrivenAgent class."""
    
    def test_agent_creation(self):
        """Test agent creation."""
        agent = GoalDrivenAgent("Test Agent")
        self.assertEqual(agent.name, "Test Agent")
        self.assertEqual(len(agent.goals), 0)
    
    def test_add_goal(self):
        """Test adding goals."""
        agent = GoalDrivenAgent("Test")
        goal = Goal(id="g1", description="Test goal")
        
        agent.add_goal(goal)
        
        self.assertIn("g1", agent.goals)
        self.assertEqual(agent.goals["g1"].description, "Test goal")
    
    def test_update_state(self):
        """Test state updates."""
        agent = GoalDrivenAgent("Test")
        goal = Goal(
            id="g1",
            description="Test",
            success_criteria=[
                SuccessCriterion(name="metric", target_value=100)
            ]
        )
        agent.add_goal(goal)
        
        agent.update_state({"metric": 50})
        
        self.assertEqual(agent.current_state["metric"], 50)
        self.assertEqual(goal.success_criteria[0].current_value, 50)
    
    def test_evaluate_goals(self):
        """Test goal evaluation."""
        agent = GoalDrivenAgent("Test")
        goal = Goal(
            id="g1",
            description="Test",
            success_criteria=[
                SuccessCriterion(
                    name="metric",
                    target_value=100,
                    current_value=100
                )
            ]
        )
        agent.add_goal(goal)
        
        results = agent.evaluate_goals()
        
        self.assertEqual(results["g1"]["status"], "achieved")
        self.assertTrue(results["g1"]["achieved"])
    
    def test_select_action(self):
        """Test action selection."""
        agent = GoalDrivenAgent("Test")
        
        # Create a goal
        goal = Goal(
            id="g1",
            description="Test",
            success_criteria=[
                SuccessCriterion(
                    name="metric",
                    target_value=100,
                    current_value=50
                )
            ]
        )
        agent.add_goal(goal)
        
        # Create actions
        actions = [
            Action(
                name="good_action",
                description="Helps achieve goal",
                expected_impact={"metric": 30}  # Gets to 80
            ),
            Action(
                name="bad_action",
                description="Doesn't help much",
                expected_impact={"metric": 10}  # Gets to 60
            )
        ]
        
        selected = agent.select_action(actions)
        
        self.assertIsNotNone(selected)
        self.assertEqual(selected.name, "good_action")


class TestIntegration(unittest.TestCase):
    """Integration tests."""
    
    def test_full_workflow(self):
        """Test complete agent workflow."""
        agent = GoalDrivenAgent("Integration Test")
        
        # Set up goal
        goal = Goal(
            id="optimize",
            description="Optimize metric",
            success_criteria=[
                SuccessCriterion(
                    name="metric",
                    target_value=100,
                    current_value=50,
                    weight=1.0
                )
            ]
        )
        agent.add_goal(goal)
        
        # Set up actions
        actions = [
            Action(
                name="increment",
                description="Increment metric",
                expected_impact={"metric": 25}
            )
        ]
        
        # Update state
        agent.update_state({"metric": 50})
        
        # Evaluate
        status = agent.evaluate_goals()
        self.assertEqual(status["optimize"]["progress"], 0.5)
        
        # Select action
        action = agent.select_action(actions)
        self.assertIsNotNone(action)
        
        # Execute
        agent.execute_action(action)
        
        # Check history
        self.assertEqual(len(agent.action_history), 1)


if __name__ == "__main__":
    unittest.main()
