from __future__ import annotations


class CleaningHooks:
    """Starter placeholder for messy-record cleanup rules.

    TODO(CLEANING): Implement project-specific rules here after your team
    creates the synthetic dataset. Keep raw records, cleaning rules, and final
    model construction separate so the report can explain each step.
    """

    def normalize_record(self, record: dict[str, object]) -> dict[str, object]:
        # TODO(CLEANING): Normalize names, parse timestamps, coerce scores to
        # integers, repair known genre aliases, and document every rule.
        return dict(record)

    def normalize_player_record(self, record: dict[str, object]) -> dict[str, object]:
        # TODO(CLEANING): Handle missing usernames, duplicate players, invalid
        # countries, and inconsistent display-name capitalization.
        return self.normalize_record(record)

    def normalize_session_record(self, record: dict[str, object]) -> dict[str, object]:
        # TODO(CLEANING): Handle missing session_id, bad game_id references,
        # negative scores, malformed duration, and invalid win/loss outcomes.
        return self.normalize_record(record)

    def reject_reason(self, record: dict[str, object]) -> str | None:
        # TODO(CLEANING): Return a reason string for dropped records so the
        # final report can count and justify removed noisy rows.
        _ = record
        return None
