"""
Multi-Turn Research Loop Example

An autonomous research agent that demonstrates the Think → Act → Evaluate → Repeat pattern.

This example shows how an agent can:
1. Search for information
2. Evaluate if the information is sufficient
3. Decide whether to search again or synthesize results
4. Learn from each iteration

Inspired by real-world autonomous agent patterns used in production systems.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from enum import Enum
import json
import time
from datetime import datetime


class EvaluationResult(Enum):
    """Result of evaluating research progress."""
    SUFFICIENT = "sufficient"
    NEEDS_MORE = "needs_more"
    INSUFFICIENT_SOURCE = "insufficient_source"
    MAX_ITERATIONS = "max_iterations"


class ActionType(Enum):
    """Types of actions the agent can take."""
    SEARCH = "search"
    ANALYZE = "analyze"
    SYNTHESIZE = "synthesize"
    ESCALATE = "escalate"


@dataclass
class ResearchQuery:
    """Represents a research query with context."""
    query: str
    context: Dict[str, Any] = field(default_factory=dict)
    max_iterations: int = 5
    min_sources: int = 3
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SearchResult:
    """Represents a single search result."""
    source: str
    content: str
    relevance_score: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResearchIteration:
    """Represents one iteration of the research loop."""
    iteration_number: int
    query: str
    action: ActionType
    results: List[SearchResult]
    evaluation: EvaluationResult
    reasoning: str
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ResearchReport:
    """Final research report."""
    original_query: str
    iterations: List[ResearchIteration]
    sources: List[SearchResult]
    synthesis: str
    confidence_score: float
    completion_reason: EvaluationResult
    total_time_seconds: float
    created_at: datetime = field(default_factory=datetime.utcnow)


class SearchProvider:
    """
    Abstract base for search providers.
    
    In production, this could be:
    - Perplexity API
    - SerpAPI
    - Custom search index
    - Vector database
    """
    
    def search(self, query: str, context: Dict[str, Any]) -> List[SearchResult]:
        """Execute search and return results."""
        raise NotImplementedError


class MockSearchProvider(SearchProvider):
    """
    Mock search provider for demonstration.
    
    In production, replace with actual search API.
    """
    
    def __init__(self):
        self.mock_db = {
            "AI agent frameworks": [
                SearchResult(
                    source="tech-blog.com",
                    content="LangChain is a popular framework for building LLM applications",
                    relevance_score=0.9,
                    metadata={"author": "Tech Expert", "date": "2026-01-15"}
                ),
                SearchResult(
                    source="github.com",
                    content="Hive is a YC-backed framework for multi-agent workflows",
                    relevance_score=0.95,
                    metadata={"stars": "6800", "language": "Python"}
                ),
                SearchResult(
                    source="documentation.io",
                    content="AutoGPT enables autonomous AI agents with goal-directed behavior",
                    relevance_score=0.85,
                    metadata={"version": "0.5.0"}
                ),
            ],
            "autonomous business": [
                SearchResult(
                    source="swan-ai.com",
                    content="Swan AI built autonomous GTM systems reaching $1M ARR with 3 people",
                    relevance_score=0.95,
                    metadata={"revenue": "$1M ARR", "team_size": 3}
                ),
                SearchResult(
                    source="indiehackers.com",
                    content="Constraints force innovation - building without hiring",
                    relevance_score=0.88,
                    metadata={"topic": "bootstrapping"}
                ),
            ],
        }
    
    def search(self, query: str, context: Dict[str, Any]) -> List[SearchResult]:
        """Simulate search with mock data."""
        # Simulate API delay
        time.sleep(0.5)
        
        # Simple keyword matching for demo
        results = []
        for key, value in self.mock_db.items():
            if any(word.lower() in query.lower() for word in key.split()):
                results.extend(value)
        
        # If no specific match, return generic results
        if not results:
            results = [
                SearchResult(
                    source="general-knowledge.com",
                    content=f"Information about {query}",
                    relevance_score=0.6
                )
            ]
        
        return results


class MultiTurnResearchAgent:
    """
    Autonomous research agent using the Think → Act → Evaluate → Repeat pattern.
    
    Key features:
    - Self-directed research with stopping criteria
    - Quality evaluation at each iteration
    - Learning from previous iterations
    - Graceful escalation when stuck
    """
    
    def __init__(
        self,
        search_provider: SearchProvider,
        max_iterations: int = 5,
        min_confidence: float = 0.7
    ):
        self.search_provider = search_provider
        self.max_iterations = max_iterations
        self.min_confidence = min_confidence
        self.iterations: List[ResearchIteration] = []
        self.collected_sources: List[SearchResult] = []
    
    def research(self, query: ResearchQuery) -> ResearchReport:
        """
        Execute multi-turn research loop.
        
        Pattern: Think → Act → Evaluate → Repeat
        """
        start_time = time.time()
        
        current_query = query.query
        
        for iteration_num in range(1, query.max_iterations + 1):
            # THINK: Decide action based on current state
            action = self._decide_action(iteration_num, current_query)
            
            # ACT: Execute the decided action
            if action == ActionType.SEARCH:
                results = self._execute_search(current_query, query.context)
            elif action == ActionType.ANALYZE:
                results = self._analyze_collected()
            elif action == ActionType.SYNTHESIZE:
                break  # Exit loop to synthesize
            elif action == ActionType.ESCALATE:
                return self._create_escalation_report(
                    query, iteration_num, start_time
                )
            
            # EVALUATE: Assess progress and decide next step
            evaluation, reasoning = self._evaluate_progress(
                iteration_num, results, query
            )
            
            # Record iteration
            iteration = ResearchIteration(
                iteration_number=iteration_num,
                query=current_query,
                action=action,
                results=results,
                evaluation=evaluation,
                reasoning=reasoning
            )
            self.iterations.append(iteration)
            
            # Store unique sources
            for result in results:
                if not any(r.source == result.source for r in self.collected_sources):
                    self.collected_sources.append(result)
            
            # Check stopping conditions
            if evaluation == EvaluationResult.SUFFICIENT:
                break
            elif evaluation == EvaluationResult.MAX_ITERATIONS:
                break
            elif evaluation == EvaluationResult.INSUFFICIENT_SOURCE:
                # Modify query for next iteration
                current_query = self._refine_query(current_query, results)
        
        # SYNTHESIZE: Create final report
        synthesis = self._synthesize_results(query)
        confidence = self._calculate_confidence()
        
        total_time = time.time() - start_time
        
        return ResearchReport(
            original_query=query.query,
            iterations=self.iterations,
            sources=self.collected_sources,
            synthesis=synthesis,
            confidence_score=confidence,
            completion_reason=evaluation,
            total_time_seconds=total_time
        )
    
    def _decide_action(self, iteration_num: int, query: str) -> ActionType:
        """Decide next action based on current state."""
        if iteration_num == 1:
            return ActionType.SEARCH
        elif len(self.collected_sources) < 2:
            return ActionType.SEARCH
        elif iteration_num >= self.max_iterations - 1:
            return ActionType.SYNTHESIZE
        else:
            # In real implementation, this would use LLM reasoning
            return ActionType.SEARCH
    
    def _execute_search(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> List[SearchResult]:
        """Execute search query."""
        print(f"🔍 Searching: {query}")
        return self.search_provider.search(query, context)
    
    def _analyze_collected(self) -> List[SearchResult]:
        """Analyze already collected sources."""
        # In real implementation, this would use LLM to analyze
        return self.collected_sources
    
    def _evaluate_progress(
        self,
        iteration_num: int,
        results: List[SearchResult],
        query: ResearchQuery
    ) -> tuple:
        """
        Evaluate research progress and decide if we should continue.
        
        Returns:
            (EvaluationResult, reasoning)
        """
        # Check max iterations
        if iteration_num >= query.max_iterations:
            return EvaluationResult.MAX_ITERATIONS, "Reached maximum iterations"
        
        # Check number of sources
        if len(self.collected_sources) >= query.min_sources:
            # Check average relevance
            avg_relevance = sum(r.relevance_score for r in results) / len(results)
            if avg_relevance >= 0.8:
                return EvaluationResult.SUFFICIENT, f"Found {len(self.collected_sources)} high-quality sources"
        
        # Check if we're making progress
        if iteration_num > 1 and len(results) == 0:
            return EvaluationResult.INSUFFICIENT_SOURCE, "No new information found"
        
        return EvaluationResult.NEEDS_MORE, f"Need more sources (have {len(self.collected_sources)}, want {query.min_sources})"
    
    def _refine_query(self, current_query: str, results: List[SearchResult]) -> str:
        """Refine query based on previous results."""
        # In real implementation, this would use LLM to generate better queries
        return f"{current_query} best practices 2026"
    
    def _synthesize_results(self, query: ResearchQuery) -> str:
        """Synthesize all collected information into a coherent report."""
        # In real implementation, this would use LLM to synthesize
        synthesis = f"""
Research Summary for: {query.query}

Sources Consulted: {len(self.collected_sources)}
Iterations: {len(self.iterations)}

Key Findings:
"""
        for i, source in enumerate(self.collected_sources[:5], 1):
            synthesis += f"\n{i}. {source.source} (relevance: {source.relevance_score:.2f})"
            synthesis += f"\n   {source.content[:100]}..."
        
        return synthesis
    
    def _calculate_confidence(self) -> float:
        """Calculate overall confidence score."""
        if not self.collected_sources:
            return 0.0
        
        # Factor in: number of sources, average relevance, diversity
        avg_relevance = sum(s.relevance_score for s in self.collected_sources) / len(self.collected_sources)
        source_count_factor = min(len(self.collected_sources) / 5, 1.0)  # Max at 5 sources
        
        return (avg_relevance * 0.6) + (source_count_factor * 0.4)
    
    def _create_escalation_report(
        self,
        query: ResearchQuery,
        iteration_num: int,
        start_time: float
    ) -> ResearchReport:
        """Create report when escalation is needed."""
        return ResearchReport(
            original_query=query.query,
            iterations=self.iterations,
            sources=self.collected_sources,
            synthesis="Escalation required - unable to complete research autonomously",
            confidence_score=0.0,
            completion_reason=EvaluationResult.INSUFFICIENT_SOURCE,
            total_time_seconds=time.time() - start_time
        )


# Example usage
def demo():
    """Demonstrate the multi-turn research loop."""
    print("=" * 60)
    print("Multi-Turn Research Loop Demo")
    print("=" * 60)
    
    # Initialize
    search_provider = MockSearchProvider()
    agent = MultiTurnResearchAgent(
        search_provider=search_provider,
        max_iterations=3
    )
    
    # Create research query
    query = ResearchQuery(
        query="AI agent frameworks",
        context={"focus": "multi-agent workflows", "experience": "intermediate"},
        max_iterations=3,
        min_sources=2
    )
    
    # Execute research
    print(f"\nStarting research on: {query.query}\n")
    report = agent.research(query)
    
    # Display results
    print("\n" + "=" * 60)
    print("Research Complete!")
    print("=" * 60)
    print(f"\nConfidence Score: {report.confidence_score:.2f}")
    print(f"Total Time: {report.total_time_seconds:.2f}s")
    print(f"Iterations: {len(report.iterations)}")
    print(f"Sources: {len(report.sources)}")
    print(f"Completion Reason: {report.completion_reason.value}")
    
    print("\n" + "-" * 60)
    print("Iteration Details:")
    print("-" * 60)
    for iteration in report.iterations:
        print(f"\nIteration {iteration.iteration_number}:")
        print(f"  Action: {iteration.action.value}")
        print(f"  Query: {iteration.query}")
        print(f"  Results: {len(iteration.results)} sources")
        print(f"  Evaluation: {iteration.evaluation.value}")
        print(f"  Reasoning: {iteration.reasoning}")
    
    print("\n" + "-" * 60)
    print("Synthesis:")
    print("-" * 60)
    print(report.synthesis)
    
    return report


if __name__ == "__main__":
    demo()
