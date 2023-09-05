import mysql.connector

mydb = mysql.connector.connect(
    host = "localhost",
    user = "root",
    passwd = "175459295"
)
print(mydb)
# class utility:
#     def __init__(self):
#         try:
#             with connect(
#                     host="localhost",
#                     user=input("Enter username: "),
#                     password=getpass("Enter password: "),
#                     database="online_movie_rating",
#             ) as connection:
#                 self.connection = connection
#                 print(connection)
#
#         except Error as e:
#             print(e)
#
#     def read_multi_query(self,query):
#         select_statement = f'SELECT * FROM {query}'
#         with self.connection.cursor() as cursor:
#             cursor.execute(select_statement)
#             result = cursor.fetchall()
#             for row in result:
#                 print(row)