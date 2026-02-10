# Context Handoff

Demonstrates context passing between multiple nodes in a pipeline.

## 🎯 Use Case

**Scenario**: A multi-stage data processing pipeline where work flows from one agent to another.

**Pattern**: Data Collection → Validation → Analysis → Report Generation

**Challenge**: How does context flow between stages without breaking?

**Solution**: Structured context passing with validation and error handling.

## 🔄 The Pattern

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Data Collector │────→│    Validator    │────→│    Analyzer     │────→│ Report Generator│
│                 │     │                 │     │                 │     │                 │
│  Fetch raw data │     │ Validate fields │     │ Run analysis    │     │ Create report   │
└─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘
         │                       │                       │                       │
         └───────────────────────┴───────────────────────┴───────────────────────┘
                                    Context Flow
```

## 🏗️ Architecture

### Context Object

The `Context` dataclass is the key to successful handoff:

```python
@dataclass
class Context:
    query: str                          # Original request
    raw_data: Dict[str, Any]           # Stage 1 output
    validated_data: Dict[str, Any]     # Stage 2 output
    analysis_results: Dict[str, Any]   # Stage 3 output
    final_report: Optional[str]        # Stage 4 output
    
    current_stage: PipelineStage
    stage_history: List[Dict]          # Execution audit trail
    errors: List[str]                  # Error tracking
```

### Pipeline Nodes

Each node:
1. **Receives context** from previous node
2. **Performs its task** using relevant context fields
3. **Updates context** with its output
4. **Passes updated context** to next node

```python
class PipelineNode:
    def execute(self, context: Context) -> StageResult:
        # 1. Read from context
        input_data = context.raw_data
        
        # 2. Process
        output = self.process(input_data)
        
        # 3. Update context
        context.validated_data = output
        context.current_stage = next_stage
        
        # 4. Return for next node
        return StageResult(success=True, ...)
```

## 🚀 Usage

```python
from context_handoff import (
    Pipeline,
    DataCollectionNode,
    ValidationNode,
    AnalysisNode,
    ReportGenerationNode
)

# Create pipeline
pipeline = Pipeline("Data Analysis Pipeline")

# Add nodes
pipeline.add_node(DataCollectionNode(data_source_func))
pipeline.add_node(ValidationNode(required_fields=["query", "data"]))
pipeline.add_node(AnalysisNode(analysis_func))
pipeline.add_node(ReportGenerationNode())

# Execute
context = pipeline.execute("Monthly sales analysis")

# Access results
print(context.validated_data)
print(context.analysis_results)
print(context.final_report)
```

## 📊 Execution Flow

### 1. Data Collection
```python
# Input: query="sales analysis"
# Output: raw_data={"data_points": [...], "metadata": {...}}
```

### 2. Validation
```python
# Input: context.raw_data
# Checks: required fields present
# Output: context.validated_data (cleaned)
```

### 3. Analysis
```python
# Input: context.validated_data
# Process: statistical analysis, trend detection
# Output: context.analysis_results
```

### 4. Report Generation
```python
# Input: context.analysis_results + history
# Process: format into human-readable report
# Output: context.final_report
```

## 🛡️ Error Handling

### Validation Errors
- Missing required fields
- Invalid data types
- Out-of-range values

**Result**: Pipeline stops, errors recorded in context

### Processing Errors
- API failures
- Analysis exceptions
- Report generation errors

**Result**: Stage fails, pipeline halts, partial results preserved

### Recovery
```python
# Context preserves partial results
def resume_pipeline(context: Context):
    if context.current_stage == PipelineStage.ANALYSIS:
        # Resume from failed stage
        return pipeline.resume_from(context)
```

## 🔧 Production Considerations

### Serialization
```python
# Save context between stages (for long-running pipelines)
context_dict = context.to_dict()
redis.set(f"pipeline:{job_id}", json.dumps(context_dict))

# Resume later
context = Context.from_dict(json.loads(redis.get(f"pipeline:{job_id}")))
```

### Distributed Execution
```python
# Each stage can run on different workers
def stage_worker(stage_name, context_dict):
    context = Context.from_dict(context_dict)
    node = get_node(stage_name)
    result = node.execute(context)
    
    # Queue next stage
    if result.next_stage:
        queue.publish(f"stage:{result.next_stage.value}", context.to_dict())
```

### Monitoring
```python
# Track pipeline execution
def log_stage_completion(context, stage, duration):
    metrics.timing(f"pipeline.stage.{stage}", duration)
    metrics.gauge("pipeline.context_size", len(json.dumps(context.to_dict())))
```

## 🎓 Key Design Decisions

### 1. Immutable Context Updates
Each stage adds new fields rather than modifying existing ones:
- ✅ Preserves audit trail
- ✅ Enables debugging
- ✅ Supports replay

### 2. Structured Handoff
Explicit context schema rather than loose dict:
- ✅ Type safety
- ✅ Auto-completion
- ✅ Documentation

### 3. Error Accumulation
Errors recorded in context rather than raised immediately:
- ✅ Partial results preserved
- ✅ Batch error handling
- ✅ Better UX

## 📈 Example Output

```
🚀 Starting pipeline: Data Analysis Pipeline
📋 Query: Monthly sales analysis
============================================================
📊 [DataCollector] Collecting data for: Monthly sales analysis
✅ Stage complete: data_collection
✅ [Validator] Validating data...
✅ Stage complete: validation
🔍 [Analyzer] Analyzing data...
✅ Stage complete: analysis
📄 [ReportGenerator] Generating report...
✅ Stage complete: report_generation
============================================================
📊 Pipeline complete!
   Final stage: complete
   Errors: 0

============================================================
Final Context:
============================================================

Query: Monthly sales analysis

Raw Data Keys: ['query', 'data_points', 'metadata']

Validated Data: {'query': 'Monthly sales analysis', 'data_points': [...]}

Analysis Results: {
  "statistics": {
    "count": 3,
    "mean": 123.33,
    "max": 150,
    "min": 100
  },
  "trends": [{"type": "increasing", "confidence": 0.7}],
  "anomalies": []
}

Stage History:
  - data_collection: DataCollector (✅)
  - validation: Validator (✅)
  - analysis: Analyzer (✅)
  - report_generation: ReportGenerator (✅)
```

## 🔄 Comparison with Other Patterns

| Pattern | Use Case | Handoff Method |
|---------|----------|----------------|
| **Context Handoff** | Multi-stage pipeline | Structured Context object |
| **Message Queue** | Async processing | Messages/events |
| **Shared State** | Concurrent agents | Database/cache |
| **Direct Call** | Simple workflows | Function arguments |

## 📝 Files

- `agent.py` - Core implementation
- `test_agent.py` - Unit tests
- `README.md` - This file

## 🚀 Try It

```bash
cd examples/context_handoff
python agent.py
```

---

**Pattern**: Context passing between pipeline stages  
**Use Case**: Multi-stage data processing workflows  
**Complexity**: Medium
