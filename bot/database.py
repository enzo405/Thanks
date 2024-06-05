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
        print("Connecting to the database...")
        self.db = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT")),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_DATABASE")
        )
        self.cursor = self.db.cursor(dictionary=True)
        self.init_db()
        print("Connected to the database.")

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
            "`guild_id` BIGINT NOT NULL,"
            "`discord_user_id` BIGINT NOT NULL,"
            "`points` BIGINT DEFAULT 0,"
            "`last_thanks` TIMESTAMP DEFAULT CURRENT_TIMESTAMP," 
            "`num_of_thanks` BIGINT DEFAULT 0,"
            "PRIMARY KEY (`guild_id`, `discord_user_id`),"
            f"FOREIGN KEY (`guild_id`) REFERENCES `{TableName.GUILDS.value}` (`guild_id`)"
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

    def select(self, table:str, columns:list=None, where:dict=None, limit:int=None, order_by:str=None):
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
        if columns is None:
            columns = ['*']
        query = f"SELECT {', '.join(columns)} FROM `{table}`"
        if where:
            where_query = ' AND '.join([f"{key} = %s" for key in where.keys()])
            query += f" WHERE {where_query}"
        if limit:
            query += f" LIMIT {limit}"
        if order_by:
            query += f" ORDER BY {order_by}"
        print(query, tuple(where.values()) if where else None)
        self.cursor.execute(query, tuple(where.values()) if where else None)
        return self.cursor.fetchall()
        
    def update(self, table:str, data:dict, where:dict):
        """
        Update records in the specified table based on the given conditions.

        Args:
            table (str): The name of the table to update.
            data (dict): A dictionary containing the column names as keys and the new values as values.
            where (dict): A dictionary containing the column names as keys and the conditions as values.

        Returns:
            None
        """
        set_clause = ', '.join([f"{key} = %s" for key in data.keys()])
        where_clause = ' AND '.join([f"{key} = %s" for key in where.keys()])
        values = tuple(data.values()) + tuple(where.values())
        print(f"UPDATE `{table}` SET {set_clause} WHERE {where_clause}", values)
        self.cursor.execute(f"UPDATE `{table}` SET {set_clause} WHERE {where_clause}", values)
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