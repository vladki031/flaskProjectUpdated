from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    orders = db.relationship('Order', back_populates='user', lazy='dynamic')

    def __init__(self, username, password):
        self.username = username
        self.set_password(password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    quantity_in_stock = db.Column(db.Integer, default=0, nullable=False)

    orders = db.relationship('OrderProduct', back_populates='product', lazy='dynamic')

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': str(self.price),
            'quantity_in_stock': self.quantity_in_stock
        }


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    user = db.relationship('User', back_populates='orders')
    products = db.relationship('OrderProduct', back_populates='order', lazy='dynamic')

    @staticmethod
    def validate_products(product_ids, quantities):
        products = Product.query.filter(Product.id.in_(product_ids)).all()
        product_dict = {product.id: product for product in products}

        for product_id, quantity in quantities.items():
            if product_id not in product_dict:
                return {'message': f'Product {product_id} not found.'}
            if product_dict[product_id].quantity_in_stock < quantity:
                return {'message': f'Insufficient stock for product {product_dict[product_id].name}.'}
        return None


class OrderProduct(db.Model):
    __tablename__ = 'order_products'

    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)

    order = db.relationship('Order', back_populates='products')
    product = db.relationship('Product', back_populates='orders')
