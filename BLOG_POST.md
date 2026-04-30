# Migrating from Microsoft Presidio to Protegrity Developer Edition: What Changes and What You Get

If you've worked with PII detection in Python, you've probably run into [Microsoft Presidio](https://github.com/microsoft/presidio). It's a solid open-source library. You point it at some text, it finds the sensitive stuff, and it can redact or mask it for you. A lot of teams use it, and for good reason. It works.

I've been using it in a small CLI tool that sanitizes support tickets before they go downstream. Customer name, email, phone number, SSN, credit card number, account number. The usual stuff that shows up in a support ticket and absolutely shouldn't leave the support system unprotected.

Presidio handles that well. But there's a catch, and it's a big one.

## The problem with irreversible redaction

When Presidio redacts a value, it's gone. `Sarah Johnson` becomes `<PERSON>`. That's it. There's no going back.

For some use cases that's fine. But if you need a downstream system to actually work with the data, if you need an AI model to distinguish between customers, or if an authorized analyst needs to see the original value later, you're stuck. Every person in the system is the same `<PERSON>` placeholder. You can't join records, you can't correlate tickets, and you can't run meaningful analytics on redacted data. The PII is protected, sure, but the data is also dead.

That's what pushed me to look at Protegrity Developer Edition.

## What Protegrity Developer Edition actually is

Here's the thing that surprised me: Protegrity Developer Edition uses Presidio internally. Its Data Discovery service includes Presidio as one of multiple detection models, alongside additional ML, NLP, and pattern-matching models. So you're not throwing Presidio away. You're just not managing it directly anymore.

No more wiring up the `AnalyzerEngine`. No more downloading a 560MB spaCy model. No more writing custom recognizers by hand. Dev Edition handles all of that behind a single API call.

But the real win isn't the simpler detection setup. It's what comes after detection.

Instead of irreversible redaction, Protegrity gives you **tokenization**. The sensitive values get replaced with format-preserving tokens. Names still look like names. Phone numbers still look like phone numbers. The structure of the data is preserved, but the actual PII is gone. A downstream AI model can still route tickets, analyze sentiment, and spot trends because it has context to work with. It's not staring at a wall of identical `<PERSON>` placeholders.

And because it's tokenization, not redaction, it's **reversible**. If an authorized user needs the real values back, they can get them. If an unauthorized user tries, they can't. That's controlled by role-based policies.

## The migration: six files

I intentionally built the Presidio version with a processor abstraction. There's a `BaseProcessor` abstract class, and the Presidio-specific code lives in one file: `presidio_processor.py`. The rest of the app, the workflow logic, the data models, the reporters, the I/O helpers, none of it knows or cares what's doing the detection.

That paid off. The migration to Protegrity Developer Edition touched **six files**:

1. **The processor** - Swapped `presidio_processor.py` (117 lines) for `protegrity_processor.py` (62 lines). One `find_and_protect()` call replaces the manual `AnalyzerEngine` / `AnonymizerEngine` setup. Detection and protection happen in a single API call.

2. **Config** - Swapped Presidio settings (language, placeholder template) for the Protegrity endpoint URL and entity map. Simpler.

3. **Requirements** - Dropped `presidio-analyzer`, `presidio-anonymizer`, and the spaCy model dependency. Added `protegrity-developer-python`.

4. **The import in main.py** - Changed `from src.processors.presidio_processor import PresidioProcessor` to `from src.processors.protegrity_processor import ProtegrityProcessor`.

5. **The processor init and CLI** - Updated `main.py` to use subcommands (`protect` / `unprotect`) since we now have both capabilities.

6. **The __init__.py** - Updated the processors package export.

That's the whole migration. Everything else, `app.py`, `models.py`, `io_utils.py`, `base.py`, the reporters, zero changes. The processor abstraction did its job.

## What the output looks like

With Presidio, a protected ticket looks like this:

```
Customer: <PERSON>
Email: <EMAIL_ADDRESS>
Phone: <PHONE_NUMBER>
SSN: <US_SSN>
```

With Protegrity, it looks like this:

```
Customer: [PERSON]7ro8 lfU[/PERSON]
Email: [EMAIL]tK9x.pLm3@example.com[/EMAIL]
Phone: [PHONE](415) 555-8832[/PHONE]
SSN: [SSN]284-91-3056[/SSN]
```

The difference is significant. The Protegrity output still has structure. An AI model processing this ticket can tell there's a person, a phone number, an SSN. It can work with the data. It just can't see the real values.

## The feature Presidio can't do: unprotect

This is the part that made the migration worth it. After swapping to Protegrity, I added an `unprotect` capability in about 70 lines of new code across four files. It calls `find_and_unprotect()`, which recognizes the entity tags, sends the tokens to the protection service, and gets back the originals.

But not for everyone. There's a role gate.

An `ai-support-agent` tries to unprotect? Access denied. It can work with the protected ticket, route it, summarize it, whatever. But it never sees the real PII.

A `human-support-agent` tries? The original data comes back. `Sarah Johnson`, the real SSN, the real credit card number. All restored.

In a production Protegrity deployment, this is enforced by the policy engine. Who can reverse tokenization is a policy decision, not a code decision. For the demo I'm simulating that gate in the processor, but the concept is the same.

With Presidio, once you redact, the data is gone forever. There's no unprotect because there's nothing left to unprotect.

## The architecture takeaway

If you're currently using Presidio and thinking about this kind of migration, the biggest favor you can do for yourself is to isolate your Presidio code behind an abstraction. Don't let your business logic import Presidio directly. Push all of it into one processor class, and have the rest of your app work with a generic interface.

I used an abstract base class with a `process_text()` method that returns a `ProcessResult` dataclass. That's it. When it came time to migrate, I wrote a new processor, updated one import, and everything else stayed the same. Same CLI, same output format, same tests (with minor updates for the new entity tag format).

It's not a complicated pattern. But it made a migration that could have been a multi-day rewrite into something I knocked out in an afternoon.

## Wrapping up

Presidio is good software. If all you need is PII detection and you're fine with irreversible redaction, it does the job and it's free. No complaints.

But if you need your protected data to still be useful, if you need AI and analytics pipelines to work with real structure instead of generic placeholders, and if you need authorized users to be able to get back to the original values, that's where Protegrity Developer Edition picks up. Presidio is still doing detection work under the hood. You just get tokenization, reversibility, and role-based access on top of it.

Six files changed. Zero business logic rewritten. And a whole new set of capabilities that weren't possible before.

If you want to see the full migration in action, I walked through it step by step in [the video demo]. The repo is structured so you can check out the `main` branch for the Presidio baseline and the `protegrity` branch for the migrated version, and diff them yourself.
