"""
Single-cell tool helpers package.

Some tool implementations (e.g. `src.tool_scselected.*`) share small utilities
from this package.
"""

from ._type_coercion import (  # noqa: F401
    coerce_bool,
    coerce_float,
    coerce_int,
    coerce_int_list,
    coerce_str,
    coerce_str_list,
)

