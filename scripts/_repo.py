"""
Shared repository-root resolution for tooling under ``scripts/`` (any depth).

Run maintenance scripts from the clone root so relative paths like ``./data/``
still resolve correctly, e.g. ``python scripts/corpus/rebuild_rag_corpus.py``.
"""
from __future__ import annotations

import sys
from pathlib import Path

_MARKERS = ("api_complete.py", "requirements.txt")


def repo_root() -> Path:
    """Return the Virtual Lawyer repo root (directory containing ``api_complete.py``)."""
    here = Path(__file__).resolve().parent
    for anc in (here, *here.parents):
        if all((anc / m).exists() for m in _MARKERS):
            return anc
    raise RuntimeError(
        "Could not find repo root (api_complete.py + requirements.txt). "
        "Run commands from your virtual-lawyer project directory."
    )


def bootstrap_path(*, include_src: bool = True) -> Path:
    """Prepend repo root and ``src/`` to ``sys.path``; return repo root."""
    root = repo_root()
    r = str(root)
    if r not in sys.path:
        sys.path.insert(0, r)
    if include_src:
        s = str(root / "src")
        if s not in sys.path:
            sys.path.insert(0, s)
    return root
