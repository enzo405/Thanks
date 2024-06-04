import os
import mysql.connector

from enum import Enum

class TableName(Enum):
    GUILDS="guilds"
    ADMINS="bot_administrator"
    POINTS="points"
    CHANNELS="channels"

class ThanksDB:
    def start(self):
        self.db = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT")),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_DATABASE")
        )
        self.cursor = self.db.cursor(dictionary=True)
        self.init_db()

    def init_db(self):
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS `{TableName.GUILDS.value}` ("
            "`guild_id` BIGINT NOT NULL,"
            "PRIMARY KEY (`guild_id`)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;"
        )

        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS `{TableName.ADMINS.value}` ("
            "`discord_id` BIGINT NOT NULL,"
            "PRIMARY KEY (`discord_id`)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;"
        )
        
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS `{TableName.POINTS.value}` ("
            "`discord_user_id` BIGINT NOT NULL,"
            "`counter` BIGINT DEFAULT 0,"
            "PRIMARY KEY (`discord_user_id`)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;"
        )
        
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS `{TableName.CHANNELS.value}` ("
            "`channel_id` BIGINT NOT NULL,"
            "`guild_id` BIGINT NOT NULL,"
            "PRIMARY KEY (`channel_id`),"
            f"FOREIGN KEY (`guild_id`) REFERENCES `{TableName.GUILDS.value}` (`guild_id`)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;"
        )

    def close(self):
        self.cursor.close()
        self.db.close()

    def insert(self, table:str, data:dict):
        """
        Insert data into the specified table.

        Args:
            table (str): The name of the table.
            data (dict): The data to insert.

        Returns:
            None
        """
        keys = ', '.join(data.keys())
        values = ', '.join(['%s'] * len(data))
        print(f"INSERT INTO `{table}` ({keys}) VALUES ({values})", tuple(data.values()))
        self.cursor.execute(f"INSERT INTO `{table}` ({keys}) VALUES ({values})", tuple(data.values()))
        self.db.commit()

    def select(self, table:str, columns:list=None, where:dict=None):
        """
        Selects data from a table in the database.

        Args:
            table (str): The name of the table.
            columns (list, optional): The columns to select. Defaults to None, which selects all columns.
            where (dict, optional): The where clause as a dictionary of column-value pairs. Defaults to None.

        Returns:
            tuple: The selected data as a tuple.
        """
        if columns is None:
            columns = ['*']
        if where is None:
            self.cursor.execute(f"SELECT {', '.join(columns)} FROM `{table}`")
            return self.cursor.fetchall()
        where_query = ' AND '.join([f"{key} = %s" for key in where.keys()])
        self.cursor.execute(f"SELECT {', '.join(columns)} FROM `{table}` WHERE {where_query}", tuple(where.values()))
        return self.cursor.fetchall()
        
    def update(self, table:str, data:dict):
        """
        Update records in the specified table based on the given conditions.

        Args:
            table (str): The name of the table to update.
            data (dict): A dictionary containing the column names as keys and the new values as values.

        Returns:
            None
        """
        set = ', '.join([f"{key} = %s" for key in data.keys()])
        print(f"UPDATE `{table}` SET {set}", tuple(data.values()))
        self.cursor.execute(f"UPDATE `{table}` SET {set}", tuple(data.values()))
        self.db.commit()

    def delete(self, table:str, where:dict):
        """
        Deletes records from the specified table based on the given WHERE clause.

        Args:
            table (str): The name of the table to delete records from.
            where (dict): A dictionary containing the column names as keys and the values as the conditions for deletion.

        Returns:
            None
        """
        where_clause = ' AND '.join([f"{key} = %s" for key in where.keys()])
        print(f"DELETE FROM `{table}` WHERE {where_clause}", tuple(where.values()))
        self.cursor.execute(f"DELETE FROM `{table}` WHERE {where_clause}", tuple(where.values()))
        self.db.commit()


db = ThanksDB()