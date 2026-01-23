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


@dataclass
class StudentPortfolio:
    sessions: Dict[str, StudySession] = field(default_factory=dict)

    def add_session(self, session: StudySession) -> None:
        self.sessions[session.session_id] = session

    def get_session(self, session_id: str) -> StudySession:
        if session_id not in self.sessions:
            raise ValueError(f"Session not found: {session_id}")
        return self.sessions[session_id]

    def record_step(
        self,
        session_id: str,
        step_index: int,
        student_answer: str,
    ) -> StepRecord:
        session = self.get_session(session_id)
        record = StepRecord(
            step_index=step_index,
            student_answer=student_answer,
        )
        session.add_record(record)
        return record
