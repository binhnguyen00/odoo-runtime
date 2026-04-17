# Odoo server runtime
- Start odoo server with a single command
- Support multiple database and virtual environment

# Quickstart

### 1. Configuration

Copy the [example_db](./example_db) to your own database folder

```bash
cp -r ./example_db ./your_db
cd ./your_db
```

Configure your database in [env.sh](./env.sh)

Configure odoo config file in [odoo.conf](./example_db/odoo.conf)

### 2. Create virtual environment

```bash
# create virtual environment
./odoo.sh venv --create

# install dependencies
./odoo.sh venv --install
```

### 3. Create postgresql database

```bash
./database.sh initial
```

more details are in [database.sh](./database.sh)

### 4. Run odoo server

```bash
# with specific modules pre installed (defined in env.sh)
./odoo.sh run --install [--watch]

# with specific modules pre updated (defined in env.sh)
./odoo.sh run --update [--watch]

# update all modules
./odoo.sh run --update-all [--watch]
```

Note:
- `--watch` is optional. It triggers `watchdog` to reload target modules on changes.
