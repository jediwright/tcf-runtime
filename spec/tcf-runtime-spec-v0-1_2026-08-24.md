**Status:** v0.1 — governed draft (Session Harness v0.2, Mode 1); single-context; companion to PC#9 v0.2; **not a TCF amendment**

⚑ SINGLE-CONTEXT — NOT PANELED
All field names marked (c) are TCF v1.7 *candidate* names, unconfirmed, carried here as bindings pending TCF v1.8 Section B. This document proposes no change to the TCF; where it needs something the TCF has not ruled, it says so and queues it.

---

# TCF Runtime Specification v0.1

## What the gate mechanism makes possible: a Quark store, per-tier shapes, a write-time epistemic gate, and a computed propagation rule

---

## 0. Position and posture

The TCF v1.7 Amendment locks the *architecture* of epistemic status: four values (Confirmed / Inferred / Unverified / Time-sensitive), governed at the Quark level, declared at the Particle level, inherited upward by weakest-status, upgradable only by a verification action with a record attached. It stubs the *implementation*: field names, controlled vocabularies, the SHACL shape, the JSON-LD mappings, and the formal propagation constraint — all queued to a dedicated specification pass.

PC#9 needs the implementation to exist as a runtime, because its gate reads it. This document specifies that runtime **on the locked architecture only**, binding to the candidate field names provisionally and marking every binding as such. It is the "practice precedes framework" move: the runtime is built to what v1.7 locks, and the TCF v1.8 session inherits a worked runtime instead of a blank stub.

**What this document is not.** Not an amendment to TCF v1.7. Not a promotion of any PROPOSED Lexicon term. Not the per-tier shape *library* (that is authored after v1.8 rules the field names). Not a generality claim: one reference substrate (Automerge document store, PC#8 harness) and one reference surface class.

**Namespaces.** `tcf:` = `https://jediwright.github.io/seam-stack/vocab/tcf#` (proposed; sits under the existing vocabulary IRI). `seam:` = existing Seam Stack vocabulary. `sh:` = SHACL. All `tcf:` IRIs in this document are (c) until v1.8.

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
  "tcfShapeVersion": "https://jediwright.github.io/seam-stack/vocab/tcf/2026-08-24",
  "quarks": {
    "<quarkId>": {
      "quarkId": "tcf:q/terminology/plain-register-v1",
      "quarkClass": "terminology | length | tone | metadata | accessibility | brand-voice | prompt | epistemic",
      "appliesToTier": ["particle", "cluster"],
      "constraintRef": "urn:tcf:shape:PlainRegisterTerminologyShape",
      "severity": "sh:Violation | sh:Warning | sh:Info",
      "register": "plain | contextual | governed-internal",
      "introducedIn": "<tcfShapeVersion IRI>",
      "supersededBy": null,
      "lineageRef": "<GSEF lineage record recordId, or null>"
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

### 3.1 Family A — per-tier constraint shapes (structure specified; instances deferred)

One shape per (Quark, tier) pair, generated from Quark records:

```turtle
tcf:sh/PlainRegisterTerminologyShape
    a sh:NodeShape ;
    sh:targetClass tcf:Particle, tcf:Cluster ;          # from appliesToTier
    sh:severity sh:Violation ;                          # from quark.severity
    tcf:quarkId tcf:q/terminology/plain-register-v1 ;   # back-reference; lets §6 filter by Quark
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
tcf:sh/EpistemicStatusShape
    a sh:NodeShape ;
    sh:targetClass tcf:Particle ;
    sh:severity sh:Violation ;
    tcf:quarkId tcf:q/epistemic/status-v1 ;
    tcf:constraintClass "epistemic" ;

    # exactly one status from the locked vocabulary
    sh:property [
        sh:path tcf:epistemicStatus ;
        sh:minCount 1 ; sh:maxCount 1 ;
        sh:in ( "confirmed" "inferred" "unverified" "time-sensitive" )
    ] ;
    sh:property [ sh:path tcf:claimType ; sh:minCount 1 ; sh:in ( "fact" "claim" "opinion" "policy" ) ] ;
    sh:property [ sh:path tcf:authoritySource ; sh:minCount 1 ] ;

    # v1.7 locked rule: Confirmed requires an attached verification record
    sh:or (
        [ sh:property [ sh:path tcf:epistemicStatus ; sh:not [ sh:hasValue "confirmed" ] ] ]
        [ sh:property [ sh:path tcf:verificationRecord ; sh:minCount 1 ; sh:node tcf:sh/VerificationRecordShape ] ]
    ) ;

    # Time-sensitive requires temporal validity (PC#9 OQ-4 fail-closed depends on this)
    sh:or (
        [ sh:property [ sh:path tcf:epistemicStatus ; sh:not [ sh:hasValue "time-sensitive" ] ] ]
        [ sh:property [ sh:path tcf:temporalValidity ; sh:minCount 1 ; sh:node tcf:sh/TemporalValidityShape ] ]
    ) ;

    # AI provenance is a distinct field and never sets status (v1.7 locked)
    sh:property [ sh:path tcf:aiProvenance ; sh:maxCount 1 ] .
```

### 3.3 Verification and derivation record shapes (implements v1.7 stubs at runtime; (c))

```turtle
tcf:sh/VerificationRecordShape
    a sh:NodeShape ;
    sh:property [ sh:path tcf:verificationMethod ; sh:minCount 1 ;
                  sh:in ( "primary-source-read" "external-attestation" "operator-attestation" "automated-check" ) ] ;
    sh:property [ sh:path tcf:verifiedBy ; sh:minCount 1 ] ;
    sh:property [ sh:path tcf:verifiedAt ; sh:minCount 1 ; sh:datatype xsd:dateTime ] ;
    sh:property [ sh:path tcf:recencyWindowEnd ; sh:minCount 1 ; sh:datatype xsd:dateTime ] ;
    sh:property [ sh:path tcf:verificationEvidenceRef ; sh:minCount 0 ] .   # Evidence-plane pointer; optional

tcf:sh/DerivationRecordShape        # required on Inferred Particles that were produced by a reasoning step
    a sh:NodeShape ;
    sh:property [ sh:path tcf:derivedFrom ; sh:minCount 1 ; sh:class tcf:Particle ] ;
    sh:property [ sh:path tcf:reasoningStep ; sh:minCount 1 ] ;
    sh:property [ sh:path tcf:confidenceBasis ; sh:minCount 1 ] .

tcf:sh/TemporalValidityShape
    a sh:NodeShape ;
    sh:property [ sh:path tcf:validFrom ; sh:minCount 1 ; sh:datatype xsd:date ] ;
    sh:property [ sh:path tcf:validUntil ; sh:minCount 1 ; sh:datatype xsd:date ] .
```

`verificationMethod` value `primary-source-read` is the runtime form of the Pre-Draft Primary-Source Gate (PPG, SL-0144 notes). It is the only method under which a `confirmed` status is self-issued by the author; the record must then carry a `verificationEvidenceRef`.

### 3.4 Family C — propagation shape (composite tiers; implements v1.7 "computed rather than declared")

```turtle
tcf:sh/PropagationShape
    a sh:NodeShape ;
    sh:targetClass tcf:Cluster, tcf:Zone, tcf:Structure, tcf:Ecosystem, tcf:Biome ;
    sh:severity sh:Violation ;
    tcf:quarkId tcf:q/epistemic/propagation-v1 ;
    tcf:constraintClass "epistemic" ;

    # a composite must carry a computed status, and it must equal the SPARQL-derived weakest
    sh:property [ sh:path tcf:computedStatus ; sh:minCount 1 ; sh:maxCount 1 ] ;
    sh:sparql [
        sh:message "Declared status exceeds computed weakest-status of members" ;
        sh:select """
            PREFIX tcf: <https://jediwright.github.io/seam-stack/vocab/tcf#>
            SELECT $this ?declared ?computed WHERE {
                $this tcf:epistemicStatus ?declared ; tcf:computedStatus ?computed .
                BIND( tcf:rank(?declared) AS ?rd )     # rank function per §7.2
                BIND( tcf:rank(?computed) AS ?rc )
                FILTER( ?rd > ?rc )
            }
        """
    ] .
```

`tcf:rank` is not a SPARQL builtin; §7.2 gives the equivalent `VALUES` table so the constraint is expressible in plain SHACL-SPARQL without a custom function.

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

**Filtering rule feeding PC#9 gate step 5.** An entry is *blocking* iff `severity = sh:Violation` AND `tier` ≥ the grant's `minimumTcfTier` (tier order: particle < cluster < zone < structure < ecosystem < biome). Entries with `constraintClass = "register"` are always `sh:Warning` until `tcf:register` is promoted (PC#9 KL-4) and are therefore never blocking at this shape version. Every non-blocking entry requires `operatorAcknowledgment` on the intent record; absence blocks (fail-closed on acknowledgment, not on the violation).

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

Inline this `VALUES` block wherever §3.4 shows `tcf:rank(...)`.

### 7.3 Computation as a SPARQL CONSTRUCT (one level; iterate bottom-up by tier)

```sparql
PREFIX tcf: <https://jediwright.github.io/seam-stack/vocab/tcf#>
CONSTRUCT { ?n tcf:computedStatus ?weakest }
WHERE {
  {
    SELECT ?n (MIN(?rank) AS ?minRank) WHERE {
      ?n tcf:members ?m .
      OPTIONAL { ?m a tcf:Particle ; tcf:epistemicStatus ?s1 }
      OPTIONAL { ?m tcf:computedStatus ?s2 }
      BIND( COALESCE(?s1, ?s2) AS ?status )
      VALUES (?status ?rank) { ("confirmed" 3) ("time-sensitive" 2) ("inferred" 1) ("unverified" 0) }
    } GROUP BY ?n
  }
  VALUES (?weakest ?minRank) { ("confirmed" 3) ("time-sensitive" 2) ("inferred" 1) ("unverified" 0) }
}
```

Run in tier order: Clusters, then Zones, then Structures, then Ecosystems, then Biomes. Six passes bound the computation regardless of graph size. A member with *no* status (neither declared nor computed) yields no `COALESCE` binding and the node's `computedStatus` is **absent** — which the PC#9 gate treats as blocking (silence blocks). No default is inserted.

### 7.4 Register propagation (most-restrictive-up; (c), non-enforcing until `tcf:register` promotes)

Same shape, inverted lattice: `governed-internal` (2) > `contextual` (1) > `plain` (0); `computedRegister(N) = argmax`. Written by the gate alongside `computedStatus`. Feeds PC#9's `tcfRegister` declared-vs-computed comparison *as a recorded mismatch* only. Nothing about §7.4 changes when `tcf:register` promotes except the severity of the mismatch entry (§6) — by shape-version bump.

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
| 6 — register acknowledgment | §7.4 computed register vs grant requirement → mismatch entry → acknowledgment presence |
| 7 — `evidenceDecay` derivable | §7.5 |

The gate reads; it does not compute anything the store has not already computed, with one exception: §7.5 is computed at submission because it depends on the grant's horizon context, not on the store alone.

---

## 10. Known limits of this runtime spec

| RL | Limit | Closing evidence |
|---|---|---|
| RL-1 | All `tcf:` field names are (c) — TCF v1.7 candidates | TCF v1.8 Section B confirms or renames; this spec re-issues as v0.2 with a binding delta |
| RL-2 | Status order (§4) is a proposal | TCF v1.8 Quark-level ruling |
| RL-3 | `confidence_level` folded into status without a ruling | TCF v1.8 keeps or drops |
| RL-4 | Family A shape instances not authored | Post-v1.8 shape-library session |
| RL-5 | Automerge as the store substrate is the only one considered | Second substrate (dialog-db / Hexane) assessed under PC#8 Phase 2 scoping; this spec does not claim substrate independence |
| RL-6 | SHACL-SPARQL engine availability on the author's substrate is assumed, not verified | Phase 0 build: pick and pin an engine; `E-STORE-INVALID` must be reachable from a real run |
| RL-7 | No performance claim for §7.3 over large graphs | Prototype measurement |
| RL-8 | This spec's own three-way-convergence framing (§4 rationale) cites the Playbook §10.1 argument, which is itself ~ | Not closable here; carried as citation, not claim |

---

## 11. Queue to the TCF v1.8 session (not amendments; requests)

1. Confirm or rename the five Section B candidate fields against the bindings in §2.4.
2. Rule the status total order (§4) — or rule that `time-sensitive` is orthogonal.
3. Decide `confidence_level` (RL-3).
4. Adopt or reject the verification / derivation record shapes (§3.3) as the Section B "controlled vocabulary — record format" stubs.
5. Adopt or reject §7.3 as the formal expression of the propagation rule the v1.7 stub asks for.
6. Note KL-11/KL-12 from PC#9 v0.2 as cross-references.

This runtime will be re-issued at v0.2 against whatever v1.8 rules, with a binding delta table. Nothing here pre-empts that session.

---

*Companion to Pattern Commons #9 v0.2. Not a TCF amendment. AI-collaborative drafting, human authorial responsibility, intellectual direction held by the named author.*

*⚑ SINGLE-CONTEXT — NOT PANELED. All bindings (c) and ~. No prototype. One reference substrate, one reference surface class; no generality claims. Delivery-not-application enforced.*

*Session: Session Harness v0.2, Mode 1, CONTEXTUAL. Ledger delta proposed at session close.*

*UX Minds, LLC · J. Wright · August 24, 2026*
