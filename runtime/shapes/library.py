"""Shape library generator + admission check (plan C-2; runtime spec §3 verbatim).

Deviations from the spec text, all logged in the build record:
  BF-1  '/' in Turtle local names escaped as '\\/' (serialization only; IRIs unchanged).
  BF-2  Family C uses rank_expr() (nested IF) inside sh:select instead of the §7.2
        VALUES table, which W3C SHACL §5.3.2 forbids in sh:select (D-5a).
  Namespace base is the plan v0.1.2 base, not spec §0 (declared deviation).
"""
from rdflib import Graph, Namespace, RDF
from rdflib.namespace import SH

from .status_rank import rank_expr, sh_in_list

TCF_BASE = "https://jediwright.github.io/tcf-runtime/vocab/tcf#"
TCF = Namespace(TCF_BASE)
TIER_CLASSES = ("Particle", "Cluster", "Zone", "Structure", "Ecosystem", "Biome")

PREFIXES = (
    "@prefix sh:  <http://www.w3.org/ns/shacl#> .\n"
    "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n"
    f"@prefix tcf: <{TCF_BASE}> .\n\n"
)


def shape_iri(local):
    return TCF_BASE + "sh/" + local


# ---- §3.1 Family A — one illustrative shape only (RL-4) -------------------------------
def family_a_plain_register(pattern=r"^(?!.*\b(substrate|floor|stack)\b).*$", quark="q\\/terminology\\/plain-register-v1"):
    return PREFIXES + (
        "tcf:sh\\/PlainRegisterTerminologyShape\n"
        "    a sh:NodeShape ;\n"
        "    sh:targetClass tcf:Particle, tcf:Cluster ;\n"
        "    sh:severity sh:Violation ;\n"
        f"    tcf:quarkId tcf:{quark} ;\n"
        '    tcf:constraintClass "terminology" ;\n'
        "    sh:property [\n"
        "        sh:path tcf:body ;\n"
        f'        sh:pattern "{pattern.replace(chr(92), chr(92)*2)}" ;\n'
        '        sh:flags "i" ;\n'
        '        sh:message "R-1 term in plain-register content"\n'
        "    ] .\n"
    )


# ---- §3.2 Family B ------------------------------------------------------------------------
def family_b():
    return PREFIXES + (
        "tcf:sh\\/EpistemicStatusShape\n"
        "    a sh:NodeShape ;\n"
        "    sh:targetClass tcf:Particle ;\n"
        "    sh:severity sh:Violation ;\n"
        "    tcf:quarkId tcf:q\\/epistemic\\/status-v1 ;\n"
        '    tcf:constraintClass "epistemic" ;\n'
        "    sh:property [\n"
        "        sh:path tcf:epistemicStatus ;\n"
        "        sh:minCount 1 ; sh:maxCount 1 ;\n"
        f"        sh:in {sh_in_list()}\n"
        "    ] ;\n"
        '    sh:property [ sh:path tcf:claimType ; sh:minCount 1 ; sh:in ( "fact" "claim" "opinion" "policy" ) ] ;\n'
        "    sh:property [ sh:path tcf:authoritySource ; sh:minCount 1 ] ;\n"
        "    sh:or (\n"
        '        [ sh:property [ sh:path tcf:epistemicStatus ; sh:not [ sh:hasValue "confirmed" ] ] ]\n'
        "        [ sh:property [ sh:path tcf:verificationRecord ; sh:minCount 1 ; sh:node tcf:sh\\/VerificationRecordShape ] ]\n"
        "    ) ;\n"
        "    sh:or (\n"
        '        [ sh:property [ sh:path tcf:epistemicStatus ; sh:not [ sh:hasValue "time-sensitive" ] ] ]\n'
        "        [ sh:property [ sh:path tcf:temporalValidity ; sh:minCount 1 ; sh:node tcf:sh\\/TemporalValidityShape ] ]\n"
        "    ) ;\n"
        "    sh:property [ sh:path tcf:aiProvenance ; sh:maxCount 1 ] .\n"
    )


# ---- §3.3 record shapes -------------------------------------------------------------------
def record_shapes():
    return PREFIXES + (
        "tcf:sh\\/VerificationRecordShape\n"
        "    a sh:NodeShape ;\n"
        "    sh:property [ sh:path tcf:verificationMethod ; sh:minCount 1 ;\n"
        '                  sh:in ( "primary-source-read" "external-attestation" "operator-attestation" "automated-check" ) ] ;\n'
        "    sh:property [ sh:path tcf:verifiedBy ; sh:minCount 1 ] ;\n"
        "    sh:property [ sh:path tcf:verifiedAt ; sh:minCount 1 ; sh:datatype xsd:dateTime ] ;\n"
        "    sh:property [ sh:path tcf:recencyWindowEnd ; sh:minCount 1 ; sh:datatype xsd:dateTime ] ;\n"
        "    sh:property [ sh:path tcf:verificationEvidenceRef ; sh:minCount 0 ] .\n\n"
        "tcf:sh\\/DerivationRecordShape\n"
        "    a sh:NodeShape ;\n"
        "    sh:property [ sh:path tcf:derivedFrom ; sh:minCount 1 ; sh:class tcf:Particle ] ;\n"
        "    sh:property [ sh:path tcf:reasoningStep ; sh:minCount 1 ] ;\n"
        "    sh:property [ sh:path tcf:confidenceBasis ; sh:minCount 1 ] .\n\n"
        "tcf:sh\\/TemporalValidityShape\n"
        "    a sh:NodeShape ;\n"
        "    sh:property [ sh:path tcf:validFrom ; sh:minCount 1 ; sh:datatype xsd:date ] ;\n"
        "    sh:property [ sh:path tcf:validUntil ; sh:minCount 1 ; sh:datatype xsd:date ] .\n"
    )


# ---- §3.4 Family C (rank lookup generated from STATUS_RANK) --------------------------------
def family_c():
    return PREFIXES + (
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
        f"            PREFIX tcf: <{TCF_BASE}>\n"
        "            SELECT $this ?declared ?computed WHERE {\n"
        "                $this tcf:epistemicStatus ?declared ; tcf:computedStatus ?computed .\n"
        f"                BIND( {rank_expr('?declared')} AS ?rd )\n"
        f"                BIND( {rank_expr('?computed')} AS ?rc )\n"
        "                FILTER( ?rd > ?rc )\n"
        "            }\n"
        '        """\n'
        "    ] .\n"
    )


def build_shapes(family_a_variant=None):
    """shape IRI -> Turtle. family_a_variant: (pattern, quark-local) override for v-B."""
    fa = family_a_plain_register(*family_a_variant) if family_a_variant else family_a_plain_register()
    return {
        shape_iri("PlainRegisterTerminologyShape"): fa,
        shape_iri("EpistemicStatusShape"): family_b(),
        shape_iri("VerificationRecordShape"): record_shapes(),   # one file, three record shapes
        shape_iri("PropagationShape"): family_c(),
    }


def build_quarks(version_iri, plain_register_v2=False):
    q = {
        "tcf:q/epistemic/status-v1": {
            "quarkId": "tcf:q/epistemic/status-v1", "quarkClass": "epistemic",
            "appliesToTier": ["particle"], "constraintRef": "urn:tcf:shape:EpistemicStatusShape",
            "severity": "sh:Violation", "register": "governed-internal",
            "introducedIn": version_iri, "supersededBy": None, "lineageRef": None},
        "tcf:q/epistemic/propagation-v1": {
            "quarkId": "tcf:q/epistemic/propagation-v1", "quarkClass": "epistemic",
            "appliesToTier": ["cluster", "zone", "structure", "ecosystem", "biome"],
            "constraintRef": "urn:tcf:shape:PropagationShape",
            "severity": "sh:Violation", "register": "governed-internal",
            "introducedIn": version_iri, "supersededBy": None, "lineageRef": None},
        "tcf:q/terminology/plain-register-v1": {
            "quarkId": "tcf:q/terminology/plain-register-v1", "quarkClass": "terminology",
            "appliesToTier": ["particle", "cluster"],
            "constraintRef": "urn:tcf:shape:PlainRegisterTerminologyShape",
            "severity": "sh:Violation", "register": "plain",
            "introducedIn": version_iri, "supersededBy": None, "lineageRef": None},
        # Companion v0.1.1 (PC#9 v0.2.3 change-log item D), absorbed by the build (D-4):
        # declared-but-not-evaluated Quark carrying its severity; no evaluator shape.
        "tcf:q/register/grant-requirement": {
            "quarkId": "tcf:q/register/grant-requirement", "quarkClass": "register",
            "appliesToTier": ["particle", "cluster", "zone", "structure", "ecosystem", "biome"],
            "constraintRef": None, "evaluated": False,
            "severity": "sh:Warning",   # spec §6: register-class entries are sh:Warning until tcf:register promotes (KL-4)
            "register": "governed-internal",
            "introducedIn": version_iri, "supersededBy": None, "lineageRef": None},
    }
    if plain_register_v2:
        q["tcf:q/terminology/plain-register-v1"]["supersededBy"] = "tcf:q/terminology/plain-register-v2"
        q["tcf:q/terminology/plain-register-v2"] = dict(
            q["tcf:q/terminology/plain-register-v1"],
            quarkId="tcf:q/terminology/plain-register-v2", supersededBy=None, introducedIn=version_iri)
    return q


def build_context():
    """JSON-LD context for this version (§2.3 'context'); fixtures are written against it."""
    t = "tcf:"
    return {
        "@version": 1.1,
        "tcf": TCF_BASE, "sh": "http://www.w3.org/ns/shacl#", "xsd": "http://www.w3.org/2001/XMLSchema#",
        "id": "@id", "type": "@type",
        "Particle": t + "Particle", "Cluster": t + "Cluster", "Zone": t + "Zone",
        "Structure": t + "Structure", "Ecosystem": t + "Ecosystem", "Biome": t + "Biome",
        "shapeVersion": {"@id": t + "shapeVersion", "@type": "@id"},
        "epistemicStatus": t + "epistemicStatus", "computedStatus": t + "computedStatus",
        "computedRegister": t + "computedRegister", "register": t + "register",
        "statusStale": {"@id": t + "statusStale", "@type": "xsd:boolean"},
        "aiProvenance": t + "aiProvenance", "claimType": t + "claimType",
        "authoritySource": {"@id": t + "authoritySource", "@type": "@id"},
        "body": t + "body",
        "members": {"@id": t + "members", "@type": "@id", "@container": "@set"},
        "validationReport": t + "validationReport",
        "verificationRecord": t + "verificationRecord",
        "verificationMethod": t + "verificationMethod", "verifiedBy": t + "verifiedBy",
        "verifiedAt": {"@id": t + "verifiedAt", "@type": "xsd:dateTime"},
        "recencyWindowEnd": {"@id": t + "recencyWindowEnd", "@type": "xsd:dateTime"},
        "verificationEvidenceRef": {"@id": t + "verificationEvidenceRef", "@type": "@id"},
        "derivationRecord": t + "derivationRecord",
        "derivedFrom": {"@id": t + "derivedFrom", "@type": "@id", "@container": "@set"},
        "reasoningStep": t + "reasoningStep", "confidenceBasis": t + "confidenceBasis",
        "temporalValidity": t + "temporalValidity",
        "validFrom": {"@id": t + "validFrom", "@type": "xsd:date"},
        "validUntil": {"@id": t + "validUntil", "@type": "xsd:date"},
    }


# ---- admission check (§3.1 last paragraph) ---------------------------------------------------
class ShapeNotAdmitted(Exception):
    pass


def admit(shapes):
    """Parse every Turtle text; every targeted NodeShape must carry tcf:quarkId and
    tcf:constraintClass. Returns the merged shapes graph. Raises ShapeNotAdmitted."""
    g = Graph()
    for iri, ttl in shapes.items():
        g.parse(data=ttl, format="turtle")
    for s in g.subjects(RDF.type, SH.NodeShape):
        if (s, SH.targetClass, None) not in g:
            continue   # record shapes: reached via sh:node, not targeted
        if (s, TCF.quarkId, None) not in g or (s, TCF.constraintClass, None) not in g:
            raise ShapeNotAdmitted(f"{s} lacks tcf:quarkId and/or tcf:constraintClass")
    return g


def load_library(store):
    """Library @ version: verified store -> admitted shapes graph (spec §3; plan C-2)."""
    return admit(store.shapes)
