from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable, List, Optional


def _safe_unlink(path: Path) -> None:
    try:
        path.unlink()
    except FileNotFoundError:
        return
    except PermissionError:
        # Windows: file may be opened in Excel; skip instead of crashing.
        return


def prune_directory(
    directory: Path,
    *,
    keep_paths: Iterable[Path],
    allow_globs: Optional[List[str]] = None,
) -> None:
    """Delete older outputs, keeping only explicit keep_paths.

    - **keep_paths**: full paths to keep (must be inside directory).
    - **allow_globs**: optional list of glob patterns to prune (e.g. ["smartshanghai_*.csv"]).
      If omitted, the function only prunes files that share the same stem prefix as keep_paths.
    """
    directory = Path(directory)
    keep_set = {Path(p).resolve() for p in keep_paths}

    candidates: List[Path] = []
    if allow_globs:
        for g in allow_globs:
            candidates.extend(directory.glob(g))
    else:
        # Heuristic: prune files that share "prefix_" style with the kept stems.
        prefixes = set()
        for p in keep_set:
            stem = p.stem
            if "_" in stem:
                prefixes.add(stem.split("_", 1)[0] + "_")
        if prefixes:
            for p in directory.iterdir():
                if p.is_file() and any(p.stem.startswith(pref) for pref in prefixes):
                    candidates.append(p)

    for p in candidates:
        rp = p.resolve()
        if rp in keep_set:
            continue
        _safe_unlink(p)


def ensure_parent(path: Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)


def atomic_write_text(path: Path, text: str, encoding: str = "utf-8") -> None:
    """Best-effort atomic write to avoid partial files."""
    path = Path(path)
    ensure_parent(path)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding=encoding)
    os.replace(tmp, path)

