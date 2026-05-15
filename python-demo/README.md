# 🐍 Python Demo — Scam Guardian Pipeline

Standalone Python implementation of the Scam Guardian pipeline. Runs in
the terminal with rich panel output. No WhatsApp account required.

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Heuristics only (no API key needed)
python demo.py --offline

# With GPT-4o-mini (structured outputs via Pydantic)
export OPENAI_API_KEY=sk-...
python demo.py
```

Five demo scenarios run automatically:

| # | Scenario | Expected verdict |
|---|---|---|
| 1 | Mom sends "jangan lupa makan siang" | 🟢 SAFE |
| 2 | Bank phishing with `.tk` URL + OTP request | 🔴 DANGEROUS |
| 3 | Marketing message with clean company URL | 🟢 SAFE |
| 4 | Fake admin offering bonus via `bit.ly` | 🔴 DANGEROUS |
| 5 | Crypto "double your BTC" scam | 🔴 DANGEROUS |

## Architecture

```
   IncomingMessage
        │
        ├──► extract_urls() ──► Link Scanner Agent
        │                       (heuristics: TLD, shortener, brand
        │                        impersonation, phishing keywords,
        │                        IP-as-domain)
        │
        └──► Message Analyzer Agent
             (GPT-4o-mini structured outputs OR keyword fallback)
                       │
                       ▼
              aggregate() — pick max severity
                       │
                       ▼
                 Alert Agent
              (formatted WhatsApp warning)
```

The two agents run **concurrently** via `asyncio.gather()` so even with a
slow LLM the heuristic verdict is ready instantly.

## Files

| File | Purpose |
|---|---|
| `demo.py` | Self-contained CLI demo (~400 lines) |
| `src/url_extractor.py` | Regex URL extraction (handles emails, parens, trailing punctuation) |
| `src/url_resolver.py` | Async redirect chain follower (max 10 hops) |
| `src/models.py` | `ThreatLevel`, `ThreatType`, `IncomingMessage`, `ThreatAssessment` |
| `src/config.py` | Pydantic-settings loader for `.env` |
| `src/storage_models.py` | SQLAlchemy `ThreatRecord` (for persistent logging) |
| `src/threat_log.py` | Threat log with retry queue and statistics |
| `tests/test_threat_log.py` | Hypothesis property tests |

## Run tests

```bash
pip install pytest hypothesis
pytest tests/
```

The test suite includes property-based tests verifying:

- All retrieved threat records have all required fields non-null
- Date-range filtering works correctly
- Failed writes go to the retry queue and recover

## Docker

```bash
docker compose up
```

Mounts a volume for SQLite persistence; reads config from `.env`.
