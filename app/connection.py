import psycopg2

def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="finsavvy_db",
        user="postgres",
        password="postgres"
    )
    return conn
