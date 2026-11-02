"""Fail if a script shadows a common Python standard-library module."""
from pathlib import Path
import sys

SCRIPTS = Path(__file__).resolve().parent
stdlib = set(getattr(sys, "stdlib_module_names", ()))
conflicts = sorted(p.name for p in SCRIPTS.glob("*.py") if p.stem in stdlib)
if conflicts:
    print("FAIL: standard-library module shadowing:", ", ".join(conflicts))
    raise SystemExit(1)
print("PASS: no Python standard-library module names shadowed in scripts/")
