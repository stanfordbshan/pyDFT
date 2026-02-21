"""Compatibility wrapper for legacy imports.

Primary mapping now lives in :mod:`pydft.core.request_mapper`.
"""

from __future__ import annotations

from .request_mapper import parse_request_payload

__all__ = ["parse_request_payload"]
