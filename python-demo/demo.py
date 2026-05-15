"""WhatsApp Scam & Phishing Guardian — Demo.

A self-contained demonstration of the multi-agent scam detection system.
Simulates incoming WhatsApp messages and runs them through the full pipeline:

    Incoming Message
        │
        ├── URL Extractor ──► Link Scanner Agent (URL reputation + redirects)
        │
        └── Message Analyzer Agent (LLM-based scam/phishing detection)
                │
                ▼
        Threat Aggregator
                │
                ▼
        Alert Agent (formatted WhatsApp warning)

Run:
    python demo.py            # Run all demo messages
    python demo.py --offline  # Run without LLM (uses heuristic fallback)
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

# Reuse the URL extractor we already built
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.url_extractor import extract_urls  # noqa: E402

load_dotenv()
console = Console()

# ─────────────────────────────────────────────────────────────────────────────
# Data Models
# ─────────────────────────────────────────────────────────────────────────────


class ThreatLevel(str, Enum):
    SAFE = "SAFE"
    SUSPICIOUS = "SUSPICIOUS"
    DANGEROUS = "DANGEROUS"


SEVERITY = {ThreatLevel.SAFE: 0, ThreatLevel.SUSPICIOUS: 1, ThreatLevel.DANGEROUS: 2}


@dataclass
class IncomingMessage:
    sender: str
    chat: str
    text: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ThreatAssessment:
    level: ThreatLevel
    threat_type: str
    confidence: float
    explanation: str
    reasoning: list[str] = field(default_factory=list)
    evidence: dict = field(default_factory=dict)


# ─────────────────────────────────────────────────────────────────────────────
# Agent 1: Link Scanner — heuristic URL analysis
# ─────────────────────────────────────────────────────────────────────────────


SUSPICIOUS_TLDS = {".tk", ".ml", ".ga", ".cf", ".click", ".xyz", ".top", ".loan"}
SHORTENERS = {
    "bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd", "buff.ly",
    "rb.gy", "shorturl.at", "cutt.ly",
}
PHISHING_KEYWORDS = {"verify", "secure", "update", "login", "account",
                     "confirm", "wallet", "bank", "paypal", "support"}


async def link_scanner(urls: list[str]) -> ThreatAssessment:
    """Scan URLs for phishing and suspicious patterns (offline heuristics)."""
    if not urls:
        return ThreatAssessment(
            level=ThreatLevel.SAFE,
            threat_type="none",
            confidence=1.0,
            explanation="No URLs to scan",
            reasoning=["No URLs found in message"],
        )

    reasoning: list[str] = [f"Found {len(urls)} URL(s) to analyze"]
    evidence: dict = {"urls": urls, "findings": []}
    max_severity = ThreatLevel.SAFE
    threat_type = "none"

    for url in urls:
        url_lower = url.lower()
        finding: dict = {"url": url, "issues": []}

        # Check 1: Known shortener
        for shortener in SHORTENERS:
            if shortener in url_lower:
                finding["issues"].append(f"URL shortener ({shortener}) — destination hidden")
                if SEVERITY[max_severity] < SEVERITY[ThreatLevel.SUSPICIOUS]:
                    max_severity = ThreatLevel.SUSPICIOUS
                threat_type = "malicious_redirect"

        # Check 2: Suspicious TLD
        for tld in SUSPICIOUS_TLDS:
            if url_lower.endswith(tld) or f"{tld}/" in url_lower:
                finding["issues"].append(f"Suspicious TLD ({tld}) often used by scammers")
                if SEVERITY[max_severity] < SEVERITY[ThreatLevel.SUSPICIOUS]:
                    max_severity = ThreatLevel.SUSPICIOUS
                threat_type = "phishing_link"

        # Check 3: Phishing keywords in domain
        domain_match = re.search(r"://([^/]+)", url_lower)
        if domain_match:
            domain = domain_match.group(1)
            for kw in PHISHING_KEYWORDS:
                if kw in domain and not domain.endswith((
                    "paypal.com", "google.com", "microsoft.com", "apple.com"
                )):
                    finding["issues"].append(
                        f"Phishing keyword '{kw}' in domain '{domain}'"
                    )
                    max_severity = ThreatLevel.DANGEROUS
                    threat_type = "phishing_link"

        # Check 4: IP address as domain
        if re.search(r"://\d+\.\d+\.\d+\.\d+", url_lower):
            finding["issues"].append("Raw IP address used instead of domain")
            max_severity = ThreatLevel.DANGEROUS
            threat_type = "phishing_link"

        # Check 5: Brand impersonation via lookalike
        for brand in ("paypa1", "amaz0n", "g00gle", "microsft", "app1e"):
            if brand in url_lower:
                finding["issues"].append(f"Brand impersonation pattern: '{brand}'")
                max_severity = ThreatLevel.DANGEROUS
                threat_type = "phishing_link"

        if finding["issues"]:
            evidence["findings"].append(finding)
            reasoning.append(f"⚠ {url}: {', '.join(finding['issues'])}")
        else:
            reasoning.append(f"✓ {url}: no obvious indicators")

    confidence = 0.95 if max_severity == ThreatLevel.DANGEROUS else (
        0.75 if max_severity == ThreatLevel.SUSPICIOUS else 0.85
    )

    explanation = {
        ThreatLevel.SAFE: "All URLs passed heuristic checks",
        ThreatLevel.SUSPICIOUS: "URL has indicators that warrant caution",
        ThreatLevel.DANGEROUS: "URL shows strong phishing indicators — do not click",
    }[max_severity]

    return ThreatAssessment(
        level=max_severity,
        threat_type=threat_type if max_severity != ThreatLevel.SAFE else "none",
        confidence=confidence,
        explanation=explanation,
        reasoning=reasoning,
        evidence=evidence,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Agent 2: Message Analyzer — LLM with structured outputs
# ─────────────────────────────────────────────────────────────────────────────


class LLMAnalysis(BaseModel):
    """Structured output schema for the message analyzer LLM."""

    threat_level: ThreatLevel = Field(description="Overall threat classification")
    threat_type: str = Field(
        description=(
            "One of: phishing_link, social_engineering, impersonation, "
            "malicious_redirect, financial_scam, none"
        )
    )
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence 0..1")
    explanation: str = Field(description="One-sentence explanation for the user")
    reasoning: list[str] = Field(
        description="3-5 step reasoning chain showing how the conclusion was reached"
    )


SYSTEM_PROMPT = """You are a security agent that analyzes WhatsApp messages
for scams, phishing, and social engineering.

For each message, identify:
- Urgency tactics ("act now", "limited time", "your account will be closed")
- Authority impersonation (pretending to be admin, bank, government, support)
- Emotional manipulation (fear, greed, sympathy)
- Financial lures (prizes, refunds, investment opportunities, urgent payments)
- Credential harvesting (asking for OTP, password, ID number)

Classify as:
- SAFE: normal conversation, no manipulation indicators
- SUSPICIOUS: 1-2 weak indicators, could be legitimate
- DANGEROUS: multiple strong indicators of scam/phishing

Always provide a clear reasoning chain."""


async def message_analyzer(message: IncomingMessage, offline: bool = False) -> ThreatAssessment:
    """Analyze message text for scam patterns using GPT-4o-mini structured outputs."""
    if offline or not os.getenv("OPENAI_API_KEY"):
        return _offline_analyzer(message)

    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI()
        completion = await client.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"Sender: {message.sender}\n"
                        f"Chat: {message.chat}\n"
                        f"Message: {message.text}"
                    ),
                },
            ],
            response_format=LLMAnalysis,
        )
        result = completion.choices[0].message.parsed
        if result is None:
            return _offline_analyzer(message)

        return ThreatAssessment(
            level=result.threat_level,
            threat_type=result.threat_type,
            confidence=result.confidence,
            explanation=result.explanation,
            reasoning=result.reasoning,
            evidence={"model": "gpt-4o-mini", "method": "structured_output"},
        )
    except Exception as e:
        console.print(f"[yellow]LLM call failed ({e}), using offline heuristic[/yellow]")
        return _offline_analyzer(message)


def _offline_analyzer(message: IncomingMessage) -> ThreatAssessment:
    """Fallback heuristic analyzer when LLM is unavailable."""
    text = message.text.lower()
    reasoning: list[str] = ["LLM unavailable — running keyword heuristic"]
    score = 0
    triggers: list[str] = []

    urgency_patterns = ["act now", "urgent", "immediately", "limited time",
                        "expires today", "last chance", "hurry"]
    auth_patterns = ["bank", "admin", "support", "verify your account",
                     "official", "tax", "government"]
    financial_patterns = ["prize", "won", "claim", "refund", "transfer",
                          "investment", "double your money", "btc", "crypto"]
    credential_patterns = ["otp", "password", "pin", "verification code",
                           "send me your", "share your"]

    for p in urgency_patterns:
        if p in text:
            score += 1
            triggers.append(f"urgency: '{p}'")
    for p in auth_patterns:
        if p in text:
            score += 1
            triggers.append(f"authority: '{p}'")
    for p in financial_patterns:
        if p in text:
            score += 2
            triggers.append(f"financial lure: '{p}'")
    for p in credential_patterns:
        if p in text:
            score += 3
            triggers.append(f"credential request: '{p}'")

    reasoning.extend([f"Triggered: {t}" for t in triggers]
                     if triggers else ["No scam indicators found"])

    if score >= 4:
        level, threat_type, conf = ThreatLevel.DANGEROUS, "social_engineering", 0.85
        explanation = "Multiple scam indicators detected"
    elif score >= 2:
        level, threat_type, conf = ThreatLevel.SUSPICIOUS, "social_engineering", 0.65
        explanation = "Some suspicious patterns detected"
    else:
        level, threat_type, conf = ThreatLevel.SAFE, "none", 0.7
        explanation = "Message appears benign"

    return ThreatAssessment(
        level=level,
        threat_type=threat_type,
        confidence=conf,
        explanation=explanation,
        reasoning=reasoning,
        evidence={"score": score, "triggers": triggers},
    )


# ─────────────────────────────────────────────────────────────────────────────
# Agent 3: Alert Agent — formats WhatsApp-style warning
# ─────────────────────────────────────────────────────────────────────────────


def alert_agent(message: IncomingMessage, assessment: ThreatAssessment) -> str:
    """Compose a WhatsApp-formatted alert message."""
    if assessment.level == ThreatLevel.SAFE:
        return ""

    icon = "🚨" if assessment.level == ThreatLevel.DANGEROUS else "⚠️"
    actions = {
        ThreatLevel.DANGEROUS: "Do NOT click any links. Block the sender. Report to admin.",
        ThreatLevel.SUSPICIOUS: "Verify with the sender through another channel before acting.",
    }

    admin_mention = "@admin " if assessment.level == ThreatLevel.DANGEROUS else ""
    alert = (
        f"{icon} *Scam Guardian Alert*\n"
        f"{admin_mention}\n"
        f"*Threat Level:* {assessment.level.value}\n"
        f"*Type:* {assessment.threat_type.replace('_', ' ').title()}\n"
        f"*Confidence:* {int(assessment.confidence * 100)}%\n\n"
        f"_{assessment.explanation}_\n\n"
        f"*Recommended action:* {actions[assessment.level]}"
    )
    return alert


# ─────────────────────────────────────────────────────────────────────────────
# Orchestrator
# ─────────────────────────────────────────────────────────────────────────────


def aggregate(*assessments: ThreatAssessment) -> ThreatAssessment:
    """Combine multiple assessments — pick the most severe."""
    valid = [a for a in assessments if a is not None]
    if not valid:
        return ThreatAssessment(ThreatLevel.SAFE, "none", 1.0, "No analysis", [])

    winner = max(valid, key=lambda a: SEVERITY[a.level])
    combined_reasoning: list[str] = []
    for a in valid:
        combined_reasoning.append(f"[{a.threat_type}] " + " | ".join(a.reasoning[:3]))

    return ThreatAssessment(
        level=winner.level,
        threat_type=winner.threat_type,
        confidence=winner.confidence,
        explanation=winner.explanation,
        reasoning=combined_reasoning,
        evidence={f"agent_{i}": a.evidence for i, a in enumerate(valid)},
    )


async def process_message(message: IncomingMessage, offline: bool = False) -> ThreatAssessment:
    """Run a message through the full agent pipeline."""
    urls = extract_urls(message.text)

    # Run agents concurrently
    link_task = asyncio.create_task(link_scanner(urls))
    msg_task = asyncio.create_task(message_analyzer(message, offline=offline))

    link_result, msg_result = await asyncio.gather(link_task, msg_task)
    return aggregate(link_result, msg_result)


# ─────────────────────────────────────────────────────────────────────────────
# Demo Messages
# ─────────────────────────────────────────────────────────────────────────────


DEMO_MESSAGES = [
    IncomingMessage(
        sender="Mom",
        chat="Family Group",
        text="Hi sayang, jangan lupa makan siang ya 🍱",
    ),
    IncomingMessage(
        sender="Unknown +62812-XXXX",
        chat="Family Group",
        text=(
            "URGENT! Your bank account will be closed in 1 hour. "
            "Verify now at http://secure-bank-verify.tk/login "
            "or send us your OTP code immediately to keep access."
        ),
    ),
    IncomingMessage(
        sender="Marketing Bot",
        chat="Office Group",
        text="Check out our new product launch: https://company.com/products 🚀",
    ),
    IncomingMessage(
        sender="Admin Group (fake)",
        chat="Office Group",
        text=(
            "Hello team, this is the admin. Click bit.ly/3xK9pQz to claim "
            "your annual bonus. Limited time only — act now!"
        ),
    ),
    IncomingMessage(
        sender="Investment Buddy",
        chat="Crypto Chat",
        text=(
            "Bro, double your money in 24 hours! Send 1 BTC to "
            "http://crypto-wallet-verify.xyz and get 2 BTC back guaranteed 💰"
        ),
    ),
]


# ─────────────────────────────────────────────────────────────────────────────
# CLI / Display
# ─────────────────────────────────────────────────────────────────────────────


LEVEL_STYLE = {
    ThreatLevel.SAFE: "bold green",
    ThreatLevel.SUSPICIOUS: "bold yellow",
    ThreatLevel.DANGEROUS: "bold red",
}


def render_message(message: IncomingMessage) -> Panel:
    body = Text()
    body.append(f"From: {message.sender}\n", style="cyan")
    body.append(f"Chat: {message.chat}\n", style="dim")
    body.append(f"\n{message.text}", style="white")
    return Panel(body, title="📩 Incoming Message", border_style="blue", padding=(0, 1))


def render_assessment(assessment: ThreatAssessment) -> Panel:
    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column(style="bold cyan")
    table.add_column()
    table.add_row("Threat Level", Text(assessment.level.value, style=LEVEL_STYLE[assessment.level]))
    table.add_row("Threat Type", assessment.threat_type)
    table.add_row("Confidence", f"{int(assessment.confidence * 100)}%")
    table.add_row("Verdict", assessment.explanation)
    table.add_row("", "")
    table.add_row("Reasoning", "")
    for step in assessment.reasoning:
        table.add_row("", f"• {step}")
    return Panel(
        table,
        title="🧠 Agent Analysis",
        border_style=LEVEL_STYLE[assessment.level].split()[-1],
        padding=(0, 1),
    )


def render_alert(alert: str) -> Optional[Panel]:
    if not alert:
        return None
    return Panel(
        Text(alert, style="white"),
        title="📢 Alert sent to chat",
        border_style="magenta",
        padding=(0, 1),
    )


async def run_demo(offline: bool = False) -> None:
    mode = "OFFLINE (heuristic only)" if offline else "ONLINE (GPT-4o-mini + heuristic)"
    console.print(Rule("[bold]🛡  WhatsApp Scam & Phishing Guardian — Demo[/bold]"))
    console.print(f"[dim]Mode: {mode}[/dim]\n")

    for i, message in enumerate(DEMO_MESSAGES, 1):
        console.print(Rule(f"[bold]Message {i}/{len(DEMO_MESSAGES)}[/bold]"))
        console.print(render_message(message))

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            progress.add_task("Running agent pipeline...", total=None)
            assessment = await process_message(message, offline=offline)

        console.print(render_assessment(assessment))
        alert_panel = render_alert(alert_agent(message, assessment))
        if alert_panel:
            console.print(alert_panel)
        console.print()

    console.print(Rule("[bold green]✓ Demo complete[/bold green]"))


def main() -> None:
    parser = argparse.ArgumentParser(description="WhatsApp Scam Guardian Demo")
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Skip LLM calls and use heuristic analyzer only",
    )
    args = parser.parse_args()
    asyncio.run(run_demo(offline=args.offline))


if __name__ == "__main__":
    main()
