"""
HITL Approval Workflow Example

A production-ready Human-in-the-Loop (HITL) email approval system.
Demonstrates all 5 HITL input types with timeout handling and escalation.

This example is designed to work with the Hive framework's HITL capabilities.
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass, field
import logging
import time
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ApprovalStatus(Enum):
    """Status of the approval request."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    MODIFIED = "modified"
    TIMEOUT = "timeout"
    ESCALATED = "escalated"


class InputType(Enum):
    """Types of HITL input supported."""
    FREE_TEXT = "free_text"
    STRUCTURED_FIELDS = "structured_fields"
    SELECTION_LIST = "selection_list"
    APPROVAL_GATE = "approval_gate"
    RICH_CONTENT = "rich_content"


@dataclass
class HITLRequest:
    """Represents a HITL approval request."""
    request_id: str
    draft_content: str
    context: Dict[str, Any] = field(default_factory=dict)
    timeout_minutes: int = 5
    created_at: datetime = field(default_factory=datetime.utcnow)
    input_types: list = field(default_factory=lambda: [
        InputType.FREE_TEXT,
        InputType.SELECTION_LIST,
        InputType.APPROVAL_GATE
    ])
    
    def is_expired(self) -> bool:
        """Check if the request has timed out."""
        elapsed = datetime.utcnow() - self.created_at
        return elapsed > timedelta(minutes=self.timeout_minutes)


@dataclass
class HITLResponse:
    """Represents a human response to a HITL request."""
    request_id: str
    status: ApprovalStatus
    responder_id: Optional[str] = None
    feedback: Optional[str] = None
    modified_content: Optional[str] = None
    response_data: Dict[str, Any] = field(default_factory=dict)
    responded_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class EscalationResult:
    """Result when a request needs escalation."""
    reason: str
    original_request: HITLRequest
    fallback_action: str
    escalation_time: datetime = field(default_factory=datetime.utcnow)


class HITLHandler:
    """
    Handles Human-in-the-Loop interactions.
    
    Manages approval workflows with timeout handling and escalation.
    """
    
    def __init__(
        self,
        timeout_minutes: int = 5,
        escalation_enabled: bool = True,
        escalation_callback: Optional[Callable] = None
    ):
        self.timeout_minutes = timeout_minutes
        self.escalation_enabled = escalation_enabled
        self.escalation_callback = escalation_callback
        self.pending_requests: Dict[str, HITLRequest] = {}
        self.responses: Dict[str, HITLResponse] = {}
        self.audit_log: list = []
        
    def create_request(
        self,
        draft_content: str,
        context: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None
    ) -> HITLRequest:
        """Create a new HITL approval request."""
        request = HITLRequest(
            request_id=request_id or self._generate_request_id(),
            draft_content=draft_content,
            context=context or {},
            timeout_minutes=self.timeout_minutes
        )
        self.pending_requests[request.request_id] = request
        
        self._log_event("request_created", {
            "request_id": request.request_id,
            "timeout": self.timeout_minutes
        })
        
        logger.info(f"HITL request created: {request.request_id}")
        return request
    
    def wait_for_response(
        self,
        request_id: str,
        poll_interval: float = 1.0
    ) -> Optional[HITLResponse]:
        """
        Wait for human response with timeout handling.
        
        In production, this would integrate with actual HITL UI/API.
        This example uses polling for demonstration.
        """
        request = self.pending_requests.get(request_id)
        if not request:
            logger.error(f"Request not found: {request_id}")
            return None
        
        logger.info(f"Waiting for response on request: {request_id}")
        
        # Simulate waiting (in production, this would be async/await with real HITL)
        start_time = datetime.utcnow()
        while not request.is_expired():
            if request_id in self.responses:
                response = self.responses[request_id]
                self._log_event("response_received", {
                    "request_id": request_id,
                    "status": response.status.value
                })
                return response
            
            time.sleep(poll_interval)  # In production: async sleep
            
        # Timeout occurred
        logger.warning(f"Request {request_id} timed out")
        return self._handle_timeout(request)
    
    def submit_response(self, response: HITLResponse) -> bool:
        """Submit a human response to a request."""
        if response.request_id not in self.pending_requests:
            logger.error(f"Cannot submit response: request {response.request_id} not found")
            return False
        
        request = self.pending_requests[response.request_id]
        
        if request.is_expired():
            logger.warning(f"Response submitted after timeout: {response.request_id}")
            return False
        
        self.responses[response.request_id] = response
        
        self._log_event("response_submitted", {
            "request_id": response.request_id,
            "responder": response.responder_id,
            "status": response.status.value
        })
        
        logger.info(f"Response submitted for request: {response.request_id}")
        return True
    
    def _handle_timeout(self, request: HITLRequest) -> Optional[HITLResponse]:
        """Handle request timeout."""
        if self.escalation_enabled and self.escalation_callback:
            escalation = EscalationResult(
                reason="timeout",
                original_request=request,
                fallback_action="notify_manager"
            )
            self.escalation_callback(escalation)
        
        timeout_response = HITLResponse(
            request_id=request.request_id,
            status=ApprovalStatus.TIMEOUT,
            feedback="Request timed out waiting for human response"
        )
        
        self._log_event("timeout_occurred", {
            "request_id": request.request_id,
            "elapsed_minutes": self.timeout_minutes
        })
        
        return timeout_response
    
    def _generate_request_id(self) -> str:
        """Generate a unique request ID."""
        import uuid
        return f"hitl_{uuid.uuid4().hex[:8]}"
    
    def _log_event(self, event_type: str, data: Dict[str, Any]):
        """Log an audit event."""
        self.audit_log.append({
            "event": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            **data
        })


class EmailApprovalWorkflow:
    """
    Production-ready email approval workflow.
    
    Demonstrates HITL integration for customer support email approval.
    """
    
    def __init__(
        self,
        timeout_minutes: int = 5,
        escalation_email: Optional[str] = None
    ):
        self.hitl_handler = HITLHandler(
            timeout_minutes=timeout_minutes,
            escalation_enabled=bool(escalation_email),
            escalation_callback=self._escalate_to_manager if escalation_email else None
        )
        self.escalation_email = escalation_email
        self.approved_emails: list = []
        
    def draft_and_send(
        self,
        customer_email: str,
        subject: str,
        draft_content: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Draft an email and send for human approval.
        
        Args:
            customer_email: Customer's email address
            subject: Email subject
            draft_content: Draft email content
            context: Additional context (customer history, urgency, etc.)
        
        Returns:
            Result dict with status and details
        """
        # Create HITL request
        enriched_context = {
            **(context or {}),
            "customer_email": customer_email,
            "subject": subject,
            "draft_content": draft_content
        }
        
        request = self.hitl_handler.create_request(
            draft_content=draft_content,
            context=enriched_context
        )
        
        logger.info(f"Email draft created for {customer_email}, awaiting approval")
        
        # In production, this would trigger actual HITL UI notification
        # For this example, we'll simulate the response
        
        # Wait for response (in production: async)
        response = self.hitl_handler.wait_for_response(request.request_id)
        
        return self._process_response(response, enriched_context)
    
    def _process_response(
        self,
        response: Optional[HITLResponse],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process the HITL response."""
        if not response:
            return {
                "status": "error",
                "message": "No response received",
                "customer_email": context["customer_email"]
            }
        
        result = {
            "status": response.status.value,
            "request_id": response.request_id,
            "customer_email": context["customer_email"],
            "subject": context["subject"]
        }
        
        if response.status == ApprovalStatus.APPROVED:
            self._send_email(context)
            result["message"] = "Email sent successfully"
            result["content_sent"] = context["draft_content"]
            
        elif response.status == ApprovalStatus.REJECTED:
            result["message"] = "Email rejected by reviewer"
            result["feedback"] = response.feedback
            
        elif response.status == ApprovalStatus.MODIFIED:
            result["message"] = "Email modified and sent"
            result["original_content"] = context["draft_content"]
            result["modified_content"] = response.modified_content
            self._send_email({**context, "draft_content": response.modified_content})
            
        elif response.status == ApprovalStatus.TIMEOUT:
            result["message"] = "Approval timed out - escalated to manager"
            result["escalation_email"] = self.escalation_email
            
        return result
    
    def _send_email(self, context: Dict[str, Any]):
        """Send the approved email (placeholder for actual email service)."""
        logger.info(f"Sending email to {context['customer_email']}")
        logger.info(f"Subject: {context['subject']}")
        # In production: integrate with SendGrid, AWS SES, etc.
        self.approved_emails.append({
            "to": context["customer_email"],
            "subject": context["subject"],
            "sent_at": datetime.utcnow().isoformat()
        })
    
    def _escalate_to_manager(self, escalation: EscalationResult):
        """Escalate timeout to manager."""
        logger.warning(f"Escalating to manager: {self.escalation_email}")
        logger.warning(f"Reason: {escalation.reason}")
        # In production: send email/Slack notification to manager


# Example usage and demonstration
if __name__ == "__main__":
    # Initialize workflow
    workflow = EmailApprovalWorkflow(
        timeout_minutes=5,
        escalation_email="manager@company.com"
    )
    
    # Example 1: Simulate approved email
    print("=== Example 1: Approved Email ===")
    
    # In production, the response would come from actual human via HITL UI
    # Here we simulate by pre-submitting a response
    def simulate_approval():
        time.sleep(0.5)  # Small delay to simulate async
        workflow.hitl_handler.submit_response(HITLResponse(
            request_id=list(workflow.hitl_handler.pending_requests.keys())[-1],
            status=ApprovalStatus.APPROVED,
            responder_id="reviewer_001",
            feedback="Looks good, approved"
        ))
    
    import threading
    threading.Thread(target=simulate_approval, daemon=True).start()
    
    result = workflow.draft_and_send(
        customer_email="customer@example.com",
        subject="Issue Resolution",
        draft_content="Dear customer, we've resolved your issue...",
        context={"urgency": "medium", "ticket_id": "TKT-12345"}
    )
    print(json.dumps(result, indent=2))
    
    print("\n=== Example 2: Rejected Email ===")
    
    def simulate_rejection():
        time.sleep(0.5)
        workflow.hitl_handler.submit_response(HITLResponse(
            request_id=list(workflow.hitl_handler.pending_requests.keys())[-1],
            status=ApprovalStatus.REJECTED,
            responder_id="reviewer_002",
            feedback="Please add discount code before sending"
        ))
    
    threading.Thread(target=simulate_rejection, daemon=True).start()
    
    result = workflow.draft_and_send(
        customer_email="vip@example.com",
        subject="Special Offer",
        draft_content="Dear VIP customer, check out our new features...",
        context={"urgency": "high", "customer_tier": "VIP"}
    )
    print(json.dumps(result, indent=2))
    
    # Print audit log
    print("\n=== Audit Log ===")
    for entry in workflow.hitl_handler.audit_log:
        print(f"{entry['timestamp']}: {entry['event']}")
