
import fbextract,os,platform
from dotenv import load_dotenv
from gevent.pywsgi import WSGIServer
from flask import Flask, jsonify,  abort, request
from datetime import datetime

load_dotenv()
app = Flask(__name__)

local_ip = '192.168.10.9'
version = os.environ.get('APP_VERSION')

API_KEY = os.getenv("API_KEY","333")
check_ext_ip = os.getenv("CHECK_EXT_IP",'192.168.10.1')


def curTojson(cur,apiver=None):
    columns = [column[0] for column in cur.description]
    if apiver == 0:
        now = datetime.now()
        now = now.strftime("%Y-%m-%d %H:%M:%S")
        result = jsonify({ now:[dict(zip(columns, row)) for row in cur.fetchall()]})
    else:
        result = []
        for row in cur.fetchall():
            result.append(dict(zip(columns, row)))
    return  jsonify(result)


@app.before_request
def check_ip_and_api_key():
    client_ip = request.remote_addr
    if client_ip.startswith("::ffff:"):
        client_ip = client_ip.split("::ffff:")[-1]
    print(f"Запит з {client_ip} на {request.path}")
    if client_ip == check_ext_ip:
        # abort(403, description="Forbidden: IP not allowed")
        key = request.args.get("key")
        if key != API_KEY:
            abort(401, description="Unauthorized: Invalid API key")

@app.route('/', methods=['GET'])
def get_endpoints():
    sql = ('select  q.num, q.endpoint,q.api_ver,q.description , \'' +str(request.base_url) +
           ('\'||utils.get_url(q.endpoint) as url '
            'from querys q'))
    result = curTojson(fbextract.get_data(sql))
    return result, 200

@app.route('/api/1/<endpoint>',defaults={'p': None}, methods=['GET'])
# @app.route('/api/1/<endpoint>', methods=['GET'])
def gen_data_1(endpoint,p):
    p = request.args.get('where')
    print(p)
    try:
        if p:
            sql = fbextract.get_sql(endpoint,p,1)
        else :
            sql = fbextract.get_sql(endpoint, None,1)
        print(sql)
        result = curTojson(fbextract.get_data(sql))
        return result,200
    except Exception as e:
        return jsonify({'error': str(e), 'sql': sql}),200

##############################################
@app.route('/api/2/<endpoint>', defaults={'p': None}, methods=['GET'])
@app.route('/api/2/<endpoint>/<p>', methods=['GET'])
def gen_data_2(endpoint, p):
    try:
        if p:
            sql = fbextract.get_sql(endpoint, p,2)
        else:
            sql = fbextract.get_sql(endpoint, None,2)
        print(sql)
        result = curTojson(fbextract.get_data(sql))
        return result, 200
    except Exception as e:
        return jsonify({'error': str(e), 'sql': sql}), 200

@app.route('/api/3/<endpoint>', methods=['GET'])
def gen_data_3(endpoint):
    try:
        params = dict(request.args)
        where = ''
        print(params)
        sql = fbextract.get_sql(endpoint, None, 1)
        for key,value in params.items():
            where = where + " and "+ key+'='+value
            where = where.replace('=like',' like')
        sql = sql + where
        print(sql)
        con =  fbextract.create_connect()
        cur = con.cursor()
        # cur.execute(sql,(date1,date2))
        result = curTojson(cur.execute(sql))
        cur.close()
        return   result
    except Exception as e:
        return jsonify({'error': str(e), 'sql': sql}), 200


if __name__ == "__main__":
    if platform.system() == 'Windows':
        http_server = WSGIServer((local_ip, int(os.getenv('PORT'))), app)
        print(f"Running HTTP-SERVER ver. {version} on port - http://" + local_ip + ':' + os.getenv('PORT'))
    else:
        http_server = WSGIServer(('', int(os.getenv('PORT'))), app)
        print(f"Running HTTP-SERVER ver. {version} on port :" + os.getenv('PORT'))
    http_server.serve_forever()
