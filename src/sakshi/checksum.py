"""sakshi.checksum — compute and verify cryptographic checksums.

This file is tangled from codev/firewall.org. Do not edit directly.

@forward-compat dmt-eval:test-plugin/checksum-utility
    Anticipated as a dmt-eval utility module shared across test-plugin
    domains.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Union


def sha256_bytes(data: bytes) -> str:
    """Return 'sha256:<hex>' for the given bytes."""
    return f"sha256:{hashlib.sha256(data).hexdigest()}"


def sha256_path(path: Union[str, Path]) -> str:
    """Return 'sha256:<hex>' for the contents of the file at *path*.

    Reads in chunks to handle large files without loading them whole.
    """
    h = hashlib.sha256()
    p = Path(path)
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return f"sha256:{h.hexdigest()}"


def matches(expected: str, actual: str) -> bool:
    """Return True iff two 'sha256:<hex>' strings are equal (case-insensitive)."""
    return expected.lower() == actual.lower()
