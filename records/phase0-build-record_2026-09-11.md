**Status:** Phase 0 build record — TCF runtime (Session Harness v0.2, Lightweight Mode); single-context; implements `spec/tcf-runtime-spec-v0-1_2026-08-24.md` per `spec/tcf-runtime-phase0-build-plan-v0-1-2_2026-09-10.md`; **not a TCF amendment; not a runtime spec amendment** (deviations queued)

⚑ SINGLE-CONTEXT — NOT PANELED
All `tcf:` field names remain (c) per runtime spec RL-1. Every `computedStatus` value produced by the fixtures carries **~** by inheritance (runtime spec §4, KL-11 unruled).

---

# TCF Runtime — Phase 0 Build Record

## Executed 2026-09-11 · J. Wright (operator, terminal) · Claude Fable 5.1 (build, single context)

---

## 0. Outcome

**Phase 0 is complete.** Plan §8 exit criteria 1–6 are met; criterion 1 is met with the D-6a ratification stated in §5 below. No halt condition fired. B-0 passed on the first real run.

**What "functional" now means.** The write-time gate loads a pinned, content-addressed shape library through a store adapter interface; refuses a store whose `versionDigest` does not match its contents before any shape runs; validates a write set against Family B and the §3.3 record shapes; enforces the upgrade rule (§5.2 step 3) and the derivation rule (step 4); recomputes weakest-status and most-restrictive-register propagation bottom-up through two composite levels; annotates stale ancestors from Family C without rejecting the write; records Family A violations without rejecting the write; content-addresses a per-node validation report and writes its digest to the node; commits the write set plus computed fields plus reports as one change through the adapter. Every refusal path in §5.4 is reached by at least one fixture from a real run on the operator's machine.

**What it is not.** Not a PC#9 crossing gate — `tcfQuarkViolations` (§6) exists and returns the §6 shape but is wired to nothing. Not Automerge-integrated — one adapter, plain files. Not a shape library — one illustrative Family A shape. Not a generality claim — one engine, one language, one fixture set, one machine. Not a performance claim — one measurement, informational. Not a ruling on KL-11 — no fixture surfaced a case where the rank and orthogonal-flag readings diverge (§6 below).

---

## 1. State at open (verified)

| Item | Value | Method | Tag |
|---|---|---|---|
| Repo | `github.com/jediwright/tcf-runtime`, HEAD `aec2bc7` (main) | operator `git rev-parse` | ✓ |
| Runtime spec | `spec/tcf-runtime-spec-v0-1_2026-08-24.md` sha256 `67af6e41…` | operator `shasum`; matches stated | ✓ |
| Build plan | `spec/tcf-runtime-phase0-build-plan-v0-1-2_2026-09-10.md` sha256 `4a482d12…` | operator `shasum`; matches stated; **repo copy governs** | ✓ |
| OI-1 | The plan copy uploaded to the build context (`2c070800…`) differed from HEAD only in §12: heading wording and a three-line output-format-confirmation paragraph absent from HEAD. §6–§8 identical. | operator `diff` | ✓ |
| Operator decisions | D-1–D-4 decided per plan §10 | operator statement | ✓ |
| Survival Ledger tail | not read this session; plan §11 delta not yet appended | operator statement | ? |
| PC#9 v0.3 | read for the `tcf:q/register/grant-requirement` record shape and witness field only | file read | ✓ |

## 2. Engine pin (exit criterion 3)

| Field | Value |
|---|---|
| Engine | **pyshacl 0.40.1** on **rdflib 7.6.0** |
| Runtime | Python 3.9.6 (macOS system Python; venv at `.venv/`) |
| Lockfile | `requirements.lock`, sha256 **`3027f99001993a0e4c401d928ac0f8b177354cce81d4d4d144e819bbcda9b091`** |
| B-0 | `records/b0/b0_probe.py` — `sh:sparql` violation from `SPARQLConstraintComponent` fired on `tcf:C1` for hand-built F-09; negative control conforms. **RL-6 closes on a real run.** Engine pin ~ → ✓. |
| `tcfShapeVersion` (v-A) | `https://jediwright.github.io/tcf-runtime/vocab/tcf/2026-09-11` — `versionDigest` `sha256:68b0836422a2b41956ddba38e1d876c090276ea7b40fd11bc733fb7aab05eec9` |
| `tcfShapeVersion` (v-B) | `https://jediwright.github.io/tcf-runtime/vocab/tcf/2026-09-11-b` — `sha256:69f93c9ac26729a21a5c919f31d94289397dbbbbac63f040ad05eeca60f6eece` |
| Namespace base | `https://jediwright.github.io/tcf-runtime/vocab/tcf#` (plan v0.1.2) |

Digests reproduced byte-for-byte on the operator's machine and in the build sandbox (BC-1 below holds with no finding).

**Mandated line (plan §7 B-7):** Library includes `tcf:q/register/grant-requirement` per PC#9 v0.2.3 change-log item D; runtime spec v0.1 text does not yet reflect this; queued to runtime v0.2. Vocabulary base is `…/tcf-runtime/vocab/tcf#` per plan v0.1.2; runtime spec §0 still states the `seam-stack` base; queued to runtime v0.2 with RL-1.

## 3. What was built (plan §2 → repo)

| Component | Location | Notes |
|---|---|---|
| C-1 store loader + canonicalization | `runtime/store/model.py` | `StoreDocument`, `compute_digest` over canonical JSON of `{quarks, shapes, context}`; `StoreInvalid` = `E-STORE-INVALID`. **BC-1:** canonicalization is sorted-key, whitespace-free, UTF-8 JSON — JCS-equivalent for the value types present (no floats, no non-ASCII escaping issues). Recorded as a build choice; §2.3's "or equivalent" wording left it open. |
| Store adapter interface | `runtime/store/adapter.py` | `load(store_ref) → StoreDocument` (unverified — verification is gate step 1), `current_version()`, `commit(change)`. The gate imports only this module (checked by `tools/check_b1_b2.py`). |
| File adapter (D-3) | `runtime/store/adapters/file.py` | Directory of store JSON, resolved by `tcfShapeVersion` IRI; commits appended to `commits.jsonl`. Only Phase 0 implementation. |
| C-2 shape library | `runtime/shapes/library.py` | Spec §3 verbatim with BF-1 escaping and BF-2 rank form; Quark records incl. companion v0.1.1; JSON-LD context; admission check (targeted NodeShape without `tcf:quarkId`/`tcf:constraintClass` refused). Stores sealed by `tools/seal_store.py` (author-side; never called by the gate). |
| `STATUS_RANK` | `runtime/shapes/status_rank.py` | Sole source of the status order; generates the §7.2 `VALUES` table (§7.3) and the `IF()` rank expression (Family C). `REGISTER_RANK` (§7.4 lattice) is co-located in the same file as a distinct ordering, disclosed here. |
| C-3 gate | `runtime/gate/gate.py` | `Gate.gate(graph, write_set) → Accept \| Reject`; §5.2 steps 1–8 in order; error vocabulary exactly §5.4; a refusal with no code surfaces as `Reject(code=None)` (never reached by any fixture). Step 8 = in-memory commit + JSON-patch-style ops through the adapter. |
| C-4 propagation | `runtime/gate/propagation.py` | §7.3 `CONSTRUCT` run per composite tier in order (six-pass bound structural); §7.4 register; §7.5 `evidenceDecay` pure function. D-6b guard applied (BF-6). |
| C-5 reports | `runtime/gate/reports.py` | Per-node `sh:ValidationReport` as sorted JSON, content-addressed; `tcf:validationReport` = digest; `tcf_quark_violations(root, minimumTcfTier)` implements the §6 filter — **unwired**. |
| C-6 runner | `tools/run_fixtures.py` | Loads `fixtures/F-*.json`, runs the gate, asserts expectations, prints the table, writes `records/fixture-results.json`. Exit 0 iff every row is green or a logged finding. |
| Fixtures | `fixtures/F-*.json`, `fixtures/stores/` | Authored by `tools/author_fixtures.py` from plan §6 verbatim; JSON-LD against the store context; prior states injected by store bypass. **No fixture was edited to pass.** |

## 4. Results table (operator run, 2026-09-11, store v-A)

| ID | Expected (plan §6) | Gate did | Result |
|---|---|---|---|
| F-01 | Accept; no report entries | Accept; 0 violations | GREEN |
| F-02 | `E-CONFIRMED-NO-RECORD` | same | GREEN |
| F-03 | `E-TIMESENSITIVE-NO-VALIDITY` | same | GREEN |
| F-04 | `E-STATUS-VOCAB` | same | GREEN |
| F-05a | `E-UPGRADE-WITHOUT-VERIFICATION` | `E-CONFIRMED-NO-RECORD` (step 2) | **RED — BF-5 logged; fixture unmodified** |
| F-05a-supp | `E-UPGRADE-WITHOUT-VERIFICATION` | same | GREEN (supplementary, D-6a) |
| F-05b | Accept | Accept | GREEN |
| F-05c | Accept (downgrade needs no record) | Accept | GREEN |
| F-06 | `E-DERIVATION-EXCEEDS-INPUT` | same | GREEN |
| F-06b | Accept | Accept | GREEN |
| F-07 | `E-STORE-INVALID` before any shape runs | same; `shapesRan=False` | GREEN |
| F-08 | Accept; `computedStatus(C1)=inferred`; witness P10 | same | GREEN |
| F-09 | Accept; C1 `statusStale`; Family C violation in C1 report | same | GREEN |
| F-10 | `computedStatus(C2)` absent, no default | absent (with D-6b guard; `unverified` without it — BF-6) | GREEN |
| F-11 | Accept; terminology `sh:Violation` recorded; blocking=1 @particle, 0/1 @cluster | same | GREEN |
| F-12 | `C3=confirmed`, `Z1=inferred`, two levels | same; **§7.3 timed: 52.99 ms** (operator machine; informational, RL-7) | GREEN |
| F-13 | `computedRegister(C4)=governed-internal`; no rejection; no blocking entry | same | GREEN |
| F-14 | gate validates C1 against v-A pin while store exposes v-B | v-A used | GREEN |
| F-15 (opt.) | `evidenceDecay` absent; then `min(validUntil)` | `None`; then `2026-12-31` | GREEN |

§5.4 codes reached: 6/6 (`E-UPGRADE-WITHOUT-VERIFICATION` via F-05a-supp only — see D-6a).

## 5. Findings table (plan §9) → v1.8 / runtime v0.2 inputs

| BF | Fixture | Spec says | Gate did | Cause | Disposition |
|---|---|---|---|---|---|
| BF-1 | B-0 | §3.1/3.2/3.4 Turtle uses `tcf:sh/…`, `tcf:q/…` as prefixed names | rdflib rejects: `/` in a Turtle local name must be `\/` | spec gap (serialization; field-name friction, RL-1 class) | fix in build (escape; IRIs unchanged) · note → runtime v0.2 |
| BF-2 | B-0 | §7.2: "inline this `VALUES` block wherever §3.4 shows `tcf:rank(…)`" | pyshacl refuses: W3C SHACL §5.3.2 forbids `VALUES` inside `sh:select` — not an engine limit; no conforming engine can run §3.4 as written | spec gap | **D-5a (operator, 2026-09-11):** nested `IF()` generated from `STATUS_RANK` inside `sh:select`; `VALUES` retained for §7.3 (plain SPARQL); identical semantics · → runtime v0.2 |
| BF-3 | F-01 | Family B accepts a valid Particle | pyshacl 0.40.1 `focus_nodes=` mis-evaluates `sh:or` branches containing `sh:not`/`sh:hasValue` (standalone validation conforms) | engine limit | fix in build (validate full candidate graph, filter results by focus node) · Phase 1 note before relying on `focus_nodes` |
| BF-4 | F-05b | §5.2 step 3: `verifiedAt` ≥ "the previous status timestamp" | §2.4 defines no such field | record-shape gap (v1.8 queue item 4) | **rides as build choice (operator, 2026-09-11):** prior `verificationRecord.verifiedAt` when present, else no lower bound. This is the one place the build chose leniency over refusal. **Called out for v1.8 review.** |
| BF-5 | F-05a | Reject `E-UPGRADE-WITHOUT-VERIFICATION` | Reject `E-CONFIRMED-NO-RECORD` at step 2 | spec: §5.2 step order — Family B (step 2) rejects `confirmed`-without-record before step 3 runs; plan §6 prediction inconsistent with §5.2 ordering | fixture unmodified; **D-6a (operator):** supplementary `F-05a-supp` (unverified → inferred, no record) counts toward §8.1 · → runtime v0.2 (either re-sequence or restate F-05a's prediction) |
| BF-6 | F-10 | §7.3: a statusless member yields no `COALESCE` binding and `computedStatus` is **absent** | `computedStatus = unverified`: under standard SPARQL semantics an unbound `?status` is join-compatible with every `VALUES` row, so a statusless member contributes rank 0 — the query inserts the weakest status; the spec's claim about its own query is false (fail-closed by accident, but a default) | spec gap (pre-registered class: engine inserts a default) | **D-6b(a) (operator):** `FILTER(BOUND(?status))` + `FILTER NOT EXISTS { member without status }` guard applied in build; F-10 green under guard · → runtime v0.2 (§7.3 text) |

Build errors fixed and not carried: fixture runner defaulted to the lexically-last store version (v-B) instead of v-A — runner now pins v-A unless the fixture says otherwise (F-14); report entries on nested property shapes lost `tcf:quarkId`/`tcf:constraintClass` — report builder now walks up to the enclosing NodeShape.

## 6. KL-11 evidence (plan §5)

No fixture produced a gate outcome that would differ between the rank reading (`time-sensitive` = 2) and the orthogonal-flag reading. This is stated explicitly so silence is not read as a ruling. F-15's second run (C1 = [P8 confirmed, P9 time-sensitive] → `time-sensitive` → `min(validUntil)`) is the closest the fixtures come: under a flag reading C1 would be `confirmed` + `timeSensitive: true` and `evidenceDecay` would take the `confirmed` branch (`min(recencyWindowEnd)`) — a different date source. Whether that is a *gate outcome* difference depends on v1.8's reading of §7.5; it is a candidate, not a finding.

## 7. Exit criteria (plan §8)

| # | Criterion | Status |
|---|---|---|
| 1 | All six `E-*` codes reached by at least one fixture in a real run | **Met** — 5/6 by plan fixtures; `E-UPGRADE-WITHOUT-VERIFICATION` by F-05a-supp (D-6a ratified). Stated plainly: met by the extended set. |
| 2 | F-01–F-14 expected outcomes, or each divergence logged with fixture unmodified | **Met** — 17 as expected; F-05a divergence logged (BF-5); F-10 as expected under D-6b guard (BF-6 logged) |
| 3 | Engine pinned with version and lockfile digest | **Met** — §2 |
| 4 | `STATUS_RANK` sole source; all `VALUES` tables generated from it | **Met** — checked by `tools/check_b1_b2.py` |
| 5 | `tcfQuarkViolations` filter exists; F-11 @particle blocking=1; @cluster blocking=0, recorded=1; wired to nothing | **Met** — F-11 asserts both; no gate step calls it |
| 6 | Build record states what "functional" means and does not | **Met** — §0 |

## 8. Operator decisions this session

| ID | Decision | Ruling (2026-09-11) |
|---|---|---|
| D-5 | Family C rank form (BF-2) | **(a)** `IF()` expression as build-level expression of §3.4; §7.2 correction queued to runtime v0.2 |
| D-6a | Supplementary fixture F-05a-supp counts toward §8.1 | **Yes** |
| D-6b | §7.3 silence guard | **(a)** applied in build; §7.3 text correction queued to runtime v0.2 |
| BF-4 | Timestamp-source leniency | **Rides** with disclaimer; v1.8 review required |

## 9. Open items carried

- OI-1: uploaded plan copy vs HEAD §12 delta (housekeeping; no build effect).
- Runtime v0.2 queue: §0 namespace base (RL-1); BF-1 Turtle escaping; BF-2 §7.2 form; BF-5 step order vs F-05a prediction; BF-6 §7.3 guard; companion v0.1.1 record (D-4).
- v1.8 queue: BF-4 timestamp source; KL-11 candidate from §6 above; RL-3 `confidence_level` — no fixture where a numeric level would have changed a decision (no pressure observed).
- Phase 1: BF-3 `focus_nodes` engine limit; GitHub Pages publication of `docs/vocab/tcf/` (not a gate); Automerge adapter.
- Survival Ledger: plan §11 delta and this session's deltas (below) not yet appended; tail unverified.

---

*Companion to TCF Runtime Spec v0.1 and Phase 0 Build Plan v0.1.2. Not a TCF amendment. AI-collaborative build, human authorial responsibility, intellectual direction held by the named author.*

*⚑ SINGLE-CONTEXT — NOT PANELED. Engine pin ✓ (real run). Ledger tail unverified. D-5, D-6a, D-6b ruled. Delivery-not-application enforced.*

*Session Harness v0.2 · Lightweight Mode · CONTEXTUAL · UX Minds, LLC · J. Wright · September 11, 2026*

**Post-commit note (2026-09-11):** the B-7 delivery zip shipped a `README.md` and `.gitignore` without checking for existing files; both were overwritten on unzip and restored from git with the new content appended (insertions only, nothing lost). Build error, fixed, not carried — recorded because delivery-not-application means the operator's files are the operator's.
