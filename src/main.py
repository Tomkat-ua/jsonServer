
#-----------------------------------------------------------------------------------------
from flask import Flask, jsonify, request
import datetime
import logging
import sys,os
from flask.logging import default_handler
from dotenv import load_dotenv
from gevent.pywsgi import WSGIServer
import fbextract
import csv
from io import StringIO

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

# try:
#     # with open('db.json', 'r',encoding='utf-8') as f: data = json.load(f)
#     # data = fbextract.get_data()
#     # for key in data:
#     #     print(key)
#     #     print(f"\n\033[1m\033[4m{key.upper()}\033[00m")
#     #     # GET with blue
#     #     print(f"{printColor('GET', '34')} http://192.168.10.9:{os.getenv('PORT')}/{key}")
#     #     # POST with green
#     #     print(f"{printColor('GET', '34')} /{key}/<id>")
#     #     print(f"{printColor('POST', '32')} /{key}")
#     #     # PUT with yellow
#     #     print(f"{printColor('PUT', '33')} /{key}")
#     #     # print delete with red
#     #     print(f"{printColor('DELETE', '31')} /{key}")
#
# except FileNotFoundError:
#     print("json data not found")
#     exit()

q = {
    "losses":"select  * from v_loses",
    "analitic":"select  * from V_SKLAD_ANALITIC_2"
}


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

    # return column_names
    # Write result to file.
    # with open(csv_file_path, 'w', newline='') as csvfile:
    #     csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    #     for row in result:
    #         csvwriter.writerow(row)
    # else:
    #     sys.exit("No rows found for query: {}".format(sql))
    #

@app.route('/<resource>/<out>', methods=['GET'])
def get_resource(resource,out):
        try:
            # if resource == 'losses':
            #     sql = ('select  * from v_loses  ')
            #     data = fbextract.get_data(sql)
            #     now = datetime.datetime.now()
            #     if out == 'json':
            #         # print(now.strftime("%Y-%m-%d %H:%M:%S"))
            #         # return data
            #         return jsonify({now.strftime("%Y-%m-%d %H:%M:%S") : data})
            #     if out == 'csv':
            #         myFile = csv.writer(data)
            #         myFile.writerows(rows)
            #         print (data)

            now = datetime.datetime.now()
            if out == 'json':
                data = curTojson(fbextract.get_data(q[resource]))
                return   jsonify({now.strftime("%Y-%m-%d %H:%M:%S") : data})

            if out == 'csv':
                return curTocsv(fbextract.get_data(q[resource] ))

        except Exception as e:
            print(e)
            return (e)
            # exit()


# @app.route('/<resource>', methods=['GET'])
# def get_resource(resource):
#     if resource in data:
#         return jsonify(data[resource])
#     else:
#         return jsonify({"error": "Resource not found"}), 404

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