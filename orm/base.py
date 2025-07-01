from orm.database import Database

class BaseModel:
    """
    Base class for Object-Relational Mapping (ORM) models.

    This class defines the core functionality and interface that all ORM subclasses must implement.
    It provides general methods for interacting with the database, such as inserting an object
    (`dump`), updating an existing record (`update`), creating an instance from a database record
    (`from_database`), and creating an instance from a parser object (`from_parser`).

    Subclasses must define the following class attributes:
        - `table_name` (str): Name of the associated database table.
        - `table_columns` (list of str): Valid column names for the table.
        - `table_id` (list of str): Column names that make up the primary key.

    Subclass constraints:
        - All mandatory database columns must match an instance attribute or property,
          accessible via <cls>.<column_name>
        - All extra instance attributes must start with _ or __ to be ignored by ORM methods.

    Available methods:
        - dump(): Insert the object into the database.
        - update(): Update the existing database record using the primary key.
        - from_parser(): Create an ORM instance from a parser object.
    """

    table_name = ''
    table_columns = []
    table_id = []
    database = Database()

    def __init__(self, **kwargs):
        pass

    @property
    def dict_record(self):
        """
        Returns a dictionary representation of the object, excluding private attributes.

        Only attributes whose names do not start with an underscore (_) are included.

        Returns:
            dict: A dictionary mapping column names to their corresponding values.
        """
        return {col: val for col, val in self.__dict__.items() if not col.startswith('_')}

    def dump(self):
        """
        Inserts the current object into the database.

        This method uses the class attribute `table_name` to determine which table to insert the record into.
        It serializes the object's attributes according to `table_columns` and performs the insertion.

        Returns:
            list of str: Values corresponding to the primary key columns (`table_id`) of the inserted object.
        """

        record = self.database.insert_record(
            table=self.table_name,
            columns=list(self.dict_record.keys()),
            values=list(self.dict_record.values()),
        )
        record_id = []
        for col_id in self.table_id:
            record_id.append(record[col_id])
        return record_id

    @classmethod
    def from_database_id(cls, record_id):
        """
        Retrieve a single record from the database using its primary key and return an instance of the class.
        param record_id must be passes as a list matching the class property `table_id`.

        Args:
            record_id (list): A list of values corresponding to the primary key columns defined in `table_id`.

        Returns:
            An instance of the class initialized with the data retrieved from the database.

        Raises:
            ValueError: If the number of elements in `record_id` does not match the number of columns in `table_id`,
                        if the record is not found in the database, or if an error occurs during the query.
        """

        if len(record_id) != len(cls.table_id):
            raise ValueError(f'Record ID ({record_id}) does not match table ID ({cls.table_id}).')

        where_clause = ' AND '.join([f'{col} = %s' for col in cls.table_id])

        try:
            record = cls.database.select_records(
                table=cls.table_name,
                where_clause=where_clause,
                where_values=record_id
            )
        except Exception as e:
            raise ValueError('Failed to fetch record from database. Error: {}'.format(e))

        if record:
            return cls(**record[0])
        else:
            raise ValueError(f'Record ID: {record_id} not found.')

    @classmethod
    def from_parser(cls, parser):
        """
        Creates an instance of the class using data extracted from a parser object.

        This method builds a dictionary by retrieving the values of attributes listed in
        `table_columns` from the given `parser` object. If an attribute is missing in the parser,
        its value defaults to `None`.

        Args:
            parser (object): An object (typically a parser instance) containing attributes
                             that correspond to the table's columns.

        Returns:
            An instance of the class initialized with the parsed data.
        """
        record = {col: getattr(parser, col, None) for col in cls.table_columns}
        return cls(**record)

    def __str__(self):
        """
        String representation of the object.

        Returns:
            str: String representation of the object.
        """
        string = '-'*40 +\
                f'\nItem from table: {self.table_name}\n\t' +\
                 '\n\t'.join([f'{key}: {val}' for key, val in self.dict_record.items()]) + \
                 '\n' + '-' * 40 + '\n'
        return string

    def __repr__(self):
        """
        String representation of the object.

        Returns:
               str: String representation of the object.
                """
        return str(self)