"""Small helpers shared by the seed files."""

from __future__ import annotations

import calendar
from datetime import date, timedelta

VAT_RATE = 0.15


def d_ago(today: date, days: int) -> str:
    return (today - timedelta(days=days)).isoformat()


def period_of(today: date, back: int = 0) -> str:
    """The last full calendar month before today as YYYY-MM. back=1 is the month before that."""
    year, month = today.year, today.month - 1 - back
    while month < 1:
        year, month = year - 1, month + 12
    return f"{year:04d}-{month:02d}"


def days_in(period: str) -> int:
    year, month = int(period[:4]), int(period[5:7])
    return calendar.monthrange(year, month)[1]


def yymm(period: str) -> str:
    return period[2:4] + period[5:7]


def money(value: float) -> float:
    return round(value + 1e-9, 2)
