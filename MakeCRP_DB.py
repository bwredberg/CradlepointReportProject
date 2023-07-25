import sqlite3

# Connect to the database (create a new one if it doesn't exist)
conn = sqlite3.connect('cradlepoint_usage.db')

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

# Create the table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS data_usage (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        Cradlepoint TEXT,
        MB_used REAL,
        date DATE
    )
''')

# Commit the changes and close the connection
conn.commit()
conn.close()