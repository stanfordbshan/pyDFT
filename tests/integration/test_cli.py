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
            "pydft.backend.cli",
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
