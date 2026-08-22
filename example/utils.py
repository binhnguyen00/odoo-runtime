import sys
import shutil
import subprocess
import logging

# Terminal Colors
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
RESET = "\033[0m"

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("%(message)s"))

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)
_logger.addHandler(handler)
_logger.propagate = False

def info(msg):
  _logger.info(f"{CYAN}ℹ {msg}{RESET}")

def success(msg):
  _logger.info(f"{GREEN}✔ {msg}{RESET}")

def warning(msg):
  _logger.warning(f"{YELLOW}⚠ {msg}{RESET}")

def error(msg):
  _logger.error(f"{RED}✖ {msg}{RESET}")

def execute(cmd, env=None, check=True, quiet=False):
  """Run a shell command."""
  kwargs = {}
  if quiet:
    kwargs["stdout"] = subprocess.DEVNULL
    kwargs["stderr"] = subprocess.DEVNULL
  if isinstance(cmd, str):
    return subprocess.run(cmd, shell=True, env=env, check=check, **kwargs)
  return subprocess.run(cmd, env=env, check=check, **kwargs)

def find_python():
  """Find available python executable."""
  for py in ["python3", "python"]:
    if shutil.which(py):
      return py
  error("No suitable Python interpreter found.")
  sys.exit(1)