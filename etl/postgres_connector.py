
import os
import json
import logging
import psycopg2
from datetime import datetime, timedelta

logger = logging.getLogger('postgres')
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)


class PostgresConnector:
    def __init__(self, db_url):
        self.db_url = db_url
        self.connector = None
        self.cursor = None
        
    def start(self):
        """ Create and save a database connector and cursor """
        self.connector = psycopg2.connect(self.db_url)
        self.cursor = self.connector.cursor()
        return self.cursor
    
    def stop(self):
        """ Close the connection and clear """
        self.connector.commit()
        self.cursor.close()
        self.connector.close()
        self.connector = None
        self.cursor = None
        
    def commit(self):
        self.connector.commit()
        
    def count_table(self, table_name):
        """ Count the rows in a table """
        selectStatement = f'SELECT * FROM "{table_name}"'
        self.cursor.execute(selectStatement)
        return len(self.cursor.fetchall())
    
    def clear_table(self, table_name, id_col):
        """ Clear all rows in a table without deleting the table itself."""
        before_len = self.count_table(table_name)
        deleteStatement = f'DELETE FROM "{table_name}" WHERE {id_col} >= 0;'
        self.cursor.execute(deleteStatement)
        logger.info(f"Count of rows in table={table_name} from {before_len} to {self.count_table(table_name)}")
    
    def reset_max_id(self, table_name, id_col):
        """ Reset the maximum id counter after an insert to prevent integrity violations."""
        set_max_id = f'SELECT setval(\'{table_name}_{id_col}_seq\', (SELECT MAX({id_col}) FROM "{table_name}")+1)';
        self.cursor.execute(set_max_id)
    

def clear_db(out_db_url):
    """
    Delete rows from a table without deleting the table
    """
    pg = PostgresConnector(db_url = out_db_url)
    pg.start()
    # Iterate over the tables
    for table_cfg in table_data[::-1]:
        table_name = table_cfg['name']
        id_col = table_cfg['id_col']
        before_len = pg.count_table(table_name)
        pg.clear_table(table_name, id_col)
    pg.stop()