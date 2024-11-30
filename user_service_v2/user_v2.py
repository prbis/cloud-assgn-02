from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/users', methods=['POST'])
def create_user_v2():
    return jsonify({'message': 'User created (v2)'}), 201

@app.route('/users/<user_id>', methods=['PUT'])
def update_user_v2(user_id):
    return jsonify({'message': 'User updated (v2)'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
