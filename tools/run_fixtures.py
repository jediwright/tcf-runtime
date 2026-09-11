"""C-6 fixture runner (plan §7 B-6). Loads each fixture, runs the gate, asserts the
expected outcome, prints the results table and writes records/fixture-results.json.
A red row is a divergence between the spec's prediction and the gate — a finding, never
a reason to edit the fixture. Exit 0 iff all non-optional rows are green."""
import glob, json, os, sys
from rdflib import Graph, URIRef, RDF

from runtime.gate.gate import Gate, Accept, Reject, ERROR_VOCABULARY
from runtime.gate.graphs import nodes_to_graph
from runtime.gate.propagation import evidence_decay
from runtime.gate.reports import tcf_quark_violations
from runtime.shapes.library import TCF, TCF_BASE
from runtime.shapes.status_rank import rank
from runtime.store.adapters.file import FileStoreAdapter

def iri(s): return URIRef(TCF_BASE + s[4:]) if s.startswith("tcf:") else URIRef(s)
def short(u): return "tcf:" + str(u).rsplit("#", 1)[-1]

def witness(g, n):
    """PC#9 tcfComputedStatusWitness: a member whose status equals the computed status."""
    cs = g.value(n, TCF.computedStatus)
    for m in g.objects(n, TCF.members):
        st = g.value(m, TCF.epistemicStatus) if (m, RDF.type, TCF.Particle) in g else g.value(m, TCF.computedStatus)
        if st is not None and cs is not None and str(st) == str(cs):
            return short(m)
    return None

def run(fx):
    VA = "https://jediwright.github.io/tcf-runtime/vocab/tcf/2026-09-11"
    # Phase 0 runs at v-A unless the fixture pins otherwise (F-14 loads v-B).
    adapter = FileStoreAdapter(fx.get("storeRoot", "fixtures/stores"), current=fx.get("current", VA))
    gate = Gate(adapter)
    ctx = adapter.load(adapter.current_version()).context if fx.get("storeRoot", "").endswith("corrupt") is False else None
    # prior state is injected directly (store bypass); use the uncorrupted context to parse it
    ctx = FileStoreAdapter("fixtures/stores").load(adapter.versions()[0]).context if ctx is None else ctx
    g = nodes_to_graph(fx["prior"], ctx) if fx["prior"] else Graph()
    res = gate.gate(g, fx["writeSet"])
    exp, checks, got = fx["expected"], [], {}
    got["outcome"] = type(res).__name__
    checks.append(("outcome", exp["outcome"], got["outcome"]))
    if isinstance(res, Reject):
        got["code"] = res.code; got["detail"] = res.detail; got["step"] = res.step
        if "code" in exp: checks.append(("code", exp["code"], res.code))
        if "shapesRan" in exp: checks.append(("shapesRan", exp["shapesRan"], res.shapes_ran))
        if res.code is not None and res.code not in ERROR_VOCABULARY: checks.append(("code∈§5.4", True, False))
    else:
        got.update(computedStatus={short(k): v for k, v in res.computed_status.items()},
                   computedRegister={short(k): v for k, v in res.computed_register.items()},
                   stale=[short(s) for s in res.stale], shapeVersions={short(k): v for k, v in res.shape_versions.items()},
                   propagationSeconds=res.propagation_seconds)
        for k, v in exp.get("computedStatus", {}).items(): checks.append((f"computedStatus {k}", v, got["computedStatus"].get(k)))
        for k in exp.get("computedStatusAbsent", []):
            checks.append((f"computedStatus {k} absent", True, g.value(iri(k), TCF.computedStatus) is None))
            got[f"computedStatus {k}"] = str(g.value(iri(k), TCF.computedStatus))
        for k, v in exp.get("witness", {}).items(): checks.append((f"witness {k}", v, witness(g, iri(k))))
        if "stale" in exp: checks.append(("stale", exp["stale"], got["stale"]))
        for k, v in exp.get("reportComponent", {}).items():
            doc = gate.report_store.get(res.reports[str(iri(k))])
            checks.append((f"report {k} has {v}", True, any(e["component"] == v for e in doc["results"])))
        for k, v in exp.get("reportViolations", {}).items():
            doc = gate.report_store.get(res.reports[str(iri(k))])
            checks.append((f"report {k} violations", v, sum(e["severity"] == "sh:Violation" for e in doc["results"])))
        for k, v in exp.get("reportEntry", {}).items():
            doc = gate.report_store.get(res.reports[str(iri(k))])
            checks.append((f"report {k} entry", v, [{"constraintClass": e["constraintClass"], "severity": e["severity"]} for e in doc["results"]
                            if e["constraintClass"] == v["constraintClass"]][:1] and
                           [{"constraintClass": e["constraintClass"], "severity": e["severity"]} for e in doc["results"] if e["constraintClass"] == v["constraintClass"]][0]))
        for tier, want in exp.get("quarkViolations", {}).items():
            root = iri(fx["writeSet"][0]["id"])
            qv = tcf_quark_violations(g, gate.report_store, root, tier)["violationSummary"]
            for kk, vv in want.items(): checks.append((f"tcfQuarkViolations@{tier}.{kk}", vv, qv[kk]))
        for k, v in exp.get("computedRegister", {}).items(): checks.append((f"computedRegister {k}", v, got["computedRegister"].get(k)))
        if "blockingEntries" in exp:
            root = iri(fx["writeSet"][0]["id"])
            checks.append(("blocking entries", exp["blockingEntries"],
                           tcf_quark_violations(g, gate.report_store, root, "particle")["violationSummary"]["blocking"]))
        for k, v in exp.get("shapeVersionUsed", {}).items(): checks.append((f"shapeVersion {k}", v, got["shapeVersions"].get(k)))
        if "evidenceDecay" in exp:
            got["evidenceDecay"] = evidence_decay(g, iri("tcf:C1"))
            checks.append(("evidenceDecay", exp["evidenceDecay"], got["evidenceDecay"]))
            if "rerun" in exp:
                r2 = gate.gate(g, exp["rerun"]["writeSet"])
                got["evidenceDecay2"] = evidence_decay(g, iri("tcf:C1"))
                checks.append(("evidenceDecay (rerun)", exp["rerun"]["evidenceDecay"], got["evidenceDecay2"]))
    ok = all(str(e) == str(a) for _, e, a in checks)
    return ok, checks, got

# Red rows whose divergence is a logged finding (plan §9). B-6 done-when: full table
# green OR every red row logged. The fixture itself is never edited.
LOGGED_FINDINGS = {"F-05a": "BF-5 — §5.2 step order: Family B (step 2) rejects confirmed-without-record before step 3 runs"}

def main():
    rows, all_ok, codes_reached, supp_codes = [], True, set(), set()
    fx_flags = {}
    for path in sorted(glob.glob("fixtures/F-*.json")):
        fx = json.load(open(path))
        ok, checks, got = run(fx)
        if got.get("code") and not fx.get("supplementary"): codes_reached.add(got["code"])
        if got.get("code") and fx.get("supplementary"): supp_codes.add(got["code"])
        if not ok and not fx.get("optional") and fx["id"] not in LOGGED_FINDINGS: all_ok = False
        fx_flags[fx["id"]] = fx.get("optional") or fx.get("supplementary")
        rows.append(dict(id=fx["id"], ok=ok, optional=fx.get("optional", False), checks=checks, got=got, specRef=fx["specRef"]))
    print(f"{'ID':<10} {'result':<8} {'expected → got (first divergence, or summary)'}")
    for r in rows:
        div = [c for c in r["checks"] if str(c[1]) != str(c[2])]
        tag = ("GREEN" if r["ok"] else "RED") + ("*" if fx_flags.get(r["id"]) else "")
        msg = (f"{div[0][0]}: expected {div[0][1]!r}, got {div[0][2]!r}" if div
               else "; ".join(f"{c[0]}={c[2]!r}" for c in r["checks"][:3]))
        if r["got"].get("propagationSeconds") is not None and r["id"] == "F-12":
            msg += f"  [§7.3 on F-12: {r['got']['propagationSeconds']*1000:.2f} ms]"
        if not r["ok"] and r["id"] in LOGGED_FINDINGS:
            tag = "RED†"; msg += f"  [logged: {LOGGED_FINDINGS[r['id']].split(' — ')[0]}]"
        print(f"{r['id']:<10} {tag:<8} {msg}")
    missing = set(ERROR_VOCABULARY) - codes_reached
    print(f"\n§5.4 codes reached by plan fixtures: {len(codes_reached)}/6" + (f"  MISSING: {sorted(missing)}" if missing else "")
          + (f"\n  reached only by supplementary fixture F-05a-supp (ratified D-6a; counts toward §8.1): {sorted(supp_codes - codes_reached)}" if supp_codes - codes_reached else ""))
    os.makedirs("records", exist_ok=True)
    json.dump(dict(rows=rows, codesReached=sorted(codes_reached)), open("records/fixture-results.json", "w"), indent=2, default=str)
    print("legend: GREEN* optional/supplementary · RED† divergence logged as finding (fixture unmodified)")
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
