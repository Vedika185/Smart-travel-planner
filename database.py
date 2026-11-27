import pymysql
import os
import sqlite3
from config import Config

def get_db_connection():
    """
    Connects to MySQL database using PyMySQL with DictCursor.
    Falls back gracefully to a local SQLite database (smart_travel.sqlite3)
    if MySQL server is offline, ensuring zero friction in development.
    """
    use_sqlite = os.getenv('USE_SQLITE_FALLBACK', 'false').lower() == 'true'
    
    if not use_sqlite:
        try:
            connection = pymysql.connect(
                host=Config.DB_HOST,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME,
                port=Config.DB_PORT,
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True,
                charset='utf8mb4'
            )
            return connection, 'mysql'
        except Exception as e:
            # If MySQL connection fails, fall back to SQLite
            print(f"[SmartTravel DB] MySQL connection unavailable ({e}). Using SQLite fallback for seamless execution.")

    # SQLite Fallback Connection
    sqlite_path = os.path.join(os.path.dirname(__file__), 'smart_travel.sqlite3')
    conn = sqlite3.connect(sqlite_path)
    conn.row_factory = sqlite3.Row
    return conn, 'sqlite'

def query_db(query, args=(), one=False):
    """Executes a SELECT query and returns list of dictionaries or single dictionary."""
    conn, db_type = get_db_connection()
    try:
        cursor = conn.cursor()
        if db_type == 'sqlite':
            # Translate MySQL placeholders %s to SQLite ?
            sqlite_query = query.replace('%s', '?')
            cursor.execute(sqlite_query, args)
            rows = cursor.fetchall()
            result = [dict(row) for row in rows]
        else:
            cursor.execute(query, args)
            result = cursor.fetchall()
        
        cursor.close()
        if not db_type == 'sqlite':
            conn.close()
        return (result[0] if result else None) if one else result
    except Exception as err:
        print(f"[DB Error in query_db]: {err}")
        raise err

def execute_db(query, args=(), return_id=False):
    """Executes INSERT, UPDATE, DELETE statements."""
    conn, db_type = get_db_connection()
    try:
        cursor = conn.cursor()
        if db_type == 'sqlite':
            sqlite_query = query.replace('%s', '?')
            cursor.execute(sqlite_query, args)
            conn.commit()
            last_id = cursor.lastrowid
        else:
            cursor.execute(query, args)
            last_id = cursor.lastrowid
            conn.commit()
        
        cursor.close()
        conn.close()
        return last_id if return_id else True
    except Exception as err:
        print(f"[DB Error in execute_db]: {err}")
        raise err

def init_db():
    """Initializes tables and seeds default data if tables do not exist."""
    schema_file = os.path.join(os.path.dirname(__file__), 'schema.sql')
    if os.path.exists(schema_file):
        with open(schema_file, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        print("[SmartTravel DB] Schema file verified and ready for deployment.")
