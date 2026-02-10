"""
Unit tests for Multi-Turn Research Loop.
"""

import unittest
from unittest.mock import Mock, MagicMock
from datetime import datetime

from agent import (
    MultiTurnResearchAgent,
    ResearchQuery,
    SearchResult,
    ResearchIteration,
    EvaluationResult,
    ActionType,
    MockSearchProvider
)


class TestResearchQuery(unittest.TestCase):
    """Test ResearchQuery dataclass."""
    
    def test_query_creation(self):
        """Test basic query creation."""
        query = ResearchQuery(
            query="test query",
            max_iterations=5,
            min_sources=3
        )
        self.assertEqual(query.query, "test query")
        self.assertEqual(query.max_iterations, 5)
        self.assertEqual(query.min_sources, 3)


class TestMockSearchProvider(unittest.TestCase):
    """Test MockSearchProvider."""
    
    def setUp(self):
        self.provider = MockSearchProvider()
    
    def test_search_returns_results(self):
        """Test that search returns results."""
        results = self.provider.search("AI agent frameworks", {})
        self.assertGreater(len(results), 0)
    
    def test_search_relevance_scores(self):
        """Test that results have relevance scores."""
        results = self.provider.search("AI agent frameworks", {})
        for result in results:
            self.assertGreaterEqual(result.relevance_score, 0.0)
            self.assertLessEqual(result.relevance_score, 1.0)


class TestMultiTurnResearchAgent(unittest.TestCase):
    """Test MultiTurnResearchAgent functionality."""
    
    def setUp(self):
        self.search_provider = MockSearchProvider()
        self.agent = MultiTurnResearchAgent(
            search_provider=self.search_provider,
            max_iterations=3
        )
    
    def test_agent_initialization(self):
        """Test agent initialization."""
        self.assertEqual(self.agent.max_iterations, 3)
        self.assertEqual(len(self.agent.iterations), 0)
        self.assertEqual(len(self.agent.collected_sources), 0)
    
    def test_research_completion(self):
        """Test that research completes successfully."""
        query = ResearchQuery(
            query="AI agent frameworks",
            max_iterations=2,
            min_sources=1
        )
        
        report = self.agent.research(query)
        
        self.assertIsNotNone(report)
        self.assertEqual(report.original_query, "AI agent frameworks")
        self.assertGreater(len(report.sources), 0)
        self.assertGreater(len(report.iterations), 0)
    
    def test_research_confidence_score(self):
        """Test that confidence score is calculated."""
        query = ResearchQuery(
            query="AI agent frameworks",
            max_iterations=2,
            min_sources=1
        )
        
        report = self.agent.research(query)
        
        self.assertGreaterEqual(report.confidence_score, 0.0)
        self.assertLessEqual(report.confidence_score, 1.0)
    
    def test_max_iterations_enforced(self):
        """Test that max iterations is enforced."""
        query = ResearchQuery(
            query="test",
            max_iterations=2,
            min_sources=10  # Impossible to reach
        )
        
        report = self.agent.research(query)
        
        # Should stop at max iterations, not continue forever
        self.assertLessEqual(len(report.iterations), 2)


class TestEvaluationLogic(unittest.TestCase):
    """Test evaluation logic."""
    
    def setUp(self):
        self.search_provider = MockSearchProvider()
        self.agent = MultiTurnResearchAgent(self.search_provider)
    
    def test_sufficient_evaluation(self):
        """Test sufficient sources evaluation."""
        # Add enough high-quality sources
        self.agent.collected_sources = [
            SearchResult("s1", "content", 0.9),
            SearchResult("s2", "content", 0.85),
            SearchResult("s3", "content", 0.9),
        ]
        
        query = ResearchQuery(query="test", min_sources=3)
        results = [SearchResult("s", "c", 0.9)]
        
        evaluation, _ = self.agent._evaluate_progress(1, results, query)
        
        self.assertEqual(evaluation, EvaluationResult.SUFFICIENT)
    
    def test_needs_more_evaluation(self):
        """Test needs more evaluation."""
        query = ResearchQuery(query="test", min_sources=5)
        results = [SearchResult("s", "c", 0.6)]
        
        evaluation, _ = self.agent._evaluate_progress(1, results, query)
        
        self.assertEqual(evaluation, EvaluationResult.NEEDS_MORE)


class TestIntegration(unittest.TestCase):
    """Integration tests."""
    
    def test_end_to_end_research(self):
        """Test complete research workflow."""
        provider = MockSearchProvider()
        agent = MultiTurnResearchAgent(provider, max_iterations=3)
        
        query = ResearchQuery(
            query="autonomous business",
            context={"focus": "AI"},
            max_iterations=2,
            min_sources=2
        )
        
        report = agent.research(query)
        
        # Verify report structure
        self.assertIsNotNone(report.synthesis)
        self.assertIsNotNone(report.completion_reason)
        self.assertGreater(report.total_time_seconds, 0)
        
        # Verify iterations recorded
        self.assertEqual(len(agent.iterations), len(report.iterations))
        
        # Verify sources collected
        self.assertEqual(len(report.sources), len(agent.collected_sources))


if __name__ == "__main__":
    unittest.main()
