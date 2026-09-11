"""C-3 — the write-time epistemic status gate

BF-3 (engine limit, fixed in build): pyshacl 0.40.1's `focus_nodes=` option mis-evaluates
sh:or branches containing sh:not/sh:hasValue (Family B rejects a conforming Particle).
The gate therefore validates the whole candidate graph and filters results by focus
node via per_node_reports(). Phase 1 note: re-check before relying on focus_nodes. (runtime spec §5.2 steps 1–8, in order).

gate(adapter, graph, write_set) -> Accept | Reject. Error vocabulary is exactly §5.4;
the build adds no codes. A refusal with no §5.4 code is surfaced as Reject(code=None)
and is a finding, never a new code. Store access goes through StoreAdapter only.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import pyshacl
from rdflib import Graph, Literal, RDF, URIRef
from rdflib.namespace import SH, XSD

from ..shapes.library import TCF, load_library, shape_iri
from ..shapes.status_rank import rank
from ..store.adapter import Change, StoreAdapter
from ..store.model import StoreInvalid
from .graphs import ancestors, node_iri, nodes_to_graph, replace_node, tier_of
from .propagation import propagate_register, propagate_status
from .reports import ReportStore, per_node_reports

E_STORE_INVALID = "E-STORE-INVALID"
E_STATUS_VOCAB = "E-STATUS-VOCAB"
E_CONFIRMED_NO_RECORD = "E-CONFIRMED-NO-RECORD"
E_TIMESENSITIVE_NO_VALIDITY = "E-TIMESENSITIVE-NO-VALIDITY"
E_UPGRADE_WITHOUT_VERIFICATION = "E-UPGRADE-WITHOUT-VERIFICATION"
E_DERIVATION_EXCEEDS_INPUT = "E-DERIVATION-EXCEEDS-INPUT"
ERROR_VOCABULARY = (E_STORE_INVALID, E_STATUS_VOCAB, E_CONFIRMED_NO_RECORD,
                    E_TIMESENSITIVE_NO_VALIDITY, E_UPGRADE_WITHOUT_VERIFICATION,
                    E_DERIVATION_EXCEEDS_INPUT)


@dataclass
class Reject:
    code: Optional[str]           # a §5.4 code, or None (= finding: refusal with no code)
    detail: str
    step: int
    shapes_ran: bool


@dataclass
class Accept:
    change: Change
    shape_versions: Dict[str, str]          # node id -> version validated against
    computed_status: Dict[str, str] = field(default_factory=dict)
    computed_register: Dict[str, str] = field(default_factory=dict)
    stale: List[str] = field(default_factory=list)
    reports: Dict[str, str] = field(default_factory=dict)   # node id -> report digest
    propagation_seconds: float = 0.0


class Gate:
    def __init__(self, adapter: StoreAdapter, report_store: Optional[ReportStore] = None):
        self.adapter = adapter
        self.report_store = report_store or ReportStore()
        self._libraries = {}      # version IRI -> (StoreDocument, shapes Graph)

    # ---- step 1 -----------------------------------------------------------------------
    def _library(self, version):
        if version not in self._libraries:
            doc = self.adapter.load(version).verify()       # StoreInvalid propagates
            self._libraries[version] = (doc, load_library(doc))
        return self._libraries[version]

    def _pinned_version(self, graph, n):
        pin = graph.value(n, TCF.shapeVersion)
        return str(pin) if pin is not None else self.adapter.current_version()

    # ---- entry point --------------------------------------------------------------------
    def gate(self, graph: Graph, write_set: list) -> "Accept | Reject":
        # The write set is parsed against the CURRENT store's context; if step 1 refuses
        # that store, no shape has run yet (F-07 asserts this ordering).
        try:
            cur_doc, _ = self._library(self.adapter.current_version())
        except StoreInvalid as e:
            return Reject(E_STORE_INVALID, e.detail, 1, shapes_ran=False)
        ws = nodes_to_graph(write_set, cur_doc.context)
        ws_nodes = [n for n in set(ws.subjects(RDF.type, None)) if tier_of(ws, n)]

        # 1. pinned library per node (existing node: its tcf:shapeVersion; new: current)
        versions = {}
        for n in ws_nodes:
            v = self._pinned_version(graph, n)
            try:
                self._library(v)
            except StoreInvalid as e:
                return Reject(E_STORE_INVALID, e.detail, 1, shapes_ran=False)
            versions[str(n)] = v

        # candidate graph = prior state with the write set applied
        cand = Graph()
        for t in graph:
            cand.add(t)
        for n in ws_nodes:
            replace_node(cand, ws, n)
            if (n, TCF.shapeVersion, None) not in cand:
                cand.add((n, TCF.shapeVersion, URIRef(versions[str(n)])))

        results = {}   # node -> list of report entries, accumulated across steps

        # 2. Family B on Particles in the write set (per pinned version)
        particles = [n for n in ws_nodes if tier_of(ws, n) == "Particle"]
        for n in particles:
            doc, shapes = self._library(versions[str(n)])
            fam_b = _sub_shapes(shapes, [shape_iri("EpistemicStatusShape"),
                                          shape_iri("VerificationRecordShape"),
                                          shape_iri("TemporalValidityShape"),
                                          shape_iri("DerivationRecordShape")])
            conforms, rg, _ = pyshacl.validate(cand, shacl_graph=fam_b, advanced=True,
                                               inference="none")   # BF-3: no focus_nodes
            entries = per_node_reports(rg, fam_b, [n])[str(n)]
            results.setdefault(str(n), []).extend(entries)
            viol = [e for e in entries if e["severity"] == "sh:Violation"]
            if viol:
                return Reject(_family_b_code(cand, n, viol), _fmt(viol), 2, shapes_ran=True)

        # 3. upgrade rule
        for n in particles:
            old = graph.value(n, TCF.epistemicStatus)
            new = cand.value(n, TCF.epistemicStatus)
            if old is None or new is None:
                continue
            ro, rn = rank(str(old)), rank(str(new))
            if ro is None or rn is None or rn <= ro:
                continue                                    # decrease never needs a record
            new_rec = ws.value(n, TCF.verificationRecord)
            old_rec = graph.value(n, TCF.verificationRecord)
            if new_rec is None:
                return Reject(E_UPGRADE_WITHOUT_VERIFICATION,
                              f"{n} {old} -> {new} with no verificationRecord in write set", 3, True)
            new_at = ws.value(new_rec, TCF.verifiedAt)
            # "previous status timestamp": §2.4 defines no such field; the build reads the
            # prior verificationRecord.verifiedAt when present, else no lower bound (BF-4).
            old_at = graph.value(old_rec, TCF.verifiedAt) if old_rec is not None else None
            if new_at is None or (old_at is not None and str(new_at) < str(old_at)):
                return Reject(E_UPGRADE_WITHOUT_VERIFICATION,
                              f"{n}: verifiedAt {new_at} not >= prior {old_at}", 3, True)
            if old_rec is not None and _record_equal(graph, old_rec, ws, new_rec):
                return Reject(E_UPGRADE_WITHOUT_VERIFICATION,
                              f"{n}: verificationRecord is neither new nor updated", 3, True)

        # 4. derivation rule
        for n in particles:
            rec = cand.value(n, TCF.derivationRecord)
            if rec is None:
                continue
            new = cand.value(n, TCF.epistemicStatus)
            inputs = list(cand.objects(rec, TCF.derivedFrom))
            ranks = [rank(str(cand.value(m, TCF.epistemicStatus))) for m in inputs]
            ranks = [r for r in ranks if r is not None]
            if ranks and rank(str(new)) is not None and rank(str(new)) > min(ranks):
                return Reject(E_DERIVATION_EXCEEDS_INPUT,
                              f"{n} rank {rank(str(new))} > min input rank {min(ranks)}", 4, True)

        # 5. recompute propagation for every composite ancestor of the write set
        anc = ancestors(cand, ws_nodes) | {n for n in ws_nodes if tier_of(ws, n) != "Particle"}
        computed, secs = propagate_status(cand, targets=anc)
        computed_reg = propagate_register(cand, targets=anc)

        # 6. Family C on those ancestors — annotate stale; never reject
        stale = []
        for n in sorted(anc, key=str):
            v = self._pinned_version(cand, n)
            doc, shapes = self._library(v)
            fam_c = _sub_shapes(shapes, [shape_iri("PropagationShape")])
            _, rg, _ = pyshacl.validate(cand, shacl_graph=fam_c, advanced=True,
                                        inference="none")   # BF-3
            entries = per_node_reports(rg, fam_c, [n])[str(n)]
            results.setdefault(str(n), []).extend(entries)
            cand.remove((n, TCF.statusStale, None))
            if any(e["component"] == "SPARQLConstraintComponent" for e in entries):
                cand.add((n, TCF.statusStale, Literal(True)))
                stale.append(str(n))

        # 7. Family A on the write set — recorded, never rejecting
        for n in ws_nodes:
            doc, shapes = self._library(versions[str(n)])
            fam_a = _family_a(shapes)
            if len(fam_a) == 0:
                continue
            _, rg, _ = pyshacl.validate(cand, shacl_graph=fam_a, advanced=True,
                                        inference="none")   # BF-3
            results.setdefault(str(n), []).extend(per_node_reports(rg, fam_a, [n])[str(n)])

        # 8. commit: write set + computed fields + reports, as one change
        touched = set(str(n) for n in ws_nodes) | set(str(n) for n in anc)
        report_digests = {}
        for nid in sorted(touched):
            n = URIRef(nid)
            ver = self._pinned_version(cand, n)
            d = self.report_store.put(nid, ver, results.get(nid, []))
            cand.remove((n, TCF.validationReport, None))
            cand.add((n, TCF.validationReport, Literal(d)))
            report_digests[nid] = d
        ops = []
        for nid in sorted(touched):
            n = URIRef(nid)
            node_triples = sorted((str(p), str(o)) for _, p, o in cand.triples((n, None, None)))
            ops.append({"op": "replace" if (n, None, None) in graph else "add",
                        "path": "/nodes/" + nid.rsplit("#", 1)[-1], "value": node_triples})
        change = Change(ops=ops, reports=report_digests)
        # apply to the live graph
        for n in sorted(touched):
            replace_node(graph, cand, URIRef(n))
        self.adapter.commit(change)
        return Accept(change=change, shape_versions=versions,
                      computed_status={str(k): v for k, v in computed.items()},
                      computed_register={str(k): v for k, v in computed_reg.items()},
                      stale=stale, reports=report_digests, propagation_seconds=secs)


# ---- helpers ------------------------------------------------------------------------------
def _sub_shapes(shapes: Graph, roots):
    """Closure of the named shapes over their blank-node structure and sh:node references."""
    out, frontier, seen = Graph(), [URIRef(r) for r in roots], set()
    for pfx, ns in shapes.namespaces():
        out.bind(pfx, ns)
    while frontier:
        s = frontier.pop()
        if s in seen:
            continue
        seen.add(s)
        for t in shapes.triples((s, None, None)):
            out.add(t)
            o = t[2]
            if not isinstance(o, Literal):
                frontier.append(o)
    return out


def _family_a(shapes: Graph):
    roots = [s for s in shapes.subjects(RDF.type, SH.NodeShape)
             if (s, SH.targetClass, None) in shapes
             and str(shapes.value(s, TCF.constraintClass)) not in ("epistemic",)]
    return _sub_shapes(shapes, roots)


def _family_b_code(cand, n, violations):
    status = cand.value(n, TCF.epistemicStatus)
    for e in violations:
        if e["component"] == "InConstraintComponent" and e["path"] == str(TCF.epistemicStatus):
            return E_STATUS_VOCAB
    for e in violations:
        if e["component"] == "OrConstraintComponent":
            if str(status) == "confirmed":
                return E_CONFIRMED_NO_RECORD
            if str(status) == "time-sensitive":
                return E_TIMESENSITIVE_NO_VALIDITY
    if status is None:
        return E_STATUS_VOCAB     # minCount 1 on epistemicStatus: status outside vocabulary (absent)
    return None                   # Family B violation with no §5.4 code -> finding


def _fmt(entries):
    return "; ".join(f'{e["component"]}@{(e["path"] or "").rsplit("#",1)[-1]}' for e in entries)


def _record_equal(g1, r1, g2, r2):
    a = sorted((str(p), str(o)) for _, p, o in g1.triples((r1, None, None)))
    b = sorted((str(p), str(o)) for _, p, o in g2.triples((r2, None, None)))
    return a == b
