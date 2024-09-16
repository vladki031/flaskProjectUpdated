from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from models import db, User, Product, Order, OrderProduct
from resources.user import UserRegistration, UserLogin
from resources.product import ProductListAPI, ProductDetailAPI
from resources.order import OrderCreationAPI, UserOrderListAPI

app = Flask(__name__)
api = Api(app)

app.config['SECRET_KEY'] = 'vlad2003'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'vlad2003'

db.init_app(app)
jwt = JWTManager(app)

api.add_resource(UserRegistration, '/api/register', methods=['POST'])
api.add_resource(UserLogin, '/api/login', methods=['POST'])
api.add_resource(ProductListAPI, '/api/products', methods=['GET'])
api.add_resource(ProductDetailAPI, '/api/products/<int:id>', methods=['GET'])
api.add_resource(OrderCreationAPI, '/api/orders', methods=['POST'])
api.add_resource(UserOrderListAPI, '/api/user/orders', methods=['GET'])

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
