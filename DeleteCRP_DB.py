import sqlite3

# Connect to the database
conn = sqlite3.connect('cradlepoint_usage.db')

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

# Delete all rows from the table
cursor.execute('DELETE FROM data_usage')

# Commit the changes
conn.commit()

# Close the connection
conn.close()
