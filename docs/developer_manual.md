# Developer Manual

## 1. Architecture goals

The codebase is split into backend and frontend concerns.

- Backend (`pydft.core`): physics, numerics, standalone CLI, optional HTTP API.
- Frontend (`pydft.gui` + `pydft.assets`): pywebview window + JavaScript UI.

No DFT math is implemented in the frontend.

For a full derivation of the equations implemented in this repository, see:
- `/Users/bshan/GitHub/pyDFT/docs/theoretical_introduction.md`

## 2. Directory layout

- `/Users/bshan/GitHub/pyDFT/src/pydft/main.py`: top-level app entrypoint.
- `/Users/bshan/GitHub/pyDFT/src/pydft/core/dft_engine.py`: SCF loop and total-energy assembly.
- `/Users/bshan/GitHub/pyDFT/src/pydft/core/parser.py`: CLI + payload parsing helpers.
- `/Users/bshan/GitHub/pyDFT/src/pydft/core/models.py`: shared dataclasses.
- `/Users/bshan/GitHub/pyDFT/src/pydft/core/grid.py`: radial grid + spherical integration helpers.
- `/Users/bshan/GitHub/pyDFT/src/pydft/core/functionals.py`: LDA XC formulas.
- `/Users/bshan/GitHub/pyDFT/src/pydft/core/potentials.py`: external and Hartree potentials.
- `/Users/bshan/GitHub/pyDFT/src/pydft/core/radial_solver.py`: finite-difference radial eigenproblem.
- `/Users/bshan/GitHub/pyDFT/src/pydft/core/occupations.py`: occupancy filling and degeneracy handling.
- `/Users/bshan/GitHub/pyDFT/src/pydft/core/presets.py`: simple-system presets.
- `/Users/bshan/GitHub/pyDFT/src/pydft/core/api.py`: optional FastAPI endpoints.
- `/Users/bshan/GitHub/pyDFT/src/pydft/core/api_server.py`: `pydft-api` runner.
- `/Users/bshan/GitHub/pyDFT/src/pydft/gui/window.py`: `webview.create_window(...)` setup.
- `/Users/bshan/GitHub/pyDFT/src/pydft/gui/api.py`: Python-JS bridge class used by pywebview.
- `/Users/bshan/GitHub/pyDFT/src/pydft/assets/*`: HTML/CSS/JS frontend assets.
- `/Users/bshan/GitHub/pyDFT/tests/unit/*`: unit tests.
- `/Users/bshan/GitHub/pyDFT/tests/integration/*`: integration + benchmark tests.

## 3. Numerical model

### 3.1 Radial Kohn-Sham equation

For each angular momentum channel `l`, solve for `u(r) = r R(r)`:

`-1/2 d²u/dr² + [l(l+1)/(2r²) + V_eff(r)] u = epsilon u`

Finite-difference discretization is used on a uniform radial grid.

### 3.2 Potentials

- External potential: `V_ext(r) = -Z/r`
- Hartree (spherical):
  `V_H(r) = Q(r)/r + integral_r^infty [q(r')/r'] dr'`
  where `q(r) = 4 pi r² n(r)` and `Q(r)=integral_0^r q(r')dr'`.
- XC: LDA unpolarized:
  - Exchange: Dirac form.
  - Correlation: Perdew-Zunger 1981 parameterization.

### 3.3 Energy expression

`E = sum_i f_i epsilon_i - E_H + E_xc - integral n(r) v_xc(r) d^3r`

where `E_H = 1/2 integral n(r) V_H(r) d^3r`.

## 4. SCF strategy

- Start from a hydrogenic density guess.
- Build `V_eff` from current density.
- Solve radial KS equations for each `l` channel.
- Fill electrons by ascending eigenvalue with `2(2l+1)` degeneracy.
- Build new density from occupied orbitals.
- Apply linear density mixing.
- Stop on max-density-difference tolerance.

## 5. Execution modes

1. Standalone mode: `pydft-cli run ...`
2. pywebview mode: `pydft` or `pydft-webview`
3. Optional HTTP API mode: `pydft-api`

## 6. Testing strategy

- Unit tests validate isolated components:
  - radial grid and integration
  - LDA formulas
  - occupation filling
  - Hartree asymptotic behavior
- Integration tests validate:
  - FastAPI endpoint execution
  - CLI JSON execution
  - benchmark comparisons

## 7. Benchmark references

Reference values currently used:

1. Hydrogen exact non-relativistic 1s energy (single-particle benchmark mode):
   `E = -0.5 Ha`
2. NIST Atomic DFT LDA helium total energy:
   `E_tot = -2.834836 Ha`

NIST table URLs:
- https://math.nist.gov/DFTdata/atomdata/node17.html
- https://math.nist.gov/DFTdata/atomdata/node18.html

The helium tolerance is intentionally wider in tests because this implementation is educational and uses a simple finite-difference setup.
