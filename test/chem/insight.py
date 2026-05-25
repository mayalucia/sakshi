"""Templated synthetic-prediction layer for the chem example.

This file is tangled from codev/examples/chem.org.

The function in this file would, in a production drug-discovery
workflow, be a call to an LLM (Claude, GPT-4, a medchem-fine-tuned
model). We substitute a deterministic templated string so:

1. The example runs anywhere without API keys.
2. The output is bit-identical across runs.
3. The discipline being demonstrated does not depend on the actual
   text content — it depends on the *register*.

The register is ~synthetic-acknowledged~, and the manifest's
~synthesis~ field names the procedure honestly.
"""

from __future__ import annotations

from .descriptors import MolDescriptors


def sar_insight_stub(d: MolDescriptors) -> str:
    """Emit a templated SAR-style insight string from descriptors.

    Procedure name: templated-sar-insight-stub

    In production, replace with an LLM call:
        sar_insight_llm(d) -> calls claude-opus-4-6 with a medchem prompt
    The register remains 'synthetic-acknowledged' in both cases.
    """
    permeation = "likely cell-permeable" if d.logp < 5 and d.tpsa < 90 else "permeation uncertain"
    drug_like = "within Lipinski-friendly range" if d.molecular_weight <= 500 else "above typical drug-like MW"
    return (
        f"Compound {d.compound_id}: LogP={d.logp} and TPSA={d.tpsa} — "
        f"{permeation}; molecular weight {d.molecular_weight} places it "
        f"{drug_like}; donor/acceptor profile ({d.hbd_count}/{d.hba_count}) "
        f"is balanced for oral bioavailability."
    )
