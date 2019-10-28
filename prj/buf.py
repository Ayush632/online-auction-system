import mysql.connector
from mysql.connector import Error
 
 
def connect():
    """ Connect to MySQL database """
    conn = None
    try:
        conn = mysql.connector.connect(host='localhost',
                                       user='ayush',
                                       password= '9290827021')
        if conn.is_connected():
            cursor=conn.cursor()
            cursor.execute("use prj")
            name="user"
            cr=50
          #  cursor.execute("""select * from wallet where user_name =%s""",(name,))
            cursor.execute("""update wallet set credits=%s where user_name = %s""",(cr,name))
        
            #row=cursor.fetchall(
          #  for i in row:
           #     print(i)
            #print('Connected to MySQL database')
 
    except Error as e:
        print(e)
 
    finally:
        if conn is not None and conn.is_connected():
            conn.close()
 
 
if __name__ == '__main__':
    connect()