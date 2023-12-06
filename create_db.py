import sqlite3

con = sqlite3.connect('skincheck.db')
db = con.cursor()

db.execute('CREATE TABLE doctors (dId INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, password TEXT NOT NULL, name TEXT NOT NULL, dEmail TEXT NOT NULL UNIQUE)')
db.execute('CREATE TABLE docPatRel (dId INTEGER, pId INTEGER NOT NULL)')
db.execute('CREATE TABLE patients (pId INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, password TEXT NOT NULL, name TEXT NOT NULL, pEmail TEXT NOT NULL UNIQUE, gender TEXT, age INTEGER, dob DATETIME, status TEXT DEFAULT "No Data")')
db.execute('CREATE TABLE data (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, dId INTEGER NOT NULL, pId INTEGER NOT NULL, diagnosis TEXT NOT NULL, desc TEXT, date DATETIME, img BLOB, overlay BLOB)')

con.commit()
print("done!")

con.close()

