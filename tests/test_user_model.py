import unittest
from app.models import User

class UserModelTestCase(unittest.TestCase):
    def test__password_setter(self):
        u = User(password='cat')
        self.assertTrue(u.password_hash is not None)

    def test__password_getter(self):
        u = User(password='cat')
        with self.assertRaises(AttributeError):
            u.password

    def test__password_verificaiton(self):
        u = User(password='cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))

    def test__password_salts_are_randmon(self):
        u = User(password='cat')
        u2 = User(password='cat')
        self.assertTrue(u.password_hash != u2.password_hash)
