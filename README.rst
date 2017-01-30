======
 Why?
======

I don't like exisiting libraries.

This client is a mapping of the `RESTful server API <https://documentation.onesignal.com/reference>`_. There is a method for every API end-point with the corresponding arguments avoiding validation. You'll get the errors from the API in the response.

Install
-------
::

   pip install yaosac

Usage
-----
::

   import yaosac
   client = yaosac.Client()
   client.create_notification(player_ids)

Contribution/Testing
--------------------
::

   python setup.py test
