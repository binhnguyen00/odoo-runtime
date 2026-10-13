import os
from datetime import datetime

"""
Recommended Project Structure:
  project/
  ├──modules/     # your custom modules
  └──runtime/
"""

PROJECT_ROOT          = "path/to/your/project"
PROJECT_MODULES_DIR   = os.path.join(PROJECT_ROOT, "modules")  # your custom modules path
RUNTIME_DIR           = os.path.join(PROJECT_ROOT, "runtime")  # runtime path
RUNTIME_PROFILE_DIR   = os.path.dirname(os.path.abspath(__file__))

ADMIN_DB              = "postgres"
ADMIN_USER            = "postgres"
ADMIN_PASSWORD        = "admin"

DB_NAME               = "example"
DB_ADMIN              = "example"
DB_PASSWORD           = "example@123"
DB_HOST               = "localhost"
DB_PORT               = "5432"

DUMP_DIR              = os.path.join(RUNTIME_PROFILE_DIR, "db")
DUMP_FILE             = os.path.join(DUMP_DIR, f"{DB_NAME}_{datetime.now().strftime('%Y%m%d%H%M%S')}.tar")

ODOO_DIR              = "/path/to/odoo/source/code"
ODOO_INIT_MODULES     = "accounting,hr"  # modules to install/ update on server start
ODOO_CONFIG_FILE      = os.path.join(RUNTIME_PROFILE_DIR, "odoo.conf")
ODOO_VENV             = os.path.join(RUNTIME_PROFILE_DIR, "venv")
ODOO_DATA_DIR         = os.path.join(RUNTIME_PROFILE_DIR, "data")
