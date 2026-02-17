"""Radial-grid utilities used by the spherical atomic solver."""

from __future__ import annotations

import numpy as np


def make_radial_grid(r_max: float, num_points: int, r_min: float = 1.0e-5) -> np.ndarray:
    """Build a uniformly spaced radial grid in atomic units.

    The grid starts from a small positive radius to avoid the 1/r singularity at r=0
    in the discretized equations.
    """

    if r_max <= r_min:
        raise ValueError("r_max must be larger than r_min")
    if num_points < 50:
        raise ValueError("num_points must be at least 50")
    return np.linspace(r_min, r_max, num_points)


def spherical_integral(values: np.ndarray, r: np.ndarray) -> float:
    """Return \int f(r) d^3r for a spherically symmetric function f(r)."""

    return float(4.0 * np.pi * np.trapz(values * r * r, r))


def normalize_density_to_electron_count(
    density: np.ndarray, r: np.ndarray, electrons: float
) -> np.ndarray:
    """Scale a density so that it integrates to the requested electron count."""

    current = spherical_integral(density, r)
    if current <= 0:
        raise ValueError("Density integral must be positive for normalization")
    return density * (electrons / current)
