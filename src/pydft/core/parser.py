"""Argument parsing and CLI entrypoints for educational SCF solvers."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

import uvicorn

from .dft_engine import run_scf
from .models import AtomicSystem, SCFParameters
from .presets import build_system


def parse_request_payload(payload: Mapping[str, Any]) -> tuple[AtomicSystem, SCFParameters]:
    """Parse a dictionary payload into strongly-typed system/parameter objects.

    This parser is reused by both CLI and pywebview bridge code to keep behavior
    consistent between standalone and GUI-driven execution.
    """

    symbol = payload.get("symbol", "He")
    atomic_number = _optional_int(payload.get("atomic_number"))
    electrons = _optional_int(payload.get("electrons"))

    params_data = payload.get("parameters", {})
    if params_data is None:
        params_data = {}
    if not isinstance(params_data, Mapping):
        raise ValueError("'parameters' must be an object")

    xc_model = str(params_data.get("xc_model", "LDA")).strip().upper()
    if xc_model not in {"LDA", "LSDA", "HF"}:
        raise ValueError("parameters.xc_model must be one of 'LDA', 'LSDA', or 'HF'")

    spin_polarization = _optional_float(params_data.get("spin_polarization"))
    if spin_polarization is not None and (spin_polarization < -1.0 or spin_polarization > 1.0):
        raise ValueError("parameters.spin_polarization must be between -1 and 1")

    if xc_model == "LDA":
        # LDA is spin-unpolarized, so zeta is ignored even if provided.
        spin_polarization = None

    use_hartree = bool(params_data.get("use_hartree", True))
    use_exchange = bool(params_data.get("use_exchange", True))
    use_correlation = bool(params_data.get("use_correlation", True))

    if xc_model == "HF":
        # Pure HF for this educational module.
        use_hartree = True
        use_exchange = True
        use_correlation = False

    system = build_system(symbol=symbol, atomic_number=atomic_number, electrons=electrons)
    params = SCFParameters(
        r_max=float(params_data.get("r_max", 20.0)),
        num_points=int(params_data.get("num_points", 1200)),
        max_iterations=int(params_data.get("max_iterations", 200)),
        density_mixing=float(params_data.get("density_mixing", 0.3)),
        density_tolerance=float(params_data.get("density_tolerance", 1e-6)),
        l_max=int(params_data.get("l_max", 1)),
        states_per_l=int(params_data.get("states_per_l", 4)),
        use_hartree=use_hartree,
        use_exchange=use_exchange,
        use_correlation=use_correlation,
        xc_model=xc_model,
        spin_polarization=spin_polarization,
    )

    return system, params


def _optional_int(value: Any) -> int | None:
    """Return integer value or None, preserving None-like inputs."""

    if value is None:
        return None
    return int(value)


def _optional_float(value: Any) -> float | None:
    """Return float value or None, preserving None/blank inputs."""

    if value is None:
        return None
    if isinstance(value, str) and value.strip() == "":
        return None
    return float(value)


def build_parser() -> argparse.ArgumentParser:
    """Create the top-level CLI parser with subcommands."""

    parser = argparse.ArgumentParser(description="Educational LDA/LSDA/HF atomic solver")
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
    run_cmd.add_argument(
        "--xc-model",
        choices=["LDA", "LSDA", "HF"],
        default="LDA",
        help="Method selector (LDA, LSDA, or HF)",
    )
    run_cmd.add_argument(
        "--spin-polarization",
        type=float,
        default=None,
        help="Spin polarization zeta=(N_up-N_down)/N, used by LSDA and HF",
    )
    run_cmd.add_argument("--json", action="store_true", help="Print result as raw JSON")
    run_cmd.add_argument("--output", type=Path, default=None, help="Optional JSON output path")

    serve_cmd = subparsers.add_parser("serve", help="Run backend API server")
    serve_cmd.add_argument("--host", default="127.0.0.1", help="Bind host")
    serve_cmd.add_argument("--port", default=8000, type=int, help="Bind port")
    serve_cmd.add_argument("--reload", action="store_true", help="Enable auto-reload")
    return parser


def _run_calculation(args: argparse.Namespace) -> int:
    payload = {
        "symbol": args.symbol,
        "atomic_number": args.atomic_number,
        "electrons": args.electrons,
        "parameters": {
            "r_max": args.r_max,
            "num_points": args.num_points,
            "max_iterations": args.max_iterations,
            "density_mixing": args.density_mixing,
            "density_tolerance": args.density_tolerance,
            "l_max": args.l_max,
            "states_per_l": args.states_per_l,
            "use_hartree": not args.disable_hartree,
            "use_exchange": not args.disable_exchange,
            "use_correlation": not args.disable_correlation,
            "xc_model": args.xc_model,
            "spin_polarization": args.spin_polarization,
        },
    }
    system, params = parse_request_payload(payload)

    result = run_scf(system, params)
    result_payload = result.to_dict()

    if args.output is not None:
        args.output.write_text(json.dumps(result_payload, indent=2), encoding="utf-8")

    if args.json:
        print(json.dumps(result_payload, indent=2))
    else:
        print(f"System: {result.system.symbol} (Z={result.system.atomic_number}, N={result.system.electrons})")
        print(f"Method: {result.xc_model}")
        if result.xc_model.upper() in {"LSDA", "HF"}:
            print(
                "Spin channels: "
                f"N_up={result.spin_up_electrons:.3f}, "
                f"N_down={result.spin_down_electrons:.3f}, "
                f"zeta={result.spin_polarization:.3f}"
            )
        print(f"Converged: {result.converged} in {result.iterations} iterations")
        print(f"Total energy (Ha): {result.total_energy:.8f}")
        print(f"Density residual: {result.density_residual:.3e}")
        print("Occupied orbital energies (Ha):")
        for orbital in result.orbitals:
            print(
                f"  n={orbital.n_index}, l={orbital.l}, spin={orbital.spin}, occ={orbital.occupancy:.1f}, "
                f"eps={orbital.energy:.8f}"
            )

    return 0


def main() -> int:
    """CLI entrypoint used by `pydft-cli` and `python -m` execution."""

    parser = build_parser()
    args = parser.parse_args()

    if args.command == "serve":
        uvicorn.run(
            "pydft.api.app:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
        )
        return 0
    return _run_calculation(args)


if __name__ == "__main__":
    raise SystemExit(main())
