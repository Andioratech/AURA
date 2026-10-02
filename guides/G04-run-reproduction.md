# G04: Reproducing a Run

**Status:** DRAFT

Select the immutable run ID. Verify input, source and data checksums. Recreate the recorded environment and backend, replay its exact configuration and seed, then compare declared metrics using the stored tolerances. Record hardware/backend differences and nondeterminism. If the run cannot be reconstructed, mark it unreproducible and do not cite it as accepted evidence.
