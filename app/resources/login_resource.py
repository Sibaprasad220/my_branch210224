from flask import Flask, jsonify, request
from flask_restful import Resource, reqparse
from app.models.users import User
from flask_jwt import JWT

app = Flask(__name__)
def authenticate(username, password):
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify(({'message': 'Usernot found '}), 404)
    return user

def identity(payload):
    user_id = payload['identity']
    return User.query.get(user_id)


jwt = JWT(app, authenticate, identity)
class LoginResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True, help='Username is required')
        parser.add_argument('password', type=str, required=True, help='Password is required')
        data = parser.parse_args()

        user = User.query.filter_by(username=data['username']).first()

        if user and user.check_password(data['password']):
            access_token = jwt.jwt_encode_callback({'identity': user.id})
            return jsonify({'access_token': access_token.decode('utf-8')})
        else:
            return jsonify({'error': 'Invalid username or password'}), 401