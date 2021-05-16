import mysql.connector


class Database:
    __instance = None

    @staticmethod
    def get_instance():
        if Database.__instance is None:
            Database()
        return Database.__instance

    def __init__(self, server, database, uid, pwd):
        self.mydb = mysql.connector.connect(
            host=server,
            user=uid,
            password=pwd,
            database=database
        )

    def get_id(self, id, table='tbl_Object'):
        with self.mydb.connect() as conn:
            result = conn.execute(r"SELECT * FROM {} WHERE IDs='{}'".format(table, id))
            row = result.fetchone()
            return row

    def get_all(self, table='tbl_Object'):
        with self.mydb.connect() as conn:
            result = conn.execute(r"SELECT * FROM {}".format(table))
            rows = result.fetchall()
            return rows

    def insert(self, object, table='tbl_Object'):
        with self.mydb.connect() as conn:
            if table == 'tbl_Object':
                return conn.execute(r"INSERT INTO {} (ImagePath, TypeID, Status, Identified, Estimate, Information)"
                                    r"VALUES (N'{}', '{}', '{}', N'{}', '{}', N'{}')"
                                    .format(table, object['ImagePath'], object['TypeID'], object['Status'], object['Identified'], object['Estimate'], object['Information']))
            elif table == 'tbl_Type':
                return conn.execute(r"INSERT INTO {} VALUES (N'{}', '{}')".format(table, object['TypeName'], object['Note']))

    def update(self, object, table='tbl_Object'):
        with self.mydb.connect() as conn:
            if table == 'tbl_Object':
                return conn.execute(r"UPDATE {} SET Identified=N'{}', Status={} WHERE IDs={}".format(table, object['Identified'], object['Status'], object['IDs']))