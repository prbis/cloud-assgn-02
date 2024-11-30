from bson import ObjectId
from flask import Flask, request, jsonify
from pymongo import MongoClient
import pika
import json

app = Flask(__name__)
MONGO_URI = 'mongodb+srv://proddutkumarbiswas:p123456@cluster0.29upj.mongodb.net/user_db?retryWrites=true&w=majority'
client = MongoClient(MONGO_URI)
db = client['user_db']
users_collection = db['users']

def publish_event(event):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue='user-updates')
    channel.basic_publish(exchange='', routing_key='user-updates', body=json.dumps(event))
    connection.close()

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    required_fields = ['account_id', 'email', 'delivery_address']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing fields'}), 400
    
    user = {
        'account_id': data['account_id'],
        'email': data['email'],
        'delivery_address': data['delivery_address']
    }
    result = users_collection.insert_one(user)
    user['_id'] = str(result.inserted_id)
    return jsonify(user), 201

@app.route('/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    if not user_id or not ObjectId.is_valid(user_id):
        return jsonify({'error': 'Invalid user_id provided'}), 400  # Return a 400 Bad Request

    data = request.get_json()
    update_fields = {}
    if 'email' in data:
        update_fields['email'] = data['email']
    if 'delivery_address' in data:
        update_fields['delivery_address'] = data['delivery_address']

    if not update_fields:
        return jsonify({'error': 'No fields to update'}), 400

    result = users_collection.update_one({'_id': ObjectId(user_id)}, {'$set': update_fields})
    if result.matched_count == 0:
        return jsonify({'error': 'User not found'}), 404

    user = users_collection.find_one({'_id': ObjectId(user_id)})
    user['_id'] = str(user['_id'])
    return jsonify(user), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
