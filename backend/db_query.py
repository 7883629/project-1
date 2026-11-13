import sqlite3

DEFECT_RATE = "defect_qty * 1.0 / NULLIF(total_qty, 0)"

QUERIES = {
    "缺陷率最高的前 5 个工单": f"""
        SELECT id, product, total_qty, defect_qty, ROUND({DEFECT_RATE}*100,2) AS defect_rate_pct
        FROM work_orders
        ORDER BY {DEFECT_RATE} DESC
        LIMIT 5    
    """,
    "按产品统计": f"""
         SELECT product,
               COUNT(*) AS order_count,
               ROUND(AVG({DEFECT_RATE}) * 100, 2) AS avg_defect_rate_pct
        FROM work_orders
        GROUP BY product
        ORDER BY avg_defect_rate_pct DESC
   """,
    "缺陷率超过 5% 的工单": f"""
       SELECT id, product,
              ROUND({DEFECT_RATE} * 100, 2) AS defect_rate_pct
       FROM work_orders
       WHERE {DEFECT_RATE} > ?
       ORDER BY defect_rate_pct DESC
   """
}
with sqlite3.connect("mes.db") as conn:
    conn.row_factory = sqlite3.Row
    for title, sql in QUERIES.items():
        params = (0.05,) if "?" in sql else ()
        print(f"\n== {title} ==")
        for row in conn.execute(sql, params):
            print(dict(row))