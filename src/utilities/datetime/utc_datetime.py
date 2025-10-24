from datetime import datetime, timezone
from typing import Union


def utc_now() -> datetime:
    """Return the current time as a timezone-aware UTC datetime"""
    return datetime.now(timezone.utc)

def to_timestamp(dt: datetime) -> float:
    """Convert a datetime to a POSIX timestamp (seconds since the epoch)"""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.timestamp()


def from_timestamp(ts: Union[int, float], tz: timezone = timezone.utc) -> datetime:
    """Create a timezone-aware datetime from a POSIX timestamp"""
    return datetime.fromtimestamp(ts, tz=tz)

def to_iso(dt: datetime) -> str:
    """Return an ISO 8601 formatted string for the given datetime"""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()


def from_iso(iso_str: str) -> datetime:
    """Parse an ISO 8601 datetime string into a timezone-aware datetime"""
    dt = datetime.fromisoformat(iso_str)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt