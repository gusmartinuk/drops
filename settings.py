import pymysql.cursors

from config import *

def is_connected():
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            return result is not None
    except Exception as e:
        return False

def connect():
    global connection
    if is_connected():
        return connection
    # Connect to your MySQL database
    connection = pymysql.connect(
        host=DATABASE_HOST,
        user=DATABASE_USERNAME,
        password=DATABASE_PASSWORD,
        db=DATABASE_NAME,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False)
    return(connection)

def disconnect():
    global connection
    with connection.cursor() as cursor:
        cursor.close()
    connection.commit()
    connection.close()

def sqlfirst(query,xdata=()):
    global connection;
    with connection.cursor() as cursor:
        # Executing the SQL query
        cursor.execute(query,xdata)
        # Fetching the first value from the result
        result = cursor.fetchone()
        if result:
            # Retrieving the first value from the result's list of values
            first_value = list(result.values())[0]
            return first_value
        else:
            return None


def sqlexec(query,xdata=()):
    global connection;
    insertid=None
    with connection.cursor() as cursor:
        # Executing the SQL query
        if xdata==():
            cursor.execute(query)
        else:    
            cursor.execute(query,xdata)
        if "insert" in query.lower():
            insertid=cursor.lastrowid        
            connection.commit()
    return(insertid)

connection=connect()
