"""sakshi.schema — Pydantic models for the provenance manifest.

This file is *tangled* from codev/schema.org. Do not edit directly.
The source-of-truth is the org file; edits here will be overwritten.

The schema encodes the four-register firewall and the two-mode
polymorphism from codev/doctrine.org. Every field carries a
forward-compatibility mirror-comment naming the aikosh schema-kind
field-name it anticipates.

@forward-compat aikosh:schema-kind/provenance-manifest
    The entire Manifest class will become an aikosh schema kind of
    this name when aikosh's schema-kind interface stabilises.
"""

from __future__ import annotations

from enum import Enum
from typing import Literal, Optional, Union

from pydantic import BaseModel, Field, field_validator, model_validator
class Register(str, Enum):
    """The four epistemic registers.

    @forward-compat aikosh:schema-kind/provenance-manifest/register-vocabulary
        Anticipated as a closed enumeration owned by aikosh, with
        sakshi as the canonical reference implementation.
    """

    MEASUREMENT = "measurement"
    DERIVED_FROM_MEASUREMENT = "derived-from-measurement"
    SYNTHETIC_ACKNOWLEDGED = "synthetic-acknowledged"
    EXPRESSION_MODE = "expression-mode"


class Mode(str, Enum):
    """The two pipeline modes.

    @forward-compat aikosh:schema-kind/provenance-manifest/mode-vocabulary
        Anticipated as a closed enumeration owned by aikosh.
    """

    RECONSTRUCTION_AND_SIMULATION = "reconstruction-and-simulation"
    EXPRESSION = "expression"


class LlmAssistanceLevel(str, Enum):
    """How much LLM assistance was used to author the step's code.

    @forward-compat aikosh:schema-kind/provenance-manifest/llm-assistance-level-vocabulary
        Anticipated as a vocabulary owned by aikosh.
    """

    NONE = "none"
    AUTOCOMPLETE = "autocomplete"
    PAIR_PROGRAMMED = "pair-programmed"
    LLM_AUTHORED_HUMAN_REVIEWED = "llm-authored-human-reviewed"
    LLM_AUTHORED_HUMAN_TESTED = "llm-authored-human-tested"
RegisterTag = Union[Register, list[Register]]
"""Either a single register or a compound (list).

@forward-compat aikosh:schema-kind/provenance-manifest/register-tag
    Compound register tags will be represented identically in the
    aikosh schema-kind — as a union of singleton and list-of-singleton.
"""


def _normalise_register_tag(tag: RegisterTag) -> list[Register]:
    """Normalise a register tag to a sorted, de-duplicated list.

    Single values become a one-element list. Lists are de-duplicated
    and sorted by enum value for stable comparison.
    """
    if isinstance(tag, Register):
        return [tag]
    return sorted(set(tag), key=lambda r: r.value)
class Input(BaseModel):
    """An upstream data artefact consumed by the step.

    @forward-compat aikosh:schema-kind/provenance-manifest/input
        Anticipated as an aikosh schema kind in its own right
        (provenance-manifest-input), referenced by aikosh-id from
        the parent manifest.
    """

    id: str = Field(
        ...,
        description="Identifier the manifest uses to refer to this input.",
    )
    # @forward-compat aikosh:schema-kind/provenance-manifest/input/aikosh-id
    #     Will become an aikosh-id reference to an aikosh-indexed artefact.

    register: RegisterTag = Field(
        ...,
        description="Register tag(s) carried by this input at the time of consumption.",
    )
    # @forward-compat aikosh:schema-kind/provenance-manifest/input/register

    checksum: Optional[str] = Field(
        None,
        description="Cryptographic checksum (e.g., 'sha256:...') of the input artefact.",
    )
    # @forward-compat aikosh:schema-kind/provenance-manifest/input/checksum

    description: Optional[str] = Field(
        None,
        description="Free-form description of the input. Optional.",
    )
    # @forward-compat aikosh:schema-kind/provenance-manifest/input/description

    @field_validator("register")
    @classmethod
    def _check_register(cls, v: RegisterTag) -> RegisterTag:
        """Normalise compound register tags."""
        if isinstance(v, list):
            return _normalise_register_tag(v)
        return v
class Output(BaseModel):
    """A data artefact produced by the step.

    @forward-compat aikosh:schema-kind/provenance-manifest/output
        Anticipated as an aikosh schema kind in its own right
        (provenance-manifest-output).
    """

    id: str = Field(
        ...,
        description="Identifier the manifest uses to refer to this output.",
    )
    # @forward-compat aikosh:schema-kind/provenance-manifest/output/aikosh-id

    register: RegisterTag = Field(
        ...,
        description="Register tag(s) carried by this output.",
    )
    # @forward-compat aikosh:schema-kind/provenance-manifest/output/register

    checksum: Optional[str] = Field(
        None,
        description="Cryptographic checksum of the output, for T-class drift detection.",
    )
    # @forward-compat aikosh:schema-kind/provenance-manifest/output/checksum

    derivation: Optional[str] = Field(
        None,
        description=(
            "Named derivation procedure, required when an output's register "
            "promotes from MEASUREMENT toward DERIVED_FROM_MEASUREMENT."
        ),
    )
    # @forward-compat aikosh:schema-kind/provenance-manifest/output/derivation

    synthesis: Optional[str] = Field(
        None,
        description=(
            "Named synthesis procedure, required when an output's register "
            "carries SYNTHETIC_ACKNOWLEDGED."
        ),
    )
    # @forward-compat aikosh:schema-kind/provenance-manifest/output/synthesis

    re_measurement: Optional[str] = Field(
        None,
        description=(
            "Named re-measurement procedure, required when a consuming step "
            "re-extracts data from an EXPRESSION_MODE input. The procedure "
            "must record any transformations being reversed (e.g., vertical "
            "exaggeration factor)."
        ),
    )
    # @forward-compat aikosh:schema-kind/provenance-manifest/output/re-measurement

    description: Optional[str] = Field(
        None,
        description="Free-form description of the output. Optional.",
    )
    # @forward-compat aikosh:schema-kind/provenance-manifest/output/description

    @field_validator("register")
    @classmethod
    def _check_register(cls, v: RegisterTag) -> RegisterTag:
        if isinstance(v, list):
            return _normalise_register_tag(v)
        return v
class LlmAssistance(BaseModel):
    """Record of LLM assistance used to author the step's code.

    @forward-compat aikosh:schema-kind/provenance-manifest/llm-assistance
        Anticipated as an aikosh schema kind. The reviewer field will
        become an aikosh-id reference to a person-record.
    """

    level: LlmAssistanceLevel = Field(
        ...,
        description="The level of LLM assistance used.",
    )
    # @forward-compat aikosh:schema-kind/provenance-manifest/llm-assistance/level

    model: Optional[str] = Field(
        None,
        description=(
            "Identifier of the LLM used (e.g., 'claude-opus-4-6'). "
            "Required when level is not NONE."
        ),
    )
    # @forward-compat aikosh:schema-kind/provenance-manifest/llm-assistance/model

    reviewer: Optional[str] = Field(
        None,
        description=(
            "Identifier of the human reviewer of the LLM-assisted code. "
            "Required when level is not NONE."
        ),
    )
    # @forward-compat aikosh:schema-kind/provenance-manifest/llm-assistance/reviewer-id

    notes: Optional[str] = Field(
        None,
        description="Free-form notes on the assistance and review.",
    )
    # @forward-compat aikosh:schema-kind/provenance-manifest/llm-assistance/notes

    @model_validator(mode="after")
    def _check_reviewer_when_assisted(self) -> "LlmAssistance":
        if self.level != LlmAssistanceLevel.NONE:
            if self.model is None:
                raise ValueError(
                    "llm_assistance.model is required when level is not 'none'"
                )
            if self.reviewer is None:
                raise ValueError(
                    "llm_assistance.reviewer is required when level is not 'none'"
                )
        return self
class TestReference(BaseModel):
    """Reference to a test the step has passed.

    @forward-compat aikosh:schema-kind/provenance-manifest/test-reference
        Anticipated as an aikosh schema kind, with the test-id field
        becoming an aikosh-id reference to a test-record indexed by
        aikosh's eventual test-discovery layer.
    """

    test_id: str = Field(
        ...,
        description=(
            "Test identifier. By convention a pytest node ID "
            "(e.g., 'test/test_imis.py::test_gap_fill_flagged')."
        ),
    )
    # @forward-compat aikosh:schema-kind/provenance-manifest/test-reference/test-id

    description: Optional[str] = Field(
        None,
        description="Free-form description of what this test asserts.",
    )
    # @forward-compat aikosh:schema-kind/provenance-manifest/test-reference/description
class Manifest(BaseModel):
    """The provenance manifest for a single pipeline step.

    This is the core sakshi data structure. The pytest plugin reads
    instances of this class and runs B/T/M checks against them.

    @forward-compat aikosh:schema-kind/provenance-manifest
        Anticipated as the top-level aikosh schema kind. The step
        field will become an aikosh-id.
    """

    step: str = Field(
        ...,
        description=(
            "Identifier for the pipeline step. Must be unique within a "
            "repository. By convention, kebab-case "
            "(e.g., 'gap-fill-station-imis-weissfluhjoch-temperature')."
        ),
    )
    # @forward-compat aikosh:schema-kind/provenance-manifest/step-aikosh-id

    mode: Mode = Field(
        ...,
        description="The pipeline mode this step is operating in.",
    )
    # @forward-compat aikosh:schema-kind/provenance-manifest/mode

    inputs: list[Input] = Field(
        default_factory=list,
        description="The data artefacts this step consumes.",
    )
    # @forward-compat aikosh:schema-kind/provenance-manifest/inputs

    outputs: list[Output] = Field(
        ...,
        description="The data artefacts this step produces.",
        min_length=1,
    )
    # @forward-compat aikosh:schema-kind/provenance-manifest/outputs

    llm_assistance: Optional[LlmAssistance] = Field(
        None,
        description=(
            "Record of LLM assistance used to author this step's code. "
            "Required by the M-class firewall when the commit author "
            "differs from the manifest-recorded author and the step's "
            "code has changed."
        ),
    )
    # @forward-compat aikosh:schema-kind/provenance-manifest/llm-assistance

    tests: list[TestReference] = Field(
        ...,
        description=(
            "Tests this step has passed. M-class fails if empty for any "
            "reconstruction-and-simulation step."
        ),
    )
    # @forward-compat aikosh:schema-kind/provenance-manifest/tests

    last_validated_against_tests: Optional[str] = Field(
        None,
        description=(
            "Cryptographic checksum of the test-validated output, used "
            "for T-class drift detection. Format: 'sha256:...'. "
            "Required when 'tests' is non-empty and at least one output "
            "carries a checksum."
        ),
    )
    # @forward-compat aikosh:schema-kind/provenance-manifest/last-validated-against-tests

    author: Optional[str] = Field(
        None,
        description=(
            "Identifier of the manifest's author. Optional but "
            "encouraged. M-class fires when commit author differs and "
            "llm_assistance is missing."
        ),
    )
    # @forward-compat aikosh:schema-kind/provenance-manifest/author-aikosh-id

    description: Optional[str] = Field(
        None,
        description="Free-form description of the step. Optional.",
    )
    # @forward-compat aikosh:schema-kind/provenance-manifest/description

    @model_validator(mode="after")
    def _check_doctrine(self) -> "Manifest":
        """Enforce the doctrine's structural constraints.

        These are B-class checks enforced at parse-time. They catch the
        cases that can be caught from the manifest alone (i.e., without
        running the actual pipeline step). The pytest plugin does the
        rest.
        """
        # B-class: an expression-mode mode forces all outputs to carry
        # EXPRESSION_MODE in their register.
        if self.mode == Mode.EXPRESSION:
            for out in self.outputs:
                regs = _normalise_register_tag(out.register)
                if Register.EXPRESSION_MODE not in regs:
                    raise ValueError(
                        f"B-class: output {out.id!r} in an expression-mode "
                        f"step must carry the 'expression-mode' register "
                        f"(got {[r.value for r in regs]})."
                    )

        # B-class: an output that promotes to DERIVED_FROM_MEASUREMENT
        # must have a derivation field.
        for out in self.outputs:
            regs = _normalise_register_tag(out.register)
            if Register.DERIVED_FROM_MEASUREMENT in regs:
                if out.derivation is None:
                    raise ValueError(
                        f"B-class: output {out.id!r} carries "
                        f"'derived-from-measurement' but has no 'derivation' "
                        f"field."
                    )

        # B-class: an output that carries SYNTHETIC_ACKNOWLEDGED must
        # have a synthesis field.
        for out in self.outputs:
            regs = _normalise_register_tag(out.register)
            if Register.SYNTHETIC_ACKNOWLEDGED in regs:
                if out.synthesis is None:
                    raise ValueError(
                        f"B-class: output {out.id!r} carries "
                        f"'synthetic-acknowledged' but has no 'synthesis' "
                        f"field."
                    )

        # B-class: an output that consumes an EXPRESSION_MODE input in
        # a reconstruction-and-simulation step must have re_measurement.
        if self.mode == Mode.RECONSTRUCTION_AND_SIMULATION:
            expression_inputs = [
                inp for inp in self.inputs
                if Register.EXPRESSION_MODE
                in _normalise_register_tag(inp.register)
            ]
            if expression_inputs:
                for out in self.outputs:
                    if out.re_measurement is None:
                        raise ValueError(
                            f"B-class: step {self.step!r} is in "
                            f"reconstruction-and-simulation mode and "
                            f"consumes expression-mode inputs "
                            f"({[i.id for i in expression_inputs]}); output "
                            f"{out.id!r} must declare 're_measurement'."
                        )

        # M-class: reconstruction-and-simulation requires non-empty tests.
        if self.mode == Mode.RECONSTRUCTION_AND_SIMULATION:
            if not self.tests:
                raise ValueError(
                    f"M-class: step {self.step!r} is in "
                    f"reconstruction-and-simulation mode but has no tests."
                )

        # M-class: if tests are present and any output has a checksum,
        # last_validated_against_tests must be present.
        if self.tests and any(o.checksum is not None for o in self.outputs):
            if self.last_validated_against_tests is None:
                raise ValueError(
                    f"M-class: step {self.step!r} has tests and "
                    f"checksummed outputs but no "
                    f"'last_validated_against_tests' field."
                )

        return self
def manifest_from_yaml(yaml_text: str) -> Manifest:
    """Parse a YAML manifest into a Manifest object.

    Validation errors are raised as pydantic.ValidationError; the
    pytest plugin catches and classifies these into B/T/M.
    """
    import yaml

    data = yaml.safe_load(yaml_text)
    return Manifest.model_validate(data)


def manifest_to_yaml(manifest: Manifest) -> str:
    """Serialise a Manifest to YAML."""
    import yaml

    return yaml.safe_dump(
        manifest.model_dump(mode="json", exclude_none=True),
        sort_keys=False,
    )
