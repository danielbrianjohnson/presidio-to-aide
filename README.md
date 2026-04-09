# Presidio Ticket Sanitizer Demo

A small command-line app that sanitizes PII in plain-text support tickets using [Microsoft Presidio](https://github.com/microsoft/presidio).

## Why this repo exists

This is a **Presidio-first baseline**.  It demonstrates a clean, working PII-sanitization pipeline that can later be migrated to [Protegrity Developer Edition](https://www.protegrity.com/) with minimal code changes.

The architecture is intentionally built around a **processor abstraction** so the migration is a small, obvious diff — not a rewrite.

## What the app does

1. Reads a `.txt` support ticket
2. Detects PII using Presidio (names, emails, phone numbers, SSNs, credit cards, account numbers, invoice IDs)
3. Replaces each PII entity with a `<ENTITY_TYPE>` placeholder
4. Writes:
   - a sanitized text file
   - a JSON findings report
5. Prints a short console summary

## Repo structure

```
presidio-ticket-demo/
├── README.md
├── MIGRATION_NOTES.md
├── requirements.txt
├── .gitignore
├── ticket.txt                  # sample input
├── expected_output/
│   ├── sanitized_ticket.txt    # reference sanitized output
│   └── findings.json           # reference findings report
├── src/
│   ├── main.py                 # CLI entry point
│   ├── app.py                  # processor-agnostic workflow
│   ├── config.py               # constants and defaults
│   ├── models.py               # ProcessResult, Finding dataclasses
│   ├── io_utils.py             # read/write helpers
│   ├── processors/
│   │   ├── __init__.py
│   │   ├── base.py             # BaseProcessor ABC — the migration seam
│   │   └── presidio_processor.py
│   └── reporters/
│       ├── __init__.py
│       ├── console_reporter.py
│       └── json_reporter.py
└── tests/
    ├── test_app.py
    ├── test_presidio_processor.py
    └── test_io_utils.py
```

## Setup

```bash
# 1. Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Download the default spaCy model (required by Presidio)
python -m spacy download en_core_web_lg
```

## Usage

```bash
python -m src.main --input ticket.txt --output-dir output
```

### Options

| Flag           | Default      | Description                |
|----------------|--------------|----------------------------|
| `--input`      | `ticket.txt` | Path to the input ticket   |
| `--output-dir` | `output`     | Directory for output files |

## Example output

```
==================================================
  Ticket Sanitization Report
==================================================
  Processor : presidio
  Findings  : 8
  Entities  :
    - ACCOUNT_NUMBER: 1
    - CREDIT_CARD: 1
    - EMAIL_ADDRESS: 1
    - INVOICE_ID: 1
    - PERSON: 1
    - PHONE_NUMBER: 2
    - US_SSN: 1

  Sanitized → output/sanitized_ticket.txt
  Report    → output/findings.json
==================================================
```

## Running tests

```bash
pytest tests/ -v
```

## Why the architecture looks like this

The `BaseProcessor` abstract class in `src/processors/base.py` exists so that:

- `app.py` never imports or references Presidio directly
- `models.py`, `io_utils.py`, and `reporters/` are processor-agnostic
- the only Presidio-specific code lives in `presidio_processor.py`

This means a future migration requires changing **one file** (the processor) and **one line** in `main.py` (the import).

## Future migration path

To migrate from Presidio to Protegrity Developer Edition:

1. Add `src/processors/protegrity_processor.py` implementing `BaseProcessor`
2. Change the import in `src/main.py` from `PresidioProcessor` to `ProtegrityProcessor`
3. Everything else — `app.py`, `models.py`, `io_utils.py`, reporters, tests — stays the same or needs only trivial updates

See [MIGRATION_NOTES.md](MIGRATION_NOTES.md) for details.
