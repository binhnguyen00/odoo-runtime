#!/usr/bin/env bash

windowsOS=false
if [ "$OSTYPE" = "msys" ] ; then
  windowsOS=true;
elif [[ "$OSTYPE" == "cygwin" ]]; then
  windowsOS=true;
elif [[ "$OSTYPE" == "win32" ]]; then
  windowsOS=true;
fi

function has_opt() {
  OPT_NAME=$1
  shift
  for i in "$@"; do
    if [[ $i == $OPT_NAME ]] ; then
      return 0  # true in bash
    fi
  done
  return 1  # false in bash
}

function get_opt() {
  OPT_NAME=$1
  DEFAULT_VALUE=$2
  shift

  for i in "$@"; do
    index=$(($index+1))
    if [[ $i == $OPT_NAME* ]] ; then
      value="${i#*=}"
      echo "$value"
      return
    fi
  done
  echo $DEFAULT_VALUE
}

function find_python() {
  for py in python3.12 python3.11 python3.10 python3.9 python3.8 python3.7 python3 python; do
    if command -v "$py" >/dev/null 2>&1; then
      echo "$py"
      return 0
    fi
  done
  echo "ERROR: No suitable Python interpreter found" >&2
  return 1
}

export PYTHON_CMD=$(find_python)
