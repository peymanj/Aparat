import sqlite3
from sqlite3 import Error
import traceback


class databaseController():
    def __init__(self, db_path):
        self.db_path = db_path
        pass


    def create_connection(self, db_file):
        """ create connection to sqlite3 database
            creates new db if old db not found
        """
        self.connection = None
        try:
            self.connection = sqlite3.connect(db_file)
            self.connection.execute("PRAGMA foreign_keys = 1")
            self.cursor = self.connection.cursor()
            # print('Connection to sqlite3 db successfull.')
            self.connection_status = True

        except Exception as e:
            traceback.print_exc()
            print('error connection to sqlite3 db' + str(e))
            self.connection_status = False

        return self.connection_status
            
    def close_db(self):
        if self.connection_status:
            self.connection.close()
            self.connection_status = False
            return True
        else:
            return False

    def run_sql(self, sql, values = None):
        try:
            self.create_connection(self.db_path)
            #  table sql create script
            queryset = None
            if values:
                self.cursor.execute(sql, values)
            else:
                self.cursor.execute(sql)
            self.connection.commit()
            # print('sqlite query successfull.')
            query_run_status = True
            
            desc = self.cursor.description
            if desc:
                column_names = [col[0] for col in desc]
                queryset = [dict(zip(column_names, row)) for row in self.cursor.fetchall()]
            
            # if len(queryset) == 1:
            #     queryset = queryset[0]

        except Exception as e:
            print('failed to run sqlite query. ' + str(e) +'\n' + sql)
            query_run_status = False

        finally:
            self.close_db()
            return queryset, query_run_status
        

