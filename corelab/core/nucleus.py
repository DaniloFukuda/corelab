# core/nucleus.py
from dataclasses import dataclass
from typing import Optional, List
import uuid

from agents.planner_agent import SimplePlannerAgent, StudyStep
from agents.tutor_agent import PlaceholderTutorAgent
from core.portfolio import StudentPortfolio, StudySession

from core.policy import DecisionPolicy, SimpleDecisionPolicy


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
    request: StudyRequest  # guardamos para o loop do main usar o núcleo sem recalcular


# =========================
# NÚCLEO (AUTORIDADE)
# =========================

class Nucleus:
    def __init__(
        self,
        planner_agent: Optional[SimplePlannerAgent] = None,
        tutor_agent: Optional[PlaceholderTutorAgent] = None,
        policy: Optional[DecisionPolicy] = None,
    ):
        self.planner_agent = planner_agent or SimplePlannerAgent()
        self.tutor_agent = tutor_agent or PlaceholderTutorAgent()
        self.policy = policy or SimpleDecisionPolicy()

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
        instruction = self.explain_step(request=request, step=first_step)

        return NucleusResult(
            session_id=session_id,
            plan=plan,
            current_step_index=current_step_index,
            instruction=instruction,
            request=request,
        )

    # -------------------------
    # CAMADA 4 — POLICY (DECISÃO FORA DO NÚCLEO)
    # -------------------------

    def decide(
        self,
        portfolio: StudentPortfolio,
        session_id: str,
        current_step_index: int,
        total_steps: int,
    ) -> NucleusDecision:

        session = portfolio.get_session(session_id)

        # delega 100% a lógica para a policy
        p = self.policy.decide(
            session=session,
            current_step_index=current_step_index,
            total_steps=total_steps,
        )

        # mantém o contrato do NucleusDecision exatamente como antes (main não quebra)
        return NucleusDecision(
            action=p.action.value,  # "advance" | "retry"
            reason=p.reason,
            current_step_index=p.current_step_index,
            next_step_index=p.next_step_index,
        )

    # -------------------------
    # API DO NÚCLEO (TUTOR)
    # -------------------------

    def explain_step(self, request: StudyRequest, step: StudyStep) -> str:
        """
        O cliente (main) NÃO chama tutor diretamente.
        Ele pede ao núcleo, e o núcleo adapta o StudyStep para a assinatura do tutor.
        """
        step_title = getattr(step, "title", None) or getattr(step, "step_title", None) or str(step)
        step_prompt = getattr(step, "prompt", None) or getattr(step, "step_prompt", None) or ""

        return self.tutor_agent.explain(
            request.topic,
            request.level,
            request.goal,
            step_title,
            step_prompt,
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
