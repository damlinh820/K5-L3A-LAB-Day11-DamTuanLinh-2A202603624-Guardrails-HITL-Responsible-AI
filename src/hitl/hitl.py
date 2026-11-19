"""
Lab 11 — Optional enrichment: Human-in-the-Loop Design
  (Không chấm — tham khảo. Tóm tắt nộp do scripts/grade.py tự sinh,
   không viết report/*.md tay.)
  - Confidence Router
  - 3 HITL decision points
"""
from dataclasses import dataclass


# ============================================================
# Optional enrichment: ConfidenceRouter (không chấm)
#
# Route agent responses based on confidence scores:
#   - HIGH (>= 0.9): Auto-send to user
#   - MEDIUM (0.7 - 0.9): Queue for human review
#   - LOW (< 0.7): Escalate to human immediately
#
# Special case: if the action is HIGH_RISK (e.g., money transfer,
# account deletion), ALWAYS escalate regardless of confidence.
#
# Implement the route() method.
# ============================================================

HIGH_RISK_ACTIONS = [
    "transfer_money",
    "close_account",
    "change_password",
    "delete_data",
    "update_personal_info",
]


@dataclass
class RoutingDecision:
    """Result of the confidence router."""
    action: str          # "auto_send", "queue_review", "escalate"
    confidence: float
    reason: str
    priority: str        # "low", "normal", "high"
    requires_human: bool


class ConfidenceRouter:
    """Route agent responses based on confidence and risk level.

    Thresholds:
        HIGH:   confidence >= 0.9 -> auto-send
        MEDIUM: 0.7 <= confidence < 0.9 -> queue for review
        LOW:    confidence < 0.7 -> escalate to human

    High-risk actions always escalate regardless of confidence.
    """

    HIGH_THRESHOLD = 0.9
    MEDIUM_THRESHOLD = 0.7

    def route(self, response: str, confidence: float,
              action_type: str = "general") -> RoutingDecision:
        """Route a response based on confidence score and action type.

        Args:
            response: The agent's response text
            confidence: Confidence score between 0.0 and 1.0
            action_type: Type of action (e.g., "general", "transfer_money")

        Returns:
            RoutingDecision with routing action and metadata
        """
        # Optional: Implement routing logic
        #
        # 1. Check if action_type is in HIGH_RISK_ACTIONS
        #    -> If yes: always escalate (action="escalate", priority="high",
        #       requires_human=True, reason="High-risk action: {action_type}")
        #
        # 2. Check confidence thresholds:
        #    - confidence >= 0.9:
        #      action="auto_send", priority="low",
        #      requires_human=False, reason="High confidence"
        #
        #    - 0.7 <= confidence < 0.9:
        #      action="queue_review", priority="normal",
        #      requires_human=True, reason="Medium confidence — needs review"
        #
        #    - confidence < 0.7:
        #      action="escalate", priority="high",
        #      requires_human=True, reason="Low confidence — escalating"

        if not 0.0 <= confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        if action_type in HIGH_RISK_ACTIONS:
            return RoutingDecision(
                "escalate", confidence, f"High-risk action: {action_type}",
                "high", True,
            )
        if confidence >= self.HIGH_THRESHOLD:
            return RoutingDecision(
                "auto_send", confidence, "High confidence", "low", False
            )
        if confidence >= self.MEDIUM_THRESHOLD:
            return RoutingDecision(
                "queue_review", confidence,
                "Medium confidence — needs review", "normal", True,
            )
        return RoutingDecision(
            "escalate", confidence, "Low confidence — escalating", "high", True
        )


# ============================================================
# Optional enrichment: 3 HITL decision points (không chấm)
# Không bắt buộc điền. Tóm tắt bài nộp: chạy scripts/grade.py
# (tự sinh lab_report.md) — không viết report tay.
#
# For each decision point, define:
# - trigger: What condition activates this HITL check?
# - hitl_model: Which model? (human-in-the-loop, human-on-the-loop,
#   human-as-tiebreaker)
# - context_needed: What info does the human reviewer need?
# - example: A concrete scenario
# - approval_path: What approve/reject/timeout decision is recorded?
# - audit_fields: Which correlation ID, intent and proposed action/diff are logged?
#
# Think about real banking scenarios where human judgment is critical.
# ============================================================

hitl_decision_points = [
    {
        "id": 1,
        "name": "High-risk banking action approval",
        "trigger": "Transfer, account closure, password change, data deletion, or PII update.",
        "hitl_model": "human-in-the-loop",
        "context_needed": "Authenticated customer, intent, amount, beneficiary, risk signals, and proposed action diff.",
        "example": "A customer requests a 50,000,000 VND transfer to a new beneficiary.",
        "approval_path": "Reviewer approves with a recorded approval ID, rejects with a reason, or timeout defaults to deny.",
        "audit_fields": "correlation_id, user_id, action, destination, payload hash, risk score, reviewer_id, decision, timestamp",
    },
    {
        "id": 2,
        "name": "Low-confidence or conflicting answer",
        "trigger": "Confidence below 0.9, conflicting retrieved sources, or unsupported financial claim.",
        "hitl_model": "human-as-tiebreaker",
        "context_needed": "Customer question, proposed response, cited sources, confidence, and conflicting facts.",
        "example": "Two documents contain different current home-loan rates.",
        "approval_path": "Reviewer selects a verified answer, requests clarification, or rejects; timeout withholds the response.",
        "audit_fields": "correlation_id, question, sources, confidence, proposed_response, reviewer_id, decision, rationale",
    },
    {
        "id": 3,
        "name": "Security alert and potential data leak",
        "trigger": "Repeated injection attempts, output redaction, unusual rate limits, or a suspected secret/PII leak.",
        "hitl_model": "human-on-the-loop",
        "context_needed": "Redacted transcript, matched rule, source provenance, account/session metadata, and recent alert history.",
        "example": "A session repeatedly asks to encode the database host in Base64.",
        "approval_path": "Reviewer closes as benign, blocks the session, or escalates incident response; timeout keeps the session restricted.",
        "audit_fields": "correlation_id, session_id, rule_id, redacted evidence, alert count, reviewer_id, disposition, timestamp",
    },
]


# ============================================================
# Quick tests
# ============================================================

def test_confidence_router():
    """Test ConfidenceRouter with sample scenarios."""
    router = ConfidenceRouter()

    test_cases = [
        ("Balance inquiry", 0.95, "general"),
        ("Interest rate question", 0.82, "general"),
        ("Ambiguous request", 0.55, "general"),
        ("Transfer $50,000", 0.98, "transfer_money"),
        ("Close my account", 0.91, "close_account"),
    ]

    print("Testing ConfidenceRouter:")
    print("=" * 80)
    print(f"{'Scenario':<25} {'Conf':<6} {'Action Type':<18} {'Decision':<15} {'Priority':<10} {'Human?'}")
    print("-" * 80)

    for scenario, conf, action_type in test_cases:
        decision = router.route(scenario, conf, action_type)
        print(
            f"{scenario:<25} {conf:<6.2f} {action_type:<18} "
            f"{decision.action:<15} {decision.priority:<10} "
            f"{'Yes' if decision.requires_human else 'No'}"
        )

    print("=" * 80)


def test_hitl_points():
    """Display HITL decision points."""
    print("\nHITL Decision Points:")
    print("=" * 60)
    for point in hitl_decision_points:
        print(f"\n  Decision Point #{point['id']}: {point['name']}")
        print(f"    Trigger:  {point['trigger']}")
        print(f"    Model:    {point['hitl_model']}")
        print(f"    Context:  {point['context_needed']}")
        print(f"    Example:  {point['example']}")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    test_confidence_router()
    test_hitl_points()
