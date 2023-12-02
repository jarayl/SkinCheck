import sqlite3

db = sqlite3.connect('skincheck.db')

db.execute('CREATE TABLE docs (dId TEXT, password TEXT, name TEXT, dEmail TEXT)')
db.execute('CREATE TABLE docPatRel (dId TEXT, pId TEXT)')
db.execute('CREATE TABLE pats (pId TEXT, name TEXT, pEmail TEXT, gender TEXT, age INTEGER, password TEXT)')
db.execute('CREATE TABLE data (dId TEXT, pId TEXT, diagnosis TEXT, desc TEXT, date DATETIME, img BLOB, overlay BLOB)')

print("done!")

db.close()

