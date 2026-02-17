"""Standalone command-line interface for the pyDFT backend."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import uvicorn

from .models import SCFParameters
from .presets import build_system
from .scf import run_scf


def build_parser() -> argparse.ArgumentParser:
    """Create the top-level CLI parser with subcommands."""

    parser = argparse.ArgumentParser(description="Educational LDA Kohn-Sham solver")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_cmd = subparsers.add_parser("run", help="Run one SCF calculation")
    run_cmd.add_argument("--symbol", default="He", help="Preset system symbol (H, He, He+) or custom label")
    run_cmd.add_argument("--atomic-number", type=int, default=None, help="Override nuclear charge Z")
    run_cmd.add_argument("--electrons", type=int, default=None, help="Override electron count")
    run_cmd.add_argument("--r-max", type=float, default=20.0, help="Radial domain maximum")
    run_cmd.add_argument("--num-points", type=int, default=1200, help="Radial grid point count")
    run_cmd.add_argument("--max-iterations", type=int, default=200, help="Maximum SCF iterations")
    run_cmd.add_argument("--density-mixing", type=float, default=0.3, help="Linear mixing factor")
    run_cmd.add_argument("--density-tolerance", type=float, default=1e-6, help="SCF convergence threshold")
    run_cmd.add_argument("--l-max", type=int, default=1, help="Maximum angular momentum channel")
    run_cmd.add_argument("--states-per-l", type=int, default=4, help="Radial states solved per l channel")
    run_cmd.add_argument("--disable-hartree", action="store_true", help="Disable Hartree term")
    run_cmd.add_argument("--disable-exchange", action="store_true", help="Disable exchange term")
    run_cmd.add_argument("--disable-correlation", action="store_true", help="Disable correlation term")
    run_cmd.add_argument("--json", action="store_true", help="Print result as raw JSON")
    run_cmd.add_argument("--output", type=Path, default=None, help="Optional JSON output path")

    serve_cmd = subparsers.add_parser("serve", help="Run backend API server")
    serve_cmd.add_argument("--host", default="127.0.0.1", help="Bind host")
    serve_cmd.add_argument("--port", default=8000, type=int, help="Bind port")
    serve_cmd.add_argument("--reload", action="store_true", help="Enable auto-reload")
    return parser


def _run_calculation(args: argparse.Namespace) -> int:
    system = build_system(
        symbol=args.symbol,
        atomic_number=args.atomic_number,
        electrons=args.electrons,
    )

    params = SCFParameters(
        r_max=args.r_max,
        num_points=args.num_points,
        max_iterations=args.max_iterations,
        density_mixing=args.density_mixing,
        density_tolerance=args.density_tolerance,
        l_max=args.l_max,
        states_per_l=args.states_per_l,
        use_hartree=not args.disable_hartree,
        use_exchange=not args.disable_exchange,
        use_correlation=not args.disable_correlation,
    )

    result = run_scf(system, params)
    payload = result.to_dict()

    if args.output is not None:
        args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"System: {result.system.symbol} (Z={result.system.atomic_number}, N={result.system.electrons})")
        print(f"Converged: {result.converged} in {result.iterations} iterations")
        print(f"Total energy (Ha): {result.total_energy:.8f}")
        print(f"Density residual: {result.density_residual:.3e}")
        print("Occupied orbital energies (Ha):")
        for orbital in result.orbitals:
            print(
                f"  n={orbital.n_index}, l={orbital.l}, occ={orbital.occupancy:.1f}, "
                f"eps={orbital.energy:.8f}"
            )

    return 0


def main() -> int:
    """CLI entrypoint used by `pydft-cli` and `python -m` execution."""

    parser = build_parser()
    args = parser.parse_args()

    command = args.command
    if command == "serve":
        uvicorn.run(
            "pydft.backend.api:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
        )
        return 0
    return _run_calculation(args)


if __name__ == "__main__":
    raise SystemExit(main())
