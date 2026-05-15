# Requirements Document

## Introduction

The WhatsApp Scam & Phishing Guardian Agent is a fully autonomous multi-agent system that protects WhatsApp groups and personal chats from scams and phishing attacks. The system operates as a continuous monitoring loop: every incoming message is classified, and if suspicious, undergoes deep analysis followed by real-time alerting and logging. The system is designed for the OpenClaw Agenthon 2026 hackathon (12-hour sprint) and must demonstrate tool call capability, autonomous loop, reasoning, and decision-making in a deployable, demo-ready package.

## Glossary

- **Guardian_System**: The top-level multi-agent system that orchestrates all sub-agents and manages the autonomous monitoring loop
- **Link_Scanner_Agent**: The agent responsible for scanning URLs found in messages, checking domain reputation, detecting phishing patterns, and analyzing redirect chains
- **Message_Analyzer_Agent**: The agent responsible for detecting scam patterns in message text, including social engineering, urgency tactics, and impersonation attempts
- **Alert_Agent**: The agent responsible for sending real-time warnings to the WhatsApp group or chat with explanations of detected threats
- **Report_Agent**: The agent responsible for generating periodic security reports summarizing threats detected, attack types, and targeted members
- **WhatsApp_Connector**: The integration layer that connects to WhatsApp using Baileys or Whapi.cloud to receive and send messages
- **Threat_Log**: The persistent storage (SQLite or PostgreSQL) that records all detected threats, classifications, and analysis results
- **Threat_Level**: A classification of message risk as SAFE, SUSPICIOUS, or DANGEROUS
- **Redirect_Chain**: The sequence of URL redirections from an initial link to its final destination

## Requirements

### Requirement 1: Message Ingestion Loop

**User Story:** As a group admin, I want every incoming message to be automatically intercepted and processed, so that no scam or phishing attempt goes undetected.

#### Acceptance Criteria

1. WHEN a new message is received in a monitored chat, THE Guardian_System SHALL intercept the message within 3 seconds of delivery
2. THE WhatsApp_Connector SHALL maintain a persistent connection to WhatsApp and automatically reconnect within 10 seconds after a disconnection
3. WHEN a message is received, THE Guardian_System SHALL extract the message text, sender information, timestamp, and any embedded URLs
4. THE Guardian_System SHALL process messages sequentially without dropping any messages from the ingestion queue

### Requirement 2: Link Scanning

**User Story:** As a group member, I want every link shared in the group to be automatically scanned for phishing and malicious content, so that I am protected from clicking dangerous URLs.

#### Acceptance Criteria

1. WHEN a message containing one or more URLs is received, THE Link_Scanner_Agent SHALL extract all URLs and initiate scanning within 2 seconds
2. WHEN scanning a URL, THE Link_Scanner_Agent SHALL check the domain reputation using VirusTotal API
3. WHEN scanning a URL, THE Link_Scanner_Agent SHALL query URLScan.io to detect phishing page patterns
4. WHEN scanning a URL, THE Link_Scanner_Agent SHALL follow and record the full redirect chain up to a maximum of 10 redirects
5. IF a URL redirect chain exceeds 10 hops, THEN THE Link_Scanner_Agent SHALL classify the URL as SUSPICIOUS and halt further following
6. WHEN scanning is complete, THE Link_Scanner_Agent SHALL assign a Threat_Level (SAFE, SUSPICIOUS, or DANGEROUS) to each URL
7. IF the VirusTotal API or URLScan.io is unreachable, THEN THE Link_Scanner_Agent SHALL classify the URL as SUSPICIOUS and log the API failure

### Requirement 3: Message Content Analysis

**User Story:** As a group member, I want messages to be analyzed for scam patterns even when they contain no links, so that social engineering attacks are detected.

#### Acceptance Criteria

1. WHEN a message is received, THE Message_Analyzer_Agent SHALL analyze the text for social engineering patterns including urgency tactics, authority impersonation, and emotional manipulation
2. WHEN analyzing a message, THE Message_Analyzer_Agent SHALL use GPT-4o or Groq LLM to classify the message intent and detect deceptive language
3. WHEN a message contains impersonation indicators (mimicking admin names, official entities, or known contacts), THE Message_Analyzer_Agent SHALL flag the message as SUSPICIOUS or DANGEROUS
4. WHEN analysis is complete, THE Message_Analyzer_Agent SHALL assign a Threat_Level and provide a confidence score between 0.0 and 1.0
5. THE Message_Analyzer_Agent SHALL complete analysis within 5 seconds of receiving the message

### Requirement 4: Real-Time Alerting

**User Story:** As a group member, I want to receive immediate warnings when a scam or phishing attempt is detected, so that I can avoid interacting with dangerous content.

#### Acceptance Criteria

1. WHEN a message is classified as SUSPICIOUS or DANGEROUS, THE Alert_Agent SHALL send a warning message to the same chat within 5 seconds of classification
2. WHEN sending a warning, THE Alert_Agent SHALL include: the threat type, a human-readable explanation of why the message is dangerous, and a recommended action (ignore, block sender, report)
3. WHEN a message is classified as DANGEROUS, THE Alert_Agent SHALL mention the group admin in the warning message
4. WHILE the Alert_Agent is sending a warning, THE Alert_Agent SHALL format the message using WhatsApp-compatible formatting (bold, italic, emojis) for readability
5. IF the Alert_Agent fails to send a warning message, THEN THE Alert_Agent SHALL retry up to 3 times with a 2-second interval between attempts

### Requirement 5: Threat Logging

**User Story:** As a group admin, I want all detected threats to be logged persistently, so that I can review historical attack patterns and take action.

#### Acceptance Criteria

1. WHEN a message is classified as SUSPICIOUS or DANGEROUS, THE Guardian_System SHALL store the following in the Threat_Log: message content, sender ID, chat ID, timestamp, Threat_Level, threat type, confidence score, and analysis details
2. THE Threat_Log SHALL retain all records for a minimum of 90 days
3. IF a database write fails, THEN THE Guardian_System SHALL queue the log entry and retry within 30 seconds

### Requirement 6: Weekly Security Report

**User Story:** As a group admin, I want to receive a weekly summary of all security events, so that I can understand the threat landscape and take preventive measures.

#### Acceptance Criteria

1. WHEN 7 days have elapsed since the last report, THE Report_Agent SHALL generate a security report and send it to the group admin
2. THE Report_Agent SHALL include in the report: total threats detected, breakdown by threat type (phishing, social engineering, impersonation), top 3 most targeted members, and a trend comparison with the previous week
3. THE Report_Agent SHALL format the report as a readable WhatsApp message with sections and summary statistics
4. IF no threats were detected during the reporting period, THEN THE Report_Agent SHALL send a brief "all clear" summary confirming active monitoring

### Requirement 7: Autonomous Operation

**User Story:** As a group admin, I want the system to operate fully autonomously without requiring manual triggers, so that protection is continuous and reliable.

#### Acceptance Criteria

1. THE Guardian_System SHALL start the autonomous monitoring loop on system startup without manual intervention
2. THE Guardian_System SHALL orchestrate the agent pipeline (classify → analyze → alert → log) for each incoming message without human triggers
3. WHILE the Guardian_System is running, THE Guardian_System SHALL maintain health status and log heartbeat events every 60 seconds
4. IF any sub-agent (Link_Scanner_Agent, Message_Analyzer_Agent, Alert_Agent, Report_Agent) becomes unresponsive for more than 30 seconds, THEN THE Guardian_System SHALL restart the unresponsive agent and log the recovery event

### Requirement 8: Agent Reasoning and Decision-Making

**User Story:** As a hackathon judge, I want to see clear evidence of autonomous reasoning and tool-calling capability, so that the system demonstrates multi-agent intelligence.

#### Acceptance Criteria

1. WHEN processing a message, THE Guardian_System SHALL log the reasoning chain showing which agents were invoked, what tools were called, and what decisions were made
2. THE Link_Scanner_Agent SHALL demonstrate tool-calling capability by invoking external APIs (VirusTotal, URLScan.io) as part of its analysis workflow
3. THE Message_Analyzer_Agent SHALL demonstrate reasoning capability by providing a step-by-step explanation of why a message was classified at a given Threat_Level
4. WHEN multiple threat indicators are present in a single message, THE Guardian_System SHALL aggregate findings from all agents and produce a unified Threat_Level using the highest severity detected

### Requirement 9: Deployment and Demo Readiness

**User Story:** As a hackathon participant, I want the system to be easily deployable and demonstrable in a 2-minute video, so that it can be evaluated by judges.

#### Acceptance Criteria

1. THE Guardian_System SHALL be deployable using a single command (docker-compose up or equivalent)
2. THE Guardian_System SHALL include a configuration file for API keys (VirusTotal, OpenAI/Groq, URLScan.io) loaded from environment variables
3. WHEN the system starts, THE Guardian_System SHALL output a startup confirmation message listing all active agents and connected chats
4. THE Guardian_System SHALL provide a health-check endpoint or command that reports the status of all sub-agents
