# Developer Manual

## 1. Architecture Overview

This repository follows strict layered architecture to keep transport code separate from computational logic.

### Layers

- `pydft/core`: pure domain contracts and shared mapping/validation
- `pydft/application`: transport-agnostic use-cases/orchestration
- `pydft/methods/atomic`: category-specific numerical implementations (LDA/LSDA/HF)
- `pydft/api`: HTTP adapter only (FastAPI schemas/routes/server)
- `pydft/gui`: pywebview adapter only (window lifecycle + bridge)
- `pydft/gui/assets`: static frontend files
- `pydft/cli.py`: CLI adapter only

## 2. Full File Tree

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
│   ├── unit/
│   └── integration/
└── docs/
```

## 3. Dependency Rules

Required direction:

- `api/gui/cli -> application -> core + methods`
- `methods -> core` (for shared models only)
- `core` must not import API/GUI/HTTP frameworks
- `application` must not depend on FastAPI or pywebview types

Practical checks:

- API and GUI adapters call `pydft.application.scf` use-cases
- Shared request mapping is centralized in `pydft.core.request_mapper`
- Numerical kernels are isolated in `pydft.methods.atomic`

## 4. Layer Responsibilities

### `pydft/core`

- Domain dataclasses: `AtomicSystem`, `SCFParameters`, `SCFResult`
- Preset system construction for shared domain inputs
- Shared request mapping/defaulting/validation used by all adapters
- No transport framework imports

### `pydft/application`

- Use-case boundary for running SCF and listing presets
- No HTTP route types, no GUI bridge types

### `pydft/methods/atomic`

- Actual physics/math implementations:
  - LDA/LSDA Kohn-Sham SCF
  - educational HF module
  - grids, potentials, radial solver, occupations

### `pydft/api`

- FastAPI schemas and route handlers only
- Delegates all business execution to application use-cases

### `pydft/gui`

- pywebview host lifecycle and JS bridge only
- Bridge supports `direct`, `api`, `auto` execution paths

## 5. Migration Philosophy

Refactor policy used:

1. Baseline first (tests + smoke outputs)
2. Move code in small, test-guarded slices
3. Introduce application layer before deleting legacy coupling
4. Preserve behavior where possible; keep compatibility wrappers when low-risk
5. Remove mixed concerns after adapters are thin

## 6. Extension Workflow

When adding a new computational method category:

1. Create method module under `src/pydft/methods/<category>/`
2. Reuse `core.models` contracts or extend them conservatively
3. Expose new use-case entry in `application/`
4. Wire API/GUI/CLI adapters through application only
5. Add unit tests for method kernels + mapping
6. Add integration tests for CLI/API contracts
7. Update manuals and examples

## 7. Testing Strategy

- Unit tests:
  - core mapping and model assumptions
  - method kernels (grid/functionals/HF/LSDA/etc.)
  - application and GUI bridge mode logic
- Integration tests:
  - API routes
  - CLI execution
  - contract consistency (API vs direct application)
  - benchmark regression checks

Run all tests:

```bash
pytest
```

## 8. Benchmark References

- Hydrogen exact non-relativistic 1s: $E=-0.5\ \mathrm{Ha}$
- NIST LDA helium total energy: $E_{\mathrm{tot}}=-2.834836\ \mathrm{Ha}$
- Helium restricted HF reference: $E_{\mathrm{tot}}\approx-2.86168\ \mathrm{Ha}$

## 9. License and Authorship

This software is developed by **Prof. Bin Shan** ([bshan@mail.hust.edu.cn](mailto:bshan@mail.hust.edu.cn)).

Released under the MIT License. See [../LICENSE](../LICENSE).
