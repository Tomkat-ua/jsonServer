
import os,fdb


# sql = ('select  a.* '
#        ' from monitoring.get_loses_analitic a ')

delay_sec        = os.getenv("DELAY_LOOP", 10)
db_server        = os.getenv("DB_HOST", '192.168.10.5')
db_path          = os.getenv("DB_PATH", 'sklad_prod')
db_user          = os.getenv("DB_USER", 'sysdba')
db_password      = os.getenv("DB_PASSWORD", 'masterkey')
#export_file      = os.getenv("EXPORT_FILE", '//192.168.10.5/data/АППО/ОБЛІК АППО/sklad_data.csv')
#export_file      ='c:/sklad/sklad_data.csv'

def get_data(sql):
    con = fdb.connect(
        host=db_server,
        port=3053,
        database=db_path,
        user=db_user,
        password=db_password,
        charset="utf-8",
        fb_library_name="C:/sklad/x64/fbclient.dll"
    )
    cur = con.cursor()
    data = cur.execute(sql)
    # columns = [column[0] for column in cur.description]
    # data = [dict(zip(columns, row)) for row in cur.fetchall()]
    return data
