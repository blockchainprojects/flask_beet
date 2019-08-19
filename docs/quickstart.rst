Flask-Beet Quickstart Guide
===========================

Installation
------------

You can install flask_beet via `pip`:::

    pip3 install flask_beet

Integration
-----------

After installation, you can integrate this extension by loading it
with:::

    from flask import Flask
    from flask_beet import Beet
    app = Flask(__name__)
    beet = Beet(app)

or using the factory method:::

    from flask import Flask
    from flask_beet import Beet
    app = Flask(__name__)
    beet = Beet()

    # elsewhere
    from . import beet
    beet.init_app(app)

Additionally to that, you have to include the `BeetMixin` into use user
model:::

   from flask_beet import BeetMixin

   # Replace
   -class User(db.Model, UserMixin):

   # with
   +class User(db.Model, UserMixin, BeetMixin):

Usage
-----

The extension will come with a new endpoint:::

    /beet/login

That deals with beet login.

Configuration
-------------

Configuration variables are::

    "BEET_ONBOARDING_VIEW": "/register",
    "BEET_INVALID_PAYLOAD_MESSAGE": "Invalid payload!",
    "BEET_UNIQUE_MESSAGE_GENERATOR": unique_request_id,
    "BEET_UNIQUE_MESSAGE_SESSION_KEY": "_signed_message_payload",
    "BEET_ONBOARDING_ACCOUNT_NAME_KEY": "_onboarding_account_name",
    "BEET_ONBOARDING_MESSAGE_KEY": "_onboarding_message",
    "BEET_LOGIN_TEMPLATE": "/beet/login.html",
    "BEET_REMEMBER": True,
