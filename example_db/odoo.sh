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

function create_venv() {
  if [ -d "$ODOO_VENV" ]; then
    echo "VIRTUAL ENVIRONMENT ALREADY EXISTS"
  else
    echo "NO VIRTUAL ENVIRONMENT FOUND. CREATING ONE..."
    "$PYTHON_CMD" -m venv "$ODOO_VENV" || {
      echo "FAILED TO CREATE VIRTUAL ENVIRONMENT"
      return 1
    }
    if [ -f "$WORKSPACE_DIR/requirements.txt" ]; then
      echo "INSTALLING DEPENDENCIES..."
      pip install -r "$WORKSPACE_DIR/requirements.txt" || {
        echo "FAILED TO INSTALL DEPENDENCIES"
        return 1
      }
    else
      echo "requirements.txt NOT FOUND AT $WORKSPACE_DIR"
    fi
  fi
}

function show_helps() { 
  echo """
Usage: Run Odoo server with prepaired configs
  ./odoo.sh [COMMAND] [OPTION]

NOTE: Custom modules are defined in ./env.sh

OPTIONS:
  target modules are definded in env.sh
  --watch:      trigger watchdog, reload target modules on changes.
  --install:    install target modules
  --update:     update target modules
  --update-all: update all modules

Run install modules 
  ./odoo.sh run --install [--watch]

Run update modules
  ./odoo.sh run --update [--watch]

Run update all target modules (defined in env.sh)
  ./odoo.sh run --update-all [--watch]

Run init fresh module
  ./odoo.sh scaffold <module-name>

Run create venv
  ./odoo.sh create-venv

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
elif [ "$COMMAND" = "create-venv" ] ; then
  create_venv
elif [ "$COMMAND" = "help" ] ; then
  show_helps
else
  show_helps
fi