#!/usr/bin/env python3
import sys
import os
import shutil
import subprocess
from env import *
from utils import *

# Check if psql is available
if not shutil.which("psql"):
  error("psql is not available. Please install PostgreSQL client utilities.")
  sys.exit(1)


def pg_env(password=None):
  env = os.environ.copy()
  env["PGPASSWORD"] = password or ADMIN_PASSWORD
  return env


def psql(sql_cmd):
  execute(f'psql -d "{ADMIN_DB}" -h "{DB_HOST}" -p {DB_PORT} -U "{ADMIN_USER}" -c "{sql_cmd}"', env=pg_env())


def drop_db():
  info(f"Dropping database '{DB_NAME}' if exists...")
  psql(f"DROP DATABASE IF EXISTS {DB_NAME}")
  success("Database dropped.")


def init_db():
  drop_db()
  info(f"Creating database '{DB_NAME}'...")
  psql(f"CREATE DATABASE {DB_NAME}")
  success("Database created.")


def grant_permission():
  info(f"Granting database permissions to user '{DB_ADMIN}'...")
  psql(f"GRANT ALL PRIVILEGES ON DATABASE {DB_NAME} TO {DB_ADMIN}")
  psql(f"ALTER DATABASE {DB_NAME} OWNER TO {DB_ADMIN}")
  psql(f"ALTER SCHEMA public OWNER TO {DB_ADMIN}")
  psql(f"ALTER USER {DB_ADMIN} WITH CREATEDB")
  success("Permissions granted.")


def init_admin():
  info(f"Checking user '{DB_ADMIN}'...")
  res = subprocess.run(
    f'psql -d "{ADMIN_DB}" -h "{DB_HOST}" -p {DB_PORT} -U "{ADMIN_USER}" -tAc "SELECT 1 FROM pg_roles WHERE rolname=\'{DB_ADMIN}\'"',
    shell=True, capture_output=True, text=True, env=pg_env()
  )
  if res.stdout.strip() == "1":
    warning(f"USER {DB_ADMIN} ALREADY EXISTS. SKIPPING CREATION.")
  else:
    psql(f"CREATE USER {DB_ADMIN} WITH PASSWORD '{DB_PASSWORD}'")
    success(f"User {DB_ADMIN} created.")
  grant_permission()


def init():
  init_db()
  init_admin()
  if os.path.exists("./data"):
    shutil.rmtree("./data")
  success("Initialization complete.")


def dump():
  os.makedirs(DUMP_DIR, exist_ok=True)
  info(f"Dumping database to {DUMP_FILE}...")
  execute(f'pg_dump -d "{ADMIN_DB}" -U "{DB_ADMIN}" -h "{DB_HOST}" -p {DB_PORT} -F t "{DB_NAME}" > "{DUMP_FILE}"', env=pg_env(DB_PASSWORD))
  success(f"Dump completed: {DUMP_FILE}")


def restore(file_path):
  if not os.path.exists(file_path):
    error(f"Error: File {file_path} does not exist.")
    sys.exit(1)

  env = pg_env(DB_PASSWORD)

  if file_path.endswith(".zip"):
    info(f"Extracting zip archive: {file_path}...")
    shutil.rmtree("./unzip", ignore_errors=True)
    execute(f'unzip -o "{file_path}" -d ./unzip')

    # Find .sql file
    sql_file = None
    for root, _, files in os.walk("./unzip"):
      for f in files:
        if f.endswith(".sql"):
          sql_file = os.path.join(root, f)
          break

    if not sql_file:
      error("Error: No .sql file found in archive.")
      shutil.rmtree("./unzip", ignore_errors=True)
      sys.exit(1)

    execute(f'psql -h "{DB_HOST}" -p {DB_PORT} -U "{DB_ADMIN}" -d "{DB_NAME}" -f "{sql_file}"', env=env)

    if os.path.exists("./unzip/filestore"):
      os.makedirs(f"{ODOO_DATA_DIR}/filestore", exist_ok=True)
      execute(f'cp -r ./unzip/filestore/* "{ODOO_DATA_DIR}/filestore/"')

    shutil.rmtree("./unzip", ignore_errors=True)

  elif file_path.endswith(".tar"):
    info(f"Restoring database from tar archive: {file_path}...")
    execute(f'pg_restore -h "{DB_HOST}" -p {DB_PORT} -U "{DB_ADMIN}" -d "{DB_NAME}" "{file_path}"', env=env)
    os.makedirs(ODOO_DATA_DIR, exist_ok=True)
    execute(f'tar -xvf "{file_path}" -C "{ODOO_DATA_DIR}" filestore/', check=False)

  else:
    error("Error: Unsupported file format. Please provide .tar or .zip file.")
    sys.exit(1)

  success("Restore completed successfully.")


def show_help():
  print("""
Usage: Manipulating database
  python database.py [COMMAND] [OPTION]

Commands:
  dump               Dump database
  restore <file>     Restore database from .tar or .zip
  initial            Initialize Database & Admin User
  init-db            Initialize Database
  init-admin         Initialize Admin User
  grant-permission   Grant DB permissions
  drop-db            Drop Database
""")


def main():
  if len(sys.argv) < 2:
    warning("No command provided. Showing help...")
    show_help()
    sys.exit(1)

  cmd = sys.argv[1]
  if cmd == "dump":
    dump()
  elif cmd == "restore":
    if len(sys.argv) < 3:
      error("Error: Please specify backup file path to restore.")
      sys.exit(1)
    restore(sys.argv[2])
  elif cmd == "initial":
    init()
  elif cmd == "init-db":
    init_db()
  elif cmd == "init-admin":
    init_admin()
  elif cmd == "grant-permission":
    grant_permission()
  elif cmd == "drop-db":
    drop_db()
  elif cmd == "help":
    show_help()
  else:
    show_help()


if __name__ == "__main__":
  main()
