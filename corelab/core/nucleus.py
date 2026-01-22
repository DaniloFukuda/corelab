# core/nucleus.py
from dataclasses import dataclass
import uuid

from agents.planner_agent import SimplePlannerAgent, StudyStep
from agents.tutor_agent import PlaceholderTutorAgent
from core.portfolio import StudentPortfolio, StudySession, StepRecord


@dataclass(frozen=True)
class StudyRequest:
    topic: str
    level: str
    goal: str


class Nucleus:
    """
    Núcleo = autoridade do sistema.
    - valida entrada
    - cria sessão no Portfólio (estado oficial)
    - chama agentes (planner/tutor)
    - registra respostas via receive_answer()
    """
    def __init__(self, planner=None, tutor=None, student_id: str = "demo-student"):
        self.planner = planner or SimplePlannerAgent()
        self.tutor = tutor or PlaceholderTutorAgent()

        # Portfólio do aluno (estado central)
        self.portfolio = StudentPortfolio(student_id=student_id)
        self.current_session: StudySession | None = None

    def start(self, req: StudyRequest) -> dict:
        # 1) Autoridade primeiro: valida antes de criar estado
        self._validate(req)

        # 2) Cria uma sessão (container lógico do estudo)
        session = StudySession(
            session_id=str(uuid.uuid4()),
            topic=req.topic,
            goal=req.goal,
        )
        self.portfolio.start_session(session)
        self.current_session = session

        # 3) Executores (agentes)
        steps: list[StudyStep] = self.planner.build_plan(req.topic, req.level, req.goal)
        first = steps[0]

        tutor_output = self.tutor.explain(
            req.topic, req.level, req.goal,
            first.title, first.prompt
        )

        # 4) Resposta estruturada para o cliente
        return {
            "plan": [{"title": s.title, "prompt": s.prompt} for s in steps],
            "current_step": {"title": first.title, "prompt": first.prompt},
            "tutor_output": tutor_output,
            "session_id": session.session_id,  # útil para debug/inspeção
        }

    def receive_answer(self, step_title: str, prompt: str, answer: str) -> None:
        """
        Registra a resposta do aluno no Portfólio (sessão atual).
        """
        if not self.current_session:
            raise RuntimeError("Nenhuma sessão ativa. Chame start() antes de receive_answer().")

        record = StepRecord(
            step_title=step_title,
            prompt=prompt,
            student_answer=answer,
        )
        self.current_session.add_step(record)

    def _validate(self, req: StudyRequest) -> None:
        if not req.topic.strip():
            raise ValueError("topic vazio")
        if not req.level.strip():
            raise ValueError("level vazio")
        if not req.goal.strip():
            raise ValueError("goal vazio")