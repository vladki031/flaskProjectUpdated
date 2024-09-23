from flask import Blueprint
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import create_access_token
from models import User
from app import db
from http import HTTPStatus
import re

user_blueprint = Blueprint('user', __name__)
api = Api(user_blueprint)

def is_valid_user_data(username, password):
    if len(username) < 3:
        return {'message': 'Username must be at least 3 characters long.'}, HTTPStatus.BAD_REQUEST
    if len(password) < 6:
        return {'message': 'Password must be at least 6 characters long.'}, HTTPStatus.BAD_REQUEST
    if not re.match(r'^[a-zA-Z0-9]+$', username):
        return {'message': 'Username can only contain letters and numbers.'}, HTTPStatus.BAD_REQUEST
    return None

class UserRegistration(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', required=True, help='Username is required.')
        parser.add_argument('password', required=True, help='Password is required.')
        data = parser.parse_args()

        username = data['username']
        password = data['password']

        validation_error = is_valid_user_data(username, password)
        if validation_error:
            return validation_error

        if User.query.filter_by(username=username).first():
            return {'message': 'Username is already taken.'}, HTTPStatus.BAD_REQUEST

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        return {'message': 'User created successfully!'}, HTTPStatus.CREATED

class UserLogin(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', required=True)
        parser.add_argument('password', required=True)
        data = parser.parse_args()

        username = data['username']
        password = data['password']

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            access_token = create_access_token(identity=user.id)
            return {'access_token': access_token}, HTTPStatus.OK
        return {'message': 'Invalid credentials'}, HTTPStatus.UNAUTHORIZED

api.add_resource(UserRegistration, '/register')
api.add_resource(UserLogin, '/login')
