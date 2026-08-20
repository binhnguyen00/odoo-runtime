<h1 style="text-align: center;"> ODOO SERVER RUNTIME </h1>

## Features

- Start Odoo server with a single Python command
- Support multiple databases and virtual environments

## Structure

Recommended project structure
```plaintext
project/
├──modules/
└──runtime/
```

Each folder in `runtime` corresponds to an Odoo database runtime environment.

```plaintext
runtime/
├── dev/
│   ├── requirements.txt  # Packages
│   ├── utils.py          # Terminal visual loggers, spinners & process helpers
│   ├── database.py       # Database management CLI script
│   ├── odoo.py           # Odoo server runtime CLI script
├── prod/
└── test/
```

## Getting started

##### 1. Create a Postgres database and superuser

```bash
python database.py initial
```

##### 2. Prepare Odoo configuration & virtualenv

- Create odoo.conf: `python odoo.py config --create` (default: `odoo.conf`)
- Create Virtual environment: `python odoo.py venv --create` (default: `venv`)
- Install required python packages: `python odoo.py venv --install`

##### 3. Run Odoo Server

- Start for the first time: `python odoo.py run --install`
- Update target modules: `python odoo.py run --update`
- Update with watchdog dev mode: `python odoo.py run --update --watch`
- For more commands and options: `python odoo.py --help`