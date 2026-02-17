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

    dr = r[1] - r[0]
    centrifugal = l * (l + 1) / (2.0 * r * r)

    diagonal = (1.0 / (dr * dr)) + centrifugal + effective_potential
    off_diagonal = np.full(r.size - 1, -0.5 / (dr * dr))

    max_state = min(num_states - 1, r.size - 1)
    energies, vectors = eigh_tridiagonal(
        diagonal,
        off_diagonal,
        select="i",
        select_range=(0, max_state),
    )

    orbitals: list[np.ndarray] = []
    for idx in range(vectors.shape[1]):
        u = vectors[:, idx].copy()
        norm = np.sqrt(np.trapz(u * u, r))
        if norm <= 0:
            raise RuntimeError("Encountered non-positive orbital normalization")
        orbitals.append(u / norm)

    return energies, orbitals
