<h1 style="text-align: center;"> ODOO SERVER RUNTIME </h1>

### Features

- Start Odoo server with a single Python command
- Rich terminal UI visuals (colors, status icons `✔`, `ℹ`, `⚠`, `✖`, environment banners, animated loading spinners)
- Zero external dependencies (built on Python 3 standard library)
- Support multiple databases and virtual environments
- Legacy shell scripts safely backed up in `legacy_sh/`

### Structure

Recommended project structure
```
project/
├──modules/
└──runtime/
```

Each folder in `runtime` corresponds to an Odoo database runtime environment.

```
runtime/
├── dev/
│   ├── requirements.txt  # Packages
│   ├── config.py         # Central configuration (DB, paths, Odoo options)
│   ├── utils.py          # Terminal visual loggers, spinners & process helpers
│   ├── database.py       # Database management CLI script
│   ├── odoo.py           # Odoo server runtime CLI script
│   ├── odoo.conf         # Odoo server configuration INI file
│   ├── database.sh       # Forwarder wrapper -> database.py
│   ├── odoo.sh           # Forwarder wrapper -> odoo.py
│   └── legacy_sh/        # Backup of original shell scripts (.sh)
├── prod/
└── test/
```

### Getting started

#### 1. Create a Postgres database and superuser

```shell
python database.py initial
```

#### 2. Prepare Odoo configuration & virtualenv

- Create odoo.conf: `python odoo.py config --create` (default: `odoo.conf`)
- Create Virtual environment: `python odoo.py venv --create` (default: `venv`)
- Install required python packages: `python odoo.py venv --install`

#### 3. Run Odoo Server

- Start for the first time: `python odoo.py run --install`
- Update target modules: `python odoo.py run --update`
- Update with watchdog dev mode: `python odoo.py run --update --watch`
- For more commands and options: `python odoo.py --help`