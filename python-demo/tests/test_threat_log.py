"""Tests for the ThreatLog storage layer.

Covers record creation, date-range filtering, statistics generation,
retry-on-failure logic, and a property-based test for field completeness.

**Validates: Requirements 5.1**
"""

import json
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from sqlalchemy.exc import OperationalError

from src.models import IncomingMessage, ThreatAssessment, ThreatLevel, ThreatType
from src.threat_log import ThreatLog


@pytest.fixture
def threat_log():
    """Create a ThreatLog instance backed by an in-memory SQLite database."""
    log = ThreatLog(database_url="sqlite:///:memory:")
    log.init_db()
    return log


def _make_message(
    text: str = "Check this out: http://evil.com",
    sender_id: str = "sender_1",
    chat_id: str = "chat_1",
    timestamp: datetime | None = None,
) -> IncomingMessage:
    """Helper to create an IncomingMessage with sensible defaults."""
    return IncomingMessage(
        message_id="msg_001",
        chat_id=chat_id,
        sender_id=sender_id,
        sender_name="Test User",
        text=text,
        timestamp=timestamp or datetime.now(timezone.utc),
        urls=["http://evil.com"],
    )


def _make_assessment(
    threat_level: ThreatLevel = ThreatLevel.SUSPICIOUS,
    threat_type: ThreatType | None = ThreatType.PHISHING_LINK,
    confidence: float = 0.85,
) -> ThreatAssessment:
    """Helper to create a ThreatAssessment with sensible defaults."""
    return ThreatAssessment(
        threat_level=threat_level,
        threat_type=threat_type,
        confidence=confidence,
        explanation="Suspicious link detected",
        reasoning_chain=["URL extracted", "Domain checked", "Flagged as phishing"],
        evidence={"domain": "evil.com"},
    )


class TestLogThreatCreatesRecord:
    """Test that log_threat persists a record with correct fields."""

    def test_log_threat_creates_record(self, threat_log: ThreatLog):
        """Verify a logged threat is persisted with all correct fields."""
        timestamp = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        message = _make_message(
            text="Win a free iPhone!",
            sender_id="scammer_42",
            chat_id="group_abc",
            timestamp=timestamp,
        )
        assessment = _make_assessment(
            threat_level=ThreatLevel.DANGEROUS,
            threat_type=ThreatType.FINANCIAL_SCAM,
            confidence=0.95,
        )

        record = threat_log.log_threat(assessment, message)

        assert record is not None
        assert record.id is not None
        assert record.message_content == "Win a free iPhone!"
        assert record.sender_id == "scammer_42"
        assert record.chat_id == "group_abc"
        # SQLite does not store timezone info, so compare naive datetimes
        assert record.timestamp.replace(tzinfo=None) == timestamp.replace(tzinfo=None)
        assert record.threat_level == "dangerous"
        assert record.threat_type == "financial_scam"
        assert record.confidence == 0.95
        assert record.analysis_details == "Suspicious link detected"
        assert json.loads(record.reasoning_chain) == [
            "URL extracted",
            "Domain checked",
            "Flagged as phishing",
        ]


class TestGetThreatsSinceFiltersByDate:
    """Test that get_threats_since correctly filters by timestamp."""

    def test_get_threats_since_filters_by_date(self, threat_log: ThreatLog):
        """Log multiple threats with different timestamps, verify date filtering."""
        base_time = datetime(2024, 6, 1, 0, 0, 0, tzinfo=timezone.utc)

        # Log threats at day 1, day 5, day 10, day 15
        timestamps = [
            base_time + timedelta(days=d) for d in [1, 5, 10, 15]
        ]
        for ts in timestamps:
            msg = _make_message(timestamp=ts)
            assessment = _make_assessment()
            threat_log.log_threat(assessment, msg)

        # Query since day 8 — should only return day 10 and day 15
        since = base_time + timedelta(days=8)
        results = threat_log.get_threats_since(since)

        assert len(results) == 2
        # SQLite does not store timezone info, so compare naive datetimes
        assert results[0].timestamp.replace(tzinfo=None) == timestamps[2].replace(tzinfo=None)  # day 10
        assert results[1].timestamp.replace(tzinfo=None) == timestamps[3].replace(tzinfo=None)  # day 15

    def test_get_threats_since_returns_empty_when_none_match(self, threat_log: ThreatLog):
        """Verify empty list when no records match the date filter."""
        past = datetime(2024, 1, 1, tzinfo=timezone.utc)
        msg = _make_message(timestamp=past)
        threat_log.log_threat(_make_assessment(), msg)

        future = datetime(2025, 1, 1, tzinfo=timezone.utc)
        results = threat_log.get_threats_since(future)
        assert results == []


class TestGetThreatStats:
    """Test that get_threat_stats returns correct totals and breakdowns."""

    def test_get_threat_stats(self, threat_log: ThreatLog):
        """Log several threats with different types/levels, verify stats."""
        base_time = datetime(2024, 6, 1, 0, 0, 0, tzinfo=timezone.utc)

        # Log 3 phishing threats from sender_a
        for i in range(3):
            msg = _make_message(
                sender_id="sender_a",
                timestamp=base_time + timedelta(hours=i),
            )
            threat_log.log_threat(
                _make_assessment(
                    threat_level=ThreatLevel.SUSPICIOUS,
                    threat_type=ThreatType.PHISHING_LINK,
                ),
                msg,
            )

        # Log 2 social engineering threats from sender_b
        for i in range(2):
            msg = _make_message(
                sender_id="sender_b",
                timestamp=base_time + timedelta(hours=3 + i),
            )
            threat_log.log_threat(
                _make_assessment(
                    threat_level=ThreatLevel.DANGEROUS,
                    threat_type=ThreatType.SOCIAL_ENGINEERING,
                ),
                msg,
            )

        # Log 1 impersonation threat from sender_c
        msg = _make_message(
            sender_id="sender_c",
            timestamp=base_time + timedelta(hours=5),
        )
        threat_log.log_threat(
            _make_assessment(
                threat_level=ThreatLevel.DANGEROUS,
                threat_type=ThreatType.IMPERSONATION,
            ),
            msg,
        )

        stats = threat_log.get_threat_stats(base_time)

        assert stats["total"] == 6
        assert stats["by_threat_type"]["phishing_link"] == 3
        assert stats["by_threat_type"]["social_engineering"] == 2
        assert stats["by_threat_type"]["impersonation"] == 1
        assert stats["by_threat_level"]["suspicious"] == 3
        assert stats["by_threat_level"]["dangerous"] == 3

        # Top targeted members: sender_a (3), sender_b (2), sender_c (1)
        top = stats["top_targeted_members"]
        assert len(top) <= 3
        assert top[0]["sender_id"] == "sender_a"
        assert top[0]["count"] == 3
        assert top[1]["sender_id"] == "sender_b"
        assert top[1]["count"] == 2
        assert top[2]["sender_id"] == "sender_c"
        assert top[2]["count"] == 1


class TestRetryOnFailure:
    """Test that failed log_threat calls queue entries and retry works."""

    def test_retry_on_failure(self, threat_log: ThreatLog):
        """Mock session to raise on first call, verify retry queue and recovery."""
        message = _make_message()
        assessment = _make_assessment()

        # Patch the session factory to raise on the first call
        original_factory = threat_log._session_factory

        call_count = {"n": 0}

        class FailingSession:
            """A session that fails on first commit."""

            def __init__(self):
                self._real_session = original_factory()

            def __enter__(self):
                call_count["n"] += 1
                if call_count["n"] == 1:
                    # Return a mock session that raises on commit
                    mock_session = MagicMock()
                    mock_session.commit.side_effect = OperationalError(
                        "database locked", None, None
                    )
                    return mock_session
                return self._real_session.__enter__()

            def __exit__(self, *args):
                if call_count["n"] > 1:
                    self._real_session.__exit__(*args)

        # Replace session factory with our failing version
        threat_log._session_factory = FailingSession

        # First call should fail and add to retry queue
        result = threat_log.log_threat(assessment, message)
        assert result is None
        assert len(threat_log._retry_queue) == 1

        # Restore the real session factory for retry
        threat_log._session_factory = original_factory

        # Process retry queue — should succeed
        succeeded = threat_log._process_retry_queue()
        assert succeeded == 1
        assert len(threat_log._retry_queue) == 0

        # Verify the record was actually persisted
        since = datetime(2020, 1, 1, tzinfo=timezone.utc)
        records = threat_log.get_threats_since(since)
        assert len(records) == 1
        assert records[0].message_content == message.text


# --- Property-Based Test ---

# Strategies for generating random ThreatAssessment and IncomingMessage data
threat_level_strategy = st.sampled_from(list(ThreatLevel))
threat_type_strategy = st.sampled_from(list(ThreatType))
confidence_strategy = st.floats(min_value=0.0, max_value=1.0, allow_nan=False)

incoming_message_strategy = st.builds(
    IncomingMessage,
    message_id=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=("L", "N"))),
    chat_id=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=("L", "N"))),
    sender_id=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=("L", "N"))),
    sender_name=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=("L", "N"))),
    text=st.text(min_size=1, max_size=200),
    timestamp=st.datetimes(
        min_value=datetime(2020, 1, 1),
        max_value=datetime(2030, 12, 31),
    ),
    urls=st.lists(st.text(min_size=1, max_size=100), max_size=5),
)

threat_assessment_strategy = st.builds(
    ThreatAssessment,
    threat_level=threat_level_strategy,
    threat_type=threat_type_strategy,
    confidence=confidence_strategy,
    explanation=st.text(min_size=1, max_size=200),
    reasoning_chain=st.lists(st.text(min_size=1, max_size=50), min_size=1, max_size=5),
    evidence=st.fixed_dictionaries({}),
)


class TestFieldCompletenessProperty:
    """Property-based test: all retrieved records have required fields non-null.

    **Validates: Requirements 5.1**
    """

    @given(
        assessment=threat_assessment_strategy,
        message=incoming_message_strategy,
    )
    @settings(max_examples=50, deadline=None)
    def test_all_required_fields_non_null(
        self, assessment: ThreatAssessment, message: IncomingMessage
    ):
        """Every logged and retrieved record must have all required fields non-null."""
        log = ThreatLog(database_url="sqlite:///:memory:")
        log.init_db()

        record = log.log_threat(assessment, message)

        # The record should be successfully created
        assert record is not None

        # Verify all required fields are non-null
        assert record.message_content is not None
        assert record.sender_id is not None
        assert record.chat_id is not None
        assert record.timestamp is not None
        assert record.threat_level is not None
        assert record.confidence is not None

        # Also verify via query retrieval
        since = datetime(2019, 1, 1, tzinfo=timezone.utc)
        retrieved = log.get_threats_since(since)
        assert len(retrieved) == 1

        retrieved_record = retrieved[0]
        assert retrieved_record.message_content is not None
        assert retrieved_record.sender_id is not None
        assert retrieved_record.chat_id is not None
        assert retrieved_record.timestamp is not None
        assert retrieved_record.threat_level is not None
        assert retrieved_record.confidence is not None
