"""Writes fixtures/F-*.json from plan v0.1.2 §6 verbatim. Each fixture is self-contained:
`prior` nodes are injected into the graph directly (store bypass — how F-10 must be built
anyway), `writeSet` goes through the gate. Expected outcomes are the runtime spec's
predictions; the runner never edits a fixture to pass. Usage: python -m tools.author_fixtures"""
import json, os

VA = "https://jediwright.github.io/tcf-runtime/vocab/tcf/2026-09-11"
VB = "https://jediwright.github.io/tcf-runtime/vocab/tcf/2026-09-11-b"
AGENT = "urn:agent:jwright"

def rec(verified_at="2026-09-11T10:00:00Z", window="2027-09-11T10:00:00Z", ev="urn:evidence:ppg-1"):
    return {"verificationMethod": "primary-source-read", "verifiedBy": AGENT,
            "verifiedAt": verified_at, "recencyWindowEnd": window, "verificationEvidenceRef": ev}

def validity(until="2026-12-31"):
    return {"validFrom": "2026-09-01", "validUntil": until}

def P(id, status, **extra):
    n = {"id": f"tcf:{id}", "type": "Particle", "epistemicStatus": status,
         "claimType": "claim", "authoritySource": AGENT}
    n.update(extra); return n

def C(id, members, status, tier="Cluster", **extra):
    n = {"id": f"tcf:{id}", "type": tier, "members": [f"tcf:{m}" for m in members],
         "epistemicStatus": status}
    n.update(extra); return n

P1u = P("P1", "unverified")
P8 = P("P8", "confirmed", verificationRecord=rec(), register="plain")
P9 = P("P9", "time-sensitive", temporalValidity=validity(), register="governed-internal")
P10 = P("P10", "inferred", derivationRecord={"derivedFrom": ["tcf:P8", "tcf:P9"],
        "reasoningStep": "synthesis of P8 and P9", "confidenceBasis": "two verified inputs"})
F08_PRIOR = [P8, P9, P10]
C1_ok = C("C1", ["P8", "P9", "P10"], "inferred", computedStatus="inferred")

FIX = [
 dict(id="F-01", specRef="§3.2", prior=[], writeSet=[P1u],
      expected=dict(outcome="Accept", reportViolations={"tcf:P1": 0})),
 dict(id="F-02", specRef="§3.2, §5.2 step 2", prior=[], writeSet=[P("P2", "confirmed")],
      expected=dict(outcome="Reject", code="E-CONFIRMED-NO-RECORD")),
 dict(id="F-03", specRef="§3.2", prior=[], writeSet=[P("P3", "time-sensitive")],
      expected=dict(outcome="Reject", code="E-TIMESENSITIVE-NO-VALIDITY")),
 dict(id="F-04", specRef="§3.2", prior=[], writeSet=[P("P4", "verified")],
      expected=dict(outcome="Reject", code="E-STATUS-VOCAB")),
 dict(id="F-05a", specRef="§5.2 step 3", prior=[P1u], writeSet=[P("P1", "confirmed")],
      expected=dict(outcome="Reject", code="E-UPGRADE-WITHOUT-VERIFICATION")),
 dict(id="F-05a-supp", specRef="§5.2 step 3 (supplementary, build-authored; ratified D-6a 2026-09-11)",
      supplementary=True, prior=[P1u], writeSet=[P("P1", "inferred")],
      expected=dict(outcome="Reject", code="E-UPGRADE-WITHOUT-VERIFICATION")),
 dict(id="F-05b", specRef="§5.2 step 3, §3.3", prior=[P1u],
      writeSet=[P("P1", "confirmed", verificationRecord=rec())],
      expected=dict(outcome="Accept")),
 dict(id="F-05c", specRef="§5.2 step 3", prior=[P("P1", "confirmed", verificationRecord=rec())],
      writeSet=[P("P1", "inferred")], expected=dict(outcome="Accept")),
 dict(id="F-06", specRef="§5.2 step 4", prior=[P("P5", "inferred"), P("P6", "unverified")],
      writeSet=[P("P7", "inferred", derivationRecord={"derivedFrom": ["tcf:P5", "tcf:P6"],
                "reasoningStep": "s", "confidenceBasis": "b"})],
      expected=dict(outcome="Reject", code="E-DERIVATION-EXCEEDS-INPUT")),
 dict(id="F-06b", specRef="§5.2 step 4", prior=[P("P5", "inferred"), P("P6", "unverified")],
      writeSet=[P("P7", "unverified", derivationRecord={"derivedFrom": ["tcf:P5", "tcf:P6"],
                "reasoningStep": "s", "confidenceBasis": "b"})],
      expected=dict(outcome="Accept")),
 dict(id="F-07", specRef="§2.3, §5.2 step 1", storeRoot="fixtures/stores/corrupt", prior=[],
      writeSet=[P1u], expected=dict(outcome="Reject", code="E-STORE-INVALID", shapesRan=False)),
 dict(id="F-08", specRef="§7.1; PC#9 tcfComputedStatusWitness", prior=F08_PRIOR,
      writeSet=[C("C1", ["P8", "P9", "P10"], "inferred")],
      expected=dict(outcome="Accept", computedStatus={"tcf:C1": "inferred"}, witness={"tcf:C1": "tcf:P10"})),
 dict(id="F-09", specRef="§5.2 step 6, §3.4", prior=F08_PRIOR + [C("C1", ["P8", "P9", "P10"], "confirmed", computedStatus="inferred")],
      writeSet=[dict(P8, body="P8 body edited")],
      expected=dict(outcome="Accept", stale=["tcf:C1"], reportComponent={"tcf:C1": "SPARQLConstraintComponent"})),
 dict(id="F-10", specRef="§7.3 silence",
      prior=[{"id": "tcf:P11", "type": "Particle", "claimType": "claim", "authoritySource": AGENT}, P8],
      writeSet=[C("C2", ["P11", "P8"], "inferred")],
      expected=dict(outcome="Accept", computedStatusAbsent=["tcf:C2"])),
 dict(id="F-10b", specRef="§7.3 silence, two levels (runtime v0.2 CP-1.1)", supplementary=True,
      prior=[{"id": "tcf:P11", "type": "Particle", "claimType": "claim", "authoritySource": AGENT}, P8,
             C("C2", ["P11", "P8"], "inferred"),                       # silenced one tier down (F-10 state); declared, no computedStatus
             C("C3", ["P8"], "confirmed", computedStatus="confirmed")],
      writeSet=[C("Z2", ["C2", "C3"], "inferred", tier="Zone")],
      expected=dict(outcome="Accept", computedStatusAbsent=["tcf:Z2"])),
 dict(id="F-11", specRef="§5.2 step 7, §3.1", prior=[],
      writeSet=[P("P12", "unverified", body="the substrate handles this")],
      expected=dict(outcome="Accept", reportEntry={"tcf:P12": {"constraintClass": "terminology", "severity": "sh:Violation"}},
                    quarkViolations={"particle": {"blocking": 1}, "cluster": {"blocking": 0, "recorded": 1}})),
 dict(id="F-12", specRef="§7.1, §7.3 tier ordering", prior=F08_PRIOR + [C1_ok],
      writeSet=[C("C3", ["P8"], "confirmed"), C("Z1", ["C1", "C3"], "inferred", tier="Zone")],
      expected=dict(outcome="Accept", computedStatus={"tcf:C3": "confirmed", "tcf:Z1": "inferred"}, timed=True)),
 dict(id="F-13", specRef="§7.4, KL-4", prior=[P8, P9],
      writeSet=[C("C4", ["P8", "P9"], "inferred")],
      expected=dict(outcome="Accept", computedRegister={"tcf:C4": "governed-internal"}, blockingEntries=0)),
 dict(id="F-14", specRef="§5.2 step 1, §5.3 last bullet", current=VB,
      prior=F08_PRIOR + [dict(C1_ok, shapeVersion=VA)],
      writeSet=[C("C1", ["P8", "P9", "P10"], "inferred")],
      expected=dict(outcome="Accept", shapeVersionUsed={"tcf:C1": VA})),
 dict(id="F-15", specRef="§7.5", optional=True, prior=F08_PRIOR,
      writeSet=[C("C1", ["P8", "P9", "P10"], "inferred")],
      expected=dict(outcome="Accept", evidenceDecay=None,
                    rerun=dict(writeSet=[C("C1", ["P8", "P9"], "inferred")], evidenceDecay="2026-12-31"))),
]

def main():
    os.makedirs("fixtures", exist_ok=True)
    for f in FIX:
        with open(f"fixtures/{f['id']}.json", "w", encoding="utf-8") as fh:
            json.dump(f, fh, indent=2, ensure_ascii=False)
    print(f"wrote {len(FIX)} fixtures")

if __name__ == "__main__":
    main()
