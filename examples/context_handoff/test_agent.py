"""
Unit tests for Context Handoff example.
"""

import unittest
from unittest.mock import Mock, MagicMock
from datetime import datetime

from agent import (
    Context,
    Pipeline,
    PipelineNode,
    PipelineStage,
    DataCollectionNode,
    ValidationNode,
    AnalysisNode,
    ReportGenerationNode,
    StageResult,
    mock_data_source,
    mock_analysis
)


class TestContext(unittest.TestCase):
    """Test Context dataclass."""
    
    def test_context_creation(self):
        """Test basic context creation."""
        ctx = Context(query="test query")
        self.assertEqual(ctx.query, "test query")
        self.assertEqual(ctx.current_stage, PipelineStage.DATA_COLLECTION)
        self.assertEqual(len(ctx.errors), 0)
    
    def test_context_to_dict(self):
        """Test context serialization."""
        ctx = Context(query="test")
        ctx.raw_data = {"key": "value"}
        
        data = ctx.to_dict()
        
        self.assertEqual(data["query"], "test")
        self.assertEqual(data["raw_data"], {"key": "value"})
        self.assertEqual(data["current_stage"], "data_collection")
    
    def test_context_from_dict(self):
        """Test context deserialization."""
        original = Context(query="test")
        original.raw_data = {"data": [1, 2, 3]}
        
        data = original.to_dict()
        restored = Context.from_dict(data)
        
        self.assertEqual(restored.query, "test")
        self.assertEqual(restored.raw_data, {"data": [1, 2, 3]})


class TestDataCollectionNode(unittest.TestCase):
    """Test DataCollectionNode."""
    
    def test_successful_collection(self):
        """Test successful data collection."""
        mock_source = Mock(return_value={"data": "test"})
        node = DataCollectionNode(mock_source)
        
        ctx = Context(query="test")
        result = node.execute(ctx)
        
        self.assertTrue(result.success)
        self.assertEqual(ctx.raw_data, {"data": "test"})
        self.assertEqual(result.next_stage, PipelineStage.VALIDATION)
        mock_source.assert_called_once_with("test")
    
    def test_collection_failure(self):
        """Test data collection failure."""
        mock_source = Mock(side_effect=Exception("API error"))
        node = DataCollectionNode(mock_source)
        
        ctx = Context(query="test")
        result = node.execute(ctx)
        
        self.assertFalse(result.success)
        self.assertIn("API error", result.errors[0])
        self.assertIsNone(result.next_stage)


class TestValidationNode(unittest.TestCase):
    """Test ValidationNode."""
    
    def test_successful_validation(self):
        """Test successful validation."""
        node = ValidationNode(required_fields=["name", "value"])
        
        ctx = Context(query="test")
        ctx.raw_data = {"name": "test", "value": 123, "extra": "ignored"}
        
        result = node.execute(ctx)
        
        self.assertTrue(result.success)
        self.assertEqual(ctx.validated_data, {"name": "test", "value": 123})
        self.assertEqual(result.next_stage, PipelineStage.ANALYSIS)
    
    def test_missing_fields(self):
        """Test validation with missing fields."""
        node = ValidationNode(required_fields=["name", "value"])
        
        ctx = Context(query="test")
        ctx.raw_data = {"name": "test"}  # Missing "value"
        
        result = node.execute(ctx)
        
        self.assertFalse(result.success)
        self.assertIn("Missing required field: value", result.errors)


class TestAnalysisNode(unittest.TestCase):
    """Test AnalysisNode."""
    
    def test_successful_analysis(self):
        """Test successful analysis."""
        mock_analyzer = Mock(return_value={"result": "analysis"})
        node = AnalysisNode(mock_analyzer)
        
        ctx = Context(query="test")
        ctx.validated_data = {"data": "input"}
        
        result = node.execute(ctx)
        
        self.assertTrue(result.success)
        self.assertEqual(ctx.analysis_results, {"result": "analysis"})
        mock_analyzer.assert_called_once_with({"data": "input"})
    
    def test_analysis_failure(self):
        """Test analysis failure."""
        mock_analyzer = Mock(side_effect=Exception("Analysis error"))
        node = AnalysisNode(mock_analyzer)
        
        ctx = Context(query="test")
        ctx.validated_data = {"data": "input"}
        
        result = node.execute(ctx)
        
        self.assertFalse(result.success)
        self.assertIn("Analysis error", result.errors[0])


class TestReportGenerationNode(unittest.TestCase):
    """Test ReportGenerationNode."""
    
    def test_report_generation(self):
        """Test successful report generation."""
        node = ReportGenerationNode()
        
        ctx = Context(query="test")
        ctx.validated_data = {"key": "value"}
        ctx.analysis_results = {"stats": {"mean": 100}}
        
        result = node.execute(ctx)
        
        self.assertTrue(result.success)
        self.assertIsNotNone(ctx.final_report)
        self.assertIn("test", ctx.final_report)
        self.assertEqual(result.next_stage, PipelineStage.COMPLETE)


class TestPipeline(unittest.TestCase):
    """Test Pipeline orchestration."""
    
    def test_pipeline_creation(self):
        """Test pipeline creation."""
        pipeline = Pipeline("Test Pipeline")
        self.assertEqual(pipeline.name, "Test Pipeline")
    
    def test_add_node(self):
        """Test adding nodes."""
        pipeline = Pipeline("Test")
        node = DataCollectionNode(mock_data_source)
        
        pipeline.add_node(node)
        
        self.assertIn(PipelineStage.DATA_COLLECTION, pipeline.nodes)
    
    def test_full_pipeline_execution(self):
        """Test complete pipeline execution."""
        pipeline = Pipeline("Test Pipeline")
        pipeline.add_node(DataCollectionNode(mock_data_source))
        pipeline.add_node(ValidationNode(required_fields=["query", "data_points"]))
        pipeline.add_node(AnalysisNode(mock_analysis))
        pipeline.add_node(ReportGenerationNode())
        
        ctx = pipeline.execute("test query")
        
        self.assertEqual(ctx.query, "test query")
        self.assertIsNotNone(ctx.raw_data)
        self.assertIsNotNone(ctx.validated_data)
        self.assertIsNotNone(ctx.analysis_results)
        self.assertIsNotNone(ctx.final_report)
        self.assertEqual(ctx.current_stage, PipelineStage.COMPLETE)
    
    def test_pipeline_error_handling(self):
        """Test pipeline stops on error."""
        pipeline = Pipeline("Test Pipeline")
        
        # Add failing validation (missing required fields)
        pipeline.add_node(DataCollectionNode(mock_data_source))
        pipeline.add_node(ValidationNode(required_fields=["nonexistent_field"]))
        
        ctx = pipeline.execute("test")
        
        # Pipeline should stop at validation
        self.assertEqual(ctx.current_stage, PipelineStage.DATA_COLLECTION)
        self.assertGreater(len(ctx.errors), 0)


class TestIntegration(unittest.TestCase):
    """Integration tests."""
    
    def test_context_serialization_roundtrip(self):
        """Test full context serialization and deserialization."""
        # Create and populate context
        ctx = Context(query="integration test")
        ctx.raw_data = {"test": "data"}
        ctx.validated_data = {"clean": "data"}
        ctx.analysis_results = {"result": 42}
        
        # Serialize
        data = ctx.to_dict()
        
        # Deserialize
        restored = Context.from_dict(data)
        
        # Verify
        self.assertEqual(restored.query, "integration test")
        self.assertEqual(restored.raw_data, {"test": "data"})
        self.assertEqual(restored.validated_data, {"clean": "data"})
        self.assertEqual(restored.analysis_results, {"result": 42})
    
    def test_stage_history_tracking(self):
        """Test that stage execution is tracked."""
        pipeline = Pipeline("History Test")
        pipeline.add_node(DataCollectionNode(mock_data_source))
        pipeline.add_node(ValidationNode(required_fields=["query", "data_points"]))
        
        ctx = pipeline.execute("test")
        
        # Should have history entries
        self.assertGreaterEqual(len(ctx.stage_history), 1)
        
        # Check history structure
        for entry in ctx.stage_history:
            self.assertIn("stage", entry)
            self.assertIn("node", entry)
            self.assertIn("success", entry)


if __name__ == "__main__":
    unittest.main()
