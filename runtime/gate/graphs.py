"""Content-graph helpers: JSON-LD (store context) <-> rdflib, node replacement, ancestry."""
import json
from rdflib import Graph, URIRef, Literal, BNode, RDF
from rdflib.namespace import XSD

from ..shapes.library import TCF, TCF_BASE

TIER_ORDER = ["Particle", "Cluster", "Zone", "Structure", "Ecosystem", "Biome"]
TIER_CLASS = {t: TCF[t] for t in TIER_ORDER}
COMPOSITE_TIERS = TIER_ORDER[1:]


def nodes_to_graph(nodes, context):
    """Parse a list of JSON-LD node objects (compact form, store context) into a Graph."""
    doc = {"@context": context, "@graph": nodes}
    g = Graph()
    g.parse(data=json.dumps(doc), format="json-ld")
    return g


def node_iri(node_id):
    return URIRef(node_id if node_id.startswith("http") else TCF_BASE + node_id)


def tier_of(g, n):
    for t in TIER_ORDER:
        if (n, RDF.type, TIER_CLASS[t]) in g:
            return t
    return None


def subtree_triples(g, n):
    """Triples of node n plus its blank-node-rooted records (one level of nesting)."""
    out = set()
    for s, p, o in g.triples((n, None, None)):
        out.add((s, p, o))
        if isinstance(o, BNode):
            out.update(g.triples((o, None, None)))
    return out


def replace_node(g, src, n):
    """Remove n's triples (and its blank-node records) from g, then copy n's subtree from src."""
    for t in list(subtree_triples(g, n)):
        g.remove(t)
    for t in subtree_triples(src, n):
        g.add(t)


def ancestors(g, nodes):
    """All composite nodes that transitively list any of `nodes` in tcf:members."""
    seen, frontier = set(), list(nodes)
    while frontier:
        n = frontier.pop()
        for parent in g.subjects(TCF.members, n):
            if parent not in seen:
                seen.add(parent)
                frontier.append(parent)
    return seen


def descendants(g, n):
    seen, frontier = set(), [n]
    while frontier:
        x = frontier.pop()
        for m in g.objects(x, TCF.members):
            if m not in seen:
                seen.add(m)
                frontier.append(m)
    return seen


def lit(g, n, pred):
    v = g.value(n, pred)
    return str(v) if v is not None else None
