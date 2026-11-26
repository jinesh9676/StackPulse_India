from datetime import date

import streamlit as st

from database.db import execute, query
from utils.calculations import calculate
from utils.stock_api import quote, valid_symbol


def holdings(uid):
    result = []
    rows = query(
        "SELECT p.*, COALESCE(s.sector, 'Other') sector "
        "FROM portfolio p LEFT JOIN stocks s "
        "ON p.stock_symbol = s.symbol WHERE user_id=?",
        (uid,),
    )
    for row in rows:
        current_price, price_date = quote(row['stock_symbol'])
        result.append(
            dict(
                row,
                current=current_price,
                price_date=price_date,
                **calculate(
                    row['quantity'],
                    row['buy_price'],
                    current_price,
                ),
            )
        )
    return result


def show(uid):
    st.header('Portfolio management')
    rows = query('SELECT * FROM portfolio WHERE user_id=?', (uid,))
    selected = st.selectbox(
        'Holding',
        [0] + [row['id'] for row in rows],
        format_func=lambda holding_id: (
            'New holding'
            if holding_id == 0
            else next(
                f"{row['stock_symbol']} #{holding_id}"
                for row in rows
                if row['id'] == holding_id
            )
        ),
    )
    row = next((item for item in rows if item['id'] == selected), {})

    with st.form(f'holding_{selected}'):
        symbol = st.text_input(
            'NSE / BSE symbol',
            row.get('stock_symbol', 'TCS.NS'),
        ).strip().upper()
        quantity = st.number_input(
            'Quantity',
            min_value=1,
            value=row.get('quantity', 1),
        )
        buy_price = st.number_input(
            'Buy price ₹',
            min_value=0.01,
            value=float(row.get('buy_price', 1)),
        )
        buy_date = st.date_input(
            'Buy date',
            date.fromisoformat(row['buy_date']) if row else date.today(),
            max_value=date.today(),
        )

        if st.form_submit_button('Save'):
            if not valid_symbol(symbol):
                st.error('Use a valid .NS or .BO symbol')
            elif selected:
                execute(
                    'UPDATE portfolio SET stock_symbol=?, quantity=?, buy_price=?, '
                    'buy_date=? WHERE id=? AND user_id=?',
                    (
                        symbol,
                        quantity,
                        buy_price,
                        str(buy_date),
                        selected,
                        uid,
                    ),
                )
                st.rerun()
            else:
                execute(
                    'INSERT INTO portfolio(user_id, stock_symbol, quantity, '
                    'buy_price, buy_date) VALUES(?,?,?,?,?)',
                    (uid, symbol, quantity, buy_price, str(buy_date)),
                )
                st.rerun()

    if selected and st.button('Delete selected holding'):
        execute(
            'DELETE FROM portfolio WHERE id=? AND user_id=?',
            (selected, uid),
        )
        st.rerun()

    st.dataframe(rows, hide_index=True)
