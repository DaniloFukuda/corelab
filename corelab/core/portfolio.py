from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime


# =========================
# REGISTROS (HISTÓRICO)
# =========================

@dataclass(frozen=True)
class StepRecord:
    step_index: int
    student_answer: str
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class StudySession:
    session_id: str
    records: List[StepRecord] = field(default_factory=list)

    def add_record(self, record: StepRecord) -> None:
        self.records.append(record)

    def last_record(self) -> Optional[StepRecord]:
        if not self.records:
            return None
        return self.records[-1]

    def last_answer_text(self) -> Optional[str]:
        last = self.last_record()
        if last is None:
            return None
        return last.student_answer

    # -------------------------
    # Utilitários por step
    # -------------------------

    def count_attempts(self, step_index: int) -> int:
        """Quantas tentativas já foram registradas para esse step."""
        return sum(1 for r in self.records if r.step_index == step_index)

    def last_answer_for_step(self, step_index: int) -> Optional[str]:
        """Última resposta registrada especificamente para esse step."""
        for r in reversed(self.records):
            if r.step_index == step_index:
                return r.student_answer
        return None


@dataclass
class StudentPortfolio:
    sessions: Dict[str, StudySession] = field(default_factory=dict)

    def add_session(self, session: StudySession) -> None:
        self.sessions[session.session_id] = session

    def get_session(self, session_id: str) -> StudySession:
        if session_id not in self.sessions:
            raise ValueError(f"Session not found: {session_id}")
        return self.sessions[session_id]

    # -------------------------
    # NOVO: get_or_create_session
    # -------------------------

    def get_or_create_session(self, session_id: str) -> StudySession:
        """Retorna a sessão; se não existir, cria uma nova."""
        if session_id not in self.sessions:
            self.sessions[session_id] = StudySession(session_id=session_id)
        return self.sessions[session_id]

    def record_step(
        self,
        session_id: str,
        step_index: int,
        student_answer: str,
    ) -> StepRecord:
        # NOVO: em vez de explodir se não existir, cria a sessão automaticamente
        session = self.get_or_create_session(session_id)
        record = StepRecord(
            step_index=step_index,
            student_answer=student_answer,
        )
        session.add_record(record)
        return record
