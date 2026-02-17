"""Potential terms used in the radial Kohn-Sham equations."""

from __future__ import annotations

import numpy as np


def external_potential_coulomb(atomic_number: int, r: np.ndarray) -> np.ndarray:
    """Return nuclear Coulomb potential V_ext(r) = -Z/r."""

    return -float(atomic_number) / r


def hartree_potential_spherical(density: np.ndarray, r: np.ndarray) -> np.ndarray:
    r"""Return the Hartree potential for a spherical density.

    Uses:
        V_H(r) = Q(r)/r + \int_r^\infty q(r')/r' dr'
    where:
        q(r) = 4*pi*r^2*n(r),  Q(r)=\int_0^r q(r')dr'.
    """

    q = 4.0 * np.pi * r * r * density
    q_over_r = q / r

    enclosed = _cumulative_trapezoid_from_start(q, r)
    tail = _cumulative_trapezoid_from_end(q_over_r, r)

    return enclosed / r + tail


def _cumulative_trapezoid_from_start(y: np.ndarray, x: np.ndarray) -> np.ndarray:
    """Cumulative trapezoidal integral from the left boundary."""

    out = np.zeros_like(y)
    if y.size < 2:
        return out

    dx = np.diff(x)
    segment_area = 0.5 * (y[1:] + y[:-1]) * dx
    out[1:] = np.cumsum(segment_area)
    return out


def _cumulative_trapezoid_from_end(y: np.ndarray, x: np.ndarray) -> np.ndarray:
    """Cumulative trapezoidal integral from the right boundary."""

    out = np.zeros_like(y)
    if y.size < 2:
        return out

    for idx in range(y.size - 2, -1, -1):
        dx = x[idx + 1] - x[idx]
        out[idx] = out[idx + 1] + 0.5 * (y[idx + 1] + y[idx]) * dx
    return out
