"""Make the script newer than the results it is supposed to have produced."""
import os
import time

now = time.time()
os.utime("results.json", (now - 600, now - 600))
os.utime("scripts/estimate.py", (now, now))
