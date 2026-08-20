import os
from datetime import datetime

"""
Recommended Project Structure:
  project/
  ├──modules/     # your custom modules
  └──runtime/
"""

PROJECT_ROOT          = os.path.abspath(os.path.join(__file__, "../.."))  # path/to/your/project
PROJECT_MODULES_DIR   = os.path.join(PROJECT_ROOT, "modules")             # your custom modules path
RUNTIME_DIR           = os.path.join(PROJECT_ROOT, "runtime")             # runtime path

ADMIN_DB              = "postgres"
ADMIN_USER            = "postgres"
ADMIN_PASSWORD        = "admin"

DB_NAME               = "example"
DB_ADMIN              = "example"
DB_PASSWORD           = "example@123"
DB_HOST               = "localhost"
DB_PORT               = "5432"

DUMP_DIR              = "./db"
DUMP_FILE             = f"{DUMP_DIR}/{DB_NAME}_{datetime.now().strftime('%Y%m%d%H%M%S')}.tar"

ODOO_DIR              = os.path.join(PROJECT_ROOT, "odoo")  # odoo source code path
ODOO_CONFIG_FILE      = "./odoo.conf"                       # odoo config file path
ODOO_INIT_MODULES     = "accounting,hr"                     # your modules name
ODOO_VENV             = "./venv"                            # odoo venv path
ODOO_DATA_DIR         = "./data"                            # odoo data path