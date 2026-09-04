from datetime import datetime, UTC
from typing import Any


class AgentMemory:
    """
    Temporary in-memory agent memory.

    Future migration:
    - SQLite
    - PostgreSQL
    - Vector DB
    - Neuro SAN shared memory
    """

    def __init__(self):
        self._memory: list[
            dict[str, Any]
        ] = []

    def remember(
        self,
        case_id: str,
        agent: str,
        insight: str,
        confidence: float,
    ) -> dict[str, Any]:

        item = {
            "case_id": case_id,
            "agent": agent,
            "insight": insight,
            "confidence": round(
                float(confidence),
                2,
            ),
            "created_at": (
                datetime.now(UTC)
                .isoformat()
            ),
        }

        self._memory.append(
            item
        )

        return item

    def get_case_memory(
        self,
        case_id: str,
    ) -> list[dict[str, Any]]:

        return [
            item
            for item in self._memory
            if item["case_id"] == case_id
        ]

    def get_agent_memory(
        self,
        agent: str,
    ) -> list[dict[str, Any]]:

        return [
            item
            for item in self._memory
            if item["agent"] == agent
        ]

    def get_high_confidence(
        self,
        minimum: float = 0.75,
    ) -> list[dict[str, Any]]:

        return [
            item
            for item in self._memory
            if item["confidence"] >= minimum
        ]

    def count(
        self,
    ) -> int:

        return len(
            self._memory
        )

    def clear(
        self,
    ) -> None:

        self._memory.clear()

    def summary(
        self,
    ) -> dict[str, Any]:

        return {
            "total_memories": len(
                self._memory
            ),
            "high_confidence_memories": len(
                self.get_high_confidence()
            ),
        }


memory_store = AgentMemory()