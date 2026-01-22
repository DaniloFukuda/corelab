# core/portfolio.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


# Representa uma resposta do aluno a um passo
@dataclass
class StepRecord:
    step_title: str
    prompt: str
    student_answer: str
    timestamp: datetime = field(default_factory=datetime.utcnow)


# Representa uma sessão de estudo (tema + objetivo)
@dataclass
class StudySession:
    session_id: str
    topic: str
    goal: str
    started_at: datetime = field(default_factory=datetime.utcnow)
    steps: List[StepRecord] = field(default_factory=list)

    def add_step(self, record: StepRecord) -> None:
        self.steps.append(record)


# Objeto central: Portfólio do Aluno
@dataclass
class StudentPortfolio:
    student_id: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    sessions: List[StudySession] = field(default_factory=list)

    def start_session(self, session: StudySession) -> None:
        self.sessions.append(session)

    def current_session(self) -> Optional[StudySession]:
        if not self.sessions:
            return None
        return self.sessions[-1]
