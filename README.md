<h1 style="text-align: center;"> ODOO SERVER RUNTIME </h1>

### Features

- Start odoo server with a single command
- Support multiple database and virtual environment

### Structure

Each folder in `runtime` is a odoo database itself.

```
runtime/
├── dev/
│   ├── env.sh           # env variables for the shell scripts
│   ├── odoo.conf        # configs to start odoo server
│   ├── odoo.sh          # odoo run script
│   ├── database.sh      # database management script
│   └── utils.sh
├── prod/
└── test/
```

### Getting started

#### 1. Create a postgres database and superuser

```shell
./database.sh initial
```

#### 2. Prepare odoo

- env variables
  - edit `env.sh`
  - edit `odoo.conf`

- virtual env
  - create: `./odoo.sh venv create` which create a python virtual env in `venv/`
  - install: `./odoo.sh venv install` which install required python packages for odoo server from `requirements.txt`

#### 3. Run Odoo

- start for the first time `./odoo.sh run --install`
- update the modules `./odoo.sh run --update`
- there are more, check `./odoo.sh run --help`