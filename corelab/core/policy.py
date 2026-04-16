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
    Política simples (Camada 4.2):
    - Regra 1: resposta vazia -> retry (com fricção)
    - Regra 2: se for a última etapa -> advance e encerra (next_step_index=None)
    - Regra 3: resposta repetida no mesmo step -> retry com fricção (anti-loop)
    - Regra 4: resposta baixa evidência:
        - se ainda está no começo -> retry com fricção leve
        - se excedeu tentativas -> retry com fricção forte (2 partes)
    - Regra 5: caso contrário -> advance normalmente
    """

    def __init__(
        self,
        max_attempts_per_step: int = 3,
        min_meaningful_chars: int = 6,
        early_friction_attempts: int = 1,
    ):
        self.max_attempts_per_step = max_attempts_per_step
        self.min_meaningful_chars = min_meaningful_chars
        self.early_friction_attempts = early_friction_attempts

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

    def _is_repeated_answer(self, session: StudySession, step_index: int, answer: str) -> bool:
        """Detecta repetição simples: mesma resposta no mesmo step (ignorando espaços/caixa)."""
        a = self._normalize(answer)
        if not a:
            return False

        last_for_step = session.last_answer_for_step(step_index)
        if last_for_step is None:
            return False

        return self._normalize(last_for_step) == a

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

        # contagem de tentativas do step
        attempts = session.count_attempts(current_step_index)

        # REGRA 3 — anti-loop: resposta repetida no mesmo step
        if self._is_repeated_answer(session, current_step_index, last_answer):
            return PolicyDecision(
                action=DecisionAction.RETRY,
                reason="repeated_answer_same_step",
                current_step_index=current_step_index,
                next_step_index=current_step_index,
                friction_message=(
                    "Você repetiu a mesma resposta. Mude o formato:\n"
                    "• Escreva 1 frase dizendo onde travou\n"
                    "• Depois 1 exemplo (mesmo incompleto) do que você tentou"
                ),
            )

        # REGRA 4 — baixa evidência (fricção progressiva)
        if self._is_low_effort(last_answer):
            # fricção leve cedo (evita “passar” com qualquer coisa)
            if attempts <= self.early_friction_attempts:
                return PolicyDecision(
                    action=DecisionAction.RETRY,
                    reason="low_effort_early",
                    current_step_index=current_step_index,
                    next_step_index=current_step_index,
                    friction_message=(
                        "Sua resposta está curta demais para eu confiar que você entendeu.\n"
                        "Complete com: (1) o que você entende até aqui e (2) onde começou a confusão."
                    ),
                )

            # fricção forte quando já insistiu
            if attempts >= self.max_attempts_per_step:
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

            # meio termo: ainda retry, mas sem “punição”
            return PolicyDecision(
                action=DecisionAction.RETRY,
                reason="low_effort_retry",
                current_step_index=current_step_index,
                next_step_index=current_step_index,
                friction_message="Tente detalhar um pouco mais (1–3 frases). O objetivo é evidência, não acerto.",
            )

        # REGRA 5 — avançar normalmente
        return PolicyDecision(
            action=DecisionAction.ADVANCE,
            reason="answer_provided",
            current_step_index=current_step_index,
            next_step_index=next_index,
        )
