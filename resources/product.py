from flask import Blueprint
from flask_restful import Api, Resource
from models import Product
from flask import request
from http import HTTPStatus

product_blueprint = Blueprint('product', __name__)
api = Api(product_blueprint)

class ProductListAPI(Resource):
    def get(self):
        in_stock = request.args.get('in_stock', type=bool)
        query = Product.query

        if in_stock:
            query = query.filter(Product.quantity_in_stock > 0)

        products = query.all()
        product_list = [product.to_json() for product in products]

        return {'products': product_list}, HTTPStatus.OK

class ProductDetailAPI(Resource):
    def get(self, id):
        product = Product.query.get_or_404(id)
        return product.to_json(), HTTPStatus.OK

api.add_resource(ProductListAPI, '/')
api.add_resource(ProductDetailAPI, '/<int:id>')
