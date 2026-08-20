#!/usr/bin/env python3
from env import PROJECT_MODULES_DIR
from env import PROJECT_ROOT
import sys
import os
import subprocess
from env import *
from utils import *


def get_python():
  is_windows = sys.platform.startswith("win")
  bin_dir = "Scripts" if is_windows else "bin"
  exe = f"python.exe" if is_windows else "python"
  return os.path.join(ODOO_VENV, bin_dir, exe)


def get_pip():
  is_windows = sys.platform.startswith("win")
  bin_dir = "Scripts" if is_windows else "bin"
  exe = f"pip.exe" if is_windows else "pip"
  return os.path.join(ODOO_VENV, bin_dir, exe)


print(f"""
===================================================
PROJECT ROOT  : {PROJECT_ROOT}
MODULES_DIR   : {PROJECT_MODULES_DIR}
ODOO DIR      : {ODOO_DIR}
CONFIG FILE   : {ODOO_CONFIG_FILE}
PYTHON VENV   : {ODOO_VENV}
PYTHON        : {get_python()}
PIP           : {get_pip()}
===================================================
""")


def create_odoo_config(output_path=None):
  if "--create" not in sys.argv:
    warning("Not creating config file. Use --create to create one.")
    return

  target_file = output_path or "odoo.conf"
  dir_name = os.path.dirname(os.path.abspath(target_file))
  if dir_name:
    os.makedirs(dir_name, exist_ok=True)

  config_content = f"""
[options]
db_host = {DB_HOST}
db_port = {DB_PORT}
db_user = {DB_ADMIN}
db_password = {DB_PASSWORD}
db_name = {DB_NAME}
addons_path =
  {ODOO_DIR}/addons,
  {PROJECT_MODULES_DIR}
admin_passwd = {ADMIN_PASSWORD}
data_dir = {ODOO_DATA_DIR}
dev_mode = True
"""

  with open(target_file, "w") as f:
    f.write(config_content)

  success(f"Configuration file created at: {target_file}")


def activate_venv():
  if not os.path.exists(ODOO_VENV):
    error("VIRTUAL ENVIRONMENT NOT FOUND. MUST CREATE ONE FIRST")
    sys.exit(1)


def run_server():
  activate_venv()
  venv_py = get_python()
  dev = "all" if "--watch" in sys.argv else "none"
  test_args = " --test-enable --stop-after-init" if "--test" in sys.argv else ""

  if "--install" in sys.argv:
    cmd = f'{venv_py} {ODOO_DIR}/odoo-bin -c {ODOO_CONFIG_FILE} -d {DB_NAME} -i base,{ODOO_INIT_MODULES} --dev={dev}{test_args}'
  elif "--update" in sys.argv:
    cmd = f'{venv_py} {ODOO_DIR}/odoo-bin -c {ODOO_CONFIG_FILE} -d {DB_NAME} -u {ODOO_INIT_MODULES} --dev={dev}{test_args}'
  elif "--update-all" in sys.argv:
    cmd = f'{venv_py} {ODOO_DIR}/odoo-bin -c {ODOO_CONFIG_FILE} -d {DB_NAME} --update=all --dev={dev}{test_args}'
  else:
    error("Command Error. Please provide --install, --update, or --update-all")
    show_help()
    sys.exit(1)

  info(f"Running command: {cmd}")
  execute(cmd)


def test():
  activate_venv()
  venv_py = get_python()
  module = sys.argv[2] if len(sys.argv) > 2 else ""
  test_tags = ""

  if module:
    test_tags = f" --test-tags={module if module.startswith('/') else '/' + module}"

  cmd = f'{venv_py} {ODOO_DIR}/odoo-bin -c {ODOO_CONFIG_FILE} -d {DB_NAME} -u {ODOO_INIT_MODULES} --test-enable{test_tags} --stop-after-init'
  info(f"Running tests for module: {module or 'all'}")
  execute(cmd)


def scaffold():
  activate_venv()
  venv_py = get_python()
  module_name = " ".join(sys.argv[2:])

  if not module_name:
    error("Please specify a module name to scaffold.")
    sys.exit(1)

  cmd = f'{venv_py} {ODOO_DIR}/odoo-bin scaffold {module_name} {PROJECT_MODULES_DIR}'
  info(f"Scaffolding module {module_name}...")
  execute(cmd)


def odoo_shell():
  activate_venv()
  venv_py = get_python()
  extra_args = " ".join(sys.argv[2:])
  cmd = f'{venv_py} {ODOO_DIR}/odoo-bin shell -c {ODOO_CONFIG_FILE} -d {DB_NAME} {extra_args}'
  info("Launching Odoo shell...")
  execute(cmd)


def uninstall():
  activate_venv()
  if len(sys.argv) < 3:
    error("Please provide modules to uninstall, e.g. python odoo.py uninstall account,hr")
    sys.exit(1)
  modules = sys.argv[2]
  venv_py = get_python()
  info(f"Uninstalling modules: {modules}...")
  python_script = f"""
modules = '{modules}'.split(',')
for m in env['ir.module.module'].search([('name', 'in', modules)]):
  m.button_immediate_uninstall()
env.cr.commit()
"""
  p = subprocess.Popen(
    f'{venv_py} {ODOO_DIR}/odoo-bin shell -c {ODOO_CONFIG_FILE} -d {DB_NAME}',
    shell=True, stdin=subprocess.PIPE, text=True
  )
  p.communicate(input=python_script)


def debug():
  activate_venv()
  venv_py = get_python()
  cmd = f'{venv_py} -Xfrozen_modules=off -m debugpy --listen 0.0.0.0:5678 {ODOO_DIR}/odoo-bin -c {ODOO_CONFIG_FILE} -d {DB_NAME} -u {ODOO_INIT_MODULES} --dev=all'
  info("Starting debug mode on 0.0.0.0:5678...")
  execute(cmd)


def venv_cmd():
  py_cmd = find_python()
  if "--create" in sys.argv:
    if os.path.exists(ODOO_VENV):
      warning("VIRTUAL ENVIRONMENT ALREADY EXISTS")
    else:
      info("Creating virtual environment...")
      os.makedirs(os.path.dirname(ODOO_VENV), exist_ok=True)
      execute(f'{py_cmd} -m venv "{ODOO_VENV}"')
      success("Virtual environment created.")
  elif "--install" in sys.argv:
    activate_venv()
    pip_bin = get_pip()
    info("Upgrading pip & setuptools...")
    execute(f'"{pip_bin}" install --upgrade pip setuptools wheel')

    requirements = f"{RUNTIME_DIR}/{DB_NAME}/requirements.txt"
    if os.path.exists(requirements):
      info("Installing workspace requirements...")
      execute(f'"{pip_bin}" install -r "{requirements}"')
    else:
      warning(f"requirements.txt not found in {RUNTIME_DIR}/{DB_NAME}")

    odoo_requirements = f"{ODOO_DIR}/requirements.txt"
    if os.path.exists(odoo_requirements):
      info("Installing Odoo requirements...")
      execute(f'"{pip_bin}" install -r "{odoo_requirements}"')
    else:
      warning(f"requirements.txt not found in {ODOO_DIR}")
    success("Venv installation complete.")


def show_help():
  print("""
Usage: Run Odoo server with prepared configs
  python odoo.py [COMMAND] [OPTION]

Commands:
  run --install | --update | --update-all [--watch] [--test]  # start odoo server via odoo-bin
  debug                                                       # start odoo server with debug mode
  test <module-name>                                          # run tests and stop after complete
  scaffold <module-name>                                      # scaffold a new odoo module
  shell                                                       # start odoo shell
  uninstall <module-1,module-2>                               # uninstall modules
  venv --create | --install                                   # create or install virtual environment
  config --create                                             # create odoo.conf
""")


def main():
  if len(sys.argv) < 2:
    show_help()
    sys.exit(1)

  cmd = sys.argv[1]
  if cmd == "run":
    run_server()
  elif cmd == "test":
    test()
  elif cmd == "scaffold":
    scaffold()
  elif cmd == "shell":
    odoo_shell()
  elif cmd == "uninstall":
    uninstall()
  elif cmd == "debug":
    debug()
  elif cmd == "venv":
    venv_cmd()
  elif cmd == "config":
    create_odoo_config("odoo.conf")
  elif cmd == "help":
    show_help()
  else:
    show_help()

if __name__ == "__main__":
  main()
