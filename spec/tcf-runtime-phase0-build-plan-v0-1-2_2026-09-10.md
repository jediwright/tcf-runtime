**Status:** v0.1.2 — build plan (Session Harness v0.2, Lightweight Mode); single-context; companion to TCF Runtime Spec v0.1 and PC#9 v0.3; **not a TCF amendment**

⚑ SINGLE-CONTEXT — NOT PANELED
All `tcf:` field names remain (c) per runtime spec RL-1. This plan builds to the runtime spec as written with one declared deviation: the vocabulary namespace base is `https://jediwright.github.io/tcf-runtime/vocab/tcf#` (v0.1.2), not the spec §0 `seam-stack` base. Every other deviation the build surfaces is queued, not applied.

---

# TCF Runtime — Phase 0 Build Plan v0.1.2

## A small working version of the write-time epistemic gate, on fixtures, with the engine pinned

---

## 0. Posture and scope

**Decision this plan implements (operator, 2026-09-10):** build-first. A minimal executable gate precedes the TCF v1.8 session; what the build surfaces becomes v1.8 input. This inverts handoff step 6 (2026-08-24), which sequenced the Phase 0 build after Counter-Pass close. The inversion is deliberate and scoped: Phase 0 here builds the **author-side write-time gate** (runtime spec §5), not the PC#9 crossing gate. The crossing gate stays behind its own program.

**What "functional" means at Phase 0 exit.** The gate loads a pinned, content-addressed shape library; validates a write set of content-graph nodes against Family B and Family C shapes; enforces the upgrade and derivation rules; computes weakest-status propagation bottom-up; writes validation reports; and refuses or accepts each fixture with the outcome the runtime spec predicts. Every refusal path in §5.4 is reached by at least one fixture from a real run.

**What it is not.** Not a prototype of PC#9. Not Automerge-integrated (see D-3). Not a shape *library* — Family A gets one illustrative shape so the report path is exercised, nothing more (RL-4 holds). Not a generality claim: one engine, one language, one fixture set. No performance claim beyond one recorded measurement (RL-7 informational).

---

## 1. Carry-in and state at open

| Item | Value | Method | Tag |
|---|---|---|---|
| Runtime spec | `tcf-runtime-spec-v0-1_2026-08-24.md` — read in full this session | file read | ✓ |
| Handoff | `session-handoff-pc09-v0-2-and-tcf-runtime-spec_2026-08-24.md` — read in full | file read | ✓ |
| PC#9 | v0.3 (`…-v0-3_2026-08-28.md`, 540 l.) — gate steps and change log read; live per project record 2026-08-28 | file read; HEAD not fetched this session | ~ |
| Companion v0.1.1 amendment | Queued by PC#9 v0.2.2/v0.2.3 (`tcf:q/register/grant-requirement` declared-but-not-evaluated Quark in library; §2.3/§6) — **not yet applied** to the runtime spec | PC#9 change log read | ✓ (queued) / ~ (not applied) |
| Runtime spec placement | **not placed** as of 2026-09-10; destination now decided: `tcf-runtime` repo (§10 D-1), repo not yet created | operator statement | ✓ |
| TCF v1.8 session | not opened | operator statement | ✓ |
| Survival Ledger tail | project record says on-disk tail SL-0221, SL-0223–0226 issued as files pending append, SL-0222 reserved, next free SL-0227 | **not verified by file read this session** | ? |
| UFO Lexicon | v2.6 current per project record; v2.7 queued | not read | ~ |
| Assumption (g) | SHACL-SPARQL engine on author's substrate | resolved by §4 of this plan | — |

The build session MUST re-verify the ledger tail by direct file read before assigning any ID (§11).

---

## 2. What Phase 0 builds

Six components, each mapped to the runtime spec section it implements. Build in this order (§7).

| # | Component | Implements | Phase 0 form |
|---|---|---|---|
| C-1 | **Quark store loader** | §2.3 invariants | Reads a store document (JSON), recomputes `versionDigest` over canonical JSON of `quarks + shapes + context`, refuses on mismatch (`E-STORE-INVALID`). Canonicalization: RFC 8785 (JCS) or equivalent deterministic serialization — pinned in build, recorded as a finding if it matters. |
| C-2 | **Shape library @ version** | §3.1 (one illustrative Family A shape), §3.2 Family B, §3.3 record shapes, §3.4 Family C with §7.2 `VALUES` table inlined | Turtle files content-addressed by sha256; admitted only if Family A shapes carry `tcf:quarkId` and `tcf:constraintClass`. Includes `tcf:q/register/grant-requirement` as a declared-but-not-evaluated Quark record (companion v0.1.1, applied here as a *build* choice — see §10 note). |
| C-3 | **Write-time gate** | §5.1–5.4 | A function `gate(store, graph, writeSet) → Accept(commit) \| Reject(code)` executing §5.2 steps 1–8 in order. Step 8 "commit" = write to an in-memory graph and emit the change as a JSON patch (D-3). |
| C-4 | **Propagation** | §7.1–7.4 | The §7.3 CONSTRUCT run six times in tier order, plus §7.4 register propagation (computed, non-enforcing). Absent status yields absent `computedStatus`; no default. |
| C-5 | **Validation report store** | §6 | Per-node `sh:ValidationReport` serialized and content-addressed; `tcf:validationReport` on the node = report sha256. Filter function producing the §6 `tcfQuarkViolations` shape from a root node + `minimumTcfTier`, exposed for later PC#9 use but **not called by any Phase 0 gate step**. |
| C-6 | **Fixture runner** | this plan §6 | Loads each fixture, runs the gate, asserts the expected outcome, prints a results table. Exit criterion lives here. |

**Error vocabulary is exactly §5.4** — six write-rejecting codes. The build adds no codes. If a needed refusal has no code, that is a finding (§9), not a new code.

---

## 3. Out of scope (named so it stays out)

- PC#9 crossing gate steps 1–10; grants; intent/completion records; `evidenceDecay` at submission (§7.5) — a pure-function test of §7.5 over store fields is **optional** (F-15) and asserts nothing about the crossing.
- Automerge as substrate (D-3). GSEF change events on the store (§8) — store versions in Phase 0 are two hand-authored files, v-A and v-B, used only to exercise pinning.
- `tcf:register` semantics. §7.4 is computed and recorded; nothing enforces it (KL-4).
- Family A shape library. One illustrative terminology shape only, so a non-blocking report entry exists.
- Any ruling on KL-11 (§5).
- Second substrate, second engine, second language (RL-5).
- Performance beyond one measured run of §7.3 on the largest fixture (RL-7 stays open; number is informational).

---

## 4. Engine decision — resolves assumption (g) / RL-6

**Requirement:** SHACL Core + **SHACL-SPARQL** (`sh:sparql` constraint components), since Family C (§3.4) is a SPARQL-based constraint and §7.3 is a SPARQL CONSTRUCT. Engines without SHACL-SPARQL cannot run this spec as written.

**Pinned for Phase 0: `pyshacl`** (Python, on `rdflib`) — advertises SHACL-SPARQL support; `rdflib` supplies the CONSTRUCT engine for §7.3 in the same runtime. Tag: **~** — support asserted from working knowledge, not primary-source read this session. The build session's first task (B-0) is to confirm it by running Family C against F-09 and observing the `sh:sparql` violation fire. If it does not, the pin fails and the session halts on that finding.

**Rejected / deferred:**
- TypeScript engines (`rdf-validate-shacl`, `shacl-engine`): SHACL-SPARQL support **?** — unverified. Relevant because the PC#8 harness and Selvage are TypeScript; a Python gate is a language seam the eventual Automerge integration will have to cross. **Named as D-2** (operator decision), not resolved here. Phase 0 tolerates the seam because the gate is fixture-only.
- Java (TopBraid SHACL / Jena): full SHACL-SPARQL, but a heavier runtime than the substrate story can carry. Not considered further.

**Pin record.** The build session records engine name, exact version, and the sha256 of the lockfile in the Phase 0 build record. `tcfShapeVersion` for the Phase 0 library: `https://jediwright.github.io/tcf-runtime/vocab/tcf/2026-09-<build-date>` (c). Namespace base for all `tcf:` IRIs in shapes, context, and fixtures: `https://jediwright.github.io/tcf-runtime/vocab/tcf#`. The IRI need not resolve at Phase 0 — the pin binds content by `versionDigest` (PC#9 step 2); publishing the library under GitHub Pages is a repo task, not a build gate.

---

## 5. KL-11 handling

The status total order is a **named constant**, not distributed logic:

```
STATUS_RANK = { confirmed: 3, "time-sensitive": 2, inferred: 1, unverified: 0 }   # ~ KL-11; v1.8 may reorder or flatten
```

- The §7.2 `VALUES` table is *generated* from this constant into every shape and query that needs it, so a v1.8 reordering is a one-line change plus a shape-version bump (§8 discipline).
- The orthogonal-flag alternative (§4 of the runtime spec) is **not** implemented. If the build finds a place where the rank reading and the flag reading would produce different gate outcomes, that place is recorded as a v1.8 input (§9) — this is the most valuable thing Phase 0 can hand v1.8.
- Every `computedStatus` value the fixtures produce carries **~** by inheritance, as the runtime spec §4 requires.

---

## 6. Fixtures

Minimal content graph: Particles (P), Clusters (C), Zones (Z). Structures and above are not needed to exercise recursion (two composite levels suffice); the six-pass bound is asserted structurally, not by fixture. Each fixture is one write set against a stated prior graph state. Expected outcomes are the runtime spec's predictions; a divergence is a **finding**, not a bug to silently fix.

| ID | Prior state | Write set | Expected | Spec ref |
|---|---|---|---|---|
| F-01 | empty | P1: `unverified`, `claimType: claim`, `authoritySource` set | Accept; no report entries | §3.2 |
| F-02 | empty | P2: `confirmed`, no `verificationRecord` | **Reject** `E-CONFIRMED-NO-RECORD` | §3.2, §5.2 step 2 |
| F-03 | empty | P3: `time-sensitive`, no `temporalValidity` | **Reject** `E-TIMESENSITIVE-NO-VALIDITY` | §3.2 |
| F-04 | empty | P4: `epistemicStatus: "verified"` | **Reject** `E-STATUS-VOCAB` | §3.2 |
| F-05a | P1 (`unverified`) | P1 → `confirmed`, no new record | **Reject** `E-UPGRADE-WITHOUT-VERIFICATION` | §5.2 step 3 |
| F-05b | P1 (`unverified`) | P1 → `confirmed` + `verificationRecord{primary-source-read, verifiedAt ≥ prior, evidenceRef}` | Accept | §5.2 step 3, §3.3 |
| F-05c | P1 (`confirmed`) | P1 → `inferred`, no record | Accept (downgrade never needs a record) | §5.2 step 3 |
| F-06 | P5 `inferred`, P6 `unverified` | P7: `inferred`, `derivationRecord{derivedFrom: [P5, P6]}` | **Reject** `E-DERIVATION-EXCEEDS-INPUT` (rank 1 > min 0) | §5.2 step 4 |
| F-06b | same | P7: `unverified`, same derivation record | Accept | §5.2 step 4 |
| F-07 | store v-A with `versionDigest` hand-edited | any write | **Reject** `E-STORE-INVALID` before any shape runs | §2.3, §5.2 step 1 |
| F-08 | P8 `confirmed`+record, P9 `time-sensitive`+validity, P10 `inferred`+derivation | C1: members [P8, P9, P10], declared `inferred` | Accept; `computedStatus(C1) = inferred`; witness = P10 | §7.1, PC#9 `tcfComputedStatusWitness` |
| F-09 | F-08 state, C1 declared `confirmed` | P10 unchanged; write touches P8 only | Accept the write; C1 annotated `statusStale: true`; `sh:Violation` in C1's report from Family C | §5.2 step 6, §3.4 |
| F-10 | P11 with **no** `epistemicStatus` (Family B would reject it — so inject via store bypass to simulate corruption) | C2: members [P11, P8] | `computedStatus(C2)` **absent**; no default; recorded as finding if the engine inserts one | §7.3 "silence" |
| F-11 | P12 `unverified` | P12 body contains an R-1 term matching the illustrative Family A shape | Accept; report entry `constraintClass: terminology`, `sh:Violation`, non-rejecting | §5.2 step 7, §3.1 |
| F-12 | F-08 state | Z1: members [C1, C3] where C3 = [P8] | `computedStatus(C3) = confirmed`, `computedStatus(Z1) = inferred` — bottom-up recursion through two levels | §7.1, §7.3 tier ordering |
| F-13 | P8 (Quark `register: plain`), P9 (`governed-internal`) | C4: members [P8, P9] | `computedRegister(C4) = governed-internal`; **no** rejection, **no** blocking entry | §7.4, KL-4 |
| F-14 | store v-A pinned on C1's `shapeVersion`; store v-B loaded | write to C1 | Gate validates against v-A (the node's pin), not v-B | §5.2 step 1, §5.3 last bullet |
| F-15 *(optional)* | F-08 state | pure call `evidenceDecay(C1)` | `inferred` → author-declared or absent; then re-run with C1 = [P8, P9] → `min(validUntil)` | §7.5 |

**Fixture authoring rule.** Fixtures are JSON-LD using the Phase 0 `context` from the store; the same files are the first content of a future `tcf/fixtures/` directory. No fixture may be edited to make it pass. If the spec's prediction is wrong, the fixture stays and the finding is logged.

---

## 7. Build sequence

| Step | Task | Done when |
|---|---|---|
| B-0 | Pin engine; run Family C against a hand-built F-09 graph outside the gate | `sh:sparql` violation observed → RL-6 closes with a real run. Failure halts the session. |
| B-1 | C-1 store loader + canonicalization behind a **store adapter interface** (`load(storeRef) → StoreDocument`, `commit(change)`); file adapter is the only Phase 0 implementation; hand-author store v-A and v-B | F-07 rejects; v-A and v-B load with distinct digests; no gate code imports the file adapter directly |
| B-2 | C-2 shape library from runtime spec §3 verbatim (Family B, record shapes, Family C with generated `VALUES`, one Family A shape); admission check | Library loads at v-A; a Family A shape lacking `tcf:quarkId` is refused |
| B-3 | C-3 gate steps 1–4 + step 8 | F-01 through F-07 produce expected outcomes |
| B-4 | C-4 propagation + C-3 steps 5–6 | F-08, F-09, F-10, F-12, F-13 |
| B-5 | C-5 reports + C-3 step 7 | F-11; every node touched carries a report digest |
| B-6 | C-6 runner; results table; one timed run of §7.3 on F-12 | Full table green or every red row logged as a finding |
| B-7 | Build record + findings table (§9) + ledger delta (§11); files placed per D-1. Build record MUST carry the line: *"Library includes `tcf:q/register/grant-requirement` per PC#9 v0.2.3 change-log item D; runtime spec v0.1 text does not yet reflect this; queued to runtime v0.2. Vocabulary base is `…/tcf-runtime/vocab/tcf#` per plan v0.1.2; runtime spec §0 still states the `seam-stack` base; queued to runtime v0.2 with RL-1."* | Handoff written |

Estimated: two to three sessions if B-0 passes on the first try.

---

## 8. Exit criteria

Phase 0 is **complete** when all of the following hold:

1. All six `E-*` codes in runtime spec §5.4 are reached by at least one fixture in a real run.
2. F-01 through F-14 produce their expected outcomes, **or** each divergence is logged as a finding with the fixture unmodified.
3. The engine is pinned with version and lockfile digest in the build record.
4. `STATUS_RANK` is the only place the order appears in source; all `VALUES` tables are generated from it.
5. `tcfQuarkViolations` filter (C-5) exists and returns the §6 shape for F-11's graph at `minimumTcfTier: particle` (blocking = 1) and `cluster` (blocking = 0, recorded = 1). It is not wired to anything.
6. The build record states what "functional" now means and what it does not.

Phase 0 is **halted** if B-0 fails, or if any Family B rule cannot be expressed in the pinned engine without semantic change. Halt is a finding, not a failure.

---

## 9. Findings capture → v1.8 inputs

Every divergence between the runtime spec's prediction and the gate's behavior is logged in a single table in the build record:

```
| BF-n | fixture | spec says | gate did | cause (spec gap / engine limit / build error) | disposition (→ v1.8 / → runtime v0.1.1 / → fix in build) |
```

Expected classes of finding, pre-registered so they are recognized when they appear:
- **Order-sensitivity** — any gate outcome that flips between the rank reading and the orthogonal-flag reading of `time-sensitive` (KL-11 evidence, the highest-value finding).
- **Field-name friction** — any (c) binding that the engine or JSON-LD context handles awkwardly (RL-1 evidence for Section B).
- **`confidence_level` pressure** — any fixture where a numeric level would have changed a decision (RL-3 evidence).
- **Record-shape gaps** — a verification or derivation record the fixtures needed that §3.3 does not describe (v1.8 queue item 4).
- **Canonicalization** — if digest stability required choices §2.3 does not make.
- **Companion v0.1.1** — anything the register-requirement Quark record needed that PC#9's change log did not specify.

Findings that are build errors get fixed and are not carried. Everything else carries with its disposition.

---

## 10. Operator decisions — decided 2026-09-10

| ID | Decision | Ruling |
|---|---|---|
| D-1 | Placement | **New standalone repo `tcf-runtime`.** Scope: everything that makes the TCF executable — Quark store and adapters, shape library, gates (write-time now; PC#9-side reader later), fixtures, and the future v1.8 self-conformance suite. Excluded by design: the framework text (canonical on jediwright.com, amended by session) and the product suite (separate lifecycle, own home when real). README first line: *implements the Tiered Content Framework published at jediwright.com; not its canonical text.* |
| D-2 | Language | **Python (pyshacl) accepted** — not as a Phase 0 concession but on the operator's positioning: the TCF is platform/framework-agnostic code-wise; local-first (Automerge, the PC#8 harness, Selvage) is the first pairing, not the substrate the gate assumes. Consequence carried into B-1: adapter interface from the start. |
| D-3 | Substrate stub | **Plain-file store for Phase 0**, behind the B-1 adapter interface. Automerge becomes a second adapter at Phase 1, not a rewrite. RL-5 unchanged. |
| D-4 | Companion v0.1.1 | **Build absorbs it.** The `tcf:q/register/grant-requirement` Quark record enters the library as a build choice; the runtime spec text is not patched now; the amendment folds into runtime v0.2 with the RL-1 binding delta. Record hygiene is the B-7 build-record line. |

**Repo layout (`tcf-runtime`):**

```
tcf-runtime/
  README.md              — scope line above; what is and is not here
  spec/                  — tcf-runtime-spec-v0-1_2026-08-24.md; this plan; later v0.2
  runtime/
    store/               — StoreDocument model, canonicalization, digest; adapters/ (file/; later automerge/)
    shapes/              — Turtle by version IRI; STATUS_RANK constant + VALUES generator
  docs/vocab/tcf/        — GitHub Pages target for the published library versions (not a build gate)
    gate/                — write-time gate (§5); propagation (§7); reports (§6)
  fixtures/              — F-01…F-15 as JSON-LD + expected outcomes
  records/               — build records, findings tables, handoffs
  conformance/           — reserved; empty until the v1.8 self-conformance program opens
```

## 11. Ledger delta proposed (operator appends; verify tail by direct read first)

```
LEDGER DELTA — 2026-09-10 / TCF gate Phase 0 build plan
─────────────────────────────────────────
claim_id:          SL-<next free; expected SL-0227 — VERIFY, do not assume>
date:              2026-09-10
source_session:    TCF runtime Phase 0 planning (Session Harness v0.2, Lightweight Mode);
                   tcf-runtime-phase0-build-plan-v0-1-1_2026-09-10.md
mode:              1
register:          CONTEXTUAL
question_type:     METHOD
verdict_as_issued: Build-first sequencing adopted for the TCF write-time gate:
                   Phase 0 builds runtime spec §2, §3 (B, C, one A), §5, §6, §7
                   on fixtures with a pinned SHACL-SPARQL engine, ahead of the
                   TCF v1.8 session; v1.8 inherits the build findings (§9).
                   Inverts 2026-08-24 handoff step 6 for the write-time gate
                   only; PC#9 crossing gate stays behind its own program.
                   KL-11 order carried as a single named constant (~), not
                   ruled. Assumption (g) resolution assigned to B-0 with a
                   named engine (pyshacl, ~) and a halt condition.
confidence:        ✓ on the sequencing decision (operator); ~ on engine pin
                   (working knowledge, not primary-source read); ~ on D-1–D-4
                   recommendations (unratified); ? on ledger tail (not read)
validation_event:  Phase 0 build session B-0 (engine); B-6 results table
                   (spec predictions); TCF v1.8 session (findings uptake)
survived:          OPEN
stamps_carried:    ⚑ SINGLE-CONTEXT — NOT PANELED
notes:             D-1–D-4 decided 2026-09-10: new repo tcf-runtime; Python;
                   file-store adapter; companion v0.1.1 absorbed by build.
                   Runtime spec v0.1 to be placed at tcf-runtime/spec/ on repo
                   creation. TCF positioned as platform-agnostic; local-first
                   is the first pairing (operator).
─────────────────────────────────────────
```

---

## 12. Phase 0 build session

```
Session scope, in order:

1. B-0: install and pin the engine; run Family C against a hand-built F-09
   graph; confirm the sh:sparql violation fires. If it does not, halt and
   write the finding — do not substitute an engine without a decision.
2. B-1 through B-5 per plan §7, fixtures per plan §6 verbatim. No fixture
   is edited to pass. Every divergence goes in the BF-n findings table.
3. B-6: results table and one timed §7.3 run on F-12.
4. B-7: build record (engine pin, lockfile digest, tcfShapeVersion IRI,
   findings table with dispositions), ledger delta(s), handoff.

Constraints: STATUS_RANK is the only place the status order appears in
source. No new E-* codes. No changes to the runtime spec text this session
(queue to v0.1.1 / v0.2). Delivery-not-application: code and fixtures are
delivered under the §10 layout for operator placement. Store access goes
through the adapter interface only.

Success: plan §8 exit criteria 1–6 met, or a halt with the finding stated.
```

---

## Appendix — Change Log

### v0.1.1 → v0.1.2 (2026-09-10, same day)

| Item | Change |
|---|---|
| Vocabulary namespace | The Phase 0 library IRI inherited the runtime spec §0 base (`…/seam-stack/vocab/tcf#`), contradicting D-1. **Corrected:** base `https://jediwright.github.io/tcf-runtime/vocab/tcf#`; Phase 0 library `https://jediwright.github.io/tcf-runtime/vocab/tcf/2026-09-<build-date>`. GitHub Pages under `tcf-runtime` is the home (operator). Pin binds content, not location (PC#9 step 2), so resolution is not a Phase 0 precondition. Runtime spec §0 base change queued to v0.2 with RL-1. §0, §4, B-7, §10 layout updated. |

### v0.1 → v0.1.1 (2026-09-10, same day)

| Item | Change |
|---|---|
| D-1 placement | **Decided.** New standalone repo `tcf-runtime` replaces `seam-stack/tcf/`. §10 rewritten; §1, §11, §12 updated. |
| D-2 language | **Decided.** Python accepted. Operator rationale recorded: the TCF is platform/framework-agnostic code-wise; local-first is the first pairing, not the substrate. §4 and B-1 updated. |
| D-3 substrate stub | **Decided.** Plain-file store for Phase 0; store sits behind an adapter interface from B-1 (new). |
| D-4 companion v0.1.1 | **Decided.** Build absorbs the queued Quark record; B-7 build-record line added. |
| File name | Renamed `tcf-gate-…` → `tcf-runtime-…` to match the repo. |

---

*Companion to TCF Runtime Spec v0.1 and PC#9 v0.3. Not a TCF amendment. AI-collaborative drafting, human authorial responsibility, intellectual direction held by the named author.*

*⚑ SINGLE-CONTEXT — NOT PANELED. Engine pin ~. Ledger tail unverified this session. D-1–D-4 decided. Delivery-not-application enforced.*

*Session Harness v0.2 · Lightweight Mode · CONTEXTUAL · UX Minds, LLC · J. Wright · September 10, 2026*
