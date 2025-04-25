# oid.txt té dues columnes: paraula i oid
# passem oid.txt a taula mysql
#
# https://dev.mysql.com/doc/connector-python/en/connector-python-example-cursor-transaction.html
#
import mysql.connector

mydb = mysql.connector.connect(
    host = "192.168.56.101",
    user = "mib",
    password = "password",
    database = "net_snmp"
)

cursorObject = mydb.cursor()

delete_oid = ("DELETE FROM oids")

add_oid = ("INSERT INTO oids "
          "(traduccio, oid) "
          "VALUES (%s, %s)")

cursorObject.execute(delete_oid)

file = open("oid.txt", "r")

for line in file:
    
    fields = line.strip().split('\t\t\t')
    cursorObject.execute(add_oid, tuple (field.strip('"') for field in fields))

mydb.commit()

file.close()
cursorObject.close()
mydb.close()

