"""sakshi — provenance discipline for environmental-data pipelines.

This file is tangled from codev/firewall.org. Do not edit directly.

Public surface:

    from sakshi import (
        Manifest, Mode, Register,
        Input, Output, LlmAssistance, LlmAssistanceLevel,
        TestReference,
        check_manifest, FirewallFailure, FailureClass,
        manifest_from_yaml, manifest_to_yaml,
        sha256_path, sha256_bytes,
    )

See README.md and codev/doctrine.org for the discipline this enforces.
"""

from sakshi.checksum import sha256_bytes, sha256_path
from sakshi.firewall import (
    FailureClass,
    FirewallFailure,
    check_doctrine,
    check_drift,
    check_manifest,
    check_methodology,
    load_manifest,
)
from sakshi.schema import (
    Input,
    LlmAssistance,
    LlmAssistanceLevel,
    Manifest,
    Mode,
    Output,
    Register,
    TestReference,
    manifest_from_yaml,
    manifest_to_yaml,
)

__version__ = "0.1.0"

__all__ = [
    # Schema
    "Manifest",
    "Mode",
    "Register",
    "Input",
    "Output",
    "LlmAssistance",
    "LlmAssistanceLevel",
    "TestReference",
    "manifest_from_yaml",
    "manifest_to_yaml",
    # Firewall
    "check_manifest",
    "check_doctrine",
    "check_drift",
    "check_methodology",
    "load_manifest",
    "FirewallFailure",
    "FailureClass",
    # Checksum
    "sha256_bytes",
    "sha256_path",
    # Meta
    "__version__",
]
