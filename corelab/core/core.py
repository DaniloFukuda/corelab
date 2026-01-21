from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass
class CoreResult:
    ok: bool
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


@dataclass
class Core:
    steps: List[Callable[[Dict[str, Any]], CoreResult]] = field(default_factory=list)

    def register_step(self, step: Callable[[Dict[str, Any]], CoreResult]) -> None:
        self.steps.append(step)

    def run(self, request: Dict[str, Any]) -> CoreResult:
        if "message" not in request or not isinstance(request["message"], str):
            return CoreResult(ok=False, error="Campo 'message' inválido")

        ctx: Dict[str, Any] = {"message": request["message"].strip()}

        for step in self.steps:
            result = step(ctx)
            if not result.ok:
                return result
            ctx.update(result.data)

        return CoreResult(ok=True, data=ctx)
