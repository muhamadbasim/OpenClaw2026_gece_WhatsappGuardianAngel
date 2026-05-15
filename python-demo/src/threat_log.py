"""Threat log storage layer for the WhatsApp Scam & Phishing Guardian Agent.

Manages all database operations for threat records including persistence,
querying, statistics generation, and retry logic for failed writes.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session, sessionmaker

from src.models import IncomingMessage, ThreatAssessment, ThreatLevel
from src.storage_models import Base, ThreatRecord

logger = logging.getLogger(__name__)


class ThreatLog:
    """Manages all database operations for threat records.

    Provides methods for logging threats, querying historical data,
    generating statistics, and handling write failures via a retry queue.
    """

    def __init__(self, database_url: Optional[str] = None) -> None:
        """Initialize the ThreatLog with a database connection.

        Args:
            database_url: SQLAlchemy database URL. Defaults to config's DATABASE_URL.
        """
        if database_url is None:
            from src.config import get_settings

            database_url = get_settings().DATABASE_URL

        self._engine = create_engine(database_url)
        self._session_factory = sessionmaker(bind=self._engine)
        self._retry_queue: list[dict] = []

    def init_db(self) -> None:
        """Create all database tables defined in the models.

        Safe to call multiple times; existing tables are not modified.
        """
        Base.metadata.create_all(self._engine)

    def log_threat(
        self, assessment: ThreatAssessment, message: IncomingMessage
    ) -> Optional[ThreatRecord]:
        """Persist a threat assessment and its associated message to the database.

        On failure, the record data is added to the retry queue for later processing.

        Args:
            assessment: The threat analysis result.
            message: The original incoming message that was analyzed.

        Returns:
            The created ThreatRecord on success, or None on failure.
        """
        record_data = {
            "message_content": message.text,
            "sender_id": message.sender_id,
            "chat_id": message.chat_id,
            "timestamp": message.timestamp,
            "threat_level": assessment.threat_level.value,
            "threat_type": assessment.threat_type.value if assessment.threat_type else None,
            "confidence": assessment.confidence,
            "analysis_details": assessment.explanation,
            "reasoning_chain": json.dumps(assessment.reasoning_chain),
        }

        try:
            with self._session_factory() as session:
                record = ThreatRecord(**record_data)
                session.add(record)
                session.commit()
                session.refresh(record)
                logger.info(
                    "Logged threat record id=%d, level=%s, chat=%s",
                    record.id,
                    record.threat_level,
                    record.chat_id,
                )
                return record
        except Exception as e:
            logger.error("Failed to log threat record: %s", e)
            self._retry_queue.append(record_data)
            return None

    def get_threats_since(self, since: datetime) -> list[ThreatRecord]:
        """Retrieve all threat records created since the given timestamp.

        Args:
            since: The start datetime for the query (inclusive).

        Returns:
            A list of ThreatRecord objects ordered by timestamp.
        """
        with self._session_factory() as session:
            records = (
                session.query(ThreatRecord)
                .filter(ThreatRecord.timestamp >= since)
                .order_by(ThreatRecord.timestamp)
                .all()
            )
            # Detach from session so they can be used after session closes
            session.expunge_all()
            return records

    def get_threat_stats(self, since: datetime) -> dict:
        """Generate statistics for threats recorded since the given timestamp.

        Args:
            since: The start datetime for the statistics window.

        Returns:
            A dictionary containing:
                - total: Total number of threat records
                - by_threat_type: Breakdown of counts by threat type
                - by_threat_level: Breakdown of counts by threat level
                - top_targeted_members: Top 3 most targeted members (by sender_id count)
        """
        with self._session_factory() as session:
            # Total count
            total = (
                session.query(func.count(ThreatRecord.id))
                .filter(ThreatRecord.timestamp >= since)
                .scalar()
            ) or 0

            # Breakdown by threat_type
            type_rows = (
                session.query(
                    ThreatRecord.threat_type,
                    func.count(ThreatRecord.id),
                )
                .filter(ThreatRecord.timestamp >= since)
                .group_by(ThreatRecord.threat_type)
                .all()
            )
            by_threat_type: dict[str, int] = {
                (row[0] or "unknown"): row[1] for row in type_rows
            }

            # Breakdown by threat_level
            level_rows = (
                session.query(
                    ThreatRecord.threat_level,
                    func.count(ThreatRecord.id),
                )
                .filter(ThreatRecord.timestamp >= since)
                .group_by(ThreatRecord.threat_level)
                .all()
            )
            by_threat_level: dict[str, int] = {row[0]: row[1] for row in level_rows}

            # Top 3 targeted members (by sender_id count)
            member_rows = (
                session.query(
                    ThreatRecord.sender_id,
                    func.count(ThreatRecord.id).label("count"),
                )
                .filter(ThreatRecord.timestamp >= since)
                .group_by(ThreatRecord.sender_id)
                .order_by(func.count(ThreatRecord.id).desc())
                .limit(3)
                .all()
            )
            top_targeted_members: list[dict[str, object]] = [
                {"sender_id": row[0], "count": row[1]} for row in member_rows
            ]

        return {
            "total": total,
            "by_threat_type": by_threat_type,
            "by_threat_level": by_threat_level,
            "top_targeted_members": top_targeted_members,
        }

    def _process_retry_queue(self) -> int:
        """Process queued entries that previously failed to write.

        Attempts to write all entries in the retry queue to the database.
        Successfully written entries are removed from the queue; entries
        that fail again remain queued for the next retry attempt.

        Returns:
            The number of entries successfully written.
        """
        if not self._retry_queue:
            return 0

        succeeded = 0
        remaining: list[dict] = []

        for record_data in self._retry_queue:
            try:
                with self._session_factory() as session:
                    record = ThreatRecord(**record_data)
                    session.add(record)
                    session.commit()
                    succeeded += 1
                    logger.info(
                        "Retry succeeded for threat record: chat=%s, level=%s",
                        record_data.get("chat_id"),
                        record_data.get("threat_level"),
                    )
            except Exception as e:
                logger.error("Retry failed for threat record: %s", e)
                remaining.append(record_data)

        self._retry_queue = remaining
        logger.info(
            "Retry queue processed: %d succeeded, %d remaining",
            succeeded,
            len(remaining),
        )
        return succeeded
