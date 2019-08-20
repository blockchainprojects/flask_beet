# -*- coding: utf-8 -*-
from datetime import datetime
from flask import Flask
from flask_testing import TestCase

from flask_sqlalchemy import SQLAlchemy
from flask_beet import Beet, BeetMixin
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin

# SQLAlchemy
db = SQLAlchemy()

roles_users = db.Table(
    "roles_users",
    db.Column("user_id", db.Integer(), db.ForeignKey("users.id")),
    db.Column("role_id", db.Integer(), db.ForeignKey("roles.id")),
)


class Role(db.Model, RoleMixin):

    __tablename__ = "roles"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __init__(self, name, description):
        self.name = name
        self.description = description


class User(db.Model, UserMixin, BeetMixin):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255))
    password = db.Column(db.String(120))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(100))
    current_login_ip = db.Column(db.String(100))
    login_count = db.Column(db.Integer)

    # Relationships
    roles = db.relationship(
        "Role", secondary=roles_users, backref=db.backref("users", lazy="dynamic")
    )


_signed_message = """-----BEGIN BITSHARES SIGNED MESSAGE-----
abcdefg
-----BEGIN META-----
account=xeroc
memokey=BTS5TPTziKkLexhVKsQKtSpo4bAv5RnB8oXcG4sMHEwCcTf3r7dqE
block=40213027
timestamp=2019-08-19T11:02:18
-----BEGIN SIGNATURE-----
1f210458337f3cf13b80c46ae04b5cfe8ee2ff094bc559fbb663a5cd345015cfec24b3dafc111fbdb7099c347885eb96e8453d3fb2b72e23e3e9e446fb61540464
-----END BITSHARES SIGNED MESSAGE-----"""

_invalid_signed_message = """-----BEGIN BITSHARES SIGNED MESSAGE-----
abcdefg
-----BEGIN META-----
account=xeroc
memokey=BTS5TPTziKkLexhVKsQKtSpo4bAv5RnB8oXcG4sMHEwCcTf3r7dqE
block=40213027
timestamp=2019-08-19T11:02:18
-----BEGIN SIGNATURE-----
1f2104580464
-----END BITSHARES SIGNED MESSAGE-----"""

_invalid_signature_signed_message = """-----BEGIN BITSHARES SIGNED MESSAGE-----
abcsfasFasfasf
-----BEGIN META-----
account=xeroc
memokey=BTS5TPTziKkLexhVKsQKtSpo4bAv5RnB8oXcG4sMHEwCcTf3r7dqE
block=40213027
timestamp=2019-08-19T11:02:18
-----BEGIN SIGNATURE-----
1f210458337f3cf13b80c46ae04b5cfe8ee2ff094bc559fbb663a5cd345015cfec24b3dafc111fbdb7099c347885eb96e8453d3fb2b72e23e3e9e446fb61540464
-----END BITSHARES SIGNED MESSAGE-----"""

_invalid_payload_signed_message = """-----BEGIN BITSHARES SIGNED MESSAGE-----
sfasfasas
-----BEGIN META-----
account=xeroc
memokey=BTS5TPTziKkLexhVKsQKtSpo4bAv5RnB8oXcG4sMHEwCcTf3r7dqE
block=40215253
timestamp=2019-08-19T12:53:45
-----BEGIN SIGNATURE-----
2033d1e0b276941849a3575bcd0d802b9befeb6177065dbbe0a6e11872e84e31e42e2e3357691744cdbace60b3336b89f1bb38c45f335c0ea08673b2e92288c6a9
-----END BITSHARES SIGNED MESSAGE-----"""


class TestCases(TestCase):
    def create_app(self):
        app = Flask(__name__)
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        app.config["SECRET_KEY"] = "foobar"
        app.config["BEET_UNIQUE_MESSAGE_GENERATOR"] = lambda: "abcdefg"
        app.config["WTF_CSRF_ENABLED"] = False
        app.config["SECURITY_CONFIRMABLE"] = True
        self.beet = Beet(app)
        self.db = db.init_app(app)
        self.security = Security(app, SQLAlchemyUserDatastore(db, User, Role))
        return app

    def setUp(self):
        db.create_all()

    def setup_user(self):
        self.user = User(active=1, confirmed_at=datetime.utcnow())
        self.user.set_beet_account_name("xeroc")
        db.session.add(self.user)
        db.session.commit()
        db.session.refresh(self.user)

        self.assertEqual(self.user.get_beet_account_name(), "xeroc")

    def test_form(self):
        rep = self.client.get("/beet/login")
        self.assertEqual(rep.status_code, 200)
        self.assertIn(b"form", rep.data)
        self.assertIn(b"abcdefg", rep.data)
        self.assertIn(b'id="signedMessage"', rep.data)

    def test_login(self):
        rep = self.client.get("/beet/login")
        rep = self.client.post(
            "/beet/login", data=dict(message=_signed_message, submit="Login")
        )
        self.assertEqual(rep.status_code, 302)
        self.assertTrue(
            rep.location.endswith(self.app.config.get("BEET_ONBOARDING_VIEW"))
        )

    def test_login_existing(self):
        self.setup_user()
        rep = self.client.get("/beet/login")
        rep = self.client.post(
            "/beet/login", data=dict(message=_signed_message, submit="Login")
        )
        self.assertEqual(rep.status_code, 302)
        self.assertTrue(
            rep.location.endswith(self.app.config.get("BEET_POST_LOGIN_VIEW"))
        )

    def test_login_invalidsignature(self):
        self.setup_user()
        rep = self.client.get("/beet/login")
        rep = self.client.post(
            "/beet/login", data=dict(message=_invalid_signed_message, submit="Login")
        )
        self.assertEqual(rep.status_code, 200)
        self.assertIn(b"No Decoder accepted the message", rep.data)

    def test_login_invalidsig(self):
        self.setup_user()
        rep = self.client.get("/beet/login")
        rep = self.client.post(
            "/beet/login",
            data=dict(message=_invalid_signature_signed_message, submit="Login"),
        )
        self.assertEqual(rep.status_code, 200)
        self.assertIn(b"The signature doesn&#39;t match the memo key", rep.data)

    def test_login_invalidpayload(self):
        self.setup_user()
        rep = self.client.get("/beet/login")
        rep = self.client.post(
            "/beet/login",
            data=dict(message=_invalid_payload_signed_message, submit="Login"),
            follow_redirects=True,
        )
        self.assertEqual(rep.status_code, 200)
        self.assertIn(b"Invalid payload!", rep.data)

    def test_login_unconfirmed_user(self):
        self.setup_user()
        self.user.confirmed_at = None
        db.session.commit()
        rep = self.client.get("/beet/login")
        rep = self.client.post(
            "/beet/login", data=dict(message=_signed_message, submit="Login")
        )
        self.assertEqual(rep.status_code, 200)
        self.assertIn(b"Email requires confirmation.", rep.data)

    def test_login_inactive_user(self):
        self.setup_user()
        self.user.active = False
        rep = self.client.get("/beet/login")
        rep = self.client.post(
            "/beet/login", data=dict(message=_signed_message, submit="Login")
        )
        self.assertEqual(rep.status_code, 200)
        self.assertIn(b"Account is disabled.", rep.data)

    def test_image(self):
        rep = self.client.get("/beet/img/beet.png")
        self.assertEqual(rep.status_code, 200)

    def test_js(self):
        rep = self.client.get("/beet/js/beet.js")
        self.assertEqual(rep.status_code, 200)
