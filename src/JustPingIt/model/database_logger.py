
import sqlite3
from datetime import datetime
from typing import Optional
from .ping import Ping


class DatabaseLogger:
    """
    A class to handle logging of ping results into a SQLite database.
    Attributes:
        db_path (str): The file path to the SQLite database.
    Methods:
        __init__(db_path: str):
            Initializes the DatabaseLogger and creates the necessary table if it doesn't exist.
        log(ping: Ping):
            Logs a ping result into the database.
        fetch_logs(ip_filter: str = "", result_filter: str = "", from_date: datetime = None, to_date: datetime = None) -> list:
            Fetches logs from the database with optional filters for IP address, result, and date range.
        delete_logs_by_ids(ids: list):
            Deletes logs from the database by their IDs.
    """
    def __init__(self, db_path: str) -> None:
        """
        Initialize the instance with the specified database path and create the necessary database table.

        Args:
            db_path (str): The file path to the database.
        """
        self.db_path = db_path
        self._create_table()

    def _create_connection(self) -> sqlite3.Connection:
        """
        Establishes a connection to the SQLite database.

        Returns:
            sqlite3.Connection: A connection object to interact with the SQLite database.
        """
        return sqlite3.connect(self.db_path)

    def _create_table(self) -> None:
        """
        Creates the 'ping_logs' table in the database if it does not already exist.

        The table includes the following columns:
            - id: An auto-incrementing integer serving as the primary key.
            - result: A text field to store the result of the ping operation.
            - timestamp: A text field to store the timestamp of the ping operation.
            - ip_address: A text field to store the IP address that was pinged.

        This method establishes a connection to the database, executes the SQL
        command to create the table, and then closes the connection. If an error
        occurs during the process, it prints an error message.

        Raises:
            Exception: If there is an issue creating the database table.
        """
        try:
            conn = self._create_connection()
            with conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS ping_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        result TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        ip_address TEXT NOT NULL
                    )
                """)
            conn.close()
        except Exception as e:
            print(f"Error creating database table: {e}")

    def log(self, ping: Ping) -> None:
        """
        Logs the details of a ping operation to the database.

        Args:
            ping (Ping): An instance of the Ping class containing the result, 
                         timestamp, and IP address of the ping operation.

        Raises:
            Exception: If an error occurs while logging to the database, 
                       it prints an error message with the exception details.
        """
        try:
            conn = self._create_connection()
            with conn:
                conn.execute("""
                    INSERT INTO ping_logs (result, timestamp, ip_address)
                    VALUES (?, ?, ?)
                """, (ping.result, ping.timestamp, ping.ip_address))
            conn.close()
        except Exception as e:
            print(f"Error logging to database: {e}")
    def fetch_logs(self, ip_filter: str ="", result_filter: str="", from_date: Optional[datetime]=None, to_date: Optional[datetime]=None) -> list:
        """
        Fetch logs from the ping_logs database table with optional filtering.
        Args:
            ip_filter (str, optional): A substring to filter logs by IP address. 
                                       Supports partial matches using SQL LIKE.
            result_filter (str, optional): A specific result value to filter logs by.
            from_date (datetime, optional): The start date for filtering logs. 
                                            Only logs with a timestamp on or after this date will be included.
            to_date (datetime, optional): The end date for filtering logs. 
                                          Only logs with a timestamp on or before this date will be included.
        Returns:
            list: A list of tuples, where each tuple contains the following fields:
                  - id (int): The unique identifier of the log entry.
                  - result (str): The result of the ping operation.
                  - timestamp (str): The timestamp of the log entry.
                  - ip_address (str): The IP address associated with the log entry.
        Notes:
            - Logs are returned in descending order of their timestamp.
            - If an error occurs during database access, an empty list is returned, and the error is printed to the console.
        """
        try:
            conn = self._create_connection()
            query = "SELECT id, result, timestamp, ip_address FROM ping_logs WHERE 1=1"
            params = []

            if ip_filter:
                query += " AND ip_address LIKE ?"
                params.append(f"%{ip_filter}%")
            if result_filter:
                query += " AND result = ?"
                params.append(result_filter)
            if from_date:
                query += " AND timestamp >= ?"
                params.append(from_date.strftime("%Y-%m-%d 00:00:00"))
            if to_date:
                query += " AND timestamp <= ?"
                params.append(to_date.strftime("%Y-%m-%d 23:59:59"))

            query += " ORDER BY timestamp DESC"

            cur = conn.cursor()
            cur.execute(query, params)
            rows = cur.fetchall()
            conn.close()
            return rows
        except Exception as e:
            print(f"Error fetching logs: {e}")
            return []

    def delete_logs_by_ids(self, ids: list) -> None:
        """
        Deletes log entries from the 'ping_logs' table in the database based on the provided list of IDs.

        Args:
            ids (list): A list of integers representing the IDs of the log entries to be deleted.

        Raises:
            Exception: If an error occurs during the deletion process, it will be caught and printed.
        """
        try:
            conn = self._create_connection()
            with conn:
                conn.executemany("DELETE FROM ping_logs WHERE id = ?", [(i,) for i in ids])
            conn.close()
        except Exception as e:
            print(f"Error deleting logs: {e}")