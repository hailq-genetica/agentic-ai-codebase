from __future__ import annotations

from typing import Any, Iterable, List, Optional


def _is_none_like(v: Any) -> bool:
    return v is None or (isinstance(v, str) and v.strip().lower() in {"none", "null", ""})


def coerce_int(v: Any, *, default: Optional[int] = None) -> Optional[int]:
    if _is_none_like(v):
        return default
    if isinstance(v, bool):
        return int(v)
    if isinstance(v, int):
        return v
    return int(float(v))  # handles "3", "3.0"


def coerce_float(v: Any, *, default: Optional[float] = None) -> Optional[float]:
    if _is_none_like(v):
        return default
    if isinstance(v, bool):
        return float(int(v))
    if isinstance(v, (int, float)):
        return float(v)
    return float(v)


def coerce_bool(v: Any, *, default: Optional[bool] = None) -> Optional[bool]:
    if _is_none_like(v):
        return default
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return bool(v)
    if isinstance(v, str):
        s = v.strip().lower()
        if s in {"true", "t", "yes", "y", "1"}:
            return True
        if s in {"false", "f", "no", "n", "0"}:
            return False
    raise ValueError(f"Cannot coerce to bool: {v!r}")


def coerce_str(v: Any, *, default: Optional[str] = None) -> Optional[str]:
    if _is_none_like(v):
        return default
    if isinstance(v, str):
        return v
    return str(v)


def coerce_int_list(v: Any, *, default: Optional[List[int]] = None) -> Optional[List[int]]:
    if _is_none_like(v):
        return default
    if isinstance(v, list):
        return [int(float(x)) for x in v]
    if isinstance(v, tuple):
        return [int(float(x)) for x in list(v)]
    if isinstance(v, str):
        s = v.strip()
        if not s:
            return default
        # allow "1,2,3"
        parts = [p.strip() for p in s.split(",") if p.strip()]
        return [int(float(p)) for p in parts]
    if isinstance(v, Iterable):
        return [int(float(x)) for x in v]
    return [int(float(v))]


def coerce_str_list(v: Any, *, default: Optional[List[str]] = None) -> Optional[List[str]]:
    if _is_none_like(v):
        return default
    if isinstance(v, list):
        return [str(x) for x in v]
    if isinstance(v, tuple):
        return [str(x) for x in list(v)]
    if isinstance(v, str):
        s = v.strip()
        if not s:
            return default
        parts = [p.strip() for p in s.split(",") if p.strip()]
        return parts
    if isinstance(v, Iterable):
        return [str(x) for x in v]
    return [str(v)]

