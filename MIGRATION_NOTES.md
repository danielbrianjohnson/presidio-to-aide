# Migration Notes: Presidio → Protegrity Developer Edition

---

## Key architecture insight

**Protegrity Developer Edition uses Presidio internally.**  Its Data Discovery service includes Presidio as one of multiple detection models (alongside additional ML, NLP, and pattern-matching models).  You don't manage Presidio directly — it runs inside the Dev Edition Docker containers.

The migration **replaces your direct Presidio calls** with Dev Edition API calls.  Presidio is still doing detection work under the hood, but now:
- It's managed for you (no AnalyzerEngine wiring, no spaCy model downloads, no custom recognizers)
- It's augmented by additional ML and context-based models you didn't have before
- It's paired with a **protection layer** (tokenization, unprotect) that Presidio alone can't provide

Dev Edition's `protegrity_developer_python` module provides single-call APIs that handle both detection and protection:

| API | What it does |
|-----|-------------|
| `protegrity.discover(text)` | Detect PII — returns entities as JSON |
| `protegrity.find_and_redact(text)` | Detect + redact/mask (similar to what our Presidio code does) |
| `protegrity.find_and_protect(text)` | Detect + tokenize in **one call** |
| `protegrity.find_and_unprotect(text)` | Find tokens + restore original values |

There is also the `appython` module (Application Protector) for role-based protect/unprotect of structured data:

```python
from appython import Protector
session = Protector().create_session("superuser")
protected = session.protect("Sarah Johnson", "name")
original  = session.unprotect(protected, "name")
```

**What changes for us:**
- We remove our direct Presidio dependencies — no more `presidio-analyzer`, `presidio-anonymizer`, or spaCy model in our project
- Presidio (plus additional models) still runs inside the Dev Edition Docker containers
- Detection and protection are handled by one API call — no duplicate detection passes
- The `protegrity_developer_python` module talks to the Data Discovery service (Docker containers)
- We gain tokenization and unprotect — capabilities Presidio alone doesn't have

---

## Demo script / talk track

### Part 1 — Presidio baseline (what we already have)

Walk through the existing app quickly.  The point is to show Presidio doing a solid job at **detection and redaction**.

```bash
python -m src.main --input ticket.txt --output-dir output
```

**Talk track:**

> "Here's our starting point.  We have a plain-text support ticket with real PII in it — names, emails, phone numbers, SSNs, credit card numbers.  We're using Microsoft Presidio, which is a great open-source PII detection and redaction library.  Let's run it."
>
> *[run the command, show the console report]*
>
> "Presidio found 8 entities across 7 types.  It correctly identified the person name, email, phone numbers, SSN, credit card, and even our custom account number and invoice ID.  The sanitized output replaces each value with a placeholder like `<PERSON>` or `<US_SSN>`.  That's solid — the PII is gone."
>
> "But here's the thing — it's *gone*.  This is **irreversible redaction**.  `Sarah Johnson` is now `<PERSON>`, and there's no getting her back.  If a downstream system needs the name, or an authorized analyst needs to see the original ticket, we're out of luck.  We've also lost data utility — every person in the system is the same `<PERSON>` placeholder, so you can't distinguish customers, you can't join records, and you can't run analytics on the protected data."
>
> "Presidio is a great open-source project for detection and redaction.  What's cool is that Protegrity Developer Edition actually uses Presidio internally as part of its detection pipeline — along with additional ML and context-based models.  But instead of us managing Presidio directly, wiring up the AnalyzerEngine, downloading spaCy models, writing custom recognizers — Dev Edition handles all of that behind a single API call.  And on top of detection, it adds a protection layer — tokenization and unprotect — that Presidio alone can't do.  Let's walk through what that migration looks like."

### Part 2 — Migration to Protegrity (the code changes)

Show the actual code diff.  The migration should be small and obvious.

**Talk track:**

> "Because we designed this app with a clean processor interface, the migration is minimal.  Let me walk you through the changes."
>
> *[show the diff / side-by-side]*

Highlight these points:

1. **We replace our direct Presidio calls with Dev Edition API calls.**  Presidio is still running inside Dev Edition's Data Discovery service — we just stop managing it ourselves.  When you call `find_and_protect()`, it uses Presidio plus additional ML and NLP models to detect PII, then tokenizes it — all in a single call.  No more AnalyzerEngine, AnonymizerEngine, or custom recognizers in our code.

2. **We add a new processor file.**  `protegrity_processor.py` replaces `presidio_processor.py`.  It uses the `protegrity_developer_python` module instead of calling Presidio's libraries directly.

3. **The rest of the app doesn't change.**  `app.py`, `models.py`, `io_utils.py`, the reporters, the ticket file — all identical.

4. **Dependencies get simpler.**  We drop `presidio-analyzer`, `presidio-anonymizer`, and the 560MB spaCy model from our project.  We add `protegrity-developer-python` (which talks to the Dev Edition Docker services where Presidio and the other models run).

**Key terminology:**
- **Protect**: detect PII and replace sensitive values with tokens — reversible
- **Unprotect**: restore tokens back to original clear-text values (requires authorization)
- **Redact**: replace sensitive values with placeholders or masking characters — irreversible (what our direct Presidio code does)
- **Data Discovery**: Dev Edition's detection engine — uses Presidio plus additional ML/NLP/pattern-matching models behind a single API

### Part 3 — Protect (run the migrated app)

```bash
python -m src.main protect --input ticket.txt --output-dir output
```

**Talk track:**

> "Now let's run the Protegrity version.  Same ticket, same command structure — we just added a `protect` subcommand."
>
> *[show the output]*
>
> "Notice the difference.  The output now has entity tags with tokenized values inside them — like `[PERSON]7ro8 lfU[/PERSON]` instead of just `<PERSON>`.  The sensitive values have been replaced with tokens by Protegrity's protection engine."
>
> "This is fundamentally different from redaction.  The data is **protected**, not destroyed.  Presidio is still running inside Dev Edition doing detection — along with additional models — but we don't manage it anymore.  Detection and protection happened in one API call."

### Part 4 — Unprotect (the feature Presidio can't do)

This is the differentiator.  Show the protected data being restored.

```bash
# Unprotect — restore original values
python -m src.main unprotect --input output/sanitized_ticket.txt --output-dir output/recovered
```

**Talk track:**

> "Now here's what Presidio simply cannot do.  I'm going to take that protected ticket and unprotect it."
>
> *[run the unprotect command, show original values restored]*
>
> "The original data is back — `Sarah Johnson`, the real SSN, the real credit card number.  The `find_and_unprotect()` API recognized the entity tags, sent the tokens to the protection service, and got back the originals."
>
> "With Presidio, once you redact, the data is gone forever.  With Protegrity, protection is reversible — and in a production deployment, that reversal is controlled by policies and user roles."

**Optional extended demo** — if you have the `appython` credentials set up, you can also show role-based access:

```bash
# Protect with role-based policy
python -m src.main protect --input ticket.txt --output-dir output --user superuser

# Unprotect as different users
python -m src.main unprotect --input output/sanitized_ticket.txt --user superuser    # → sees originals
python -m src.main unprotect --input output/sanitized_ticket.txt --user hr           # → may see masked data
```

### Part 5 — Wrap-up

> "To recap:  we started with a working Presidio baseline — calling Presidio directly for detection and irreversible redaction.  We migrated to Protegrity Developer Edition by swapping one processor file and changing one import — the rest of the app stayed the same.  Presidio is still running inside Dev Edition doing detection, but now it's managed for us, augmented with additional models, and paired with a protection layer that gives us reversible tokenization and unprotect.  We went from managing Presidio ourselves and only getting redaction, to a single API call that gives us detection plus real data protection."

---

## What stays unchanged during migration

| File / Directory             | Reason                                      |
|------------------------------|---------------------------------------------|
| `src/app.py`                 | Processor-agnostic — only calls `process_text()` |
| `src/models.py`              | Shared data contract (`ProcessResult`, `Finding`) |
| `src/io_utils.py`            | Reads/writes files — no processor logic     |
| `src/reporters/`             | Consumes `ProcessResult` — no processor logic |
| `src/config.py`              | Add Dev Edition config values, but structure stays |
| `ticket.txt`                 | Same input for both processors              |
| `tests/test_io_utils.py`     | Tests file I/O only                         |
| `tests/test_app.py`          | Uses processor as a plug-in — swap the import |

## What gets replaced

| File                               | Change                                        |
|-------------------------------------|-----------------------------------------------|
| `src/processors/presidio_processor.py` | **Replaced** by `protegrity_processor.py`    |
| `src/main.py`                       | Change import + add `protect`/`unprotect` subcommands |
| `requirements.txt`                  | Remove Presidio deps, add `protegrity-developer-python` |
| `src/processors/base.py`            | Add optional `unprotect_text()` method        |

## Step-by-step migration

### Step 1: Prerequisites

Protegrity Developer Edition runs as Docker containers.  Before coding:

```bash
# Clone the Dev Edition repo
git clone https://github.com/Protegrity-Developer-Edition/protegrity-developer-edition.git

# Start the services
cd protegrity-developer-edition
docker compose up -d

# Install the Python module
pip install protegrity-developer-python
```

For protect/unprotect (beyond redaction), register at https://www.protegrity.com/developers/dev-edition-api and export credentials:

```bash
export DEV_EDITION_EMAIL='<your_email>'
export DEV_EDITION_PASSWORD='<your_password>'
export DEV_EDITION_API_KEY='<your_api_key>'
```

### Step 2: Create the Protegrity processor

Create `src/processors/protegrity_processor.py`:
- Subclass `BaseProcessor`
- Use `protegrity_developer_python.find_and_protect(text)` for the protect flow — this replaces our direct Presidio AnalyzerEngine + AnonymizerEngine calls with a single API call (Presidio still runs inside Dev Edition's containers)
- Use `protegrity_developer_python.find_and_unprotect(text)` for the unprotect flow
- Use `protegrity_developer_python.discover(text)` if you need findings/entity details
- Configure via `protegrity.configure(endpoint_url=..., named_entity_map=..., ...)`
- Return the same `ProcessResult` dataclass

### Step 3: Update `main.py`

- Change import from `PresidioProcessor` to `ProtegrityProcessor`
- Add `protect` / `unprotect` subcommands
- The Presidio path can remain as a `redact` subcommand for comparison

### Step 4: Update `base.py` (minor)

Add an optional `unprotect_text()` method to the base class.  The Presidio processor raises "not supported" — this makes the capability gap explicit in code.

### Step 5: Update `requirements.txt`

```
# Remove these:
presidio-analyzer>=2.2.0
presidio-anonymizer>=2.2.0

# Add this:
protegrity-developer-python>=1.1.0
```

No more spaCy model download needed — Presidio and its models run inside the Dev Edition Docker containers.

### Step 6: Add tests

Mirror `tests/test_presidio_processor.py` for the Protegrity processor, plus:
- Test that `find_and_protect` → `find_and_unprotect` round-trips back to original text
- Test that protected output contains entity tags (e.g., `[PERSON]...[/PERSON]`)
- Test that findings/discovery returns entity details

### Step 7: Update reporters (minor)

Console report could show "protection method: tokenization" vs "protection method: redaction" to make the difference visible in the output.

## Key terminology reference

| Term | Meaning |
|------|---------|
| **Protect** | Detect PII + replace values with tokens (one call via `find_and_protect`) |
| **Unprotect** | Restore tokens back to original clear text (via `find_and_unprotect`) |
| **Redact** | Replace values with placeholders/masking chars — irreversible |
| **Data Discovery** | Dev Edition's PII detection engine — uses Presidio plus additional ML/NLP models internally |
| **Tokenization** | The protection method — values are replaced with format-preserving surrogates |
| **Application Protector** | The `appython` module for role-based protect/unprotect of structured data |

## Migration seam

The main seam is `src/processors/base.py`:

```python
class BaseProcessor(ABC):
    @abstractmethod
    def process_text(self, text: str) -> ProcessResult:
        ...
```

Any class that implements this interface can be plugged into the app with no other changes.
