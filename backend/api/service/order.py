import sqlite3

from db import get_db

DEFECT_RATE = "defect_qty * 1.0 / NULLIF(total_qty, 0)"

PRODUCT_RATE = "SUM(defect_qty) * 1.0 / NULLIF(SUM(total_qty), 0)"


class OrderService:
    def get_orders_by_defect(self, conn: sqlite3.Connection, limit: int = 10, offset: int = 0, min_rate: float = 0):
        rows = conn.execute(f"""
                    SELECT id, product, total_qty, defect_qty, ROUND({DEFECT_RATE}*100,2) AS defect_rate_pct
                    FROM work_orders
                    WHERE {DEFECT_RATE} > ?
                    ORDER BY {DEFECT_RATE} DESC
                    LIMIT ?
                    OFFSET ?  
            """, (min_rate, limit, offset))

        return [dict(row) for row in rows]

    def get_orders_by_product(self, conn: sqlite3.Connection):
        rows = conn.execute(f"""
                      SELECT product,
                      COUNT(*) AS order_count,
                      ROUND({PRODUCT_RATE} * 100, 2) AS defect_rate_pct
                      FROM work_orders
                      GROUP BY product
                      ORDER BY defect_rate_pct ASC
             """)
        return [dict(row) for row in rows]
