"""sakshi.firewall — the B/T/M firewall checks.

This file is tangled from codev/firewall.org. Do not edit directly.

The functions here are callable independently of pytest. The pytest
plugin in pytest_plugin.py adapts them to pytest's collection and
reporting machinery.

@forward-compat dmt-eval:test-plugin/firewall-domain
    The entire FirewallFailure class and the check_* functions are
    anticipated as a dmt-eval test-plugin domain named 'sakshi-firewall',
    with check_* functions becoming domain checks and FirewallFailure
    becoming a domain-specific Verdict subclass.
"""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Optional

from sakshi.checksum import matches, sha256_path
from sakshi.schema import (
    Manifest,
    Mode,
    Register,
    _normalise_register_tag,
    manifest_from_yaml,
)


class FailureClass(str, Enum):
    """The B/T/M failure classes from the doctrine.

    @forward-compat dmt-eval:test-plugin/failure-class
        Anticipated as a dmt-eval Verdict.Severity enumeration.
    """

    BLOCKING = "B"
    TIGHTEN = "T"
    MISSED = "M"


class FirewallFailure(Exception):
    """A firewall check failed. Carries a B/T/M classification.

    @forward-compat dmt-eval:test-plugin/verdict
        Anticipated as a dmt-eval Verdict subclass.
    """

    def __init__(
        self,
        cls: FailureClass,
        message: str,
        *,
        manifest_step: Optional[str] = None,
        hint: Optional[str] = None,
    ):
        self.cls = cls
        self.manifest_step = manifest_step
        self.hint = hint
        full = f"[{cls.value}-class] {message}"
        if manifest_step is not None:
            full = f"[{cls.value}-class] step={manifest_step!r}: {message}"
        if hint is not None:
            full = f"{full}\n  hint: {hint}"
        super().__init__(full)
def load_manifest(path: Path) -> Manifest:
    """Load a YAML manifest file. Raises FirewallFailure (M-class) on parse failure.

    @forward-compat dmt-eval:test-plugin/manifest-loader
        Anticipated as a dmt-eval dataset-loader equivalent.
    """
    if not path.exists():
        raise FirewallFailure(
            FailureClass.MISSED,
            f"manifest file not found: {path}",
            hint="Create the manifest YAML at this path, or remove the reference.",
        )
    try:
        text = path.read_text(encoding="utf-8")
        return manifest_from_yaml(text)
    except Exception as e:
        # pydantic.ValidationError messages are usually B-class (doctrine
        # violation) but the parse failure itself is M-class until we
        # can inspect the message.
        msg = str(e)
        cls = (
            FailureClass.BLOCKING
            if any(
                marker in msg
                for marker in ("B-class:", "doctrine", "register", "mode")
            )
            else FailureClass.MISSED
        )
        raise FirewallFailure(
            cls,
            f"manifest parse failed for {path.name}: {msg}",
            hint="Edit the manifest to satisfy the schema; see codev/doctrine.org.",
        ) from e
def check_doctrine(manifest: Manifest) -> None:
    """Re-run the doctrine's structural checks against an already-built Manifest.

    The pydantic schema's model_validator runs these at parse-time. This
    function is provided for callers that constructed the Manifest
    directly (e.g., the firewall's own self-tests).

    @forward-compat dmt-eval:test-plugin/check-structural
    """
    # Round-trip through pydantic's validator by re-validating.
    Manifest.model_validate(manifest.model_dump())
def check_drift(
    manifest: Manifest,
    manifest_path: Optional[Path] = None,
) -> None:
    """T-class: verify that output checksums on disk match the manifest.

    @forward-compat dmt-eval:test-plugin/check-drift
        Anticipated as a dmt-eval test-plugin hook with the same name
        and signature.
    """
    base = manifest_path.parent if manifest_path is not None else Path.cwd()

    for out in manifest.outputs:
        if out.checksum is None:
            continue
        candidate = base / out.id
        if not (candidate.exists() and candidate.is_file()):
            # Not a resolvable path; skip silently. The manifest may
            # describe an in-memory artefact whose checksum is supplied
            # by the producing test.
            continue
        actual = sha256_path(candidate)
        if not matches(out.checksum, actual):
            raise FirewallFailure(
                FailureClass.TIGHTEN,
                (
                    f"output {out.id!r} checksum drift: "
                    f"manifest says {out.checksum}, file is {actual}"
                ),
                manifest_step=manifest.step,
                hint=(
                    "Either re-run the tests and update the manifest's "
                    "checksum (real drift), or revert the change "
                    "(stale validation)."
                ),
            )

    # The last_validated_against_tests field is a composite-checksum
    # over the test-validated state. If present, we compute a composite
    # over current output checksums and compare.
    if manifest.last_validated_against_tests is not None:
        actual_composite = _composite_checksum(manifest, base)
        if actual_composite is not None:
            if not matches(manifest.last_validated_against_tests, actual_composite):
                raise FirewallFailure(
                    FailureClass.TIGHTEN,
                    (
                        f"last_validated_against_tests checksum drift: "
                        f"manifest says {manifest.last_validated_against_tests}, "
                        f"current composite is {actual_composite}"
                    ),
                    manifest_step=manifest.step,
                    hint=(
                        "Re-run the test suite. If the new composite is "
                        "the correct one, update "
                        "'last_validated_against_tests' in the manifest."
                    ),
                )


def _composite_checksum(
    manifest: Manifest, base: Path
) -> Optional[str]:
    """Compute a sha256 over the concatenation of output checksums.

    Returns None if any output has no checksum (composite is undefined).
    """
    from sakshi.checksum import sha256_bytes

    parts: list[bytes] = []
    for out in manifest.outputs:
        if out.checksum is None:
            return None
        parts.append(f"{out.id}:{out.checksum}".encode("utf-8"))
    return sha256_bytes(b"\n".join(parts))
def check_methodology(
    manifest: Manifest,
    commit_author: Optional[str] = None,
) -> None:
    """M-class: methodology checks beyond what the schema enforces.

    @forward-compat dmt-eval:test-plugin/check-methodology
    """
    import os

    if commit_author is None:
        commit_author = os.environ.get("GIT_AUTHOR_EMAIL")

    if commit_author and manifest.author and commit_author != manifest.author:
        if manifest.llm_assistance is None:
            raise FirewallFailure(
                FailureClass.MISSED,
                (
                    f"commit author {commit_author!r} differs from manifest "
                    f"author {manifest.author!r}, but llm_assistance field "
                    "is missing"
                ),
                manifest_step=manifest.step,
                hint=(
                    "Record llm_assistance for this commit, or set the "
                    "manifest author to the current committer."
                ),
            )
def check_manifest(
    manifest_or_path: "Manifest | Path",
    *,
    commit_author: Optional[str] = None,
) -> None:
    """Run all firewall checks against a manifest.

    Accepts either a Manifest object or a Path to a YAML file. Raises
    FirewallFailure with a B/T/M classification on the first failure.

    @forward-compat dmt-eval:test-plugin/run-all-checks
        Anticipated as the top-level dmt-eval test-plugin entry-point.
    """
    if isinstance(manifest_or_path, Path):
        manifest = load_manifest(manifest_or_path)
        manifest_path: Optional[Path] = manifest_or_path
    else:
        manifest = manifest_or_path
        manifest_path = None

    # Order matters: B-class (doctrine) before T-class (drift) before
    # M-class (methodology). A broken doctrine should not generate
    # drift warnings.
    check_doctrine(manifest)
    check_drift(manifest, manifest_path)
    check_methodology(manifest, commit_author)
