import sqlite3

db = sqlite3.connect('skincheck.db')

db.execute('CREATE TABLE doctors (dId TEXT PRIMARY KEY UNIQUE, password TEXT NOT NULL, name TEXT NOT NULL, dEmail TEXT NOT NULL)')
db.execute('CREATE TABLE docPatRel (dId TEXT, pId TEXT NOT NULL)')
db.execute('CREATE TABLE patients (pId TEXT PRIMARY KEY UNIQUE, password TEXT NOT NULL, name TEXT NOT NULL, pEmail TEXT NOT NULL, gender TEXT, age INTEGER)')
db.execute('CREATE TABLE data (dId TEXT NOT NULL, pId TEXT NOT NULL, diagnosis TEXT NOT NULL, desc TEXT, date DATETIME, img BLOB, overlay BLOB)')

print("done!")

db.close()

