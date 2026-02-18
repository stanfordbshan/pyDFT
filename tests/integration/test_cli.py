from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"


def test_cli_json_output() -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{SRC}:{env.get('PYTHONPATH', '')}"

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "pydft.core.parser",
            "run",
            "--symbol",
            "H",
            "--num-points",
            "350",
            "--max-iterations",
            "80",
            "--json",
        ],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )

    payload = json.loads(completed.stdout)
    assert payload["system"]["symbol"] == "H"
    assert "total_energy" in payload
    assert "converged" in payload


def test_cli_accepts_lsda_flags() -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{SRC}:{env.get('PYTHONPATH', '')}"

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "pydft.core.parser",
            "run",
            "--symbol",
            "H",
            "--num-points",
            "350",
            "--max-iterations",
            "80",
            "--xc-model",
            "LSDA",
            "--spin-polarization",
            "1.0",
            "--json",
        ],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )

    payload = json.loads(completed.stdout)
    assert payload["xc_model"] == "LSDA"
    assert payload["spin_polarization"] > 0


def test_cli_accepts_hf_mode() -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{SRC}:{env.get('PYTHONPATH', '')}"

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "pydft.core.parser",
            "run",
            "--symbol",
            "He",
            "--num-points",
            "450",
            "--max-iterations",
            "120",
            "--xc-model",
            "HF",
            "--spin-polarization",
            "0.0",
            "--json",
        ],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )

    payload = json.loads(completed.stdout)
    assert payload["xc_model"] == "HF"
    assert payload["total_energy"] < -2.7
