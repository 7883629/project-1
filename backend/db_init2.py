import json
import sqlite3
from pathlib import Path

DB_PATH = Path("mes.db")
ORDERS_PATH = Path("orders.json")


def create_table(conn: sqlite3.Connection) -> None:
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("""
                 CREATE TABLE IF NOT EXISTS sessions
                 (
                     id         TEXT PRIMARY KEY,
                     created_at TEXT NOT NULL 
                 )
                 """)

    conn.execute("""
                 CREATE TABLE IF NOT EXISTS messages
                 (
                     id         INTEGER PRIMARY KEY AUTOINCREMENT,
                     session_id TEXT NOT NULL REFERENCES sessions(id),
                     role       TEXT NOT NULL CHECK ( role IN ('user', 'assistant')),
                     content    TEXT NOT NULL,
                     created_at TEXT NOT NULL 
                 )
                 """)

    conn.execute("""
                 CREATE INDEX IF NOT EXISTS idx_messages_session_id ON messages(session_id)
                 """)
    conn.commit()

# def import_orders(conn: sqlite3.Connection) -> int:
#     orders = json.loads(ORDERS_PATH.read_text(encoding="utf-8"))
#     rows = [
#         (
#             o["id"],
#             o["product"],
#             o["total_qty"],
#             o["defect_qty"],
#             o.get("defect_desc"),
#             o.get("created_at"),
#         )
#         for o in orders
#     ]
#     conn.executemany(
#         """
#         INSERT OR REPLACE INTO work_orders
#             (id, product, total_qty, defect_qty, defect_desc, created_at)
#         VALUES (?, ?, ?, ?, ?, ?)
#         """,
#         rows,
#     )
#     return len(rows)


def main() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        create_table(conn)
    #     count = import_orders(conn)
    # print(f"导入 {count} 条工单到 {DB_PATH}")


if __name__ == "__main__":
    main()
