from __future__ import annotations

"""Small account editor for class demo accounts.

Examples:
    python tools/manage_demo_accounts.py list
    python tools/manage_demo_accounts.py set-password shahreare newpass123
    python tools/manage_demo_accounts.py upsert alice "Alice" pass123
"""

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ACCOUNT_PATH = ROOT / "data" / "demo_accounts.json"


def load_accounts() -> list[dict[str, Any]]:
    if not ACCOUNT_PATH.exists():
        return []
    data = json.loads(ACCOUNT_PATH.read_text(encoding="utf-8"))
    return data if isinstance(data, list) else []


def save_accounts(accounts: list[dict[str, Any]]) -> None:
    ACCOUNT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ACCOUNT_PATH.write_text(json.dumps(accounts, indent=2, sort_keys=True), encoding="utf-8")


def find_account(accounts: list[dict[str, Any]], username: str) -> dict[str, Any] | None:
    username = username.strip().lower()
    for account in accounts:
        if str(account.get("username", "")).lower() == username:
            return account
    return None


def list_accounts() -> None:
    for account in load_accounts():
        port = account.get("server_port") or ""
        print(f"{account.get('username',''):12} {account.get('display_name',''):14} {account.get('password',''):10} {port}")


def set_password(username: str, password: str) -> None:
    accounts = load_accounts()
    account = find_account(accounts, username)
    if account is None:
        raise SystemExit(f"No account named {username}")
    account["password"] = password
    save_accounts(accounts)
    print(f"Updated password for {username}.")


def upsert(username: str, display_name: str, password: str, avatar_id: str = "") -> None:
    accounts = load_accounts()
    account = find_account(accounts, username)
    if account is None:
        account = {
            "username": username.strip().lower(),
            "country": "USA",
            "joined_year": 2026,
            "level": 1,
            "favorite_genre": "Arcade",
            "total_sessions": 0,
            "total_wins": 0,
            "status": "Online",
            "bio": "Class account for Scorpions Arcade.",
            "role": "Student",
            "student_number": None,
            "server_port": None,
        }
        accounts.append(account)
    account["display_name"] = display_name
    account["password"] = password
    account["avatar_id"] = avatar_id or f"avatar_{username.strip().lower()}"
    save_accounts(accounts)
    print(f"Saved account {username}.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Manage Scorpions Arcade class accounts.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list")
    password_parser = sub.add_parser("set-password")
    password_parser.add_argument("username")
    password_parser.add_argument("password")
    upsert_parser = sub.add_parser("upsert")
    upsert_parser.add_argument("username")
    upsert_parser.add_argument("display_name")
    upsert_parser.add_argument("password")
    upsert_parser.add_argument("--avatar-id", default="")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.command == "list":
        list_accounts()
    elif args.command == "set-password":
        set_password(args.username, args.password)
    elif args.command == "upsert":
        upsert(args.username, args.display_name, args.password, args.avatar_id)


if __name__ == "__main__":
    main()
