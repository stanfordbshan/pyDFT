"""Atomic method modules (LDA/LSDA/HF) for educational calculations."""

from .dft_engine import run_scf
from .hartree_fock import run_hartree_fock

__all__ = ["run_scf", "run_hartree_fock"]
