# sakshi — CLAUDE.md

*Claude-Code adapter for `sakshi`. See `system.md` for the backend-neutral version.*

You are working inside `modules/sakshi/`, a discipline-layer for environmental-data pipelines under LLM-assisted-development pressure.

## What this module does

`sakshi` keeps a firewall standing between **measurement, derivation, synthesis, and expression** in scientific-data pipelines. It does this with a pydantic manifest schema and a pytest plugin that fails fast when a register-boundary is silently crossed.

See `system.md` for the full architectural description and `README.md` for the public-facing positioning.

## Cardinal rule

**The source of truth is `codev/*.org`, not `src/sakshi/*.py`.**

The `.py` files are tangled outputs from org-babel. If you find yourself wanting to edit a `.py` file directly, stop and edit the corresponding `.org` source block instead. Then tangle. Edits to `.py` without back-port to `.org` will be overwritten.

This is the standard MāyāLucIA literate-programming discipline.

## Where things live

| What | Source-of-truth | Tangled output |
|------|-----------------|----------------|
| The doctrine (four registers, two modes, B/T/M) | `codev/doctrine.org` | (none — pure prose) |
| Pydantic manifest schema | `codev/schema.org` | `src/sakshi/schema.py` |
| Pytest plugin (firewall) | `codev/firewall.org` | `src/sakshi/pytest_plugin.py` |
| Synthetic worked example | `codev/examples/synthetic.org` | `test/test_synthetic.py` + `data/synthetic/` |
| IMIS worked example | `codev/examples/imis.org` | `test/test_imis.py` |
| Self-validation (dogfood) | `codev/dogfood.org` | `test/test_dogfood.py` + `sakshi.manifest.yaml` |
| Extension guide (how to add a check) | `codev/extension.org` | (worked examples in `test/extensions/`) |
| v0.2 roadmap | `codev/roadmap-v0.2.org` | (none — design document) |

## Forward-compatibility discipline (load-bearing for review)

`sakshi` v0.1 ships standalone. v0.2 will fold:

- Layer 1 (pytest plugin / firewall) into `dmt-eval` as a test-plugin domain
- Layer 2 (pydantic manifest schema) into `aikosh` as a schema kind

This fold-in is intended to be a **refactor of plumbing, not a redesign of doctrine**. To make that real:

1. Every pydantic field in `codev/schema.org` must have a **mirror-comment** naming the `aikosh` schema-kind field-name it anticipates. Format:
   ```
   # @forward-compat aikosh:schema-kind/<field-name>
   ```
2. Every pytest plugin hook in `codev/firewall.org` must have a **mirror-comment** naming the `dmt-eval` test-plugin surface-contract it anticipates. Format:
   ```
   # @forward-compat dmt-eval:test-plugin/<hook-name>
   ```
3. If you add a new field or a new hook without its mirror-comment, you have introduced a v0.2 refactor cost. The review pass will catch this; better to add the mirror-comment at write-time.

These mirror-comments are not aspirational — they are the contract documentation for the v0.2 refactor. They will be audited at the v0.1 template-review checkpoint.

## Review discipline

`sakshi` v0.1 will receive a B/T/M review pass from mayadev when the build is ready. The review will cover:

- **B-class**: doctrinal correctness (firewall actually holds in worked examples), schema correctness (manifests round-trip, polymorphism enforced), plugin correctness (failures actually fail the build).
- **T-class**: forward-compat audit per the discipline above (every field and hook has its mirror-comment, and the anticipated field-names are coherent against `aikosh` and `dmt-eval` system.md docs at time of review).
- **M-class**: scope honesty (README and system.md tell the same story; v0.2 roadmap is named, not vague; doctrine documents the science, not just the code).

Do not run the review pass yourself. mayadev does it. Surface the artefact for review when ready.

## When to send messages

The `send-message` skill is available. Cross-spirit coordination relevant to sakshi:

- **mayadev@mayalucia** — review authority for v0.1. Notify when build is ready for B/T/M pass.
- **themis@mayalucia** (dmt-eval guardian) — when v0.2 fold-in becomes live, themis is the counterpart. v0.1 should not message themis unsolicited; the forward-compat commitment in the README is the public signal.
- **vannevar@mayalucia** (aikosh guardian) — same as themis. The README signals; do not push.
- **dhara@parbati** — for the IMIS demonstrator. dhara provided the substrate context (Weissfluhjoch + Davos Flueela as the two-station choice) and should be looped in on `codev/examples/imis.org` revisions if substrate-fact-checking is needed.

## Build commands

```sh
make tangle           # org → py
pip install -e ".[test]"
pytest                # run firewall against worked examples
pytest test/test_dogfood.py    # self-validate
```

## Anti-patterns (do not do these)

- Do not edit `.py` files directly — edit `.org` and tangle.
- Do not add a check to the pytest plugin without adding a worked-example test that triggers it.
- Do not add a manifest field without its `@forward-compat` mirror-comment.
- Do not add a "report" or "audit log" feature. The discipline is fail-fast-and-inform; reports are scope creep.
- Do not couple to `dmt-eval` or `aikosh` import-wise in v0.1. The forward-compat is documentary, not behavioural. v0.1 must run without those modules installed.
- Do not expand to a third mode beyond `reconstruction-and-simulation` and `expression`. If a use case seems to need a third mode, surface it for review — almost certainly the case fits one of the two with the right compound register.

## Provenance

`sakshi` v0.1 was scoped and built in 2026-05 by griot (le-comptoir commission), under consultation with dhara@parbati (substrate context, naming pushback that led to the sakshi name over PARBATI) and mayadev@mayalucia (architectural placement, forward-compat discipline, B/T/M taxonomy mapping). The build was prompted by the WSL Science IT Research Software Engineer application (Dr. Ionut Iosifescu Enescu, refline 273855); the artefact is intended to outlast that occasion.
