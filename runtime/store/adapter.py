"""Store adapter interface (plan D-2/D-3; B-1).

The gate imports ONLY this module. Concrete adapters live in runtime/store/adapters/
and are injected by the caller. Phase 0 ships the file adapter; Automerge is a
Phase 1 adapter, not a rewrite.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List

from .model import StoreDocument


@dataclass
class Change:
    """A committed write: the write set plus gate-computed fields plus reports,
    emitted as a JSON-patch-style list of ops (plan C-3 step 8, D-3)."""
    ops: List[Dict[str, Any]] = field(default_factory=list)
    reports: Dict[str, str] = field(default_factory=dict)   # nodeId -> report digest


class StoreAdapter(ABC):
    @abstractmethod
    def load(self, store_ref: str) -> StoreDocument:
        """Load the store at `store_ref` (a tcfShapeVersion IRI or adapter-native ref).
        MUST return the document unverified; verification (§2.3) is the gate's step 1."""

    @abstractmethod
    def current_version(self) -> str:
        """tcfShapeVersion IRI the store currently exposes for new nodes (§5.2 step 1)."""

    @abstractmethod
    def commit(self, change: Change) -> Any:
        """Commit a gate-accepted change to the substrate. Returns an adapter-native ref."""
