# pyDFT

Educational density functional theory (DFT) code for simple atomic systems.

Developed by **Prof. Bin Shan** ([bshan@mail.hust.edu.cn](mailto:bshan@mail.hust.edu.cn)).

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
- [User Manual](docs/user_manual.md)
- [Developer Manual](docs/developer_manual.md)
- [Theoretical Introduction](docs/theoretical_introduction.md)

## License

This project is released under the MIT License.
See [LICENSE](LICENSE) for the full text.

Copyright (c) 2026 Prof. Bin Shan

