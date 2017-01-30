import os

import requests


class ImproperlyConfigured(Exception):
    pass

APP_AUTH_METHODS = ['create_notification', ]
USER_AUTH_METHODS = ['view_apps', ]


def add_headers(f):
    """Decorator that adds the corresponding header to each method"""

    def deco(self, *args, **kwargs):
        if f.__name__ in APP_AUTH_METHODS:
            auth = 'app'
        elif f.__name__ in USER_AUTH_METHODS:
            auth = 'user'
        kwargs.update({'headers': client._get_headers(auth)})
        f(self, *args, **kwargs)
    return deco



class Client:
    """To use the client you need an User Auth Key or an App Auth Key[0]
    depending on the methods you want to call. They can be set as
    environment variables 'OS_USER_AUTH_KEY' and 'OS_APP_AUTH_KEY' or
    assigned to the client via `app_auth_key` and `user_auth_key`.

    0 - https://documentation.onesignal.com/docs/accounts-and-keys

    """

    OS_URL = 'https://onesignal.com/api/v1/'

    def _check_an_auth_key(self, key_name):
        value = os.environ.get(key_name, None)
        if value is None:
            raise ImproperlyConfigured(("An Auth Key missing. You can set "
                                        "it through the '%s' environment "
                                        "variable or the 'app_auth_key' "
                                        "argument." % key_name))
        self._set_an_auth_key(key_name, value)

    def _set_an_auth_key(self, key_name, value):
        attr_name = key_name[3:] if key_name.startswith('OS_')  else key_name
        setattr(self, '_' + attr_name.lower(), value)

    @property
    def app_auth_key(self):
        self._check_an_auth_key('OS_APP_AUTH_KEY')
        return self._app_auth_key

    @app_auth_key.setter
    def app_auth_key(self, value):
        if getattr(self, '_app_auth_key', None) is None:
            self._set_an_auth_key('OS_APP_AUTH_KEY', value)

    @property
    def user_auth_key(self):
        self._check_an_auth_key('OS_USER_AUTH_KEY')
        return self._app_auth_key

    @user_auth_key.setter
    def user_auth_key(self, value):
        if getattr(self, '_user_auth_key', None) is None:
            self._set_an_auth_key('OS_USER_AUTH_KEY', value)

    def _get_headers(self, auth_name):
        auth = getattr(self, auth_name + '_auth_key')
        headers = {'content-type': 'application/json',
                   'authorization': 'Basic %s' % auth}
        return headers
    #
    # API methods
    #
    @add_headers
    def create_notification(self, contents, **kwargs):
        _url = 'notifications'
        url = self.OS_URL + _url
        data = {'contents': contents,
                'app_id': self.app_auth_key}
        data.update(kwargs)

        response = requests.post(data, url, **kwargs)

    def cancel_notification(self, id, app_id):
        _url = 'notifications'
        url = self.OS_URL + _url + '/' + id + '?app_id=' + app_id

        response = requests.delete(url)


client = Client()
