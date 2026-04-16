# core/storage.py
import json
import os
from typing import Any, Dict

from core.portfolio import StudentPortfolio, StudySession, StepRecord


def _ensure_parent_dir(path: str) -> None:
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)


def portfolio_to_dict(portfolio: StudentPortfolio) -> Dict[str, Any]:
    return {
        "sessions": {
            session_id: {
                "session_id": s.session_id,
                "records": [
                    {
                        "step_index": r.step_index,
                        "student_answer": r.student_answer,
                        "created_at": r.created_at,
                    }
                    for r in s.records
                ],
            }
            for session_id, s in portfolio.sessions.items()
        }
    }


def portfolio_from_dict(data: Dict[str, Any]) -> StudentPortfolio:
    portfolio = StudentPortfolio()

    sessions = data.get("sessions", {}) or {}
    for session_id, sdata in sessions.items():
        # tolerante: se não tiver session_id dentro, usamos a key do dict
        sid = sdata.get("session_id") or session_id
        session = StudySession(session_id=sid)

        for rdata in (sdata.get("records", []) or []):
            record = StepRecord(
                step_index=int(rdata.get("step_index", 0)),
                student_answer=str(rdata.get("student_answer", "")),
                created_at=str(rdata.get("created_at", "")) or StepRecord(step_index=0, student_answer="").created_at,
            )
            session.add_record(record)

        portfolio.add_session(session)

    return portfolio


def load_portfolio(path: str) -> StudentPortfolio:
    if not os.path.exists(path):
        return StudentPortfolio()

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        return StudentPortfolio()

    return portfolio_from_dict(data)


def save_portfolio(portfolio: StudentPortfolio, path: str) -> None:
    _ensure_parent_dir(path)
    data = portfolio_to_dict(portfolio)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
