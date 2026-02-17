# pyDFT

Educational density functional theory (DFT) code for simple atomic systems.

## Key features
- `pydft.core`: Kohn-Sham LDA SCF solver (backend physics/math).
- `pydft.gui`: pywebview desktop frontend logic.
- `pydft.assets`: HTML/CSS/JS assets used by the GUI.
- Standalone CLI mode (`pydft-cli`).
- Optional FastAPI service mode (`pydft-api`).
- Unit, integration, and benchmark tests via `pytest`.

## Recommended structure

```text
pyDFT/
├── pyproject.toml
├── README.md
├── src/
│   └── pydft/
│       ├── __init__.py
│       ├── __main__.py
│       ├── main.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── __main__.py
│       │   ├── dft_engine.py
│       │   ├── parser.py
│       │   ├── models.py
│       │   ├── grid.py
│       │   ├── functionals.py
│       │   ├── potentials.py
│       │   ├── radial_solver.py
│       │   ├── occupations.py
│       │   ├── presets.py
│       │   ├── api.py
│       │   └── api_server.py
│       ├── gui/
│       │   ├── __init__.py
│       │   ├── __main__.py
│       │   ├── window.py
│       │   └── api.py
│       └── assets/
│           ├── index.html
│           ├── styles.css
│           └── app.js
├── tests/
├── benchmarks/
└── docs/
```

## Docs
- `/Users/bshan/GitHub/pyDFT/docs/user_manual.md`
- `/Users/bshan/GitHub/pyDFT/docs/developer_manual.md`
- `/Users/bshan/GitHub/pyDFT/docs/theoretical_introduction.md`
