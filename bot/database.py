import os
import threading
import time
from enum import Enum

import mysql.connector


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
        self.db = None
        self._lock = threading.Lock()
        self._and = " AND "
        self.connect()
        self.start_keep_alive()

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
                self.init_db()
                print("[INFO] Connected to the database.")
                break
            except mysql.connector.Error as err:
                print(f"[ERROR] Error: {err}")
                print(f"[ERROR] Retrying in {self.retry_interval} seconds...")
                time.sleep(self.retry_interval)

    def reconnect_if_needed(self):
        """Reconnect if the database connection is not available."""
        if self.db is None or not self.db.is_connected():
            print("[ERROR] Lost connection to the database. Reconnecting...")
            self.connect()

    def start_keep_alive(self):
        """Periodically ping the database to keep the connection alive."""
        def keep_alive():
            while True:
                time.sleep(self.keep_alive_interval)
                try:
                    with self._lock:
                        if self.db is None or not self.db.is_connected():
                            self.connect()
                        else:
                            cursor = self.db.cursor()
                            cursor.execute("SELECT 1")
                            cursor.fetchall()
                            cursor.close()
                except mysql.connector.Error as err:
                    print(f"[ERROR] Keep-alive error: {err}")
                    self.connect()

        threading.Thread(target=keep_alive, daemon=True).start()

    def close(self):
        if self.db and self.db.is_connected():
            self.db.close()

    # ── Schema Init ────────────────────────────────────────────────────────────

    def init_db(self):
        """Create tables if they don't exist."""
        statements = [
            f"CREATE TABLE IF NOT EXISTS `{TableName.GUILDS.value}` ("
            "`guild_id` BIGINT NOT NULL,"
            "PRIMARY KEY (`guild_id`)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;",

            f"CREATE TABLE IF NOT EXISTS `{TableName.ADMINS.value}` ("
            "`discord_id` BIGINT NOT NULL,"
            "PRIMARY KEY (`discord_id`)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;",

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
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;",

            f"CREATE TABLE IF NOT EXISTS `{TableName.CHANNELS.value}` ("
            "`channel_id` BIGINT NOT NULL,"
            "`guild_id` BIGINT NOT NULL,"
            "PRIMARY KEY (`channel_id`),"
            f"FOREIGN KEY (`guild_id`) REFERENCES `{TableName.GUILDS.value}` (`guild_id`)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;",

            f"CREATE TABLE IF NOT EXISTS `{TableName.AUTOROLES.value}` ("
            "`role_id` BIGINT NOT NULL,"
            "`guild_id` BIGINT NOT NULL,"
            "`threshold` SMALLINT NOT NULL,"
            "PRIMARY KEY (`role_id`, `threshold`),"
            f"FOREIGN KEY (`guild_id`) REFERENCES `{TableName.GUILDS.value}` (`guild_id`)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;",
        ]
        with self._lock:
            cursor = self.db.cursor()
            try:
                for stmt in statements:
                    cursor.execute(stmt)
                self.db.commit()
            finally:
                cursor.close()

    # ── CRUD Operations ────────────────────────────────────────────────────────
    # Each method creates its own cursor and closes it when done.
    # The lock prevents concurrent access from the keep-alive thread.

    def insert(self, table: str, data: dict):
        """
        Insert data into the specified table.

        Args:
            table (str): The name of the table.
            data (dict): The data to insert.
        """
        self.reconnect_if_needed()
        keys = ", ".join(data.keys())
        values = ", ".join(["%s"] * len(data))
        query = f"INSERT INTO `{table}` ({keys}) VALUES ({values})"
        print(f"[DEBUG] {query}", tuple(data.values()))
        with self._lock:
            cursor = self.db.cursor(dictionary=True)
            try:
                cursor.execute(query, tuple(data.values()))
                self.db.commit()
            finally:
                cursor.close()  # ✅ always close

    def select(
        self,
        table: str,
        columns: list = None,
        where: dict = None,
        limit: int = None,
        order_by: str = None,
    ):
        """
        Select data from the specified table.

        Args:
            table (str): The name of the table.
            columns (list, optional): Columns to select. Defaults to all.
            where (dict, optional): WHERE clause as column-value pairs.
            limit (int, optional): Max rows to return.
            order_by (str, optional): Column to order by.

        Returns:
            list[dict]: The selected rows.
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
        with self._lock:
            cursor = self.db.cursor(dictionary=True)
            try:
                cursor.execute(query, tuple(where.values()) if where else None)
                return cursor.fetchall()  # ✅ always fetch
            finally:
                cursor.close()            # ✅ always close

    def update(self, table: str, data: dict, where: dict):
        """
        Update records in the specified table.

        Args:
            table (str): The name of the table.
            data (dict): Column-value pairs to update.
            where (dict): WHERE clause as column-value pairs.
        """
        self.reconnect_if_needed()
        set_clause = ", ".join([f"{key} = %s" for key in data.keys()])
        where_clause = self._and.join([f"{key} = %s" for key in where.keys()])
        values = tuple(data.values()) + tuple(where.values())
        query = f"UPDATE `{table}` SET {set_clause} WHERE {where_clause}"
        print(f"[DEBUG] {query}", values)
        with self._lock:
            cursor = self.db.cursor(dictionary=True)
            try:
                cursor.execute(query, values)
                self.db.commit()
            finally:
                cursor.close()  # ✅ always close

    def delete(self, table: str, where: dict):
        """
        Delete records from the specified table.

        Args:
            table (str): The name of the table.
            where (dict): WHERE clause as column-value pairs.
        """
        self.reconnect_if_needed()
        where_clause = self._and.join([f"{key} = %s" for key in where.keys()])
        query = f"DELETE FROM `{table}` WHERE {where_clause}"
        print(f"[DEBUG] {query}", tuple(where.values()))
        with self._lock:
            cursor = self.db.cursor(dictionary=True)
            try:
                cursor.execute(query, tuple(where.values()))
                self.db.commit()
            finally:
                cursor.close()  # ✅ always close


db = ThanksDB(retry_interval=10, keep_alive_interval=60)