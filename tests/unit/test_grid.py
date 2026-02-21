from __future__ import annotations

import numpy as np

from pydft.methods.atomic.grid import make_radial_grid, normalize_density_to_electron_count, spherical_integral


def test_make_radial_grid_is_monotonic() -> None:
    r = make_radial_grid(r_max=15.0, num_points=400)
    assert r.shape == (400,)
    assert r[0] > 0.0
    assert np.all(np.diff(r) > 0.0)


def test_spherical_integral_constant_function() -> None:
    r = make_radial_grid(r_max=4.0, num_points=5000)
    values = np.ones_like(r)
    numeric = spherical_integral(values, r)

    exact = 4.0 * np.pi * (r[-1] ** 3 - r[0] ** 3) / 3.0
    rel_error = abs(numeric - exact) / exact
    assert rel_error < 1.0e-3


def test_density_normalization_targets_electron_count() -> None:
    r = make_radial_grid(r_max=10.0, num_points=1000)
    density = np.exp(-r)
    normalized = normalize_density_to_electron_count(density, r, electrons=2)
    electron_count = spherical_integral(normalized, r)
    assert abs(electron_count - 2.0) < 1.0e-8
