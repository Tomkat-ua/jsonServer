
#-----------------------------------------------------------------------------------------
import datetime, logging, sys,os,csv,fbextract,json
from dotenv import load_dotenv
from gevent.pywsgi import WSGIServer
from io import StringIO
from flask import Flask, jsonify#,render_template
import mgrs
# from json import load as jsonLoad
# from json import dumps as jsonDumps


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


print(f"Running JSON-SERVER on port {os.getenv('PORT')}")


with open("qrys.json", "r") as f:
    q = json.load(f)
# q = {
#     "losses":"select  * from v_loses",
#     "analitic":"select  * from V_SKLAD_ANALITIC_2",
#     "loss-cost":"losses.up_losses_cost",
#     "arrived": "select * from VIEW_PRIHOD"
# }



def curTojson(cur):
    columns = [column[0] for column in cur.description]
    return  [dict(zip(columns, row)) for row in cur.fetchall()]

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



@app.route('/<resource>/<out>', methods=['GET'])
def get_resource(resource,out):
        try:
            sql = q[resource]
            # sql =  'select * from monitoring.GET_DETDOC_SERIALS(:doc_id,:tov_id,0,:doc_type_id)'
            # sql = sql.replace(':doc_id','300000355')
            # sql = sql.replace(':tov_id','300000014')
            # sql = sql.replace(':doc_type_id','10')
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


# @app.route('/<resource>', methods=['POST'])
# def create_resource(resource):
#     data[resource].append(request.json)
#     with open('db.json', 'w') as f:
#         json.dump(data, f, indent=4)
#     return jsonify(data[resource]), 201

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