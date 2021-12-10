from pathlib import Path

Path("/Users/gabriel.pereira/Documents/mle/repos/daggr/tests/core/scripts/log").touch()
with open(
    "/Users/gabriel.pereira/Documents/mle/repos/daggr/tests/core/scripts/log", "a"
) as f:
    f.write("step1\n")
