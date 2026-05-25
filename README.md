# sakshi

*Sanskrit सक्षी — "the witness." The one whose role is not to act on the data but to remain present to it: to observe what was measured, what was derived, what was synthesised, and what was expressed, and to refuse to let those four registers blur into each other.*

---

## What this is

`sakshi` is a small, opinionated discipline-layer for **environmental-data pipelines that are being modified by humans working alongside large language models**.

It does one job: it keeps the firewall standing between **measurement, derivation, synthesis, and expression**, and it fails loudly the moment a pipeline step tries to silently cross it.

It is built around two ideas, neither of which is novel on its own; the contribution is in their combination.

1. **The four-register firewall.** Every dataset, every figure, every model output carries a register-tag: `measurement` (came from a sensor), `derived-from-measurement` (a deterministic function of measurements), `synthetic-acknowledged` (generated, and the manifest says so), or `expression-mode` (an artistic or pedagogical rendering whose claim to truth is different in kind). Compound tags are permitted and often required. The firewall holds when no step in a pipeline silently demotes a tag — and the discipline catches the demotion before it reaches a publication, a model card, or a press release.

2. **Two-mode polymorphism.** A scientific-data pipeline operates in one of two modes: **reconstruction-and-simulation** (the goal is to model a real system, and measurements are the ground truth) or **expression** (the goal is to render an experience, and measurements are a starting palette). The same data can serve both modes, but a manifest must declare which mode is active at each step, and the firewall enforces the different obligations of each.

These two ideas are encoded in a pydantic schema (the manifest) and a pytest plugin (the check). Both are small. The point is the discipline, not the code.

---

## Why this exists

Environmental-data infrastructure today — repositories like EnviDat, sensor networks like IMIS, EO archives like Copernicus — was built before the working scientist had a coding assistant at their shoulder. The pipelines that publish, transform, and visualise that data were built on an implicit assumption: *the person making the change understands what they are changing.*

That assumption was always partial. LLM-assisted development has made it brittle.

It is now routine for a researcher to ask a model to "tidy up this figure script" or "make the QC flag column more readable" or "interpolate the missing values" — and to receive working code that, in the act of being helpful, has silently:

- Replaced a measurement column with a model-derived estimate, with no flag.
- Smoothed a sensor artefact that was the actual scientific signal.
- Filled gaps with plausible values that pass downstream sanity-checks but encode a generative model the manifest does not declare.
- Rendered a figure in an aesthetically pleasing way that crosses from reconstruction-mode into expression-mode without saying so.

None of these is fraud. Each is the natural failure mode of *a coding assistant that has been instructed to be helpful, working on a pipeline whose register-discipline lives in the heads of researchers who are not at the keyboard.*

`sakshi` is the discipline made external. It does not prevent LLM-assisted edits. It refuses to let them pass silently.

---

## How it works (one minute)

A pipeline step is described by a `Manifest` — a small YAML or in-code declaration:

```yaml
step: gap-fill-station-imis-weissfluhjoch-temperature
mode: reconstruction-and-simulation
inputs:
  - id: raw-imis-2024
    register: measurement
    checksum: sha256:f3a1...
outputs:
  - id: filled-imis-2024
    register: derived-from-measurement
    derivation: temporal-interpolation-linear
llm_assistance:
  level: pair-programmed
  model: claude-opus-4-6
  reviewer: i.iosifescu
tests:
  - test_no_measurement_silently_overwritten
  - test_interpolation_flag_present_in_output
last_validated_against_tests: sha256:b7c2...
```

The pytest plugin reads manifests and runs three classes of check on each:

- **B-class (Bug / blocking)**: register-tag violations. A `measurement` input flows out without a derivation entry, or a `synthetic-acknowledged` value is being treated as a measurement downstream. Build fails.
- **T-class (Tighten-on-commit / drift)**: output checksum has changed since the last manifest-recorded validation. Either the test suite needs re-running and the checksum updating, or a real drift has occurred. Build fails until the human acknowledges which.
- **M-class (Missed / methodology)**: required tags are missing, mode is not declared, or a manifest has no `tests:` entry at all. Build fails fast and tells the human exactly what is missing.

The plugin does not maintain a compliance report. It **fails fast and informs**. The B/T/M taxonomy is borrowed from the MāyāLucIA review discipline; the failure messages are written to surface what a human needs to do, not what a dashboard needs to display.

---

## What's in this repository

- `codev/doctrine.org` — the four-register firewall and the two-mode polymorphism, with worked examples of each failure mode.
- `codev/schema.org` — the pydantic manifest schema, literate, with each field annotated for forward-compatibility with `aikosh`'s eventual schema-kind interface.
- `codev/firewall.org` — the pytest plugin, literate, with each hook annotated for forward-compatibility with `dmt-eval`'s eventual test-plugin contract.
- `codev/examples/synthetic.org` — a random-walk dataset with four injected faults, one per B/T/M class plus one false-positive trap. The pedagogical spine.
- `codev/examples/imis.org` — a cached two-station snapshot from the SLF IMIS network (Weissfluhjoch and Davos Flueela), gap-filling and QC-flag handling, with manifest. The credibility anchor.
- `codev/examples/chem.org` — a small-molecule chemoinformatics pipeline (SMILES → RDKit descriptors → Lipinski Ro5 → templated SAR insight), with one clean manifest and two pedagogical broken manifests. A *portability sketch* — same epistemic register as `synthetic.org`, not the same as `imis.org`. It demonstrates that the sakshi schema accommodates a molecule-as-graph topology without modification; it does **not** claim that sakshi has been validated against chemoinformatics practice. v0.1 ships this without a chem-practitioner reviewer; v0.2 will either find one (and re-tier to demonstrator) or remove the example. Requires the optional `[chem]` extra (`pip install sakshi[chem]`) to run RDKit-dependent tests; manifest-level tests run without it.
- `codev/dogfood.org` — `sakshi` validates its own build pipeline. The artefact that distributes the discipline cannot itself ignore the discipline.
- `codev/extension.org` — how to add a check for a new register class, a new mode, or a domain-specific invariant.
- `codev/roadmap-v0.2.org` — the named fold-in: when `dmt-eval`'s test-plugin contract stabilises (currently moving under [WP-0069 Brain-Score architectural comparison](https://github.com/mayalucia/dmt-eval)), `sakshi`'s firewall becomes a `dmt-eval` test-plugin domain; when `aikosh`'s schema-kind interface stabilises, `sakshi`'s manifest becomes an `aikosh` schema kind.

The source-of-truth lives in the `.org` files. The `.py` files in `src/sakshi/` and `test/` are tangled outputs.

---

## v0.1 scope and what comes next

This is v0.1. It ships **standalone**, with `pydantic` and `pytest` as the only load-bearing dependencies. It does this on purpose.

`sakshi` is a discipline-layer that *would naturally live inside* two other MāyāLucIA modules: `dmt-eval` (which is becoming the project's general validation engine) and `aikosh` (which is becoming the project's schema and knowledge-collection layer). At time of writing, both of those modules are mid-scaffolding — their plugin contracts are not yet stable. Shipping `sakshi` on top of unstable substrates would couple the discipline to the substrate, and would make the substrate's churn into `sakshi`'s churn.

Instead, v0.1 ships standalone with **interfaces designed to mirror what the eventual substrate-hosts will need**. Every pydantic field in the manifest schema is annotated with the `aikosh` schema-kind field-name it anticipates. Every pytest plugin hook is annotated with the `dmt-eval` test-plugin surface-contract it anticipates. When the substrates stabilise, the v0.2 fold-in is a refactor of plumbing, not a redesign of doctrine.

This is intentional cross-spirit coordination, not a private plan: the README states it, the codev files document it field-by-field, and the work registers a feature-request against `dmt-eval` and `aikosh` without making it a demand.

---

## What this is not

- It is not a compliance framework. There is no audit-trail dashboard, no report-generator, no certification. The discipline is in the *failure*, not in the bureaucracy of recording.
- It is not Alpine-specific or sensor-network-specific. IMIS is v0.1's *credibility-anchored* demonstrator (WSL stands behind the substrate). The doctrine is substrate-neutral in design — the `synthetic.org` pedagogical example and the `chem.org` portability sketch ship to illustrate this, but neither is credibility-anchored. The chem sketch in particular makes the substrate-neutrality claim *testable* (the schema accommodates a molecule-as-graph topology without modification) but does not make it *validated* (no chem-practitioner has reviewed). v0.2 will either find a chem reviewer or retire the sketch.
- It is not a replacement for code review. It is a tool that lets reviewers focus on what only humans can review (was this the right transformation?) by automating what can be checked structurally (was the register of this column preserved or declared changed?).
- It is not anti-LLM. It assumes LLM-assisted development is the new baseline and asks: what discipline does that baseline need to remain trustworthy?

---

## Status

Pre-alpha. v0.1 ships the doctrine, the schema, the firewall, and three worked examples at distinct epistemic tiers: `synthetic.org` (pedagogical, random-walk-with-injected-faults, not credibility-anchored), `imis.org` (the credibility-anchored demonstrator, with WSL behind the substrate), and `chem.org` (a portability sketch — same tier as `synthetic.org`, *not* a demonstrator, with no chem-practitioner reviewer yet). v0.2 will fold into `dmt-eval` and `aikosh` when those modules' contracts stabilise, and will either find a chem reviewer (re-tiering chem to demonstrator) or retire the sketch.

## License

MIT.

## Related work

- `dmt-eval` — MāyāLucIA's general validation engine. `sakshi` v0.2 will fold its firewall in as a test-plugin domain.
- `aikosh` — MāyāLucIA's schema and knowledge-collection layer. `sakshi` v0.2 will fold its manifest schema in as a schema kind.
- `parbati` — MāyāLucIA's Himalayan-substrate spirit. Provides the IMIS worked example and the eventual second demonstrator (WP-0141 InSAR landslide-susceptibility slice).
- EnviDat (WSL) — CKAN-based FAIR-compliant environmental data repository; the canonical environment that motivates this discipline.

— *sakshi v0.1*
