# tcf-runtime

Executable runtime for the [Tiered Content Framework](https://www.jediwright.com/content-strategy-framework). This repository **implements** the framework; it is **not** its canonical text. The framework is versioned and amended on its published page. This repository tracks that page and never leads it.

## What this is

The TCF defines how content is structured, labeled, and governed across seven tiers, with epistemic status (confirmed / inferred / unverified / time-sensitive) declared at the Particle level and inherited upward by the weakest member. That is a set of rules. This repository is the machinery that enforces them:

- **Quark store** — the versioned, content-addressed collection of constraints the framework calls "governed at the Quark level"
- **Shape library** — SHACL shapes, pinned by version IRI and digest, that make those constraints checkable
- **Write-time epistemic gate** — refuses or annotates a content write at introduction, before it is committed
- **Propagation** — computes composite-tier status from members; never declared by an author
- **Fixtures** — the test cases that define what "working" means at each phase

Governing document: [`spec/tcf-runtime-spec-v0-1_2026-08-24.md`](spec/tcf-runtime-spec-v0-1_2026-08-24.md). Current build plan: [`spec/tcf-runtime-phase0-build-plan-v0-1-2_2026-09-10.md`](spec/tcf-runtime-phase0-build-plan-v0-1-2_2026-09-10.md).

## What this is not

- Not the framework. Amendments to the TCF happen on the published page, by session; this repository re-issues its spec to match.
- Not tied to a platform. Python and a file-backed store are the first implementation; local-first substrates (Automerge) are the first pairing, reached through an adapter, not assumed. Other pairings are expected.
- Not the publish-side crossing gate. That is [Pattern Commons #9](https://github.com/jediwright/local-first-series) and reads this runtime's outputs; it does not live here.
- Not the content-production product suite. Different lifecycle, separate home when it exists.

## Layout

```
spec/            governing runtime spec and build plans
runtime/
  store/         store model, canonicalization, digest; adapters/ (file first)
  shapes/        SHACL Turtle by version IRI; the STATUS_RANK constant and VALUES generator
  gate/          write-time gate, propagation, validation reports
fixtures/        test cases as JSON-LD with expected outcomes
records/         build records, findings tables, session handoffs
conformance/     reserved for the TCF v1.8 self-conformance suite
docs/vocab/tcf/  published vocabulary versions (GitHub Pages target)
```

Vocabulary namespace: `https://jediwright.github.io/tcf-runtime/vocab/tcf#`. Library versions are pinned by content digest; the IRI identifies, it does not need to resolve.

## Status

**Phase 0 — not started.** Scope: the write-time gate on fixtures, engine pinned, every refusal path reached by a real run. Exit criteria are in the build plan §8. Nothing here stops a real publish yet.

All `tcf:` field names are TCF v1.7 *candidates* pending a v1.8 ruling. Every claim in `spec/` is single-context and unpaneled until stated otherwise.

## Lineage

Runtime spec issued 2026-08-24 as a companion to Pattern Commons #9 (Survival Ledger SL-0148). Build-first sequencing adopted 2026-09-10. Related work: [seam-stack](https://github.com/jediwright/seam-stack), [local-first-series](https://github.com/jediwright/local-first-series), [selvage](https://github.com/jediwright/selvage).

## License

MIT — Jedi Wright, Systems of Thought, UX Minds, LLC. AI-collaborative drafting, human authorial responsibility, intellectual direction held by the named author.

## State

**Phase 0 complete (2026-09-11).** A working write-time gate on fixtures with the engine pinned (pyshacl 0.40.1 / rdflib 7.6.0). See [`records/phase0-build-record_2026-09-11.md`](records/phase0-build-record_2026-09-11.md) for what "functional" means, what it does not, and the findings table feeding runtime v0.2 and TCF v1.8.

## Run

```
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.lock
python -m tools.seal_store
python -m tools.check_b1_b2
python -m tools.run_fixtures
```
