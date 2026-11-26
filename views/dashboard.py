import streamlit as st
import pandas as pd
import plotly.express as px

from views.portfolio import holdings


def show(uid, mode):
    st.header(mode)
    rows = holdings(uid)
    if not rows:
        st.info("Add a holding first.")
        return

    df = pd.DataFrame(rows)
    priced = df[df.current.notna()].copy()
    st.caption(
        "Latest available daily close, not an exchange real-time feed. "
        "Brokerage assumed zero; taxes and other charges excluded."
    )

    a, b, c = st.columns(3)
    a.metric("Invested ₹", f'{df.invested.sum():,.2f}')
    complete = len(priced) == len(df)
    b.metric(
        "Portfolio value ₹",
        f'{priced.value.sum():,.2f}' if complete else "Unavailable",
    )
    c.metric(
        "Unrealized P/L ₹",
        f'{priced.profit.sum():,.2f}' if complete else "Unavailable",
    )

    if not complete:
        st.warning("Some prices unavailable; aggregate valuation withheld.")

    if mode == "Recovery Tracker":
        st.caption(
            "Recovery ratio = current / buy price; required gain is measured "
            "from current price."
        )
        recovery_columns = [
            "stock_symbol",
            "buy_price",
            "current",
            "needed",
            "recovery",
            "required_gain",
        ]
        st.dataframe(
            priced[priced.profit < 0][recovery_columns],
            hide_index=True,
        )
    else:
        st.dataframe(df.drop(columns=["user_id"]), hide_index=True)
        if not priced.empty:
            st.plotly_chart(
                px.bar(
                    priced,
                    x="stock_symbol",
                    y="profit",
                    color="profit",
                )
            )
            if mode == "Dashboard":
                st.plotly_chart(
                    px.pie(
                        priced,
                        names="stock_symbol",
                        values="value",
                        title="Allocation (priced holdings)",
                    )
                )
                sector_values = priced.groupby("sector", as_index=False).value.sum()
                st.plotly_chart(
                    px.bar(sector_values, x="sector", y="value")
                )
                st.write("Top gainers / losers")
                st.dataframe(
                    priced[["stock_symbol", "roi"]].sort_values(
                        "roi", ascending=False
                    )
                )

    st.download_button(
        "Download CSV",
        df.drop(columns=["user_id"]).to_csv(index=False),
        "portfolio.csv",
        "text/csv",
    )
