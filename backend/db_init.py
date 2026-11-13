import json
import sqlite3
from pathlib import Path

DB_PATH = Path("mes.db")
ORDERS_PATH = Path("orders.json")


def create_table(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS work_orders (
            id          TEXT PRIMARY KEY,
            product     TEXT NOT NULL,
            total_qty   INTEGER NOT NULL CHECK (total_qty >= 0),
            defect_qty  INTEGER NOT NULL CHECK (defect_qty >= 0),
            defect_desc TEXT,
            created_at  TEXT
        )
    """)


def import_orders(conn: sqlite3.Connection) -> int:
    orders = json.loads(ORDERS_PATH.read_text(encoding="utf-8"))
    rows = [
        (
            o["id"],
            o["product"],
            o["total_qty"],
            o["defect_qty"],
            o.get("defect_desc"),
            o.get("created_at"),
        )
        for o in orders
    ]
    conn.executemany(
        """
        INSERT OR REPLACE INTO work_orders
            (id, product, total_qty, defect_qty, defect_desc, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        rows,
    )
    return len(rows)

def main() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        create_table(conn)
        count = import_orders(conn)
    print(f"导入 {count} 条工单到 {DB_PATH}")

if __name__ == "__main__":
    main()