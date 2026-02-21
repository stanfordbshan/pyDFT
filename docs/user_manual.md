# User Manual

## 1. What pyDFT Does

`pyDFT` is an educational toolkit for simple atom-like electronic-structure calculations.

Supported method families:

- `LDA` (spin-unpolarized)
- `LSDA` (spin-polarized)
- educational `HF` (exchange-only, currently targeted at H/He+/He)

## 2. Installation

From repository root:

```bash
pip install -e .
```

Optional desktop GUI dependency:

```bash
pip install -e '.[frontend]'
```

Testing dependencies:

```bash
pip install -e '.[dev]'
```

## 3. Local Usage

### 3.1 Desktop GUI

```bash
pydft
```

In GUI you can select:

- method (`LDA`, `LSDA`, `HF`)
- compute mode (`direct`, `api`, `auto`)
- API base URL (used by `api` mode and `auto` fallback)

Compute modes:

- `direct`: run inside local desktop process
- `api`: always call remote/local HTTP backend
- `auto`: try direct first, fallback to API

### 3.2 CLI

Basic run:

```bash
pydft-cli run --symbol He --num-points 1200 --max-iterations 200
```

LSDA example:

```bash
pydft-cli run \
  --symbol H \
  --xc-model LSDA \
  --spin-polarization 1.0 \
  --disable-correlation
```

HF example:

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

## 4. Remote Backend Usage

Start API server on backend machine:

```bash
pydft-api --host 0.0.0.0 --port 8000
```

Main endpoints:

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

Then in GUI set:

- `Compute mode = api` (or `auto`)
- `API base URL = http://<server-ip>:8000`

## 5. Troubleshooting

### GUI says direct mode unavailable

You are likely running browser-only frontend (no pywebview host). Use `api` mode or launch with `pydft`.

### Auto mode fails

Check both:

1. local Python environment for direct mode
2. API base URL reachability for fallback mode

### HF run errors on larger atoms

Current educational HF module is intentionally limited to up to two electrons.

### Convergence is slow

Try:

- increasing `max_iterations`
- reducing `density_mixing` (e.g. `0.2`)
- using slightly looser `density_tolerance` (e.g. `1e-5`)

## 6. Testing

Run complete test suite:

```bash
pytest
```

## 7. Accuracy Notes

This project prioritizes readability and educational transparency over production-level performance.
Results depend on grid, basis truncation, and convergence settings.

## 8. Related Docs

- [Developer Manual](developer_manual.md)
- [Theoretical Introduction](theoretical_introduction.md)

## 9. License and Authorship

This software is developed by **Prof. Bin Shan** ([bshan@mail.hust.edu.cn](mailto:bshan@mail.hust.edu.cn)).

Released under the MIT License. See [../LICENSE](../LICENSE).
