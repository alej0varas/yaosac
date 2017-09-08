======
 Why?
======

I don't like exisiting libraries.

This client is a mapping of the `RESTful server API <https://documentation.onesignal.com/reference>`_. There is a method for every API end-point with the corresponding arguments. Only two methods raise an exception `create_notification` and `view_notification`. In all the other cases you will get the errors from the API in the response.

Install
-------
::

   pip install yaosac

Usage
-----
::

   import yaosac
   yaosac.client.create_notification(player_ids)

   notification_id = 'a-notification-id-you-keep-somewhere'
   notification = yaosac.client.view_notification(notification_id)

Contribution/Testing
--------------------
::

   python setup.py test
