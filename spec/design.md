# Design Document

## Overview

The WhatsApp Scam & Phishing Guardian Agent is a multi-agent system built with Python, using LangChain/CrewAI for agent orchestration, Baileys (via a Node.js bridge) or Whapi.cloud for WhatsApp connectivity, and external threat intelligence APIs for link analysis. The system runs as a Docker-composed service with an autonomous event loop that processes every incoming message through a classification → analysis → alert → log pipeline.

## Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Guardian System (Orchestrator)             │
│                                                              │
│  ┌──────────────┐    ┌──────────────────────────────────┐   │
│  │  WhatsApp    │    │        Agent Pipeline             │   │
│  │  Connector   │───▶│                                   │   │
│  │  (Baileys/   │    │  ┌─────────┐   ┌─────────────┐  │   │
│  │   Whapi)     │    │  │ Message │   │    Link      │  │   │
│  └──────────────┘    │  │Analyzer │   │   Scanner    │  │   │
│                      │  │  Agent  │   │    Agent     │  │   │
│                      │  └────┬────┘   └──────┬───────┘  │   │
│                      │       │               │          │   │
│                      │       └───────┬───────┘          │   │
│                      │               ▼                  │   │
│                      │        ┌─────────────┐           │   │
│                      │        │   Alert     │           │   │
│                      │        │   Agent     │           │   │
│                      │        └──────┬──────┘           │   │
│                      │               │                  │   │
│                      │               ▼                  │   │
│                      │        ┌─────────────┐           │   │
│                      │        │  Threat Log │           │   │
│                      └────────┴─────────────┴───────────┘   │
│                                                              │
│  ┌──────────────┐    ┌──────────────────────────────────┐   │
│  │  Scheduler   │───▶│        Report Agent               │   │
│  │ (APScheduler)│    └──────────────────────────────────┘   │
│  └──────────────┘                                           │
└─────────────────────────────────────────────────────────────┘
```

### Component Design

#### 1. WhatsApp Connector (`src/connector/whatsapp_connector.py`)

Manages the WhatsApp connection lifecycle using Whapi.cloud REST API (simpler for hackathon) or a Baileys Node.js subprocess bridge.

- Maintains persistent webhook/polling connection
- Emits message events to the Guardian System event queue
- Handles reconnection logic with exponential backoff
- Extracts structured message data (text, sender, timestamp, media, URLs)

#### 2. Guardian System Orchestrator (`src/orchestrator/guardian.py`)

The central coordinator that manages the autonomous loop and agent pipeline.

- Runs an async event loop consuming messages from the connector
- Routes messages through the agent pipeline based on content type
- Aggregates threat assessments from multiple agents
- Manages agent health via heartbeat monitoring
- Implements agent restart on failure detection

#### 3. Link Scanner Agent (`src/agents/link_scanner.py`)

Specialized agent for URL threat analysis with external tool integration.

- Extracts URLs using regex patterns from message text
- Calls VirusTotal API for domain reputation scoring
- Calls URLScan.io for phishing page detection
- Follows redirect chains (HTTP HEAD requests) up to 10 hops
- Produces a ThreatAssessment with level and evidence

#### 4. Message Analyzer Agent (`src/agents/message_analyzer.py`)

LLM-powered agent for detecting social engineering and scam patterns.

- Uses structured prompts with GPT-4o/Groq for classification
- Detects patterns: urgency, authority impersonation, emotional manipulation, financial lures
- Compares sender display name against known admin/contact names
- Returns classification with confidence score and reasoning chain

#### 5. Alert Agent (`src/agents/alert_agent.py`)

Responsible for composing and delivering warning messages.

- Formats alerts using WhatsApp markdown (bold, italic, emojis)
- Includes threat type, explanation, and recommended action
- Tags admin for DANGEROUS threats
- Implements retry logic (3 attempts, 2s interval)

#### 6. Report Agent (`src/agents/report_agent.py`)

Generates periodic security summaries from the threat log.

- Scheduled via APScheduler (weekly cron trigger)
- Queries threat log for the reporting period
- Computes statistics: total threats, breakdown by type, most targeted members
- Compares with previous period for trend analysis
- Formats as a structured WhatsApp message

#### 7. Threat Log (`src/storage/threat_log.py`)

Persistent storage layer for all threat events.

- SQLite for hackathon simplicity (PostgreSQL-ready via SQLAlchemy)
- Schema: id, message_content, sender_id, chat_id, timestamp, threat_level, threat_type, confidence, analysis_details, reasoning_chain
- Write queue with retry for resilience
- Query interface for report generation

### Data Models

```python
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

class ThreatLevel(Enum):
    SAFE = "safe"
    SUSPICIOUS = "suspicious"
    DANGEROUS = "dangerous"

class ThreatType(Enum):
    PHISHING_LINK = "phishing_link"
    SOCIAL_ENGINEERING = "social_engineering"
    IMPERSONATION = "impersonation"
    MALICIOUS_REDIRECT = "malicious_redirect"
    FINANCIAL_SCAM = "financial_scam"

@dataclass
class IncomingMessage:
    message_id: str
    chat_id: str
    sender_id: str
    sender_name: str
    text: str
    timestamp: datetime
    urls: list[str]

@dataclass
class ThreatAssessment:
    threat_level: ThreatLevel
    threat_type: Optional[ThreatType]
    confidence: float  # 0.0 to 1.0
    explanation: str
    reasoning_chain: list[str]
    evidence: dict

@dataclass
class AlertMessage:
    chat_id: str
    threat_type: str
    explanation: str
    recommended_action: str
    mention_admin: bool
    formatted_text: str
```

### Technology Stack

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Language | Python 3.11+ | Fast prototyping, rich AI/ML ecosystem |
| WhatsApp API | Whapi.cloud | REST-based, no binary dependencies, quick setup |
| Agent Framework | LangChain | Tool-calling, chains, structured output |
| LLM | GPT-4o (primary), Groq (fallback) | Reasoning quality + speed fallback |
| Link Analysis | VirusTotal API, URLScan.io | Industry-standard threat intelligence |
| Database | SQLite + SQLAlchemy | Zero-config for hackathon, ORM for portability |
| Scheduler | APScheduler | Lightweight, in-process scheduling |
| Deployment | Docker Compose | Single-command deployment |
| Config | python-dotenv | Environment variable management |

### Project Structure

```
whatsapp-scam-guardian/
├── docker-compose.yml
├── Dockerfile
├── .env.example
├── requirements.txt
├── README.md
├── src/
│   ├── __init__.py
│   ├── main.py                    # Entry point, starts Guardian System
│   ├── config.py                  # Configuration from env vars
│   ├── connector/
│   │   ├── __init__.py
│   │   └── whatsapp_connector.py  # WhatsApp connection management
│   ├── orchestrator/
│   │   ├── __init__.py
│   │   └── guardian.py            # Main orchestrator + event loop
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── link_scanner.py        # Link Scanner Agent
│   │   ├── message_analyzer.py    # Message Analyzer Agent
│   │   ├── alert_agent.py         # Alert Agent
│   │   └── report_agent.py        # Report Agent
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── models.py              # SQLAlchemy models
│   │   └── threat_log.py          # Threat log operations
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── virustotal.py          # VirusTotal API wrapper
│   │   ├── urlscan.py             # URLScan.io API wrapper
│   │   └── url_resolver.py        # Redirect chain follower
│   └── utils/
│       ├── __init__.py
│       ├── url_extractor.py       # URL extraction from text
│       └── formatter.py           # WhatsApp message formatting
├── tests/
│   ├── __init__.py
│   ├── test_url_extractor.py
│   ├── test_link_scanner.py
│   ├── test_message_analyzer.py
│   ├── test_alert_agent.py
│   ├── test_threat_log.py
│   └── test_guardian.py
└── scripts/
    └── seed_test_messages.py      # Demo seed data
```

## Correctness Properties

### Property 1: URL Extraction Completeness (Req 1.3, 2.1)

For all messages containing URLs, the URL extractor must find every valid URL in the text. The count of extracted URLs must equal the count of actual URLs present.

**Type:** Invariant
**Testable:** Yes - property-based test with generated messages containing random valid URLs

### Property 2: Threat Level Assignment Totality (Req 2.6, 3.4)

For all messages that complete the analysis pipeline, every message must receive exactly one Threat_Level classification. No message may exit the pipeline without a classification.

**Type:** Invariant
**Testable:** Yes - property-based test ensuring all processed messages have a valid ThreatLevel

### Property 3: Confidence Score Bounds (Req 3.4)

For all threat assessments produced by the Message_Analyzer_Agent, the confidence score must be in the range [0.0, 1.0] inclusive.

**Type:** Invariant
**Testable:** Yes - property-based test with generated assessment outputs

### Property 4: Threat Level Aggregation Monotonicity (Req 8.4)

When multiple agents produce threat assessments for the same message, the aggregated Threat_Level must be greater than or equal to the maximum individual Threat_Level (SAFE < SUSPICIOUS < DANGEROUS).

**Type:** Invariant
**Testable:** Yes - property-based test with generated combinations of threat levels

### Property 5: Alert Message Completeness (Req 4.2)

For all alert messages generated by the Alert_Agent, the message must contain: a threat type label, an explanation string with length > 0, and a recommended action from the valid set {ignore, block sender, report}.

**Type:** Invariant
**Testable:** Yes - property-based test with generated threat assessments as input

### Property 6: Redirect Chain Bounded Length (Req 2.4, 2.5)

For all URLs processed by the Link_Scanner_Agent, the recorded redirect chain must have at most 11 entries (initial URL + 10 redirects). If the chain reaches 11 entries, the URL must be classified as SUSPICIOUS or higher.

**Type:** Invariant
**Testable:** Yes - property-based test with mocked redirect responses

### Property 7: Threat Log Record Completeness (Req 5.1)

For all entries written to the Threat_Log, every required field (message_content, sender_id, chat_id, timestamp, threat_level, threat_type, confidence, analysis_details) must be non-null.

**Type:** Invariant
**Testable:** Yes - property-based test with generated threat events

### Property 8: Message Pipeline No-Drop (Req 1.4, 7.2)

For all messages ingested by the Guardian_System, the count of messages entering the pipeline must equal the count of messages that complete processing (either classified as SAFE and logged, or classified as SUSPICIOUS/DANGEROUS and alerted+logged).

**Type:** Invariant
**Testable:** Yes - property-based test with generated message sequences

### Property 9: Admin Mention Consistency (Req 4.3)

For all alert messages where the source threat is classified as DANGEROUS, the formatted alert text must contain an admin mention. For all alerts where the source threat is SUSPICIOUS, the alert must not contain an admin mention.

**Type:** Metamorphic
**Testable:** Yes - property-based test with generated threat levels

### Property 10: Report Statistics Consistency (Req 6.2)

For all generated reports, the sum of threats broken down by type must equal the total threats count reported. The "most targeted members" list must contain at most 3 entries.

**Type:** Invariant
**Testable:** Yes - property-based test with generated threat log data

## Handling Ambiguity

1. **WhatsApp API choice**: Defaulted to Whapi.cloud (REST-based) for hackathon simplicity. Baileys requires a Node.js subprocess bridge which adds complexity for a 12-hour sprint.

2. **LLM fallback strategy**: GPT-4o is primary for quality; Groq is fallback for speed/availability. If both fail, the message is classified as SUSPICIOUS (fail-safe).

3. **"Most targeted members" definition**: Defined as members who received the most messages classified as SUSPICIOUS or DANGEROUS in the reporting period.

4. **Heartbeat scope**: Heartbeat logs are internal system health indicators, not sent to WhatsApp chats.

5. **Message queue behavior**: Messages are processed sequentially (FIFO) to maintain ordering guarantees. Parallel processing is a future optimization.
