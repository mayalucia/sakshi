"""Hand-curated small SMILES dataset for sakshi's chemoinformatics example.

This file is tangled from codev/examples/chem.org.

Each entry is a public, textbook drug-like compound or a small
Bemis–Murcko core. SMILES strings are copied from PubChem entries
(public-domain compound identifiers; no proprietary structures).

Columns when written to CSV:
    compound_id  -- short identifier
    name         -- common name
    smiles       -- canonical SMILES
"""

from __future__ import annotations

from pathlib import Path

SMILES_SEED = [
    # Drug-like reference compounds (public textbook chemistry).
    ("ASP", "aspirin",     "CC(=O)Oc1ccccc1C(=O)O"),
    ("IBU", "ibuprofen",   "CC(C)Cc1ccc(C(C)C(=O)O)cc1"),
    ("CAF", "caffeine",    "Cn1cnc2c1c(=O)n(C)c(=O)n2C"),
    ("PCM", "paracetamol", "CC(=O)Nc1ccc(O)cc1"),
    # Small Bemis–Murcko-style scaffolds for descriptor variety.
    ("PYR", "pyridine",    "c1ccncc1"),
    ("IND", "indole",      "c1ccc2[nH]ccc2c1"),
    ("QIN", "quinoline",   "c1ccc2ncccc2c1"),
    ("THI", "thiazole",    "c1cscn1"),
]


def write_csv(out_path: Path) -> None:
    """Write the seed dataset to a CSV at out_path."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["compound_id,name,smiles"]
    for cid, name, smi in SMILES_SEED:
        lines.append(f"{cid},{name},{smi}")
    out_path.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    write_csv(Path(__file__).parent / "smiles_seed.csv")
