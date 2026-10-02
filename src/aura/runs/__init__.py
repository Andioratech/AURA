"""Bounded diagnostic execution and immutable local bundle inspection."""

from .check import check_run
from .execute import execute

__all__ = ["check_run", "execute"]
