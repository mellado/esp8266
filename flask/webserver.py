from datetime import datetime, timedelta
import json
from flask import Flask
from flask import request, jsonify

BEDROOM_PATH_LOG = "/tmp/bedroom.log"
app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello world'

@app.route('/dashboard')
def dashboard():
    pass

def get_near_future_datetime():
    result = datetime.now() + timedelta(minutes = 10)
    return result

@app.route('/get_data')
def send_data():
    from_datetime = request.args.get('from_datetime')
    to_datetime = request.args.get('to_datetime', default=get_near_future_datetime())
    print("from %s, to %s", (from_datetime, to_datetime))
    raw = open(BEDROOM_PATH_LOG).read()
    raw = raw.replace('}',"},\n")
    raw = raw[:-2]
    raw = "[\n" + raw + "\n]"
    # data = json.load(open(BEDROOM_PATH_LOG))
    data = json.loads(raw)
    data = [i for i in data if i.get("time") >= from_datetime]
    data = [i for i in data if i.get("time") <= to_datetime.strftime("%Y-%m-%d %H:%M:%S")]
    raw = "%s - %s<br>%s - %s<br><pre>%s</pre>"% (from_datetime, to_datetime, data[0].get("time"), data[-1].get("time"), data)
    return raw

@app.route('/save_data', methods=['POST'])
def save_data():
    error = None
    result = {'success':'ok'}
    content = request.get_json(silent=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    f = open(BEDROOM_PATH_LOG, "a")
    line = {'time': timestamp, 'temperature':content['temperature'],
            'humidity':content['humidity']}
    json.dump(line, f)
    f.close()

    return jsonify(**result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
