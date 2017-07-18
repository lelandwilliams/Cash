# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import mysql.connector
from mysql.connector import errorcode

TABLES={}

TABLES['vendor'] = (
        "CREATE TABLE `vendor` ("
        "`name` VARCHAR(60) NOT NULL KEY,"
        "`alias` VARCHAR(60) ,"
        "`category` VARCHAR(60) )"
        )


TABLES['budget'] = (
        "CREATE TABLE `budget` ("
        "`month` TINYINT NOT NULL,"
        "`year` SMALLINT NOT NULL)"
        )

TABLES['transaction'] = (
        "CREATE TABLE `transaction` ("
       "`idx` SERIAL,"
        "`date` DATE,"
        "`amount` DECIMAL(7,2) NOT NULL,"
        "`vendor` VARCHAR(60),"
        "`alias` VARCHAR(60),"
        "`category` VARCHAR(60) )"
        )


config = {
        'user':'user',
        'password':'pword',
        'database':'cash'
        }
sql = mysql.connector.connect(**config)

cursor = sql.cursor()
for name,ddl in TABLES.items():
    try:
        print("Creating table {}: ".format(name), end='')
        cursor.execute(ddl)
    except mysql.connector.Error as err:
        print('')
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("already exists.")
        else:
            print(err.msg)
    else:
            print("OK")

cursor.close()
sql.close()

