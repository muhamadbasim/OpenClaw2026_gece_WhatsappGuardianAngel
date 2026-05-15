"""Data models for the WhatsApp Scam & Phishing Guardian Agent.

This module defines the core data structures used throughout the system
for message processing, threat assessment, and alert generation.
"""

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


class ThreatLevel(Enum):
    """Classification levels for message threat severity.

    Used by the analysis pipeline to categorize messages into
    actionable threat tiers that determine alerting behavior.
    """

    SAFE = "safe"
    SUSPICIOUS = "suspicious"
    DANGEROUS = "dangerous"


class ThreatType(Enum):
    """Categories of threats detected by the analysis agents.

    Each type corresponds to a specific attack vector or scam pattern
    that the system is trained to identify.
    """

    PHISHING_LINK = "phishing_link"
    SOCIAL_ENGINEERING = "social_engineering"
    IMPERSONATION = "impersonation"
    MALICIOUS_REDIRECT = "malicious_redirect"
    FINANCIAL_SCAM = "financial_scam"


@dataclass
class IncomingMessage:
    """Represents a message received from WhatsApp.

    Contains all relevant metadata extracted from the raw WhatsApp API
    response, including pre-extracted URLs for efficient processing.
    """

    message_id: str
    chat_id: str
    sender_id: str
    sender_name: str
    text: str
    timestamp: datetime
    urls: list[str] = field(default_factory=list)


@dataclass
class ThreatAssessment:
    """Result of threat analysis performed by one or more agents.

    Captures the classification decision along with supporting evidence
    and the reasoning chain used to reach the conclusion.
    """

    threat_level: ThreatLevel
    threat_type: Optional[ThreatType]
    confidence: float  # 0.0 to 1.0
    explanation: str
    reasoning_chain: list[str] = field(default_factory=list)
    evidence: dict = field(default_factory=dict)


@dataclass
class AlertMessage:
    """A formatted alert message ready to be sent to a WhatsApp chat.

    Contains all the information needed by the Alert Agent to deliver
    a warning to group members about a detected threat.
    """

    chat_id: str
    threat_type: str
    explanation: str
    recommended_action: str
    mention_admin: bool
    formatted_text: str
