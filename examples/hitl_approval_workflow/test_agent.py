"""
Unit tests for HITL Approval Workflow.
"""

import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import time
import threading

from agent import (
    HITLHandler,
    HITLRequest,
    HITLResponse,
    EmailApprovalWorkflow,
    ApprovalStatus,
    InputType,
    EscalationResult
)


class TestHITLRequest(unittest.TestCase):
    """Test HITLRequest dataclass."""
    
    def test_request_creation(self):
        """Test basic request creation."""
        request = HITLRequest(
            request_id="test_001",
            draft_content="Test content",
            timeout_minutes=5
        )
        self.assertEqual(request.request_id, "test_001")
        self.assertEqual(request.draft_content, "Test content")
        self.assertEqual(request.timeout_minutes, 5)
        self.assertFalse(request.is_expired())
    
    def test_request_expiration(self):
        """Test request expiration logic."""
        request = HITLRequest(
            request_id="test_002",
            draft_content="Test",
            timeout_minutes=0  # Immediate timeout for testing
        )
        # Manually set created_at to past
        request.created_at = datetime.utcnow() - timedelta(minutes=1)
        self.assertTrue(request.is_expired())


class TestHITLHandler(unittest.TestCase):
    """Test HITLHandler functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.handler = HITLHandler(timeout_minutes=5)
    
    def test_create_request(self):
        """Test request creation."""
        request = self.handler.create_request(
            draft_content="Test draft",
            context={"test": "data"}
        )
        self.assertIn(request.request_id, self.handler.pending_requests)
        self.assertEqual(request.draft_content, "Test draft")
    
    def test_submit_response(self):
        """Test response submission."""
        request = self.handler.create_request(draft_content="Test")
        response = HITLResponse(
            request_id=request.request_id,
            status=ApprovalStatus.APPROVED
        )
        
        result = self.handler.submit_response(response)
        self.assertTrue(result)
        self.assertIn(request.request_id, self.handler.responses)
    
    def test_submit_response_invalid_request(self):
        """Test submitting response for non-existent request."""
        response = HITLResponse(
            request_id="invalid_id",
            status=ApprovalStatus.APPROVED
        )
        result = self.handler.submit_response(response)
        self.assertFalse(result)
    
    def test_audit_logging(self):
        """Test audit log functionality."""
        self.handler.create_request(draft_content="Test")
        self.assertEqual(len(self.handler.audit_log), 1)
        self.assertEqual(self.handler.audit_log[0]["event"], "request_created")


class TestEmailApprovalWorkflow(unittest.TestCase):
    """Test EmailApprovalWorkflow."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.workflow = EmailApprovalWorkflow(
            timeout_minutes=5,
            escalation_email="manager@test.com"
        )
    
    def test_workflow_initialization(self):
        """Test workflow initialization."""
        self.assertEqual(self.workflow.escalation_email, "manager@test.com")
        self.assertIsNotNone(self.workflow.hitl_handler)
    
    def test_draft_and_send_approved(self):
        """Test email approval workflow - approved case."""
        # Submit response in background
        def submit_approval():
            time.sleep(0.1)
            pending_ids = list(self.workflow.hitl_handler.pending_requests.keys())
            if pending_ids:
                self.workflow.hitl_handler.submit_response(HITLResponse(
                    request_id=pending_ids[-1],
                    status=ApprovalStatus.APPROVED,
                    responder_id="reviewer_001"
                ))
        
        threading.Thread(target=submit_approval, daemon=True).start()
        
        result = self.workflow.draft_and_send(
            customer_email="customer@test.com",
            subject="Test Subject",
            draft_content="Test content"
        )
        
        self.assertEqual(result["status"], "approved")
        self.assertEqual(result["customer_email"], "customer@test.com")
        self.assertIn("message", result)
    
    def test_draft_and_send_rejected(self):
        """Test email approval workflow - rejected case."""
        def submit_rejection():
            time.sleep(0.1)
            pending_ids = list(self.workflow.hitl_handler.pending_requests.keys())
            if pending_ids:
                self.workflow.hitl_handler.submit_response(HITLResponse(
                    request_id=pending_ids[-1],
                    status=ApprovalStatus.REJECTED,
                    responder_id="reviewer_001",
                    feedback="Needs revision"
                ))
        
        threading.Thread(target=submit_rejection, daemon=True).start()
        
        result = self.workflow.draft_and_send(
            customer_email="customer@test.com",
            subject="Test Subject",
            draft_content="Test content"
        )
        
        self.assertEqual(result["status"], "rejected")
        self.assertEqual(result["feedback"], "Needs revision")


class TestIntegration(unittest.TestCase):
    """Integration tests."""
    
    def test_full_workflow_with_timeout(self):
        """Test complete workflow with timeout."""
        # Create workflow with very short timeout
        workflow = EmailApprovalWorkflow(
            timeout_minutes=0,  # Immediate timeout
            escalation_email="manager@test.com"
        )
        
        result = workflow.draft_and_send(
            customer_email="customer@test.com",
            subject="Test",
            draft_content="Test"
        )
        
        self.assertEqual(result["status"], "timeout")
        self.assertIn("escalation_email", result)


if __name__ == "__main__":
    unittest.main()
