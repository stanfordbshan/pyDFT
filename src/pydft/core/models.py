"""Data models used by the backend solver and API layers."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class AtomicSystem:
    """Definition of an atom-like system in atomic units.

    Attributes:
        symbol: Human-readable label (for example, "H" or "He").
        atomic_number: Nuclear charge Z.
        electrons: Total electron count.
        description: Optional free-text description.
    """

    symbol: str
    atomic_number: int
    electrons: int
    description: str = ""


@dataclass(slots=True)
class SCFParameters:
    """Numerical settings for educational DFT/HF self-consistent loops."""

    r_max: float = 20.0
    num_points: int = 1200
    max_iterations: int = 200
    density_mixing: float = 0.3
    density_tolerance: float = 1e-6
    l_max: int = 1
    states_per_l: int = 4
    use_hartree: bool = True
    use_exchange: bool = True
    use_correlation: bool = True
    xc_model: str = "LDA"
    spin_polarization: float | None = None


@dataclass(slots=True)
class OrbitalResult:
    """Summary of one occupied Kohn-Sham state."""

    n_index: int
    l: int
    occupancy: float
    energy: float
    spin: str = "paired"


@dataclass(slots=True)
class SCFResult:
    """Output produced by one SCF calculation."""

    converged: bool
    iterations: int
    total_energy: float
    eigenvalue_sum: float
    hartree_energy: float
    xc_energy: float
    xc_potential_energy: float
    density_residual: float
    system: AtomicSystem
    parameters: SCFParameters
    orbitals: list[OrbitalResult] = field(default_factory=list)
    radial_grid: list[float] = field(default_factory=list)
    density: list[float] = field(default_factory=list)
    effective_potential: list[float] = field(default_factory=list)
    density_up: list[float] = field(default_factory=list)
    density_down: list[float] = field(default_factory=list)
    effective_potential_up: list[float] = field(default_factory=list)
    effective_potential_down: list[float] = field(default_factory=list)
    xc_model: str = "LDA"
    spin_up_electrons: float = 0.0
    spin_down_electrons: float = 0.0
    spin_polarization: float = 0.0
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable dictionary representation."""

        return asdict(self)
