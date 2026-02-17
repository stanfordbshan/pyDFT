# Developer Manual

## 1. Architecture goals

The codebase is intentionally split into backend and frontend.

- Backend: all physics, numerics, and API logic.
- Frontend: pywebview desktop UI that only calls backend API.

No DFT logic exists in the frontend.

## 2. Directory layout

- `src/pydft/backend/models.py`: shared dataclasses.
- `src/pydft/backend/grid.py`: radial grid + spherical integration helpers.
- `src/pydft/backend/functionals.py`: LDA XC formulas.
- `src/pydft/backend/potentials.py`: external and Hartree potentials.
- `src/pydft/backend/radial_solver.py`: finite-difference radial eigenproblem.
- `src/pydft/backend/occupations.py`: occupancy filling and degeneracy handling.
- `src/pydft/backend/scf.py`: SCF loop and total-energy assembly.
- `src/pydft/backend/api.py`: FastAPI endpoints.
- `src/pydft/backend/cli.py`: standalone CLI.
- `src/pydft/frontend/app.py`: pywebview launcher.
- `src/pydft/frontend/ui/*`: HTML/CSS/JS frontend assets.
- `tests/unit/*`: unit tests.
- `tests/integration/*`: integration + benchmark tests.

## 3. Numerical model

### 3.1 Radial Kohn-Sham equation

For each angular momentum channel `l`, we solve for `u(r) = r R(r)`:

-1/2 d²u/dr² + [l(l+1)/(2r²) + V_eff(r)] u = epsilon u

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

Total energy is reported from standard KS decomposition:

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

## 5. Backend usage modes

1. Standalone mode: `pydft-cli run ...`
2. API mode: `pydft-api` exposing HTTP endpoints.

The frontend uses mode 2.

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

The Helium tolerance is intentionally wider in tests because this implementation is educational and uses a simple finite-difference setup.
