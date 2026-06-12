from dataclasses import dataclass, field


@dataclass
class StageResult:
    stage_name: str
    raw_response: str = ""
    parsed_data: dict | None = None
    extracted: bool = False
    repaired: bool = False
    repair_steps: list[str] = field(default_factory=list)
    validation_warnings: list[str] = field(default_factory=list)
    validation_errors: list[str] = field(default_factory=list)
    fallback_used: bool = False
    latency_ms: float | None = None
    token_estimate_input: int | None = None
    token_estimate_output: int | None = None

    @property
    def success(self) -> bool:
        return self.parsed_data is not None and len(self.validation_errors) == 0

    @property
    def used_fallback(self) -> bool:
        return self.fallback_used

    def to_dict(self) -> dict:
        return {
            "stage_name": self.stage_name,
            "raw_response": self.raw_response[:200] if self.raw_response else "",
            "parsed_data": self.parsed_data,
            "extracted": self.extracted,
            "repaired": self.repaired,
            "repair_steps": self.repair_steps,
            "validation_warnings": self.validation_warnings,
            "validation_errors": self.validation_errors,
            "fallback_used": self.fallback_used,
            "latency_ms": self.latency_ms,
            "token_estimate_input": self.token_estimate_input,
            "token_estimate_output": self.token_estimate_output,
        }
