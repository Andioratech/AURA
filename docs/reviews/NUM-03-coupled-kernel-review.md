# NUM-03 Interim Review — First Coupled Hasegawa Kernel

**Date:** 2026-10-03 · **Disposition:** Focused kernel checks PASS; NUM-03 remains ACTIVE and no pilot is accepted

## Scope reviewed

This review covers the initial `evaluate_hasegawa_piston_sphere_field` implementation in `src/aura/fields/hasegawa.py` and its explicit-order diagnostic. The modeled case uses a coaxial uniformly moving circular piston at `z=0` and a stationary rigid sound-hard sphere centered on `+z`, in homogeneous, linear, lossless air under `exp(-iwt)`. Source factors are the conjugated Hasegawa series for the project convention. The sphere scattering branch is `-j'_n(ka)/h'_n(ka)` at every order, including stationary `n=1`; the translating-sphere branch is not used.

The routine accepts a caller-selected maximum order, piston peak face velocity, geometry, air parameters, exterior Cartesian points and a local workspace cap. It returns FIELD-1.0 pressure, particle velocity and pressure gradient. It rejects points on/behind the piston-baffle plane, points within the sphere, `kr > 40`, orders above 512 and inadequate local workspace. Its order-sequence function reports observed relative changes only; it does not accept convergence. Neither interface is connected yet to NUM-02 run-level preflight, chunk manifests or the immutable run lifecycle. Runtime readiness remains INDETERMINATE.

## Evidence

- Eight focused tests pass. A conventional unscaled modal sum at one off-axis exterior point independently checks pressure, all velocity components and pressure-gradient components against the scaled coupled kernel at order 36. Agreement is within the test's `1e-10` relative comparison budget; this validates those implementation equations for that point/order, not the full domain.
- Front and rear pole samples at the minimum declared gap have normal particle velocity below `4.1e-17 m/s`; the 60° off-axis sphere-surface sample is also below `1e-13 m/s` at order 100. These checks are consistent with the stationary sound-hard boundary at three selected points, not the full surface.
- Explicit order 280→300 pressure differences at the minimum-gap poles are `2.27e-13` at the front and `1.59e-11` at the rear. These are pointwise order diagnostics only. They do not bound a tail, establish surface-wide convergence or determine a production tolerance.
- The local workspace rejection test replaces the scaled source-factor constructor with a failing sentinel and confirms inadequate memory is rejected first.
- The exact full local Quality workflow for commit `ae4788f8f06eba62bb416b9f2cdc2a5232487194` passed: ENV-1.0, hash-locked install, editable install, `pip check`, Ruff, required-document checks and 1,656 tests. Its remote [Quality run 37143645550](https://github.com/Andioratech/AURA/actions/runs/37143645550) completed successfully.
- An exploratory comparison used piston radii 0.1 m and 1.0 m, outside the frozen 10 mm aperture, at order 30 through 300. Pressure differences from the plane-wave/sphere reference remained large (relative differences 0.41–1.85 at the on/off-axis samples). This is not a valid rejection of the model or of convergence: the sharp, uniformly driven finite-disk axial Rayleigh expression contains an edge term `exp(ik sqrt(z²+R²))` whose magnitude does not vanish as aperture radius increases, so this naive aperture limit does not converge pointwise. A valid P3 overlap test must feed plane-wave-equivalent incident modal coefficients to the sphere-scattering evaluator, rather than treating an ever-wider sharp piston as a plane wave. The exploratory mismatch is retained as an inconclusive failed comparison, not a physical result.

## Limitations and open work

There is no coupled comparison yet with the independent plane-wave/sphere field at common points; the plane-wave implementation does not currently serve as a coupled evaluator input. The piston-only Rayleigh checks apply to the source-only component, not the coupled solution. P3 overlap, off-axis sphere-boundary tests over the surface, gap-wide and order-wide convergence, far-field behavior, estimator/live-array reconciliation, explicit chunking, typed run diagnostics, runtime calibration and a reproducible pilot remain open. No measured air field is compared. This is mathematical software verification in a narrowly bounded ideal model, not model validation, experiment, force/acceleration evidence or gravity-equivalence evidence.

If any independent comparison or resource check fails, preserve the failure and revisit NUM-01. Do not widen `kr`, change sphere/source assumptions, infer a production threshold from the listed point checks, or promote an intermediate test to a phase PASS.
