
import os,fdb#,json



# fb_monitoring = Gauge('fb_monitoring','FB Monitoring Data',['host','db','key'])
# info= Info('app','Application about',['name','version'])
# info.labels(app_name,app_ver)

sql = ('select  a.* '
       ' from monitoring.get_loses_analitic a ')

delay_sec        = os.getenv("DELAY_LOOP", 10)
db_server        = os.getenv("DB_HOST", '192.168.10.5')
db_path          = os.getenv("DB_PATH", 'sklad_dev')
db_user          = os.getenv("DB_USER", 'sysdba')
db_password      = os.getenv("DB_PASSWORD", 'masterkey')
#export_file      = os.getenv("EXPORT_FILE", '//192.168.10.5/data/АППО/ОБЛІК АППО/sklad_data.csv')
#export_file      ='c:/sklad/sklad_data.csv'

def get_data():
    #driver_config.server_defaults.host.value = db_server
   # con = connect(db_path, user=db_user, password=db_password)
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
    cur.execute(sql)
    # rows = cur.fetchall()

    columns = [column[0] for column in cur.description]
    data = [dict(zip(columns, row)) for row in cur.fetchall()]
    # print(data)
    # json_data=json.dumps({'losses':data})
    #json_data = json.dumps({'losses':data})#, indent=4)
    #print(json_data)
    return data
# #------------------------
#     # Fetch all rows and convert to a list of dictionaries
#     rows = cur.fetchall()
#     result = []
#     for row in rows:
#         d = {}
#         #print(d)
#         for i, col in enumerate(cur.description):
#             d[col[0]] = row[i]
#             result.append(d)
#     # Convert the list of dictionaries to JSON and print it
#     json_result = json.dumps({'losses': result})
#     return json_result
# #------------------

# get_data()