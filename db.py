from flask import g, current_app
# g safe threading for multiple requests,
import sqlite3
from typing import Dict, Tuple, Any, Callable


def db_get_cursor():
    conn = db_get_conn()
    return conn.cursor()


def db_get_conn():
    """
    Retrieve the global database connection for the current request.

    The `g` object is Flask's global object for request-data lifecycle.
    `g.conn` ensures that only single SQLite connection is used.
    """
    if hasattr(g, 'conn'):
        return g.conn # connection exists, with row factory already set
    try:
        g.conn = sqlite3.connect('gunpla.db', isolation_level=None) # autocommit ON
        g.conn.row_factory = sqlite3.Row # set row_factory to sqlite3.Row class; calling it later will return an instance of Row
        return g.conn
    except sqlite3.Error as e:
        # this covers many types of DB errors
        raise Exception (f"Failed to connect to the database : {e}")



# helps close the DB conn, even if there is an error.
def db_close(error: str) -> Dict|None:
    if hasattr(g, 'conn'):
        try:
            g.conn.close()
        except Exception as e:
            # handle DB closing errors
            current_app.logger.error(f"Failed to close database connection: {e}")
            return ({'error': f"Failed to close database connection: {e}"})

    if error:  # handles errors resulting from within the Routes
        current_app.logger.error(f"Request ended with error: {error}")
        return ({'error': f"Request ended with error: {error}"})


def db_create_kit(data: dict [str, str|int|None]) -> dict[str, str|bool|None]: 
    cursor = db_get_cursor()
    columns = list(data.keys())
    values = tuple(data.values())
    column_string = ", ".join(columns) # using ", " as the delimiter btwn each element in STR, which is built from 'columns'.
    placeholders = ", ".join(["?"] * len(columns)) # we need [ ] around the "?", since .join() needs an iterable
    sql = f"INSERT INTO gunpla ({column_string}) VALUES ({placeholders})"

    try: 
        # Values are passed HERE to prevent SQL injection. 
        # Adding them directly to the SQL string would be unsafe and error-prone.
        cursor.execute(sql, values)
        return {"success": True, "message": f"Kit {data.get('name')} created successfully"}
    
    except sqlite3.Error as e: # specific catch for DB errors
        current_app.logger.error(f"create_kit : database error on Create = {e}")
        return {"success": False, "error": f"Database failed to create kit: {str(e)}"}

def db_get_collection(user_id):
    """Retrieve all kits from the database for a specific user."""
    with sqlite3.connect('gunpla.db') as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM gunpla WHERE owner_id = ? ORDER BY id ASC", (user_id,))
        rows = cursor.fetchall()
    return [dict(row) for row in rows]


def db_create_kit():
    """
    Create a kit by data and owner ID (session).
    Returns:
        dict | None
    """
    conn = db_get_conn()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cur.execute("INSERT INTO gunpla(name, scale , material, notes, condition, grade, owner_id) VALUES (?, ?, ?, ?, ?, ?, ?)", \
            (name, scale, material, notes, condition, grade, session['user_id']))
        return 0 
    row = cursor.fetchone()
    return dict(row) if row else None



def db_get_kit(kit_id: int, user_id: int) -> dict | None:
    """
    Retrieve a single kit by its ID and owner ID.

    Returns:
        dict | None: A dictionary containing the kit's information if found, otherwise None.
    """
    conn = db_get_conn()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM gunpla WHERE id = ? AND owner_id = ?", (kit_id, user_id))
    row = cursor.fetchone()
    return dict(row) if row else None


def db_delete_kit(kit_id: int, user_id: int) -> dict [str|bool, str|bool]:
    """
    Deletes a kit by its ID and owner ID.

    Returns:
        dict: Indicates success or failure.
    """
    conn = db_get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM gunpla WHERE id = ? AND owner_id = ?", (kit_id, user_id))
        if cursor.rowcount == 0:
            return {"success": False, "error": f"Failed to delete kit ID # {kit_id}."}
        return {"success": True, "message": f"Kit with ID {kit_id} deleted."}
    
    except sqlite3.Error as e:  # Catch only database-related errors for better specificity
        # Use current_app.logger to log errors tied to the current Flask app instance
        current_app.logger.error(f"db_delete_kit: Database error: {e}")
        return {"success": False, "error": f"Database error: {str(e)}"}

    

