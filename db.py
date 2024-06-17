import psycopg2


def get_db_connection():
    conn = psycopg2.connect(
        host="",
        port="",
        database="",
        user="",
        password=""
    )
    return conn
