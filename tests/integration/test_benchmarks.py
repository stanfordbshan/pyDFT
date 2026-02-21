"""Benchmark checks against reference values from standard literature data sources."""

from __future__ import annotations

from pydft.core.models import AtomicSystem, SCFParameters
from pydft.methods.atomic.dft_engine import run_scf


def test_hydrogen_single_particle_benchmark() -> None:
    """Hydrogen 1s exact non-relativistic reference: -0.5 Ha.

    This benchmark disables Hartree and XC to isolate the radial solver.
    """

    system = AtomicSystem(symbol="H", atomic_number=1, electrons=1)
    params = SCFParameters(
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
    )

    result = run_scf(system, params)

    assert abs(result.total_energy - (-0.5)) < 1.5e-2


def test_hydrogen_exchange_only_lsda_lowers_energy_vs_lda() -> None:
    """Open-shell H in exchange-only mode should benefit from spin polarization.

    The setup matches the common educational comparison (Hartree+exchange on,
    correlation off) where LSDA typically yields a lower total energy than
    spin-unpolarized LDA.
    """

    system = AtomicSystem(symbol="H", atomic_number=1, electrons=1)
    common = dict(
        r_max=35.0,
        num_points=1500,
        max_iterations=220,
        density_mixing=0.3,
        density_tolerance=1e-7,
        l_max=1,
        states_per_l=5,
        use_hartree=True,
        use_exchange=True,
        use_correlation=False,
    )

    lda_result = run_scf(system, SCFParameters(**common, xc_model="LDA"))
    lsda_result = run_scf(
        system,
        SCFParameters(**common, xc_model="LSDA", spin_polarization=1.0),
    )

    assert lsda_result.total_energy < lda_result.total_energy - 0.02
    assert -0.50 < lsda_result.total_energy < -0.42


def test_hydrogen_lda_lsda_against_nist_reference_values() -> None:
    """Hydrogen LDA/LSD total energies benchmark against NIST atomic tables.

    NIST entries:
    - LDA total energy: -0.445671 Ha
    - LSD total energy: -0.478671 Ha
    """

    system = AtomicSystem(symbol="H", atomic_number=1, electrons=1)
    common = dict(
        r_max=40.0,
        num_points=1400,
        max_iterations=260,
        density_mixing=0.25,
        density_tolerance=2e-8,
        l_max=2,
        states_per_l=6,
        use_hartree=True,
        use_exchange=True,
        use_correlation=True,
    )

    lda = run_scf(system, SCFParameters(**common, xc_model="LDA"))
    lsda = run_scf(system, SCFParameters(**common, xc_model="LSDA", spin_polarization=1.0))

    assert abs(lda.total_energy - (-0.445671)) < 6e-3
    assert abs(lsda.total_energy - (-0.478671)) < 6e-3


def test_helium_hf_benchmark_against_reference() -> None:
    """He HF total energy benchmark.

    Standard nonrelativistic restricted HF reference for helium is
    approximately -2.86168 Ha. A wider tolerance is used due to the
    educational radial finite-difference setup.
    """

    system = AtomicSystem(symbol="He", atomic_number=2, electrons=2)
    params = SCFParameters(
        r_max=35.0,
        num_points=1600,
        max_iterations=260,
        density_mixing=0.25,
        density_tolerance=1e-7,
        l_max=0,
        states_per_l=1,
        xc_model="HF",
        spin_polarization=0.0,
    )

    result = run_scf(system, params)

    assert result.xc_model == "HF"
    assert abs(result.total_energy - (-2.86168)) < 0.08


def test_helium_lda_benchmark_against_nist_range() -> None:
    """He LDA total energy benchmark against NIST LDA table.

    NIST reports Etot(LDA) = -2.834836 Hartree for Helium.
    A wider tolerance is used because this educational solver uses a simple
    finite-difference radial discretization and a different practical setup.
    """

    system = AtomicSystem(symbol="He", atomic_number=2, electrons=2)
    params = SCFParameters(
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
    )

    result = run_scf(system, params)

    nist_helium_lda = -2.834836
    assert abs(result.total_energy - nist_helium_lda) < 0.12
