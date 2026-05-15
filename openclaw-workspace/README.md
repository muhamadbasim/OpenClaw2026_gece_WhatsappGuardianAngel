# 🛡 OpenClaw Agent Workspace

This folder contains the **drop-in workspace** for the Scam Guardian
agent running on [OpenClaw](https://docs.openclaw.ai).

## What's here

| File | Purpose |
|---|---|
| `SOUL.md` | The system prompt — classification rules, output format, detection heuristics. **Edit this to change agent behavior.** |
| `IDENTITY.md` | Agent name, vibe, emoji, mission |
| `AGENTS.md` | Workspace conventions and red lines |

## How to install

```bash
# 1. Make sure OpenClaw is installed and the WhatsApp plugin is enabled
openclaw plugins enable whatsapp

# 2. Copy this workspace into OpenClaw's agents directory
mkdir -p ~/.openclaw/agents/scam-guardian/workspace
cp *.md ~/.openclaw/agents/scam-guardian/workspace/

# 3. Register the agent
openclaw agents add scam-guardian \
    --workspace ~/.openclaw/agents/scam-guardian/workspace \
    --non-interactive

# 4. Bind WhatsApp messages to this agent
openclaw agents bind --agent scam-guardian --bind whatsapp

# 5. Login WhatsApp (scan QR)
openclaw channels login --channel whatsapp
```

After this, every WhatsApp DM your linked number receives gets routed to
the Scam Guardian agent for analysis.

## How to customize

Edit `SOUL.md`. The agent re-reads its workspace on every incoming
message — **no restart needed**.

For example, to add a new rule for romance scams, append under
"Detection Heuristics":

```markdown
- Romance scam indicators: unsolicited "I love you" from unknown sender,
  requests for money/gift cards, claims of being stuck abroad
```

Save the file, send a test message, and the agent uses the new rule
immediately.

## Notes

- This workspace assumes WhatsApp is in **DM-only mode** (`groupPolicy: allowlist`)
- Agent uses whatever LLM is configured at the OpenClaw account level
  (we use GPT-5.5 via GrowthCircle, but any OpenClaw-supported provider works)
- Auth state, sessions, and credentials live outside this workspace and
  are **never committed to git**
