from __future__ import annotations


VALID_OUTCOMES = {"Win", "Loss", "Draw", "Quit", "Finished", "DNF"}


class CleaningHooks:
    """Reusable cleanup rules for dataset-facing UI/demo helpers."""

    def normalize_record(self, record: dict[str, object]) -> dict[str, object]:
        '''normalize shared fields in a dataset record'''

        # TODO (DONE)(CLEANING): Normalize names, parse timestamps, coerce scores.

        # copy record so original data is not changed
        cleaned = dict(record)

        # normalize username spacing and case
        if "username" in cleaned:
            cleaned["username"] = str(cleaned["username"]).strip().lower()

        # normalize display name spacing
        if "display_name" in cleaned:
            cleaned["display_name"] = " ".join(str(cleaned["display_name"]).split())

        # convert numeric fields to safe non-negative integers
        for numeric_field in ("score", "duration_seconds", "total_plays", "currently_playing"):
            if numeric_field in cleaned:
                try:
                    cleaned[numeric_field] = max(0, int(cleaned[numeric_field]))
                except (TypeError, ValueError):
                    cleaned[numeric_field] = 0

        return cleaned

    def normalize_player_record(self, record: dict[str, object]) -> dict[str, object]:
        '''normalize player-specific fields'''

        # TODO (DONE)(CLEANING): Handle missing usernames and display-name capitalization.

        # apply shared normalization first
        cleaned = self.normalize_record(record)

        # use player_id as fallback username
        if not cleaned.get("username") and cleaned.get("player_id"):
            cleaned["username"] = str(cleaned["player_id"]).lower()

        # add fallback display name if missing
        cleaned.setdefault("display_name", str(cleaned.get("username", "Unknown Player")).title())

        return cleaned

    def normalize_session_record(self, record: dict[str, object]) -> dict[str, object]:
        '''normalize session-specific fields'''

        # TODO (DONE)(CLEANING): Handle bad session fields and invalid outcomes.

        # apply shared normalization first
        cleaned = self.normalize_record(record)

        # normalize outcome label
        outcome = str(cleaned.get("outcome", "Finished"))
        cleaned["outcome"] = outcome if outcome in VALID_OUTCOMES else "Finished"

        # add safe default values
        cleaned.setdefault("duration_seconds", 0)
        cleaned.setdefault("score", 0)

        return cleaned

    def reject_reason(self, record: dict[str, object]) -> str | None:
        '''return reason if record should be rejected'''

        # TODO (DONE)(CLEANING): Return a reason string for dropped records.

        # reject empty record
        if not record:
            return "empty record"

        # reject player records with missing player_id
        if "player_id" in record and not str(record.get("player_id", "")).strip():
            return "missing player_id"

        # reject session records with missing session_id
        if "session_id" in record and not str(record.get("session_id", "")).strip():
            return "missing session_id"

        # reject chat messages with empty text
        if "message_id" in record and not str(record.get("text", "")).strip():
            return "empty chat message"

        return None