bin=`cd "$bin"; pwd`
CURRENT_DIR=`cd $bin; pwd`

ADMIN_DB="postgres"
ADMIN_USER="postgres"
ADMIN_PASSWORD="admin"

DB_NAME="dev"
DB_ADMIN="dev"
DB_PASSWORD="dev@123" 
DB_HOST="localhost"
DB_PORT="5432"

WORKSPACE_DIR="/Users/jackjack/projects/mobi_social_listening"
ODOO_DIR="/Users/jackjack/projects/odoo-17.0"
CONFIG_FILE="$WORKSPACE_DIR/runtime/$DB_NAME/odoo.conf"

DATE=$(date +%Y%m%d%H%M%S)
DUMP_DIR="$WORKSPACE_DIR/runtime/$DB_NAME/db"
DUMP_FILE="$DUMP_DIR/${DB_NAME}_${DATE}.tar"

INIT_MODULES="mobi_crewai,os_telegram,facebook"
ODOO_VENV="$WORKSPACE_DIR/runtime/$DB_NAME/.venv"

DATA_DIR="$WORKSPACE_DIR/runtime/$DB_NAME/data"