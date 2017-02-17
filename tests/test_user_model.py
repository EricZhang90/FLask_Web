import unittest
from app.models import User, Role, Permission, AnonymousUser

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

    def test_roles_and_permissions(self):
        Role.insert_roles()
        u = User(email='test_one@example.com', password='cat')
        self.assertTrue(u.can(Permission.WRITE_ARTICLES))
        self.assertFalse(u.can(Permission.MODERATE_COMMENTS))

    def test_anonymous_user(self):
        u = AnonymousUser()
        self.assertFalse(u.can(Permission.FOLLOW))
