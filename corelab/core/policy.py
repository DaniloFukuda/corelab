# core/policy.py
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from core.portfolio import StudySession, StudyStep


class DecisionAction(str, Enum):
    RETRY = "RETRY"
    ADVANCE = "ADVANCE"


@dataclass(frozen=True)
class Decision:
    action: DecisionAction
    reason: str
    friction_message: Optional[str] = None


class DecisionPolicy:
    def decide(self, session: StudySession, step: StudyStep) -> Decision:
        raise NotImplementedError


class SimpleDecisionPolicy(DecisionPolicy):
    """
    Política simples:
    - Se o último registro do step foi correto => ADVANCE
    - Se incorreto => RETRY
    - Se excedeu tentativas máximas => RETRY com fricção (anti-loop)
    """

    def __init__(self, max_attempts_per_step: int = 3):
        self.max_attempts_per_step = max_attempts_per_step

    def decide(self, session: StudySession, step: StudyStep) -> Decision:
        latest = session.get_latest_record(step_id=step.id)

        if latest is None:
            return Decision(
                action=DecisionAction.RETRY,
                reason="no_record",
                friction_message="Responda ao exercício para registrar a primeira tentativa.",
            )

        attempts = session.count_attempts(step_id=step.id)

        if attempts >= self.max_attempts_per_step and not latest.is_correct:
            return Decision(
                action=DecisionAction.RETRY,
                reason="too_many_attempts",
                friction_message=(
                    "Você já tentou algumas vezes. Antes de tentar de novo, "
                    "escreva em 1-2 linhas: (1) onde você travou e (2) qual era sua ideia inicial."
                ),
            )

        if latest.is_correct:
            return Decision(
                action=DecisionAction.ADVANCE,
                reason="correct",
            )

        return Decision(
            action=DecisionAction.RETRY,
            reason="incorrect",
            friction_message="Tente novamente. Dica: explique seu raciocínio em 1 frase antes de responder.",
        )
