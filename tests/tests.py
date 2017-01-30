import os
import unittest
from unittest import mock

import requests
import yaosac


class ClientTestCase(unittest.TestCase):
    key_name = 'OS_TEST_KEY'
    attr_name = 'test_key'

    def setUp(self):
        self.client = yaosac.Client()
        requests.get = mock.Mock()
        requests.post = mock.Mock()
        requests.delete = mock.Mock()

    def test_check_an_auth_key(self):
        """Check if an auth key is set"""
        key = 'a-key'
        other_key = 'other-key'
        os.environ[self.key_name] = key

        self.client._check_an_auth_key(self.key_name)

        self.assertEqual(getattr(self.client, '_' + self.attr_name), key)

        del(os.environ[self.key_name])

    def test_check_an_auth_key__raises_improperlyconfigured(self):
        """If the auth key is not found raise an exception"""
        with self.assertRaises(Exception) as context:
            self.client._check_an_auth_key(self.key_name)

        self.assertIn(self.key_name, context.exception.args[0])

    def test_set_an_auth_key(self):
        value = 'a-value'

        self.client._set_an_auth_key(self.key_name, value)

        self.assertEqual(getattr(self.client, '_' + self.attr_name), value)

    def test_auth_key_properties(self):
        value = 'a-value'
        os.environ['OS_APP_AUTH_KEY'] = value

        result = self.client.app_auth_key

        self.assertEqual(self.client._app_auth_key, value)
        self.assertEqual(result, value)

        os.environ['OS_USER_AUTH_KEY'] = value

        result = self.client.user_auth_key

        self.assertEqual(self.client._user_auth_key, value)
        self.assertEqual(result, value)

    def test_auth_key_properties__setter(self):
        value = 'a-key'

        self.client.app_auth_key = value

        self.assertEqual(self.client._app_auth_key, value)

        self.client.user_auth_key = value

        self.assertEqual(self.client._user_auth_key, value)

    def test_get_header(self):
        key = 'test-key'
        yaosac.client.test_auth_key = key

        result = yaosac.client._get_headers('test')
        
        self.assertIn(key, result['authorization'])
    #
    # end-points tests
    #

    # One function. Functions just pass `kwargs` to in the payload.
    # errors like not sending a key 'en' in `contents` will not be
    # validated, the API gives clear error messages for this cases.

    def test_create_notification(self):
        kwargs = {'what': 'ever'}
        expected_kwargs = kwargs.copy()
        expected_kwargs.update({'headers': ''})
        contents = {'en': 'Bla'}

        response = self.client.create_notification(contents, **kwargs)

        self.assertEqual(requests.post.call_count, 1)
        self.assertIn('contents', requests.post.call_args[0][0])
        self.assertIn('app_id', requests.post.call_args[0][0])
        for key in kwargs:
            self.assertIn(key, requests.post.call_args[1], key)
        self.assertIn('headers', requests.post.call_args[1])
        self.assertIsNone(response)

    def test_cancel_notification(self):
        id = 'notification-id'
        app_id = ':P'

        response = self.client.cancel_notification(id, app_id)

        self.assertEqual(requests.delete.call_count, 1)
        self.assertIn(id, requests.delete.call_args[0][0])
        self.assertIn(app_id, requests.delete.call_args[0][0])
        self.assertIsNone(response)


class AddHeadersTestCase(unittest.TestCase):
    def setUp(self):
        self._orgi_app = yaosac.APP_AUTH_METHODS
        self._orgi_user = yaosac.USER_AUTH_METHODS
        
    def test_cases_for_app_auth_key(self):
        os.environ['OS_APP_AUTH_KEY'] = 'a-key'
        method_name = 'app_auth_method'
        yaosac.APP_AUTH_METHODS = [method_name, ]
        f = mock.Mock()
        f.__name__ = method_name

        yaosac.add_headers(f)(yaosac.client)

        f.assert_called_once_with(yaosac.client, headers=yaosac.client._get_headers('app'))

    def test_cases_for_user_auth_key(self):
        os.environ['OS_USER_AUTH_KEY'] = 'user-key'
        method_name = 'user_auth_method'
        yaosac.USER_AUTH_METHODS = [method_name, ]
        f = mock.Mock()
        f.__name__ = method_name

        yaosac.add_headers(f)(yaosac.client)

        f.assert_called_once_with(yaosac.client, headers=yaosac.client._get_headers(auth_name='user'))

    def tearDown(self):
        yaosac.APP_AUTH_METHODS = self._orgi_app
        yaosac.USER_AUTH_METHODS = self._orgi_user
