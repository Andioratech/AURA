# ANA-07 Numerical Sensitivity Review

**Scope:** precision, phase, source-exclusion and cancellation checks for the frozen ideal-field kernels · **Disposition:** reviewed software scope; no failure found in the checks below

## Existing test evidence reviewed

The current software suite already checks several numerical-risk points independently of the 32 recorded campaign configurations:

- The B-03, B-04, B-05 and B-06 Decimal references are recomputed at 60 and 80 digits; the frozen comparison values remain stable within `1e-45` of each reference scale.
- The field tests compare the platform `sin`, `cos` and (for the spherical kernel) `hypot` operations at the exact arguments used by each frozen case with an 80-digit Decimal computation. The asserted absolute trigonometric error is at most four binary64 epsilons; spherical norm error is at most two epsilons.
- B-04 tests include standing-wave pressure nodes, antinodes, phase variants, signed mean flux and the nonzero velocity at a pressure node. The B-05 tests include coherent cross terms, phase changes, and samples immediately on both sides of a neighboring node using `math.nextafter`.
- B-06 tests cover a translated source, radial direction changes, a common phase shift, the exact exclusion radius and its adjacent representable radii, the full reactive velocity, and rejection of ill-conditioned phases and out-of-range numerical inputs.
- Known-wrong pressure, velocity, gradient and spreading substitutions are checked against independent references. These are software detection checks, not alternate physical models.

The exact production source, test suite and environment were checked by full local Quality at 1,385 tests; the exact commit checks are linked in the [recorded matrix report](../benchmarks/ANA-07-recorded-field-matrix.md).

## Additional B-04 node probe

As a separate exploratory diagnostic, the B04-EQUAL pressure-node coordinate `x = 0.000375 m` was moved by exactly one representable binary64 step below and above using `math.nextafter`. The source amplitudes, phases, frequency, fixed tolerance and Decimal oracle were unchanged. Each perturbed case was evaluated with the production pair kernel and compared with the independent Decimal B-04 reference.

| Sample coordinate | Offset from node | Normalized max pressure error | Velocity error | Gradient error | Mean-intensity error |
|---:|---:|---:|---:|---:|---:|
| `0.00037499999999999995 m` | `-5.421010862427522e-20 m` | `7.383743464307944e-17` | `0` | `0` | `0` |
| `0.00037500000000000006 m` | `+5.421010862427522e-20 m` | `9.051514731951984e-17` | `0` | `0` | `0` |

At the two neighboring points, pressure magnitude was `1.133107779529596e-15 Pa` and `6.432490598706545e-16 Pa`, while axial fluid velocity remained `2.666666666666667e-6 m/s`. The normalized errors are below the fixed `4.547473508864641e-13` budget. The complete machine-readable input, source and environment hashes, observed components and independent values are retained at `results/verification/ANA-07/SENS-B04-NODE-ULP-260c730-attempt2/record.json`, SHA-256 `8f162f80184eb5828f8b746b6bb1f081bc0f828a95a8b6eee23ad471209ec426`.

An initial report-formatting attempt completed the in-memory calculation but failed while arranging the JSON fields. It did not produce an accepted sensitivity result. The failure is preserved at `results/verification/ANA-07/SENS-B04-NODE-ULP-260c730/attempt-1-failure.json`, SHA-256 `fc33d407e4bc446110e8ae6b4374145b739a9feddafd95596b912984c7fd5255`; a separate corrected attempt produced the report above. No input, kernel, oracle or acceptance tolerance was changed between these report attempts.

## Audit applicability and decision

For the declared uncoupled-field scope, each recorded case already receives independent pressure, every velocity and gradient component, and derived mean-intensity comparisons. ANA-06 separately checks closed-surface energy balance for four exact ideal source definitions, including the source definition shared with B06-AXIAL. These ledger checks are supporting evidence for those four definitions only; they are not reconstructed from ANA-07 bundle samples and are not asserted for all 32 configurations.

No force, momentum-transfer or motion post-audit is applicable to these incident-field-only records: they contain no body-coupled field or force output, and the project contracts prohibit inferring such a quantity from the recorder's pressure samples. Introducing one here would require a separately reviewed physical model and scope. This review therefore finds no additional field-only numerical post-audit missing from the defined contract. Formal P3 reviewers still need to decide whether the combined per-case flux comparison and exact-source ANA-06 ledgers meet the gate's model-audit requirement.

No plot was generated for this matrix. Its four global error summaries, exact case counts and the targeted cancellation table above are fully represented as checked numerical tables; a chart would not add a spatial field or trend variable and could visually overstate differences between nearly-zero residuals. Any later visualization must be generated from and checked against the retained machine-readable records.

## Limits

The probe examines one ideal standing-wave node at one frequency and one coordinate precision. The test suite's precision comparisons are not a formal interval proof for every binary64 input, and neither those checks nor this probe bound arbitrary cancellation, platform changes, untested geometries, discretized solvers, physical source error, water-property uncertainty or body coupling. Physical validation remains `NOT_ESTABLISHED`.
