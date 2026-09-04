from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from .database import Base


def now_utc() -> datetime:
    return datetime.now(
        timezone.utc
    )


class Case(Base):
    __tablename__ = "cases"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
    )

    title: Mapped[str] = mapped_column(
        String(200)
    )

    decision: Mapped[str] = mapped_column(
        Text
    )

    status: Mapped[str] = mapped_column(
        String(40),
        default="INPUT_REQUIRED",
    )

    assumptions_json: Mapped[str] = mapped_column(
        Text,
        default="{}",
    )

    result_json: Mapped[str] = mapped_column(
        Text,
        default="{}",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=now_utc,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=now_utc,
        onupdate=now_utc,
    )


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
    )

    case_id: Mapped[str] = mapped_column(
        ForeignKey("cases.id"),
        index=True,
    )

    agent: Mapped[str] = mapped_column(
        String(100)
    )

    event_type: Mapped[str] = mapped_column(
        String(80)
    )

    summary: Mapped[str] = mapped_column(
        Text
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=now_utc,
    )


class MemoryEvent(Base):
    """
    Long-term agent memory.

    Used by:
    - research_agent
    - red_team
    - committee
    - orchestrator

    This replaces the temporary
    in-memory memory store later.
    """

    __tablename__ = "memory_events"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
    )

    case_id: Mapped[str] = mapped_column(
        ForeignKey("cases.id"),
        index=True,
    )

    agent: Mapped[str] = mapped_column(
        String(100)
    )

    insight: Mapped[str] = mapped_column(
        Text
    )

    confidence: Mapped[str] = mapped_column(
        String(20),
        default="0.50",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=now_utc,
    )