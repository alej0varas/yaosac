import os

import requests


class ImproperlyConfigured(Exception):
    pass


class Client:
    """Client methods are a map of the server API end-points[0] where the
    method name is the end-point name in lower case and spaces
    replaced by underscores. Depending on the methods you call you
    will need an User Auth Key or an App Auth Key or an App
    Id[1]. They can be set as environment variables
    'OS_USER_AUTH_KEY', 'OS_APP_AUTH_KEY' and 'OS_APP_ID' or assigned
    to the client via `app_auth_key`, `user_auth_key` and `app_id`
    attributes.

    0 - https://documentation.onesignal.com/reference
    1 - https://documentation.onesignal.com/docs/accounts-and-keys

    """

    OS_URL = 'https://onesignal.com/api/v1/'

    def _check_an_auth_key(self, key_name):
        value = os.environ.get(key_name, None)
        attr_name = (key_name[3:] if key_name.startswith('OS_') else
                     key_name).lower()
        if value is None:
            raise ImproperlyConfigured(("An Auth Key missing. You can set "
                                        "it through the '%s' environment "
                                        "variable or the '%s' "
                                        "argument." % (key_name, attr_name)))
        self._set_an_auth_key(attr_name, value)

    def _set_an_auth_key(self, attr_name, value):
        setattr(self, '_' + attr_name.lower(), value)

    @property
    def app_auth_key(self):
        if getattr(self, '_app_auth_key', None) is None:
            self._check_an_auth_key('OS_APP_AUTH_KEY')
        return self._app_auth_key

    @app_auth_key.setter
    def app_auth_key(self, value):
        if getattr(self, '_app_auth_key', None) is None:
            self._set_an_auth_key('OS_APP_AUTH_KEY', value)

    @property
    def app_id(self):
        if getattr(self, '_app_id', None) is None:
            self._check_an_auth_key('OS_APP_ID')
        return self._app_id

    @app_id.setter
    def app_id(self, value):
        if getattr(self, '_app_id', None) is None:
            self._set_an_auth_key('OS_APP_ID', value)

    @property
    def user_auth_key(self):
        if getattr(self, '_user_auth_key', None) is None:
            self._check_an_auth_key('OS_USER_AUTH_KEY')
        return self._user_auth_key

    @user_auth_key.setter
    def user_auth_key(self, value):
        if getattr(self, '_user_auth_key', None) is None:
            self._set_an_auth_key('OS_USER_AUTH_KEY', value)

    def _get_headers(self, auth_name=None):
        headers = {'content-type': 'application/json'}
        if auth_name is not None:
            auth = getattr(self, auth_name + '_auth_key')
            headers.update({'authorization': 'Basic %s' % auth})
        return headers
    #
    # API methods
    #
    def create_notification(self, contents, **kwargs):
        _url = 'notifications'
        url = self.OS_URL + _url
        data = {'contents': contents,
                'app_id': self.app_id}
        data.update(kwargs)
        headers = self._get_headers('app')

        response = requests.post(data, url, headers=headers)
        return response

    def cancel_notification(self, id, app_id):
        _url = 'notifications'
        url = self.OS_URL + _url + '/' + id + '?app_id=' + app_id
        headers = self._get_headers('app')

        response = requests.delete(url, headers=headers)
        return response

    def view_apps(self):
        _url = 'apps'
        url = self.OS_URL + _url
        headers = self._get_headers('user')

        response = requests.get(url, headers=headers)
        return response
        
    def view_an_app(self, app_id):
        _url = 'apps'
        url = self.OS_URL + _url + '/' + app_id
        headers = self._get_headers('user')

        response = requests.get(url, headers=headers)
        return response

    def create_an_app(self, **kwargs):
        _url = 'apps'
        url = self.OS_URL + _url
        headers = self._get_headers('user')

        response = requests.post(url, data=kwargs, headers=headers)
        return response
        
    def update_an_app(self, app_id, **kwargs):
        _url = 'apps'
        url = self.OS_URL + _url + '/' + app_id
        headers = self._get_headers('user')

        response = requests.put(url, data=kwargs, headers=headers)
        return response

    def view_devices(self, limit=None, offset=None):
        _url = 'players'
        url = self.OS_URL + _url + '/?app_id=' + self.app_id
        if limit is not None:
            url += '&limit=' + str(limit)
        if offset is not None:
            url += '&offset=' + str(offset)
        headers = self._get_headers('app')

        response = requests.get(url, headers=headers)
        return response

    def view_device(self, device_id):
        _url = 'players'
        url = self.OS_URL + _url + '/' + device_id + '?app_id=' + self.app_id
        headers = self._get_headers()

        response = requests.get(url, headers=headers)
        return response

    def add_a_device(self, **kwargs):
        _url = 'players'
        url = self.OS_URL + _url
        kwargs.update({'app_id': self.app_id})
        headers = self._get_headers()

        response = requests.post(url, data=kwargs, headers=headers)
        return response

    def edit_device(self, device_id, **kwargs):
        _url = 'players'
        url = self.OS_URL + _url + '/' + device_id
        kwargs.update({'app_id': self.app_id})
        headers = self._get_headers()

        response = requests.put(url, data=kwargs, headers=headers)
        return response

    def new_session(self, device_id, **kwargs):
        _url = 'players'
        url = self.OS_URL + _url + '/' + device_id + '/on_session'
        headers = self._get_headers()

        response = requests.post(url, data=kwargs, headers=headers)
        return response

    def new_purchase(self, device_id, **kwargs):
        _url = 'players'
        url = self.OS_URL + _url + '/' + device_id + '/on_purchase'
        headers = self._get_headers()

        response = requests.post(url, data=kwargs, headers=headers)
        return response

    def increment_session_length(self, device_id, active_time):
        _url = 'players'
        url = self.OS_URL + _url + '/' + device_id + '/on_focus'
        data = {'state': 'ping', 'active_time': active_time}
        headers = self._get_headers()

        response = requests.post(url, data=data, headers=headers)
        return response

    def csv_export(self, **kwargs):
        _url = 'players'
        url = self.OS_URL + _url + '/csv_export' + '?app_id=' + self.app_id
        data = {'extra_fields': list(kwargs.keys())}
        headers = self._get_headers('app')

        response = requests.post(url, data=data, headers=headers)
        return response

    def view_notification(self, notification_id):
        _url = 'notifications'
        url = (self.OS_URL + _url + '/' + notification_id
               + '?app_id=' + self.app_id)
        headers = self._get_headers('user')

        response = requests.get(url, headers=headers)
        return response

    def view_notifications(self, limit=None, offset=None):
        _url = 'notifications'
        url = self.OS_URL + _url + '/' + '?app_id=' + self.app_id
        if limit is not None:
            url += '&limit=' + str(limit)
        if offset is not None:
            url += '&offset=' + str(offset)
        headers = self._get_headers('app')

        response = requests.get(url, headers=headers)
        return response

    def track_open(self, notification_id):
        _url = 'notifications'
        url = self.OS_URL + _url + '/' + notification_id
        data = {'app_id': self.app_id,
                'opened': True}
        headers = self._get_headers()

        response = requests.put(url, data=data, headers=headers)
        return response


client = Client()
