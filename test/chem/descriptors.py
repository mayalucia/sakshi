"""Deterministic descriptor and Lipinski-Ro5 layer for the chem example.

This file is tangled from codev/examples/chem.org.

Optional dependency: RDKit (install with `pip install sakshi[chem]`).
If RDKit is not available, descriptor functions raise ImportError and
the test runner skips the workflow tests.
"""

from __future__ import annotations

from dataclasses import dataclass

try:
    from rdkit import Chem
    from rdkit.Chem import Crippen, Descriptors, Lipinski

    RDKIT_AVAILABLE = True
except ImportError:  # pragma: no cover
    RDKIT_AVAILABLE = False


@dataclass(frozen=True)
class MolDescriptors:
    """The fixed descriptor suite produced by rdkit-descriptor-suite-v2024."""

    compound_id: str
    molecular_weight: float
    logp: float
    tpsa: float
    hbd_count: int
    hba_count: int


def compute_descriptors(compound_id: str, smiles: str) -> MolDescriptors:
    """Compute the descriptor suite for a single SMILES.

    Procedure name: rdkit-descriptor-suite-v2024
    """
    if not RDKIT_AVAILABLE:
        raise ImportError(
            "RDKit not installed. Install with `pip install sakshi[chem]`."
        )
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"RDKit could not parse SMILES for {compound_id!r}: {smiles!r}")
    return MolDescriptors(
        compound_id=compound_id,
        molecular_weight=round(Descriptors.MolWt(mol), 2),
        logp=round(Crippen.MolLogP(mol), 2),
        tpsa=round(Descriptors.TPSA(mol), 2),
        hbd_count=Lipinski.NumHDonors(mol),
        hba_count=Lipinski.NumHAcceptors(mol),
    )


def lipinski_violations(d: MolDescriptors) -> int:
    """Count the number of Lipinski Rule-of-Five violations.

    Procedure name: lipinski-ro5-violation-count

    Ro5 (Lipinski 1997): a drug-like molecule typically has
        MW <= 500, LogP <= 5, HBD <= 5, HBA <= 10.
    """
    violations = 0
    if d.molecular_weight > 500:
        violations += 1
    if d.logp > 5:
        violations += 1
    if d.hbd_count > 5:
        violations += 1
    if d.hba_count > 10:
        violations += 1
    return violations
