"""Run simple benchmark calculations and compare to reference values.

References used:
- Hydrogen exact non-relativistic ground-state energy: -0.5 Ha.
- NIST Atomic DFT LDA table for Helium: Etot = -2.834836 Ha.
"""

from __future__ import annotations

from pydft.backend.models import AtomicSystem, SCFParameters
from pydft.backend.scf import run_scf


def run_hydrogen_exact_mode() -> float:
    result = run_scf(
        AtomicSystem(symbol="H", atomic_number=1, electrons=1),
        SCFParameters(
            r_max=35.0,
            num_points=1200,
            max_iterations=20,
            density_mixing=0.5,
            density_tolerance=1e-10,
            l_max=0,
            states_per_l=2,
            use_hartree=False,
            use_exchange=False,
            use_correlation=False,
        ),
    )
    return result.total_energy


def run_helium_lda() -> float:
    result = run_scf(
        AtomicSystem(symbol="He", atomic_number=2, electrons=2),
        SCFParameters(
            r_max=28.0,
            num_points=1400,
            max_iterations=220,
            density_mixing=0.25,
            density_tolerance=2e-6,
            l_max=1,
            states_per_l=5,
            use_hartree=True,
            use_exchange=True,
            use_correlation=True,
        ),
    )
    return result.total_energy


def main() -> None:
    hydrogen_energy = run_hydrogen_exact_mode()
    helium_energy = run_helium_lda()

    print("Benchmark summary (Hartree):")
    print("----------------------------------------------")
    print(f"Hydrogen exact reference  : {-0.500000: .6f}")
    print(f"Hydrogen computed         : {hydrogen_energy: .6f}")
    print(f"Hydrogen absolute error   : {abs(hydrogen_energy + 0.5): .6f}")
    print("----------------------------------------------")
    print(f"Helium NIST LDA reference : {-2.834836: .6f}")
    print(f"Helium computed           : {helium_energy: .6f}")
    print(f"Helium absolute error     : {abs(helium_energy + 2.834836): .6f}")


if __name__ == "__main__":
    main()
