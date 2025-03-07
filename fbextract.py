
import os,fdb
db_server        = os.getenv("DB_HOST", '192.168.10.5')
db_path          = os.getenv("DB_PATH", 'sklad_prod')
db_user          = os.getenv("DB_USER", 'MONITOR')
db_password      = os.getenv("DB_PASSWORD", 'inwino')

def create_connect():
    con = fdb.connect(
        host=db_server,
        port=3053,
        database=db_path,
        user=db_user,
        password=db_password,
        charset="utf-8",
        fb_library_name="C:/sklad/x64/fbclient.dll"
    )
    return con

def close_connect(con):
    con.close()

def exec_proc(sql,params):
    con = create_connect()
    cur = con.cursor()
    cur.callproc(sql, params)
    # data  = cur.fetchone()
    data = cur.fetchall()
    close_connect(con)
    cur.close()
    return data

def get_data(sql):
    #sql = 'select * from ' + sql
    con = create_connect()
    cur = con.cursor()
    data = cur.execute(sql)
    # columns = [column[0] for column in cur.description]
    # data = [dict(zip(columns, row)) for row in cur.fetchall()]
    # close_connect(con)
    return data
    cur.close()
    close_connect(con)

