from app.core.issues import Issue, DefaultSource
from abc import ABC, abstractmethod
from typing import Optional, Any, Dict, List
import sqlite3, json


class Database(ABC):
    """
    Abstract class for database connections
    """
    @abstractmethod
    def get_all(self, table_name: str) -> List[Dict]:
        pass

    @abstractmethod
    def add_row(self, table_name: str, row: Dict) -> None:
        pass

    @abstractmethod
    def add_all(self, table_name: str, rows: List[Dict]) -> None:
        pass

    @abstractmethod
    def find(self, table_name: str, query: Dict) -> List[Dict]:
        pass

    @abstractmethod
    def close(self):
        pass





class DocumentDatabase(Database):
    """
    Database class for storing documents in a SQLite database in a NoSQL-like way
    """

    # A list of allowed tables. Tables with such names will be created if they don't exist in the DB.
    TABLES: Dict[str, str] = {
      "issues": "issues",
      "rules": "rules",
    }

    def __init__(self, f: str):
        """
        Create a new database connection
        :param f: path to the database file
        """
        self._db = sqlite3.connect(f)
        for table_name in self.TABLES.keys():
            self._db.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (data TEXT);")

    def _check_table(self, table_name: str) -> None:
        """
        Check if table exists, otherwise raise a KeyError
        :param table_name: name of the table
        :return: True if table exists, False otherwise
        """
        if table_name not in self.TABLES:
            raise KeyError(f"Table {table_name} not found")

    def _execute(self, query) -> Any:
        """
        Execute a query
        :param query: SQL query
        return: result of the query
        """
        return self._db.execute(query)

    def add_row(self, table_name: str, row: Dict) -> None:
        """
        Add a row to a table
        :param table_name: name of the table
        :param row: dictionary representing the row
        """
        self._check_table(table_name)
        self._db.execute(f"INSERT INTO {table_name} VALUES (?);", (json.dumps(row),))

    def add_all(self, table_name: str, rows: List[Dict]) -> None:
        """
        Add multiple rows to a table
        :param table_name: name of the table
        :param rows: list of dictionaries representing the rows
        """
        self._check_table(table_name)
        for row in rows:
            self.add_row(table_name, row)

    def get_all(self, table_name: str) -> List[Dict]:
        """
        Get all rows from a table
        :param table_name: name of the table
        :return: list of dictionaries representing the rows in the table
        """
        self._check_table(table_name)
        results = []
        for r in self._db.execute(f"SELECT * FROM {table_name}"):
            results.append(json.loads(r[0]))
        return results

    def find(self, table_name: str, query: Dict) -> List[Dict]:
        """
        Find rows in a table that match a query
        Limitations: only supports exact matches (check dict elements for equality)
        :param table: name of the table
        :param query: dictionary of key-value pairs to match
        :return: list of dictionaries representing the rows that match the query (empty if none match)
        """
        results = []
        for k, v in query.items():
            if isinstance(v, str):
                query[k] = f"'{v}'"
            # FIXME injection
            q = ' AND '.join(f" json_extract(data, '$.{k}') = {v}" for k, v in query.items())
            for r in self._db.execute(f"SELECT * FROM {table_name} WHERE {q}"):
                # we need generators here? do yield then instead of adding to the list
                # yield r[0]
                results.append(json.loads(r[0]))
        return results
    
    def close(self):
        """
        Close the database connection
        """
        try:
            # check if connection is still open
            self._execute("SELECT 1")
            self._db.close()
        except sqlite3.ProgrammingError:
            pass  # connection is already closed

    def __del__(self):
        """
        Destructor closing the database connection if needed.
        """
        self.close()
    #
    # def get_issue_by_id(self, issue_id: str):
    #     return self.find(self.TABLES["issues"], {"issue_id": issue_id})


class MockDatabase(Database):
    def __init__(self):
        self._db = {"issues": self.prepare_mock_issues()}

    def get_all(self, table_name: str) -> List[Dict]:
        raise NotImplementedError()

    def add_row(self, table_name: str, row: Dict) -> None:
        raise NotImplementedError()

    def add_all(self, table_name: str, rows: List[Dict]) -> None:
        raise NotImplementedError()

    def find(self, table_name: str, query: Dict) -> List[Dict]:
        raise NotImplementedError()

    def close(self):
        raise NotImplementedError()

    @staticmethod
    def prepare_mock_issues() -> List[Dict]:
        issues: list[dict] = []

        gl_source = DefaultSource(
                issue_id="1",
                issue_name="hello world",
                created_at="2024-04-27T10:15:30.123456+0530",
                updated_at="2024-04-27T10:15:30.123456+0530",
                description="default issue old",
                )

        jr_source = DefaultSource(
                issue_id="2",
                issue_name="hello world",
                created_at="2024-04-28T10:15:30.123456+0530",
                updated_at="2024-04-28T10:15:30.123456+0530",
                description="default issue new",
                )

        gl_issue = Issue(gl_source)
        jr_issue = Issue(jr_source)

        print(gl_issue.asdict())

        issues.append(gl_issue.asdict())
        issues.append(jr_issue.asdict())

        return issues
