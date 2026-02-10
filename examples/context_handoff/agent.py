"""
Context Handoff Example

Demonstrates how to pass context between multiple nodes/agents in a pipeline.
This is critical for multi-agent systems where work flows from one agent to another.

Pattern: Data Collection → Analysis → Report Generation

Key challenge: How does context flow between stages without breaking?
Key solution: Structured context passing with validation and error handling.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Callable
from enum import Enum
from datetime import datetime
import json


class PipelineStage(Enum):
    """Stages in the data processing pipeline."""
    DATA_COLLECTION = "data_collection"
    VALIDATION = "validation"
    ANALYSIS = "analysis"
    REPORT_GENERATION = "report_generation"
    COMPLETE = "complete"


@dataclass
class Context:
    """
    Structured context that flows through the pipeline.
    
    This is the key to successful multi-agent coordination:
    - Each stage adds its output
    - Each stage can see previous stages' outputs
    - Validation ensures required fields are present
    - Metadata tracks execution history
    """
    # Input data
    query: str
    raw_data: Dict[str, Any] = field(default_factory=dict)
    
    # Stage outputs
    validated_data: Dict[str, Any] = field(default_factory=dict)
    analysis_results: Dict[str, Any] = field(default_factory=dict)
    final_report: Optional[str] = None
    
    # Execution metadata
    current_stage: PipelineStage = PipelineStage.DATA_COLLECTION
    stage_history: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary for serialization."""
        return {
            "query": self.query,
            "raw_data": self.raw_data,
            "validated_data": self.validated_data,
            "analysis_results": self.analysis_results,
            "final_report": self.final_report,
            "current_stage": self.current_stage.value,
            "stage_history": self.stage_history,
            "errors": self.errors,
            "start_time": self.start_time.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Context':
        """Create context from dictionary."""
        ctx = cls(query=data["query"])
        ctx.raw_data = data.get("raw_data", {})
        ctx.validated_data = data.get("validated_data", {})
        ctx.analysis_results = data.get("analysis_results", {})
        ctx.final_report = data.get("final_report")
        ctx.current_stage = PipelineStage(data.get("current_stage", "data_collection"))
        ctx.stage_history = data.get("stage_history", [])
        ctx.errors = data.get("errors", [])
        return ctx


@dataclass
class StageResult:
    """Result of executing a pipeline stage."""
    success: bool
    output: Dict[str, Any]
    errors: List[str]
    next_stage: Optional[PipelineStage]
    execution_time_ms: float


class PipelineNode:
    """
    Base class for pipeline nodes.
    
    Each node:
    - Receives context from previous node
    - Performs its specific task
    - Updates context with its output
    - Passes updated context to next node
    """
    
    def __init__(self, name: str, stage: PipelineStage):
        self.name = name
        self.stage = stage
    
    def execute(self, context: Context) -> StageResult:
        """Execute this node's task."""
        raise NotImplementedError
    
    def _log_execution(self, context: Context, success: bool, errors: List[str]):
        """Log execution to context history."""
        context.stage_history.append({
            "stage": self.stage.value,
            "node": self.name,
            "success": success,
            "errors": errors,
            "timestamp": datetime.utcnow().isoformat()
        })


class DataCollectionNode(PipelineNode):
    """
    First stage: Collect raw data based on query.
    
    In production, this might:
    - Query databases
    - Call APIs
    - Scrape web pages
    - Read files
    """
    
    def __init__(self, data_source: Callable[[str], Dict[str, Any]]):
        super().__init__("DataCollector", PipelineStage.DATA_COLLECTION)
        self.data_source = data_source
    
    def execute(self, context: Context) -> StageResult:
        """Collect raw data."""
        print(f"📊 [{self.name}] Collecting data for: {context.query}")
        
        try:
            # Fetch data from source
            raw_data = self.data_source(context.query)
            
            # Update context
            context.raw_data = raw_data
            context.current_stage = PipelineStage.VALIDATION
            
            self._log_execution(context, True, [])
            
            return StageResult(
                success=True,
                output=raw_data,
                errors=[],
                next_stage=PipelineStage.VALIDATION,
                execution_time_ms=100.0  # Mock timing
            )
            
        except Exception as e:
            error_msg = f"Data collection failed: {str(e)}"
            context.errors.append(error_msg)
            self._log_execution(context, False, [error_msg])
            
            return StageResult(
                success=False,
                output={},
                errors=[error_msg],
                next_stage=None,
                execution_time_ms=0.0
            )


class ValidationNode(PipelineNode):
    """
    Second stage: Validate and clean collected data.
    
    Ensures:
    - Required fields are present
    - Data types are correct
    - Values are within expected ranges
    """
    
    def __init__(self, required_fields: List[str]):
        super().__init__("Validator", PipelineStage.VALIDATION)
        self.required_fields = required_fields
    
    def execute(self, context: Context) -> StageResult:
        """Validate raw data."""
        print(f"✅ [{self.name}] Validating data...")
        
        errors = []
        validated = {}
        
        # Check required fields
        for field in self.required_fields:
            if field not in context.raw_data:
                errors.append(f"Missing required field: {field}")
            else:
                validated[field] = context.raw_data[field]
        
        if errors:
            context.errors.extend(errors)
            self._log_execution(context, False, errors)
            
            return StageResult(
                success=False,
                output={},
                errors=errors,
                next_stage=None,
                execution_time_ms=50.0
            )
        
        # Update context
        context.validated_data = validated
        context.current_stage = PipelineStage.ANALYSIS
        
        self._log_execution(context, True, [])
        
        return StageResult(
            success=True,
            output=validated,
            errors=[],
            next_stage=PipelineStage.ANALYSIS,
            execution_time_ms=50.0
        )


class AnalysisNode(PipelineNode):
    """
    Third stage: Analyze validated data.
    
    Performs:
    - Statistical analysis
    - Pattern recognition
    - Trend identification
    - Anomaly detection
    """
    
    def __init__(self, analysis_function: Callable[[Dict[str, Any]], Dict[str, Any]]):
        super().__init__("Analyzer", PipelineStage.ANALYSIS)
        self.analysis_function = analysis_function
    
    def execute(self, context: Context) -> StageResult:
        """Analyze validated data."""
        print(f"🔍 [{self.name}] Analyzing data...")
        
        try:
            # Perform analysis
            results = self.analysis_function(context.validated_data)
            
            # Update context
            context.analysis_results = results
            context.current_stage = PipelineStage.REPORT_GENERATION
            
            self._log_execution(context, True, [])
            
            return StageResult(
                success=True,
                output=results,
                errors=[],
                next_stage=PipelineStage.REPORT_GENERATION,
                execution_time_ms=200.0
            )
            
        except Exception as e:
            error_msg = f"Analysis failed: {str(e)}"
            context.errors.append(error_msg)
            self._log_execution(context, False, [error_msg])
            
            return StageResult(
                success=False,
                output={},
                errors=[error_msg],
                next_stage=None,
                execution_time_ms=0.0
            )


class ReportGenerationNode(PipelineNode):
    """
    Final stage: Generate human-readable report.
    
    Combines:
    - Original query
    - Analysis results
    - Insights and recommendations
    """
    
    def __init__(self, report_template: Optional[str] = None):
        super().__init__("ReportGenerator", PipelineStage.REPORT_GENERATION)
        self.report_template = report_template or self._default_template()
    
    def execute(self, context: Context) -> StageResult:
        """Generate final report."""
        print(f"📄 [{self.name}] Generating report...")
        
        try:
            # Generate report
            report = self._generate_report(context)
            
            # Update context
            context.final_report = report
            context.current_stage = PipelineStage.COMPLETE
            
            self._log_execution(context, True, [])
            
            return StageResult(
                success=True,
                output={"report": report},
                errors=[],
                next_stage=PipelineStage.COMPLETE,
                execution_time_ms=150.0
            )
            
        except Exception as e:
            error_msg = f"Report generation failed: {str(e)}"
            context.errors.append(error_msg)
            self._log_execution(context, False, [error_msg])
            
            return StageResult(
                success=False,
                output={},
                errors=[error_msg],
                next_stage=None,
                execution_time_ms=0.0
            )
    
    def _default_template(self) -> str:
        """Default report template."""
        return """
# Research Report: {query}

## Data Summary
{validated_data}

## Analysis Results
{analysis_results}

## Key Insights
{insights}

## Recommendations
{recommendations}

---
Generated: {timestamp}
Pipeline stages: {stage_count}
        """
    
    def _generate_report(self, context: Context) -> str:
        """Generate formatted report."""
        return self.report_template.format(
            query=context.query,
            validated_data=json.dumps(context.validated_data, indent=2),
            analysis_results=json.dumps(context.analysis_results, indent=2),
            insights="Based on the analysis, we found significant patterns...",
            recommendations="1. Action item one\n2. Action item two",
            timestamp=datetime.utcnow().isoformat(),
            stage_count=len(context.stage_history)
        )


class Pipeline:
    """
    Orchestrates multi-stage processing with context handoff.
    
    Key responsibilities:
    - Register nodes in order
    - Execute pipeline with context passing
    - Handle errors and recovery
    - Track execution history
    """
    
    def __init__(self, name: str):
        self.name = name
        self.nodes: Dict[PipelineStage, PipelineNode] = {}
    
    def add_node(self, node: PipelineNode):
        """Add a node to the pipeline."""
        self.nodes[node.stage] = node
    
    def execute(self, query: str) -> Context:
        """
        Execute the full pipeline.
        
        Returns:
            Final context with all stage outputs
        """
        print(f"\n🚀 Starting pipeline: {self.name}")
        print(f"📋 Query: {query}")
        print("=" * 60)
        
        # Initialize context
        context = Context(query=query)
        
        # Execute stages in order
        stage_order = [
            PipelineStage.DATA_COLLECTION,
            PipelineStage.VALIDATION,
            PipelineStage.ANALYSIS,
            PipelineStage.REPORT_GENERATION
        ]
        
        for stage in stage_order:
            if stage not in self.nodes:
                print(f"⚠️  No node registered for stage: {stage.value}")
                continue
            
            node = self.nodes[stage]
            result = node.execute(context)
            
            if not result.success:
                print(f"❌ Pipeline failed at stage: {stage.value}")
                print(f"   Errors: {result.errors}")
                break
            
            print(f"✅ Stage complete: {stage.value}")
        
        print("=" * 60)
        print(f"📊 Pipeline complete!")
        print(f"   Final stage: {context.current_stage.value}")
        print(f"   Errors: {len(context.errors)}")
        
        return context


# Example data source and analysis functions
def mock_data_source(query: str) -> Dict[str, Any]:
    """Mock data source for demonstration."""
    return {
        "query": query,
        "data_points": [
            {"date": "2026-01-01", "value": 100},
            {"date": "2026-01-02", "value": 150},
            {"date": "2026-01-03", "value": 120},
        ],
        "metadata": {
            "source": "mock_api",
            "timestamp": datetime.utcnow().isoformat()
        }
    }


def mock_analysis(data: Dict[str, Any]) -> Dict[str, Any]:
    """Mock analysis function for demonstration."""
    data_points = data.get("data_points", [])
    values = [dp["value"] for dp in data_points]
    
    return {
        "statistics": {
            "count": len(values),
            "mean": sum(values) / len(values) if values else 0,
            "max": max(values) if values else 0,
            "min": min(values) if values else 0,
        },
        "trends": [
            {"type": "increasing", "confidence": 0.7}
        ],
        "anomalies": []
    }


def demo():
    """Demonstrate the context handoff pipeline."""
    print("=" * 60)
    print("Context Handoff Demo")
    print("=" * 60)
    
    # Create pipeline
    pipeline = Pipeline("Data Analysis Pipeline")
    
    # Add nodes
    pipeline.add_node(DataCollectionNode(mock_data_source))
    pipeline.add_node(ValidationNode(required_fields=["query", "data_points"]))
    pipeline.add_node(AnalysisNode(mock_analysis))
    pipeline.add_node(ReportGenerationNode())
    
    # Execute pipeline
    context = pipeline.execute("Monthly sales analysis")
    
    # Display results
    print("\n" + "=" * 60)
    print("Final Context:")
    print("=" * 60)
    print(f"\nQuery: {context.query}")
    print(f"\nRaw Data Keys: {list(context.raw_data.keys())}")
    print(f"\nValidated Data: {context.validated_data}")
    print(f"\nAnalysis Results: {json.dumps(context.analysis_results, indent=2)}")
    print(f"\nStage History:")
    for entry in context.stage_history:
        print(f"  - {entry['stage']}: {entry['node']} ({'✅' if entry['success'] else '❌'})")
    
    if context.final_report:
        print("\n" + "=" * 60)
        print("Generated Report:")
        print("=" * 60)
        print(context.final_report)
    
    return context


if __name__ == "__main__":
    demo()
