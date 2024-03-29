from flask import Flask, request
import random

app = Flask(__name__)

@app.route('/number/', methods=['GET'])
def get_number():
    param = request.args.get('param', type=float)
    random_number = random.random()
    operation = 'multiply'
    result = random_number * param
    return {"result": result, "operation": operation}

@app.route('/number/', methods=['POST'])
def post_number():
    json_data = request.json
    json_param = json_data.get('jsonParam', 0)
    random_number = random.random()
    operations = ['add', 'subtract', 'multiply', 'divide']
    operation = random.choice(operations)
    if operation == 'add':
        result = random_number + json_param
    elif operation == 'subtract':
        result = random_number - json_param
    elif operation == 'multiply':
        result = random_number * json_param
    elif operation == 'divide':
        result = random_number / json_param
    return {"result": result, "operation": operation}

@app.route('/number/', methods=['DELETE'])
def delete_number():
    random_number = random.random()
    operations = ['add', 'subtract', 'multiply', 'divide']
    operation = random.choice(operations)
    return {"result": random_number, "operation": operation}


if __name__ == '__main__':
    app.run(debug=True)

