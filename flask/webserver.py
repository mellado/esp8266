from datetime import datetime
import json
from flask import Flask
from flask import request, jsonify
from xively_interface import publish

BEDROOM_PATH_LOG = "/home/osmc/esp8266/flask/bedroom.log"
app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello world'

@app.route('/save_data', methods=['POST'])
def save_data():
    error = None
    result = {'success':'ok'}
    content = request.get_json(silent=True)
    print(content)
    print(content['temperature'])
    print(content['humidity'])
    publish("humidity", "dormitorio", content['humidity'])
    publish("temperature", "dormitorio", content['temperature'])
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    f = open(BEDROOM_PATH_LOG, "a")
    line = {'time': timestamp, 'temperature':content['temperature'],
            'humidity':content['humidity']}
    json.dump(line, f)
    f.close()

    return jsonify(**result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
