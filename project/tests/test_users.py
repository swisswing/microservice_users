import json
import unittest

from project.tests import BaseTestCase
from project import db
from project.api.models import User


def add_user(username, email):
    user = User(username, email)
    db.session.add(user)
    db.session.commit()
    return user


class TestUserService(BaseTestCase):
    """ Test for the Users Service. """

    def test_users(self):
        """Ensure the /ping route behaves correctly"""
        response = self.client.get('/users/ping')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('pong!', data['message'])
        self.assertIn('success', data['status'])

    def test_add_user(self):
        """Ensure a new user can be added to the database"""
        username = 'foo'
        email = 'foo@gmail.com'
        with self.client as client:
            response = client.post(
                '/users',
                data=json.dumps({
                    'username': username,
                    'email': email
                }),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertIn(f'{email} was added!', data['message'])
            self.assertIn('success', data['status'])

    def test_add_user_invalid_json(self):
        """Ensure error is thrown if the JSON object is empty"""
        with self.client as client:
            response = client.post(
                '/users',
                data=json.dumps({}),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_user_invalid_json_keys(self):
        """Ensure error is thrown if the JSON object does not have
        a username key"""
        with self.client as client:
            response = client.post(
                '/users',
                data=json.dumps({'email': 'dhsjak@hjkfsa.com'}),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_user_duplicate_email(self):
        """Ensure error is thrown if the email already exists"""
        username = 'same'
        email = 'same@same.com'
        with self.client as client:
            client.post(
                '/users',
                data=json.dumps({
                    'username': username,
                    'email': email
                }),
                content_type='application/json'
            )
            response = client.post(
                '/users',
                data=json.dumps({
                    'username': username,
                    'email': email
                }),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn(
                'Sorry. That email already exists', data['message']
            )
            self.assertIn('fail', data['status'])

    def test_get_single_user(self):
        """Ensure get single user behaves correctly"""
        user = User(username='abc', email='abc@gmail.com')
        db.session.add(user)
        db.session.commit()
        with self.client as client:
            response = client.get(
                f'/users/{user.id}'
            )
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data.decode())

            self.assertIn('abc', data['data']['username'])
            self.assertIn('abc@gmail.com', data['data']['email'])
            self.assertIn('success', data['status'])

    def test_single_user_no_id(self):
        """Ensure an error is thrown if an id is not provided"""
        with self.client as client:
            response = client.get(
                f'/users/blash'
            )
            # data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)

    def test_single_user_incorrect_id(self):
        """Ensure an error is thrown if the id does not exist"""
        with self.client as client:
            response = client.get(
                f'/users/999'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('User does not exist', data['message'])
            self.assertIn('fail', data['status'])

    def test_all_users(self):
        """Ensure get all users behaves correctly"""
        add_user('test1', 'test1@gmail.com')
        add_user('test2', 'test2@gmail.com')

        with self.client as client:
            response = client.get('/users')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertIn('success', data['status'])
            self.assertEqual(len(data['data']['users']), 2)
            self.assertIn('test1', data['data']['users'][0]['username'])
            self.assertIn('test2', data['data']['users'][1]['username'])
            self.assertIn('test1@gmail.com', data['data']['users'][0]['email'])
            self.assertIn('test2@gmail.com', data['data']['users'][1]['email'])

    def test_main_no_users(self):
        """Ensure the main route behaves correctly when no users have been
        added to the database """
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'All Users', response.data)
        self.assertIn(b'<p>No users!</p>', response.data)

    def test_main_with_users(self):
        """Ensure that main route behaves correctly when users have been
        added to the database"""
        add_user('michael', 'michael@mherman.org')
        add_user('fletcher', 'fletcher@notreal.com')

        with self.client as client:
            response = client.get('/')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'All Users', response.data)
            self.assertNotIn(b'<p>No users!</p>', response.data)
            self.assertIn(b'michael', response.data)
            self.assertIn(b'fletcher', response.data)

    def test_main_add_user(self):
        """Ensure a new user can be added to the database via a POST request"""
        with self.client as client:
            response = client.post(
                '/',
                data=dict(username='cindy', email='cindy@abcdefg.com'),
                follow_redirects=True
            )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'All Users', response.data)
        self.assertNotIn(b'<p>No users!</p>', response.data)
        self.assertIn(b'cindy', response.data)


if __name__ == '__main__':
    unittest.main()
