import psycopg2
from psycopg2 import sql
import os
import config

class Database:
    """
    Singleton class that handles database connections and
    database functionality.
    """
    _instance = None

    def __new__(cls):
        """
        Returns the singleton instance. If it doesn't exist, it creates the
        non-initialized singleton instance.
        """
        if not cls._instance:
            cls._instance = object.__new__(cls)
            cls._instance.__initialized = False
            return cls._instance
        else:
            return cls._instance

    def __init__(self):
        """
        Initializes the singleton instance if not already initialized.
        """
        self._connection = psycopg2.connect(
            dbname=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            host=config.DB_HOST,
            port=config.DB_PORT
        )
        self._initialized = True

    @property
    def connection(self):
        """
        Returns the connection to the database.
        :return: psycopg2 connection
        """
        return self._connection

    def commit(self):
        """
        Commits the current transaction to the database.
        :return: None
        """
        self.connection.commit()

    def rollback(self):
        """
        Rollback the current transaction to the database.
        :return: None
        """
        self.connection.rollback()

    def insert_record(self, table, columns, values, autocommit=False):
        """
        Inserts a record into the specified table using the given columns and values.

        This method constructs a parameterized SQL INSERT statement and executes it
        using the current database connection. Columns starting with an underscore ('_')
        are excluded from the insert operation.

        Args:
           table (str): The name of the table where the record will be inserted.
           columns (list of str): A list of column names for the insert.
           values (list): A list of values corresponding to each column.
           autocommit (bool, optional): If True, commits the transaction after the insert.
                                      Defaults to False.

        Returns:
           inserted_record (dict): Dictionary containing the inserted record, or an empty dictionary if
                                   insertion fails.

        Raises:
            Exception: Propagates any database-related exceptions if not handled internally.
        """

        record = {col: value for col, value in zip(columns, values) if not col.startswith('_')}
        n_columns = len(record)

        sql_statement = sql.SQL("INSERT INTO {table} ({fields}) VALUES ({values}) RETURNING *;").format(
            table=sql.Identifier(table),
            fields=sql.SQL(',').join(map(sql.Identifier, record.keys())),
            values=sql.SQL(',').join(sql.Placeholder() * n_columns)
        )

        inserted_record = {}
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(sql_statement, list(record.values()))
                record_values = cursor.fetchone()
                record_columns = [desc[0] for desc in cursor.description]
                inserted_record = dict(zip(record_columns, record_values))
            if autocommit:
                self.commit()
        except Exception as e:
            self.rollback()
            print(f'[ERROR] insert_record failed: {e}')

        return inserted_record

    def select_records(self, table, columns='*', where_clause=None, where_values=None):
        """
        Selects records from the specified table with optional WHERE conditions.

        Constructs a parameterized SQL SELECT query using the given table and columns.
        If a WHERE clause is provided, it is safely formatted with placeholders and values.

        Args:
            table (str): The name of the table to select from.
            columns (list of str or str): Columns to select. Defaults to '*' for all columns.
            where_clause (str, optional): A WHERE clause with placeholders (e.g., "age > %s AND active = %s").
            where_values (list, optional): A list of values to fill in the placeholders in the WHERE clause.

        Returns:
            list[tuple]: A list of rows (tuples) returned by the query.

        Raises:
            Exception: Propagates database-related exceptions if the query fails.
        """
        if isinstance(columns, list):
            columns_sql = sql.SQL(', ').join(map(sql.Identifier, columns))
        else:
            columns_sql = sql.SQL(columns)

        query = sql.SQL("SELECT {fields} FROM {table}").format(
            fields=columns_sql,
            table=sql.Identifier(table)
        )

        if where_clause:
            query += sql.SQL(" WHERE ") + sql.SQL(where_clause)

        with self.connection.cursor() as cursor:
            cursor.execute(query, where_values if where_values else [])
            records_columns = [desc[0] for desc in cursor.description]
            records_values = cursor.fetchall()
            records = [dict(zip(records_columns, values)) for values in records_values]
            return records


    def update_record(self, table, columns, values, where_clause, where_values, autocommit=False):
        """
        Updates records in the specified table using the provided column-value pairs and WHERE conditions.

        This method constructs a parameterized SQL UPDATE statement and executes it safely.
        It requires a WHERE clause to avoid accidental updates of all rows.

        Args:
            table (str): The name of the table to update.
            columns (list of str): List of column names to update.
            values (list): List of values corresponding to the columns.
            where_clause (str): The WHERE clause with placeholders (e.g., "id = %s").
            where_values (list): Values to bind to the WHERE clause placeholders.
            autocommit (bool, optional): If True, commits the transaction after the update. Defaults to False.

        Returns:
            int: The number of rows affected by the update.

        Raises:
            ValueError: If columns and values lists have different lengths.
            Exception: Propagates any database-related exceptions if not handled internally.
        """
        if len(columns) != len(values):
            raise ValueError("The number of columns must match the number of values.")

        set_clause = sql.SQL(', ').join(
            sql.Composed([sql.Identifier(col), sql.SQL(' = '), sql.Placeholder()])
            for col in columns
        )

        query = sql.SQL("UPDATE {table} SET {set_clause} WHERE {where}").format(
            table=sql.Identifier(table),
            set_clause=set_clause,
            where=sql.SQL(where_clause)
        )

        with self.connection.cursor() as cursor:
            cursor.execute(query, values + where_values)
            affected_rows = cursor.rowcount

        if autocommit:
            self.commit()

        return affected_rows