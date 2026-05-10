"""SQLite persistence helpers for SmartClasse."""

import json
import os
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from src.config import settings


Base = declarative_base()


def _build_engine():
    connect_args = {}
    if settings.DATABASE_URL.startswith("sqlite"):
        connect_args["check_same_thread"] = False

    return create_engine(settings.DATABASE_URL, connect_args=connect_args)


engine = _build_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)


class StudentProfileRecord(Base):
    __tablename__ = "student_profiles"

    student_id = Column(String, primary_key=True, index=True)
    profile_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class ExerciseAttemptRecord(Base):
    __tablename__ = "exercise_attempts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String, index=True, nullable=False)
    exercise_id = Column(String, index=True, nullable=False)
    subject = Column(String, nullable=True)
    skill = Column(String, nullable=True)
    response_json = Column(Text, nullable=False)
    is_correct = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class DiagnosticSessionRecord(Base):
    __tablename__ = "diagnostic_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String, index=True, nullable=False)
    responses_json = Column(Text, nullable=False)
    analysis_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


def init_db() -> None:
    database_path = settings.DATABASE_URL.split("///")[-1]
    directory = os.path.dirname(database_path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    Base.metadata.create_all(bind=engine)


@contextmanager
def session_scope():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def _dumps(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, default=str)


def _loads(payload: str) -> Any:
    return json.loads(payload)


def upsert_student_profile(profile: Dict[str, Any]) -> Dict[str, Any]:
    student_id = profile["student_id"]
    now = datetime.utcnow()

    with session_scope() as session:
        record = session.get(StudentProfileRecord, student_id)
        if record is None:
            session.add(
                StudentProfileRecord(
                    student_id=student_id,
                    profile_json=_dumps(profile),
                    created_at=now,
                    updated_at=now,
                )
            )
        else:
            record.profile_json = _dumps(profile)
            record.updated_at = now

    return profile


def load_student_profile(student_id: str) -> Optional[Dict[str, Any]]:
    with session_scope() as session:
        record = session.get(StudentProfileRecord, student_id)
        if record is None:
            return None

        profile = _loads(record.profile_json)
        profile["created_at"] = record.created_at.isoformat()
        profile["updated_at"] = record.updated_at.isoformat()
        return profile


def record_diagnostic_session(student_id: str, responses: List[Dict[str, Any]], analysis: Dict[str, Any]) -> Dict[str, Any]:
    payload = {
        "student_id": student_id,
        "responses": responses,
        "analysis": analysis,
        "created_at": datetime.utcnow().isoformat(),
    }

    with session_scope() as session:
        session.add(
            DiagnosticSessionRecord(
                student_id=student_id,
                responses_json=_dumps(responses),
                analysis_json=_dumps(analysis),
            )
        )

    return payload


def record_exercise_attempt(
    student_id: str,
    exercise_id: str,
    response: Any,
    is_correct: bool,
    subject: Optional[str] = None,
    skill: Optional[str] = None,
) -> Dict[str, Any]:
    payload = {
        "student_id": student_id,
        "exercise_id": exercise_id,
        "response": response,
        "is_correct": is_correct,
        "subject": subject,
        "skill": skill,
        "created_at": datetime.utcnow().isoformat(),
    }

    with session_scope() as session:
        session.add(
            ExerciseAttemptRecord(
                student_id=student_id,
                exercise_id=exercise_id,
                subject=subject,
                skill=skill,
                response_json=_dumps(response),
                is_correct=is_correct,
            )
        )

    return payload


def load_student_attempts(student_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    with session_scope() as session:
        rows = (
            session.query(ExerciseAttemptRecord)
            .filter(ExerciseAttemptRecord.student_id == student_id)
            .order_by(ExerciseAttemptRecord.created_at.desc())
            .limit(limit)
            .all()
        )

    attempts: List[Dict[str, Any]] = []
    for row in rows:
        attempts.append(
            {
                "exercise_id": row.exercise_id,
                "subject": row.subject,
                "skill": row.skill,
                "response": _loads(row.response_json),
                "is_correct": row.is_correct,
                "created_at": row.created_at.isoformat(),
            }
        )
    return attempts


def load_student_progress(student_id: str) -> Dict[str, Any]:
    profile = load_student_profile(student_id)
    attempts = load_student_attempts(student_id)

    correct_count = sum(1 for attempt in attempts if attempt["is_correct"])
    total_count = len(attempts)
    success_rate = (correct_count / total_count * 100) if total_count > 0 else 0

    return {
        "student_id": student_id,
        "profile": profile,
        "statistics": {
            "total_exercises": total_count,
            "correct_answers": correct_count,
            "success_rate_percent": round(success_rate, 2),
        },
        "recent_history": attempts[:5],
    }
