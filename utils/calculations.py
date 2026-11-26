def calculate(quantity, buy, current):
    invested = quantity * buy
    if current is None:
        return dict(
            invested=invested,
            value=None,
            profit=None,
            roi=None,
            recovery=None,
            needed=None,
            required_gain=None,
        )

    value = quantity * current
    return dict(
        invested=invested,
        value=value,
        profit=value - invested,
        roi=(value - invested) / invested * 100,
        recovery=min(100, current / buy * 100),
        needed=max(0, buy - current),
        required_gain=(
            max(0, (buy / current - 1) * 100)
            if current > 0
            else None
        ),
    )
