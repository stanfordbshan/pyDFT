"""Finite-difference radial Schr\"odinger solver for spherical KS equations."""

from __future__ import annotations

import numpy as np
from scipy.linalg import eigh_tridiagonal


def solve_radial_kohn_sham(
    r: np.ndarray,
    effective_potential: np.ndarray,
    l: int,
    num_states: int,
) -> tuple[np.ndarray, list[np.ndarray]]:
    """Solve radial equation for fixed angular momentum l.

    The discretized Hamiltonian acts on u(r)=rR(r):
        [-1/2 d^2/dr^2 + l(l+1)/(2r^2) + V_eff(r)] u = eps u
    """

    if num_states < 1:
        raise ValueError("num_states must be >= 1")

    if r.size < 3:
        raise ValueError("radial grid must contain at least 3 points")

    # Enforce u(0)=0 and u(r_max)=0 using a Dirichlet interior solve.
    # This avoids an unphysical spurious state at the singular r->0 endpoint.
    r_inner = r[1:-1]
    v_inner = effective_potential[1:-1]

    dr = r[1] - r[0]
    centrifugal = l * (l + 1) / (2.0 * r_inner * r_inner)

    diagonal = (1.0 / (dr * dr)) + centrifugal + v_inner
    off_diagonal = np.full(r_inner.size - 1, -0.5 / (dr * dr))

    max_state = min(num_states - 1, r_inner.size - 1)
    energies, vectors = eigh_tridiagonal(
        diagonal,
        off_diagonal,
        select="i",
        select_range=(0, max_state),
    )

    orbitals: list[np.ndarray] = []
    for idx in range(vectors.shape[1]):
        u = np.zeros_like(r)
        u[1:-1] = vectors[:, idx]
        norm = np.sqrt(np.trapezoid(u * u, r))
        if norm <= 0:
            raise RuntimeError("Encountered non-positive orbital normalization")
        orbitals.append(u / norm)

    return energies, orbitals
