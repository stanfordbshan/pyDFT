from __future__ import annotations

import numpy as np

from pydft.core.functionals import lda_xc_unpolarized


def test_exchange_matches_dirac_formula() -> None:
    density = np.array([0.5])
    eps_xc, v_xc = lda_xc_unpolarized(
        density,
        use_exchange=True,
        use_correlation=False,
    )

    c_x = (3.0 / np.pi) ** (1.0 / 3.0)
    expected_eps_x = -0.75 * c_x * density[0] ** (1.0 / 3.0)
    expected_v_x = -c_x * density[0] ** (1.0 / 3.0)

    assert np.isclose(eps_xc[0], expected_eps_x)
    assert np.isclose(v_xc[0], expected_v_x)


def test_correlation_is_non_positive() -> None:
    density = np.logspace(-5, 1, 60)
    eps_xc, v_xc = lda_xc_unpolarized(
        density,
        use_exchange=False,
        use_correlation=True,
    )
    assert np.all(eps_xc <= 0.0)
    assert np.all(v_xc <= 0.0)


def test_vacuum_density_returns_zero_xc() -> None:
    density = np.array([0.0])
    eps_xc, v_xc = lda_xc_unpolarized(density)
    assert eps_xc[0] == 0.0
    assert v_xc[0] == 0.0
