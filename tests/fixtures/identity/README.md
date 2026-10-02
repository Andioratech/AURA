# Canonical identity golden fixture

`canonical.json` contains seven hand-authored JSON trees and exact expected byte strings, plus a valid manufactured SolverSpec with manually ordered canonical text. Expected text was not obtained from the production encoder. The 0.1 expansion follows the exact binary64 value documented by Python; the remaining values use direct literal ordering and exact decimal arithmetic.

The solver's `solver_document_sha256` was independently computed with the system `sha256sum` executable from the fixed text, without importing `aura`:

```python
import json
import subprocess
from pathlib import Path

fixture = json.loads(Path("tests/fixtures/identity/canonical.json").read_text())
preimage = b"AURA-C14N-1\ndocument\n" + fixture["solver_canonical"].encode("ascii")
print(subprocess.run(["sha256sum"], input=preimage, capture_output=True, check=True).stdout.decode())
```

Expected digest: `ca3f7514c34fd66f9c140f92e0e307e5f1ca99cfd0e9122a3e530cb3fd908433`. This is a software reference, not a scientific experiment/run identity. Tests also use the standard empty-byte and `abc` SHA-256 answers for raw files. [Encoding contract](../../../docs/research/content-identity.md); [B-02 report](../../../docs/benchmarks/B02-content-identity.md).
