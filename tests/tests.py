import os
import unittest
from unittest import mock

import requests
import yaosac


APP_AUTH_KEY = 'app-test-key'
APP_ID = 'app-test-id'
USER_AUTH_KEY = 'user-test-key'
os.environ['OS_APP_AUTH_KEY'] = APP_AUTH_KEY
os.environ['OS_APP_ID'] = APP_ID
os.environ['OS_USER_AUTH_KEY'] = USER_AUTH_KEY


class ClientInternalTestCase(unittest.TestCase):
    key_name = 'OS_TEST_KEY'
    attr_name = '_test_key'

    def test_check_an_auth_key(self):
        """Check if an auth key is set"""
        value = 'a-value'
        os.environ[self.key_name] = value

        yaosac.client._check_an_auth_key(self.key_name)

        self.assertEqual(getattr(yaosac.client, self.attr_name), value)

        del(os.environ[self.key_name])

    def test_check_an_auth_key__raises_improperlyconfigured(self):
        """If the auth key is not found raise an exception"""
        key_name = 'DOES_NOT_EXIST'
        with self.assertRaises(Exception) as context:
            yaosac.client._check_an_auth_key(key_name)

        self.assertIn(key_name, context.exception.args[0])

    def test_auth_key_properties(self):
        result = yaosac.client.app_auth_key

        self.assertEqual(yaosac.client._app_auth_key, APP_AUTH_KEY)
        self.assertEqual(result, APP_AUTH_KEY)

        result = yaosac.client.user_auth_key

        self.assertEqual(yaosac.client._user_auth_key, USER_AUTH_KEY)
        self.assertEqual(result, USER_AUTH_KEY)

        result = yaosac.client.app_id

        self.assertEqual(yaosac.client._app_id, APP_ID)
        self.assertEqual(result, APP_ID)

    def test_auth_key_properties__setter(self):
        _orig = yaosac.client.app_auth_key

        value = 'new-app'

        yaosac.client.app_auth_key = value

        self.assertEqual(yaosac.client._app_auth_key, value)

        value = 'new-user'

        yaosac.client.user_auth_key = value

        self.assertEqual(yaosac.client._user_auth_key, value)

        value = 'new-app-id'

        yaosac.client.app_id = value

        self.assertEqual(yaosac.client._app_id, value)

        yaosac.client.app_auth_key = _orig

    def test_get_header(self):
        result = yaosac.client._get_headers()

        self.assertIn('Content-Type', result)

        value = 'a-value-test'
        yaosac.client.test_auth_key = value

        result = yaosac.client._get_headers('test')
        
        self.assertIn(value, result['Authorization'])

        result = yaosac.client._get_headers('app')
        
        self.assertIn(APP_AUTH_KEY, result['Authorization'])

    def test_make_request(self):
        url = 'bleh'
        method = 'put'

        with mock.patch('requests.' + method) as mock_method:
            with mock.patch('yaosac.Client._get_headers') as mock_get_headers:
                mock_headers = {'mock': 'headers'}
                mock_get_headers.return_value = mock_headers

                # Basic
                yaosac.client._make_request(url, method)

                mock_method.assert_called_once_with(
                    url, json=None, headers=mock_headers)

                # With data
                mock_method.reset_mock()
                mock_get_headers.reset_mock()
                yaosac.client._make_request(url, method, data={})

                mock_method.assert_called_once_with(
                    url, json={}, headers=mock_headers)

                # With auth
                mock_method.reset_mock()
                mock_get_headers.reset_mock()
                auth = 'auth'
                yaosac.client._make_request(url, method, auth=auth)
                mock_method.assert_called_once_with(
                    url, json=None, headers=mock_headers)
                mock_get_headers.assert_called_once_with(auth)


class ClientAPIMEthodsTestCase(unittest.TestCase):
    def setUp(self):
        requests.get = mock.Mock()
        requests.post = mock.Mock()
        requests.put = mock.Mock()
        requests.delete = mock.Mock()
        requests.get.return_value = not None
        requests.post.return_value = not None
        requests.put.return_value = not None
        requests.delete.return_value = not None

    #
    # end-points tests
    #

    # One function. Functions just pass `kwargs` to in the payload.
    # errors like not sending a key 'en' in `contents` will not be
    # validated, the API gives clear error messages for this cases.

    def test_create_notification(self):
        kwargs = {'what': 'ever'}
        contents = {'en': 'Bla'}

        response = yaosac.client.create_notification(contents, **kwargs)

        self.assertEqual(requests.post.call_count, 1)
        self.assertIn('app_id', requests.post.call_args[1]['json'])
        self.assertIn('contents', requests.post.call_args[1]['json'])
        self.assertIn('what', requests.post.call_args[1]['json'])
        self.assertIn(APP_AUTH_KEY,
                      requests.post.call_args[1]['headers']['Authorization'])
        self.assertIsNotNone(response)

    def test_create_notification__content_is_string(self):
        # if contents is just a string, not dict, it's set as the
        # default 'en' language inside a dict.
        kwargs = {'what': 'ever'}
        contents = 'Bla bla'

        response = yaosac.client.create_notification(contents, **kwargs)

        self.assertIn('en', requests.post.call_args[1]['json']['contents'])
        self.assertIn(contents,
                      requests.post.call_args[1]['json']['contents']['en'])


    def test_cancel_notification(self):
        notification_id = 'notification-id'

        response = yaosac.client.cancel_notification(notification_id)

        self.assertEqual(requests.delete.call_count, 1)
        self.assertIn(notification_id, requests.delete.call_args[0][0])
        self.assertIn(APP_ID, requests.delete.call_args[0][0])
        self.assertIn('headers', requests.delete.call_args[1])
        self.assertIn(APP_AUTH_KEY,
                      requests.delete.call_args[1]['headers']['Authorization'])
        self.assertIsNotNone(response)

    def test_view_apps(self):
        response = yaosac.client.view_apps()

        self.assertIn('apps', requests.get.call_args[0][0])
        self.assertIn(USER_AUTH_KEY,
                      requests.get.call_args[1]['headers']['Authorization'])
        self.assertIsNotNone(response)

    def test_view_an_app(self):
        app_id = 'an-id'
        response = yaosac.client.view_an_app(app_id)

        self.assertIn('apps', requests.get.call_args[0][0])
        self.assertIn(app_id, requests.get.call_args[0][0])
        self.assertIn(USER_AUTH_KEY,
                      requests.get.call_args[1]['headers']['Authorization'])
        self.assertIsNotNone(response)

    def test_create_an_app(self):
        payload = {'what': 'ever'}
        response = yaosac.client.create_an_app(**payload)

        self.assertIn('apps', requests.post.call_args[0][0])
        self.assertEqual(payload, requests.post.call_args[1]['json'])
        self.assertIn(USER_AUTH_KEY,
                      requests.post.call_args[1]['headers']['Authorization'])

    def test_update_an_app(self):
        payload = {'what': 'ever'}
        response = yaosac.client.update_an_app(**payload)

        self.assertIn(APP_ID, requests.put.call_args[0][0])
        self.assertIn('apps', requests.put.call_args[0][0])
        self.assertEqual(payload, requests.put.call_args[1]['json'])
        self.assertIn(USER_AUTH_KEY,
                      requests.put.call_args[1]['headers']['Authorization'])

    def test_view_devices(self):
        response = yaosac.client.view_devices()

        self.assertIn('players', requests.get.call_args[0][0])
        self.assertIn('app_id=', requests.get.call_args[0][0])
        self.assertIn(APP_ID, requests.get.call_args[0][0])
        self.assertIn(APP_AUTH_KEY,
                      requests.get.call_args[1]['headers']['Authorization'])

        # with limit
        requests.get.reset_mock()
        limit = 69
        response = yaosac.client.view_devices(limit=limit)

        self.assertIn('limit=', requests.get.call_args[0][0])
        self.assertIn(str(limit), requests.get.call_args[0][0])

        # with offset
        requests.get.reset_mock()
        offset = 420
        response = yaosac.client.view_devices(offset=offset)

        self.assertIn('offset=', requests.get.call_args[0][0])
        self.assertIn(str(offset), requests.get.call_args[0][0])

    def test_view_device(self):
        device_id = 'my-phone'
        response = yaosac.client.view_device(device_id)

        self.assertIn('players', requests.get.call_args[0][0])
        self.assertIn(device_id, requests.get.call_args[0][0])
        self.assertIn('app_id=', requests.get.call_args[0][0])
        self.assertIn(APP_ID, requests.get.call_args[0][0])
        self.assertNotIn('Authorization', requests.get.call_args[1]['headers'])

    def test_add_a_device(self):
        payload = {'read': 'the', 'docs': 1}
        response = yaosac.client.add_a_device(**payload)

        self.assertIn('players', requests.post.call_args[0][0])
        self.assertIn('app_id', requests.post.call_args[1]['json'])
        self.assertEqual(APP_ID,
                         requests.post.call_args[1]['json']['app_id'])
        for key, value in payload.items():
            self.assertIn(key, requests.post.call_args[1]['json'])
            self.assertEqual(value, requests.post.call_args[1]['json'][key])
        self.assertNotIn('Authorization', requests.post.call_args[1]['headers'])

    def test_edit_device(self):
        device_id = 'my-phone'
        payload = {'read': 'the', 'docs': 1}
        response = yaosac.client.edit_device(device_id, **payload)

        self.assertIn('players', requests.put.call_args[0][0])
        self.assertIn(device_id, requests.put.call_args[0][0])
        self.assertIn('app_id', requests.put.call_args[1]['json'])
        self.assertEqual(APP_ID,
                         requests.put.call_args[1]['json']['app_id'])
        for key, value in payload.items():
            self.assertIn(key, requests.put.call_args[1]['json'])
            self.assertEqual(value, requests.put.call_args[1]['json'][key])
        self.assertNotIn('Authorization', requests.put.call_args[1]['headers'])

    def test_edit_device(self):
        device_id = 'my-phone'
        payload = {'read': 'the', 'docs': 1}
        response = yaosac.client.new_session(device_id, **payload)

        self.assertIn('players', requests.post.call_args[0][0])
        self.assertIn('on_session', requests.post.call_args[0][0])
        self.assertIn(device_id, requests.post.call_args[0][0])
        self.assertEqual(payload, requests.post.call_args[1]['json'])
        self.assertNotIn('Authorization', requests.post.call_args[1]['headers'])

    def test_new_purchase(self):
        device_id = 'my-phone'
        payload = {'read': 'the', 'docs': 1}
        response = yaosac.client.new_purchase(device_id, **payload)

        self.assertIn('players', requests.post.call_args[0][0])
        self.assertIn('on_purchase', requests.post.call_args[0][0])
        self.assertIn(device_id, requests.post.call_args[0][0])
        self.assertEqual(payload, requests.post.call_args[1]['json'])
        self.assertNotIn('Authorization', requests.post.call_args[1]['headers'])

    def test_increment_session_length(self):
        device_id = 'my-phone'
        active_time = 10
        expected_payload = {'state': 'ping', 'active_time': active_time}

        response = yaosac.client.increment_session_length(device_id, active_time)

        self.assertIn('players', requests.post.call_args[0][0])
        self.assertIn('on_focus', requests.post.call_args[0][0])
        self.assertIn(device_id, requests.post.call_args[0][0])
        self.assertEqual(expected_payload, requests.post.call_args[1]['json'])
        self.assertNotIn('Authorization', requests.post.call_args[1]['headers'])

    def test_csv_export(self):
        response = yaosac.client.csv_export()

        self.assertIn('players', requests.post.call_args[0][0])
        self.assertIn('csv_export', requests.post.call_args[0][0])
        self.assertIn('app_id=', requests.post.call_args[0][0])
        self.assertIn(APP_ID, requests.post.call_args[0][0])
        self.assertIn(APP_AUTH_KEY,
                      requests.post.call_args[1]['headers']['Authorization'])


        # Extra fields
        # location
        requests.post.reset_mock()
        response = yaosac.client.csv_export(location=True)

        self.assertIn('location',
                      requests.post.call_args[1]['json']['extra_fields'])
        # country
        requests.post.reset_mock()
        response = yaosac.client.csv_export(country=True)

        self.assertIn('country',
                      requests.post.call_args[1]['json']['extra_fields'])

        # rooted
        requests.post.reset_mock()
        response = yaosac.client.csv_export(rooted=True)

        self.assertIn('rooted',
                      requests.post.call_args[1]['json']['extra_fields'])

    def test_view_notification(self):
        notification_id = 'an-push'
        response = yaosac.client.view_notification(notification_id)

        self.assertIn('notifications', requests.get.call_args[0][0])
        self.assertIn(notification_id, requests.get.call_args[0][0])
        self.assertIn('app_id=', requests.get.call_args[0][0])
        self.assertIn(APP_ID, requests.get.call_args[0][0])
        self.assertIn(APP_AUTH_KEY,
                      requests.get.call_args[1]['headers']['Authorization'])

    def test_view_notifications(self):
        response = yaosac.client.view_notifications()

        self.assertIn('notifications', requests.get.call_args[0][0])
        self.assertIn('app_id=', requests.get.call_args[0][0])
        self.assertIn(APP_ID, requests.get.call_args[0][0])
        self.assertIn(APP_AUTH_KEY,
                      requests.get.call_args[1]['headers']['Authorization'])

        # with limit
        requests.get.reset_mock()
        limit = 69
        response = yaosac.client.view_notifications(limit=limit)

        self.assertIn('limit=', requests.get.call_args[0][0])
        self.assertIn(str(limit), requests.get.call_args[0][0])

        # with offset
        requests.get.reset_mock()
        offset = 420
        response = yaosac.client.view_notifications(offset=offset)

        self.assertIn('offset=', requests.get.call_args[0][0])
        self.assertIn(str(offset), requests.get.call_args[0][0])

    def test_track_open(self):
        notification_id = 'a-push'
        response = yaosac.client.track_open(notification_id)

        self.assertIn('notifications', requests.put.call_args[0][0])
        self.assertIn(notification_id, requests.put.call_args[0][0])
        self.assertIn('app_id', requests.put.call_args[1]['json'])
        self.assertIn(APP_ID, requests.put.call_args[1]['json']['app_id'])
        self.assertIn('opened', requests.put.call_args[1]['json'])
        self.assertTrue(requests.put.call_args[1]['json']['opened'])
        self.assertNotIn('Authorization', requests.put.call_args[1]['headers'])
