from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Order, Product, OrderProduct, User
from app import db
from decimal import Decimal


class OrderCreationAPI(Resource):
    @jwt_required()
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('products', type=dict, action='append', required=True,
                            help='Products with quantities are required')
        data = parser.parse_args()

        user_id = get_jwt_identity()
        user = db.session.get(User, user_id)

        if not data['products']:
            return {'message': 'You need to provide a list of products to order.', 'status_code': 400}, 400

        product_ids = [item.get('product_id') for item in data['products']]
        products = Product.query.filter(Product.id.in_(product_ids)).all()
        products_dict = {product.id: product for product in products}

        total_amount = Decimal('0.00')
        new_order = Order(user=user, total_amount=total_amount)
        db.session.add(new_order)

        for item in data['products']:
            product_id = item.get('product_id')
            quantity = item.get('quantity')

            if not product_id or not quantity:
                return {'message': 'Each product must have a product ID and a quantity.', 'status_code': 400}, 400

            product = products_dict.get(product_id)
            if not product:
                return {'message': f'Product with ID {product_id} was not found in our catalog.',
                        'status_code': 404}, 404

            if product.quantity_in_stock < quantity:
                return {'message': f'Sorry, we only have {product.quantity_in_stock} of {product.name} left.',
                        'status_code': 400}, 400

            product.quantity_in_stock -= quantity
            line_total = product.price * quantity
            total_amount += line_total

            order_product = OrderProduct(order=new_order, product=product, quantity=quantity)
            db.session.add(order_product)

        new_order.total_amount = total_amount
        db.session.commit()

        return {
            'message': 'Your order has been placed successfully!',
            'order_id': new_order.id,
            'total_amount': str(total_amount)
        }, 201


class UserOrderListAPI(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()

        orders = Order.query.filter_by(user_id=user_id).all()
        orders_list = []

        if not orders:
            return {'message': 'No orders found for this user.', 'orders': []}, 200

        for order in orders:
            order_details = {
                'order_id': order.id,
                'total_amount': str(order.total_amount),
                'created_at': order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'products': []
            }

            order_products = OrderProduct.query.filter_by(order_id=order.id).all()

            for op in order_products:
                product = Product.query.get(op.product_id)
                if product:
                    order_details['products'].append({
                        'product_id': product.id,
                        'name': product.name,
                        'quantity': op.quantity,
                        'price': str(product.price)
                    })

            orders_list.append(order_details)

        return {'orders': orders_list}, 200
