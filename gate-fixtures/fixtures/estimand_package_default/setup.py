"""Run the derivation and the package call, exactly as S6 would."""
import subprocess
import sys

subprocess.run([sys.executable, "derive.py"], check=True)
subprocess.run([sys.executable, "package_call.py"], check=True)
