"""Stamp the registry against the shipped script, then plant the edit."""
import os
import subprocess
import sys
from pathlib import Path

skills = os.environ["SKILLS_ROOT"]
registry = f"{skills}/script-registry/scripts/registry.py"
subprocess.run([sys.executable, registry, "stamp", "--registry",
                "script_registry.json"], check=True)
Path("scripts/estimate.py").write_text(Path("edited.py.txt").read_text())
