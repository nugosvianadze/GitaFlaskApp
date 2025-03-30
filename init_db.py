import sqlite3

DATABASE = 'my_first_db.sqlite3'

conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

print("creating users table.....")
try:
    cursor.execute(
        """
        CREATE TABLE if not exists users
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT,
        last_name TEXT,
        age INTEGER,
        birth_date DATE,
        address TEXT,
        password TEXT,
        id_number INTEGER,
        email TEXT
    );
        """
    )
except Exception as e:
    print(f"error while creating users table : {e}")
finally:
    conn.commit()
    print('users table craeted successfully')
