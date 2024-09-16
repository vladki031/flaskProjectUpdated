from flask_restful import Resource, reqparse
from models import User
from app import db
from flask_jwt_extended import create_access_token

class UserRegistration(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', required=True, help='Username is required and cannot be empty.')
        parser.add_argument('password', required=True, help='Password is required and cannot be empty.')
        data = parser.parse_args()

        if len(data['username']) < 3:
            return {'message': 'Username must be at least 3 characters long.', 'status_code': 400}, 400
        if len(data['password']) < 6:
            return {'message': 'Password must be at least 6 characters long.', 'status_code': 400}, 400

        if User.query.filter_by(username=data['username']).first():
            return {'message': 'Username is already taken. Please choose a different one.', 'status_code': 400}, 400

        new_user = User(username=data['username'], password=data['password'])
        db.session.add(new_user)
        db.session.commit()

        return {'message': 'User created successfully!', 'status_code': 201}, 201


class UserLogin(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', required=True, help='Username cannot be blank!')
        parser.add_argument('password', required=True, help='Password cannot be blank!')
        data = parser.parse_args()

        user = User.query.filter_by(username=data['username']).first()

        if user and user.check_password(data['password']):
            access_token = create_access_token(identity=user.id)
            return {'access_token': access_token}, 200
        else:
            return {'message': 'Invalid credentials'}, 401
