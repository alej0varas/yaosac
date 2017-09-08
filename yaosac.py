import os

import requests


class ImproperlyConfigured(Exception):
    pass


class Client:
    """Client methods are a map of the server API end-points"""

    OS_URL = 'https://onesignal.com/api/v1/'

    def _check_an_auth_key(self, key_name):
        value = os.environ.get(key_name, None)
        attr_name = key_name[2:].lower()
        if value is None:
            raise ImproperlyConfigured(("An Auth Key is missing. You can set "
                                        "it through the '%s' environment "
                                        "variable or the '%s' argument."
                                        % (key_name, attr_name)))
        setattr(self, attr_name, value)

    @property
    def app_auth_key(self):
        if getattr(self, '_app_auth_key', None) is None:
            self._check_an_auth_key('OS_APP_AUTH_KEY')
        return self._app_auth_key

    @app_auth_key.setter
    def app_auth_key(self, value):
        setattr(self, '_app_auth_key', value)

    @property
    def app_id(self):
        if getattr(self, '_app_id', None) is None:
            self._check_an_auth_key('OS_APP_ID')
        return self._app_id

    @app_id.setter
    def app_id(self, value):
        setattr(self, '_app_id', value)

    @property
    def user_auth_key(self):
        if getattr(self, '_user_auth_key', None) is None:
            self._check_an_auth_key('OS_USER_AUTH_KEY')
        return self._user_auth_key

    @user_auth_key.setter
    def user_auth_key(self, value):
        setattr(self, '_user_auth_key', value)

    def _get_headers(self, auth_name=None):
        headers = {'Content-Type': 'application/json'}
        if auth_name is not None:
            auth = getattr(self, auth_name + '_auth_key')
            headers.update({'Authorization': 'Basic %s' % auth})
        return headers

    def _make_request(self, url, method_name, data=None, auth=None):
        headers = self._get_headers(auth)
        method = getattr(requests, method_name)

        response = method(url, json=data, headers=headers)
        return response

    #
    # API methods
    #
    def create_notification(self, contents=None, template_id=None, **kwargs):
        _url = 'notifications'
        url = self.OS_URL + _url
        # Be sure we don't send a empty `template_id`
        if not template_id:
            template_id = None
        assert contents or template_id, ('A required field is missing '
                                         '`contents` or `template_id`')
        data = {'app_id': self.app_id}
        if contents is not None:
            if isinstance(contents, str):
                # Set the string as the required default language
                contents = {'en': contents}
            data.update({'contents': contents})
        else:
            data.update({'template_id': template_id})
        data.update(kwargs)
        return self._make_request(url, 'post', data=data, auth='app')

    def cancel_notification(self, notification_id):
        _url = 'notifications'
        url = (self.OS_URL + _url + '/' + notification_id
               + '?app_id=' + self.app_id)
        return self._make_request(url, 'delete', auth='app')

    def view_apps(self):
        _url = 'apps'
        url = self.OS_URL + _url
        return self._make_request(url, 'get', auth='user')
        
    def view_an_app(self, app_id):
        _url = 'apps'
        url = self.OS_URL + _url + '/' + app_id
        return self._make_request(url, 'get', auth='user')

    def create_an_app(self, **kwargs):
        _url = 'apps'
        url = self.OS_URL + _url
        return self._make_request(url, 'post', data=kwargs, auth='user')
        
    def update_an_app(self, **kwargs):
        _url = 'apps'
        url = self.OS_URL + _url + '/' + self.app_id
        return self._make_request(url, 'put', data=kwargs, auth='user')

    def view_devices(self, limit=None, offset=None):
        _url = 'players'
        url = self.OS_URL + _url + '/?app_id=' + self.app_id
        if limit is not None:
            url += '&limit=' + str(limit)
        if offset is not None:
            url += '&offset=' + str(offset)
        return self._make_request(url, 'get', auth='app')

    def view_device(self, device_id):
        _url = 'players'
        url = self.OS_URL + _url + '/' + device_id + '?app_id=' + self.app_id
        return self._make_request(url, 'get')

    def add_a_device(self, **kwargs):
        _url = 'players'
        url = self.OS_URL + _url
        kwargs.update({'app_id': self.app_id})
        return self._make_request(url, 'post', data=kwargs)

    def edit_device(self, device_id, **kwargs):
        _url = 'players'
        url = self.OS_URL + _url + '/' + device_id
        kwargs.update({'app_id': self.app_id})
        return self._make_request(url, 'put', data=kwargs)

    def new_session(self, device_id, **kwargs):
        _url = 'players'
        url = self.OS_URL + _url + '/' + device_id + '/on_session'
        return self._make_request(url, 'post', data=kwargs)

    def new_purchase(self, device_id, **kwargs):
        _url = 'players'
        url = self.OS_URL + _url + '/' + device_id + '/on_purchase'
        return self._make_request(url, 'post', data=kwargs)

    def increment_session_length(self, device_id, active_time):
        _url = 'players'
        url = self.OS_URL + _url + '/' + device_id + '/on_focus'
        data = {'state': 'ping', 'active_time': active_time}
        return self._make_request(url, 'post', data=data)

    def csv_export(self, **kwargs):
        _url = 'players'
        url = self.OS_URL + _url + '/csv_export' + '?app_id=' + self.app_id
        data = {'extra_fields': list(kwargs.keys())}
        return self._make_request(url, 'post', data=data, auth='app')

    def view_notification(self, notification_id):
        # We rise an exception here because if not id is given the
        # call is equal to `view_notifications`. If we let this
        # happens the call to OneSignal will be valid but the content
        # unexpected.
        assert notification_id, "`notification_id`({}) is not a valid id".format(notification_id)
        _url = 'notifications'
        url = (self.OS_URL + _url + '/' + notification_id
               + '?app_id=' + self.app_id)
        return self._make_request(url, 'get', auth='app')

    def view_notifications(self, limit=None, offset=None):
        _url = 'notifications'
        url = self.OS_URL + _url + '/' + '?app_id=' + self.app_id
        if limit is not None:
            url += '&limit=' + str(limit)
        if offset is not None:
            url += '&offset=' + str(offset)
        return self._make_request(url, 'get', auth='app')

    def track_open(self, notification_id):
        _url = 'notifications'
        url = self.OS_URL + _url + '/' + notification_id
        data = {'app_id': self.app_id,
                'opened': True}
        return self._make_request(url, 'put', data=data)


client = Client()
