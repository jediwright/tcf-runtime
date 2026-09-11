**Status:** v0.2 — **ISSUED 2026-09-11** (Session Harness v0.2, Mode 3 Counter-Pass, it.1–it.3, **converged with narrowing** at it.3; validation event passed at `tcf-runtime fa7fded`); companion to PC#9 v0.3; supersedes `tcf-runtime-spec-v0-1_2026-08-24.md` (sha256 `67af6e41…`); **not a TCF amendment**

**Counter-Pass converged (it.3, 2026-09-11)** — siloed critic, three iterations; narrowed claims: §7.3 silence (precondition stated, CP-2.1/2.2), §3.4 IF()/VALUES identity (RDF 1.1 term equality, CP-3.3). Records: `records/counter-pass-*-tcf-runtime-v0-2_2026-09-11.md`.
All field names marked (c) are TCF v1.7 *candidate* names, unconfirmed, carried here as bindings pending TCF v1.8 Section B. This document proposes no change to the TCF; where it needs something the TCF has not ruled, it says so and queues it. Every `computedStatus` value carries **~** by inheritance (§4, KL-11 unruled).

**What v0.2 changes and does not.** v0.2 corrects the v0.1 text where the Phase 0 build (`records/phase0-build-record_2026-09-11.md`) showed it does not execute as written — BF-1, BF-2, BF-5, BF-6 — and absorbs two queued deltas: the namespace base (plan v0.1.2, RL-1) and the companion v0.1.1 record (PC#9 v0.2.3 item D; D-4). The build code in `runtime/` is the reference implementation of the intended semantics; the text moves to match it. No locked rule is weakened, no default is introduced, computed stays computed. §4 (KL-11), §7.5, RL-3, and the BF-4 timestamp leniency are **untouched** — they belong to TCF v1.8. Change log in §12.

---

# TCF Runtime Specification v0.2

## What the gate mechanism makes possible: a Quark store, per-tier shapes, a write-time epistemic gate, and a computed propagation rule

---

## 0. Position and posture

The TCF v1.7 Amendment locks the *architecture* of epistemic status: four values (Confirmed / Inferred / Unverified / Time-sensitive), governed at the Quark level, declared at the Particle level, inherited upward by weakest-status, upgradable only by a verification action with a record attached. It stubs the *implementation*: field names, controlled vocabularies, the SHACL shape, the JSON-LD mappings, and the formal propagation constraint — all queued to a dedicated specification pass.

PC#9 needs the implementation to exist as a runtime, because its gate reads it. This document specifies that runtime **on the locked architecture only**, binding to the candidate field names provisionally and marking every binding as such. It is the "practice precedes framework" move: the runtime is built to what v1.7 locks, and the TCF v1.8 session inherits a worked runtime instead of a blank stub.

**What this document is not.** Not an amendment to TCF v1.7. Not a promotion of any PROPOSED Lexicon term. Not the per-tier shape *library* (that is authored after v1.8 rules the field names). Not a generality claim: one reference substrate (Automerge document store, PC#8 harness) and one reference surface class.

**Namespaces.** `tcf:` = `https://jediwright.github.io/tcf-runtime/vocab/tcf#` (proposed; home is the `tcf-runtime` repo per plan v0.1.2 / D-1, published under `docs/vocab/tcf/` when Phase 1 lands GitHub Pages — publication is not a gate; a PC#9 pin binds content, not location). Library versions are `…/tcf-runtime/vocab/tcf/<date>` (Phase 0: `…/2026-09-11`, digest `sha256:68b08364…`). `seam:` = existing Seam Stack vocabulary; the `seam-stack` base named in v0.1 is **retired** for `tcf:` terms. `sh:` = SHACL. All `tcf:` IRIs in this document are (c) until v1.8; the base change is a binding delta under RL-1, not a field-name ruling.

---

## 1. Runtime overview

Four components; two gates; one shape library.

```
  ┌──────────────────────── author's local-first substrate ────────────────────────┐
  │                                                                                │
  │   Quark Store (§2)  ──pins──▶  Shape Library @ tcfShapeVersion (§3)            │
  │        │                              │                                        │
  │        │  every write                 │ validates                              │
  │        ▼                              ▼                                        │
  │   Content Graph  ◀──── Write-Time Epistemic Gate (§5) ── rejects / annotates   │
  │   (Particles → Clusters → Zones → Structures …)                                │
  │        │                                                                       │
  │        │  Propagation (§7) — computed, not declared                            │
  │        ▼                                                                       │
  │   Submission ──▶  PC#9 Crossing Gate (reads §6 report, §7 computed status)     │
  └────────────────────────────────────────┬───────────────────────────────────────┘
                                           ▼
                                   externally legible surface
```

- **The write-time gate** fires on every write to a Quark-governed node. It enforces the v1.7 inheritance rule at introduction (the Propagation Discipline: verify at introduction, not in batch at the end).
- **The PC#9 crossing gate** fires once at submission. It does not re-validate; it *reads* the store's current validation report and computed status.

Two gates, two events, one shape library, one pinned version.

---

## 2. The Quark store

### 2.1 What it is

A versioned, content-addressed collection of Quark records. A Quark record is a constraint, not content: an approved-terminology list, a character limit, a tone parameter, a metadata schema definition, an accessibility threshold, a brand-voice primitive, a prompt-engineering constraint, or an epistemic-status rule (all Quark-level object classes per TCF v1.6). The store is the machine form of "governed at the Quark level."

### 2.2 Where it lives

On the author's substrate, as a **read-mostly Automerge document** (`tcf-quark-store`) replicated to the author's capability-governed peers. Writes to the store are themselves GSEF changeClass events (§8). The store is *not* on the target surface and the target surface is never consulted for it (PC#9 OQ-2/OQ-6 posture).

### 2.3 Store structure

```json
{
  "storeId": "urn:tcf:quark-store:<author-did>",
  "tcfShapeVersion": "https://jediwright.github.io/tcf-runtime/vocab/tcf/2026-09-11",
  "quarks": {
    "<quarkId>": {
      "quarkId": "tcf:q/terminology/plain-register-v1",
      "quarkClass": "terminology | length | tone | metadata | accessibility | brand-voice | prompt | epistemic | register",
      "appliesToTier": ["particle", "cluster"],
      "constraintRef": "urn:tcf:shape:PlainRegisterTerminologyShape",
      "severity": "sh:Violation | sh:Warning | sh:Info",
      "register": "plain | contextual | governed-internal",
      "introducedIn": "<tcfShapeVersion IRI>",
      "supersededBy": null,
      "lineageRef": "<GSEF lineage record recordId, or null>"
    },
    "tcf:q/register/grant-requirement": {
      "quarkId": "tcf:q/register/grant-requirement",
      "quarkClass": "register",
      "appliesToTier": ["particle", "cluster", "zone", "structure", "ecosystem", "biome"],
      "constraintRef": null,
      "evaluated": false,
      "severity": "sh:Warning",
      "register": "governed-internal",
      "introducedIn": "<tcfShapeVersion IRI>",
      "supersededBy": null,
      "lineageRef": null
    }
  },
  "shapes": { "<shape IRI>": "<SHACL Turtle, content-addressed by sha256>" },
  "context": "<JSON-LD context document for this version>",
  "versionDigest": "sha256:<digest over canonical JSON of quarks+shapes+context>"
}
```

**Invariants.**
- `versionDigest` is computed, never declared. A store whose digest does not match its contents is invalid; the write-time gate refuses to load it.
- `tcfShapeVersion` changes if and only if `versionDigest` changes. This is what makes PC#9's `tcfShapeVersion` pin meaningful.
- A Quark is never edited in place. It is superseded (`supersededBy`) by a new Quark in a new version. The prior version remains loadable for grants pinned to it (TCF v1.7 Seam 1 DRAFTED rule, adopted here as a runtime invariant).
- `register` on a Quark is the Quark's own register requirement. It feeds §7.4 (computed most-restrictive register). It is (c) and governs nothing until `tcf:register` is promoted (PC#9 KL-4).
- **Declared-but-not-evaluated Quarks (companion v0.1.1; PC#9 v0.2.3 item D).** A Quark record may carry `"evaluated": false` and `"constraintRef": null`. Such a record contributes **no shape** to the library and is never run by either gate; it exists so that a gate which mints an entry *about* the Quark can read the entry's `severity` from the pinned library instead of a literal. At this shape version there is exactly one: `tcf:q/register/grant-requirement`, `severity: sh:Warning`, read by PC#9 gate step 6 (§6). Its `quarkClass` `register` is a **runtime-only class** added to the enumeration above for this record; it is not one of the TCF v1.6 Quark-level object classes listed in §2.1 and governs nothing until `tcf:register` is promoted (KL-4). Promotion of `tcf:register` flips that severity by shape-version bump (§8), never by editing a gate. `evaluated` is read as `true` when absent. Whether the store loader should *refuse* a record with `constraintRef: null` and `evaluated` absent or `true` is not decided here — the Phase 0 loader does not check it, and v0.2 makes no refusal claim the build does not implement (Phase 1 candidate).

### 2.4 Content-graph node minimum

Every governed node (Particle and above) carries:

```json
{
  "@type": "tcf:Particle | tcf:Cluster | tcf:Zone | tcf:Structure | tcf:Ecosystem | tcf:Biome",
  "tcf:shapeVersion": "<tcfShapeVersion IRI the node was written under>",
  "tcf:epistemicStatus": "confirmed | inferred | unverified | time-sensitive",   // (c) declared
  "tcf:computedStatus":  "<same vocabulary>",                                    // computed, §7 — composite tiers only
  "tcf:aiProvenance":    "<per v0.4.1 vocabulary>",                              // distinct field, per v1.7
  "tcf:members":         ["<node ids>"],                                         // composite tiers only
  "tcf:validationReport": "<sha256 of last §6 report>"
}
```

The epistemic block on a Particle binds to the five v1.7 candidate fields:

| v1.7 candidate (c) | Runtime binding (c) | Type | Req. at Particle | Used by |
|---|---|---|---|---|
| `claim_type` | `tcf:claimType` | controlled: `fact` / `claim` / `opinion` / `policy` | R | §3.2 |
| `authority_source` | `tcf:authoritySource` | IRI or agent id | R | §3.2 |
| `confidence_level` | *folded into* `tcf:epistemicStatus` | — | — | v1.7 treats the four-value status as the confidence surface; a separate numeric level is not locked. Flag for v1.8: keep or drop. |
| `temporal_validity` | `tcf:temporalValidity` | `{ "validFrom": date, "validUntil": date }` | R iff status = `time-sensitive` | §5, §7.5, PC#9 OQ-4 |
| `verification_record` | `tcf:verificationRecord` | object (§3.3) | R iff status = `confirmed` | §3.2, §5 |

---

## 3. SHACL shapes at Quark level — three shape families

The shape library at a given `tcfShapeVersion` contains exactly three families. Per-tier constraint shapes (family A) are *authored after* v1.8; families B and C are specified here in full because they implement what v1.7 already locks.

**Serialization note (BF-1).** Shape and Quark IRIs use `/` inside the local part (`tcf:sh/…`, `tcf:q/…`). In Turtle a `/` in a prefixed local name is a reserved character and MUST be escaped as `\/` (Turtle 1.1 `PN_LOCAL_ESC`); the unescaped forms in v0.1 do not parse on a conforming parser. The Turtle below is written escaped and assumes the three prefixes `sh:`, `xsd:`, `tcf:` from §0, which `library.py` emits as `@prefix` lines at the head of every shape file (`@prefix sh: <http://www.w3.org/ns/shacl#> .` / `@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .` / `@prefix tcf: <https://jediwright.github.io/tcf-runtime/vocab/tcf#> .`); the blocks are not standalone documents without them. The IRIs are unchanged — `tcf:sh\/EpistemicStatusShape` denotes `https://jediwright.github.io/tcf-runtime/vocab/tcf#sh/EpistemicStatusShape` — and JSON `quarkId` strings (compact form, not Turtle) are unaffected. The reference generator is `runtime/shapes/library.py`.

### 3.1 Family A — per-tier constraint shapes (structure specified; instances deferred)

One shape per (Quark, tier) pair, generated from Quark records:

```turtle
tcf:sh\/PlainRegisterTerminologyShape
    a sh:NodeShape ;
    sh:targetClass tcf:Particle, tcf:Cluster ;          # from appliesToTier
    sh:severity sh:Violation ;                          # from quark.severity
    tcf:quarkId tcf:q\/terminology\/plain-register-v1 ;   # back-reference; lets §6 filter by Quark
    tcf:constraintClass "terminology" ;                 # from quarkClass; lets PC#9 gate filter by class
    sh:property [
        sh:path tcf:body ;
        sh:pattern "^(?!.*\\b(substrate|floor|stack)\\b).*$" ;   # illustrative only
        sh:flags "i" ;
        sh:message "R-1 term in plain-register content"
    ] .
```

Every Family A shape MUST carry `tcf:quarkId` and `tcf:constraintClass`. Those two annotations are what make the validation report filterable into PC#9's `tcfQuarkViolations` (§6). A shape without them is not admitted to the library.

### 3.2 Family B — epistemic status shape (Particle-level; implements v1.7 "What is locked")

```turtle
tcf:sh\/EpistemicStatusShape
    a sh:NodeShape ;
    sh:targetClass tcf:Particle ;
    sh:severity sh:Violation ;
    tcf:quarkId tcf:q\/epistemic\/status-v1 ;
    tcf:constraintClass "epistemic" ;

    # exactly one status from the locked vocabulary
    sh:property [
        sh:path tcf:epistemicStatus ;
        sh:minCount 1 ; sh:maxCount 1 ;
        sh:in ( "confirmed" "time-sensitive" "inferred" "unverified" )
    ] ;
    sh:property [ sh:path tcf:claimType ; sh:minCount 1 ; sh:in ( "fact" "claim" "opinion" "policy" ) ] ;
    sh:property [ sh:path tcf:authoritySource ; sh:minCount 1 ] ;

    # v1.7 locked rule: Confirmed requires an attached verification record
    sh:or (
        [ sh:property [ sh:path tcf:epistemicStatus ; sh:not [ sh:hasValue "confirmed" ] ] ]
        [ sh:property [ sh:path tcf:verificationRecord ; sh:minCount 1 ; sh:node tcf:sh\/VerificationRecordShape ] ]
    ) ;

    # Time-sensitive requires temporal validity (PC#9 OQ-4 fail-closed depends on this)
    sh:or (
        [ sh:property [ sh:path tcf:epistemicStatus ; sh:not [ sh:hasValue "time-sensitive" ] ] ]
        [ sh:property [ sh:path tcf:temporalValidity ; sh:minCount 1 ; sh:node tcf:sh\/TemporalValidityShape ] ]
    ) ;

    # AI provenance is a distinct field and never sets status (v1.7 locked)
    sh:property [ sh:path tcf:aiProvenance ; sh:maxCount 1 ] .
```

### 3.3 Verification and derivation record shapes (implements v1.7 stubs at runtime; (c))

```turtle
tcf:sh\/VerificationRecordShape
    a sh:NodeShape ;
    sh:property [ sh:path tcf:verificationMethod ; sh:minCount 1 ;
                  sh:in ( "primary-source-read" "external-attestation" "operator-attestation" "automated-check" ) ] ;
    sh:property [ sh:path tcf:verifiedBy ; sh:minCount 1 ] ;
    sh:property [ sh:path tcf:verifiedAt ; sh:minCount 1 ; sh:datatype xsd:dateTime ] ;
    sh:property [ sh:path tcf:recencyWindowEnd ; sh:minCount 1 ; sh:datatype xsd:dateTime ] ;
    sh:property [ sh:path tcf:verificationEvidenceRef ; sh:minCount 0 ] .   # Evidence-plane pointer; optional

tcf:sh\/DerivationRecordShape        # required on Inferred Particles that were produced by a reasoning step
    a sh:NodeShape ;
    sh:property [ sh:path tcf:derivedFrom ; sh:minCount 1 ; sh:class tcf:Particle ] ;
    sh:property [ sh:path tcf:reasoningStep ; sh:minCount 1 ] ;
    sh:property [ sh:path tcf:confidenceBasis ; sh:minCount 1 ] .

tcf:sh\/TemporalValidityShape
    a sh:NodeShape ;
    sh:property [ sh:path tcf:validFrom ; sh:minCount 1 ; sh:datatype xsd:date ] ;
    sh:property [ sh:path tcf:validUntil ; sh:minCount 1 ; sh:datatype xsd:date ] .
```

`verificationMethod` value `primary-source-read` is the runtime form of the Pre-Draft Primary-Source Gate (PPG, SL-0144 notes). It is the only method under which a `confirmed` status is self-issued by the author; the record must then carry a `verificationEvidenceRef`.

### 3.4 Family C — propagation shape (composite tiers; implements v1.7 "computed rather than declared")

```turtle
tcf:sh\/PropagationShape
    a sh:NodeShape ;
    sh:targetClass tcf:Cluster, tcf:Zone, tcf:Structure, tcf:Ecosystem, tcf:Biome ;
    sh:severity sh:Violation ;
    tcf:quarkId tcf:q\/epistemic\/propagation-v1 ;
    tcf:constraintClass "epistemic" ;

    # a composite must carry a computed status, and it must equal the SPARQL-derived weakest
    sh:property [ sh:path tcf:computedStatus ; sh:minCount 1 ; sh:maxCount 1 ] ;
    sh:sparql [
        sh:message "Declared status exceeds computed weakest-status of members" ;
        sh:select """
            PREFIX tcf: <https://jediwright.github.io/tcf-runtime/vocab/tcf#>
            SELECT $this ?declared ?computed WHERE {
                $this tcf:epistemicStatus ?declared ; tcf:computedStatus ?computed .
                BIND( IF(?declared="confirmed",3,IF(?declared="time-sensitive",2,IF(?declared="inferred",1,IF(?declared="unverified",0,?__unbound)))) AS ?rd )
                BIND( IF(?computed="confirmed",3,IF(?computed="time-sensitive",2,IF(?computed="inferred",1,IF(?computed="unverified",0,?__unbound)))) AS ?rc )
                FILTER( ?rd > ?rc )
            }
        """
    ] .
```

The two `BIND` lines are the §7.2 rank table in its **SHACL-SPARQL form** (BF-2, D-5a): a `VALUES` clause is not permitted inside `sh:select` (W3C SHACL §5.3.2, pre-binding restrictions), so the lookup is a nested `IF()`. A value outside the vocabulary falls through to the never-bound `?__unbound`, leaving `?rd`/`?rc` unbound and the `FILTER` false — the same behaviour an unmatched `VALUES` row would give. The expression is **generated from `STATUS_RANK`** (`runtime/shapes/status_rank.py::rank_expr`), never hand-maintained; the literal above is what the generator emits at this version and is shown so the shape is readable without the code. **Identity is at RDF 1.1 term equality** (CP-3.3): an engine that distinguishes `"confirmed"` from `"confirmed"^^xsd:string` (rdflib 7.6.0 does — `IF()` compares by value, `VALUES` joins by term) makes `IF()` the *stricter* of the two for a composite's declared status — a typed variant is read as in-vocabulary and can be flagged stale — never the weaker; it can neither insert a default nor lift a refusal. Particles cannot carry the typed variant past Family B's `sh:in`. Engine term model is inside RL-6's one-engine residual.

---

## 4. Ordering — the thing TCF v1.7 does not say (KL-11)

The weakest-status rule ("a Cluster's status is the weakest of its Particles' statuses") is only computable over a **total order** on the four values. v1.7 locks the four values and the rule; it does not state the order. Three of the four are unambiguous. `time-sensitive` is not: it is a *temporal* qualifier sitting in a *confidence* vocabulary.

**Proposed order (~, queued to TCF v1.8 as a Quark-level ruling):**

| rank | status | reading |
|---|---|---|
| 3 | `confirmed` | verified, record attached, within recency window |
| 2 | `time-sensitive` | verified-as-of a bounded window; decays by clock, not by evidence |
| 1 | `inferred` | derived; derivation record attached |
| 0 | `unverified` | no verification action |

**Rationale.** `time-sensitive` in v1.7's own definition is a *verified* claim with a validity bound — the amendment's GPRF cousin ("verification tags with evidence decay") is the same object. Ranking it above `inferred` says: a bounded verified claim is stronger than an unbounded derived one. Ranking it below `confirmed` says: the bound is a weakness relative to an open recency window.

**Alternative the v1.8 session should weigh:** treat `time-sensitive` as an orthogonal flag rather than a rank (status ∈ {confirmed, inferred, unverified} × timeSensitive ∈ {true, false}). That is cleaner for computation and worse for the three-way convergence argument (Playbook §10.1), which rests on four *values*. This runtime adopts the rank so the rule computes today; the ranking is an explicit ~ binding, replaceable by shape-version bump.

**Consequence:** until v1.8 rules, `tcf:computedStatus` values in any record carry ~ and the PC#9 intent record's `tcfComputedStatus` inherits that tag.

---

## 5. The write-time epistemic status gate

### 5.1 When it fires

On every write that creates or mutates a node of class `tcf:Particle` or above in the content graph, before the write is committed to the Automerge document. It is a **pre-commit validator on the author's substrate**, not a crossing. It is the runtime form of the Propagation Discipline: the check happens at introduction.

### 5.2 What it does, in order

1. **Load the pinned shape library** at the node's `tcf:shapeVersion` (or, for new nodes, the store's current version). Digest mismatch → refuse to load → write rejected with `E-STORE-INVALID`.
2. **Run Family B** on any Particle in the write set. `sh:Violation` → write rejected. (`confirmed` without verification record; `time-sensitive` without temporal validity; status outside vocabulary.)
3. **Check the upgrade rule** (v1.7 locked): if the write raises a Particle's `tcf:epistemicStatus` rank (§4), the write set MUST include a new or updated `tcf:verificationRecord` with `verifiedAt` ≥ the previous status timestamp. Absent → write rejected with `E-UPGRADE-WITHOUT-VERIFICATION`. A rank *decrease* never requires a record.
   **Step-order consequence (BF-5).** Step 2 runs first, so an upgrade *to `confirmed`* with no record is rejected at step 2 with `E-CONFIRMED-NO-RECORD` — the locked Family B rule fires before the upgrade rule is reached. Step 2 checks both the record's **presence** and its **conformance** to `VerificationRecordShape` (via `sh:node`) — a `confirmed` upgrade carrying a malformed record (e.g. no `verifiedBy`) is also rejected at step 2 with `E-CONFIRMED-NO-RECORD`. `E-UPGRADE-WITHOUT-VERIFICATION` is reachable only when Family B passes: (a) an upgrade to a non-`confirmed` rank with no record (`unverified` → `inferred`; `unverified`/`inferred` → `time-sensitive` with validity but no record); (b) any upgrade whose record is present but fails one of step 3's three checks — `verifiedAt` absent, `verifiedAt` below the prior, or the record neither new nor updated; for a `confirmed` upgrade only the last two apply, since a missing `verifiedAt` is already rejected at step 2 by `VerificationRecordShape` (Family B does not validate the record on a non-`confirmed` Particle; step 3 checks `verifiedAt` and novelty only, never shape conformance). The order is deliberate and stands: Family B enforces the locked rule that `confirmed` carries a well-formed record; step 3 checks that the record is *adequate evidence of an upgrade action* — new or updated, and not earlier than the prior. Plan §6 F-05a's predicted code was therefore wrong as written; the correct prediction for its write set is `E-CONFIRMED-NO-RECORD` (see §12).
4. **Check the derivation rule** (v1.7 locked): a write that produces a Particle from a reasoning step over other Particles MUST attach a `tcf:derivationRecord`, and the new Particle's status rank MUST be ≤ min rank of `tcf:derivedFrom`. Violation → write rejected with `E-DERIVATION-EXCEEDS-INPUT`.
5. **Recompute propagation** (§7) for every composite ancestor of any node in the write set. Write `tcf:computedStatus` on each. This is a *computed write*, performed by the gate, not the author.
6. **Run Family C** on those ancestors. If an ancestor's *declared* status now exceeds its recomputed status → the ancestor is annotated `tcf:statusStale: true` and a `sh:Violation` entry is written to its validation report. The write is **not** rejected (the author changed a child, not the ancestor); the stale ancestor cannot cross (PC#9 gate step 4) until re-declared.
7. **Run Family A** on the write set. Violations and warnings are recorded to each node's validation report (§6). Family A `sh:Violation` does **not** reject the write — an author may keep a non-compliant draft locally. It blocks the *crossing*, not the *edit*. (Local edits never fire a seam: PC#9 trigger section.)
8. **Commit** the write set plus computed fields plus reports as one Automerge change.

### 5.3 What it refuses to do

- It never consults the target surface.
- It never upgrades a status. Only a verification action with a record does that, and the action is the author's.
- It never defaults a missing field. Missing is recorded as missing; where v1.7 requires presence, missing rejects.
- It never validates against a shape version other than the pinned one.

### 5.4 Error vocabulary (runtime; not Lexicon)

`E-STORE-INVALID` · `E-STATUS-VOCAB` · `E-CONFIRMED-NO-RECORD` · `E-TIMESENSITIVE-NO-VALIDITY` · `E-UPGRADE-WITHOUT-VERIFICATION` · `E-DERIVATION-EXCEEDS-INPUT`. All are write-rejecting. Everything else is a report entry.

---

## 6. The validation report and `tcfQuarkViolations` (PC#9 KL-6)

Each governed node stores its most recent SHACL `sh:ValidationReport`, content-addressed. At submission, the PC#9 gate does not re-validate; it **filters** the reports of the submitted node and all its descendants into `tcfQuarkViolations`:

```json
{
  "tcfQuarkViolations": [
    {
      "nodeId": "<focus node>",
      "quarkId": "tcf:q/terminology/plain-register-v1",
      "constraintClass": "terminology",
      "severity": "sh:Violation",
      "tier": "particle",
      "message": "R-1 term in plain-register content",
      "shapeVersion": "<tcfShapeVersion IRI>",
      "reportDigest": "sha256:…"
    }
  ],
  "violationSummary": { "blocking": 0, "recorded": 2, "acknowledged": 2 }
}
```

**Filtering rule feeding PC#9 gate step 5.** An entry is *blocking* iff `severity = sh:Violation` AND `tier` ≥ the grant's `minimumTcfTier` (tier order: particle < cluster < zone < structure < ecosystem < biome). Every non-blocking entry requires `operatorAcknowledgment` on the intent record; absence blocks (fail-closed on acknowledgment, not on the violation).

**Register-class entries at this shape version.** Any store-produced entry with `constraintClass = "register"` is reported as `sh:Warning` by the §6 filter regardless of the shape's declared severity (KL-4; reference: `runtime/gate/reports.py::tcf_quark_violations`), and is therefore never blocking. This rule is currently **dormant**: at this shape version the store produces no register-class entry at all — §7.4 computes and records `tcf:computedRegister` as a field and no shape in the library compares it to the declared register, so the "declared vs computed register" mismatch *entry* that v0.1 §7.4 and §9 row 6 described is **not produced** (see §9; Phase 1 candidate). The override is a **code constant** in the filter, not keyed to `shapeVersion` — it is the one place in this runtime where a severity is set by code rather than read from the library. It is removed at Phase 1 together with authoring the store-side register shape, whose `severity` will then be read from its own Quark record like any other; until then it is a disclosed, dormant exception to §2.3's "by shape-version bump, never by editing a gate".

**Two producers of entries (companion v0.1.1; PC#9 v0.2.2 N5, v0.2.3 item D, v0.2.4 4b).** The array above holds entries from two sources, distinguishable by `quarkId` (at this version, by `quarkId = "tcf:q/register/grant-requirement"` alone, since no store-produced register entry exists):

- **Store-produced** entries — everything the write-time gate recorded (§5.2 steps 6–7), filtered at submission as described. These are the **only** entries PC#9 gate step 5's blocking rule evaluates.
- **Gate-minted** entries — one kind only at this shape version: the grant-relative register mismatch, minted by PC#9 gate **step 6** when the object's declared `tcfRegister` differs from the grant's `tcfRegisterRequirement`. Entry shape (PC#9 v0.3): `{ nodeId, quarkId: "tcf:q/register/grant-requirement", constraintClass: "register", severity, shapeVersion, reportDigest }`, with `reportDigest` over `{ grantReference, tcfRegisterRequirement, tcfRegister }`. The gate **reads `severity` from the pinned library's Quark record** for `tcf:q/register/grant-requirement` (§2.3, declared-but-not-evaluated) — it does not mint a literal. The entry carries no `tier` and is **exempt from the step-5 filtering rule**: it post-dates step 5 and never retroactively changes step 5's result (PC#9 v0.3, KL-4 Disposition, record-readability note). That step 6 itself is severity-blind — checking only that an `operatorAcknowledgment` bound to the entry is present — is **PC#9's claim, carried here ~** (PC#9 v0.3, KL-4 Disposition — Mechanics: "severity is behaviourally inert in this gate … step 6 is severity-blind"); no PC#9-side build exists to verify it. If a future PC#9 revision makes step 6 severity-sensitive, this entry needs `tier` and the exemption lapses. So the entry's severity is behaviourally inert in the gate at every value; it is what the *record* says, not what the gate does. If the pinned library carries **no** such record → step 6 blocks and no acknowledgment cures it (silence blocks). Per PC#9 ("What Comes Next" item 8, as corrected fresh it-2): this is **not an issuance precondition under any written grant invariant**; it is a horizon-long uncurable block on the register-mismatch branch for any grant issued against such a library.

This is the runtime-side half of PC#9's KL-4 disposition: the store's §7.4 comparison (declared vs *computed* register, composite tiers — field only at this version) and the gate's step-6 comparison (declared vs *grant requirement*) are **two distinct comparisons**; neither evaluates register semantics. When `tcf:register` promotes, what changes here is the severity the library record carries — by shape-version bump (§8) — and, because step 6 is severity-blind, that changes the record and not the gate.

`reportDigest` and `shapeVersion` together let a reader re-run the validation later against the same shapes and get the same report — the report is reproducible, not just recorded.

---

## 7. Propagation — computed, not reasoned

### 7.1 Definition

For any composite node `N` with members `M(N)`:

```
computedStatus(N) = argmin_{m ∈ M(N)} rank( status(m) )
where status(m) = epistemicStatus(m) if m is a Particle
                = computedStatus(m)  otherwise
```

Recursion bottoms out at Particles. The value is written by the gate (§5.2 step 5), never typed by the author.

### 7.2 Rank table (plain SHACL-SPARQL form, no custom function)

```sparql
VALUES (?status ?rank) {
  ("confirmed"      3)
  ("time-sensitive" 2)
  ("inferred"       1)
  ("unverified"     0)
}
```

This `VALUES` form is valid in plain SPARQL and is used by the §7.3 `CONSTRUCT`. It is **not** valid inside a SHACL `sh:select` (BF-2); there the same table is expressed as the nested `IF()` shown in §3.4. Both forms are generated from one source, `STATUS_RANK` (`runtime/shapes/status_rank.py`), which is the **sole** place the order appears — a v1.8 re-ranking changes that one constant and both forms follow. The order itself remains ~ (§4).

### 7.3 Computation as a SPARQL CONSTRUCT (one level; iterate bottom-up by tier)

```sparql
PREFIX tcf: <https://jediwright.github.io/tcf-runtime/vocab/tcf#>
CONSTRUCT { ?n tcf:computedStatus ?weakest }
WHERE {
  {
    SELECT ?n (MIN(?rank) AS ?minRank) WHERE {
      ?n a <TIER_CLASS> ; tcf:members ?m .            # one composite tier per pass
      OPTIONAL { ?m a tcf:Particle ; tcf:epistemicStatus ?s1 }
      OPTIONAL { ?m tcf:computedStatus ?s2 }
      BIND( COALESCE(?s1, ?s2) AS ?status )
      # Silence guard (BF-6, D-6b; CP-1.1): a composite with any member that has no
      # status under §7.1 is dropped from the result, so its computedStatus is ABSENT.
      FILTER NOT EXISTS {
        ?n tcf:members ?x .
        FILTER NOT EXISTS { ?x a tcf:Particle ; tcf:epistemicStatus ?a }   # Particle: declared
        FILTER NOT EXISTS { ?x tcf:computedStatus ?b }                   # composite: computed
      }
      FILTER( BOUND(?status) )   # belt-and-braces; redundant once the guard above holds
      VALUES (?status ?rank) { ("confirmed" 3) ("time-sensitive" 2) ("inferred" 1) ("unverified" 0) }
    } GROUP BY ?n
  }
  VALUES (?weakest ?minRank) { ("confirmed" 3) ("time-sensitive" 2) ("inferred" 1) ("unverified" 0) }
}
```

Run in tier order: Clusters, then Zones, then Structures, then Ecosystems, then Biomes, substituting the tier class for `<TIER_CLASS>` on each pass. Six passes bound the computation regardless of graph size. Before each pass the gate **removes** the prior `tcf:computedStatus` on the nodes it is about to recompute, so a composite whose member lost its status becomes absent rather than stale.

**Why the guard exists (BF-6).** v0.1 claimed that a statusless member "yields no `COALESCE` binding and the node's `computedStatus` is absent." That claim was false under standard SPARQL semantics: an **unbound** `?status` is join-compatible with **every** `VALUES` row, so a statusless member contributed rank 0 and the query wrote `unverified` — a default, inserted by the engine, exactly the class of failure this runtime pre-registered against. "Statusless" means **no status under §7.1**: a Particle with no `tcf:epistemicStatus`, or a composite with no `tcf:computedStatus` — a composite's *declared* status is not its §7.1 status and does not rescue it. The `NOT EXISTS` guard drops the whole composite if *any* member is statusless in that sense (otherwise the composite would be computed over its remaining members, which is a different default). With the guard, silence **propagates upward**: a silenced Cluster leaves its Zone silent, and so on to the root — which the PC#9 gate treats as blocking (silence blocks). No default is inserted at any tier. A composite with **no members** matches no row and has no `computedStatus` (argmin over the empty set is undefined; absent, not defaulted). `FILTER(BOUND(?status))` is retained as belt-and-braces; every row that survives the guard has a bound status by construction.

**Precondition of the silence claim (Counter-Pass it.2, CP-2.1/CP-2.2).** The guard tests *presence* of a §7.1 status, not its *vocabulary* or its *placement*. Two content-graph states defeat it, and both are states the gate never writes — and, where a Particle carries a stray `computedStatus` beside a valid declared status, never reads (`COALESCE` takes the declared status first; verified, CP-3.1): (i) a composite whose `tcf:computedStatus` is outside the four-value vocabulary joins no `VALUES` row and is silently omitted from its parent's `MIN`, so the parent is computed over the remaining members; (ii) a Particle carrying `tcf:computedStatus` (a §2.4 breach — composite tiers only) binds `?s2` and contributes a status §7.1 says it does not have. The no-default claim therefore holds over graphs in which every `computedStatus` was written by §5.2 step 5 (values come from `STATUS_RANK`; the gate writes only to composites) and every Particle status passed Family B (`sh:in`). That is every graph reachable through the gate. Reaching either defeating state requires content-graph corruption, which `E-STORE-INVALID` does **not** detect — its digest covers the Quark store, not the content graph. Content-graph integrity shapes (`sh:in` on `tcf:computedStatus` in Family C; `sh:maxCount 0` on `tcf:computedStatus` in Family B) are a **Phase 1 item** (§12 open item g), not a v0.2 change: they add checks the build does not run, and the pass rule is that text matches the build unless the build is shown wrong on a gate-reachable graph.

**Correction history.** The Phase 0 build's guard tested `?x tcf:epistemicStatus` on *any* node, so a silenced composite that also carried a declared status was not treated as statusless by its parent (Counter-Pass it.1, CP-1.1). Reproduced on the pinned engine: Zone {C1 declared `confirmed`, silenced; C2 computed `confirmed`} → the build wrote `Z = unverified` (the unbound row joined rank 0 despite `BOUND`; the critic had predicted `confirmed` over C2 alone — both are inserted defaults). The guard above is the corrected form; `runtime/gate/propagation.py::construct_query` moves to match it (operator apply; the build was shown wrong under the pass rule). Verified single-level on fixture F-10 (build record §4); two-level silence is **not yet covered by a fixture** — F-10b (a silenced Cluster inside a Zone, expected `computedStatus(Z)` absent) is an operator apply and part of this amendment's validation event.

### 7.4 Register propagation (most-restrictive-up; (c), non-enforcing until `tcf:register` promotes)

Same shape, inverted lattice: `governed-internal` (2) > `contextual` (1) > `plain` (0); `computedRegister(N) = argmax`. Written by the gate alongside `computedStatus`. At this shape version §7.4 is **computed and recorded as a field only**: no shape compares `tcf:computedRegister` to the declared register, so the declared-vs-computed mismatch *entry* that v0.1 described is not produced (§6, §9 row 6; Phase 1 candidate). When that shape is authored, its severity comes from its own Quark record and changes on `tcf:register` promotion by shape-version bump.

### 7.5 `evidenceDecay` derivation (PC#9 OQ-4)

```
if computedStatus(N) = time-sensitive:
    evidenceDecay(N) = min over members m with status time-sensitive of temporalValidity(m).validUntil
elif computedStatus(N) = confirmed:
    evidenceDecay(N) = min over members m of verificationRecord(m).recencyWindowEnd
else:
    evidenceDecay(N) = author-declared or absent
```

Computed at submission by the PC#9 gate from store fields; carried into the intent record. A `time-sensitive` composite with any `time-sensitive` member lacking `temporalValidity` cannot occur — Family B rejects that Particle at write time — so the fail-closed path in PC#9 OQ-4 is reachable only via store corruption, which `E-STORE-INVALID` catches first.

---

## 8. Change control: the store under GSEF (PC#9 OQ-6)

- Adding, superseding, or re-ranking a Quark is a GSEF change event. Changes that touch shapes carrying `constraintClass = "epistemic"` or any shape the PC#9 crossing record vocabulary references are changeClass C or D (PC#9 OQ-6 premise).
- A change publishes a new `tcfShapeVersion` IRI and a new `versionDigest`. The prior version stays loadable.
- The GSEF lineage record for the change is referenced from the new Quark's `lineageRef`. It is Evidence-plane. Neither gate reads it.
- Standing grants pinned to the prior version continue to validate against it through their horizon. Renewal pins the new version. No mid-horizon migration.
- Open (queued to GSEF PP-OI series, not this spec): whether a changeClass D event should *shorten* in-flight grant horizons. This runtime says no; the GSEF session may rule otherwise.

---

## 9. What the PC#9 crossing gate reads from this runtime

| PC#9 gate step | Runtime source |
|---|---|
| 2 — shape version resolvable | `store.tcfShapeVersion` == grant pin; `versionDigest` verifies |
| 3 — tier threshold | node `@type` |
| 4 — declared == computed | `tcf:epistemicStatus` vs `tcf:computedStatus` (§7.1); `tcf:statusStale` must be false |
| 5 — no blocking violations | §6 filtered report |
| 6 — register acknowledgment | *Two distinct comparisons.* Store: declared vs §7.4 computed register (composite tiers) — **field only at this version; no store-produced entry exists** (§6; Phase 1 candidate). Gate: declared `tcfRegister` vs grant `tcfRegisterRequirement` → gate-minted entry, severity read from the library's `tcf:q/register/grant-requirement` record at the pinned version (§6) → acknowledgment presence; missing record → block |
| 7 — `evidenceDecay` derivable | §7.5 |

The gate reads; it does not compute anything the store has not already computed, with one exception: §7.5 is computed at submission because it depends on the grant's horizon context, not on the store alone.

---

## 10. Known limits of this runtime spec

| RL | Limit | Closing evidence |
|---|---|---|
| RL-1 | All `tcf:` field names are (c) — TCF v1.7 candidates | TCF v1.8 Section B confirms or renames; this spec re-issues with a binding delta table. **v0.2 carries one binding delta already: the namespace base (§0).** Field names unchanged. |
| RL-2 | Status order (§4) is a proposal | TCF v1.8 Quark-level ruling |
| RL-3 | `confidence_level` folded into status without a ruling | TCF v1.8 keeps or drops |
| RL-4 | Family A shape instances not authored | Post-v1.8 shape-library session |
| RL-5 | Automerge as the store substrate is the only one considered | Second substrate (dialog-db / Hexane) assessed under PC#8 Phase 2 scoping; this spec does not claim substrate independence |
| RL-6 | ~~SHACL-SPARQL engine availability on the author's substrate is assumed, not verified~~ **Closed 2026-09-11** on a real run: pyshacl 0.40.1 / rdflib 7.6.0, `requirements.lock` sha256 `3027f990…`; all six `E-*` codes reached (build record §2, §7; SL-0228 pending append). Residual: one engine, one machine; engine limit BF-3 (`focus_nodes`) worked around, recheck at Phase 1 | — |
| RL-7 | No performance claim for §7.3 over large graphs | Prototype measurement. One informational data point: 52.99 ms on fixture F-12 (two composite levels, operator machine). Not a claim. |
| RL-8 | This spec's own three-way-convergence framing (§4 rationale) cites the Playbook §10.1 argument, which is itself ~ | Not closable here; carried as citation, not claim |

---

## 11. Queue to the TCF v1.8 session (not amendments; requests)

1. Confirm or rename the five Section B candidate fields against the bindings in §2.4.
2. Rule the status total order (§4) — or rule that `time-sensitive` is orthogonal.
3. Decide `confidence_level` (RL-3).
4. Adopt or reject the verification / derivation record shapes (§3.3) as the Section B "controlled vocabulary — record format" stubs.
5. Adopt or reject §7.3 as the formal expression of the propagation rule the v1.7 stub asks for.
6. Note KL-11/KL-12 from PC#9 v0.2 as cross-references.

This runtime will be re-issued against whatever v1.8 rules, with a binding delta table. Nothing here pre-empts that session. v0.2 is *not* that re-issue; it is the pre-v1.8 correction pass. Additional v1.8 inputs surfaced by Phase 0 and carried outside this document: BF-4 (§5.2 step 3 "previous status timestamp" is undefined in §2.4 — the build reads the prior `verificationRecord.verifiedAt` when present, else no lower bound; the one lenient build choice), the KL-11 candidate from build record §6, and the RL-3 no-pressure observation.

---

## 12. Change log — v0.1 → v0.2 (2026-09-11)

Source of every row: `records/phase0-build-record_2026-09-11.md` §5 (findings BF-*), §8 (rulings D-*), §2 (mandated line); `session-handoff-tcf-runtime-phase0-close_2026-09-11.md` §3. Ledger: SL-0229 (spec-text findings, OPEN; **pending append**) — this amendment is its closing event, recorded as a supersession, not a new claim.

| Item | Section(s) | Change | Source |
|---|---|---|---|
| Namespace base | §0, §2.3 example, §3.4 and §7.3 `PREFIX`, RL-1 | `…/seam-stack/vocab/tcf#` → `…/tcf-runtime/vocab/tcf#`; library versions `…/tcf-runtime/vocab/tcf/<date>`. Binding delta under RL-1; field names unchanged. | Plan v0.1.2 change log; D-1; build record §2 mandated line |
| BF-1 Turtle escaping | §3 (new serialization note), §3.1–3.4 | `/` in prefixed local names escaped `\\/`; IRIs unchanged; JSON `quarkId` strings unaffected. | Build record §5 BF-1 |
| BF-2 rank form | §3.4, §7.2 | `VALUES` is not permitted inside `sh:select` (W3C SHACL §5.3.2). §3.4 now shows the nested `IF()` generated from `STATUS_RANK`; §7.2 states the two forms and the single source. `VALUES` retained for §7.3. | Build record §5 BF-2; D-5a |
| BF-5 step order | §5.2 step 3 | Order unchanged (Family B before the upgrade rule — deliberate). Consequence stated: upgrade-to-`confirmed`-without-record rejects `E-CONFIRMED-NO-RECORD` at step 2; `E-UPGRADE-WITHOUT-VERIFICATION` reachable only when Family B passes. **Plan §6 F-05a's predicted code corrected to `E-CONFIRMED-NO-RECORD`**; F-05a-supp (`unverified` → `inferred`, no record) is the canonical fixture for `E-UPGRADE-WITHOUT-VERIFICATION`. The fixture file's `expected` field is an operator apply after issuance (plan §6 authoring rule; D-6a precedent) — see open items. | Build record §5 BF-5; D-6a |
| BF-6 silence guard | §7.3 | v0.1's silence claim was false under SPARQL semantics (unbound joins every `VALUES` row → `unverified` default). `FILTER(BOUND)` + `FILTER NOT EXISTS` guard added; per-tier targeting and prior-value removal stated; rationale paragraph added. Stricter reading: absent = blocking at PC#9. | Build record §5 BF-6; D-6b(a) |
| Companion v0.1.1 (D-4) | §2.3 (record + invariant), §6 (two producers), §9 row 6 | `tcf:q/register/grant-requirement` registered as a declared-but-not-evaluated Quark carrying `severity: sh:Warning`; `evaluated`/`constraintRef: null` semantics defined; PC#9 gate step 6 mints the grant-relative register entry reading severity from the pinned library; missing record → block; store-produced vs gate-minted entries distinguished; §9 row 6 names the two distinct comparisons. | PC#9 v0.2.2 N5, v0.2.3 item D, v0.2.4 4b, "What Comes Next" item 8; plan D-4; build record §2 mandated line |
| **it.1 reconciliation** | §2.3, §3, §3.2, §5.2, §6, §7.3, §9, §12 | CP-1.1 (BREAKS, build-wrong confirmed): §7.3 guard tests Particle-declared status, not any-node — silence now propagates across tiers; `propagation.py` fix + fixture F-10b are operator applies. CP-1.2: F-10 claim scoped to one level; `BOUND` stated as redundant. CP-1.3: step 2 = presence *and* conformance; reachable set for `E-UPGRADE-WITHOUT-VERIFICATION` completed. CP-1.4: `register` added to `quarkClass` enumeration as runtime-only. CP-1.5: store-side §7.4 register *entry* stated as not produced at this version (field only); v0.1's "register-class entries are `sh:Warning`" sentence **restored, re-scoped to store-produced entries** (the gate-minted entry, also `constraintClass: "register"`, takes its severity from the library record instead) with its build reference (`reports.py`) — its deletion in it.0 was a silent change, now logged. CP-1.6: gate-minted entry exempt from the step-5 tier/severity filter (PC#9 entry shape kept). CP-1.7: missing-record consequence restated per PC#9 item 8 — horizon-long block, not an issuance invariant. CP-1.8: §3 prefix assumption stated. CP-1.9: `sh:in` order aligned to generator. CP-1.10: open item (b) completed. | `counter-pass-critic-return-it1-tcf-runtime-v0-2_2026-09-11.md` |
| **it.2 reconciliation** | §5.2, §6, §7.3, §7.4, §12, footer | CP-2.1/2.2 (NARROWS): silence claim given its precondition — presence not vocabulary/placement; corruption-only counterexamples reproduced on the pinned engine; integrity shapes deferred to Phase 1 (open item g) rather than a second query change. CP-2.3: empty composite → absent. CP-2.4: step 3 reachable set folded to "any upgrade failing step 3's three checks"; "step 3 validates" corrected. CP-2.5: §7.4 clause — field only, entry not produced (§7.4 is out of the critic's lane; the clause removes a contradiction the in-lane §6 change created and makes no new claim). CP-2.6: `reports.py` override stated as a code constant, dormant, removed at Phase 1 — a disclosed exception to "never by editing a gate". CP-2.7: severity-blind step 6 tagged ~ and sourced to PC#9 v0.3 KL-4 Disposition — Mechanics. CP-2.8: it.1 row says "re-scoped". Footer iteration stamp fixed. | `counter-pass-critic-return-it2-tcf-runtime-v0-2_2026-09-11.md` |
| **it.3 reconciliation — CONVERGED** | §3.4, §5.2, §7.3, §12 | CP-3.1 (NIT): stray Particle `computedStatus` is gate-reachable but never read — reachability sentence corrected. CP-3.2 (NIT): step 3 case (b) carve-out for `confirmed` upgrades. CP-3.3 (NARROWS, non-blocking): `IF()`/`VALUES` identity holds at RDF 1.1 term equality; on rdflib 7.6.0 a typed `xsd:string` variant makes `IF()` the stricter — reproduced producer-side; sentence added to §3.4. CP-3.4 (NIT): open item (b) made current. CP-2.1/2.2 deferrals accepted by the critic as checkable reasons. Critic's diff base was the it.0 candidate (`899449cf`, operator attachment) — cumulative it.0→it.2 diff verified instead, no silent change. | `counter-pass-critic-return-it3-tcf-runtime-v0-2_2026-09-11.md` |
| RL-6 closed | §10 | Engine pinned on a real run; residual stated. | Build record §2, §7; SL-0228 (pending append) |
| RL-7 note | §10 | One informational timing recorded; no claim. | Build record §4 |
| Housekeeping | header, footer, §11 pointer | Status → v0.2 candidate; companion reference PC#9 v0.2 → v0.3; §11 clarifies v0.2 is not the v1.8 re-issue; v1.8 inputs from Phase 0 named. | — |

**Not changed, deliberately (out of lane; TCF v1.8 owns them):** §4 order and KL-11; §7.5; RL-3; BF-4 (§5.2 step 3 timestamp source — text left as v0.1 wrote it, with the build's reading disclosed in §11); §5.4 error vocabulary (no new `E-*` codes).

**Validation event for this amendment — PASSED 2026-09-11.** `tools/run_fixtures.py` on the operator's machine at `tcf-runtime` **`fa7fded`** (CP-1.1 guard fix + fixture F-10b): F-01–F-15 unchanged from Phase 0, F-05a red-and-logged (BF-5, its `expected` apply still open), F-10 green, **F-10b green** (`computedStatus(Z2)` absent — two-level silence). §7.3 on F-12: 44.43 ms (informational). Run record: `records/fixture-results.json` at `fa7fded`.

**Open items from this amendment (operator applies, not spec changes):** (a) F-05a `expected` → `E-CONFIRMED-NO-RECORD` in `fixtures/` and plan §6 errata note; (b) `runtime/shapes/library.py` module docstring still says BF-1/BF-2 are "queued" and calls the namespace base a "declared deviation" from spec §0 — false once v0.2 issues; hygiene edit (`propagation.py` already corrected at `fa7fded`); (c) whether the loader should refuse a `constraintRef: null` record lacking `evaluated: false` — **not a v0.2 claim**; queued as a Phase 1 design item (§2.3 states the reading only); (d) `propagation.py` guard fix (CP-1.1) — **done, `fa7fded`**; (e) fixture F-10b — **done, `fa7fded`**; (g) **content-graph integrity shapes** (CP-2.1/2.2): `sh:in` on `tcf:computedStatus` in Family C and `sh:maxCount 0` on `tcf:computedStatus` in Family B, plus a fixture for each — Phase 1; until then the §7.3 silence claim carries its stated precondition; (f) a Phase 1 candidate shape producing the store-side declared-vs-computed register entry (§6, §9 row 6), and a cross-reference to PC#9 v0.3 OQ-2, which currently states that composite-tier `tcfRegister` "is witnessed by the store's §7.4 declared-vs-computed entry" — that entry does not exist at this runtime version; PC#9 hygiene item, not amended here.

**Out-of-lane observations logged from Counter-Pass it.1 (not acted on; routed):** (i) `gate.py` step 3 compares `verifiedAt` lexically via `str()`, not by `xsd:dateTime` value order — BF-4 territory, v1.8/Phase 1; (ii) §3.4 Family C has no `sh:in` on `tcf:computedStatus`, so an out-of-vocabulary computed value passes the rank `FILTER` silently — folded into open item (g); a composite carrying two `tcf:computedStatus` values (`sh:maxCount` breach) yields `MIN` over both — same class, same routing (it.2); a composite's *declared* `tcf:epistemicStatus` is bound by no `sh:in` (Family B targets Particles only) — the reachable half of CP-3.3, also item (g) (it.3); (iii) `gate.py` step 3 skips the upgrade check when the prior status is out-of-vocabulary — same reachability, same routing; (iv) `constraintRef` uses `urn:tcf:shape:…` while shape IRIs are `…tcf#sh/…` and the binding is unstated — v0.1-inherited, queued to the post-v1.8 shape-library session with RL-4.

---

*Companion to Pattern Commons #9 v0.3 and to the Phase 0 build record. Not a TCF amendment. AI-collaborative drafting, human authorial responsibility, intellectual direction held by the named author.*

*Counter-Pass converged with narrowing (it.3). All bindings (c) and ~. Phase 0 prototype exists (`runtime/`, one engine, one fixture set); no generality claims. Delivery-not-application enforced.*

*Session: Session Harness v0.2, Mode 3 Counter-Pass (producer; siloed critic it.1–it.3), CONTEXTUAL. Closes SL-0229 (supersession). Ledger delta SL-0231 proposed at close — next free, verify tail.*

*UX Minds, LLC · J. Wright · v0.1 August 24, 2026 · v0.2 issued September 11, 2026*
