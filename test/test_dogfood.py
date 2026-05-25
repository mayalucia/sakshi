"""sakshi validates its own build pipeline.

This file is tangled from codev/dogfood.org.

Four assertions:

1. The manifest loads under sakshi's own schema.
2. All declared inputs exist on disk.
3. All declared outputs exist on disk.
4. No silent extras — src/sakshi/ has no .py files beyond manifest outputs.

The third and fourth tests together enforce the cardinal rule that the
source-of-truth is codev/*.org. If a .py file exists without a
corresponding org source, it is a silent demotion of the discipline.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from sakshi import Manifest, load_manifest

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = REPO_ROOT / "sakshi.manifest.yaml"


@pytest.fixture(scope="module")
def manifest() -> Manifest:
    return load_manifest(MANIFEST_PATH)


def test_manifest_loads(manifest: Manifest):
    """sakshi must be able to describe its own build under its own schema."""
    assert manifest.step == "sakshi-build-v0.1"
    assert manifest.mode.value == "reconstruction-and-simulation"
    assert len(manifest.inputs) > 0
    assert len(manifest.outputs) > 0


def test_all_inputs_exist(manifest: Manifest):
    """Every declared input must exist on disk."""
    missing = []
    for inp in manifest.inputs:
        path = REPO_ROOT / inp.id
        if not path.exists():
            missing.append(inp.id)
    assert not missing, (
        f"Manifest declares inputs that do not exist on disk: {missing}. "
        "Either the inputs were deleted (revert) or the manifest is stale "
        "(update)."
    )


def test_all_outputs_exist(manifest: Manifest):
    """Every declared output must exist on disk after tangle."""
    missing = []
    for out in manifest.outputs:
        path = REPO_ROOT / out.id
        if not path.exists():
            missing.append(out.id)
    assert not missing, (
        f"Manifest declares outputs that do not exist on disk: {missing}. "
        "Run `make tangle` (or org-babel-tangle-all in Emacs)."
    )


def test_no_silent_extras(manifest: Manifest):
    """src/sakshi/ must contain only files declared in the manifest.

    A .py file in src/sakshi/ without an org source is a silent demotion
    of the source-of-truth rule.
    """
    declared = {
        out.id
        for out in manifest.outputs
        if out.id.startswith("src/sakshi/")
    }
    actual_py = {
        f"src/sakshi/{p.name}"
        for p in (REPO_ROOT / "src" / "sakshi").glob("*.py")
    }
    # Ignore __pycache__ etc., which glob does not return.
    extras = actual_py - declared
    assert not extras, (
        f"Found src/sakshi/ .py files not declared in the manifest: "
        f"{extras}. Either back-port them to codev/*.org and re-tangle, "
        f"or remove them."
    )
