# Tasks

## Task 1: Project Setup and Configuration

- [x] 1.1 Create project directory structure with all folders (src/, tests/, scripts/)
- [x] 1.2 Create requirements.txt with dependencies: langchain, openai, httpx, sqlalchemy, apscheduler, python-dotenv, pydantic
- [x] 1.3 Create .env.example with all required API keys (WHAPI_TOKEN, OPENAI_API_KEY, VIRUSTOTAL_API_KEY, URLSCAN_API_KEY, GROQ_API_KEY)
- [x] 1.4 Create src/config.py to load and validate environment variables using pydantic BaseSettings
- [x] 1.5 Create Dockerfile with Python 3.11 base image and dependency installation
- [x] 1.6 Create docker-compose.yml with the guardian service and volume mounts for SQLite persistence

## Task 2: Data Models and Storage Layer

- [x] 2.1 Create src/storage/models.py with SQLAlchemy models for ThreatRecord (id, message_content, sender_id, chat_id, timestamp, threat_level, threat_type, confidence, analysis_details, reasoning_chain)
- [x] 2.2 Create data model classes in src/models.py: ThreatLevel enum, ThreatType enum, IncomingMessage dataclass, ThreatAssessment dataclass, AlertMessage dataclass
- [x] 2.3 Create src/storage/threat_log.py with ThreatLog class: init_db(), log_threat(), get_threats_since(), get_threat_stats(), retry queue logic
- [x] 2.4 Write tests/test_threat_log.py: test record creation, query by date range, retry on failure, field completeness property test

## Task 3: URL Extraction and Resolution Tools

- [x] 3.1 Create src/utils/url_extractor.py with extract_urls() function using regex to find all valid URLs in message text
- [x] 3.2 Create src/tools/url_resolver.py with follow_redirects() that follows HTTP redirects up to 10 hops and records the chain
- [ ] 3.3 Write tests/test_url_extractor.py: test extraction from various message formats, property test for URL completeness
- [ ] 3.4 Write tests/test_url_resolver.py: test redirect chain following, test 10-hop limit, test timeout handling

## Task 4: External API Tool Wrappers

- [ ] 4.1 Create src/tools/virustotal.py with VirusTotalClient class: check_url() method that queries the VirusTotal API and returns reputation score
- [ ] 4.2 Create src/tools/urlscan.py with URLScanClient class: scan_url() method that submits URL to URLScan.io and retrieves results
- [ ] 4.3 Add error handling to both API clients: timeout handling, rate limiting, graceful degradation (return SUSPICIOUS on failure)
- [ ] 4.4 Write tests for API wrappers with mocked responses: test success paths, test failure paths, test timeout behavior

## Task 5: WhatsApp Connector

- [ ] 5.1 Create src/connector/whatsapp_connector.py with WhatsAppConnector class using Whapi.cloud REST API
- [ ] 5.2 Implement message receiving: webhook handler or polling loop that receives incoming messages
- [ ] 5.3 Implement message sending: send_message() method for alerts and reports with WhatsApp formatting support
- [ ] 5.4 Implement connection health monitoring: is_connected(), reconnect logic with exponential backoff
- [ ] 5.5 Implement message parsing: convert raw API response to IncomingMessage dataclass with URL extraction

## Task 6: Link Scanner Agent

- [ ] 6.1 Create src/agents/link_scanner.py with LinkScannerAgent class using LangChain tool-calling pattern
- [ ] 6.2 Register VirusTotal and URLScan as LangChain tools on the agent
- [ ] 6.3 Implement scan_urls() method: extract URLs → check each via tools → follow redirects → assign ThreatLevel
- [ ] 6.4 Implement threat level decision logic: combine VirusTotal score + URLScan result + redirect chain length into final classification
- [ ] 6.5 Write tests/test_link_scanner.py: test classification logic with mocked API responses, property test for threat level totality

## Task 7: Message Analyzer Agent

- [ ] 7.1 Create src/agents/message_analyzer.py with MessageAnalyzerAgent class using LangChain with GPT-4o/Groq
- [ ] 7.2 Design and implement the analysis prompt: structured prompt that classifies messages for social engineering, urgency, impersonation
- [ ] 7.3 Implement analyze_message() method: send message to LLM → parse structured response → return ThreatAssessment with confidence and reasoning
- [ ] 7.4 Implement impersonation detection: compare sender name against known admin/contact list
- [ ] 7.5 Write tests/test_message_analyzer.py: test with mocked LLM responses, property test for confidence bounds [0.0, 1.0]

## Task 8: Alert Agent

- [ ] 8.1 Create src/agents/alert_agent.py with AlertAgent class
- [ ] 8.2 Create src/utils/formatter.py with WhatsApp formatting helpers: bold(), italic(), emoji_prefix(), format_alert()
- [ ] 8.3 Implement send_alert() method: compose alert message with threat type, explanation, recommended action → send via connector
- [ ] 8.4 Implement admin mention logic: include @admin tag when ThreatLevel is DANGEROUS
- [ ] 8.5 Implement retry logic: retry up to 3 times with 2-second intervals on send failure
- [ ] 8.6 Write tests/test_alert_agent.py: test message formatting, test admin mention consistency property, test retry behavior

## Task 9: Report Agent

- [ ] 9.1 Create src/agents/report_agent.py with ReportAgent class
- [ ] 9.2 Implement generate_report() method: query threat log → compute statistics → format report message
- [ ] 9.3 Implement statistics computation: total threats, breakdown by type, top 3 targeted members, week-over-week trend
- [ ] 9.4 Implement scheduling: configure APScheduler with weekly cron trigger to call generate_report()
- [ ] 9.5 Implement "all clear" logic: send brief confirmation when no threats detected in period
- [ ] 9.6 Write tests/test_report_agent.py: test statistics computation, property test for report consistency (sum of types = total)

## Task 10: Guardian System Orchestrator

- [ ] 10.1 Create src/orchestrator/guardian.py with GuardianSystem class
- [ ] 10.2 Implement the autonomous event loop: async loop that consumes messages from connector and routes through pipeline
- [ ] 10.3 Implement agent pipeline: message → classify (has URLs? has text?) → route to appropriate agents → aggregate results
- [ ] 10.4 Implement threat level aggregation: combine assessments from Link_Scanner and Message_Analyzer using max severity
- [ ] 10.5 Implement health monitoring: heartbeat logging every 60 seconds, agent responsiveness checks
- [ ] 10.6 Implement agent recovery: detect unresponsive agents (30s timeout) and restart them
- [ ] 10.7 Implement reasoning chain logging: record which agents were invoked, tools called, and decisions made for each message
- [ ] 10.8 Write tests/test_guardian.py: test pipeline routing, property test for no-drop guarantee, test aggregation monotonicity

## Task 11: Main Entry Point and Startup

- [ ] 11.1 Create src/main.py: initialize all components, start connector, start orchestrator, start scheduler
- [ ] 11.2 Implement startup confirmation: log and print active agents, connected chats, system status
- [ ] 11.3 Implement health-check command: CLI flag or simple HTTP endpoint that reports agent status
- [ ] 11.4 Implement graceful shutdown: handle SIGTERM/SIGINT, close connections, flush logs

## Task 12: Demo and Deployment Preparation

- [ ] 12.1 Create scripts/seed_test_messages.py: script that sends sample scam/phishing messages for demo purposes
- [ ] 12.2 Create README.md with setup instructions, architecture diagram, demo guide, and 2-minute video script outline
- [ ] 12.3 Test full docker-compose deployment: verify single-command startup, all agents initialize, health check passes
- [ ] 12.4 Create sample .env with test API keys and document which free-tier APIs are needed for demo
