======
 Why?
======

I don't like exisiting libraries.

This client is a mapping of the `RESTful server API
<https://documentation.onesignal.com/reference>`_. There is a method
for every API end-point with the corresponding arguments. Only two
methods raise an exception `create_notification` and
`view_notification`. In all the other cases you will get the errors
from the API in the response.

Client's methods names are the end-point name in lower case with
spaces replaced by underscores. Depending on the method you call you
will need an `User Auth Key or an App Auth Key or an App Id
<https://documentation.onesignal.com/docs/accounts-and-keys>`_. They
can be set as environment variables 'OS_USER_AUTH_KEY',
'OS_APP_AUTH_KEY' and 'OS_APP_ID' or assigned to the client via
`app_auth_key`, `user_auth_key` and `app_id` attributes.


Install
-------
::

   pip install yaosac

Usage
-----
::

   import yaosac

   # Send a notification
   yaosac.client.create_notification(player_ids)

   # Get a notification
   notification_id = 'a-notification-id-you-keep-somewhere'
   notification = yaosac.client.view_notification(notification_id)

Contribution/Testing
--------------------
::

   python3 setup.py test
