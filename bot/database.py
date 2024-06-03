import os
import mysql.connector

from enum import Enum

class TableName(Enum):
    GUILDS="guilds"
    ADMINS="bot_administrator"
    POINTS="points"

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
            "PRIMARY KEY (`discord_id`)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;"
        )

    def close(self):
        self.cursor.close()
        self.db.close()

    def insert(self, table:str, data:dict):
        """
        @param table: str - table name
        @param data: dict - data to insert
        """
        keys = ', '.join(data.keys())
        values = ', '.join(['%s'] * len(data))
        self.cursor.execute(f"INSERT INTO `{table}` ({keys}) VALUES ({values})", tuple(data.values()))
        print(f"INSERT INTO `{table}` ({keys}) VALUES ({values})", tuple(data.values()))
        self.db.commit()

    def select(self, table:str, columns:list=None, where:dict=None):
        """
        @param table: str - table name
        @param columns: list - columns to select
        @param where: dict - where clause
        @return: tuple - selected data
        """
        if columns is None:
            columns = ['*']
        if where is None:
            self.cursor.execute(f"SELECT {', '.join(columns)} FROM `{table}`")
            return self.cursor.fetchall()
        where_query = ' AND '.join([f"{key} = %s" for key in where.keys()])
        self.cursor.execute(f"SELECT {', '.join(columns)} FROM `{table}` WHERE {where_query}", tuple(where.values()))
        return self.cursor.fetchall()
        
    def update(self, table:str, data:dict, where:str, where_data:tuple):
        """
        @param table: str - table name
        @param data: dict - data to update
        @param where: str - where clause
        @param where_data: tuple - where data
        """
        set = ', '.join([f"{key} = %s" for key in data.keys()])
        self.cursor.execute(f"UPDATE `{table}` SET {set} WHERE {where}", tuple(list(data.values()) + list(where_data)))
        print(f"UPDATE `{table}` SET {set} WHERE {where}", tuple(list(data.values()) + list(where_data)))
        self.db.commit()

    def delete(self, table:str, where:str, where_data:tuple):
        """
        @param table: str - table name
        @param where: str - where clause
        @param where_data: tuple - where data
        """
        self.cursor.execute(f"DELETE FROM `{table}` WHERE {where}", where_data)
        print(f"DELETE FROM `{table}` WHERE {where}", where_data)
        self.db.commit()


db = ThanksDB()