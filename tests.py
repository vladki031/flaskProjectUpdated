import unittest
from app import app, db
from models import User, Product
from flask_jwt_extended import create_access_token

class APITestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False

        self.app_context = app.app_context()
        self.app_context.push()
        self.app = app.test_client()

        db.create_all()

        user = User(username='vlad', password='vlad2003')
        user.set_password('vlad2003')
        db.session.add(user)
        db.session.commit()

        self.access_token = create_access_token(identity=user.id)

    def tearDown(self):
        db.session.remove()
        db.drop_all()

        self.app_context.pop()

    def test_product_list(self):
        response = self.app.get('/api/products/')
        self.assertEqual(response.status_code, 200)

    def test_order_creation_unauthenticated(self):
        response = self.app.post('/api/orders/', json={})
        self.assertEqual(response.status_code, 401)

    def test_order_creation_authenticated(self):
        product = Product(name='Test Product', description='Test Description', price=9.99, quantity_in_stock=10)
        db.session.add(product)
        db.session.commit()

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.app.post('/api/orders/', headers=headers, json={
            'products': [{'product_id': product.id, 'quantity': 2}]
        })
        self.assertEqual(response.status_code, 201)

if __name__ == '__main__':
    unittest.main()
