"""§6 validation report store (C-5): per-node sh:ValidationReport, serialized
deterministically and content-addressed; tcf:validationReport on the node = digest.
Also the tcfQuarkViolations filter — exposed for later PC#9 use; NOT called by any
Phase 0 gate step (plan C-5)."""
import hashlib
import json
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import SH

from ..shapes.library import TCF
from .graphs import descendants, tier_of, TIER_ORDER


def _shape_annotations(shapes_graph, shape, _depth=0):
    """quarkId/constraintClass of the shape, or of the nearest enclosing NodeShape
    (results on nested property/or/node shapes report the inner shape)."""
    q = shapes_graph.value(shape, TCF.quarkId)
    c = shapes_graph.value(shape, TCF.constraintClass)
    if q is not None or c is not None or _depth > 6:
        return (str(q) if q is not None else None, str(c) if c is not None else None)
    for parent in shapes_graph.subjects(None, shape):
        r = _shape_annotations(shapes_graph, parent, _depth + 1)
        if r != (None, None):
            return r
    return (None, None)


def per_node_reports(results_graph, shapes_graph, nodes):
    """Split a pyshacl results graph into per-node report objects (JSON, sorted)."""
    reports = {str(n): [] for n in nodes}
    for r in results_graph.subjects(SH.sourceConstraintComponent, None):
        focus = results_graph.value(r, SH.focusNode)
        if focus is None or str(focus) not in reports:
            continue
        shape = results_graph.value(r, SH.sourceShape)
        # Nested (sh:node / sh:or) results report the inner shape; walk up via the
        # top-level shape's annotations when the inner one carries none.
        quark, cclass = _shape_annotations(shapes_graph, shape) if shape is not None else (None, None)
        sev = results_graph.value(r, SH.resultSeverity)
        path = results_graph.value(r, SH.resultPath)
        msg = results_graph.value(r, SH.resultMessage)
        comp = results_graph.value(r, SH.sourceConstraintComponent)
        reports[str(focus)].append({
            "sourceShape": str(shape) if shape is not None else None,
            "quarkId": quark, "constraintClass": cclass,
            "severity": "sh:" + str(sev).rsplit("#", 1)[-1] if sev is not None else None,
            "component": str(comp).rsplit("#", 1)[-1] if comp is not None else None,
            "path": str(path) if path is not None else None,
            "message": str(msg) if msg is not None else None,
        })
    for k in reports:
        reports[k].sort(key=lambda e: json.dumps(e, sort_keys=True))
    return reports


class ReportStore:
    """digest -> report document. Reproducible: same shapes + same node -> same digest."""
    def __init__(self):
        self.reports = {}

    def put(self, node_id, shape_version, entries):
        doc = {"@type": "sh:ValidationReport", "focusNode": node_id,
               "shapeVersion": shape_version, "conforms": not any(
                   e["severity"] == "sh:Violation" for e in entries), "results": entries}
        raw = json.dumps(doc, sort_keys=True, separators=(",", ":")).encode("utf-8")
        digest = "sha256:" + hashlib.sha256(raw).hexdigest()
        self.reports[digest] = doc
        return digest

    def get(self, digest):
        return self.reports[digest]


def tcf_quark_violations(g, store, root, minimum_tcf_tier):
    """§6 filter: reports of root + descendants -> tcfQuarkViolations + violationSummary.
    Blocking iff severity = sh:Violation AND tier >= minimumTcfTier. Register-class
    entries are always sh:Warning at this shape version (KL-4)."""
    min_idx = TIER_ORDER.index(minimum_tcf_tier.capitalize())
    entries, blocking, recorded = [], 0, 0
    for n in [root] + sorted(descendants(g, root)):
        digest = g.value(n, TCF.validationReport)
        if digest is None:
            continue
        doc = store.get(str(digest))
        tier = tier_of(g, n)
        for e in doc["results"]:
            sev = "sh:Warning" if e["constraintClass"] == "register" else e["severity"]
            is_blocking = sev == "sh:Violation" and TIER_ORDER.index(tier) >= min_idx
            entries.append({"nodeId": str(n), "quarkId": e["quarkId"],
                            "constraintClass": e["constraintClass"], "severity": sev,
                            "tier": tier.lower(), "message": e["message"],
                            "shapeVersion": doc["shapeVersion"], "reportDigest": str(digest)})
            if is_blocking:
                blocking += 1
            else:
                recorded += 1
    return {"tcfQuarkViolations": entries,
            "violationSummary": {"blocking": blocking, "recorded": recorded, "acknowledged": 0}}
