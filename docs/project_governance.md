# Project Governance

**Project:** AI Language Coach  
**Version:** 1.0  
**Date:** 2026-05-30  
**Authority:** Project Architect

---

## Purpose

This document defines how development decisions are made, recorded, and executed on this project. It exists to protect three things:

1. The integrity of the architecture as the codebase grows
2. The language-pair agnosticism that is the platform's core architectural invariant
3. The ability of a solo founder to maintain and scale the project without tribal knowledge

These rules apply to every contributor, including AI coding assistants.

---

## Part 1 — Documentation as Source of Truth

### 1.1 The Docs Directory Is Authoritative

The files in `docs/` are the source of truth for this project. They take precedence over:

- Code comments
- Commit messages
- README files
- Informal Slack or chat conversations
- Memory of previous decisions

When there is a conflict between what the documentation says and what the code does, the documentation is right until a documented decision says otherwise.

### 1.2 Document Contents and Ownership

| File | What it governs | Must be updated when |
|---|---|---|
| `docs/product_spec.md` | Features, scope, user personas, MVP boundaries | A feature is added, changed, or deprioritised |
| `docs/architecture.md` | System structure, service boundaries, technology choices | A new service, layer, or technology is introduced |
| `docs/api_contract.md` | Every API endpoint: purpose, request, response | An endpoint is added, modified, or removed |
| `docs/database_schema.md` | Every table, column, index, and relationship | The database schema changes |
| `docs/development_backlog.md` | Ordered implementation tasks | A task is added, completed, or reprioritised |
| `docs/engineering_rules.md` | Code style and architectural constraints | A new constraint or convention is adopted |
| `docs/project_governance.md` | This file — process rules | The development process changes |

### 1.3 Documentation Is Not Optional

Documentation updates are not a post-implementation courtesy. They are a prerequisite for implementation.

The sequence for any non-trivial change is:

```
1. Update docs/       ← write what you intend to build
2. Review for conflicts with existing docs
3. Resolve conflicts (see Part 2)
4. Implement
5. Verify implementation matches docs

```

---

## Part 2 — Conflict Resolution

### 2.1 What Counts as a Conflict

A conflict exists when:

- A proposed implementation would require a different API shape than `api_contract.md` describes
- A proposed database change contradicts `database_schema.md`
- A proposed feature is not listed in `product_spec.md`
- A proposed architectural pattern contradicts `architecture.md` or `engineering_rules.md`
- An implementation has already diverged from a doc without a recorded decision

### 2.2 Conflict Resolution Procedure

When a conflict is identified, the following steps must be taken **before any implementation proceeds**:

**Step 1 — Identify the conflict explicitly.**

State, in writing:
- Which doc contains the conflicting statement
- Which line or section
- What the proposed implementation does differently
- Why the change is being considered

**Step 2 — Propose a documentation update.**

Write the updated doc section as it would read after the change. This is not optional — vague conflict reports without a proposed resolution are not actionable.

**Step 3 — Evaluate the impact.**

Check whether the proposed doc update cascades to other docs. API changes usually touch `api_contract.md` and may touch `architecture.md`. Schema changes touch `database_schema.md` and may touch `api_contract.md`.

**Step 4 — Obtain approval.**

For a solo founder, "approval" means a deliberate, recorded decision — not a casual override. Create an ADR in `docs/decisions/` before proceeding.

**Step 5 — Update all affected docs atomically.**

All documentation that is affected by the decision must be updated in the same commit as the ADR. No doc should be left in a state that contradicts any other doc.

### 2.3 When Urgency Pressures the Process

Production incidents, security patches, and critical bugs may require implementation before documentation is updated. In these cases:

- Implement the minimum necessary fix
- Open a `TODO` comment in the code: `# GOVERNANCE: docs not yet updated — see [description]`
- Update documentation within 24 hours
- Create an ADR if the fix represents an architectural change

This exception is narrow. Feature work and refactoring do not qualify.

---

## Part 3 — Preflight Requirements

### 3.1 Before Starting Any Implementation Session

Every new development session — including AI-assisted sessions — must begin with the following steps:

1. **Read `docs/project_governance.md`** (this file) to understand the process.
2. **Read `docs/product_spec.md`** to confirm the feature being worked on is in scope.
3. **Read the relevant doc** for the layer being changed:
   - Backend API work → `docs/api_contract.md`
   - Database work → `docs/database_schema.md`
   - Architecture changes → `docs/architecture.md`
   - New features → `docs/development_backlog.md`
4. **Check `docs/decisions/`** for any ADR that is relevant to the work.
5. **Identify conflicts** before writing a single line of code.

This preflight is not bureaucracy. It takes under five minutes and prevents hours of rework.

### 3.2 Preflight for AI Coding Assistants

When an AI coding tool (e.g. Claude Code) begins a session in this repository, it must:

1. Read this governance document first.
2. Read the relevant docs for the task described by the user.
3. Explicitly state any conflicts found before proposing or writing code.
4. Refuse to implement features that are not in `product_spec.md` without a documented doc update first.
5. Preserve the language-pair agnosticism invariant in every output (see Part 4).

---

## Part 4 — Language-Pair Agnosticism Is a Hard Constraint

### 4.1 The Invariant

This platform supports arbitrary language pairs. It does not assume:

- That the learner speaks English
- That the target language uses the Latin alphabet
- That any specific language is available
- That lesson content, prompts, or UI copy will be in English

This invariant is architectural, not preferential. It cannot be traded away for delivery speed.

### 4.2 Enforcement

Every implementation task, every doc update, and every ADR must be evaluated against the following checklist:

- [ ] Does this introduce any language-specific code path (e.g. `if language == "fr"`)?
- [ ] Does this name any database column or API field after a specific language?
- [ ] Does this hard-code a language name in a prompt, UI string, or configuration value?
- [ ] Does this assume the learner reads or writes in a left-to-right script?
- [ ] Does this assume the learner's UI language is English?

If any answer is "yes", the implementation must be revised before merging.

When implementation reveals new work:
1. Add the discovered task to development_backlog.md
2. Assign a milestone
3. Record dependencies

### 4.3 Adding a New Language

Adding support for a new language must require only:

1. One `INSERT` into the `languages` table
2. Testing the AI tutor and lesson generator with the new pair
3. Optional: curating placement assessment questions

If source code changes are required to support a new language, that is a defect in the architecture. Raise it as a conflict per Part 2, create an ADR, and fix the architecture before proceeding.

---

## Part 5 — Architecture Decision Records (ADRs)

### 5.1 What Requires an ADR

An ADR is required for any decision that:

- Introduces or replaces a technology (framework, library, AI provider, database)
- Changes how authentication or authorisation works
- Changes the data model in a way that affects existing records
- Adds a new service boundary or removes one
- Changes how AI prompts are structured or delivered
- Overrides a rule in `docs/engineering_rules.md`
- Resolves a conflict between docs and implementation

An ADR is not required for:

- Bug fixes that do not change architecture
- Styling changes
- Adding a new API endpoint that follows the existing pattern
- Adding a new lesson type that fits within `content_json`

### 5.2 ADR Location and Naming

All ADRs live in `docs/decisions/`.

Files are named: `NNN-short-slug.md` where `NNN` is a zero-padded sequence number.

```
docs/decisions/
├── 001-authentication.md
├── 002-ai-provider.md
├── 003-progress-tracking.md
└── 004-...
```

Numbers are never reused. Superseded ADRs are marked `Status: Superseded by ADR-NNN` and kept in the directory.

### 5.3 ADR Template

See `docs/decisions/000-template.md` for the canonical template. Every ADR must include:

- **Title** — short imperative phrase describing the decision
- **Status** — `Proposed` | `Accepted` | `Superseded by ADR-NNN` | `Deprecated`
- **Date** — ISO 8601
- **Context** — the problem being solved and why a decision was needed
- **Decision** — what was decided, stated plainly
- **Rationale** — why this option was chosen over alternatives
- **Alternatives Considered** — other options evaluated and why they were rejected
- **Consequences** — what becomes easier, what becomes harder, what is now constrained
- **Compliance Check** — explicit confirmation that language-pair agnosticism is preserved

### 5.4 ADR Lifecycle

```
Proposed → Accepted → (if revisited) → Superseded
                                     → Deprecated
```

A `Proposed` ADR may be discussed and modified. Once `Accepted`, it is immutable — supersede it with a new ADR rather than editing it.

---

## Part 6 — Feature Development Workflow

### 6.1 The Full Sequence

```
┌─────────────────────────────────────────────────────────┐
│  1. PREFLIGHT                                           │
│     Read relevant docs. Identify conflicts.             │
└──────────────────────┬──────────────────────────────────┘
                       │ No conflicts found
┌──────────────────────▼──────────────────────────────────┐
│  2. DOC UPDATE                                          │
│     Update product_spec, architecture, api_contract,    │
│     database_schema as appropriate.                     │
│     Create ADR if architectural decision required.      │
└──────────────────────┬──────────────────────────────────┘
                       │ Docs updated and consistent
┌──────────────────────▼──────────────────────────────────┐
│  3. IMPLEMENT                                           │
│     Write code that matches the docs exactly.           │
│     No undocumented decisions during implementation.    │
└──────────────────────┬──────────────────────────────────┘
                       │ Implementation complete
┌──────────────────────▼──────────────────────────────────┐
│  4. VERIFY                                              │
│     Confirm implementation matches docs.                │
│     Run tests. Smoke test the changed flows.            │
└──────────────────────┬──────────────────────────────────┘
                       │ Verified
┌──────────────────────▼──────────────────────────────────┐
│  5. BACKLOG UPDATE                                      │
│     Mark task completed in development_backlog.md.      │
│     Note any new tasks discovered during implementation.│
└─────────────────────────────────────────────────────────┘
```

### 6.2 Commit Discipline

- Documentation updates and the implementation they describe should be in the same commit where practical.
- Commit messages reference the backlog task ID (e.g. `M1-06: implement /chat endpoint`).
- ADR creation is always a separate commit with message `ADR-NNN: <title>`.

---

## Part 7 — What This Document Does Not Govern

- Day-to-day code review comments on style
- Tactical implementation choices within an agreed architecture (e.g. variable naming, loop structure)
- Test strategy within an agreed service (unit vs integration is governed by `engineering_rules.md`)
- Business decisions (pricing, marketing, partnerships)

These are left to the judgment of the developer.

---

## Part 8 — Definition of a completed development backlog item

A backlog item is complete only when:

- Implementation is finished
- Tests pass
- Documentation is updated (if required)
- No conflicts remain
- The task is marked complete in development_backlog.md

---

## Appendix — Quick Reference Card

```
Before coding:         Read governance.md + relevant docs
Found a conflict?      Document it → propose doc update → create ADR → then code
New feature?           Update product_spec.md + api_contract.md first
New endpoint?          Update api_contract.md first
Schema change?         Update database_schema.md first
Architecture change?   Create ADR in docs/decisions/
Language question?     If it names a language in code → it's wrong
AI session starts?     AI must read this doc before producing code
```
