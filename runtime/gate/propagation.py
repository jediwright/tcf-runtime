"""§7 propagation — computed, not reasoned. §7.3 CONSTRUCT run once per composite tier
in order (six passes bound the computation); §7.4 register propagation; §7.5 evidenceDecay.
Absent status yields absent computedStatus: no default is inserted (§7.3 'silence')."""
import time
from rdflib import Graph, Literal, RDF

from ..shapes.library import TCF, TCF_BASE
from ..shapes.status_rank import values_table, REGISTER_RANK, register_rank, rank
from .graphs import COMPOSITE_TIERS, TIER_CLASS, TIER_ORDER


def construct_query(tier_class):
    """Spec §7.3 with (i) VALUES tables generated from STATUS_RANK, (ii) tier targeting,
    (iii) the BF-6 silence guard (D-6b). Queued to runtime v0.2."""
    return f"""
PREFIX tcf: <{TCF_BASE}>
CONSTRUCT {{ ?n tcf:computedStatus ?weakest }}
WHERE {{
  {{
    SELECT ?n (MIN(?rank) AS ?minRank) WHERE {{
      ?n a <{tier_class}> ; tcf:members ?m .
      OPTIONAL {{ ?m a tcf:Particle ; tcf:epistemicStatus ?s1 }}
      OPTIONAL {{ ?m tcf:computedStatus ?s2 }}
      BIND( COALESCE(?s1, ?s2) AS ?status )
      # BF-6 / D-6b(a): silence guard. Spec §7.3 says a statusless member yields an
      # absent computedStatus; under standard SPARQL an unbound ?status is join-
      # compatible with every VALUES row and inserts rank 0. Drop the composite instead.
      FILTER( BOUND(?status) )
      FILTER NOT EXISTS {{ ?n tcf:members ?x .
          FILTER NOT EXISTS {{ ?x tcf:epistemicStatus ?a }}
          FILTER NOT EXISTS {{ ?x tcf:computedStatus ?b }} }}
      {values_table("?status", "?rank")}
    }} GROUP BY ?n
  }}
  {values_table("?weakest", "?minRank")}
}}
"""


def propagate_status(g, targets=None):
    """Run the §7.3 CONSTRUCT per composite tier, bottom-up. Writes tcf:computedStatus
    on every composite (or only `targets` if given). Returns (written: dict, seconds)."""
    t0 = time.perf_counter()
    written = {}
    for tier in COMPOSITE_TIERS:
        cls = TIER_CLASS[tier]
        composites = set(g.subjects(RDF.type, cls))
        if targets is not None:
            composites &= set(targets)
        if not composites:
            continue
        # Remove prior computed values on the nodes we are about to (re)compute so a
        # node whose members lost status becomes ABSENT rather than stale.
        for n in composites:
            g.remove((n, TCF.computedStatus, None))
        produced = g.query(construct_query(cls)).graph
        for n, _, v in produced.triples((None, TCF.computedStatus, None)):
            if n in composites:
                g.add((n, TCF.computedStatus, v))
                written[n] = str(v)
    return written, time.perf_counter() - t0


def propagate_register(g, targets=None):
    """§7.4: computedRegister(N) = most restrictive over members (Particle: tcf:register;
    composite: tcf:computedRegister). Computed and recorded; enforces nothing (KL-4)."""
    written = {}
    for tier in COMPOSITE_TIERS:
        composites = set(g.subjects(RDF.type, TIER_CLASS[tier]))
        if targets is not None:
            composites &= set(targets)
        for n in composites:
            g.remove((n, TCF.computedRegister, None))
            best = None
            for m in g.objects(n, TCF.members):
                r = g.value(m, TCF.register) if (m, RDF.type, TCF.Particle) in g else g.value(m, TCF.computedRegister)
                rr = register_rank(str(r)) if r is not None else None
                if rr is not None and (best is None or rr > best):
                    best = rr
            if best is not None:
                val = next(k for k, v in REGISTER_RANK.items() if v == best)
                g.add((n, TCF.computedRegister, Literal(val)))
                written[n] = val
    return written


def evidence_decay(g, n):
    """§7.5, pure function over store fields. Returns an ISO date/dateTime string or None."""
    cs = g.value(n, TCF.computedStatus)
    cs = str(cs) if cs is not None else None
    members = list(g.objects(n, TCF.members))
    if cs == "time-sensitive":
        vals = []
        for m in members:
            st = g.value(m, TCF.epistemicStatus) if (m, RDF.type, TCF.Particle) in g else g.value(m, TCF.computedStatus)
            if st is not None and str(st) == "time-sensitive":
                tv = g.value(m, TCF.temporalValidity)
                vu = g.value(tv, TCF.validUntil) if tv is not None else None
                if vu is not None:
                    vals.append(str(vu))
        return min(vals) if vals else None
    if cs == "confirmed":
        vals = []
        for m in members:
            vr = g.value(m, TCF.verificationRecord)
            rw = g.value(vr, TCF.recencyWindowEnd) if vr is not None else None
            if rw is not None:
                vals.append(str(rw))
        return min(vals) if vals else None
    declared = g.value(n, TCF.evidenceDecay)
    return str(declared) if declared is not None else None
