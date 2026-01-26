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
    friction_message: Optional[str] = None


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
    Política simples (Camada 4.1):
    - Regra 1: resposta vazia -> retry
    - Regra 2: se for a última etapa -> advance e encerra (next_step_index=None)
    - Regra 3: se excedeu tentativas no step e resposta é fraca -> retry com fricção
    - Regra 4: caso contrário -> advance normalmente
    """

    def __init__(
        self,
        max_attempts_per_step: int = 3,
        min_meaningful_chars: int = 6,
    ):
        self.max_attempts_per_step = max_attempts_per_step
        self.min_meaningful_chars = min_meaningful_chars

        # respostas “sinal de chute”/baixa evidência (determinístico)
        self.low_effort_tokens = {
            "ok", "sim", "nao", "não", "sei", "sei la", "sei lá",
            "n", "s", "hm", "hmm", "ah", "oi",
        }

    def _normalize(self, text: str) -> str:
        return " ".join(str(text).strip().lower().split())

    def _is_low_effort(self, answer: str) -> bool:
        a = self._normalize(answer)
        if not a:
            return True
        if len(a) < self.min_meaningful_chars:
            return True
        if a in self.low_effort_tokens:
            return True
        # se for uma única palavra muito curta, tende a ser fraco
        if len(a.split()) == 1 and len(a) < 8:
            return True
        return False

    def decide(
        self,
        session: StudySession,
        current_step_index: int,
        total_steps: int,
    ) -> PolicyDecision:
        # pega a última resposta específica do step atual
        last_answer = session.last_answer_for_step(current_step_index)

        # REGRA 1 — resposta vazia → retry
        if last_answer is None or not str(last_answer).strip():
            return PolicyDecision(
                action=DecisionAction.RETRY,
                reason="empty_or_missing_answer",
                current_step_index=current_step_index,
                next_step_index=current_step_index,
                friction_message="Responda com algo escrito (mesmo que seja: 'travei em...').",
            )

        # REGRA 2 — última etapa → encerrar
        next_index = current_step_index + 1
        if next_index >= total_steps:
            return PolicyDecision(
                action=DecisionAction.ADVANCE,
                reason="end_of_plan_reached",
                current_step_index=current_step_index,
                next_step_index=None,
            )

        # REGRA 3 — anti-loop: muitas tentativas + resposta fraca
        attempts = session.count_attempts(current_step_index)
        if attempts >= self.max_attempts_per_step and self._is_low_effort(last_answer):
            return PolicyDecision(
                action=DecisionAction.RETRY,
                reason="too_many_attempts_low_effort",
                current_step_index=current_step_index,
                next_step_index=current_step_index,
                friction_message=(
                    "Você já tentou algumas vezes. Agora responda obrigatoriamente em 2 partes:\n"
                    "1) Onde exatamente você travou?\n"
                    "2) Qual foi sua ideia inicial (mesmo que esteja errada)?"
                ),
            )

        # REGRA 4 — avançar normalmente
        return PolicyDecision(
            action=DecisionAction.ADVANCE,
            reason="answer_provided",
            current_step_index=current_step_index,
            next_step_index=next_index,
        )
