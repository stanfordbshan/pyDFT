"""Local-density approximation (LDA) exchange-correlation functionals.

This module uses:
- Dirac exchange for an unpolarized electron gas.
- Perdew-Zunger (1981) correlation parameterization.
"""

from __future__ import annotations

import numpy as np

_DENSITY_FLOOR = 1.0e-16


def lda_xc_unpolarized(
    density: np.ndarray,
    use_exchange: bool = True,
    use_correlation: bool = True,
) -> tuple[np.ndarray, np.ndarray]:
    """Return (eps_xc, v_xc) arrays for an unpolarized density.

    Args:
        density: Electron density n(r) in a.u.
        use_exchange: Toggle exchange contribution.
        use_correlation: Toggle correlation contribution.

    Returns:
        eps_xc: Exchange-correlation energy per electron.
        v_xc: Exchange-correlation potential.
    """

    n = np.asarray(density, dtype=float)
    n_safe = np.clip(n, _DENSITY_FLOOR, None)

    eps_x = np.zeros_like(n_safe)
    v_x = np.zeros_like(n_safe)

    if use_exchange:
        c_x = (3.0 / np.pi) ** (1.0 / 3.0)
        eps_x = -0.75 * c_x * n_safe ** (1.0 / 3.0)
        v_x = -c_x * n_safe ** (1.0 / 3.0)

    eps_c = np.zeros_like(n_safe)
    v_c = np.zeros_like(n_safe)
    if use_correlation:
        eps_c, v_c = _pz81_correlation_unpolarized(n_safe)

    eps_xc = eps_x + eps_c
    v_xc = v_x + v_c

    vacuum_mask = n <= _DENSITY_FLOOR
    eps_xc[vacuum_mask] = 0.0
    v_xc[vacuum_mask] = 0.0
    return eps_xc, v_xc


def _pz81_correlation_unpolarized(density: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Perdew-Zunger (1981) correlation for spin-unpolarized density.

    The formulas are piecewise in rs.
    """

    rs = (3.0 / (4.0 * np.pi * density)) ** (1.0 / 3.0)
    eps_c = np.zeros_like(rs)
    v_c = np.zeros_like(rs)

    # rs < 1 branch.
    a = 0.0311
    b = -0.048
    c = 0.0020
    d = -0.0116

    # rs >= 1 branch.
    gamma = -0.1423
    beta1 = 1.0529
    beta2 = 0.3334

    low = rs < 1.0
    high = ~low

    if np.any(low):
        rs_low = rs[low]
        ln_rs = np.log(rs_low)
        eps = a * ln_rs + b + c * rs_low * ln_rs + d * rs_low
        deps_drs = a / rs_low + c * (ln_rs + 1.0) + d
        v = eps - (rs_low / 3.0) * deps_drs

        eps_c[low] = eps
        v_c[low] = v

    if np.any(high):
        rs_high = rs[high]
        sqrt_rs = np.sqrt(rs_high)
        denom = 1.0 + beta1 * sqrt_rs + beta2 * rs_high
        eps = gamma / denom
        deps_drs = -gamma * (0.5 * beta1 / sqrt_rs + beta2) / (denom * denom)
        v = eps - (rs_high / 3.0) * deps_drs

        eps_c[high] = eps
        v_c[high] = v

    return eps_c, v_c
