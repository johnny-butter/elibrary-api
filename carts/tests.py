import threading

from django.test import TestCase, TransactionTestCase, Client

from .models import Cart
from orders.models import Order

from .factories import CartFactory
from users.factories import UserFactory
from books.factories import BookFactory


CARTS_ENDPOINT_PREFIX = '/api/v1/carts'


class TestCartApi(TestCase):

    def setUp(self):
        password = '123456789'
        self.user = UserFactory(password=password)

        resp = self.client.post(
            '/api/v1/users/auth',
            {'username': self.user.username, 'password': password},
            content_type='application/json',
        )
        self.authed_client = Client(HTTP_Authorization=f"Bearer {resp.json()['token']}")

        self.book = BookFactory(stock=1)

    def test_get_user_cart(self):
        book_name = 'test_cart'
        book = BookFactory(name=book_name)

        CartFactory(user=self.user, book=book)

        for i in range(2):
            CartFactory(user=self.user)

        resp = self.authed_client.get(f'{CARTS_ENDPOINT_PREFIX}/')
        resp_json = resp.json()

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp_json['data']), 3)
        self.assertIn(book_name, [item['book']['name'] for item in resp_json['data']])

    def test_add_item_to_cart(self):
        data = {
            'book_id': self.book.id,
            'price': self.book.price,
            'amount': 1,
        }

        resp = self.authed_client.put(f'{CARTS_ENDPOINT_PREFIX}/', data, content_type='application/json')

        cart = Cart.objects.last()
        self.book.refresh_from_db()

        self.assertEqual(resp.status_code, 204)
        self.assertEqual(cart.user, self.user)
        self.assertEqual(cart.amount, 1)
        self.assertEqual(cart.unit_price, data['price'])
        self.assertEqual(self.book.stock, 0)

    def test_add_item_to_cart_stock_not_enough(self):
        data = {
            'book_id': self.book.id,
            'price': self.book.price,
            'amount': 2,
        }

        resp = self.authed_client.put(f'{CARTS_ENDPOINT_PREFIX}/', data, content_type='application/json')

        self.assertEqual(resp.status_code, 400)

    def test_add_item_to_cart_without_price(self):
        data = {
            'book_id': self.book.id,
            'amount': 1,
        }

        resp = self.authed_client.put(f'{CARTS_ENDPOINT_PREFIX}/', data, content_type='application/json')

        self.assertEqual(resp.status_code, 400)

    def test_add_cart_item_amount(self):
        book = BookFactory(stock=3)

        cart_item = CartFactory(user=self.user, book=book, amount=1)
        cart_item_price_before = cart_item.unit_price

        data = {
            'book_id': book.id,
            'amount': 3,
        }

        resp = self.authed_client.put(f'{CARTS_ENDPOINT_PREFIX}/', data, content_type='application/json')

        cart_item.refresh_from_db()
        book.refresh_from_db()

        self.assertEqual(resp.status_code, 204)
        self.assertEqual(cart_item.amount, 3)
        self.assertEqual(cart_item.unit_price, cart_item_price_before)
        self.assertEqual(book.stock, 1)

    def test_reduce_cart_item_amount(self):
        book_stock = self.book.stock

        cart_item = CartFactory(user=self.user, book=self.book, amount=2)

        data = {
            'book_id': self.book.id,
            'amount': 1,
        }

        resp = self.authed_client.put(f'{CARTS_ENDPOINT_PREFIX}/', data, content_type='application/json')

        self.book.refresh_from_db()
        cart_item.refresh_from_db()

        self.assertEqual(resp.status_code, 204)
        self.assertEqual(cart_item.amount, 1)
        self.assertEqual(self.book.stock, book_stock + 1)

    def test_remove_item_from_cart(self):
        book_stock = self.book.stock
        cart_item = CartFactory(user=self.user, book=self.book, amount=2)

        data = {
            'cart_id': cart_item.id,
        }

        resp = self.authed_client.delete(f'{CARTS_ENDPOINT_PREFIX}/', data, content_type='application/json')

        self.book.refresh_from_db()

        self.assertEqual(resp.status_code, 204)
        self.assertEqual(self.book.stock, book_stock + 2)
        with self.assertRaises(Cart.DoesNotExist):
            Cart.objects.get(id=cart_item.id)

    def test_cart_checkout(self):
        book = BookFactory(stock=1)

        cart_item = CartFactory(user=self.user, book=book, amount=3)

        resp = self.authed_client.post(
            f'{CARTS_ENDPOINT_PREFIX}/checkout',
            {'payment_type': 'CreditCard'},
            content_type='application/json')
        resp_json = resp.json()

        order = Order.objects.get(id=resp_json['order_id'])
        order_items = order.ordereditem_set.all()

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp_json['total_price'], order.total_price)
        self.assertEqual(resp_json['items'][0]['price'], order_items.first().unit_price)
        self.assertEqual(resp_json['items'][0]['amount'], order_items.first().amount)
        self.assertEqual(resp_json['items'][0]['book']['id'], book.id)
        self.assertEqual(Cart.objects.filter(user=self.user).count(), 0)
        self.assertEqual(order.total_price, cart_item.unit_price * cart_item.amount)
        self.assertEqual(len(order_items), 1)


class TestCartApiConcurrent(TransactionTestCase):

    def setUp(self):
        password = '123456789'
        self.user1 = UserFactory(username='user1', password=password)
        self.user2 = UserFactory(username='user2', password=password)
        self.user3 = UserFactory(username='user3', password=password)

        self.authed_client_1 = Client(HTTP_Authorization=f"Bearer {self._get_jwt_token(self.user1.username, password)}")
        self.authed_client_2 = Client(HTTP_Authorization=f"Bearer {self._get_jwt_token(self.user2.username, password)}")
        self.authed_client_3 = Client(HTTP_Authorization=f"Bearer {self._get_jwt_token(self.user3.username, password)}")

    def _get_jwt_token(self, username: str, password: str) -> str:
        resp = self.client.post(
            '/api/v1/users/auth',
            {'username': username, 'password': password},
            content_type='application/json',
        )

        return resp.json()['token']

    def test_add_item_to_cart_concurrent(self):
        book = BookFactory(stock=1)

        data = {
            'book_id': book.id,
            'price': book.price,
            'amount': 1,
        }
        kwargs = {'content_type': 'application/json'}

        tasks = [
            threading.Thread(target=self.authed_client_1.put, args=(f'{CARTS_ENDPOINT_PREFIX}/', data), kwargs=kwargs),
            threading.Thread(target=self.authed_client_2.put, args=(f'{CARTS_ENDPOINT_PREFIX}/', data), kwargs=kwargs),
            threading.Thread(target=self.authed_client_3.put, args=(f'{CARTS_ENDPOINT_PREFIX}/', data), kwargs=kwargs)
        ]

        for task in tasks:
            task.start()

        for task in tasks:
            task.join()

        book.refresh_from_db()

        self.assertEqual(book.stock, 0)
        self.assertEqual(len(Cart.objects.filter(book=book).filter(user__in=[self.user1, self.user2, self.user3])), 1)
