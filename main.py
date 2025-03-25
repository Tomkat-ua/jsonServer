
#-- IMPORT -------------------------------------------------------------------------------
import fbextract,os,datetime
from dotenv import load_dotenv
from gevent.pywsgi import WSGIServer
from flask import Flask, jsonify,render_template

#-----------------------------------------------------------------------------------------
load_dotenv()

app = Flask(__name__)

print(f"Running JSON-SERVER on port {os.getenv('PORT')}")
##--------------------------------------------------------------##
def curTojson(cur,apiver=None):
    columns = [column[0] for column in cur.description]
    if apiver == 0:
        now = datetime.datetime.now()
        now = now.strftime("%Y-%m-%d %H:%M:%S")
        result = jsonify({ now:[dict(zip(columns, row)) for row in cur.fetchall()]})
    else:
        result = jsonify([dict(zip(columns, row)) for row in cur.fetchall()])
    return  result

########## NON API ##############
@app.route('/<endpoint>/json', methods=['GET'])
def get_nonapi_data(endpoint):
        try:
            sql = fbextract.get_sql(endpoint, None,1)
            data = curTojson(fbextract.get_data(sql),0)
            return data
        except Exception as e:
            return jsonify({'error': str(e),'sql':sql})

################################
@app.route('/api/1/<endpoint>',defaults={'p': None}, methods=['GET'])
@app.route('/api/1/<endpoint>/<p>', methods=['GET'])
def gen_data_1(endpoint,p):
    try:
        if p:
            sql = fbextract.get_sql(endpoint,p,1)
        else :
            sql = fbextract.get_sql(endpoint, None,1)
        print(sql)
        result = curTojson(fbextract.get_data(sql))
        #result.headers["Content-Type"] = "application/json; charset=utf-8"
        return result,200
    except Exception as e:
        return jsonify({'error': str(e), 'sql': sql}),200
################################
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
        #result.headers["Content-Type"] = "application/json; charset=utf-8"
        return result, 200
    except Exception as e:
        return jsonify({'error': str(e), 'sql': sql}), 200
################################


if __name__ == "__main__":
    http_server = WSGIServer(('', int(os.getenv('PORT'))), app)
    http_server.serve_forever()

