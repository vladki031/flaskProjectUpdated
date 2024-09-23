from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
from models import db
from config import Config
from resources.user import user_blueprint
from resources.product import product_blueprint
from resources.order import order_blueprint

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
jwt = JWTManager(app)

app.register_blueprint(user_blueprint, url_prefix='/api/users')
app.register_blueprint(product_blueprint, url_prefix='/api/products')
app.register_blueprint(order_blueprint, url_prefix='/api/orders')

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
