from database.db import query, execute
from utils.stock_api import quote


def check(uid):
    sql = "SELECT * FROM alerts WHERE user_id=? AND triggered=0"
    for a in query(sql, (uid,)):
        p, _ = quote(a["stock_symbol"])
        is_triggered = (
            p <= a["target_price"]
            if a["alert_type"] == "Loss"
            else p >= a["target_price"]
        )
        if p is not None and is_triggered:
            execute(
                "UPDATE alerts SET triggered=1 WHERE id=? AND user_id=?",
                (a["id"], uid),
            )
