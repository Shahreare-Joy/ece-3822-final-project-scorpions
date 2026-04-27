from __future__ import annotations

"""Persistent local account storage for demo-ready client login.

Purpose:
    The final class project should authenticate through the Python platform
    server, and later through whichever persistence/design the team chooses.
    For the live UI demo, this file gives the launcher a safe local account
    source that survives closing and reopening the app.

Where to edit:
    Edit data/demo_accounts.json directly, or use tools/manage_demo_accounts.py.
    Do not hardcode classmates inside screen files.
"""

import json
from pathlib import Path
from typing import Any

from client.models import Player


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ACCOUNT_PATH = PROJECT_ROOT / "data" / "demo_accounts.json"


def _default_demo_records(count: int = 22) -> list[dict[str, Any]]:
    """Return editable class roster accounts.

    Passwords are intentionally simple because this is a local demo file, not
    production auth. The platform_server/accounts.py area is where the team can
    later replace this with hashed server-side account records.
    """

    _ = count
    return [
        _class_account("evan", "Evan", "ave428"),
        _class_account("ibrahim", "Ibrahim", "bri517"),
        _class_account("mennah", "Mennah", "enm246"),
        _class_account("deven", "Deven", "ved391"),
        _class_account("paul", "Paul", "uap604"),
        _class_account("jude", "Jude", "dej738"),
        _class_account("michael", "Michael", "cim829"),
        _class_account("shahreare", "Shahreare", "has068", student_number=68, server_port=50068, bio="Team lead and Scorpions Arcade host."),
        _class_account("kevin", "Kevin", "vek069", student_number=69, server_port=50069),
        _class_account("richard", "Richard", "hri412"),
        _class_account("thomas", "Thomas", "hot585"),
        _class_account("ellie", "Ellie", "lei734"),
        _class_account("ryan", "Ryan", "ayr260"),
        _class_account("emmanuel", "Emmanuel", "mem913"),
        _class_account("hamza", "Hamza", "amh075", student_number=75, server_port=50075),
        _class_account("damien", "Damien", "mad632"),
        _class_account("vraj", "Vraj", "arv447"),
        _class_account("owen", "Owen", "ewo524"),
        _class_account("minju", "Minju", "imn881"),
        _class_account("santiago", "Santiago", "nas302"),
        _class_account("kimberly", "Kimberly", "mik990"),
        _class_account("mykai", "Mykai", "ykm082", student_number=82, server_port=50082),
        _class_account("nicholas", "Nicholas", "cin672"),
        _class_account("chuqi", "Chuqi", "qcu231", role="TA"),
        _class_account("sal", "Sal", "als911", role="Professor"),
    ]


def _class_account(
    username: str,
    display_name: str,
    password: str,
    student_number: int | None = None,
    server_port: int | None = None,
    role: str = "Student",
    bio: str | None = None,
) -> dict[str, Any]:
    """Build one class account record for data/demo_accounts.json."""

    return {
        "username": username,
        "display_name": display_name,
        "password": password,
        "country": "USA",
        "joined_year": 2026,
        "level": 8 if role == "Student" else 20,
        "favorite_genre": "Arcade",
        "total_sessions": 0,
        "total_wins": 0,
        "status": "Online",
        "bio": bio or f"{role} account for Scorpions Arcade class play.",
        "avatar_id": f"avatar_{username}",
        "role": role,
        "student_number": student_number,
        "server_port": server_port,
    }


class DemoAccountStore:
    """Load and save editable demo accounts from data/demo_accounts.json."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or DEFAULT_ACCOUNT_PATH

    def ensure_file(self) -> None:
        if self.path.exists():
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.save_records(_default_demo_records())

    def load_records(self) -> list[dict[str, Any]]:
        self.ensure_file()
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{self.path} contains invalid JSON: {exc}") from exc
        if not isinstance(data, list):
            raise ValueError(f"{self.path} must contain a JSON list of accounts.")
        return [record for record in data if isinstance(record, dict)]

    def save_records(self, records: list[dict[str, Any]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(records, indent=2, sort_keys=True), encoding="utf-8")

    def load_players(self) -> dict[str, Player]:
        players: dict[str, Player] = {}
        for record in self.load_records():
            player = self.record_to_player(record)
            if player.username:
                players[player.username] = player
        return players

    def add_or_update_player(self, player: Player) -> None:
        records = self.load_records()
        updated = False
        player_record = self.player_to_record(player)
        for index, record in enumerate(records):
            if str(record.get("username", "")).strip().lower() == player.username:
                records[index] = player_record
                updated = True
                break
        if not updated:
            records.append(player_record)
        self.save_records(records)

    def username_exists(self, username: str) -> bool:
        username = username.strip().lower()
        return any(str(record.get("username", "")).strip().lower() == username for record in self.load_records())

    def delete_username(self, username: str) -> None:
        username = username.strip().lower()
        records = [record for record in self.load_records() if str(record.get("username", "")).strip().lower() != username]
        self.save_records(records)

    @staticmethod
    def record_to_player(record: dict[str, Any]) -> Player:
        username = str(record.get("username", "")).strip().lower()
        display_name = str(record.get("display_name") or username or "Player").strip()
        return Player(
            username=username,
            display_name=display_name,
            password=str(record.get("password", "")),
            country=str(record.get("country", "USA")),
            joined_year=int(record.get("joined_year", 2026) or 2026),
            level=int(record.get("level", 1) or 1),
            favorite_genre=str(record.get("favorite_genre", "Arcade")),
            total_sessions=int(record.get("total_sessions", 0) or 0),
            total_wins=int(record.get("total_wins", 0) or 0),
            status=str(record.get("status", "Online")),
            bio=str(record.get("bio", "Scorpions Arcade player.")),
            avatar_id=str(record.get("avatar_id", "")),
        )

    @staticmethod
    def player_to_record(player: Player) -> dict[str, Any]:
        return {
            "username": player.username,
            "display_name": player.display_name,
            "password": player.password,
            "country": player.country,
            "joined_year": player.joined_year,
            "level": player.level,
            "favorite_genre": player.favorite_genre,
            "total_sessions": player.total_sessions,
            "total_wins": player.total_wins,
            "status": player.status,
            "bio": player.bio,
            "avatar_id": player.avatar_id,
        }
