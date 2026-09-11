"""B-0 probe — TCF runtime Phase 0 (plan v0.1.2 §7 B-0).

Runs Family C (runtime spec §3.4) against a hand-built F-09 graph OUTSIDE the gate.
PASS: the sh:sparql constraint fires (sh:Violation, sh:SPARQLConstraintComponent) on C1.
Namespace base per plan v0.1.2, not spec §0.

Two build findings are embodied here (see build record BF-1, BF-2):
  BF-1  Turtle local names containing '/' (tcf:sh/…, tcf:q/…) must be escaped as '\\/'.
        IRIs unchanged. Serialization fix only.
  BF-2  W3C SHACL §5.3.2 forbids VALUES inside sh:select. Spec §7.2's "inline the
        VALUES table" instruction is therefore not valid SHACL-SPARQL. The rank lookup
        is generated from STATUS_RANK as a nested IF() instead — same semantics
        (unmatched value -> unbound -> FILTER fails). VALUES remains valid in the
        §7.3 CONSTRUCT (plain SPARQL) and is generated there from the same constant.
"""
import sys
import pyshacl
import rdflib
from rdflib import Graph, Namespace

TCF = "https://jediwright.github.io/tcf-runtime/vocab/tcf#"

# The ONLY place the status order appears in source (plan §5; ~ KL-11).
STATUS_RANK = {"confirmed": 3, "time-sensitive": 2, "inferred": 1, "unverified": 0}


def rank_expr(var):
    """SHACL-SPARQL-safe rank lookup, generated from STATUS_RANK (BF-2)."""
    expr = "?__unbound"
    for status, rank in reversed(list(STATUS_RANK.items())):
        expr = f'IF({var}="{status}",{rank},{expr})'
    return expr


def values_table(status_var="?status", rank_var="?rank"):
    """§7.2 VALUES form, for plain-SPARQL contexts (§7.3 CONSTRUCT)."""
    rows = " ".join(f'("{s}" {r})' for s, r in STATUS_RANK.items())
    return f"VALUES ({status_var} {rank_var}) {{ {rows} }}"


SHAPES = (
    "@prefix sh:  <http://www.w3.org/ns/shacl#> .\n"
    f"@prefix tcf: <{TCF}> .\n"
    "\n"
    "tcf:sh\\/PropagationShape\n"
    "    a sh:NodeShape ;\n"
    "    sh:targetClass tcf:Cluster, tcf:Zone, tcf:Structure, tcf:Ecosystem, tcf:Biome ;\n"
    "    sh:severity sh:Violation ;\n"
    "    tcf:quarkId tcf:q\\/epistemic\\/propagation-v1 ;\n"
    '    tcf:constraintClass "epistemic" ;\n'
    "    sh:property [ sh:path tcf:computedStatus ; sh:minCount 1 ; sh:maxCount 1 ] ;\n"
    "    sh:sparql [\n"
    '        sh:message "Declared status exceeds computed weakest-status of members" ;\n'
    '        sh:select """\n'
    f"            PREFIX tcf: <{TCF}>\n"
    "            SELECT $this ?declared ?computed WHERE {\n"
    "                $this tcf:epistemicStatus ?declared ; tcf:computedStatus ?computed .\n"
    f"                BIND( {rank_expr('?declared')} AS ?rd )\n"
    f"                BIND( {rank_expr('?computed')} AS ?rc )\n"
    "                FILTER( ?rd > ?rc )\n"
    "            }\n"
    '        """\n'
    "    ] .\n"
)

# Hand-built F-09 state: P8 confirmed, P9 time-sensitive, P10 inferred; C1 declared
# confirmed, computedStatus hand-set to inferred (weakest = P10). Records elided —
# B-0 runs outside the gate and Family B is not loaded here.
DATA = (
    f"@prefix tcf: <{TCF}> .\n"
    'tcf:P8  a tcf:Particle ; tcf:epistemicStatus "confirmed" .\n'
    'tcf:P9  a tcf:Particle ; tcf:epistemicStatus "time-sensitive" .\n'
    'tcf:P10 a tcf:Particle ; tcf:epistemicStatus "inferred" .\n'
    "tcf:C1  a tcf:Cluster ;\n"
    "    tcf:members tcf:P8, tcf:P9, tcf:P10 ;\n"
    '    tcf:epistemicStatus "confirmed" ;\n'
    '    tcf:computedStatus "inferred" .\n'
)


def main():
    sg = Graph().parse(data=SHAPES, format="turtle")
    dg = Graph().parse(data=DATA, format="turtle")
    conforms, rg, text = pyshacl.validate(dg, shacl_graph=sg, advanced=True, inference="none")
    print(f"pyshacl {pyshacl.__version__} | rdflib {rdflib.__version__}")
    print(text)
    SH = Namespace("http://www.w3.org/ns/shacl#")
    hits = list(rg.subjects(SH.sourceConstraintComponent, SH.SPARQLConstraintComponent))
    focus = {str(rg.value(r, SH.focusNode)) for r in hits}
    print("conforms:", conforms)
    print("sh:sparql violations:", len(hits), "focus:", focus)
    ok = (not conforms) and len(hits) == 1 and focus == {TCF + "C1"}
    print("B-0 RESULT:", "PASS — sh:sparql violation fired on C1" if ok
          else "FAIL — halt per plan §7 B-0")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
