"""Foreign-company adapter registry.

Maps a seed dict to the right adapter instance. Phase 1: everything goes to
GenericInhouseAdapter. Phase 2 will add a P0 dict here.
"""
from __future__ import annotations

from typing import Any, Dict

from parsers.foreign_company_adapters import (
    AmazonAdapter,
    BaseForeignAdapter,
    GenericInhouseAdapter,
    MicrosoftAdapter,
    GoogleAdapter,
    PgAdapter,
    UnileverAdapter,
    CitadelAdapter,
)

P0_ADAPTERS: Dict[str, type] = {
    "Google": GoogleAdapter,
    "Microsoft": MicrosoftAdapter,
    "Amazon / AWS": AmazonAdapter,
    "P&G": PgAdapter,
    "Unilever": UnileverAdapter,
    "Citadel": CitadelAdapter,
}


def get_adapter(seed: Dict[str, Any]) -> BaseForeignAdapter:
    cls = P0_ADAPTERS.get(seed.get("company", ""))
    if cls is not None:
        return cls(seed)
    return GenericInhouseAdapter(seed)
