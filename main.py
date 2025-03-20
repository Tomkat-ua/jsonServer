
#-----------------------------------------------------------------------------------------
import datetime, logging, sys,os,csv,fbextract
from dotenv import load_dotenv
from gevent.pywsgi import WSGIServer
from io import StringIO
from flask import Flask, jsonify
from json import load as jsonLoad
#-----------------------------------------------------------------------------------------

def removeLog():
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    sys.modules['flask.cli'].show_server_banner = lambda *x: None

def findIndexById(resourceList, id):
    for index, item in enumerate(resourceList):
        if item.get("id") == id:
            return index
    return None

def printColor(message, color):
    return (f"\033[{color}m{message}\033[00m")


def curTojson(cur):
    columns = [column[0] for column in cur.description]
    return  [dict(zip(columns, row)) for row in cur.fetchall()]

with open("qrys.json", "r") as f:
    q = jsonLoad(f)

#now = datetime.datetime.now()
load_dotenv()

app = Flask(__name__)


print(f"Running JSON-SERVER on port {os.getenv('PORT')}")

##--------------------------------------------------------------##
################################
@app.route('/<resource>/<out>', methods=['GET'])
def get_resource(resource,out):
        try:
            sql = q[resource]
            if out == 'json':
                data = curTojson(fbextract.get_data(sql))
                now = datetime.datetime.now()
                return   jsonify({now.strftime("%Y-%m-%d %H:%M:%S") : data})
            if out == 'csv':
                return curTocsv(fbextract.get_data(sql))
        except Exception as e:
            return jsonify({'error': str(e),'sql':sql})
################################
@app.route('/get_lost/<serial>', methods=['GET'])
def docs_serial(serial):
    try:
        sql = q['get_lost'] % serial
        data = curTojson(fbextract.get_data(sql))
        return data
    except Exception as e:
        return jsonify({'error': str(e), 'sql': sql})
###############################
@app.route('/get_lost_items/<serial>/<p>', methods=['GET'])
def items_serial(serial,p):
    try:
        sql = str(q['get_lost_items']) #% serial
        sql = sql.replace('%s',serial)
        where =''
        if p == '-1':
            where = ' where t.item_count_loss >0 '
        if p == "1":
            where = ' where t.item_count_rem > 0 '
        if p == "0":
            where =''

        sql = sql + where
        print(sql)
        data = curTojson(fbextract.get_data(sql))
        return data
    except Exception as e:
        return jsonify({'error': str(e), 'sql': sql})
##############################
@app.route('/test', methods=['GET'])
def test():
    # import hashlib
    # hash_object = hashlib.md5(b'Hello World')
    # print(hash_object.hexdigest())
    # return hash_object.hexdigest()
    with open("qrys.json", "r") as f:
        j = json.load(f)
    return j
#############################
if __name__ == "__main__":
    http_server = WSGIServer(('', int(os.getenv('PORT'))), app)
    http_server.serve_forever()

