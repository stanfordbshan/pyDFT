# pyDFT

Educational atomic electronic-structure toolkit with strict layered architecture.

Developed by **Prof. Bin Shan** ([bshan@mail.hust.edu.cn](mailto:bshan@mail.hust.edu.cn)).

## Quick Start

Install editable package:

```bash
pip install -e .
```

Optional extras:

```bash
pip install -e '.[frontend,dev]'
```

Run desktop GUI (pywebview host):

```bash
pydft
```

Run CLI calculation:

```bash
pydft-cli run --symbol He --xc-model LDA
```

Run HTTP backend:

```bash
pydft-api --host 127.0.0.1 --port 8000
```

## Compute Modes (GUI)

The GUI supports three compute modes:

- `direct`: in-process execution via the Python bridge (no HTTP hop)
- `api`: send request to configured HTTP backend URL
- `auto`: try `direct` first, then API fallback if direct fails

`API base URL` is configurable in the GUI form and is used by `api` and `auto` fallback paths.

## Layered Architecture

```text
pyDFT/
├── pyproject.toml
├── README.md
├── src/
│   └── pydft/
│       ├── __init__.py
│       ├── __main__.py
│       ├── main.py
│       ├── cli.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── __main__.py
│       │   ├── models.py
│       │   ├── presets.py
│       │   ├── request_mapper.py
│       │   └── parser.py
│       ├── application/
│       │   ├── __init__.py
│       │   └── scf.py
│       ├── methods/
│       │   ├── __init__.py
│       │   └── atomic/
│       │       ├── __init__.py
│       │       ├── dft_engine.py
│       │       ├── functionals.py
│       │       ├── grid.py
│       │       ├── hartree_fock.py
│       │       ├── lsda.py
│       │       ├── occupations.py
│       │       ├── potentials.py
│       │       └── radial_solver.py
│       ├── api/
│       │   ├── __init__.py
│       │   ├── __main__.py
│       │   ├── app.py
│       │   └── server.py
│       └── gui/
│           ├── __init__.py
│           ├── __main__.py
│           ├── bridge.py
│           ├── window.py
│           └── assets/
│               ├── index.html
│               ├── styles.css
│               └── app.js
├── tests/
├── benchmarks/
└── docs/
```

## Docs

- [User Manual](docs/user_manual.md)
- [Developer Manual](docs/developer_manual.md)
- [Theoretical Introduction](docs/theoretical_introduction.md)

## License

This project is released under the MIT License. See [LICENSE](LICENSE).

Copyright (c) 2026 Prof. Bin Shan
