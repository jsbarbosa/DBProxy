import MySQLdb

db = MySQLdb.connect(
    host="0.0.0.0",
    user="root",
    passwd="root",
    port=3307
)        # name of the data base

# you must create a Cursor object. It will let
#  you execute all the queries you need
cur = db.cursor()

db.close()
