
import os,fdb

db_server        = os.getenv("DB_HOST", '192.168.10.5')
db_path          = os.getenv("DB_PATH", 'sklad_dev')
db_user          = os.getenv("DB_USER", 'sysdba')
db_password      = os.getenv("DB_PASSWORD", 'masterkey')



def create_connect():
    con = fdb.connect(
        host=db_server,
        port=3053,
        database=db_path,
        user=db_user,
        password=db_password,
        charset="utf-8"
    )
    return con

def close_connect(con):
    con.close()

def get_data(sql):
#    con = fdb.connect(
#        host=db_server,
#        port=3053,
#        database=db_path,
#        user=db_user,
#        password=db_password,
#        charset="utf-8"
#    )
    con = create_connect()
    cur = con.cursor()
    data = cur.execute(sql)
    return data
    cur.close()
    close_connect(con)

