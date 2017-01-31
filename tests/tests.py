import os
import unittest
from unittest import mock

import requests
import yaosac


class ClientInternalTestCase(unittest.TestCase):
    key_name = 'OS_TEST_KEY'
    attr_name = 'test_key'

    def setUp(self):
        yaosac.client = yaosac.Client()

    def test_check_an_auth_key(self):
        """Check if an auth key is set"""
        key = 'a-key'
        other_key = 'other-key'
        os.environ[self.key_name] = key

        yaosac.client._check_an_auth_key(self.key_name)

        self.assertEqual(getattr(yaosac.client, '_' + self.attr_name), key)

        del(os.environ[self.key_name])

    def test_check_an_auth_key__raises_improperlyconfigured(self):
        """If the auth key is not found raise an exception"""
        with self.assertRaises(Exception) as context:
            yaosac.client._check_an_auth_key(self.key_name)

        self.assertIn(self.key_name, context.exception.args[0])

    def test_set_an_auth_key(self):
        value = 'a-value'

        yaosac.client._set_an_auth_key(self.key_name, value)

        self.assertEqual(getattr(yaosac.client, '_' + self.attr_name), value)

    def test_auth_key_properties(self):
        value = 'a-value-app'
        os.environ['OS_APP_AUTH_KEY'] = value

        result = yaosac.client.app_auth_key

        self.assertEqual(yaosac.client._app_auth_key, value)
        self.assertEqual(result, value)

        value = 'a-value-user'
        os.environ['OS_USER_AUTH_KEY'] = value

        result = yaosac.client.user_auth_key

        self.assertEqual(yaosac.client._user_auth_key, value)
        self.assertEqual(result, value)

        value = 'a-value-app-id'
        os.environ['OS_APP_ID'] = value

        result = yaosac.client.app_id

        self.assertEqual(yaosac.client._app_id, value)
        self.assertEqual(result, value)

    def test_auth_key_properties__setter(self):
        value = 'a-value-app'

        yaosac.client.app_auth_key = value

        self.assertEqual(yaosac.client._app_auth_key, value)

        value = 'a-value-user'

        yaosac.client.user_auth_key = value

        self.assertEqual(yaosac.client._user_auth_key, value)

        value = 'a-value-app-id'

        yaosac.client.app_id = value

        self.assertEqual(yaosac.client._app_id, value)

    def test_get_header(self):
        result = yaosac.client._get_headers()

        self.assertIn('content-type', result)

        value = 'a-value-test'
        yaosac.client.test_auth_key = value

        result = yaosac.client._get_headers('test')
        
        self.assertIn(value, result['authorization'])

        value = 'a-value-app'
        yaosac.client._set_an_auth_key('APP_AUTH_KEY', value)

        result = yaosac.client._get_headers()
        
        self.assertIn(value, result['authorization'])


class ClientAPIMEthodsTestCase(unittest.TestCase):
    def setUp(self):
        self.app_auth_key = 'app-test-key'
        self.app_id = 'app-test-id'
        self.user_auth_key = 'user-test-key'
        os.environ['OS_APP_AUTH_KEY'] = self.app_auth_key
        os.environ['OS_APP_ID'] = self.app_id
        os.environ['OS_USER_AUTH_KEY'] = self.user_auth_key
        self.client = yaosac.Client()
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

        response = self.client.create_notification(contents, **kwargs)

        self.assertEqual(requests.post.call_count, 1)
        self.assertIn('contents', requests.post.call_args[0][0])
        self.assertIn('app_id', requests.post.call_args[0][0])
        self.assertIn('what', requests.post.call_args[0][0])
        self.assertIn('headers', requests.post.call_args[1])
        self.assertIn(self.app_auth_key,
                      requests.post.call_args[1]['headers']['authorization'])
        self.assertIsNotNone(response)

    def test_cancel_notification(self):
        id = 'notification-id'
        app_id = ':P'

        response = self.client.cancel_notification(id, app_id)

        self.assertEqual(requests.delete.call_count, 1)
        self.assertIn(id, requests.delete.call_args[0][0])
        self.assertIn(app_id, requests.delete.call_args[0][0])
        self.assertIn('headers', requests.delete.call_args[1])
        self.assertIn(self.app_auth_key,
                      requests.delete.call_args[1]['headers']['authorization'])
        self.assertIsNotNone(response)

    def test_view_apps(self):
        response = self.client.view_apps()

        self.assertIn('apps', requests.get.call_args[0][0])
        self.assertIn(self.user_auth_key,
                      requests.get.call_args[1]['headers']['authorization'])
        self.assertIsNotNone(response)

    def test_view_an_app(self):
        app_id = 'an-id'
        response = self.client.view_an_app(app_id)

        self.assertIn('apps', requests.get.call_args[0][0])
        self.assertIn(app_id, requests.get.call_args[0][0])
        self.assertIn(self.user_auth_key,
                      requests.get.call_args[1]['headers']['authorization'])
        self.assertIsNotNone(response)

    def test_create_an_app(self):
        payload = {'what': 'ever'}
        response = self.client.create_an_app(**payload)

        self.assertIn('apps', requests.post.call_args[0][0])
        self.assertEqual(payload, requests.post.call_args[1]['data'])
        self.assertIn(self.user_auth_key,
                      requests.post.call_args[1]['headers']['authorization'])

    def test_update_an_app(self):
        payload = {'what': 'ever'}
        app_id = ';P'
        response = self.client.update_an_app(app_id, **payload)

        self.assertIn(app_id, requests.put.call_args[0][0])
        self.assertIn('apps', requests.put.call_args[0][0])
        self.assertEqual(payload, requests.put.call_args[1]['data'])
        self.assertIn(self.user_auth_key,
                      requests.put.call_args[1]['headers']['authorization'])

    def test_view_devices(self):
        response = self.client.view_devices()

        self.assertIn('players', requests.get.call_args[0][0])
        self.assertIn('app_id=', requests.get.call_args[0][0])
        self.assertIn(self.app_id, requests.get.call_args[0][0])
        self.assertIn(self.app_auth_key,
                      requests.get.call_args[1]['headers']['authorization'])

        # with limit
        requests.get.reset_mock()
        limit = 69
        response = self.client.view_devices(limit=limit)

        self.assertIn('limit=', requests.get.call_args[0][0])
        self.assertIn(str(limit), requests.get.call_args[0][0])

        # with offset
        requests.get.reset_mock()
        offset = 420
        response = self.client.view_devices(offset=offset)

        self.assertIn('offset=', requests.get.call_args[0][0])
        self.assertIn(str(offset), requests.get.call_args[0][0])

    def test_view_device(self):
        device_id = 'my-phone'
        response = self.client.view_device(device_id)

        self.assertIn('players', requests.get.call_args[0][0])
        self.assertIn(device_id, requests.get.call_args[0][0])
        self.assertIn('app_id=', requests.get.call_args[0][0])
        self.assertIn(self.app_id, requests.get.call_args[0][0])
        self.assertNotIn('authorization', requests.get.call_args[1]['headers'])

    def test_add_a_device(self):
        payload = {'read': 'the', 'docs': 1}
        response = self.client.add_a_device(**payload)

        self.assertIn('players', requests.post.call_args[0][0])
        self.assertIn('app_id', requests.post.call_args[1]['data'])
        self.assertEqual(self.app_id,
                         requests.post.call_args[1]['data']['app_id'])
        for key, value in payload.items():
            self.assertIn(key, requests.post.call_args[1]['data'])
            self.assertEqual(value, requests.post.call_args[1]['data'][key])
        self.assertNotIn('authorization', requests.post.call_args[1]['headers'])

    def test_edit_device(self):
        device_id = 'my-phone'
        payload = {'read': 'the', 'docs': 1}
        response = self.client.edit_device(device_id, **payload)

        self.assertIn('players', requests.put.call_args[0][0])
        self.assertIn(device_id, requests.put.call_args[0][0])
        self.assertIn('app_id', requests.put.call_args[1]['data'])
        self.assertEqual(self.app_id,
                         requests.put.call_args[1]['data']['app_id'])
        for key, value in payload.items():
            self.assertIn(key, requests.put.call_args[1]['data'])
            self.assertEqual(value, requests.put.call_args[1]['data'][key])
        self.assertNotIn('authorization', requests.put.call_args[1]['headers'])

    def test_edit_device(self):
        device_id = 'my-phone'
        payload = {'read': 'the', 'docs': 1}
        response = self.client.new_session(device_id, **payload)

        self.assertIn('players', requests.post.call_args[0][0])
        self.assertIn('on_session', requests.post.call_args[0][0])
        self.assertIn(device_id, requests.post.call_args[0][0])
        self.assertEqual(payload, requests.post.call_args[1]['data'])
        self.assertNotIn('authorization', requests.post.call_args[1]['headers'])

    def test_new_purchase(self):
        device_id = 'my-phone'
        payload = {'read': 'the', 'docs': 1}
        response = self.client.new_purchase(device_id, **payload)

        self.assertIn('players', requests.post.call_args[0][0])
        self.assertIn('on_purchase', requests.post.call_args[0][0])
        self.assertIn(device_id, requests.post.call_args[0][0])
        self.assertEqual(payload, requests.post.call_args[1]['data'])
        self.assertNotIn('authorization', requests.post.call_args[1]['headers'])

    def test_increment_session_length(self):
        device_id = 'my-phone'
        active_time = 10
        expected_payload = {'state': 'ping', 'active_time': active_time}

        response = self.client.increment_session_length(device_id, active_time)

        self.assertIn('players', requests.post.call_args[0][0])
        self.assertIn('on_focus', requests.post.call_args[0][0])
        self.assertIn(device_id, requests.post.call_args[0][0])
        self.assertEqual(expected_payload, requests.post.call_args[1]['data'])
        self.assertNotIn('authorization', requests.post.call_args[1]['headers'])

    def test_csv_export(self):
        response = self.client.csv_export()

        self.assertIn('players', requests.post.call_args[0][0])
        self.assertIn('csv_export', requests.post.call_args[0][0])
        self.assertIn('app_id=', requests.post.call_args[0][0])
        self.assertIn(self.app_id, requests.post.call_args[0][0])
        self.assertIn(self.app_auth_key,
                      requests.post.call_args[1]['headers']['authorization'])


        # Extra fields
        # location
        requests.post.reset_mock()
        response = self.client.csv_export(location=True)

        self.assertIn('location',
                      requests.post.call_args[1]['data']['extra_fields'])
        # country
        requests.post.reset_mock()
        response = self.client.csv_export(country=True)

        self.assertIn('country',
                      requests.post.call_args[1]['data']['extra_fields'])

        # rooted
        requests.post.reset_mock()
        response = self.client.csv_export(rooted=True)

        self.assertIn('rooted',
                      requests.post.call_args[1]['data']['extra_fields'])

    def test_view_notification(self):
        notification_id = 'an-push'
        response = self.client.view_notification(notification_id)

        self.assertIn('notifications', requests.get.call_args[0][0])
        self.assertIn(notification_id, requests.get.call_args[0][0])
        self.assertIn('app_id=', requests.get.call_args[0][0])
        self.assertIn(self.app_id, requests.get.call_args[0][0])
        self.assertIn(self.user_auth_key,
                      requests.get.call_args[1]['headers']['authorization'])

    def test_view_notifications(self):
        response = self.client.view_notifications()

        self.assertIn('notifications', requests.get.call_args[0][0])
        self.assertIn('app_id=', requests.get.call_args[0][0])
        self.assertIn(self.app_id, requests.get.call_args[0][0])
        self.assertIn(self.app_auth_key,
                      requests.get.call_args[1]['headers']['authorization'])

        # with limit
        requests.get.reset_mock()
        limit = 69
        response = self.client.view_notifications(limit=limit)

        self.assertIn('limit=', requests.get.call_args[0][0])
        self.assertIn(str(limit), requests.get.call_args[0][0])

        # with offset
        requests.get.reset_mock()
        offset = 420
        response = self.client.view_notifications(offset=offset)

        self.assertIn('offset=', requests.get.call_args[0][0])
        self.assertIn(str(offset), requests.get.call_args[0][0])

    def test_track_open(self):
        notification_id = 'a-push'
        response = self.client.track_open(notification_id)

        self.assertIn('notifications', requests.put.call_args[0][0])
        self.assertIn(notification_id, requests.put.call_args[0][0])
        self.assertIn('app_id', requests.put.call_args[1]['data'])
        self.assertIn(self.app_id, requests.put.call_args[1]['data']['app_id'])
        self.assertIn('opened', requests.put.call_args[1]['data'])
        self.assertTrue(requests.put.call_args[1]['data']['opened'])
        self.assertNotIn('authorization', requests.put.call_args[1]['headers'])
