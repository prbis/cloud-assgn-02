from flask import Flask, request, Response
import requests
import json
import random

app = Flask(__name__)

# Service Base URLs
#USER_SERVICE_V1_URL = 'http://user_service_v1:5001'
#USER_SERVICE_V2_URL = 'http://user_service_v2:5003'
#ORDER_SERVICE_URL = 'http://order_service:5002'

# Service Base URLs
USER_SERVICE_V1_URL = 'https://userservice01-806117749861.us-central1.run.app'
USER_SERVICE_V2_URL = 'https://userservice02-806117749861.us-central1.run.app'
ORDER_SERVICE_URL = 'https://orderservice-806117749861.us-central1.run.app'

# Load configuration
with open('config.json') as f:
    config = json.load(f)

P = config.get('P', 50)  # Default to 50%

@app.route('/users', methods=['POST', 'PUT'])
@app.route('/users/<user_id>', methods=['PUT'])
def users_proxy(user_id=None):
    # Strangler pattern: Route based on P
    target_service = USER_SERVICE_V2_URL if random.randint(1, 100) > P else USER_SERVICE_V1_URL

    if request.method == 'POST':
        url = f"{target_service}/users"
        response = requests.post(url, json=request.get_json())
    elif request.method == 'PUT':
        if user_id:
            url = f"{target_service}/users/{user_id}"
            response = requests.put(url, json=request.get_json())
        else:
            return Response(status=501)
    else:
        return Response(status=405)

    return Response(response.content, status=response.status_code, content_type=response.headers['Content-Type'])

@app.route('/orders', methods=['POST', 'PUT'])
@app.route('/orders/<order_id>', methods=['PUT'])
def orders_proxy(order_id=None):
    if request.method == 'POST':
        url = f"{ORDER_SERVICE_URL}/orders"
        response = requests.post(url, json=request.get_json())
    elif request.method == 'PUT':
        if order_id:
            url = f"{ORDER_SERVICE_URL}/orders/{order_id}"
            response = requests.put(url, json=request.get_json())
        else:
            return Response(status=501)
    else:
        return Response(status=405)

    return Response(response.content, status=response.status_code, content_type=response.headers['Content-Type'])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
