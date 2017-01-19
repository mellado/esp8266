from flask import Flask
from flask import request, jsonify
from xively_interface import publish

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
    return jsonify(**result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
