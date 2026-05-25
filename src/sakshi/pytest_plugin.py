"""sakshi.pytest_plugin — pytest integration for the firewall.

This file is tangled from codev/firewall.org. Do not edit directly.

Registered as a pytest plugin via the project's entry-point in
pyproject.toml ([project.entry-points.pytest11] sakshi = "...").

@forward-compat dmt-eval:test-plugin/pytest-integration
    Anticipated as a dmt-eval test-plugin pytest-integration shim.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pytest

from sakshi.firewall import FirewallFailure, check_manifest


# ----- Discovery --------------------------------------------------------


DEFAULT_MANIFEST_GLOBS = (
    "**/manifest.yaml",
    "**/manifest.yml",
    "**/*.manifest.yaml",
    "**/*.manifest.yml",
    "**/sakshi.manifest.yaml",
)


def _discover_manifests(rootdir: Path) -> Iterable[Path]:
    """Find all manifest YAML files under *rootdir*.

    @forward-compat dmt-eval:test-plugin/discover-targets
    """
    seen: set[Path] = set()
    for pattern in DEFAULT_MANIFEST_GLOBS:
        for p in rootdir.glob(pattern):
            if p.is_file() and p not in seen:
                seen.add(p)
                yield p


# ----- Pytest hooks -----------------------------------------------------


def pytest_addoption(parser):
    """Register sakshi-specific command-line options.

    @forward-compat dmt-eval:test-plugin/cli-options
    """
    group = parser.getgroup("sakshi")
    group.addoption(
        "--sakshi-manifests-dir",
        action="append",
        default=[],
        help=(
            "Restrict sakshi manifest discovery to this directory "
            "(repeatable). Default: rootdir."
        ),
    )
    group.addoption(
        "--sakshi-no-discovery",
        action="store_true",
        default=False,
        help="Disable automatic manifest discovery.",
    )


def pytest_collection_modifyitems(config, items):
    """Surface B/T/M class in the test ID for any sakshi-collected items.

    @forward-compat dmt-eval:test-plugin/collect-modify
    """
    # No-op in v0.1; the SakshiManifestItem class (below) already
    # constructs its nodeid with the class prefix. Hook is retained
    # for forward-compatibility.
    return None


def pytest_collect_file(parent, file_path: Path):
    """Hook a sakshi manifest YAML file into pytest's collection.

    @forward-compat dmt-eval:test-plugin/collect-target
    """
    if not file_path.suffix.lower() in (".yaml", ".yml"):
        return None
    name = file_path.name.lower()
    if not (
        name == "manifest.yaml"
        or name == "manifest.yml"
        or name.endswith(".manifest.yaml")
        or name.endswith(".manifest.yml")
    ):
        return None

    # Manifests living under a directory named 'broken/' are pedagogical
    # artefacts deliberately constructed to fail. They must not be
    # auto-discovered as live test targets; the doctrinal tests that
    # exercise them load them explicitly with pytest.raises.
    # @forward-compat dmt-eval:test-plugin/discovery-exclude
    if any(part == "broken" for part in file_path.parts):
        return None

    config = parent.config
    if config.getoption("--sakshi-no-discovery"):
        return None

    restricted = config.getoption("--sakshi-manifests-dir")
    if restricted:
        if not any(
            str(file_path).startswith(str(Path(d).resolve()))
            for d in restricted
        ):
            return None

    return SakshiManifestFile.from_parent(parent, path=file_path)


# ----- Custom collector and item ---------------------------------------


class SakshiManifestFile(pytest.File):
    """A pytest File node wrapping one sakshi manifest YAML.

    @forward-compat dmt-eval:test-plugin/target-file
    """

    def collect(self):
        yield SakshiManifestItem.from_parent(self, name=self.path.stem)


class SakshiManifestItem(pytest.Item):
    """One pytest item per manifest: runs all firewall checks.

    @forward-compat dmt-eval:test-plugin/target-item
    """

    def runtest(self):
        try:
            check_manifest(self.path)
        except FirewallFailure as e:
            # Re-raise as a pytest.Failed so that pytest's reporting
            # surfaces the message cleanly. We keep the original
            # exception in the chain.
            raise SakshiFirewallFailed(str(e)) from e

    def repr_failure(self, excinfo):
        """Format the failure for pytest output.

        @forward-compat dmt-eval:test-plugin/verdict-renderer
        """
        if isinstance(excinfo.value, SakshiFirewallFailed):
            return str(excinfo.value)
        return super().repr_failure(excinfo)

    def reportinfo(self):
        return self.path, 0, f"sakshi::{self.name}"


class SakshiFirewallFailed(Exception):
    """Pytest-friendly wrapper around FirewallFailure.

    @forward-compat dmt-eval:test-plugin/verdict-exception
    """

    pass
