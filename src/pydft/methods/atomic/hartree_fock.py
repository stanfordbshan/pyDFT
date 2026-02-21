"""Educational spherical Hartree-Fock module for very simple atoms.

This implementation is intentionally explicit and pedagogical:
- radial finite-difference orbitals on the same grid as the DFT solver
- spin channels handled separately
- exact self-interaction cancellation for each occupied spin orbital

Current scope is limited to systems with up to two electrons. This keeps the
model simple enough for instructional use while still enabling meaningful
LDA/LSDA/HF comparisons for H, He+, and He.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from pydft.core.models import AtomicSystem, OrbitalResult, SCFParameters, SCFResult

from .grid import make_radial_grid, normalize_density_to_electron_count, spherical_integral
from .lsda import resolve_spin_configuration, split_density_from_polarization
from .potentials import external_potential_coulomb, hartree_potential_spherical
from .radial_solver import solve_radial_kohn_sham


@dataclass(slots=True)
class _HFStep:
    """Data produced by one fixed-potential HF iteration."""

    effective_potential_up: np.ndarray
    effective_potential_down: np.ndarray
    proposed_density_up: np.ndarray
    proposed_density_down: np.ndarray
    energy_up: float | None
    energy_down: float | None
    orbital_up: np.ndarray | None
    orbital_down: np.ndarray | None
    eigenvalue_sum: float
    hartree_energy: float
    exchange_energy: float
    exchange_potential_energy: float
    total_energy: float


def run_hartree_fock(system: AtomicSystem, params: SCFParameters) -> SCFResult:
    """Run an educational atomic HF calculation on the radial grid.

    Notes:
    - Pure HF is enforced (exchange-only, no correlation).
    - Current implementation supports up to two electrons.
    - The radial basis is limited to 1s-like occupied orbitals per spin channel.
    """

    if system.electrons > 2:
        raise ValueError(
            "Educational HF mode currently supports at most 2 electrons "
            "(H, He+, He presets)."
        )

    n_up_electrons, n_down_electrons, target_zeta = resolve_spin_configuration(
        electrons=system.electrons,
        spin_polarization=params.spin_polarization,
    )
    _validate_spin_populations(n_up_electrons, n_down_electrons)

    r = make_radial_grid(params.r_max, params.num_points)
    density_guess = _initial_density_guess(system, r)
    density_up, density_down = split_density_from_polarization(density_guess, target_zeta)
    density_up = _normalize_component_density(density_up, r, n_up_electrons)
    density_down = _normalize_component_density(density_down, r, n_down_electrons)

    converged = False
    residual = np.inf
    iterations = 0

    for iterations in range(1, params.max_iterations + 1):
        step = _single_hf_step(
            system=system,
            r=r,
            density_up=density_up,
            density_down=density_down,
            electrons_up=n_up_electrons,
            electrons_down=n_down_electrons,
        )

        mixed_up = (1.0 - params.density_mixing) * density_up + params.density_mixing * step.proposed_density_up
        mixed_down = (1.0 - params.density_mixing) * density_down + params.density_mixing * step.proposed_density_down

        mixed_up = _normalize_component_density(np.maximum(mixed_up, 0.0), r, n_up_electrons)
        mixed_down = _normalize_component_density(np.maximum(mixed_down, 0.0), r, n_down_electrons)

        residual_up = float(np.max(np.abs(mixed_up - density_up)))
        residual_down = float(np.max(np.abs(mixed_down - density_down)))
        residual = max(residual_up, residual_down)

        density_up = mixed_up
        density_down = mixed_down

        if residual < params.density_tolerance:
            converged = True
            break

    report_step = _single_hf_step(
        system=system,
        r=r,
        density_up=density_up,
        density_down=density_down,
        electrons_up=n_up_electrons,
        electrons_down=n_down_electrons,
    )

    output_up = _normalize_component_density(
        np.maximum(report_step.proposed_density_up, 0.0),
        r,
        n_up_electrons,
    )
    output_down = _normalize_component_density(
        np.maximum(report_step.proposed_density_down, 0.0),
        r,
        n_down_electrons,
    )
    output_total = output_up + output_down
    effective_avg = 0.5 * (report_step.effective_potential_up + report_step.effective_potential_down)

    orbitals: list[OrbitalResult] = []
    if report_step.energy_up is not None:
        orbitals.append(
            OrbitalResult(
                n_index=1,
                l=0,
                occupancy=float(n_up_electrons),
                energy=float(report_step.energy_up),
                spin="up",
            )
        )
    if report_step.energy_down is not None:
        orbitals.append(
            OrbitalResult(
                n_index=1,
                l=0,
                occupancy=float(n_down_electrons),
                energy=float(report_step.energy_down),
                spin="down",
            )
        )

    achieved_zeta = 0.0
    if system.electrons > 0:
        achieved_zeta = (n_up_electrons - n_down_electrons) / float(system.electrons)

    return SCFResult(
        converged=converged,
        iterations=iterations,
        total_energy=report_step.total_energy,
        eigenvalue_sum=report_step.eigenvalue_sum,
        hartree_energy=report_step.hartree_energy,
        xc_energy=report_step.exchange_energy,
        xc_potential_energy=report_step.exchange_potential_energy,
        density_residual=residual,
        system=system,
        parameters=params,
        orbitals=orbitals,
        radial_grid=r.tolist(),
        density=output_total.tolist(),
        density_up=output_up.tolist(),
        density_down=output_down.tolist(),
        effective_potential=effective_avg.tolist(),
        effective_potential_up=report_step.effective_potential_up.tolist(),
        effective_potential_down=report_step.effective_potential_down.tolist(),
        xc_model="HF",
        spin_up_electrons=float(n_up_electrons),
        spin_down_electrons=float(n_down_electrons),
        spin_polarization=float(achieved_zeta),
        notes=_build_hf_notes(
            system=system,
            spin_up=n_up_electrons,
            spin_down=n_down_electrons,
        ),
    )


def _single_hf_step(
    system: AtomicSystem,
    r: np.ndarray,
    density_up: np.ndarray,
    density_down: np.ndarray,
    electrons_up: float,
    electrons_down: float,
) -> _HFStep:
    """Solve one fixed-potential HF step for one occupied orbital per spin."""

    v_ext = external_potential_coulomb(system.atomic_number, r)
    v_h_up = _hartree_or_zero(density_up, r, electrons_up)
    v_h_down = _hartree_or_zero(density_down, r, electrons_down)

    # Exchange cancels same-spin self-Hartree exactly in this one-orbital-per-spin model.
    effective_up = v_ext + v_h_down
    effective_down = v_ext + v_h_up

    energy_up: float | None = None
    energy_down: float | None = None
    orbital_up: np.ndarray | None = None
    orbital_down: np.ndarray | None = None

    proposed_up = np.zeros_like(r)
    proposed_down = np.zeros_like(r)

    if electrons_up > 1.0e-12:
        energies, orbitals = solve_radial_kohn_sham(
            r=r,
            effective_potential=effective_up,
            l=0,
            num_states=1,
        )
        orbital_up = orbitals[0]
        energy_up = float(energies[0])
        proposed_up = electrons_up * _density_from_orbital(orbital_up, r)

    if electrons_down > 1.0e-12:
        energies, orbitals = solve_radial_kohn_sham(
            r=r,
            effective_potential=effective_down,
            l=0,
            num_states=1,
        )
        orbital_down = orbitals[0]
        energy_down = float(energies[0])
        proposed_down = electrons_down * _density_from_orbital(orbital_down, r)

    proposed_up = _normalize_component_density(np.maximum(proposed_up, 0.0), r, electrons_up)
    proposed_down = _normalize_component_density(np.maximum(proposed_down, 0.0), r, electrons_down)
    total_density = density_up + density_down
    v_h_total = _hartree_or_zero(total_density, r, electrons_up + electrons_down)

    eigenvalue_sum = 0.0
    if energy_up is not None:
        eigenvalue_sum += electrons_up * energy_up
    if energy_down is not None:
        eigenvalue_sum += electrons_down * energy_down

    hartree_energy = 0.5 * spherical_integral(total_density * v_h_total, r)

    exchange_potential_up = -v_h_up
    exchange_potential_down = -v_h_down
    exchange_potential_energy = spherical_integral(
        density_up * exchange_potential_up + density_down * exchange_potential_down,
        r,
    )
    exchange_energy = 0.5 * exchange_potential_energy

    total_energy = eigenvalue_sum - (hartree_energy + exchange_energy)

    return _HFStep(
        effective_potential_up=effective_up,
        effective_potential_down=effective_down,
        proposed_density_up=proposed_up,
        proposed_density_down=proposed_down,
        energy_up=energy_up,
        energy_down=energy_down,
        orbital_up=orbital_up,
        orbital_down=orbital_down,
        eigenvalue_sum=float(eigenvalue_sum),
        hartree_energy=float(hartree_energy),
        exchange_energy=float(exchange_energy),
        exchange_potential_energy=float(exchange_potential_energy),
        total_energy=float(total_energy),
    )


def _hartree_or_zero(density: np.ndarray, r: np.ndarray, electrons: float) -> np.ndarray:
    if electrons <= 1.0e-12:
        return np.zeros_like(density)
    return hartree_potential_spherical(density, r)


def _density_from_orbital(orbital: np.ndarray, r: np.ndarray) -> np.ndarray:
    """Map radial function u(r) to spherical density n(r) for one spin orbital."""

    return orbital * orbital / (4.0 * np.pi * r * r)


def _normalize_component_density(density: np.ndarray, r: np.ndarray, electrons: float) -> np.ndarray:
    """Normalize one spin density, keeping empty channels at zero."""

    if electrons <= 1.0e-12:
        return np.zeros_like(density)
    return normalize_density_to_electron_count(density, r, electrons)


def _validate_spin_populations(electrons_up: float, electrons_down: float) -> None:
    """Reject unsupported spin populations for this educational HF module."""

    if electrons_up > 1.0 + 1.0e-8 or electrons_down > 1.0 + 1.0e-8:
        raise ValueError(
            "Educational HF mode supports one occupied 1s orbital per spin channel "
            "(N_up <= 1, N_down <= 1)."
        )


def _initial_density_guess(system: AtomicSystem, r: np.ndarray) -> np.ndarray:
    """Hydrogenic guess normalized to total electron count."""

    effective_z = max(0.5, float(system.atomic_number) - 0.35 * max(system.electrons - 1, 0))
    guess = (effective_z**3 / np.pi) * np.exp(-2.0 * effective_z * r)
    guess = guess * max(system.electrons, 1)
    guess = np.maximum(guess, 1.0e-12)

    return normalize_density_to_electron_count(guess, r, system.electrons)


def _build_hf_notes(system: AtomicSystem, spin_up: float, spin_down: float) -> list[str]:
    """Short assumptions and interpretation notes for HF mode."""

    notes = [
        "Educational radial Hartree-Fock (HF) implementation.",
        "Pure HF: exchange included, correlation omitted.",
        "Current HF scope: systems with up to 2 electrons (H, He+, He).",
        "One occupied 1s-like orbital per spin channel is used.",
        f"Spin channel populations: N_up={spin_up:.3f}, N_down={spin_down:.3f}.",
    ]

    if system.electrons == 1:
        notes.append("For one-electron systems, self-interaction cancels exactly in HF.")

    return notes
