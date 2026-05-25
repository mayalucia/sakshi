"""Tests for sakshi's chemoinformatics worked example.

This file is tangled from codev/examples/chem.org.

The test suite walks a four-stage chemoinformatics pipeline (SMILES →
descriptors → Lipinski violations → templated SAR insight) and asserts
the firewall behaviour at each step, including the two pedagogical
broken manifests.

RDKit-dependent tests are skipped if RDKit is not installed; the
manifest-level tests run regardless.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from sakshi import (
    FailureClass,
    FirewallFailure,
    check_manifest,
    load_manifest,
)

HERE = Path(__file__).parent
CHEM_DIR = HERE / "chem"
MANIFESTS_DIR = CHEM_DIR / "manifests"
BROKEN_DIR = MANIFESTS_DIR / "broken"
DATA_DIR = CHEM_DIR / "data"

# Make the chem helper modules importable.
sys.path.insert(0, str(CHEM_DIR))


@pytest.fixture(scope="module", autouse=True)
def ensure_smiles_csv():
    csv_path = DATA_DIR / "smiles_seed.csv"
    if not csv_path.exists():
        from data.smiles_seed import write_csv  # type: ignore[import-not-found]

        write_csv(csv_path)


# ----- Manifest-only checks --------------------------------------------


def test_01_chem_correct_loads():
    """The clean manifest parses cleanly and passes all firewall checks."""
    manifest = load_manifest(MANIFESTS_DIR / "01_chem_correct.manifest.yaml")
    assert manifest.step == "chem-smiles-to-sar-insight-v1"
    check_manifest(manifest)


def test_01_chem_correct_has_four_outputs_with_registers():
    """The clean manifest's three outputs carry the right registers."""
    manifest = load_manifest(MANIFESTS_DIR / "01_chem_correct.manifest.yaml")
    by_id = {o.id: o for o in manifest.outputs}
    assert by_id["descriptors.parquet"].register.value == "derived-from-measurement"
    assert by_id["descriptors.parquet"].derivation == "rdkit-descriptor-suite-v2024"
    assert by_id["lipinski_violations.parquet"].register.value == "derived-from-measurement"
    assert by_id["lipinski_violations.parquet"].derivation == "lipinski-ro5-violation-count"
    assert by_id["sar_insights.parquet"].register.value == "synthetic-acknowledged"
    assert by_id["sar_insights.parquet"].synthesis == "templated-sar-insight-stub"


def test_02_broken_missing_derivation_raises():
    """Stage 2 missing derivation field must raise B-class at parse."""
    with pytest.raises(Exception) as excinfo:
        load_manifest(BROKEN_DIR / "02_chem_missing_derivation.manifest.yaml")
    msg = str(excinfo.value)
    assert "B-class" in msg
    assert "derivation" in msg
    assert "descriptors.parquet" in msg


def test_03_broken_missing_synthesis_raises():
    """Stage 4 missing synthesis field must raise B-class at parse."""
    with pytest.raises(Exception) as excinfo:
        load_manifest(BROKEN_DIR / "03_chem_missing_synthesis.manifest.yaml")
    msg = str(excinfo.value)
    assert "B-class" in msg
    assert "synthesis" in msg
    assert "sar_insights.parquet" in msg


# ----- Pipeline-execution checks (RDKit-gated) -------------------------


def _rdkit_available() -> bool:
    try:
        import rdkit  # noqa: F401

        return True
    except ImportError:
        return False


requires_rdkit = pytest.mark.skipif(
    not _rdkit_available(),
    reason="RDKit not installed; install with `pip install sakshi[chem]`.",
)


@requires_rdkit
def test_descriptors_match_expected_for_aspirin():
    """Descriptor suite for aspirin matches textbook values within rounding."""
    from descriptors import compute_descriptors  # type: ignore[import-not-found]

    d = compute_descriptors("ASP", "CC(=O)Oc1ccccc1C(=O)O")
    # Aspirin: MW≈180, LogP≈1.2, TPSA≈63.6, HBD=1, HBA=3 (textbook values)
    assert 175 <= d.molecular_weight <= 185
    assert 0.5 <= d.logp <= 1.8
    assert 60 <= d.tpsa <= 70
    assert d.hbd_count == 1
    assert d.hba_count == 3


@requires_rdkit
def test_descriptors_match_expected_for_caffeine():
    """Descriptor suite for caffeine matches textbook values within rounding."""
    from descriptors import compute_descriptors  # type: ignore[import-not-found]

    d = compute_descriptors("CAF", "Cn1cnc2c1c(=O)n(C)c(=O)n2C")
    # Caffeine: MW≈194, LogP≈-0.1, TPSA≈58, HBD=0, HBA=3
    assert 190 <= d.molecular_weight <= 200
    assert d.hbd_count == 0


@requires_rdkit
def test_lipinski_violations_zero_for_drug_like():
    """All eight bundled compounds satisfy Lipinski Ro5 (zero violations)."""
    from data.smiles_seed import SMILES_SEED  # type: ignore[import-not-found]
    from descriptors import compute_descriptors, lipinski_violations  # type: ignore[import-not-found]

    for cid, _name, smi in SMILES_SEED:
        d = compute_descriptors(cid, smi)
        assert lipinski_violations(d) == 0, (
            f"Compound {cid} unexpectedly violates Ro5: {d}"
        )


@requires_rdkit
def test_sar_insight_is_deterministic_function_of_descriptors():
    """The insight stub is deterministic and depends only on descriptors."""
    from descriptors import compute_descriptors  # type: ignore[import-not-found]
    from insight import sar_insight_stub  # type: ignore[import-not-found]

    d = compute_descriptors("IBU", "CC(C)Cc1ccc(C(C)C(=O)O)cc1")
    s1 = sar_insight_stub(d)
    s2 = sar_insight_stub(d)
    assert s1 == s2
    assert "IBU" in s1
    assert str(d.logp) in s1


@requires_rdkit
def test_sar_insight_register_honesty():
    """The insight layer's output is synthetic-acknowledged in the manifest.

    This is a documentation test: it asserts that the project's
    convention treats the templated stub identically to a real LLM
    call. If you replace sar_insight_stub with an actual LLM call,
    the manifest does not change — the register is already honest.
    """
    manifest = load_manifest(MANIFESTS_DIR / "01_chem_correct.manifest.yaml")
    insight_output = next(
        o for o in manifest.outputs if o.id == "sar_insights.parquet"
    )
    assert insight_output.register.value == "synthetic-acknowledged"
    assert insight_output.synthesis is not None


# ----- Substrate-portability assertion ---------------------------------


def test_chem_manifest_uses_no_chemistry_specific_schema_fields():
    """The chem manifest uses only generic sakshi schema fields.

    This test makes the substrate-portability claim concrete:
    everything in the chem manifest is built from sakshi's generic
    vocabulary (register, derivation, synthesis, mode). Nothing in
    sakshi's schema mentions chemistry. If the doctrine were
    domain-specific, this test would be impossible to write.
    """
    import yaml

    raw = yaml.safe_load(
        (MANIFESTS_DIR / "01_chem_correct.manifest.yaml").read_text()
    )
    # The only domain-specific strings are in `description` and
    # `derivation`/`synthesis` *values* — i.e., free-form text the
    # schema does not constrain. The *keys* are all generic.
    chem_specific_keys = {"smiles", "molecule", "compound", "rdkit", "lipinski"}

    def walk_keys(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                yield k
                yield from walk_keys(v)
        elif isinstance(obj, list):
            for item in obj:
                yield from walk_keys(item)

    keys = set(walk_keys(raw))
    leaked = keys & chem_specific_keys
    assert not leaked, (
        f"Chemistry-specific keys leaked into the manifest structure: {leaked}. "
        f"sakshi's schema should not need chemistry-specific extensions."
    )
