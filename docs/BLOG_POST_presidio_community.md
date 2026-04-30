# Adding Reversible Tokenization to a Presidio Pipeline with Protegrity AI Developer Edition

I've been using Microsoft Presidio for PII detection in a CLI tool that sanitizes support tickets. It works well. Point it at text, get back detected entities, redact or mask as needed. For a side project processing customer support tickets (names, emails, SSNs, credit card numbers), I had a working pipeline in about an hour. Presidio's analyzer is accurate, the recognizer registry is extensible, and for straightforward detection-and-redact workflows, it just works.

But I hit a wall when my use case evolved.

## Where I needed more than redaction

The support ticket pipeline started simple: detect PII, redact it, pass sanitized tickets downstream for analysis. But once we started routing tickets with an AI model, the redacted output became a problem.

When every customer is `<PERSON>` and every phone number is `<PHONE_NUMBER>`, the model can't distinguish between tickets. You can't correlate a repeat caller. You can't spot patterns across a customer's history. The data is protected, yes, but it's also flattened into uselessness for anything beyond single-ticket processing.

What I actually needed was **reversible, format-preserving protection**. Values that look structurally valid (so downstream systems don't choke), that are consistent (same input produces same token), and that authorized users can reverse when needed.

Presidio doesn't do this, and it's not really designed to. Its anonymization operators (redact, replace, hash, mask) are all one-way by design. That's a valid architectural choice, not a limitation. But it meant I needed something else for the protection layer.

## Enter Protegrity AI Developer Edition

What caught my attention: AI Developer Edition (AIDE) actually uses Presidio internally as one of its detection models. So the detection accuracy I was already relying on carries over. AIDE layers additional ML and pattern-matching models on top.

The difference is what happens after detection. Instead of redaction, AIDE applies **tokenization**: format-preserving, reversible, policy-controlled. A name becomes a different name-shaped string. A phone number becomes a different valid-looking phone number. The structure survives, but the real values don't.

## What the migration looked like

I had already isolated my Presidio code behind a processor abstraction (`BaseProcessor` with a `process_text()` method), so the swap was mechanical:

**Before**, `presidio_processor.py` (117 lines):
- Manual `AnalyzerEngine` setup
- spaCy model download (560MB `en_core_web_lg`)
- Custom recognizer registration
- Separate `AnonymizerEngine` pass
- Manual result mapping to my data model

**After**, `protegrity_processor.py` (62 lines):
- One `find_and_protect()` API call
- Detection + protection in a single pass
- No local model management

The rest of the app (workflow logic, data models, reporters, I/O) unchanged. Six files touched total, zero business logic rewritten.

### Output comparison

Presidio redaction:
```
Customer: <PERSON>
Email: <EMAIL_ADDRESS>
Phone: <PHONE_NUMBER>
SSN: <US_SSN>
```

AIDE tokenization:
```
Customer: [PERSON]7ro8 lfU[/PERSON]
Email: [EMAIL]tK9x.pLm3@example.com[/EMAIL]
Phone: [PHONE](415) 555-8832[/PHONE]
SSN: [SSN]284-91-3056[/SSN]
```

The second version is still usable data. An AI model can distinguish between customers, route tickets, analyze patterns. It just never sees real PII.

## The capability I gained: authorized reversal

Once protection is tokenization rather than redaction, you can reverse it. Selectively. AIDE's `find_and_unprotect()` call recognizes entity tags, sends tokens to the protection service, and returns originals. But only if your role allows it.

In my pipeline:
- An `ai-support-agent` role can process and route the protected ticket. Cannot reverse.
- A `human-support-agent` role can call unprotect and recover the original values.

This is policy-controlled, not code-controlled. In production, who can detokenize is a centralized policy decision. For the demo I simulate the role gate in the processor, but the enforcement model is the same.

With Presidio's redaction, this isn't possible. There's nothing left to reverse. The original values don't exist anywhere in the output.

## Practical notes if you're considering this

**Keep your Presidio abstraction.** If your code imports `AnalyzerEngine` directly in business logic, you'll have a harder time. Push all Presidio interaction into one module with a clean interface. My abstract base class with `process_text() -> ProcessResult` made the swap trivial.

**You lose local-only operation.** Presidio runs entirely locally. AIDE calls an API endpoint. If air-gapped local processing is a hard requirement, that's a real tradeoff.

**Detection coverage expands.** Presidio's detection is one of multiple models in AIDE. I noticed it catching entity types I hadn't written custom recognizers for.

**spaCy dependency goes away.** No more managing a 560MB model download in CI/CD, no more version conflicts with other NLP libraries in your stack.

## Summary

Presidio gave me solid PII detection and got the project off the ground fast. When I needed format-preserving tokenization and reversible protection, Protegrity AI Developer Edition picked up where Presidio left off, while keeping Presidio's detection under the hood. The migration was an afternoon of work, mostly because I'd kept the Presidio code isolated.

The repo has a `presidio` branch (baseline) and a `protegrity` branch (migrated). Run `git diff presidio..protegrity --stat` to see exactly what changed: [github.com/danielbrianjohnson/presidio-to-aide](https://github.com/danielbrianjohnson/presidio-to-aide).
