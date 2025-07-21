
#-----------------------------------------------------------------------------------------
import datetime, logging, sys,os,csv,fbextract,json
from dotenv import load_dotenv
from gevent.pywsgi import WSGIServer
from io import StringIO
from flask import Flask, jsonify,render_template,request
import mgrs
from flask_restful import Api, Resource
from flask_cors import CORS

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

load_dotenv()

app = Flask(__name__)
# api = Api(app)
CORS(app)

api_ver = '0.1'

print(f"Running JSON-SERVER on port {os.getenv('PORT')}")


with open("qrys.json", "r") as f:
    q = json.load(f)
# q = {
#     "losses":"select  * from v_loses",
#     "analitic":"select  * from V_SKLAD_ANALITIC_2",
#     "loss-cost":"losses.up_losses_cost",
#     "arrived": "select * from VIEW_PRIHOD"
# }
def get_sql(endpoint,p,apiver):
    sql = 'select * from querys where ENDPOINT = \'%s\';' % endpoint
    data = fbextract.get_data(sql)
    for row in data:
        result = row[2]
        if p:
            result = result + ' where ' + p
        return result


def curTojson(cur):
    columns = [column[0] for column in cur.description]
    return  jsonify([dict(zip(columns, row)) for row in cur.fetchall()])

# api.add_resource(UserData, "/api/data")

def curTocsv(cur):
    column_names = [i[0] for i in cur.description]
    f = StringIO()
    w = csv.writer(f,delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    w.writerow(column_names)
    for row in cur:
        w.writerow(row)
    #w.writerows(cur)

    result = f.getvalue()
    return result



# @app.route('/<res>', methods=['GET'])
# def get_from_proc(res):
#     # return q["test"]
#     # param = []
#     # print(fbextract.get_data(q[res]))
#     data = curTojson(fbextract.get_data(q[res]))
#     # data = curTojson(fbextract.exec_proc(q["test"],param))
#
#     return jsonify({now.strftime("%Y-%m-%d %H:%M:%S"): data})

#@app.route('/<resource>/<out>', methods=['GET'])
# def get_resource(resource,out):
#         try:
#             if out == 'json':
#                 data = curTojson(fbextract.get_data(q[resource]))
#                 return   jsonify({now.strftime("%Y-%m-%d %H:%M:%S") : data})
#             if out == 'csv':
#                 return curTocsv(fbextract.get_data(q[resource] ))
#         except Exception as e:
#             # return  '<html> <h4> ERROR</h4> </br> <body>'  +str(e) + '</body></html>'
#             return jsonify({'error': str(e)})


@app.route("/")
def index():
    return render_template("index1.html")


@app.route("/api/data", methods=["GET"])
def get_data():
    data = {
        "name": "Alice",
        "age": 25,
        "email": "alice@example.com",
        "skills": ["Python", "Flask", "API Development"]
    }
    return jsonify(data)

# @app.route('/', methods=['GET', 'POST'])
# def home():
#     if request.method == 'GET':
#         return render_template('index1.html')
#     name = request.form.get('name')
#     email = request.form.get('email')
#     print(name, email)
#     return render_template('index1.html')

@app.route('/hello/<name>')
def hello(name):
  return render_template('hello.html', name=name)

@app.route('/submit', methods=['POST'])
def submit():
  name = request.form['name']
  return f'Hello, {name}'


@app.route('/<resource>/<out>/2222', methods=['GET'])
def get_resource(resource,out):
        try:
            sql = q[resource]
            print(sql)
            if out == 'json':
                data = curTojson(fbextract.get_data(sql))
                for row in data:
                    r = row['ACTION_COORD']
                    if len(r)>0:
                        m = mgrs.MGRS()
                        print(r)
                        d = m.toLatLon(r)
                        row['la'] = d[0]
                        row['lo'] = d[1]
                    else:
                        row['la'] = ''
                        row['lo'] = ''
                    print(row)
                now  = datetime.datetime.now()
                return   jsonify({now.strftime("%Y-%m-%d %H:%M:%S") : data})
            if out == 'csv':
                return curTocsv(fbextract.get_data(sql))
        except Exception as e:
            return jsonify({'error': str(e),'sql':sql})


@app.route('/get_lost/<serial>', methods=['GET'])
def docs_serial(serial):
    try:
        sql = q['get_lost'] % serial
        data = curTojson(fbextract.get_data(sql))
        return data
    except Exception as e:
        return jsonify({'error': str(e), 'sql': sql})
#################################
@app.route('/get_lost_items/<serial>/<p>', methods=['GET'])
def items_serial(serial,p):
    try:
        sql = str(q['get_lost_items']) #% serial
        sql = sql.replace('%s',serial)
        where =''
        #sql = sql.replace('%p',p)
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
##############################3


@app.route('/api/1/<endpoint>',defaults={'p': None}, methods=['GET'])
@app.route('/api/1/<endpoint>/<p>', methods=['GET'])
def gen_data_1(endpoint,p):
    try:
        if p:
            sql = get_sql(endpoint,p,1)
        else :
            sql = get_sql(endpoint, None,1)
        print(sql)
        result = curTojson(fbextract.get_data(sql))
        result.headers["Content-Type"] = "application/json; charset=utf-8"
        return result,200
    except Exception as e:
        return jsonify({'error': str(e), 'sql': sql}),200

@app.route('/api/2/<endpoint>', defaults={'p': None}, methods=['GET'])
@app.route('/api/2/<endpoint>/<p>', methods=['GET'])
def gen_data_2(endpoint, p):
    try:
        if p:
            sql = get_sql(endpoint, p,2)
        else:
            sql = get_sql(endpoint, None,2)
        print(sql)
        result = curTojson(fbextract.get_data(sql))
        result.headers["Content-Type"] = "application/json; charset=utf-8"
        return result, 200
    except Exception as e:
        return jsonify({'error': str(e), 'sql': sql}), 200

    #
    # @app.route('/products', defaults={'product_id': None})
    # @app.route('/products/<product_id>')
    # def show_product(product_id):
    #     if product_id:
    #     # code to show individual product
    #     else:
    # # code to show whole catalog


# @app.route('/<resource>/<id>', methods=['GET'])
# def get_resource_by_id_with_children(resource, id):
#     if resource in data:
#         for item in data[resource]:
#             if item['ID'] == int(id):
#                 # print(request.args.get('child'))
#                 if 'child' in request.args:
#                     child = request.args.get('child')
#                     if child in data:
#                         children = []
#                         for child_item in data[child]:
#                             if child_item['postId'] == int(id):
#                                 children.append(child_item)
#                         return jsonify(children)
#                     else:
#                         return jsonify({"error": f"{child} not found"}), 404
#                 else:
#                     return jsonify(item)
#         return jsonify({"error": f"{resource} not found"}), 404
#     else:
#         return jsonify({"error": f"{resource} not found"}), 404




# @app.route('/<resource>/<id>', methods=['PUT'])
# def update_resource(resource, id):
#     # first check if the id exists
#     needle = findIndexById(data[resource], int(id))
#     if needle is not None:
#         data[resource][needle] = request.json
#         with open('db.json', 'w') as f:
#             json.dump(data, f, indent=4)
#         return jsonify(data[resource][needle])
#     else:
#         return jsonify({"error": f"{resource} not found"}), 404

#
# @app.route('/<resource>/<id>', methods=['PATCH'])
# def patch_resource(resource, id):
#     # First, check if the ID exists
#     needle = findIndexById(data[resource], int(id))
#
#     if needle is not None:
#         updated_data = request.json
#         itemTobePatched = data[resource][needle]
#         for key in updated_data:
#             itemTobePatched[key] = updated_data[key]
#
#         data[resource][needle] = itemTobePatched
#
#         with open('db.json', 'w') as f:
#             json.dump(data, f, indent=4)
#
#         return jsonify(data[resource][needle])
#     else:
#         return jsonify({"error": f"{resource} not found"}), 404
#
#
# @app.route('/<resource>/<id>', methods=['DELETE'])
# def delete_resource(resource, id):
#     needle = findIndexById(data[resource], int(id))
#     if needle is not None:
#         del data[resource][needle]
#         with open('db.json', 'w') as f:
#             json.dump(data, f, indent=4)
#         return jsonify({"message": f"{resource} deleted"}), 200
#     else:
#         return jsonify({"error": f"{resource} not found"}), 404
#



if __name__ == "__main__":
    # use .env file to get port
    #app.run(port=os.getenv('PORT'), debug=False)
    http_server = WSGIServer(('192.168.10.9', int(os.getenv('PORT'))), app)
    http_server.serve_forever()