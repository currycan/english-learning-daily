from datetime import date, datetime, timezone, timedelta
from pathlib import Path
import pytest

import scripts.content_utils as cu
from scripts.content_utils import get_beijing_date, content_path, CONTENT_DIR, BEIJING_TZ


def test_content_path_returns_correct_filename():
    d = date(2026, 3, 22)
    assert content_path(d) == Path("content/2026-03-22.md")


def test_content_path_zero_pads_month_and_day():
    d = date(2026, 12, 1)
    assert content_path(d) == Path("content/2026-12-01.md")


def test_get_beijing_date_returns_date_instance():
    result = get_beijing_date()
    assert isinstance(result, date)


def test_beijing_date_differs_from_utc_near_midnight(monkeypatch):
    """At 22:30 UTC on 2026-03-22, Beijing date should be 2026-03-23 (06:30 BJT)."""
    fixed_utc = datetime(2026, 3, 22, 22, 30, tzinfo=timezone.utc)

    class FakeDatetime:
        @staticmethod
        def now(tz=None):
            return fixed_utc.astimezone(tz) if tz else fixed_utc

    monkeypatch.setattr(cu, "datetime", FakeDatetime)
    assert cu.get_beijing_date() == date(2026, 3, 23)


def test_beijing_date_same_day_early_morning_utc(monkeypatch):
    """At 00:30 UTC on 2026-03-23, Beijing date is also 2026-03-23 (08:30 BJT)."""
    fixed_utc = datetime(2026, 3, 23, 0, 30, tzinfo=timezone.utc)

    class FakeDatetime:
        @staticmethod
        def now(tz=None):
            return fixed_utc.astimezone(tz) if tz else fixed_utc

    monkeypatch.setattr(cu, "datetime", FakeDatetime)
    assert cu.get_beijing_date() == date(2026, 3, 23)


def test_content_dir_constant():
    assert CONTENT_DIR == Path("content")


def test_beijing_tz_constant():
    assert BEIJING_TZ == timezone(timedelta(hours=8))
