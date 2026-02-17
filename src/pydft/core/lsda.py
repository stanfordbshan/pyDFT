"""Local spin-density approximation (LSDA) helpers.

This module provides educational spin-polarized XC utilities that complement
the unpolarized LDA implementation.
"""

from __future__ import annotations

import math

import numpy as np

_DENSITY_FLOOR = 1.0e-16


def resolve_spin_configuration(
    electrons: int,
    spin_polarization: float | None,
) -> tuple[float, float, float]:
    """Return (N_up, N_down, zeta) for the requested spin setup.

    If `spin_polarization` is None, a simple educational default is used:
    N_up = ceil(N/2), N_down = floor(N/2).
    """

    if electrons <= 0:
        raise ValueError("electrons must be positive")

    if spin_polarization is None:
        n_up = float(math.ceil(electrons / 2))
        n_down = float(electrons - n_up)
        zeta = (n_up - n_down) / float(electrons)
        return n_up, n_down, zeta

    zeta = float(spin_polarization)
    if zeta < -1.0 or zeta > 1.0:
        raise ValueError("spin_polarization must be between -1 and 1")

    n_up = 0.5 * electrons * (1.0 + zeta)
    n_down = float(electrons) - n_up
    if n_up < -1.0e-12 or n_down < -1.0e-12:
        raise ValueError("Invalid spin split from spin_polarization")

    # Numerical guard for tiny negative floating-point noise.
    n_up = max(0.0, n_up)
    n_down = max(0.0, n_down)
    return n_up, n_down, zeta


def split_density_from_polarization(
    density_total: np.ndarray,
    zeta: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Split total density into spin-up and spin-down components."""

    n = np.asarray(density_total, dtype=float)
    zeta_clipped = float(np.clip(zeta, -1.0, 1.0))
    n_up = 0.5 * (1.0 + zeta_clipped) * n
    n_down = 0.5 * (1.0 - zeta_clipped) * n
    return n_up, n_down


def lsda_xc(
    density_up: np.ndarray,
    density_down: np.ndarray,
    use_exchange: bool = True,
    use_correlation: bool = True,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Return LSDA quantities (eps_xc, v_xc_up, v_xc_down, zeta)."""

    n_up = np.asarray(density_up, dtype=float)
    n_down = np.asarray(density_down, dtype=float)

    n_up_safe = np.clip(n_up, _DENSITY_FLOOR, None)
    n_down_safe = np.clip(n_down, _DENSITY_FLOOR, None)
    n_total = n_up_safe + n_down_safe

    zeta = np.clip((n_up_safe - n_down_safe) / n_total, -1.0, 1.0)

    eps_x = np.zeros_like(n_total)
    v_x_up = np.zeros_like(n_total)
    v_x_down = np.zeros_like(n_total)

    if use_exchange:
        c_x = (3.0 / np.pi) ** (1.0 / 3.0)
        a_x_spin = 0.75 * c_x * (2.0 ** (1.0 / 3.0))

        e_x_density = -a_x_spin * (n_up_safe ** (4.0 / 3.0) + n_down_safe ** (4.0 / 3.0))
        eps_x = e_x_density / n_total

        v_x_up = -((6.0 / np.pi) ** (1.0 / 3.0)) * n_up_safe ** (1.0 / 3.0)
        v_x_down = -((6.0 / np.pi) ** (1.0 / 3.0)) * n_down_safe ** (1.0 / 3.0)

    eps_c = np.zeros_like(n_total)
    v_c_up = np.zeros_like(n_total)
    v_c_down = np.zeros_like(n_total)
    if use_correlation:
        eps_c, v_c_up, v_c_down = _pz81_correlation_spin(n_total, zeta)

    eps_xc = eps_x + eps_c
    v_xc_up = v_x_up + v_c_up
    v_xc_down = v_x_down + v_c_down

    vacuum_mask = (n_up + n_down) <= _DENSITY_FLOOR
    eps_xc[vacuum_mask] = 0.0
    v_xc_up[vacuum_mask] = 0.0
    v_xc_down[vacuum_mask] = 0.0
    zeta[vacuum_mask] = 0.0

    return eps_xc, v_xc_up, v_xc_down, zeta


def _pz81_correlation_spin(n_total: np.ndarray, zeta: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Perdew-Zunger LSDA correlation with spin interpolation."""

    rs = (3.0 / (4.0 * np.pi * n_total)) ** (1.0 / 3.0)

    eps0, deps0 = _pz81_eps_and_deps(rs, polarized=False)
    eps1, deps1 = _pz81_eps_and_deps(rs, polarized=True)

    fz = _spin_interp_f(zeta)
    dfz = _spin_interp_df(zeta)

    eps_c = eps0 + (eps1 - eps0) * fz
    deps_drs = deps0 + (deps1 - deps0) * fz
    deps_dzeta = (eps1 - eps0) * dfz

    v_common = eps_c - (rs / 3.0) * deps_drs
    v_up = v_common + (1.0 - zeta) * deps_dzeta
    v_down = v_common + (-1.0 - zeta) * deps_dzeta

    return eps_c, v_up, v_down


def _pz81_eps_and_deps(rs: np.ndarray, polarized: bool) -> tuple[np.ndarray, np.ndarray]:
    """Return (eps_c, d eps_c / d rs) for PZ81 at fixed polarization."""

    eps_c = np.zeros_like(rs)
    deps = np.zeros_like(rs)

    if polarized:
        a, b, c, d = 0.01555, -0.0269, 0.0007, -0.0048
        gamma, beta1, beta2 = -0.0843, 1.3981, 0.2611
    else:
        a, b, c, d = 0.0311, -0.048, 0.0020, -0.0116
        gamma, beta1, beta2 = -0.1423, 1.0529, 0.3334

    low = rs < 1.0
    high = ~low

    if np.any(low):
        rs_low = rs[low]
        ln_rs = np.log(rs_low)

        eps_low = a * ln_rs + b + c * rs_low * ln_rs + d * rs_low
        deps_low = a / rs_low + c * (ln_rs + 1.0) + d

        eps_c[low] = eps_low
        deps[low] = deps_low

    if np.any(high):
        rs_high = rs[high]
        sqrt_rs = np.sqrt(rs_high)

        denom = 1.0 + beta1 * sqrt_rs + beta2 * rs_high
        eps_high = gamma / denom
        deps_high = -gamma * (0.5 * beta1 / sqrt_rs + beta2) / (denom * denom)

        eps_c[high] = eps_high
        deps[high] = deps_high

    return eps_c, deps


def _spin_interp_f(zeta: np.ndarray) -> np.ndarray:
    """Perdew-Zunger spin interpolation factor f(zeta)."""

    denominator = (2.0 ** (4.0 / 3.0)) - 2.0
    return (((1.0 + zeta) ** (4.0 / 3.0)) + ((1.0 - zeta) ** (4.0 / 3.0)) - 2.0) / denominator


def _spin_interp_df(zeta: np.ndarray) -> np.ndarray:
    """Derivative d f(zeta) / d zeta."""

    denominator = (2.0 ** (4.0 / 3.0)) - 2.0
    return (4.0 / 3.0) * (((1.0 + zeta) ** (1.0 / 3.0)) - ((1.0 - zeta) ** (1.0 / 3.0))) / denominator
