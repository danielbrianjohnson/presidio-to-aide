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

## Demo script — full rundown

> Everything below is meant to be followed top-to-bottom during the recording.
> Each step includes the **git branch**, the **terminal commands**, and the **talk track**.
>
> The `protegrity` branch has **two commits**:
> 1. **"migrate to Protegrity Developer Edition"** — the clean swap (6 files)
> 2. **"add unprotect capability"** — new feature only possible after migration (4 files)

---

### Part 1 — Presidio baseline

**Branch:** `main`

**Setup (do before recording, or show quickly):**

```bash
git checkout main
source .venv/bin/activate
```

> Confirm venv has Presidio installed — if fresh, run:
> `pip install -r requirements.txt && python -m spacy download en_core_web_lg`

**Step 1 — Show the input ticket:**

```bash
cat ticket.txt
```

> "Here's our starting point — a plain-text support ticket.  It has a customer name, email, phone number, SSN, account number, a credit card number, and an invoice ID.  This is the kind of thing a support team might receive every day.  We need to sanitize it before it goes downstream."

**Step 2 — Run the Presidio baseline:**

```bash
python -m src.main --input ticket.txt --output-dir output
```

> "We're using Microsoft Presidio — a great open-source PII detection and redaction library.  Let's run it."
>
> *[wait for output]*
>
> "Presidio found 8 entities across 7 types.  It correctly identified the person name, email, phone numbers, SSN, credit card, and even our custom account number and invoice ID.  The sanitized output replaces each value with a placeholder like `<PERSON>` or `<US_SSN>`."

**Step 3 — Show the sanitized output:**

```bash
cat output/sanitized_ticket.txt
```

> "That's solid — every sensitive value has been replaced.  The PII is gone."
>
> "But here's the thing — it's *gone*.  This is irreversible redaction.  `Sarah Johnson` is now `<PERSON>`, and there's no getting her back.  If a downstream system needs the name, or an authorized analyst needs to see the original, we're out of luck.  We've also lost data utility — every person in the system is the same `<PERSON>` placeholder, so you can't distinguish customers, join records, or run analytics."

**Step 4 — Transition to Protegrity:**

> "Presidio is a great open-source project for detection and redaction.  What's cool is that Protegrity Developer Edition actually uses Presidio internally as part of its detection pipeline — along with additional ML and context-based models.  But instead of us managing Presidio directly — wiring up the AnalyzerEngine, downloading a 560MB spaCy model, writing custom recognizers — Dev Edition handles all of that behind a single API call.  And on top of detection, it adds a protection layer — tokenization and unprotect — that Presidio alone can't do."
>
> "Let's walk through what that migration looks like."

---

### Part 2 — The migration diff

**Branch:** still on `main` (we're looking at the diff, not switching yet)

**Step 5 — Show the migration commit:**

```bash
git log main..protegrity --oneline
```

> "The protegrity branch has two commits.  The first is the migration itself — swapping Presidio for Protegrity.  The second adds the unprotect capability, which is only possible because of the migration.  Let's look at the migration commit first."

**Step 6 — Show the migration diff summary:**

```bash
git diff main..protegrity~1 --stat
```

> "Six files changed.  That's the entire migration.  Let's walk through them."

**Step 7 — Show the processor swap:**

```bash
git diff main..protegrity~1 -- src/processors/presidio_processor.py src/processors/protegrity_processor.py
```

> "This is the core change.  We delete `presidio_processor.py` — that's 117 lines where we were manually setting up Presidio's AnalyzerEngine, AnonymizerEngine, and custom recognizers.  We replace it with `protegrity_processor.py` — 62 lines.  It calls `find_and_protect()` — one function that does detection and tokenization in a single call.  Presidio is still running inside Dev Edition's Docker containers doing detection, we just don't manage it anymore."

**Step 8 — Show the config and import changes:**

```bash
git diff main..protegrity~1 -- src/config.py src/processors/__init__.py src/main.py
```

> "The rest is boilerplate.  Config swaps Presidio settings for Protegrity endpoint and entity map.  The `__init__` and `main.py` each swap one import line.  That's it — three lines of actual logic changed."

**Step 9 — Show the requirements change:**

```bash
git diff main..protegrity~1 -- requirements.txt
```

> "Dependencies get simpler.  We drop `presidio-analyzer`, `presidio-anonymizer` — and the 560MB spaCy model download.  We add one dependency: `protegrity-developer-python`, which talks to the Dev Edition Docker services."

**Step 10 — Show what didn't change:**

```bash
git diff main..protegrity~1 -- src/app.py src/models.py src/io_utils.py src/reporters/ src/processors/base.py
```

> "And here's the payoff of the clean architecture — `app.py`, `models.py`, `io_utils.py`, `base.py`, the reporters — zero changes.  The processor abstraction did its job.  The rest of the app doesn't know or care whether Presidio or Protegrity is doing the work."
>
> "Same CLI, same output format, same everything.  Just a different engine under the hood."

---

### Part 3 — Run the Protegrity version (protect)

**Step 11 — Switch to the protegrity branch:**

```bash
git checkout protegrity
```

> Confirm Dev Edition Docker services are running:
> `docker compose -f /path/to/protegrity-developer-edition/docker-compose.yml ps`
>
> Confirm protegrity module is installed:
> `pip install protegrity-developer-python`

**Step 12 — Run protect:**

```bash
python -m src.main protect --input ticket.txt --output-dir output
```

> "Now let's run the Protegrity version.  Same ticket, same command — we just added a `protect` subcommand."
>
> *[wait for output]*
>
> "Notice the difference.  The output has entity tags with tokenized values inside them — like `[PERSON]7ro8 lfU[/PERSON]` instead of just `<PERSON>`.  The sensitive values have been replaced with tokens by Protegrity's protection engine."

**Step 13 — Show the protected output:**

```bash
cat output/sanitized_ticket.txt
```

> "This is fundamentally different from what Presidio did.  The data is protected, not destroyed.  A downstream system can still see that there's a person, a phone number, an SSN — the structure is preserved.  But the actual values are tokens."
>
> "And Presidio is still running inside Dev Edition doing detection — along with additional models — we just don't manage it anymore.  Detection and protection happened in one API call."

---

### Part 4 — Unprotect (the feature Presidio can't do)

**Branch:** `protegrity`

> "This is the second commit — the feature we get *because* we migrated."

**Step 14 — Show what the unprotect commit added:**

```bash
git diff protegrity~1..protegrity --stat
```

> "Four small files.  We added `unprotect_text()` to the processor, a `run_unprotect` workflow, and protect/unprotect subcommands.  This was only 70 lines of new code — and it gives us a capability Presidio simply doesn't have."

**Step 15 — Run unprotect:**

```bash
python -m src.main unprotect --input output/sanitized_ticket.txt --output-dir output/recovered
```

> "Now here's what Presidio simply cannot do.  I'm going to take that protected ticket and unprotect it — restore the original values."
>
> *[wait for output]*

**Step 16 — Show the restored output:**

```bash
cat output/recovered/restored_ticket.txt
```

> "The original data is back — `Sarah Johnson`, the real SSN, the real credit card number.  The `find_and_unprotect()` API recognized the entity tags, sent the tokens to the protection service, and got back the originals."
>
> "With Presidio, once you redact, the data is gone forever.  With Protegrity, protection is reversible — and in a production deployment, that reversal is controlled by policies and user roles."

---

### Part 5 — Wrap-up

**Branch:** `protegrity`

> "To recap: we started with a working Presidio baseline — calling Presidio directly for detection and irreversible redaction.  We migrated to Protegrity Developer Edition by swapping one processor file, updating config and imports — six files total, zero changes to business logic."
>
> "Presidio is still running inside Dev Edition doing detection, but now it's managed for us, augmented with additional models, and paired with a protection layer that gives us reversible tokenization and unprotect."
>
> "Then, in a second small commit, we added the unprotect capability — something Presidio can't do at all.  That's the real payoff of the migration."

---

### Quick-reference: command cheat sheet

| Step | Branch | Command |
|------|--------|---------|
| Show ticket | `main` | `cat ticket.txt` |
| Run Presidio | `main` | `python -m src.main --input ticket.txt --output-dir output` |
| Show Presidio output | `main` | `cat output/sanitized_ticket.txt` |
| Show commits | `main` | `git log main..protegrity --oneline` |
| Migration diff summary | `main` | `git diff main..protegrity~1 --stat` |
| Diff processors | `main` | `git diff main..protegrity~1 -- src/processors/presidio_processor.py src/processors/protegrity_processor.py` |
| Diff config/imports | `main` | `git diff main..protegrity~1 -- src/config.py src/processors/__init__.py src/main.py` |
| Diff requirements | `main` | `git diff main..protegrity~1 -- requirements.txt` |
| Diff unchanged files | `main` | `git diff main..protegrity~1 -- src/app.py src/models.py src/io_utils.py src/reporters/ src/processors/base.py` |
| Switch branch | — | `git checkout protegrity` |
| Run protect | `protegrity` | `python -m src.main protect --input ticket.txt --output-dir output` |
| Show protected output | `protegrity` | `cat output/sanitized_ticket.txt` |
| Unprotect commit diff | `protegrity` | `git diff protegrity~1..protegrity --stat` |
| Run unprotect | `protegrity` | `python -m src.main unprotect --input output/sanitized_ticket.txt --output-dir output/recovered` |
| Show restored output | `protegrity` | `cat output/recovered/restored_ticket.txt` |

---

## What stays unchanged during migration (commit 1)

| File / Directory             | Reason                                      |
|------------------------------|---------------------------------------------|
| `src/app.py`                 | Processor-agnostic — only calls `process_text()` |
| `src/models.py`              | Shared data contract (`ProcessResult`, `Finding`) |
| `src/io_utils.py`            | Reads/writes files — no processor logic     |
| `src/reporters/`             | Consumes `ProcessResult` — no processor logic |
| `src/processors/base.py`     | Abstract interface stays the same            |
| `src/main.py`                | Only the import line changes (1 line)        |
| `ticket.txt`                 | Same input for both processors              |

## What changes in the migration (commit 1)

| File                               | Change                                        |
|-------------------------------------|-----------------------------------------------|
| `src/processors/presidio_processor.py` | **Deleted** (117 lines)                      |
| `src/processors/protegrity_processor.py` | **Added** (62 lines)                       |
| `src/config.py`                     | Swap Presidio settings → Protegrity endpoint + entity map |
| `src/processors/__init__.py`        | Swap import (1 line)                          |
| `src/main.py`                       | Swap import + processor instantiation (2 lines) |
| `requirements.txt`                  | Remove Presidio deps, add `protegrity-developer-python` |

## What the unprotect feature adds (commit 2)

| File                               | Change                                        |
|-------------------------------------|-----------------------------------------------|
| `src/processors/base.py`            | Add `unprotect_text()` with `NotImplementedError` default |
| `src/processors/protegrity_processor.py` | Add `unprotect_text()` implementation       |
| `src/app.py`                        | Add `run_unprotect()` workflow                |
| `src/main.py`                       | Add `protect`/`unprotect` subcommands         |

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

### Step 2: Swap the processor

Delete `src/processors/presidio_processor.py`.  Create `src/processors/protegrity_processor.py`:
- Subclass `BaseProcessor`
- Use `protegrity_developer_python.find_and_protect(text)` — replaces direct Presidio AnalyzerEngine + AnonymizerEngine calls with a single API call
- Configure via `protegrity.configure(endpoint_url=..., named_entity_map=...)`
- Return the same `ProcessResult` dataclass

### Step 3: Update config, imports, and dependencies

- `src/config.py`: Replace Presidio settings with `PROTEGRITY_ENDPOINT_URL` and `PROTEGRITY_ENTITY_MAP`
- `src/processors/__init__.py`: Swap `PresidioProcessor` import → `ProtegrityProcessor`
- `src/main.py`: Swap import (1 line) and processor instantiation (1 line)
- `requirements.txt`: Remove `presidio-analyzer`, `presidio-anonymizer`, add `protegrity-developer-python>=1.1.0`

No more spaCy model download needed — Presidio and its models run inside the Dev Edition Docker containers.

### Step 4 (optional): Add unprotect capability

This is a separate feature add, not required for the migration:
- Add `unprotect_text()` to `src/processors/base.py` with `NotImplementedError` default
- Implement `unprotect_text()` in `protegrity_processor.py` using `find_and_unprotect()`
- Add `run_unprotect()` to `src/app.py`
- Add `protect`/`unprotect` subcommands to `src/main.py`

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
