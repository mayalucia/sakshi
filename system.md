# sakshi — system.md

*The backend-neutral architectural document. CLAUDE.md is the Claude-Code adapter for this same content.*

## Soul

`sakshi` (Sanskrit सक्षी, "the witness") is the discipline-layer that keeps the firewall standing between **measurement, derivation, synthesis, and expression** in environmental-data pipelines that are being modified by humans working alongside large language models.

It is not a compliance system. It is a small, opinionated tool whose only behaviour is to **fail fast and inform** when a pipeline step crosses a register boundary it has not declared.

## Position within MāyāLucIA

`sakshi` is a `modules/`-level peer to `dmt-eval` and `aikosh`. It is registered as a git submodule in the parent `mayalucia/` system.md table (registration order: this repo created → submodule-added-and-committed to parent → parent system.md table updated).

It is **not** a sub-component of either `dmt-eval` or `aikosh`. In v0.2, parts of `sakshi` will fold *into* those modules (the firewall as a `dmt-eval` test-plugin domain; the manifest as an `aikosh` schema kind), but the doctrine itself — the four-register firewall and the two-mode polymorphism — remains substrate-neutral and lives here.

`sakshi` consumes nothing from `parbati`. It demonstrates *on* parbati substrate (one of two demonstrators is a cached IMIS snapshot whose original collection is parbati's domain), but the manifest schema and pytest plugin are domain-blind.

## Three-layer architecture

```
┌────────────────────────────────────────────────────┐
│ Layer 3 — Doctrine                                 │
│   The four-register firewall.                      │
│   The two-mode polymorphism.                       │
│   The B/T/M failure taxonomy.                      │
│   Substrate-neutral. Lives in codev/doctrine.org.  │
├────────────────────────────────────────────────────┤
│ Layer 2 — Schema                                   │
│   pydantic models for Manifest, Input, Output,     │
│   LlmAssistance, TestReference.                    │
│   Polymorphic over mode (reconstruction vs         │
│   expression).                                     │
│   Forward-compat: each field annotated with its    │
│   anticipated aikosh schema-kind field-name.       │
│   Lives in codev/schema.org → src/sakshi/schema.py │
├────────────────────────────────────────────────────┤
│ Layer 1 — Firewall                                 │
│   pytest plugin that reads manifests and runs      │
│   B-class / T-class / M-class checks.              │
│   Fails fast and informs. No reports.              │
│   Forward-compat: each hook annotated with its     │
│   anticipated dmt-eval test-plugin surface.        │
│   Lives in codev/firewall.org →                    │
│      src/sakshi/pytest_plugin.py.                  │
└────────────────────────────────────────────────────┘
```

Demonstrators sit alongside, not in the stack:

- `codev/examples/synthetic.org` — random-walk + four injected faults. Pedagogical.
- `codev/examples/imis.org` — cached two-station IMIS snapshot (Weissfluhjoch, Davos Flueela). Credibility anchor.
- `codev/dogfood.org` — sakshi validates its own build pipeline.

## The four registers

A `register` is a tag attached to a data artefact (a column, a file, a figure, a model output) that declares its epistemic status.

| Register | Meaning | Originates from |
|----------|---------|-----------------|
| `measurement` | A direct sensor or observation reading. | Physical world. |
| `derived-from-measurement` | A deterministic function of measurements. | Computation on measurements. |
| `synthetic-acknowledged` | A generated value, declared as such. | A model, simulator, or LLM. |
| `expression-mode` | A rendering whose claim to truth is artistic or pedagogical. | Human choice for communication. |

**Compound registers are required where applicable.** A gap-filled column may be `derived-from-measurement | synthetic-acknowledged` if some gaps were closed by a generative model. The discipline is to refuse to collapse the compound for convenience.

**The firewall**: no step in a pipeline may silently demote a register. Demotion examples:

- `measurement` → `derived-from-measurement` without a `derivation:` entry (silent computation).
- `synthetic-acknowledged` → `measurement` (synthetic value treated as ground truth).
- `expression-mode` → `derived-from-measurement` (aesthetic rendering re-imported as data).

## The two modes

A `mode` is a manifest-level declaration of what the pipeline step is *for*.

| Mode | Meaning | Obligations |
|------|---------|-------------|
| `reconstruction-and-simulation` | Goal is to model a real system. Measurements are ground truth. | All register-promotions must be declared with a `derivation:`. Synthetic values must be flagged. Test coverage required. |
| `expression` | Goal is to render an experience. Measurements are a starting palette. | Sources must be cited; expression-mode register required on all outputs; downstream consumption is firewalled — `expression-mode` outputs cannot flow into a `reconstruction-and-simulation` step without an explicit `re-measurement:` declaration. |

**The polymorphism**: the same dataset can serve both modes, but a manifest must declare which mode is active for each step. The firewall holds the modes apart.

## The B/T/M failure taxonomy

Borrowed from the MāyāLucIA review discipline (specifically mayadev's review pass conventions). Mapped to manifest-failure cases:

| Class | Stands for | Manifest-failure case | Build behaviour |
|-------|-----------|----------------------|-----------------|
| **B** | Blocking | Register-tag violation. Compound-register collapse. Mode-firewall breach. | Fail. Cannot proceed. |
| **T** | Tighten-on-commit | Output checksum has drifted since `last_validated_against_tests`. Tests not re-run. | Fail until human declares: real drift (T-class, accept new checksum) or stale validation (T-class, re-run tests and update). |
| **M** | Missed (methodology) | Required tag absent. Mode not declared. No `tests:` entry. LLM-assistance field missing when commit author differs from manifest-recorded author. | Fail fast with a message naming exactly what is missing. |

**The output is the failure message, not a report.** The discipline lives in the moment of failure, when a human is at the keyboard with a decision to make. Reports defer decisions; failures force them.

## Forward-compatibility commitments

`sakshi` v0.1 ships standalone with `pydantic` and `pytest`. It does this on purpose — the substrates it would naturally consume (`dmt-eval`, `aikosh`) are mid-scaffolding and would couple sakshi's churn to theirs.

But v0.1 commits to a forward-compat contract:

1. **Manifest schema fields** are annotated (in `codev/schema.org` and as docstrings in `src/sakshi/schema.py`) with the anticipated `aikosh` schema-kind field-name. When `aikosh`'s schema-kind interface stabilises, the manifest becomes an `aikosh` schema kind via a field-rename refactor, not a redesign.

2. **Pytest plugin hooks** are annotated with the anticipated `dmt-eval` test-plugin surface contract. When `dmt-eval`'s test-plugin contract stabilises (WP-0069 Brain-Score architectural comparison is the current pressure on this surface), the firewall becomes a `dmt-eval` test-plugin domain via a hook-rename refactor.

3. **The doctrine layer is not folded.** Layer 3 stays in `sakshi`. Only Layers 1 and 2 fold into substrates. The substrate-neutral discipline remains a standalone artefact.

This is the v0.2 roadmap. It is named in the README, documented field-by-field in the codev files, and surfaced to themis (dmt-eval guardian) and vannevar (aikosh guardian) via the sūtra.

## Cardinal rule

**The source of truth is `codev/*.org`, not `src/sakshi/*.py`.**

The `.py` files are tangled outputs. If `.py` and `.org` disagree, `.org` wins. Edits to `.py` that have not been back-ported to `.org` will be overwritten on next tangle.

This is the standard MāyāLucIA literate-programming discipline, inherited from `dmt-eval` and `aikosh`. `sakshi` does not vary from it.

## Repository layout

```
sakshi/
├── pyproject.toml           # hatchling build, pydantic+pytest+pandas+numpy
├── README.md                # public face (cited from cover letters, etc.)
├── system.md                # this file (backend-neutral architecture)
├── CLAUDE.md                # Claude-Code adapter for the same content
├── codev/                   # source of truth (literate org)
│   ├── doctrine.org         # Layer 3 — the science
│   ├── schema.org           # Layer 2 — pydantic models (tangles to src/sakshi/schema.py)
│   ├── firewall.org         # Layer 1 — pytest plugin (tangles to src/sakshi/pytest_plugin.py)
│   ├── examples/
│   │   ├── synthetic.org    # random-walk + 4 injected faults (tangles to test/test_synthetic.py)
│   │   └── imis.org         # cached IMIS two-station slice (tangles to test/test_imis.py)
│   ├── dogfood.org          # sakshi validates its own build
│   ├── extension.org        # how-to-add-a-check guide
│   └── roadmap-v0.2.org     # named fold-in to dmt-eval and aikosh
├── src/sakshi/              # tangled outputs (do not edit directly)
├── test/                    # tangled tests (do not edit directly)
├── data/imis-cached/        # cached IMIS snapshot (small, committed)
└── develop/                 # scratch, design notes, not source-of-truth
```

## Build and verify

```sh
# Tangle org → py
make tangle    # or: org-babel-tangle-all in Emacs

# Install in editable mode
pip install -e ".[test]"

# Run the firewall against the worked examples
pytest

# Run sakshi against its own pipeline (dogfood)
pytest test/test_dogfood.py
```

## Versioning

- **v0.1** (this) — standalone, pydantic + pytest, forward-compat interfaces, two demonstrators, dogfooded.
- **v0.2** — fold Layer 1 into `dmt-eval` as test-plugin domain; fold Layer 2 into `aikosh` as schema kind. Layer 3 stays here. Triggered by stabilisation of those modules' contracts.
- **v0.3** — second demonstrator from `parbati` (WP-0141 InSAR landslide-susceptibility), Himalayan side of the bridge.

## Guardian spirit

`sakshi` will receive its own guardian spirit (TBD name) when v0.2 work begins. v0.1 is built under griot's stewardship as a commission artefact for the WSL Science IT application; mayadev (mayalucia primary developer) holds review authority.
