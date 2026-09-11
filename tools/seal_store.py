"""Author-side tool: generate the Phase 0 stores v-A and v-B and seal their digests.
Never run by the gate. Usage: python -m tools.seal_store [outdir]"""
import json, os, sys
from runtime.shapes.library import build_shapes, build_quarks, build_context
from runtime.store.model import StoreDocument

VOCAB = "https://jediwright.github.io/tcf-runtime/vocab/tcf/"
STORE_ID = "urn:tcf:quark-store:did:web:jediwright.github.io"


def make(version, **kw):
    return StoreDocument(STORE_ID, VOCAB + version,
                         build_quarks(VOCAB + version, plain_register_v2=kw.get("v2", False)),
                         build_shapes(kw.get("fa")), build_context()).seal()


def main(outdir="fixtures/stores"):
    os.makedirs(outdir, exist_ok=True)
    va = make("2026-09-11")
    vb = make("2026-09-11-b", v2=True,
              fa=(r"^(?!.*\b(substrate|floor|stack|pipeline)\b).*$", "q\\/terminology\\/plain-register-v2"))
    for name, doc in (("store-vA.json", va), ("store-vB.json", vb)):
        with open(os.path.join(outdir, name), "w", encoding="utf-8") as f:
            json.dump(doc.to_dict(), f, indent=2, ensure_ascii=False, sort_keys=True)
        print(name, doc.tcfShapeVersion, doc.versionDigest)
    # F-07 prior state: v-A with versionDigest hand-edited (last hex char flipped)
    bad = va.to_dict()
    bad["versionDigest"] = bad["versionDigest"][:-1] + ("0" if bad["versionDigest"][-1] != "0" else "1")
    os.makedirs(os.path.join(outdir, "corrupt"), exist_ok=True)
    with open(os.path.join(outdir, "corrupt", "store-vA-corrupt.json"), "w", encoding="utf-8") as f:
        json.dump(bad, f, indent=2, ensure_ascii=False, sort_keys=True)
    print("corrupt/store-vA-corrupt.json (F-07) digest hand-edited")


if __name__ == "__main__":
    main(*sys.argv[1:])
