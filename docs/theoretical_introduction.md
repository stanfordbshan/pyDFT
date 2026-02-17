# Theoretical Introduction

This document gives the theoretical background for the educational `pyDFT` code.
It is written to match what the current implementation actually solves in
`src/pydft/core`.

## 1. Scope and Physical Model

The code models atom-like systems with these assumptions:

1. Non-relativistic electrons.
2. Fixed nuclei (Born-Oppenheimer approximation).
3. Spherical symmetry (radial atom model).
4. Local or local-spin density approximation (LDA/LSDA).
5. Kohn-Sham self-consistent field (SCF) method.

All equations are in atomic units (a.u.):

- $\hbar=1$
- $m_e=1$
- $|e|=1$
- $4\pi\epsilon_0=1$

So energies are in Hartree and distances in Bohr.

## 2. From Many-Electron Problem to DFT

For an atom with nuclear charge $Z$ at the origin, the electronic Hamiltonian is

$$
\hat{H} = \sum_{i=1}^{N}\left(-\frac{1}{2}\nabla_i^2 - \frac{Z}{r_i}\right)
+ \sum_{i<j}\frac{1}{|\mathbf{r}_i-\mathbf{r}_j|}.
$$

Direct many-body solution is expensive, so DFT reformulates the ground-state
problem in terms of the density $n(\mathbf{r})$.

The Hohenberg-Kohn framework writes the ground-state energy as

$$
E[n] = F[n] + \int V_{\mathrm{ext}}(\mathbf{r})\, n(\mathbf{r})\, d^3r,
$$

where $V_{\mathrm{ext}}(\mathbf{r})=-Z/r$, and $F[n]$ is universal.

## 3. Kohn-Sham Decomposition

Kohn-Sham DFT introduces a non-interacting reference system with the same
density:

$$
F[n] = T_s[n] + E_H[n] + E_{xc}[n].
$$

- $T_s[n]$: non-interacting kinetic functional.
- $E_H[n]$: Hartree (classical Coulomb) energy.
- $E_{xc}[n]$: exchange-correlation (everything else).

The Hartree energy is

$$
E_H[n] = \frac{1}{2}\iint
\frac{n(\mathbf{r})n(\mathbf{r}')}{|\mathbf{r}-\mathbf{r}'|}
\, d^3r\, d^3r'.
$$

Stationarity gives single-particle Kohn-Sham equations:

$$
\left[-\frac{1}{2}\nabla^2 + V_{\mathrm{eff}}(\mathbf{r})\right]\phi_i(\mathbf{r})
= \epsilon_i\phi_i(\mathbf{r}),
$$

with

$$
V_{\mathrm{eff}}(\mathbf{r}) = V_{\mathrm{ext}}(\mathbf{r})
+ V_H(\mathbf{r}) + V_{xc}(\mathbf{r}),
$$

$$
V_H(\mathbf{r}) = \int \frac{n(\mathbf{r}')}{|\mathbf{r}-\mathbf{r}'|}\, d^3r',
\qquad
V_{xc}(\mathbf{r}) = \frac{\delta E_{xc}}{\delta n(\mathbf{r})}.
$$

Density is rebuilt from orbitals:

$$
n(\mathbf{r}) = \sum_i f_i |\phi_i(\mathbf{r})|^2,
$$

where $f_i$ are occupancies.

## 4. Spherical Reduction Used in This Repo

For atoms, orbitals are separated as

$$
\phi_{nlm}(\mathbf{r}) = R_{nl}(r)Y_{lm}(\hat{\mathbf{r}}),
$$

and define

$$
u_{nl}(r) = r R_{nl}(r).
$$

Then each $(n,l)$ channel satisfies a 1D radial equation:

$$
\left[-\frac{1}{2}\frac{d^2}{dr^2} + \frac{l(l+1)}{2r^2} + V_{\mathrm{eff}}(r)\right]
 u_{nl}(r) = \epsilon_{nl}u_{nl}(r).
$$

Normalization in this representation is

$$
\int_0^{\infty} |u_{nl}(r)|^2\, dr = 1.
$$

Radial density formula used in code:

$$
n(r) = \sum_{nl} f_{nl}\, \frac{|u_{nl}(r)|^2}{4\pi r^2}.
$$

Occupancy capacity of each radial state is

$$
0 \le f_{nl} \le 2(2l+1),
$$

(two spins times $(2l+1)$ magnetic degeneracy).

## 5. Spherical Hartree Potential Formula

For a spherical density, define

$$
q(r) = 4\pi r^2 n(r),
\qquad
Q(r) = \int_0^r q(s)\, ds.
$$

Then

$$
V_H(r) = \frac{Q(r)}{r} + \int_r^{\infty}\frac{q(s)}{s}\, ds.
$$

This form is exactly what the implementation computes in
`src/pydft/core/potentials.py`.

## 6. LDA and LSDA Exchange-Correlation in This Repo

The code provides both:

1. LDA (spin-unpolarized), implemented in `src/pydft/core/functionals.py`.
2. LSDA (spin-polarized), implemented in `src/pydft/core/lsda.py`.

Both use:

- Dirac exchange.
- Perdew-Zunger 1981 (PZ81) correlation.

### 6.1 LDA formulas

For total density $n$:

$$
\epsilon_x(n) = -\frac{3}{4}\left(\frac{3}{\pi}\right)^{1/3} n^{1/3},
$$

$$
v_x(n) = \frac{d(n\epsilon_x)}{dn}
= -\left(\frac{3}{\pi}\right)^{1/3} n^{1/3}.
$$

Define

$$
r_s = \left(\frac{3}{4\pi n}\right)^{1/3}.
$$

PZ81 correlation is piecewise:

For $r_s<1$:

$$
\epsilon_c(r_s)=A\ln r_s + B + C r_s\ln r_s + D r_s,
$$

with

$$
A=0.0311,\; B=-0.048,\; C=0.0020,\; D=-0.0116.
$$

For $r_s\ge1$:

$$
\epsilon_c(r_s)=\frac{\gamma}{1+\beta_1\sqrt{r_s}+\beta_2 r_s},
$$

with

$$
\gamma=-0.1423,\; \beta_1=1.0529,\; \beta_2=0.3334.
$$

The corresponding correlation potential is

$$
v_c = \epsilon_c - \frac{r_s}{3}\frac{d\epsilon_c}{dr_s}.
$$

Then

$$
\epsilon_{xc}=\epsilon_x+\epsilon_c,\qquad v_{xc}=v_x+v_c.
$$

### 6.2 LSDA formulas

In LSDA, define spin densities:

$$
n = n_\uparrow + n_\downarrow,\qquad
\zeta = \frac{n_\uparrow - n_\downarrow}{n}.
$$

Spin-resolved Dirac exchange energy density is

$$
e_x(n_\uparrow,n_\downarrow)
= -\frac{3}{4}\left(\frac{3}{\pi}\right)^{1/3}2^{1/3}
\left(n_\uparrow^{4/3}+n_\downarrow^{4/3}\right).
$$

Thus exchange energy per particle is

$$
\epsilon_x = \frac{e_x}{n},
$$

and spin potentials are

$$
v_{x,\uparrow} = -\left(\frac{6}{\pi}\right)^{1/3}n_\uparrow^{1/3},\qquad
v_{x,\downarrow} = -\left(\frac{6}{\pi}\right)^{1/3}n_\downarrow^{1/3}.
$$

PZ81 correlation is evaluated for unpolarized and fully polarized limits, then
interpolated with

$$
f(\zeta)=\frac{(1+\zeta)^{4/3}+(1-\zeta)^{4/3}-2}{2^{4/3}-2}.
$$

The implementation computes:

$$
\epsilon_c(r_s,\zeta)=\epsilon_c^{(0)}(r_s)+
\left[\epsilon_c^{(1)}(r_s)-\epsilon_c^{(0)}(r_s)\right]f(\zeta),
$$

then obtains $v_{c,\uparrow}$ and $v_{c,\downarrow}$ from derivatives with
respect to $n_\uparrow$ and $n_\downarrow$.

Finally:

$$
\epsilon_{xc}=\epsilon_x+\epsilon_c,\quad
v_{xc,\uparrow}=v_{x,\uparrow}+v_{c,\uparrow},\quad
v_{xc,\downarrow}=v_{x,\downarrow}+v_{c,\downarrow}.
$$

## 7. Total Energy Expression Used for Reporting

In LDA mode, the code reports

$$
E_{\mathrm{tot}} = \sum_i f_i\epsilon_i
- E_H[n] + E_{xc}[n] - \int n(\mathbf{r})v_{xc}(\mathbf{r})\, d^3r.
$$

with

$$
E_H[n] = \frac{1}{2}\int n(\mathbf{r})V_H(\mathbf{r})\, d^3r,
$$

$$
E_{xc}[n] = \int n(\mathbf{r})\epsilon_{xc}(n(\mathbf{r}))\, d^3r.
$$

In LSDA mode, the last term becomes spin-resolved:

$$
E_{\mathrm{tot}}^{\mathrm{LSDA}} = \sum_i f_i\epsilon_i
- E_H[n] + E_{xc}[n_\uparrow,n_\downarrow]
- \int \left[n_\uparrow v_{xc,\uparrow} + n_\downarrow v_{xc,\downarrow}\right]d^3r.
$$

The subtractions remove double counting of interaction terms already contained
in the orbital eigenvalue sum.

## 8. Numerical Discretization

### 8.1 Radial grid

Uniform grid on $[r_{\min},r_{\max}]$:

$$
r_j = r_{\min} + j\Delta r,\quad j=0,\dots,N-1,
$$

with small positive $r_{\min}$ to avoid singular division by zero.

### 8.2 Finite-difference radial Hamiltonian

For interior points, second derivative is approximated as

$$
\frac{d^2u}{dr^2}\bigg|_{r_j}
\approx \frac{u_{j+1}-2u_j+u_{j-1}}{\Delta r^2}.
$$

This yields a tridiagonal matrix:

$$
H_{jj} = \frac{1}{\Delta r^2} + \frac{l(l+1)}{2r_j^2} + V_{\mathrm{eff}}(r_j),
$$

$$
H_{j,j\pm1} = -\frac{1}{2\Delta r^2}.
$$

The implementation enforces Dirichlet boundary conditions on the transformed
radial function:

$$
u(0)=0,\qquad u(r_{\max})=0.
$$

Only interior points are solved, then boundary zeros are reattached. This
removes spurious endpoint states and gives physically correct lowest energies.

Implementation location:
`src/pydft/core/radial_solver.py`.

### 8.3 Spherical integrals

For any spherical function $f(r)$,

$$
\int f(\mathbf{r})\, d^3r = 4\pi\int_0^{\infty} f(r)r^2 dr,
$$

numerically evaluated by trapezoidal quadrature on the radial grid.

## 9. SCF Procedure in This Repo

Given initial density $n^{(0)}(r)$, for iteration $k$:

1. Build effective potentials:
   - LDA: $V_{\mathrm{eff}}[n^{(k)}]$.
   - LSDA: $V_{\mathrm{eff},\uparrow}[n_\uparrow^{(k)},n_\downarrow^{(k)}]$ and
     $V_{\mathrm{eff},\downarrow}[n_\uparrow^{(k)},n_\downarrow^{(k)}]$.
2. Solve radial KS eigenproblems for each $l$.
3. Fill electrons by ascending $\epsilon_{nl}$:
   - LDA: capacity $2(2l+1)$.
   - LSDA (per spin channel): capacity $(2l+1)$.
4. Build output density:
   - LDA: $\tilde{n}^{(k)}(r)$.
   - LSDA: $\tilde{n}_\uparrow^{(k)}(r)$ and $\tilde{n}_\downarrow^{(k)}(r)$.
5. Linear mixing:

$$
n^{(k+1)} = (1-\alpha)n^{(k)} + \alpha\tilde{n}^{(k)},
$$

where $\alpha$ is `density_mixing`.

LSDA applies the same mixing formula independently to $n_\uparrow$ and
$n_\downarrow$.

6. Normalize to electron count:

$$
\int n^{(k+1)}(\mathbf{r})\, d^3r = N.
$$

7. Convergence metric:

$$
\Delta^{(k)} = \max_r\left|n^{(k+1)}(r)-n^{(k)}(r)\right|.
$$

Stop when

$$
\Delta^{(k)} < \texttt{density\_tolerance}
$$

or maximum iterations reached.

## 10. Mapping GUI/CLI Parameters to Theory

- `r_max`: radial simulation box size $r_{\max}$.
- `num_points`: grid resolution $N$.
- `l_max`: highest angular channel $l$ included.
- `states_per_l`: number of radial eigenstates kept per $l$.
- `density_mixing`: $\alpha$ in linear mixing.
- `density_tolerance`: SCF stop criterion $\Delta$.
- `use_hartree`, `use_exchange`, `use_correlation`: switches for terms in
  $V_{\mathrm{eff}}$ and total-energy bookkeeping.
- `xc_model`: chooses `LDA` or `LSDA`.
- `spin_polarization`: optional $\zeta=(N_\uparrow-N_\downarrow)/N$ target in
  LSDA mode.

## 11. Expected Behavior and Practical Interpretation

- For one-electron systems with Hartree and XC disabled, the model approaches
  the hydrogenic Schrodinger limit.
- With LDA enabled, total energies are approximate and should be interpreted as
  pedagogical DFT outputs, not production all-electron reference data.
- For open-shell systems, LSDA can lower total energy relative to LDA by
  allowing $n_\uparrow \neq n_\downarrow$.
- Density tails are physically small and can require log-scale plotting to be
  visually informative.

## 12. Known Limitations of the Present Model

1. Spherical symmetry only (no molecules, no angularly resolved geometry).
2. Exchange-correlation restricted to LDA/LSDA (no GGA/hybrid/meta-GGA).
3. No relativistic corrections.
4. Finite-domain and finite-grid discretization errors.

These simplifications are intentional for educational clarity.

## 13. Suggested Reading

1. R. M. Martin, *Electronic Structure: Basic Theory and Practical Methods*.
2. W. Kohn and L. J. Sham, Phys. Rev. 140, A1133 (1965).
3. J. P. Perdew and A. Zunger, Phys. Rev. B 23, 5048 (1981).

## 14. License and authorship

This software is developed by **Prof. Bin Shan** ([bshan@mail.hust.edu.cn](mailto:bshan@mail.hust.edu.cn)).

Released under the MIT License. See [../LICENSE](../LICENSE).
