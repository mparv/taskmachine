import datetime
import uuid
import io
import csv
import psutil
import os
import sys
import time
import json
import queue
import socket
import threading
import shutil
import psutil
import requests
from cachetools import TTLCache, cached

cache = TTLCache(maxsize=100000, ttl=60)
q_global = queue.Queue(maxsize=1000)



from collections import defaultdict
from flask import Flask, jsonify, request, Response
from flask_cors import CORS

from storage.line_db import create_line_db_routes
from scraper.web_scraper import get_h3_html
from serve_static import serve_public_pages
from tm_utils import Utils, ConfigUtils
from tm_logging.tm_logging import TmLogging
from relay import create_investment_routes

from flask_swagger_ui import get_swaggerui_blueprint

if len(sys.argv) != 3:
    print("Supply command line args, containing config file\n" + 
        "python start.py <config.cfg> <data_dir>")
    exit(1)

app = Flask(__name__, static_folder='static')
app.jinja_env.variable_start_string = '{%='
app.jinja_env.variable_end_string = '=%}'
CORS(app, resources={r"/endpoint": {"origins": "*"}})

tasks = {}
total_tasks = {}
paras = defaultdict(list)
archieved = set()
tokens = {}
platform = {}
video_map = {}
tm_logger = TmLogging()

config_util = ConfigUtils(sys.argv[1], tm_logger)
data_dir = sys.argv[2]
os.environ["TM_THRIFT_DB"] = config_util.get_db_models()
import file_client

SWAGGER_URL = "/swagger"
API_URL = "/static/swagger.json"
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL,
    config= {
        'app_name': "My Flask API"
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

@app.route("/endpoint", methods=["POST", "OPTIONS"])
def endpoint_extension():
    if request.method == 'OPTIONS':
        return '', 200

    data = request.get_json()
    date_now = str(datetime.datetime.now()).replace(":", "_").replace(".", "_")
    data['harbor-extension'] = date_now + " " + data['text'].replace(",", "__COMMA__")\
        .replace(":", "__COLON__").replace("\n", "__NEWLINE__")
    del data['text']
    paras['harbor-extension'].append(f"{data['harbor-extension']}")

    save_para('harbor-extension', data)

    return {"status": "success"}, 200

@app.route('/platform/systemInfo')
def platform_system_info():
    uptime = int(time.time()) - int(platform['start_time'])
    uptime_h = uptime / (60*60)
    html_out_str = ""

    html_out_str += f"<h2>Uptime: {round(uptime_h, 3)} hour(s) </h2>"
    html_out_str += "<h2>Disk usage</h2>"

    for disk_label in ['C:', 'D:', 'E:', 'F:', 'G:', 'H:']:
        try:
            usage = shutil.disk_usage(disk_label)
            html_out_str += f"<h3>{disk_label} Free {round(usage.free/(1024**3), 1)}," +\
             f" %free {round(usage.free*100/usage.total, 1)}</h3>"
        except Exception:
            pass
    html_out_str += f"<h2>CPU Stats</h2>"
    html_out_str += f"<h3>{psutil.cpu_percent(percpu=True, interval=1)}</h3>"
    html_out_str += f"<h2>Memory Stats</h2>"
    html_out_str += f"<h3>{round(psutil.virtual_memory().available/(1024**2), 2)} MB</h3>"
    
    return html_out_str,200

@app.route("/web")
def web():
    headings_3 = get_h3_html(config_util.get_scrape_urls())
    raw_html = "<ol>"
    for item in headings_3:
        raw_html = raw_html + "<li>" + item + "</li>" + "<br />"
    raw_html = raw_html + "</ol>"

    return raw_html, 200

@app.route('/tokenop/v1/', methods=['GET'])
def get_tokens():
    global tokens
    resp = ""
    for earned_for, amount in tokens.items():
        if earned_for == '__EXPENDED__':
            continue

        resp += "" + earned_for + " - " + str(amount) + " <br />"

    return resp, 200

@app.route('/tokenop/v1/add', methods=['POST'])
def tokens_add():
    global tokens
    data = request.get_json()
    data['earned_for'] = data['earned_for'].replace(",", "").replace(":", "")
    if data['earned_on'] == "":
        data['earned_on'] = str(datetime.datetime.now()).split(" ")[0]
    save_token(data)
    if data['earned_for'] in tokens:
        tokens[data['earned_for']] += int(data['amount'])
    else:
        tokens[data['earned_for']] = int(data['amount'])

    return {"status": "ok"}, 200


@app.route("/tokenop/v1/expend/<string:amount>")
def tokens_expend(amount):
    global tokens
    data = {
        'earned_for': '__EXPENDED__',
        'earned_on': str(datetime.datetime.now()).split(" ")[0],
        'amount': -int(amount)
    }
    save_token(data)
    tokens.append(data)
    return {"status": "ok"}, 200

@app.route('/notes/v1/search', methods=['POST'])
def notes_search():
    search_ = request.get_json()['queryP']
    book = request.get_json()['book'] if request.get_json()['book'] else 'dummykey' 

    resp = ""
    for line in paras.get(book, []):
        line_lower = line.lower()
        if search_.lower() in line_lower:
            resp = resp + (line.replace("__NEWLINE__", "\n")\
                .replace("__COLON__", ":").replace("__COMMA__", ",") + "\n\n")
    
    return resp, 200

@cached(cache)
def get_books_helper():
    return get_books_from_file_client("pzk", "notes")

@app.route("/notes/v1/store/bookList")
def get_books_list():
    books = get_books_helper()
    if books is None:
        return str("NO BOOKS FOUND"), 200
        
    data = ["<li>" + x.fields['filename'].split(".")[0] + "</li>" \
        for x in get_books_from_file_client("pzk", "notes")]

    data = "<ol>" + "".join(data) + "</ol>"
    return str(data), 200



def get_books_from_file_client(tenant, database):
    return file_client.get_books(tenant, database)

@app.route("/notes/v1/store", methods=['POST'])
def notes_store():
    data = request.get_json()
    if data['book'] == '':
        data['book'] = 'dummykey'
    data['book'] = data['book'].lower()
    data['paragraph'] = data['paragraph'].replace(":", "__COLON__")\
        .replace(",", "__COMMA__").replace("\n", "__NEWLINE__")

    save_data = {data['book']: data['paragraph']}
    save_para(data['book'], save_data)
    paras[data['book']].append(data['paragraph'])

    return {"status": "ok"}, 200

@app.route("/notes/v1/store/<string:book>", methods=['DELETE'])
def delete_book(book):
    global paras

    delete_para(book)
    if book in paras:
        del paras[book]
    
    return {"status": "ok"}, 200

def delete_para(book):
    file_client.delete_data("pzk", "notes", book)

def save_para(book, data):
    q_global.put((file_client.append_data, ["pzk", "notes", book, data]))
    #file_client.append_data("pzk", "notes", book, data)
    
def read_para():
    tm_logger.info("Loading notes data")
    start_time = int(time.time())
    resp = defaultdict(list)
    books = [x.fields['filename'] for x in file_client.get_books("pzk", "notes")]
    for book_ in books:
        book = book_.split(".")[0]
        for x in file_client.read_data("pzk", "notes", book):
            data = x.fields
            try:
                item1, item2 = data.popitem()
            except KeyError:
                continue
            resp[book].append(item2)

    tm_logger.info("Loaded {} notes data in {} sec(s)".format(len(resp), (int(time.time()) - start_time)))
    return resp
    
@app.route("/utils/v1/processes")
def processes():
    top_procs = []

    for proc in psutil.process_iter(['pid', 'name', 'exe', 'memory_info', 'cpu_percent']):
        try:
            pid = proc.info['pid']
            name = proc.info['name'] or "Unknown"
            exe = proc.info['exe'] or "Unknown"
            memory_info = proc.info['memory_info']
            cpu_percent = proc.info['cpu_percent']

            memory_usage = memory_info.rss / (1024 * 1024)  # Convert to MB
            if memory_usage > 100 or cpu_percent > 1:
                top_procs.append({
                    'pid': pid,
                    'name': name,
                    'path': exe,
                    'memory_usage': memory_usage,
                    'cpu_usage': cpu_percent
                })

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    return top_procs, 200

@app.route("/utils/v1/network_usage/<string:date_>")
@app.route("/utils/v1/network_usage/", defaults={'date_': None})
def network_usage(date_):
    is_checked = request.args.get('zeroSix')
    is_checked = is_checked == 'true'
    total_usage = 0
    if not date_:
        date_ = str(datetime.datetime.now()).split(" ")[0]
    
    with open(data_dir) as fw:
        for line in fw.readlines():
            # Format: 2024-11-20 06:11:02.822893 - 4.1791534423828125
            dt_, usage = line.split(" - ")
            day_ = dt_.split(" ")[0]
            hr_ = int(dt_.split(" ")[1].split(":")[0])
            if day_ == date_:
                total_usage += float(usage)

                #if is_checked:
                #    if hr_ in [0, 1, 2, 3, 4, 5]:
                #        total_usage += float(usage)
                #elif hr_ not in [0, 1, 2, 3, 4, 5]:
                #    total_usage += float(usage)

    gib_data = int(total_usage/1000)
    try:
        mib_data = int(str(int(total_usage))[-3:-2])
    except Exception:
        mib_data = 0

    return "Usage of network on {}: {}.{} GB".format(date_, gib_data, mib_data), 200

@app.route('/tm/v1/tasks/<string:id>', methods=['GET'])
def get_task_by_id(id):
    task = tasks.get(id)
    if task:
        return jsonify(task), 200
    else:
        return jsonify({"error": "Task not found"}), 404

@app.route('/tm/v1/tasks/', methods=['POST'])
def create_task():
    task_data = request.get_json()
    task_id = str(uuid.uuid4())
    task_data['is_archived'] = False
    
    tasks[task_id] = task_data
    task_data['id'] = task_id
    task_data['description'] = task_data['description'].replace(",", "").replace(":", "")
    task_data['title'] = task_data['title'].replace(",", "").replace(":", "")
    task_data['created_on'] = str(datetime.datetime.now()).split(" ")[0]
    task_data['project'] = task_data['project'].replace(",", "").replace(":", "")

    save_entry(task_data)
    return jsonify(task_data), 201

@app.route('/tm/v1/tasks/search', methods=['POST'])
def search_task():
    task_data = request.get_json()
    task_data['is_archived'] = "True" if task_data['is_archived'] else "False"
    json_arr = []

    check_tasks = tasks
    if task_data['is_archived'] == "True":
        check_tasks = total_tasks

    for task in list(check_tasks.values()):
        if task.get('due_date') == task_data['due_date'] or task_data['due_date'] == '':
            if task.get('priority') == task_data['priority'] or task_data['priority'] == 'ALL':
                if task_data['project'] == '' or task.get('project') == task_data['project']:
                    json_arr.append(task)

    return jsonify(json_arr), 200

@app.route("/tm/v1/tasks/projects")
def project_get():
    projects = []
    project_dict = defaultdict(int)

    for task in list(tasks.values()):
        if task.get('project'):
            project_dict[task['project']] += 1

    for key, value in project_dict.items():
        projects.append({
            'name': key,
            'tasks': value
        })
    projects.append({'name': 'pre19Oct24', 'tasks': -1})

    return jsonify(projects), 200

@app.route('/tm/v1/tasks/archive/<string:id>', methods=['DELETE'])
def archive_task(id):

    task_id = id
    if task_id in tasks:
        task_data = tasks[task_id]
        task_data['is_archived'] = True
        save_entry(task_data)
        del tasks[task_id]
    else:
        return "Task {} not present".format(task_id), 400
        
    return "", 200


def save_token(data):
    string_dict = {str(k): str(v) for k, v in data.items()}
    file_client.append_data('pzk', 'ofc', 'tokens', string_dict)

def read_tokens():
    tm_logger.info("Loading tokens data")
    rsp = file_client.read_data('pzk', 'ofc', 'tokens')
    return [x.fields for x in rsp]

def save_entry(data):
    string_dict = {str(k): str(v) for k, v in data.items()}
    q_global.put((file_client.append_data, ["pzk", "ofc", "confluence", string_dict]))
    #file_client.append_data("pzk", "ofc", "confluence", string_dict)

def read_data():
    tm_logger.info("Loading tasks data")
    start_time = int(time.time())
    out_dict = {}
    rsp = file_client.read_data("pzk", "ofc", "confluence")
    for data_dict_ in rsp:
        data_dict = data_dict_.fields
        if data_dict['is_archived'] in [True, 'true', "True"]:
            archieved.add(data_dict['id'])

        out_dict[data_dict['id']] = data_dict
        total_tasks[data_dict['id']] = data_dict

    for archived_entry_id in archieved:
        if archived_entry_id in out_dict:
            del out_dict[archived_entry_id]

    tm_logger.info("Loaded {} entries of task data in {} sec(s)".format(len(rsp), (int(time.time()) - start_time)))

    return out_dict

def wait_for_db():
    host = "localhost"
    port = 5010

    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.settimeout(5)
                s.connect((host, port))
                break
            except (socket.timeout, socket.error):
                tm_logger.error("ERR problem connecting to database")
                time.sleep(5)


@app.route('/video/PMovie/<fileid>')
def pmovie(fileid):
    path = None
    if fileid in video_map:
        path = video_map[fileid]['filepath']

    if path is None:
        return "Video File not found", 404

    range_header = request.headers.get('Range', None)
    if not range_header:
        return send_file(path, mimetype='video/mp4')

    byte_range = range_header.replace('bytes=', '').split('-')
    start = int(byte_range[0])
    end = int(byte_range[1]) if byte_range[1] else None

    with open(path, 'rb') as f:
        f.seek(start)
        data = f.read(end - start + 1 if end else None)

    rv = Response(data, status=206, mimetype='video/mp4')
    rv.headers.add('Content-Range', f'bytes {start}-{end or start + len(data) - 1}/{os.path.getsize(path)}')
    return rv

@app.route("/reloadVideos")
def reloadVideos():
    # wrong design TODO
    resp = requests.get("http://localhost:6666/getRandomVideo")
    
    json_arr = []
    for video in resp.json()["video"]:
        md5 = Utils.get_md5sum(video['filename'])
        video_map[md5] = video
        json_arr.append({
            "filename": video["filename"],
            "filepath": md5
        })

    return json_arr, 200

def background_task():
    tm_logger.info("Inside background task")
    while True:
        method, args = q_global.get()
        method(*args)
        time.sleep(2)
        tm_logger.info(f"Task complete {method}: {args}")
        q_global.task_done()


if __name__ == "__main__":
    # custom_attributes[], group_id"", tags"", activity_logs[], notification_endpoints[]
    # pip install flask-swagger-ui

    th1 = threading.Thread(target=background_task, daemon=True)
    th1.start()

    wait_for_db()
    tasks = read_data()
    paras = read_para()

    tokens_ = read_tokens()
    for token in tokens_:
        if Utils.cmp_dates('2024-11-07', token['earned_on']):
            continue

        if token['earned_for'] in tokens:
            tokens[token['earned_for']] += int(token['amount'])
        else:
            tokens[token['earned_for']] = int(token['amount'])

    create_line_db_routes(app, file_client)
    create_investment_routes(app)
    serve_public_pages(app)
    
    platform['start_time'] = time.time()

    app.run(ssl_context=(config_util.get_cert_location(), config_util.get_key_location()))
