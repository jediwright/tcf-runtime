"""B-1 / B-2 done-when checks (plan §7). Exit 0 iff all pass."""
import os, re, sys
from rdflib import Graph
from runtime.store.adapters.file import FileStoreAdapter
from runtime.store.model import StoreInvalid
from runtime.shapes.library import load_library, admit, ShapeNotAdmitted, shape_iri

results = []
def check(label, fn):
    try:
        out = fn(); results.append((label, "PASS", out))
    except AssertionError as e:
        results.append((label, "FAIL", str(e)))
    except Exception as e:
        results.append((label, "FAIL", f"{type(e).__name__}: {e}"))

def b1_distinct():
    ad = FileStoreAdapter("fixtures/stores")
    a = ad.load("https://jediwright.github.io/tcf-runtime/vocab/tcf/2026-09-11").verify()
    b = ad.load("https://jediwright.github.io/tcf-runtime/vocab/tcf/2026-09-11-b").verify()
    assert a.versionDigest != b.versionDigest, "v-A and v-B digests identical"
    return f"v-A {a.versionDigest[:19]}…  v-B {b.versionDigest[:19]}…"

def b1_f07():
    ad = FileStoreAdapter("fixtures/stores/corrupt")
    doc = ad.load("https://jediwright.github.io/tcf-runtime/vocab/tcf/2026-09-11")
    try:
        doc.verify()
    except StoreInvalid as e:
        assert e.code == "E-STORE-INVALID"
        return "corrupt v-A refused with E-STORE-INVALID (F-07 prior state)"
    raise AssertionError("corrupt store verified")

def b1_no_direct_import():
    bad = []
    for root, _, files in os.walk("runtime/gate"):
        for f in files:
            if f.endswith(".py"):
                src = open(os.path.join(root, f)).read()
                if re.search(r"store\.adapters", src): bad.append(f)
    assert not bad, f"gate imports a concrete adapter: {bad}"
    return "runtime/gate imports no concrete adapter"

def b2_loads():
    ad = FileStoreAdapter("fixtures/stores")
    g = load_library(ad.load(ad.current_version()).verify())
    n = len(list(g.subjects()))
    assert n > 0
    return f"library admitted at v-A ({len(g)} triples)"

def b2_refuses():
    ad = FileStoreAdapter("fixtures/stores")
    doc = ad.load(ad.current_version()).verify()
    shapes = dict(doc.shapes)
    k = shape_iri("PlainRegisterTerminologyShape")
    shapes[k] = "\n".join(l for l in shapes[k].splitlines() if "tcf:quarkId" not in l)
    try:
        admit(shapes)
    except ShapeNotAdmitted as e:
        return f"Family A shape without tcf:quarkId refused: {str(e)[-40:]}"
    raise AssertionError("shape lacking tcf:quarkId was admitted")

def b2_single_source():
    hits = []
    for root, _, files in os.walk("runtime"):
        for f in files:
            if f.endswith(".py") and f != "status_rank.py":
                src = open(os.path.join(root, f)).read()
                if re.search(r'"(confirmed|time-sensitive|inferred|unverified)"\s+[0-3]\b', src):
                    hits.append(f)
    assert not hits, f"status order literal outside status_rank.py: {hits}"
    return "STATUS_RANK is the only literal order in runtime/"

for label, fn in [("B-1 v-A/v-B load, distinct digests", b1_distinct), ("B-1 F-07 prior state rejects", b1_f07),
                  ("B-1 no direct adapter import in gate", b1_no_direct_import),
                  ("B-2 library loads at v-A", b2_loads), ("B-2 admission refuses missing quarkId", b2_refuses),
                  ("B-2/§8.4 single source of order", b2_single_source)]:
    check(label, fn)
w = max(len(r[0]) for r in results)
for label, st, out in results: print(f"{label:<{w}}  {st}  {out}")
sys.exit(0 if all(r[1]=="PASS" for r in results) else 1)
