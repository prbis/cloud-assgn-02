from flask import Flask, request, jsonify
from pymongo import MongoClient
import pika
import json
import time
from bson.objectid import ObjectId
from multiprocessing import Process



app = Flask(__name__)

# MongoDB Configuration
MONGO_URI = 'mongodb+srv://proddutkumarbiswas:p123456@cluster0.29upj.mongodb.net/order_db?retryWrites=true&w=majority'
client = MongoClient(MONGO_URI)
db = client['order_db']
orders_collection = db['orders']

# RabbitMQ Connection with Retry Mechanism
def connect_to_rabbitmq():
    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host='rabbitmq', port=5672)
            )
            print("Connected to RabbitMQ!")
            return connection
        except pika.exceptions.AMQPConnectionError:
            print("RabbitMQ not ready. Retrying in 5 seconds...")
            time.sleep(5)

# RabbitMQ Consumer Logic
def start_rabbitmq_consumer():
    connection = connect_to_rabbitmq()
    channel = connection.channel()
    channel.queue_declare(queue='user-updates')

    def callback(ch, method, properties, body):
        print("Received User Update Event")
        event = json.loads(body)
        changes = event['changes']
        orders_collection.update_many({'email': changes.get('email')}, {'$set': changes})
        print("Orders updated based on user changes.")

    channel.basic_consume(queue='user-updates', on_message_callback=callback, auto_ack=True)
    print("Listening for RabbitMQ messages...")
    channel.start_consuming()

# Flask Routes for Order Service
@app.route('/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    required_fields = ['items', 'email', 'delivery_address']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing fields'}), 400

    order = {
        'items': data['items'],
        'email': data['email'],
        'delivery_address': data['delivery_address'],
        'status': 'under process'
    }
    result = orders_collection.insert_one(order)
    order['_id'] = str(result.inserted_id)
    return jsonify(order), 201

@app.route('/orders', methods=['GET'])
def get_orders():
    status = request.args.get('status')
    query = {}
    if status:
        query['status'] = status

    orders = list(orders_collection.find(query))
    for order in orders:
        order['_id'] = str(order['_id'])

    return jsonify(orders), 200

@app.route('/orders/<order_id>', methods=['PUT'])
def update_order(order_id):
    data = request.get_json()
    update_fields = {}
    if 'status' in data:
        update_fields['status'] = data['status']
    if 'email' in data:
        update_fields['email'] = data['email']
    if 'delivery_address' in data:
        update_fields['delivery_address'] = data['delivery_address']

    if not update_fields:
        return jsonify({'error': 'No fields to update'}), 400

    result = orders_collection.update_one({'_id': ObjectId(order_id)}, {'$set': update_fields})
    if result.matched_count == 0:
        return jsonify({'error': 'Order not found'}), 404

    order = orders_collection.find_one({'_id': ObjectId(order_id)})
    order['_id'] = str(order['_id'])
    return jsonify(order), 200

# Main Entry Point
if __name__ == '__main__':
    # Start RabbitMQ consumer in a separate process
    consumer_process = Process(target=start_rabbitmq_consumer)
    consumer_process.start()

    # Start Flask app
    print("Starting Flask app...")
    app.run(host='0.0.0.0', port=8080, debug=False)  # Turn off debug mode for production

    # Ensure RabbitMQ consumer stops when Flask stops
    consumer_process.join()

