# User Manual

## 1. What this project does

`pyDFT` is an educational atomic electronic-structure toolkit for simple systems.
Current scope:
- Spherical atoms (H, He+, He, Li, Be, Ne presets; custom Z/N also supported).
- Local (Spin) Density Approximation:
  - LDA (spin-unpolarized): Dirac exchange + Perdew-Zunger correlation.
  - LSDA (spin-polarized): spin-resolved extension of the same exchange/correlation forms.
- Educational Hartree-Fock (HF):
  - exchange-only (no correlation)
  - currently targeted at H, He+, He for clear LDA/LSDA/HF comparisons
- Self-consistent field (SCF) solver on a finite-difference radial grid.

For full theoretical background and derivations, see:
- [theoretical_introduction.md](theoretical_introduction.md)

## 2. Install

From the repository root:

```bash
pip install -e .
```

Optional GUI dependency:

```bash
pip install -e '.[frontend]'
```

Development/test dependencies:

```bash
pip install -e '.[dev]'
```

## 3. Run the desktop app (pywebview)

Preferred entrypoint:

```bash
pydft
```

Equivalent command:

```bash
pydft-webview
```

The frontend talks to Python through the pywebview bridge API (`window.pywebview.api`).

## 4. Run backend as a standalone program

### One SCF run

```bash
pydft-cli run --symbol He --num-points 1200 --max-iterations 200
```

LSDA example (open-shell hydrogen, exchange-only):

```bash
pydft-cli run \
  --symbol H \
  --xc-model LSDA \
  --spin-polarization 1.0 \
  --disable-correlation
```

HF example (helium):

```bash
pydft-cli run \
  --symbol He \
  --xc-model HF \
  --spin-polarization 0.0
```

JSON output:

```bash
pydft-cli run --symbol He --json
```

Write JSON to file:

```bash
pydft-cli run --symbol He --json --output he_result.json
```

### Benchmark-style hydrogen run (single-particle mode)

```bash
pydft-cli run \
  --symbol H \
  --disable-hartree \
  --disable-exchange \
  --disable-correlation \
  --l-max 0
```

## 5. Optional: run backend HTTP API

```bash
pydft-api --host 127.0.0.1 --port 8000
```

Endpoints:
- `GET /api/v1/health`
- `GET /api/v1/presets`
- `POST /api/v1/scf`

Example request:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/scf \
  -H 'Content-Type: application/json' \
  -d '{
    "symbol": "He",
    "parameters": {
      "num_points": 1200,
      "max_iterations": 200,
      "density_mixing": 0.3,
      "xc_model": "HF",
      "spin_polarization": 0.0
    }
  }'
```

## 6. Run tests

```bash
pytest
```

## 7. Run benchmarks

```bash
python -m benchmarks.benchmark_atoms
```

## 8. Notes about accuracy

This code prioritizes educational clarity over production-level numerical performance.
Accuracy depends on:
- `num_points`
- `r_max`
- SCF mixing and tolerance
- orbital basis span (`l_max`, `states_per_l`)
- chosen method (`LDA`, `LSDA`, or `HF`) and spin polarization setting (for `LSDA`/`HF`)

Increase resolution for tighter agreement with reference data.

## 9. License and authorship

This software is developed by **Prof. Bin Shan** ([bshan@mail.hust.edu.cn](mailto:bshan@mail.hust.edu.cn)).

Released under the MIT License. See [../LICENSE](../LICENSE).
