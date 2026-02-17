from __future__ import annotations

import numpy as np

from pydft.core.grid import make_radial_grid, spherical_integral
from pydft.core.potentials import hartree_potential_spherical


def test_hartree_of_zero_density_is_zero() -> None:
    r = make_radial_grid(10.0, 300)
    density = np.zeros_like(r)
    potential = hartree_potential_spherical(density, r)
    assert np.allclose(potential, 0.0)


def test_hartree_has_correct_far_field_scaling() -> None:
    r = make_radial_grid(20.0, 1500)
    density = np.exp(-2.0 * r)
    density *= 2.0 / spherical_integral(density, r)

    potential = hartree_potential_spherical(density, r)

    expected = 2.0 / r[-1]
    assert abs(potential[-1] - expected) < 5.0e-3
