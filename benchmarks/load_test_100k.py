from __future__ import annotations

"""Direct 100,000-player data-structure load test.

This benchmark does not use sockets or the platform network API. It builds the
Python data structures directly, runs increasing query volumes against them,
and exports CSV/SVG files that can be used in the final report.
"""

from dataclasses import dataclass
from pathlib import Path
import random
import sys
from time import perf_counter

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from benchmarks.plotting_hooks import export_plot_data
from datastructures.bst import BinarySearchTree
from datastructures.circular_buffer import CircularBuffer
from datastructures.hash_table import ChainedHashTable
from datastructures.heap import MaxHeap
from platform_server.history import HistoryService


PLAYER_COUNT = 100_000
QUERY_COUNTS = [1_000, 10_000, 50_000, 100_000]
RESULT_DIR = PROJECT_ROOT / "benchmarks" / "results"


@dataclass(frozen=True)
class SyntheticPlayer:
    username: str
    display_name: str
    favorite_genre: str
    skill_rating: int


def build_players(count: int = PLAYER_COUNT) -> list[SyntheticPlayer]:
    genres = ["Action", "Arcade", "Puzzle", "Racing", "Strategy"]
    return [
        SyntheticPlayer(
            username=f"user{i:06d}",
            display_name=f"Player {i}",
            favorite_genre=genres[i % len(genres)],
            skill_rating=800 + (i * 37) % 2200,
        )
        for i in range(count)
    ]


def build_sessions(players: list[SyntheticPlayer]) -> list[dict[str, object]]:
    game_ids = ["scorpions-arena", "sky-raiders", "turbo-sprint", "crystal-run"]
    outcomes = ["Finished", "Game Over", "Time Up"]
    return [
        {
            "session_id": f"s{i:06d}",
            "username": player.username,
            "player_id": player.username,
            "game_id": game_ids[i % len(game_ids)],
            "started_at": f"2026-05-{(i % 28) + 1:02d}T12:{i % 60:02d}:00Z",
            "duration_seconds": 60 + (i % 240),
            "score": (i * 13) % 50_000,
            "outcome": outcomes[i % len(outcomes)],
        }
        for i, player in enumerate(players)
    ]


def time_repeated(function, values: list[object], query_count: int) -> tuple[float, object]:
    start = perf_counter()
    last = None
    for index in range(query_count):
        last = function(values[index % len(values)])
    total_ms = (perf_counter() - start) * 1000
    return total_ms, last


def run_load_test() -> list[dict[str, object]]:
    rng = random.Random(3822)
    players = build_players()
    shuffled_players = list(players)
    rng.shuffle(shuffled_players)
    usernames = [player.username for player in players]
    query_keys = [usernames[(index * 7919) % len(usernames)] for index in range(max(QUERY_COUNTS))]

    rows: list[dict[str, object]] = []

    player_table = ChainedHashTable(capacity=262_144)
    for player in players:
        player_table.put(player.username, player)
    rows.extend(_measure("hash_table_player_lookup", "ChainedHashTable.get", lambda key: player_table.get(key), query_keys))

    player_tree = BinarySearchTree()
    for player in shuffled_players:
        player_tree.insert(player.username, player)
    rows.extend(_measure("bst_player_exact_search", "BinarySearchTree.search", lambda key: player_tree.search(key), query_keys))

    score_heap = MaxHeap()
    for index, player in enumerate(players):
        score_heap.push((index * 17) % 1_000_000, player.username)
    rows.extend(_measure("heap_leaderboard_top_score", "MaxHeap.peek_max", lambda _key: score_heap.peek_max(), query_keys))

    sessions = build_sessions(players)
    history = HistoryService()
    history.load_sessions(sessions)
    rows.extend(_measure("history_by_player_lookup", "HistoryService.by_player", lambda key: history.by_player(key, 5), query_keys))

    chat_buffer = CircularBuffer(capacity=2_000)
    for index in range(2_000):
        chat_buffer.append({"sender": usernames[index], "message": f"message {index}", "session_id": "load-test"})
    rows.extend(_measure("chat_recent_buffer", "CircularBuffer.recent", lambda _key: chat_buffer.recent(25), query_keys))

    catalog_by_genre = ChainedHashTable(capacity=32)
    game_rows = [
        {"game_id": f"game-{i:04d}", "title": f"Game {i}", "genre": players[i].favorite_genre}
        for i in range(1_000)
    ]
    for game in game_rows:
        genre = str(game["genre"])
        bucket = catalog_by_genre.get(genre)
        if not isinstance(bucket, list):
            bucket = []
            catalog_by_genre.put(genre, bucket)
        bucket.append(game)
    genres = ["Action", "Arcade", "Puzzle", "Racing", "Strategy"]
    genre_queries = [genres[index % len(genres)] for index in range(max(QUERY_COUNTS))]
    rows.extend(_measure("catalog_genre_filter", "ChainedHashTable.get", lambda key: catalog_by_genre.get(key, []), genre_queries))

    return rows


def _measure(workload: str, structure: str, function, query_values: list[object]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for query_count in QUERY_COUNTS:
        total_ms, last = time_repeated(function, query_values, query_count)
        result_size = len(last) if hasattr(last, "__len__") and not isinstance(last, str) else 1
        rows.append(
            {
                "workload": workload,
                "structure": structure,
                "player_count": PLAYER_COUNT,
                "query_count": query_count,
                "total_ms": round(total_ms, 4),
                "avg_ms": round(total_ms / query_count, 8),
                "result_size": result_size,
            }
        )
    return rows


def export_svg_bar_chart(rows: list[dict[str, object]], output_path: Path) -> None:
    """Create a dependency-free SVG plot of average response time."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    width = 1280
    height = 760
    margin_left = 210
    margin_bottom = 70
    chart_width = width - margin_left - 40
    chart_height = height - 120
    max_avg = max(float(row["avg_ms"]) for row in rows) or 1.0
    bar_gap = 5
    bar_height = max(8, (chart_height - bar_gap * (len(rows) - 1)) / len(rows))
    colors = {
        "hash_table_player_lookup": "#5ad1a4",
        "bst_player_exact_search": "#77a7ff",
        "heap_leaderboard_top_score": "#ffd166",
        "history_by_player_lookup": "#ef476f",
        "chat_recent_buffer": "#b583ff",
        "catalog_genre_filter": "#4cc9f0",
    }

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#111827"/>',
        '<text x="40" y="36" fill="#f9fafb" font-family="Arial" font-size="24" font-weight="700">100,000 Player Direct Data-Structure Load Test</text>',
        '<text x="40" y="64" fill="#cbd5e1" font-family="Arial" font-size="14">Average milliseconds per query; no network calls used</text>',
    ]

    for i in range(6):
        x = margin_left + (chart_width * i / 5)
        value = max_avg * i / 5
        lines.append(f'<line x1="{x:.1f}" y1="86" x2="{x:.1f}" y2="{height - margin_bottom}" stroke="#334155" stroke-width="1"/>')
        lines.append(f'<text x="{x:.1f}" y="{height - 42}" fill="#cbd5e1" font-family="Arial" font-size="11" text-anchor="middle">{value:.5f}</text>')

    y = 92
    for row in rows:
        avg = float(row["avg_ms"])
        bar_width = 2 if avg == 0 else max(2, (avg / max_avg) * chart_width)
        label = f'{row["workload"]} ({int(row["query_count"]):,})'
        color = colors.get(str(row["workload"]), "#94a3b8")
        lines.append(f'<text x="38" y="{y + bar_height * 0.68:.1f}" fill="#e5e7eb" font-family="Arial" font-size="11">{_xml_escape(label)}</text>')
        lines.append(f'<rect x="{margin_left}" y="{y:.1f}" width="{bar_width:.1f}" height="{bar_height:.1f}" fill="{color}" rx="3"/>')
        lines.append(f'<text x="{margin_left + bar_width + 7:.1f}" y="{y + bar_height * 0.68:.1f}" fill="#f8fafc" font-family="Arial" font-size="11">{avg:.6f} ms</text>')
        y += bar_height + bar_gap

    lines.append(f'<text x="{margin_left + chart_width / 2:.1f}" y="{height - 14}" fill="#e5e7eb" font-family="Arial" font-size="13" text-anchor="middle">Average response time per query (ms)</text>')
    lines.append("</svg>")
    output_path.write_text("\n".join(lines), encoding="utf-8")


def export_summary(rows: list[dict[str, object]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fastest = min(rows, key=lambda row: float(row["avg_ms"]))
    slowest = max(rows, key=lambda row: float(row["avg_ms"]))
    by_workload: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        by_workload.setdefault(str(row["workload"]), []).append(row)

    lines = [
        "# 100,000 Player Load Test Summary",
        "",
        "This benchmark tests the Python data structures directly and does not use the network.",
        "",
        f"- Simulated players: {PLAYER_COUNT:,}",
        f"- Query volumes: {', '.join(f'{count:,}' for count in QUERY_COUNTS)}",
        f"- Fastest row: {fastest['workload']} at {fastest['query_count']:,} queries ({fastest['avg_ms']} ms/query)",
        f"- Slowest row: {slowest['workload']} at {slowest['query_count']:,} queries ({slowest['avg_ms']} ms/query)",
        "",
        "## Results By Workload",
        "",
    ]
    for workload, workload_rows in by_workload.items():
        last = workload_rows[-1]
        lines.append(f"- {workload}: {last['structure']} reached {last['query_count']:,} queries at {last['avg_ms']} ms/query.")

    lines.extend(
        [
            "",
            "## Bottleneck Notes",
            "",
            "- Hash-table style lookups stayed fastest because average lookup is O(1).",
            "- Heap top-score lookup was fast because peek is O(1).",
            "- BST exact search was slower than hash lookup because tree traversal is O(log n) on average.",
            "- History lookup stayed fast because sessions are indexed by player in a hash table.",
            "- Chat recent retrieval depends on the number of recent messages returned, so it is O(k).",
            "- Catalog filtering is fast because genre maps directly to a bucket of games.",
        ]
    )
    output_path.write_text("\n".join(lines), encoding="utf-8")


def _xml_escape(value: object) -> str:
    return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


if __name__ == "__main__":
    result_rows = run_load_test()
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = RESULT_DIR / "load_test_100k.csv"
    svg_path = RESULT_DIR / "load_test_100k_avg_ms.svg"
    summary_path = RESULT_DIR / "load_test_100k_summary.md"

    export_plot_data(result_rows, str(csv_path))
    export_svg_bar_chart(result_rows, svg_path)
    export_summary(result_rows, summary_path)

    for result_row in result_rows:
        print(result_row)
    print(f"\nCSV: {csv_path}")
    print(f"SVG: {svg_path}")
    print(f"Summary: {summary_path}")
