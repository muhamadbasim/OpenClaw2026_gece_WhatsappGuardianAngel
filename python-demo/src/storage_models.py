"""SQLAlchemy models for the WhatsApp Scam & Phishing Guardian Agent.

Defines the ThreatRecord model for persisting threat analysis results.
Uses SQLAlchemy 2.0 declarative style with mapped_column.
"""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Float, Integer, String, Text, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass


class ThreatRecord(Base):
    """Represents a single threat analysis record stored in the database.

    Each record captures the full context of a message that was analyzed,
    including the classification result, confidence score, and reasoning.
    """

    __tablename__ = "threat_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    message_content: Mapped[str] = mapped_column(Text, nullable=False)
    sender_id: Mapped[str] = mapped_column(String(100), nullable=False)
    chat_id: Mapped[str] = mapped_column(String(100), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    threat_level: Mapped[str] = mapped_column(String(20), nullable=False)
    threat_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    analysis_details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reasoning_chain: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self) -> str:
        return (
            f"<ThreatRecord(id={self.id}, chat_id={self.chat_id!r}, "
            f"threat_level={self.threat_level!r}, confidence={self.confidence})>"
        )
