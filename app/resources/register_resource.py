from flask import jsonify, request
from flask_restful import Resource
# from app.models import db, User, Role
from flask import request, jsonify
from flask_restful import Resource
from app.models.users import User, db
from app.models.role import Role

# Resource for user registration
class RegisterResource(Resource):
    def post(self):
        data = request.get_json()

        if 'username' not in data or 'password' not in data or 'email' not in data or 'roles' not in data:
            return jsonify({'error': 'Username, password, email, and roles are required'}), 400

        new_user = User(username=data['username'], email=data['email'])
        new_user.set_password(data['password'])

        for role_name in data['roles']:
            role = Role.query.filter_by(name=role_name).first()
            if role:
                new_user.roles.append(role)

        db.session.add(new_user)
        db.session.commit()

        return jsonify({'message': 'User registered successfully'}), 201