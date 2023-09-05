import mysql.connector
class database:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            passwd="175459295",
            database="testing"
        )
        self.cursur = self.connection.cursor()

    def createDB(self,database):
        self.cursur.execute("CREATE DATABASE %s", database)

    def createTable(self,table,typeLst):
        formula = "CREATE TABLE " + table + " ("

        for i in range(len(typeLst)):
            if i == len(typeLst) - 1:
                formula += typeLst[i][0] + " " + typeLst[i][1]
            else:
                formula += typeLst[i][0] + " " + typeLst[i][1] + ','
        formula += ")"
        self.cursur.execute(formula)

    def dropTb(self,table):
        formula = "DROP TABLE %s CASCADE CONSTRAINTS"
        self.cursur.execute(formula,table)

    def execute(self,query):
        self.cursur.execute(query)

def main():
    connection = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        passwd="175459295",
        database="testing"
    )
    cursur = connection.cursor()
    db = database()
    db.dropTb("activity")
    db.dropTb("goal")
    db.dropTb("password")
    db.dropTb("users")
    db.execute("CREATE TABLE users (user_id NUMBER NOT NULL PRIMARY KEY ,user_username NUMBER NOT NULL, user_email VARCHAR2(32 CHAR))")
