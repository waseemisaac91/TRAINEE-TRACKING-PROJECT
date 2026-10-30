import psycopg2

DB_CONFIG = {
    "dbname": "crm",
    "user": "postgres",
    "password": "W@isaac1091",
    "host": "localhost",
    "port": "5432"
}

try:
    connection = psycopg2.connect(**DB_CONFIG)
    print("Connection successful!")
    cursor = connection.cursor()

  
    # Query: Number of applications per trainee
    query = """
        SELECT t.FullName, COUNT(a.ApplicationID) AS Total_Applications
        FROM Trainees t
        JOIN Applications a ON t.TraineeID = a.TraineeID
        GROUP BY t.TraineeID, t.FullName
        ORDER BY Total_Applications DESC;
    """
    cursor.execute(query)
    results = cursor.fetchall()

    print("--- Applications per Trainee ---")
    for row in results:
        print(f"Trainee: {row[0]} | Applications: {row[1]}")

except Exception as e:
    print(f"Error: {e}")

finally:
    if 'connection' in locals():
        cursor.close()
        connection.close()