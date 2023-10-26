import pyodbc

dsn = "BddTrav"
user = "sa"
password = "123Paoma456"

# Connection string
#conn_str = f"DSN={dsn};UID={user};PWD={password}"
conn_str = "Driver={FreeTDS};Server=ccpserver;Database=BddTrav;UID=sa;PWD=123Paoma456;TrustServerCertificate=no;"



try:
    # Connect to the ODBC data source
    conn = pyodbc.connect(conn_str)

    # Perform database operations
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Tblbureau WHERE ncodique='10101'")
    rows = cursor.fetchall()
    
    # Print the retrieved data
    for row in rows:
        print(row)

    # Close the connection
    conn.close()

except pyodbc.Error as e:
    print(f"Error connecting to the ODBC data source: {e}")
