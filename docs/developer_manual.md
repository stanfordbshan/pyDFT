# Developer Manual

## 1. Architecture goals

The codebase is split into backend and frontend concerns.

- Backend (`pydft.core`): physics, numerics, standalone CLI, optional HTTP API.
- Frontend (`pydft.gui` + `pydft.gui.assets`): pywebview window + JavaScript UI.

No DFT math is implemented in the frontend.

For a full derivation of the equations implemented in this repository, see:
- [theoretical_introduction.md](theoretical_introduction.md)

## 2. Directory layout

- `src/pydft/main.py`: top-level app entrypoint.
- `src/pydft/core/dft_engine.py`: SCF loop and total-energy assembly.
- `src/pydft/core/parser.py`: CLI + payload parsing helpers.
- `src/pydft/core/models.py`: shared dataclasses.
- `src/pydft/core/grid.py`: radial grid + spherical integration helpers.
- `src/pydft/core/functionals.py`: LDA XC formulas.
- `src/pydft/core/lsda.py`: LSDA spin-resolved XC formulas and spin splitting helpers.
- `src/pydft/core/hartree_fock.py`: educational radial HF implementation.
- `src/pydft/core/potentials.py`: external and Hartree potentials.
- `src/pydft/core/radial_solver.py`: finite-difference radial eigenproblem.
- `src/pydft/core/occupations.py`: occupancy filling and degeneracy handling.
- `src/pydft/core/presets.py`: simple-system presets.
- `src/pydft/api/app.py`: optional FastAPI endpoints.
- `src/pydft/api/server.py`: `pydft-api` runner.
- `src/pydft/gui/window.py`: `webview.create_window(...)` setup.
- `src/pydft/gui/api.py`: Python-JS bridge class used by pywebview.
- `src/pydft/gui/assets/*`: HTML/CSS/JS frontend assets.
- `tests/unit/*`: unit tests.
- `tests/integration/*`: integration + benchmark tests.

## 3. Numerical model

### 3.1 Radial Kohn-Sham equation

For each angular momentum channel $l$, solve for $u(r)=rR(r)$:

$$
-\frac{1}{2}\frac{d^2u}{dr^2} + \left[\frac{l(l+1)}{2r^2} + V_{\mathrm{eff}}(r)\right]u = \epsilon u.
$$

Finite-difference discretization is used on a uniform radial grid.

### 3.2 Potentials

- External potential: $V_{\mathrm{ext}}(r)=-Z/r$.
- Hartree (spherical):

$$
V_H(r) = \frac{Q(r)}{r} + \int_r^{\infty}\frac{q(r')}{r'}dr',
$$

with

$$
q(r)=4\pi r^2 n(r),\qquad Q(r)=\int_0^r q(r')dr'.
$$

- XC:
  - LDA: unpolarized Dirac exchange + PZ81 correlation.
  - LSDA: spin-resolved extension with $n_\uparrow$, $n_\downarrow$ and
    $\zeta=(n_\uparrow-n_\downarrow)/(n_\uparrow+n_\downarrow)$.
- HF (current educational module):
  - exchange-only, no correlation
  - one occupied $1s$-like orbital per spin channel
  - intended for up to two-electron atoms (H/He+/He)

### 3.3 Energy expression

$$
E = \sum_i f_i\epsilon_i - E_H + E_{xc} - \int n(r)v_{xc}(r)\, d^3r,
$$

where

$$
E_H = \frac{1}{2}\int n(r)V_H(r)\, d^3r.
$$

## 4. SCF strategy

- Start from a hydrogenic density guess.
- Build $V_{\mathrm{eff}}$ from current density.
- In LSDA mode, build separate $V_{\mathrm{eff},\uparrow}$ and
  $V_{\mathrm{eff},\downarrow}$ from spin densities.
- In HF mode, build spin-channel Fock-like radial potentials with same-spin
  self-interaction cancellation.
- Solve radial KS equations for each $l$ channel.
- Fill electrons by ascending eigenvalue:
  - LDA: $2(2l+1)$ capacity per radial state.
  - LSDA per spin channel: $(2l+1)$ capacity.
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
   $E=-0.5\ \mathrm{Ha}$.
2. NIST Atomic DFT LDA helium total energy:
   $E_{\mathrm{tot}}=-2.834836\ \mathrm{Ha}$.
3. Helium restricted HF reference:
   $E_{\mathrm{tot}}\approx-2.86168\ \mathrm{Ha}$.

NIST table URLs:
- https://math.nist.gov/DFTdata/atomdata/node17.html
- https://math.nist.gov/DFTdata/atomdata/node18.html

The helium tolerance is intentionally wider in tests because this implementation is educational and uses a simple finite-difference setup.

## 8. License and authorship

This software is developed by **Prof. Bin Shan** ([bshan@mail.hust.edu.cn](mailto:bshan@mail.hust.edu.cn)).

Released under the MIT License. See [../LICENSE](../LICENSE).
