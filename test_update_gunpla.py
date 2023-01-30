import os
from flask import Flask, flash, jsonify, redirect, render_template, request, session
import sqlite3


# sets up this file as main module, setting folders & files relative to it
app = Flask(__name__, instance_relative_config=True)
# con = sqlite3.connect("gunpla.db")  # accesses the DB, or implicitly creates it in DIR

 # threading issue when writing to db -- ask about it
 # isolation level = autocommit > on.  Ask about this, too
conn = sqlite3.connect('gunpla.db', check_same_thread=False, isolation_level=None)
conn.row_factory = sqlite3.Row # use built-in Row-factory to help parse Tuples
cur = conn.cursor()
#cur = con.cursor()  # set up cursor obj


def update_gunpla(action, kit_data=None, kit_id=None):

    app.logger.info("FUNCTION update_gunpla STARTED %s")
 
    if kit_data:
        name = kit_data['name']
        scale = kit_data['scale']
        notes = kit_data['notes']
        condition = kit_data['condition']
        grade = kit_data['grade']
        material = kit_data['material']

    

    if action == "create":
        # app.logger.info("FUNC: update_gunpla CREATE %s")
        # app.logger.info(f" FUNC: adding to Gunpla DB {kit_data['name']}")
        cur.execute("INSERT INTO gunpla (name, scale , material, notes, condition, grade) VALUES (?, ?, ?, ?, ?, ?)", (name, scale, material, notes, condition, grade))


    elif action == "update":

        app.logger.info("FUNC: update_gunpla UPDATE **** %s")
        app.logger.info(f"FUNC:  UPDATING to Gunpla DB {kit_data['name']}")
        cur.execute("UPDATE gunpla SET name = ?, scale = ?, material = ?, notes = ?, condition = ?, grade = ? WHERE id = ?", [name, scale, material, notes, condition, grade, kit_id])
                    
        app.logger.info("FUNC: update_gunpla EDIT now completed!!!!! %s")

    elif action == "delete":
        cur.execute("DELETE FROM gunpla WHERE id = ?", (kit_id,))  

    else:
        print("Unknown input - update_gunpla in error")
        app.logger.info("Unknown input - update_gunpla in error")


alex ={
    'name': 'Alex N',
    'scale': '100',
    'notes': 'No notes',
    'grade': 'mg',
    'material': 'plastic',
    'condition': 'snapped',
}

zeta ={
    'name': 'MSZ-006 Zeta Gundam 2.0',
    'scale': '100',
    'notes': 'stored in Z 2.0 box, may be broken?',
    'grade': 'mg',
    'material': 'plastic',
    'condition': 'snapped',
}

# for k, v in my_data.items():
#     print(k,v)

# update_gunpla(action='update', kit_id=119, kit_data=alex)

# update_gunpla(action="create", kit_data=zeta)

update_gunpla(action="update", kit_data=zeta, kit_id=128)

# update_gunpla(action='delete', kit_id='127')

print("Program done.")