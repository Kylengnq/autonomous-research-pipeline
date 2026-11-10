"""Stamp the registry against the shipped script and leave it alone."""
import os
import subprocess
import sys

registry = f"{os.environ['SKILLS_ROOT']}/script-registry/scripts/registry.py"
subprocess.run([sys.executable, registry, "stamp", "--registry",
                "script_registry.json"], check=True)
