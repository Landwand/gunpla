
import os
from flask import Flask, flash, jsonify, redirect, render_template, request, session
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash

# kit_data = {
# 'condition': 'used',
# 'grade' : 'hg',
# 'name' :'zaku',
# 'notes' : 'none',
# 'scale' : '144',
# 'material' : 'ip'
# }

# for k, v in kit_data.items():
#     print ("K and V: ",k, v)

# def hashprint(variable):
#     hashed = generate_password_hash(variable)
#     print(f"this is the hashed: {hashed}")
#     checked = check_password_hash(hashed, variable)
#     print(f'This is the check: {checked}')
#     checked = check_password_hash(hashed, variable)
#     print(f'This is the check: {checked}')
#     checked = check_password_hash(hashed, variable)
#     print(f'This is the check: {checked}')


# if __name__ == "__main__":
#     var = input("What is the hash to check? ")
#     hashprint(var)

# '''


# CREATE TABLE gunpla(
# id INTEGER PRIMARY KEY,
# grade TEXT,
# scale INTEGER,
# name TEXT,
# material TEXT,
# condition TEXT,
# notes TEXT,
# owner_id INT);

# ''''


conn = sqlite3.connect('gunpla.db', check_same_thread=False, isolation_level=None) # accesses the DB, or implicitly creates it in DIR
conn.row_factory = sqlite3.Row # use built-in Row-factory to help parse Tuples
cur = conn.cursor()

username = 'test4'
hashed_pw = 'test4'
cur.execute("SELECT * FROM users WHERE username = ?", (username,))
r = cur.fetchone()
if r:
    print (f"Rows : {r['username']}")
else:
    print("name doesn't exist yet")

cur.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (username, hashed_pw))

print ('Work done!')



