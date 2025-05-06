#!/bin/bash

source ./env.sh
source "$WORKSPACE_DIR/runtime/utils.sh"

echo """
===================================================
WORKSPACE DIR : $WORKSPACE_DIR
ODOO DIR      : $ODOO_DIR
CONFIG FILE   : $CONFIG_FILE
PYTHON VENV   : $ODOO_VENV
===================================================
"""

function run() {
  local DEV="none"  # Default dev mode
  if has_opt "--watch" "$@"; then
    DEV="all"
  fi
  if has_opt "--install" "$@"; then
    exec $ODOO_DIR/odoo-bin \
      -c $CONFIG_FILE \
      -d $DB_NAME \
      -i base,$INIT_MODULES \
      --dev=$DEV
  elif has_opt "--update" "$@"; then
    exec $ODOO_DIR/odoo-bin \
      -c $CONFIG_FILE \
      -d $DB_NAME \
      -u $INIT_MODULES \
      --dev=$DEV
  elif has_opt "--update-all" "$@"; then
    exec $ODOO_DIR/odoo-bin \
      -c $CONFIG_FILE \
      -d $DB_NAME \
      --update=all \
      --dev=$DEV
  else 
    echo """
    Command Error
    Showing help...
    """
    show_help
    exit 1
  fi
}

function scaffold() {
  MODULE_NAME="$@"
  exec $ODOO_DIR/odoo-bin scaffold $MODULE_NAME $WORKSPACE_DIR
}

function debug() {
  python -Xfrozen_modules=off -m debugpy --listen 0.0.0.0:5678 \
    $ODOO_DIR/odoo-bin \
    --dev=reload \
    -c $CONFIG_FILE \
    -d $DB_NAME \
    -u $INIT_MODULES \
    --dev=all
}

function active_venv() {
  find_python() {
    for py in python3.12 python3.11 python3.10 python3.9 python3.8 python3.7 python3 python; do
      if command -v "$py" >/dev/null 2>&1; then
        echo "$py"
        return 0
      fi
    done
    echo "NO PYTHON INTERPRETER FOUND" >&2
    echo "AVAILABLE PYTHON VERSIONS: [$(command -v python*)]"
    return 1
  }
  PYTHON_CMD=$(find_python) || return 1

  activate() {
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
      source "$ODOO_VENV/Scripts/activate"
    else
      source "$ODOO_VENV/bin/activate"
    fi
  }

  if [ -d "$ODOO_VENV" ]; then
    activate
  else
    echo "NO VIRTUAL ENVIRONMENT FOUND. CREATING ONE..."
    "$PYTHON_CMD" -m venv "$ODOO_VENV" || {
      echo "FAILED TO CREATE VIRTUAL ENVIRONMENT"
      return 1
    }
    activate
    if [ -f "$WORKSPACE_DIR/requirements.txt" ]; then
      echo "INSTALLING DEPENDENCIES..."
      pip install -r "$WORKSPACE_DIR/requirements.txt" || {
        echo "FAILED TO INSTALL DEPENDENCIES"
        return 1
      }
    else
      echo "requirements.txt NOT FOUND AT $WORKSPACE_DIR"
    fi
    
    echo "VIRTUAL ENVIRONMENT ACTIVATED"
  fi

  echo "USING PYTHON: $(which python)"
}

function show_helps() { 
  echo """
Usage: Run Odoo server with prepaired configs
  ./odoo.sh [COMMAND] [OPTION]

NOTE: Custom modules are defined in ./env.sh

OPTIONS:
  target modules are definded in env.sh
  --watch: trigger watchdog, reload target modules on changes.
  --install: install target modules
  --update: update target modules
  --update-all: update all modules

TEST OPTIONS:
  --file <path>: Run tests in a specific file (path relative to addons).
      e.g., --file my_module/tests/test_models.py
  --tags <tags>: Run tests matching specific tags (comma-separated).
      e.g., --tags my_tag,-skipped_tag,:TestClass.method

Run install modules 
  ./odoo.sh run --install [--watch]

Run update modules
  ./odoo.sh run --update [--watch]

Run update modules
  ./odoo.sh run --update-all [--watch]

Run init fresh module
  ./odoo.sh scaffold <module-name>

Run active venv
  ./odoo.sh activate-venv

Remote Debug
  ./odoo.sh debug
  """
}

COMMAND=$1;
if [ -n "$COMMAND" ]; then
  shift
else
  echo "No command provided. Showing helps..."
  show_helps
  exit 1
fi

if [ "$COMMAND" = "run" ] ; then
  run $@
elif [ "$COMMAND" = "debug" ] ; then
  debug
elif [ "$COMMAND" = "scaffold" ] ; then
  scaffold $@
elif [ "$COMMAND" = "activate-venv" ] ; then
  active_venv
elif [ "$COMMAND" = "help" ] ; then
  show_helps
else
  show_helps
fi