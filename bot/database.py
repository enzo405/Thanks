import os
import mysql.connector
import time

from enum import Enum


class TableName(Enum):
    GUILDS = "guilds"
    ADMINS = "bot_administrator"
    POINTS = "points"
    CHANNELS = "channels"
    AUTOROLES = "autoroles"
    CACHE_DAILY = "cache_daily"


class ThanksDB:
    def __init__(self, retry_interval=5, keep_alive_interval=60):
        self.retry_interval = retry_interval
        self.keep_alive_interval = keep_alive_interval
        self.start_keep_alive()
        self._and = " AND "

    def connect(self):
        while True:
            try:
                print("[INFO] Connecting to the database...")
                self.db = mysql.connector.connect(
                    host=os.getenv("DB_HOST", "localhost"),
                    port=int(os.getenv("DB_PORT", 3306)),
                    user=os.getenv("DB_USER"),
                    password=os.getenv("DB_PASSWORD"),
                    database=os.getenv("DB_DATABASE"),
                )
                self.cursor = self.db.cursor(dictionary=True)
                self.init_db()
                print("[INFO] Connected to the database.")
                break
            except mysql.connector.Error as err:
                print(f"[ERROR] Error: {err}")
                print(f"[ERROR] Retrying in {self.retry_interval} seconds...")
                time.sleep(self.retry_interval)

    def start_keep_alive(self):
        """Periodically run a simple query to keep the connection alive."""
        import threading

        def keep_alive():
            while True:
                try:
                    if self.db.is_connected():
                        self.cursor.execute("SELECT 1")
                    else:
                        self.connect()
                except mysql.connector.Error as err:
                    print(f"[ERROR] Keep-alive error: {err}")
                    self.connect()
                time.sleep(self.keep_alive_interval)

        threading.Thread(target=keep_alive, daemon=True).start()

    def reconnect_if_needed(self):
        """Reconnect if the database connection is not available."""
        if not self.db.is_connected():
            print("[ERROR] Lost connection to the database. Reconnecting...")
            self.connect()

    def init_db(self):
        self.cursor.execute(
            f"CREATE TABLE IF NOT EXISTS `{TableName.GUILDS.value}` ("
            "`guild_id` BIGINT NOT NULL,"
            "PRIMARY KEY (`guild_id`)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;"
        )

        self.cursor.execute(
            f"CREATE TABLE IF NOT EXISTS `{TableName.ADMINS.value}` ("
            "`discord_id` BIGINT NOT NULL,"
            "PRIMARY KEY (`discord_id`)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;"
        )

        self.cursor.execute(
            f"CREATE TABLE IF NOT EXISTS `{TableName.POINTS.value}` ("
            "`guild_id` BIGINT NOT NULL,"
            "`discord_user_id` BIGINT NOT NULL,"
            "`points` INT DEFAULT 0,"
            "`last_thanks` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
            "`num_of_thanks` INT DEFAULT 0,"
            "`last_received_points_date` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
            "`current_day_received_points` TINYINT DEFAULT 0,"
            "PRIMARY KEY (`guild_id`, `discord_user_id`),"
            f"FOREIGN KEY (`guild_id`) REFERENCES `{TableName.GUILDS.value}` (`guild_id`)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;"
        )

        self.cursor.execute(
            f"CREATE TABLE IF NOT EXISTS `{TableName.CHANNELS.value}` ("
            "`channel_id` BIGINT NOT NULL,"
            "`guild_id` BIGINT NOT NULL,"
            "PRIMARY KEY (`channel_id`),"
            f"FOREIGN KEY (`guild_id`) REFERENCES `{TableName.GUILDS.value}` (`guild_id`)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;"
        )

        self.cursor.execute(
            f"CREATE TABLE IF NOT EXISTS `{TableName.AUTOROLES.value}` ("
            "`role_id` BIGINT NOT NULL,"
            "`guild_id` BIGINT NOT NULL,"
            "`threshold` SMALLINT NOT NULL,"
            "PRIMARY KEY (`role_id`, `threshold`),"
            f"FOREIGN KEY (`guild_id`) REFERENCES `{TableName.GUILDS.value}` (`guild_id`)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;"
        )

    def close(self):
        self.cursor.close()
        self.db.close()

    def insert(self, table: str, data: dict):
        """
        Insert data into the specified table.

        Args:
            table (str): The name of the table.
            data (dict): The data to insert.

        Returns:
            None
        """
        self.reconnect_if_needed()
        keys = ", ".join(data.keys())
        values = ", ".join(["%s"] * len(data))
        print(f"[DEBUG] INSERT INTO `{table}` ({keys}) VALUES ({values})", tuple(data.values()))
        self.cursor.execute(
            f"INSERT INTO `{table}` ({keys}) VALUES ({values})", tuple(data.values())
        )
        self.db.commit()

    def select(
        self,
        table: str,
        columns: list = None,
        where: dict = None,
        limit: int = None,
        order_by: str = None,
    ):
        """
        Selects data from a table in the database.

        Args:
            table (str): The name of the table.
            columns (list, optional): The columns to select. Defaults to None, which selects all columns.
            where (dict, optional): The where clause as a dictionary of column-value pairs. Defaults to None.
            limit (int, optional): The maximum number of rows to return. Defaults to None.
            order_by (str, optional): The column to order the results by. Defaults to None.

        Returns:
            tuple: The selected data as a tuple.
        """
        self.reconnect_if_needed()
        if columns is None:
            columns = ["*"]
        query = f"SELECT {', '.join(columns)} FROM `{table}`"
        if where:
            where_query = self._and.join([f"{key} = %s" for key in where.keys()])
            query += f" WHERE {where_query}"
        if order_by:
            query += f" ORDER BY {order_by}"
        if limit:
            query += f" LIMIT {limit}"
        print("[DEBUG]", query, tuple(where.values()) if where else None)
        self.cursor.execute(query, tuple(where.values()) if where else None)
        return self.cursor.fetchall()

    def update(self, table: str, data: dict, where: dict):
        """
        Update records in the specified table based on the given conditions.

        Args:
            table (str): The name of the table to update.
            data (dict): A dictionary containing the column names as keys and the new values as values.
            where (dict): A dictionary containing the column names as keys and the conditions as values.

        Returns:
            None
        """
        self.reconnect_if_needed()
        set_clause = ", ".join([f"{key} = %s" for key in data.keys()])
        where_clause = self._and.join([f"{key} = %s" for key in where.keys()])
        values = tuple(data.values()) + tuple(where.values())
        print(f"[DEBUG] UPDATE `{table}` SET {set_clause} WHERE {where_clause}", values)
        self.cursor.execute(
            f"UPDATE `{table}` SET {set_clause} WHERE {where_clause}", values
        )
        self.db.commit()

    def delete(self, table: str, where: dict):
        """
        Deletes records from the specified table based on the given WHERE clause.

        Args:
            table (str): The name of the table to delete records from.
            where (dict): A dictionary containing the column names as keys and the values as the conditions for deletion.

        Returns:
            None
        """
        self.reconnect_if_needed()
        where_clause = self._and.join([f"{key} = %s" for key in where.keys()])
        print(f"[DEBUG] DELETE FROM `{table}` WHERE {where_clause}", tuple(where.values()))
        self.cursor.execute(
            f"DELETE FROM `{table}` WHERE {where_clause}", tuple(where.values())
        )
        self.db.commit()


db = ThanksDB(
    retry_interval=10, keep_alive_interval=60
)  # Retry connection every 10 seconds, keep-alive every 60 seconds
