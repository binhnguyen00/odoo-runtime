source "./env.sh"
source "$WORKSPACE_DIR/runtime/utils.sh"

# Check if psql is available
if ! command -v psql > /dev/null 2>&1; then
  echo "psql is not available. Please install PostgreSQL client utilities."
  exit 1
fi

function init() {
  init_db
  init_admin
  rm -rf ./data
}

function init_db() {
  drop_db
  PGPASSWORD=$ADMIN_PASSWORD psql -d $ADMIN_DB -h $DB_HOST -p $DB_PORT -U $ADMIN_USER -c "CREATE DATABASE $DB_NAME"
}

function init_admin() {
  ADMIN_EXISTS=$(PGPASSWORD=$ADMIN_PASSWORD psql -d $ADMIN_DB -h $DB_HOST -p $DB_PORT -U $ADMIN_USER -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_ADMIN'")
  if [ "$ADMIN_EXISTS" == "1" ]; then
    echo "USER $DB_ADMIN ALREADY EXISTS. SKIPPING CREATION."
  else
    PGPASSWORD=$ADMIN_PASSWORD psql -d $ADMIN_DB -h $DB_HOST -p $DB_PORT -U $ADMIN_USER -c "CREATE USER $DB_ADMIN WITH PASSWORD '$DB_PASSWORD';"
  fi
  grant_permission
}

function grant_permission() {
  PGPASSWORD=$ADMIN_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $ADMIN_USER -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_ADMIN"
  PGPASSWORD=$ADMIN_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $ADMIN_USER -c "ALTER DATABASE $DB_NAME OWNER TO $DB_ADMIN"
  PGPASSWORD=$ADMIN_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $ADMIN_USER -c "ALTER SCHEMA public OWNER TO $DB_ADMIN"
  PGPASSWORD=$ADMIN_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $ADMIN_USER -c "ALTER USER $DB_ADMIN WITH CREATEDB;"
}

function dump() {
  mkdir -p "$DUMP_DIR"
  PGPASSWORD=$DB_PASSWORD pg_dump -U "$DB_ADMIN" -h "$DB_HOST" -p "$DB_PORT" -F t "$DB_NAME" > "$DUMP_FILE"
}

function drop_db() {
  PGPASSWORD=$ADMIN_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $ADMIN_USER -c "DROP DATABASE IF EXISTS $DB_NAME"
}

function restore() {
  FILE="$@"
  # Check if file exists
  if [ ! -f "$FILE" ]; then
    echo "Error: File $FILE does not exist."
    exit 1
  fi

  # Support .tar and .zip
  if [[ "$FILE" == *.zip ]]; then
    # Unzip the file
    unzip -o "$FILE" -d ./unzip || { echo "Failed to extract $FILE"; exit 1; }

    # Find and restore the SQL file
    SQL_FILE=$(find ./unzip -type f -name "*.sql")
    if [ -z "$SQL_FILE" ]; then
      echo "Error: No .sql file found in the archive."
      rm -rf ./unzip
      exit 1
    fi

    # Restore the database
    PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_ADMIN -d $DB_NAME -f "$SQL_FILE" || {
      echo "Database restore failed."
      rm -rf ./unzip
      exit 1
    }

    # Restore filestore if it exists in the zip
    if [ -d "./unzip/filestore" ]; then
      mkdir -p "$DATA_DIR/filestore"
      cp -r ./unzip/filestore/* "$DATA_DIR/filestore/"
    fi

    # Clean up
    rm -rf ./unzip

  elif [[ "$FILE" == *.tar ]]; then
    # Restore the database from the tar file
    PGPASSWORD=$DB_PASSWORD pg_restore -h $DB_HOST -p $DB_PORT -U $DB_ADMIN -d $DB_NAME "$FILE" || {
      echo "Database restore failed."
      exit 1
    }

    # Restore filestore if it exists in the tar
    if tar -tf "$FILE" | grep -q "filestore/"; then
      mkdir -p "$DATA_DIR/filestore"
      tar -xvf "$FILE" -C "$DATA_DIR" filestore/
    fi

  else
    echo "Error: Unsupported file format. Please provide .tar/.zip file."
    exit 1
  fi

  echo "Restore completed successfully."
}

function show_help() {
  echo """
Usage: Manipulating database 
  ./database.sh [COMMAND] [OPTION]

NOTE: You should change the value in ./common/database-env.sh

Dump
  ./database.sh dump

Drop
  ./database.sh drop-db
  ./database.sh drop-user

Restore
  ./database.sh restore [path-to-file]
  IMPORTAIN:
    Before restoration process, run ./database.sh initial to create a clean database.
    If your file is .zip, run server then do the restoration
    Else just restore normally

Initial (Database & Admin)
  ./database.sh initial

  Initial Database
    ./database.sh init-db

  Initial Admin User
    ./database.sh init-admin
  
  """
}

COMMAND=$1;
if [ -n "$COMMAND" ]; then
  shift
else
  echo "No command provided. Showing help..."
  show_help
  exit 1
fi

if [ "$COMMAND" = "dump" ] ; then
  dump
elif [ "$COMMAND" = "restore" ] ; then
  restore $@
elif [ "$COMMAND" = "initial" ] ; then
  init
elif [ "$COMMAND" = "init-db" ] ; then
  init_db
elif [ "$COMMAND" = "init-admin" ] ; then
  init_admin
elif [ "$COMMAND" = "drop-db" ] ; then
  drop_db
elif [ "$COMMAND" = "grant-permission" ] ; then
  grant_permission
elif [ "$COMMAND" = "help" ] ; then
  show_help
else
  show_help
fi