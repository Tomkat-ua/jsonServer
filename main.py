#-----------------------------------------------------------------------------------------
import fbextract,os,platform
from dotenv import load_dotenv
from gevent.pywsgi import WSGIServer
from flask import Flask, jsonify,  abort, request
# import urllib.request
from datetime import datetime
# from flask_wtf import FlaskForm
# from wtforms import StringField, SubmitField, TextAreaField
# import requests
# import mqttParser
# from owlready2 import *




load_dotenv()

app = Flask(__name__)

local_ip = '192.168.10.9'

# print(f"Running JSON-SERVER on port {os.getenv('PORT')}" + " - http://" + local_ip + ':'+os.getenv('PORT'))

API_KEY = os.getenv("API_KEY","AIzaSyDtzSvLJesvqAUbySNq20egFBiKtZCKMEM")
# ALLOWED_IPS = {"192.168.10.*", "127.0.0.1"}
check_ext_ip = '192.168.10.1'

# print(f"Running JSON-SERVER {request.base_url}")
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

       # result = jsonify([dict(zip(columns, row)) for row in cur.fetchall()])
    return  jsonify(result)


@app.before_request
def check_ip_and_api_key():
    client_ip = request.remote_addr
    # if client_ip not in ALLOWED_IPS:
    if client_ip == check_ext_ip:
        # abort(403, description="Forbidden: IP not allowed")
        key = request.args.get("key")
        if key != API_KEY:
            abort(401, description="Unauthorized: Invalid API key")

@app.route('/', methods=['GET'])
def get_endpoints():
    # key = request.args.get("key")  # або request.headers.get("X-API-KEY")
    # if key != API_KEY:
    #     abort(401, description="Невірний API ключ")

    sql = ('select  q.num, q.endpoint,q.api_ver,q.description , \'' +str(request.base_url) +
           ('\'||utils.get_url(q.endpoint) as url '
            'from querys q'))
    result = curTojson(fbextract.get_data(sql))
    # print(f"The base URL is: {request.base_url}")
    return result, 200

########## NON API ##############
@app.route('/<endpoint>/json', methods=['GET'])
def get_nonapi_data(endpoint):

        try:
            sql = fbextract.get_sql(endpoint, None,1)
            data = curTojson(fbextract.get_data(sql),0)
            return data
        except Exception as e:
            return jsonify({'error': str(e),'sql':sql})

#################################



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
        # date1 = params.get('date1')
        # date2 = params.get('date2')
        # sql = 'select  O_TOVAR_KOD,O_TOVAR_NAME,O_TOVAR_EI from P_UV_ALL (?,?)'

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


######## -- DEVELOPER --######################################44

@app.route('/search')
def search():

    try:
       params = dict(request.args)
       date1 = params.get('date1')
       date2 = params.get('date2')
       sql = 'select  O_TOVAR_KOD,O_TOVAR_NAME,O_TOVAR_EI from P_UV_ALL (?,?)'
       con =  fbextract.create_connect()
       cur = con.cursor()
       cur.execute(sql,(date1,date2))
       result = cur.fetchall()
       cur.close()
       return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e), 'sql': sql}), 200




@app.route('/json', methods=['POST'])
def json():
    # Get the JSON data from the request
    data = request.get_json()
    # Print the data to the console
    print(data)
    # Return a success message
    return 'JSON received!'


@app.route('/date')
def get_date():
    a = 'Sun, 08 May 2024 07:05:33 GMT'
    dt = datetime.strptime(a, "%a, %d %b %Y %H:%M:%S %Z")
    result =dt
    print(result)
    return str(result)
########### END DEV ##############################
# if __name__ == "__main__":
#     http_server = WSGIServer((local_ip, int(os.getenv('PORT'))), app)
#     http_server.serve_forever()


if __name__ == "__main__":
    if platform.system() == 'Windows':
        http_server = WSGIServer((local_ip, int(os.getenv('PORT'))), app)
        print(f"Running HTTP-SERVER on port - http://" + local_ip + ':' + os.getenv('PORT'))
    else:
        http_server = WSGIServer(('', int(os.getenv('PORT'))), app)
        print(f"Running HTTP-SERVER on port :" + os.getenv('PORT'))
    http_server.serve_forever()
