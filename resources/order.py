from flask import Blueprint
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Order, Product, OrderProduct, User
from app import db
from decimal import Decimal
from http import HTTPStatus

order_blueprint = Blueprint('order', __name__)
api = Api(order_blueprint)


class OrderCreationAPI(Resource):
    @jwt_required()
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('products', type=dict, action='append', required=True)
        data = parser.parse_args()

        user_id = get_jwt_identity()
        user = db.session.get(User, user_id)

        product_ids = [item['product_id'] for item in data['products']]
        quantities = {item['product_id']: item['quantity'] for item in data['products']}

        validation_error = Order.validate_products(product_ids, quantities)
        if validation_error:
            return validation_error

        total_amount = Decimal('0.00')
        new_order = Order(user=user, total_amount=total_amount)

        for item in data['products']:
            product = Product.query.get(item['product_id'])
            product.quantity_in_stock -= item['quantity']
            line_total = product.price * item['quantity']
            total_amount += line_total

            order_product = OrderProduct(order=new_order, product=product, quantity=item['quantity'])
            db.session.add(order_product)

        new_order.total_amount = total_amount
        db.session.commit()

        return {'message': 'Order placed successfully!', 'order_id': new_order.id}, HTTPStatus.CREATED


class UserOrderListAPI(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        orders = Order.query.filter_by(user_id=user_id).all()

        orders_list = []
        for order in orders:
            order_details = {
                'order_id': order.id,
                'total_amount': str(order.total_amount),
                'created_at': order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'products': [
                    {
                        'product_id': op.product.id,
                        'name': op.product.name,
                        'quantity': op.quantity,
                        'price': str(op.product.price)
                    }
                    for op in order.products
                ]
            }
            orders_list.append(order_details)

        return {'orders': orders_list}, HTTPStatus.OK


api.add_resource(OrderCreationAPI, '/')
api.add_resource(UserOrderListAPI, '/user')
