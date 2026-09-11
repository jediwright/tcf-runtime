"""Plain-file store adapter — the only Phase 0 implementation (D-3).

A directory of *.json store documents, resolved by tcfShapeVersion IRI. `current`
is the IRI the adapter exposes for new nodes (set at construction, defaulting to
the lexically last version present). Commits are appended to a JSON-lines log.
"""
import json
import os
from typing import Any, Dict, Optional

from ..adapter import Change, StoreAdapter
from ..model import StoreDocument


class FileStoreAdapter(StoreAdapter):
    def __init__(self, root: str, current: Optional[str] = None, log_path: Optional[str] = None):
        self.root = root
        self._index: Dict[str, str] = {}
        for name in sorted(os.listdir(root)):
            if name.endswith(".json"):
                path = os.path.join(root, name)
                with open(path, encoding="utf-8") as f:
                    iri = json.load(f)["tcfShapeVersion"]
                self._index[iri] = path
        if not self._index:
            raise FileNotFoundError(f"no store documents under {root}")
        self._current = current or sorted(self._index)[-1]
        if self._current not in self._index:
            raise KeyError(f"current version {self._current!r} not in {root}")
        self.log_path = log_path or os.path.join(root, "commits.jsonl")

    def versions(self):
        return sorted(self._index)

    def load(self, store_ref: str) -> StoreDocument:
        path = self._index.get(store_ref) or (store_ref if os.path.isfile(store_ref) else None)
        if path is None:
            raise KeyError(f"unknown store ref {store_ref!r}")
        with open(path, encoding="utf-8") as f:
            return StoreDocument.from_dict(json.load(f))

    def current_version(self) -> str:
        return self._current

    def commit(self, change: Change) -> Any:
        rec = {"ops": change.ops, "reports": change.reports}
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, sort_keys=True) + "\n")
        return self.log_path
