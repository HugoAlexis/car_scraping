import os
import psycopg2


def database_exists(conn, dbname):
    """
    Uses a database_config connection to Postgresql to determine if the database_config
    {dbname} already exists.

    args:
        conn: psycopg2 connection
    returns:
        exists: Boolean
    """

    with conn.cursor() as cursor:
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (dbname,))
        already_exists = len(cursor.fetchall()) > 0
        return already_exists


def create_database(conn, dbname, verbose=True):
    """
    Create a database_config {dbname} using the psycopg2 connection {conn}.

    args:
        conn: psycopg2 connection
        dbname: database_config name
    """
    with conn.cursor() as cursor:
        cursor.execute(F"CREATE DATABASE {dbname}")
        if verbose:
            print('Database created')


def apply_schema(conn, schema_path):
    if not os.path.exists(schema_path):
        raise FileNotFoundError(f'Schema {schema_path} does not exist')
    SQL_SCHEMA = open(schema_path).read()
    with conn.cursor() as cursor:
        cursor.execute(SQL_SCHEMA)
        print('Schema applied')


def initialize_database(dbname, user, password, host, port):
    """
    Initializes a PostgreSQL database_config with the given parameters.

    - Connects to the default 'postgres' database_config to check if a database_config named `dbname` exists.
    - If the database_config does not exist, it creates it.
    - After creating the database_config, it connects to the new database_config and executes
      the SQL schema found in 'database_config/schema.sql' to set up tables and other objects.

    Args:
        dbname (str): Name of the database_config to create and initialize.
        user (str): PostgreSQL username.
        password (str): Password for the PostgreSQL user.
        host (str): Host address of the PostgreSQL server.
        port (str or int): Port number of the PostgreSQL server.

    Prints:
        - 'Database initialized' if the database_config was created.
        - 'Database schema initialized' if the schema was applied after creation.

    Notes:
        - Requires the file 'database_config/schema.sql' to be present with valid SQL schema.
        - Assumes the user has permissions to create new databases.
        - Uses autocommit mode to run CREATE DATABASE and schema commands.
    """
    _apply_schema = False

    # Create database_config if not exists
    postgres_conn = psycopg2.connect(
        dbname='postgres',
        user=user,
        password=password,
        host=host,
        port=port,
    )
    postgres_conn.autocommit = True

    if not database_exists(postgres_conn, dbname):
        create_database(postgres_conn, dbname)
        _apply_schema = True
    postgres_conn.close()

    # Apply schema database_config/schema.sql if database didn't exist
    if _apply_schema:
        db_conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port,
        )
        db_conn.autocommit = True
        apply_schema(db_conn, 'database_config/schema.sql')
