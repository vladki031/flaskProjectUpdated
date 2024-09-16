from flask_restful import Resource
from models import Product
from flask import request

class ProductListAPI(Resource):
    def get(self):
        in_stock = request.args.get('in_stock', type=bool)
        query = Product.query

        if in_stock:
            query = query.filter(Product.quantity_in_stock > 0)

        products = query.all()
        product_list = []
        for product in products:
            product_list.append({
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'price': str(product.price),
                'quantity_in_stock': product.quantity_in_stock
            })

        return {'products': product_list}, 200


class ProductDetailAPI(Resource):
    def get(self, id):
        product = Product.query.get_or_404(id)
        return {
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': str(product.price),
            'quantity_in_stock': product.quantity_in_stock
        }, 200
