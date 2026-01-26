# core/policy.py
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Protocol

from core.portfolio import StudySession


class DecisionAction(str, Enum):
    RETRY = "retry"
    ADVANCE = "advance"


@dataclass(frozen=True)
class PolicyDecision:
    action: DecisionAction
    reason: str
    current_step_index: int
    next_step_index: Optional[int]


class DecisionPolicy(Protocol):
    def decide(
        self,
        session: StudySession,
        current_step_index: int,
        total_steps: int,
    ) -> PolicyDecision:
        ...


class SimpleDecisionPolicy:
    """
    Política simples (equivalente às suas regras atuais da Camada 3):
    - Regra 1: resposta vazia -> retry
    - Regra 2: se for a última etapa -> advance e encerra (next_step_index=None)
    - Regra 3: caso contrário -> advance normalmente
    """

    def decide(
        self,
        session: StudySession,
        current_step_index: int,
        total_steps: int,
    ) -> PolicyDecision:
        last_answer = session.last_answer_text()

        # REGRA 1 — resposta vazia → retry
        if last_answer is None or not str(last_answer).strip():
            return PolicyDecision(
                action=DecisionAction.RETRY,
                reason="Empty or missing answer",
                current_step_index=current_step_index,
                next_step_index=current_step_index,
            )

        # REGRA 2 — última etapa → encerrar
        next_index = current_step_index + 1
        if next_index >= total_steps:
            return PolicyDecision(
                action=DecisionAction.ADVANCE,
                reason="Answer provided; end of plan reached",
                current_step_index=current_step_index,
                next_step_index=None,
            )

        # REGRA 3 — avançar normalmente
        return PolicyDecision(
            action=DecisionAction.ADVANCE,
            reason="Answer provided",
            current_step_index=current_step_index,
            next_step_index=next_index,
        )
