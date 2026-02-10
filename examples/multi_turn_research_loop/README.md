# Multi-Turn Research Loop

An autonomous research agent demonstrating the **Think → Act → Evaluate → Repeat** pattern.

## 🎯 Use Case

**Scenario**: An AI agent needs to research a topic thoroughly before providing an answer.

**Challenge**: 
- Single search often yields incomplete information
- Human researchers iterate: search, read, search again with refined queries
- How do we encode this into an autonomous agent?

**Solution**: Multi-turn research loop with built-in quality evaluation

## 🔄 The Pattern

```
┌─────────┐    ┌─────────┐    ┌──────────┐    ┌─────────┐
│  THINK  │───→│   ACT   │───→│ EVALUATE │───→│ REPEAT? │
└─────────┘    └─────────┘    └──────────┘    └────┬────┘
     ↑                                              │
     └──────────────────────────────────────────────┘
                      (if needed)
```

**THINK**: Given current knowledge, what's the next best action?
- Search for more information?
- Analyze what we have?
- Synthesize final answer?
- Escalate to human?

**ACT**: Execute the decided action
- Perform search with current query
- Analyze collected sources

**EVALUATE**: Assess progress against criteria
- Do we have enough sources?
- Is the information high quality?
- Have we reached max iterations?
- Are we making progress?

**REPEAT**: If evaluation says "needs more", loop again
- With refined query
- With adjusted strategy

## 🏗️ Architecture

```
ResearchQuery
    ├── query: str
    ├── context: dict
    ├── max_iterations: int
    └── min_sources: int

MultiTurnResearchAgent
    ├── search_provider: SearchProvider
    ├── max_iterations: int
    ├── iterations: List[ResearchIteration]
    └── collected_sources: List[SearchResult]
    
    └── research(query) → ResearchReport
        ├── _decide_action() → ActionType
        ├── _execute_search() → List[SearchResult]
        ├── _evaluate_progress() → EvaluationResult
        ├── _refine_query() → str
        └── _synthesize_results() → str
```

## 🚀 Usage

```python
from multi_turn_research_loop import (
    MultiTurnResearchAgent,
    ResearchQuery,
    MockSearchProvider
)

# Initialize
search_provider = MockSearchProvider()
agent = MultiTurnResearchAgent(
    search_provider=search_provider,
    max_iterations=5
)

# Create query
query = ResearchQuery(
    query="AI agent frameworks",
    context={"focus": "multi-agent workflows"},
    max_iterations=3,
    min_sources=3
)

# Execute research
report = agent.research(query)

# Check results
print(f"Confidence: {report.confidence_score}")
print(f"Sources: {len(report.sources)}")
print(f"Iterations: {len(report.iterations)}")
print(report.synthesis)
```

## 📊 Evaluation Criteria

The agent stops when ANY of these conditions are met:

1. **Sufficient Information**: 
   - ≥ min_sources collected
   - Average relevance ≥ 0.8

2. **Maximum Iterations**: 
   - Reached max_iterations limit
   - Prevents infinite loops

3. **Insufficient Source**:
   - No new information in iteration
   - Escalate to human researcher

4. **Quality Plateau**:
   - Not making meaningful progress
   - Query refinement not helping

## 🧠 Key Design Decisions

### 1. Separation of Concerns
- **SearchProvider**: Abstracts search implementation
- **ResearchAgent**: Orchestrates the loop
- **Evaluation**: Pluggable stopping criteria

### 2. Observable State
Every iteration is recorded:
- What action was taken
- What results were found
- Why the evaluation decided what it did

This enables:
- Debugging agent behavior
- Auditing research quality
- Learning from patterns

### 3. Graceful Degradation
When stuck, the agent:
- Records why it couldn't complete
- Returns partial results
- Suggests escalation

## 🔧 Production Considerations

### Search Provider Options
- **Perplexity API**: Real-time web search with citations
- **SerpAPI**: Google search results
- **Vector DB**: Semantic search over knowledge base
- **Hybrid**: Combine multiple sources

### LLM Integration Points
In production, replace rule-based logic with LLM:

```python
# Current: Rule-based
def _decide_action(self, iteration_num, query):
    if iteration_num == 1:
        return ActionType.SEARCH
    # ...

# Production: LLM-based
def _decide_action(self, iteration_num, query):
    prompt = f"""
    Given {len(self.collected_sources)} sources from {iteration_num} iterations,
    should we: search more, analyze, synthesize, or escalate?
    
    Sources: {self._format_sources()}
    """
    return llm.decide(prompt)
```

### Cost Optimization
- **Tiered models**: Cheap model for search, expensive for synthesis
- **Caching**: Cache search results within session
- **Early stopping**: Aggressive evaluation to minimize iterations

## 📈 Example Output

```
Starting research on: AI agent frameworks

🔍 Searching: AI agent frameworks
🔍 Searching: AI agent frameworks best practices 2026

============================================================
Research Complete!
============================================================

Confidence Score: 0.85
Total Time: 2.34s
Iterations: 2
Sources: 3
Completion Reason: sufficient

------------------------------------------------------------
Iteration Details:
------------------------------------------------------------

Iteration 1:
  Action: search
  Query: AI agent frameworks
  Results: 3 sources
  Evaluation: needs_more
  Reasoning: Need more sources (have 1, want 3)

Iteration 2:
  Action: search
  Query: AI agent frameworks best practices 2026
  Results: 3 sources
  Evaluation: sufficient
  Reasoning: Found 3 high-quality sources

------------------------------------------------------------
Synthesis:
------------------------------------------------------------

Research Summary for: AI agent frameworks

Sources Consulted: 3
Iterations: 2

Key Findings:
1. tech-blog.com (relevance: 0.90)
   LangChain is a popular framework for building LLM applications...
2. github.com (relevance: 0.95)
   Hive is a YC-backed framework for multi-agent workflows...
3. documentation.io (relevance: 0.85)
   AutoGPT enables autonomous AI agents with goal-directed behavior...
```

## 🎓 Learning Points

### 1. Iteration > Perfection
Don't try to get perfect results in one shot. Build feedback loops.

### 2. Evaluation is Key
The magic is in knowing when to stop. Good stopping criteria prevent:
- Wasted iterations
- Premature conclusions
- Infinite loops

### 3. Transparency Matters
Recording every iteration's reasoning enables:
- Debugging
- Improvement
- Trust

## 🔗 Related Concepts

- **ReAct Pattern**: Reasoning + Acting (similar approach)
- **Tree of Thoughts**: Explore multiple research paths
- **RAG**: Retrieval-Augmented Generation (uses similar search)

## 📝 Files

- `agent.py` - Core implementation
- `test_agent.py` - Unit tests
- `README.md` - This file

## 🚀 Try It

```bash
cd examples/multi_turn_research_loop
python agent.py
```

---

**Pattern**: Think → Act → Evaluate → Repeat  
**Use Case**: Autonomous research and information gathering  
**Complexity**: Medium
