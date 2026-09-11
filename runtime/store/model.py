"""Quark store document model, canonicalization, and digest (runtime spec §2.3).

Canonicalization (C-1): RFC 8785 JCS-equivalent for the JSON subset used here —
sorted keys, no insignificant whitespace, UTF-8, no non-finite floats. Recorded
as build choice BC-1; see build record.
"""
import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Dict


class StoreInvalid(Exception):
    """Raised when a store's versionDigest does not match its contents (§2.3)."""
    code = "E-STORE-INVALID"

    def __init__(self, detail):
        super().__init__(f"{self.code}: {detail}")
        self.detail = detail


def canonical_json(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def compute_digest(quarks, shapes, context) -> str:
    """sha256 over canonical JSON of {quarks, shapes, context} — the §2.3 triple."""
    payload = {"quarks": quarks, "shapes": shapes, "context": context}
    return "sha256:" + hashlib.sha256(canonical_json(payload)).hexdigest()


@dataclass
class StoreDocument:
    storeId: str
    tcfShapeVersion: str
    quarks: Dict[str, dict]
    shapes: Dict[str, str]          # shape IRI -> Turtle text
    context: dict                   # JSON-LD context for this version
    versionDigest: str = ""

    def computed_digest(self) -> str:
        return compute_digest(self.quarks, self.shapes, self.context)

    def verify(self) -> "StoreDocument":
        """§2.3 invariant: digest is computed, never declared. Mismatch -> StoreInvalid."""
        expected = self.computed_digest()
        if self.versionDigest != expected:
            raise StoreInvalid(
                f"versionDigest {self.versionDigest!r} != computed {expected!r} "
                f"for {self.tcfShapeVersion}")
        return self

    def seal(self) -> "StoreDocument":
        """Author-side helper: set versionDigest from contents. Never called by the gate."""
        self.versionDigest = self.computed_digest()
        return self

    @classmethod
    def from_dict(cls, d: dict) -> "StoreDocument":
        return cls(storeId=d["storeId"], tcfShapeVersion=d["tcfShapeVersion"],
                   quarks=d["quarks"], shapes=d["shapes"], context=d["context"],
                   versionDigest=d.get("versionDigest", ""))

    def to_dict(self) -> dict:
        return {"storeId": self.storeId, "tcfShapeVersion": self.tcfShapeVersion,
                "quarks": self.quarks, "shapes": self.shapes, "context": self.context,
                "versionDigest": self.versionDigest}

    def shape_digests(self) -> Dict[str, str]:
        """Content address of each shape's Turtle (C-2: 'content-addressed by sha256')."""
        return {iri: hashlib.sha256(ttl.encode("utf-8")).hexdigest()
                for iri, ttl in self.shapes.items()}
