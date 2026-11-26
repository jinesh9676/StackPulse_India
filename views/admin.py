import streamlit as st

from auth.security import issue_reset
from database.db import execute, query
from utils.stock_api import valid_symbol


def show(uid):
    if not query(
        "SELECT id FROM users "
        "WHERE id=? AND role='admin' AND status='active'",
        (uid,),
    ):
        st.stop()

    st.header("Admin console")
    users = query(
        "SELECT id, full_name, username, email, role, status FROM users"
    )
    st.metric("Registered accounts", len(users))
    st.dataframe(users)
    st.dataframe(query("SELECT * FROM portfolio"))
    st.dataframe(query("SELECT * FROM alerts"))
    st.dataframe(query("SELECT * FROM logs ORDER BY id DESC LIMIT 100"))

    others = [u["id"] for u in users if u["role"] == "user"]
    if others:
        target = st.selectbox("Manage user", others)
        if st.button("Deactivate"):
            execute(
                "UPDATE users SET status='inactive' "
                "WHERE id=? AND role='user'",
                (target,),
            )
            st.rerun()
        if st.button("Activate"):
            execute(
                "UPDATE users SET status='active' "
                "WHERE id=? AND role='user'",
                (target,),
            )
            st.rerun()
        if st.button("Generate reset token"):
            st.code(issue_reset(target))
            st.caption(
                "Deliver privately after verifying identity. "
                "Expires in 15 minutes."
            )

    with st.form("stock"):
        symbol = st.text_input("Symbol").upper()
        company = st.text_input("Company")
        sector = st.text_input("Sector")
        if st.form_submit_button("Save stock"):
            if valid_symbol(symbol) and company and sector:
                execute(
                    "INSERT OR REPLACE INTO stocks VALUES(?, ?, ?)",
                    (symbol, company, sector),
                )
                st.rerun()
            else:
                st.error("Invalid stock details")

    st.dataframe(query("SELECT * FROM stocks"))
    alerts = query("SELECT id FROM alerts")
    if alerts:
        alert_id = st.selectbox(
            "Alert to remove",
            [alert["id"] for alert in alerts],
        )
        if st.button("Remove alert"):
            execute("DELETE FROM alerts WHERE id=?", (alert_id,))
            st.rerun()

    with st.form("settings"):
        notice_rows = query(
            "SELECT value FROM settings WHERE key='notice'"
        )
        notice = st.text_input(
            "Dashboard announcement",
            next((row["value"] for row in notice_rows), ""),
        )
        if st.form_submit_button("Save announcement"):
            execute(
                "INSERT OR REPLACE INTO settings VALUES('notice', ?)",
                (notice,),
            )
            st.rerun()
