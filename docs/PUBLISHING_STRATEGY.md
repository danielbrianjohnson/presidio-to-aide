# Publishing Strategy

## Overview

This project has two audiences and two publishing channels. The content is tailored differently for each.

---

## Channels

### 1. Presidio Community (developer audience)

**Goal:** Establish credibility within the Presidio ecosystem, demonstrate that AIDE builds on (not replaces) Presidio, and attract developers who've hit the same "redaction is irreversible" wall.

**Assets:**
- Blog post: `docs/BLOG_POST_presidio_community.md`
- Repo with branch diff: https://github.com/danielbrianjohnson/presidio-to-aide

**Where to post:**
- [ ] Presidio GitHub Discussions (primary)
- [ ] Reddit r/Python or r/machinelearning (optional, if we want broader reach)
- [ ] Personal blog / dev.to / Medium (optional amplification)

**Tone:** Factual, developer-to-developer. "I used Presidio, it worked, I needed more, here's what I did." No marketing language.

**CTA:** Clone the repo, run the diff, try AIDE.

---

### 2. Protegrity Blog (business/technical audience)

**Goal:** Showcase AIDE's value proposition (data stays useful while protected) through a relatable scenario. Supports sales/marketing narrative around AI-ready data protection.

**Assets:**
- Blog post: `docs/BLOG_POST_protegrity.md`
- Demo video (TBD)
- Repo link for technical readers who want to dig in

**Where to post:**
- [ ] Protegrity blog (exact URL TBD, marketing team manages publication)
- [ ] GitHub Discussion on [Protegrity-Developer-Edition](https://github.com/orgs/Protegrity-Developer-Edition/discussions) (per publishing guidelines)
- [ ] LinkedIn (promotion once live)

**Tone:** Narrative/story. Customer problem, solution, outcome. Still technical enough to be credible but accessible to non-developers.

**CTA:** Try AI Developer Edition, watch the demo.

---

## Assets Inventory

| Asset | Status | Location |
|-------|--------|----------|
| Presidio community blog post | Draft complete | `docs/BLOG_POST_presidio_community.md` |
| Protegrity blog post | Draft complete | `docs/BLOG_POST_protegrity.md` |
| Demo video | Complete, ready to post | YouTube (TBD), current: [SharePoint link](https://protegrity-my.sharepoint.com/personal/kalai_leauanae_protegrity_com/_layouts/15/stream.aspx?id=%2Fpersonal%2Fkalai%5Fleauanae%5Fprotegrity%5Fcom%2FDocuments%2FMicrosoft%20Teams%20Chat%20Files%2FPresidioDemo%5FAIDevEd%2Emp4) |
| GitHub repo (personal) | Live | https://github.com/danielbrianjohnson/presidio-to-aide |
| AIDE community-solutions PR | Not started | Protegrity-Developer-Edition org repo |
| AIDE GitHub Discussion | Not started | https://github.com/orgs/Protegrity-Developer-Edition/discussions |
| Presidio GitHub Discussion | Not started | https://github.com/microsoft/presidio/discussions |

---

## Sequencing

1. **Finalize blog posts** - incorporate any remaining feedback
2. **Post video to YouTube** - coordinate timing with blog publication
3. **Post to Presidio community** - GitHub Discussion, link repo + blog post
4. **Submit PR to AIDE repo** - per publishing guidelines
5. **Protegrity blog** - hand off to marketing (Auria/Franz for hook/angle)
6. **Update links** - swap video placeholder in README + blog posts with YouTube URL before merging
7. **LinkedIn/social** - once Protegrity post is live

---

## Open Questions

- Who owns the Protegrity blog post editing/publication? (Auria? Franz? Marketing team?)
- Do we want a dev.to cross-post for the Presidio version?
- Video format: full walkthrough vs. short highlight reel?
- Reddit: worth the effort or skip for now?
- Timing: coordinate Presidio + Protegrity posts, or stagger them?

---

## Stakeholders

| Person | Role |
|--------|------|
| Dan | Author, repo owner, demo builder |
| Auria | Marketing hook/angle (Protegrity post) |
| Franz | Potential input on Protegrity post |
| Ran | AIDE shortform credit |
