from datetime import UTC, datetime
from typing import Any


ALLOWED_EVIDENCE_STATUSES = {
    "UNVERIFIED",
    "VERIFIED",
    "REJECTED",
}


ALLOWED_SOURCE_KINDS = {
    "USER_INPUT",
    "DETERMINISTIC_TOOL",
    "UPLOADED_DOCUMENT",
    "EXTERNAL_SOURCE",
    "AGENT_INFERENCE",
}


class EvidenceStore:
    """
    Case-scoped in-memory evidence store.

    Evidence from one case is never included in another case.

    This version remains in memory. Evidence will therefore disappear
    when FastAPI restarts. A later database-backed implementation can
    preserve the same public methods.
    """

    def __init__(self) -> None:
        self._evidence_by_case: dict[
            str,
            list[dict[str, Any]],
        ] = {}

    def _get_case_items(
        self,
        case_id: str,
    ) -> list[dict[str, Any]]:
        """
        Return the internal evidence collection for one case,
        creating it when necessary.
        """

        if case_id not in self._evidence_by_case:
            self._evidence_by_case[
                case_id
            ] = []

        return self._evidence_by_case[
            case_id
        ]

    def _normalise_confidence(
        self,
        confidence: Any,
    ) -> float:
        """
        Convert confidence into a value between 0 and 1.
        """

        try:
            value = float(confidence)
        except (TypeError, ValueError):
            value = 0.0

        return round(
            min(
                max(value, 0.0),
                1.0,
            ),
            2,
        )

    def _normalise_status(
        self,
        status: Any,
    ) -> str:
        """
        Restrict evidence status to supported values.
        """

        cleaned = str(
            status or "UNVERIFIED"
        ).strip().upper()

        if cleaned not in ALLOWED_EVIDENCE_STATUSES:
            return "UNVERIFIED"

        return cleaned

    def _normalise_source_kind(
        self,
        source_kind: Any,
    ) -> str:
        """
        Restrict source kind to supported values.
        """

        cleaned = str(
            source_kind or "AGENT_INFERENCE"
        ).strip().upper()

        if cleaned not in ALLOWED_SOURCE_KINDS:
            return "AGENT_INFERENCE"

        return cleaned

    def add(
        self,
        case_id: str,
        claim: str,
        source: str,
        confidence: float,
        agent: str,
        *,
        source_kind: str = "AGENT_INFERENCE",
        status: str = "UNVERIFIED",
        evidence_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Add one case-scoped evidence record.

        AGENT_INFERENCE is not treated as verified source-backed
        evidence unless another trusted process explicitly verifies it.
        """

        cleaned_case_id = str(
            case_id
        ).strip()

        cleaned_claim = str(
            claim
        ).strip()

        cleaned_source = str(
            source
        ).strip()

        cleaned_agent = str(
            agent
        ).strip()

        if not cleaned_case_id:
            raise ValueError(
                "case_id is required."
            )

        if not cleaned_claim:
            raise ValueError(
                "Evidence claim is required."
            )

        if not cleaned_source:
            raise ValueError(
                "Evidence source is required."
            )

        if not cleaned_agent:
            raise ValueError(
                "Evidence agent is required."
            )

        items = self._get_case_items(
            cleaned_case_id
        )

        item_id = (
            str(evidence_id).strip()
            if evidence_id
            else (
                f"EV-{len(items) + 1:04d}"
            )
        )

        item = {
            "id": item_id,
            "case_id": cleaned_case_id,
            "claim": cleaned_claim,
            "source": cleaned_source,
            "source_kind": (
                self._normalise_source_kind(
                    source_kind
                )
            ),
            "confidence": (
                self._normalise_confidence(
                    confidence
                )
            ),
            "agent": cleaned_agent,
            "status": (
                self._normalise_status(
                    status
                )
            ),
            "metadata": (
                dict(metadata)
                if isinstance(
                    metadata,
                    dict,
                )
                else {}
            ),
            "created_at": (
                datetime.now(UTC)
                .isoformat()
            ),
        }

        items.append(item)

        return dict(item)

    def add_user_input(
        self,
        case_id: str,
        claim: str,
        *,
        label: str = "User-supplied case information",
    ) -> dict[str, Any]:
        """
        Store information explicitly supplied by the user.

        User input is traceable but remains unverified unless it is
        independently validated.
        """

        return self.add(
            case_id=case_id,
            claim=claim,
            source=label,
            confidence=1.0,
            agent="case_understanding",
            source_kind="USER_INPUT",
            status="UNVERIFIED",
        )

    def add_tool_result(
        self,
        case_id: str,
        claim: str,
        source: str,
        agent: str,
        *,
        confidence: float = 1.0,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Store an output from a deterministic calculation tool.

        Deterministic tool output is marked VERIFIED because its
        provenance is the named local calculation tool. This does not
        mean the user-supplied assumptions themselves are verified.
        """

        return self.add(
            case_id=case_id,
            claim=claim,
            source=source,
            confidence=confidence,
            agent=agent,
            source_kind="DETERMINISTIC_TOOL",
            status="VERIFIED",
            metadata=metadata,
        )

    def all(
        self,
        case_id: str,
    ) -> list[dict[str, Any]]:
        """
        Return a copy of all evidence for one case.
        """

        return [
            dict(item)
            for item in self._get_case_items(
                case_id
            )
        ]

    def verified(
        self,
        case_id: str,
    ) -> list[dict[str, Any]]:
        """
        Return verified evidence for one case.
        """

        return [
            dict(item)
            for item in self._get_case_items(
                case_id
            )
            if item["status"] == "VERIFIED"
        ]

    def unverified(
        self,
        case_id: str,
    ) -> list[dict[str, Any]]:
        """
        Return unverified evidence for one case.
        """

        return [
            dict(item)
            for item in self._get_case_items(
                case_id
            )
            if item["status"] == "UNVERIFIED"
        ]

    def rejected(
        self,
        case_id: str,
    ) -> list[dict[str, Any]]:
        """
        Return rejected evidence for one case.
        """

        return [
            dict(item)
            for item in self._get_case_items(
                case_id
            )
            if item["status"] == "REJECTED"
        ]

    def get_by_agent(
        self,
        case_id: str,
        agent: str,
    ) -> list[dict[str, Any]]:
        """
        Return evidence generated by one agent for one case.
        """

        cleaned_agent = str(
            agent
        ).strip()

        return [
            dict(item)
            for item in self._get_case_items(
                case_id
            )
            if item["agent"] == cleaned_agent
        ]

    def get_by_source_kind(
        self,
        case_id: str,
        source_kind: str,
    ) -> list[dict[str, Any]]:
        """
        Return evidence matching a source category.
        """

        cleaned_kind = (
            self._normalise_source_kind(
                source_kind
            )
        )

        return [
            dict(item)
            for item in self._get_case_items(
                case_id
            )
            if item["source_kind"]
            == cleaned_kind
        ]

    def verify(
        self,
        case_id: str,
        evidence_id: str,
    ) -> dict[str, Any]:
        """
        Mark one evidence item as verified.
        """

        for item in self._get_case_items(
            case_id
        ):
            if item["id"] == evidence_id:
                item["status"] = "VERIFIED"
                item["verified_at"] = (
                    datetime.now(UTC)
                    .isoformat()
                )

                return dict(item)

        raise KeyError(
            "Evidence item not found."
        )

    def reject(
        self,
        case_id: str,
        evidence_id: str,
        reason: str,
    ) -> dict[str, Any]:
        """
        Reject one evidence item with a recorded reason.
        """

        cleaned_reason = str(
            reason
        ).strip()

        if not cleaned_reason:
            raise ValueError(
                "A rejection reason is required."
            )

        for item in self._get_case_items(
            case_id
        ):
            if item["id"] == evidence_id:
                item["status"] = "REJECTED"
                item["rejection_reason"] = (
                    cleaned_reason
                )
                item["rejected_at"] = (
                    datetime.now(UTC)
                    .isoformat()
                )

                return dict(item)

        raise KeyError(
            "Evidence item not found."
        )

    def count(
        self,
        case_id: str,
    ) -> int:
        """
        Count all evidence records for one case.
        """

        return len(
            self._get_case_items(
                case_id
            )
        )

    def average_confidence(
        self,
        case_id: str,
        *,
        verified_only: bool = False,
    ) -> float:
        """
        Calculate average confidence for one case.

        Confidence is model or process metadata. It is not proof that
        the underlying claim is correct.
        """

        items = (
            self.verified(case_id)
            if verified_only
            else self.all(case_id)
        )

        if not items:
            return 0.0

        return round(
            sum(
                float(
                    item["confidence"]
                )
                for item in items
            )
            / len(items),
            2,
        )

    def validate(
        self,
        case_id: str,
    ) -> dict[str, Any]:
        """
        Validate the evidence gate for one case.

        PASS requires at least one VERIFIED item and no weak verified
        evidence. A research plan or an agent inference is not treated
        as verified evidence by default.
        """

        all_items = self.all(
            case_id
        )

        verified_items = self.verified(
            case_id
        )

        unverified_items = self.unverified(
            case_id
        )

        rejected_items = self.rejected(
            case_id
        )

        weak_verified = [
            item
            for item in verified_items
            if float(
                item["confidence"]
            )
            < 0.5
        ]

        if not verified_items:
            status = "REVIEW_REQUIRED"
            reason = (
                "No verified evidence is available "
                "for this case."
            )

        elif weak_verified:
            status = "REVIEW_REQUIRED"
            reason = (
                "One or more verified evidence items "
                "have low confidence."
            )

        else:
            status = "PASS"
            reason = (
                "At least one verified evidence item "
                "is available and no weak verified "
                "item was detected."
            )

        return {
            "case_id": case_id,
            "status": status,
            "reason": reason,
            "total_evidence": len(
                all_items
            ),
            "verified_evidence_count": len(
                verified_items
            ),
            "unverified_evidence_count": len(
                unverified_items
            ),
            "rejected_evidence_count": len(
                rejected_items
            ),
            "average_confidence": (
                self.average_confidence(
                    case_id
                )
            ),
            "verified_average_confidence": (
                self.average_confidence(
                    case_id,
                    verified_only=True,
                )
            ),
            "weak_verified_count": len(
                weak_verified
            ),
            "weak_verified_evidence": (
                weak_verified
            ),
            "verified_evidence": (
                verified_items
            ),
        }

    def clear_case(
        self,
        case_id: str,
    ) -> None:
        """
        Remove evidence for one case only.
        """

        self._evidence_by_case.pop(
            case_id,
            None,
        )

    def clear_all(
        self,
    ) -> None:
        """
        Remove evidence for every case.

        This should only be used in tests or controlled development.
        """

        self._evidence_by_case.clear()

    def case_ids(
        self,
    ) -> list[str]:
        """
        Return case IDs currently represented in the store.
        """

        return list(
            self._evidence_by_case.keys()
        )


evidence_store = EvidenceStore()