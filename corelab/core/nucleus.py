from dataclasses import dataclass
from typing import Optional, List
import uuid

from agents.planner_agent import SimplePlannerAgent, StudyStep
from agents.tutor_agent import PlaceholderTutorAgent
from core.portfolio import StudentPortfolio, StudySession, StepRecord


# =========================
# CONTRATOS (DATACLASSES)
# =========================

@dataclass(frozen=True)
class StudyRequest:
    topic: str
    level: str
    goal: str


@dataclass(frozen=True)
class NucleusDecision:
    action: str  # "advance" | "retry"
    reason: str
    current_step_index: int
    next_step_index: Optional[int]


@dataclass(frozen=True)
class NucleusResult:
    session_id: str
    plan: List[StudyStep]
    current_step_index: int
    instruction: str


# =========================
# NÚCLEO (AUTORIDADE)
# =========================

class Nucleus:
    def __init__(
        self,
        planner_agent: Optional[SimplePlannerAgent] = None,
        tutor_agent: Optional[PlaceholderTutorAgent] = None,
    ):
        self.planner_agent = planner_agent or SimplePlannerAgent()
        self.tutor_agent = tutor_agent or PlaceholderTutorAgent()

    # ---------
    # ENTRADA
    # ---------

    def start(
        self,
        request: StudyRequest,
        portfolio: StudentPortfolio,
    ) -> NucleusResult:
        self._validate_request(request)

        # cria sessão
        session_id = str(uuid.uuid4())
        session = StudySession(session_id=session_id)
        portfolio.add_session(session)

        # gera plano
        plan = self.planner_agent.build_plan(
            topic=request.topic,
            level=request.level,
            goal=request.goal,
        )

        # seleciona primeiro passo
        current_step_index = 0
        first_step = plan[current_step_index]

        # instrução inicial
        instruction = self.tutor_agent.explain(first_step)

        return NucleusResult(
            session_id=session_id,
            plan=plan,
            current_step_index=current_step_index,
            instruction=instruction,
        )

    # -------------------------
    # CAMADA 3 — DECISÃO
    # -------------------------

    def decide(
        self,
        portfolio: StudentPortfolio,
        session_id: str,
        current_step_index: int,
        total_steps: int,
    ) -> NucleusDecision:

        session = portfolio.get_session(session_id)
        last_answer = session.last_answer_text()

        # REGRA 1 — resposta vazia → retry
        if last_answer is None or not str(last_answer).strip():
            return NucleusDecision(
                action="retry",
                reason="Empty or missing answer",
                current_step_index=current_step_index,
                next_step_index=current_step_index,
            )

        # REGRA 2 — última etapa → encerrar
        next_index = current_step_index + 1
        if next_index >= total_steps:
            return NucleusDecision(
                action="advance",
                reason="Answer provided; end of plan reached",
                current_step_index=current_step_index,
                next_step_index=None,
            )

        # REGRA 3 — avançar normalmente
        return NucleusDecision(
            action="advance",
            reason="Answer provided",
            current_step_index=current_step_index,
            next_step_index=next_index,
        )

    # -------------------------
    # VALIDAÇÕES
    # -------------------------

    def _validate_request(self, request: StudyRequest) -> None:
        if not request.topic.strip():
            raise ValueError("Topic cannot be empty")

        if not request.level.strip():
            raise ValueError("Level cannot be empty")

        if not request.goal.strip():
            raise ValueError("Goal cannot be empty")
