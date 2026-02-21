from __future__ import annotations

import numpy as np
import pytest

from pydft.methods.atomic.functionals import lda_xc_unpolarized
from pydft.methods.atomic.lsda import lsda_xc, resolve_spin_configuration


def test_resolve_spin_configuration_default_split() -> None:
    n_up, n_down, zeta = resolve_spin_configuration(electrons=3, spin_polarization=None)
    assert np.isclose(n_up, 2.0)
    assert np.isclose(n_down, 1.0)
    assert np.isclose(zeta, 1.0 / 3.0)


def test_resolve_spin_configuration_explicit_zeta() -> None:
    n_up, n_down, zeta = resolve_spin_configuration(electrons=4, spin_polarization=0.5)
    assert np.isclose(n_up, 3.0)
    assert np.isclose(n_down, 1.0)
    assert np.isclose(zeta, 0.5)


def test_resolve_spin_configuration_rejects_out_of_range() -> None:
    with pytest.raises(ValueError):
        resolve_spin_configuration(electrons=2, spin_polarization=1.1)


def test_lsda_exchange_matches_unpolarized_lda_when_spin_balanced() -> None:
    density = np.logspace(-4, 1, 25)
    density_up = 0.5 * density
    density_down = 0.5 * density

    eps_lda, v_lda = lda_xc_unpolarized(
        density,
        use_exchange=True,
        use_correlation=False,
    )
    eps_lsda, v_up, v_down, zeta = lsda_xc(
        density_up,
        density_down,
        use_exchange=True,
        use_correlation=False,
    )

    assert np.allclose(eps_lsda, eps_lda, rtol=5e-7, atol=1e-10)
    assert np.allclose(v_up, v_lda, rtol=5e-7, atol=1e-10)
    assert np.allclose(v_down, v_lda, rtol=5e-7, atol=1e-10)
    assert np.max(np.abs(zeta)) < 1e-12


def test_lsda_vacuum_density_is_zero() -> None:
    density_up = np.zeros(5)
    density_down = np.zeros(5)

    eps_xc, v_up, v_down, zeta = lsda_xc(density_up, density_down)
    assert np.all(eps_xc == 0.0)
    assert np.all(v_up == 0.0)
    assert np.all(v_down == 0.0)
    assert np.all(zeta == 0.0)
