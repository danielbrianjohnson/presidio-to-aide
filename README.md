# Presidio to AIDE: Reversible PII Tokenization for Support Tickets

A CLI tool that detects and protects PII in plain-text support tickets using Protegrity AI Developer Edition (AIDE). Demonstrates migrating from Microsoft Presidio's irreversible redaction to AIDE's reversible, format-preserving tokenization with role-based access control.

## Demo

[![Watch the demo](https://img.shields.io/badge/Video-Watch%20Demo-red?style=for-the-badge&logo=youtube)](VIDEO_URL_HERE)

<!-- Replace VIDEO_URL_HERE with the YouTube/Loom link once posted -->

## Quickstart

```bash
git clone https://github.com/danielbrianjohnson/presidio-to-aide.git
cd presidio-to-aide
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your AIDE endpoint
python -m src.main protect --input ticket.txt --output-dir output
```

## Expected result

The `protect` command produces:
- `output/sanitized_ticket.txt` with PII replaced by format-preserving tokens
- `output/findings.json` with entity types, locations, and confidence scores

The `unprotect` command (with an authorized role) restores original values from a protected ticket.

## Use case

Support teams need to route tickets through AI models and analytics pipelines without exposing customer PII. Simple redaction (`<PERSON>`, `<EMAIL>`) destroys the data's utility: AI can't distinguish between customers, can't correlate repeat callers, can't spot patterns.

This demo shows how AIDE's tokenization keeps data structurally useful while protecting real values, and how authorized users can recover originals when needed.

## What it demonstrates

- Migrating a working Presidio pipeline to AIDE with minimal code changes
- PII detection using AIDE's discovery service (which includes Presidio internally)
- Format-preserving tokenization that preserves data utility
- Role-gated detokenization (authorized vs. unauthorized reversal)
- Clean processor abstraction pattern for swappable protection backends

## Features showcased

- **Discovery**: Automatic PII detection across multiple entity types (names, emails, phone numbers, SSNs, credit cards, account numbers)
- **Protection**: Format-preserving tokenization via single API call
- **Detokenization**: Reversible protection with role-based access control

## Protegrity components used

- AI Developer Edition (AIDE)
- Data Discovery service
- Data Protection service (tokenization / detokenization)

## Architecture

```
ticket.txt
    |
    v
+----------+     +---------------------+
|  main.py |---->|       app.py        |
|  (CLI)   |     |  (workflow logic)   |
+----------+     +----------+----------+
                            |
                            v
                 +---------------------+
                 | protegrity_processor |
                 |  find_and_protect() |
                 |  find_and_unprotect()|
                 +----------+----------+
                            |
                            v
                 +---------------------+
                 |   AIDE API          |
                 |  (discovery +       |
                 |   protection)       |
                 +---------------------+
                            |
                            v
              output/sanitized_ticket.txt
              output/findings.json
```

## Getting started

### Prerequisites

- Python 3.10+
- Protegrity AI Developer Edition running (local or remote endpoint)

### Installation

```bash
git clone https://github.com/danielbrianjohnson/presidio-to-aide.git
cd presidio-to-aide
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your AIDE endpoint URL
```

### Run instructions

**Protect a ticket:**

```bash
python -m src.main protect --input ticket.txt --output-dir output
```

**Unprotect a ticket (authorized role):**

```bash
python -m src.main unprotect --input output/sanitized_ticket.txt --output-dir output/recovered
```

**Unprotect with unauthorized role (access denied):**

```bash
python -m src.main unprotect --input output/sanitized_ticket.txt --output-dir output/recovered --role ai-support-agent
```

## Try it

1. Look at `ticket.txt` (or `data/sample_ticket.txt`) to see the raw input with synthetic PII
2. Run `protect` and inspect the output: tokens look like real values but aren't
3. Run `unprotect` with the default `human-support-agent` role to see originals restored
4. Run `unprotect` with `--role ai-support-agent` to see access denied
5. Compare branches: `git diff presidio..protegrity` to see the full migration diff

## Security and privacy notes

- All sample data is **synthetic**. No real PII is present in this repository.
- The `.env` file (containing endpoint config) is gitignored.
- Role-based access control in this demo simulates the policy gate. In production, this is enforced by the Protegrity policy engine.
- No secrets are committed. See `.env.example` for required configuration.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `ConnectionRefusedError` | AIDE endpoint not running. Check `.env` and verify the service is up. |
| Empty findings | Confirm `ticket.txt` contains detectable PII entities. Check score threshold in config. |
| `ModuleNotFoundError: protegrity` | Activate venv and run `pip install -r requirements.txt`. |
| Unprotect returns access denied | Default role is `human-support-agent`. Pass `--role human-support-agent` explicitly. |

## Branch structure

| Branch | Contents |
|--------|----------|
| `main` | Full project: AIDE code + unprotect capability + docs + blog posts |
| `protegrity` | Code-only: the 6-file migration from Presidio to AIDE |
| `presidio` | Code-only: original Presidio baseline |

Diff the migration: `git diff presidio..protegrity`

## Next steps / extensions

- Connect to a real support ticket queue (Zendesk, Jira Service Desk, etc.)
- Add batch processing for multiple tickets
- Integrate with an LLM for AI-powered ticket routing on protected data
- Add audit logging for protect/unprotect operations
- Deploy AIDE endpoint to a shared environment for team access

## License

MIT
