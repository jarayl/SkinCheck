import sqlite3

db = sqlite3.connect('skincheck.db')

db.execute('CREATE TABLE users ()')
