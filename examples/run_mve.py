# -*- coding: utf-8 -*-
from datetime import datetime
from flask import Flask
from flask_testing import TestCase

from flask_sqlalchemy import SQLAlchemy
from flask_beet import Beet, BeetMixin, get_onboarding_account_name
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin
from bitshares.bitshares import BitShares
from bitshares.instance import set_shared_blockchain_instance
from flask_login import current_user

# SQLAlchemy
db = SQLAlchemy()


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
        "Role",
        secondary=db.Table(
            "roles_users",
            db.Column("user_id", db.Integer(), db.ForeignKey("users.id")),
            db.Column("role_id", db.Integer(), db.ForeignKey("roles.id")),
        ),
        backref=db.backref(
            "users",
            lazy="dynamic"
        )
    )


def create_app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = "foobar"
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["SECURITY_CONFIRMABLE"] = True

    app.config["BEET_UNIQUE_MESSAGE_GENERATOR"] = lambda: "abcdefg"

    beet = Beet(app)
    db.init_app(app)

    @app.before_first_request
    def create_db():
        db.create_all()

    security = Security(app, SQLAlchemyUserDatastore(db, User, Role))
    return app


def setup_user():
    user = User(
        active=1,
        confirmed_at=datetime.utcnow()
    )
    user.set_beet_account_name("xeroc")
    db.session.add(user)
    db.session.commit()


def run_app():
    # Decide if connecting to mainnet, or testnet,
    #  node = "wss://testnet.nodes.bitshares.ws"
    node = "wss://eu.nodes.bitshares.ws"

    bitshares = BitShares(node)
    # this will trigger flask_beet to also use this one
    set_shared_blockchain_instance(bitshares)

    app = create_app()

    @app.route("/")
    def index():
        if current_user and not current_user.is_anonymous:
            return "Logged in as " + str(current_user.beet_account_name)
        else:
            return "Visit /beet/login"

    @app.route("/register")
    def register():
        # route defined in config BEET_ONBOARDING_VIEW
        return "Unknown user, insert your registration form here. Use /register/" + get_onboarding_account_name() + " for quick & dirty test."

    @app.route("/register/<username>")
    def register_user(username):
        user = User(active=1, confirmed_at=datetime.utcnow())
        user.set_beet_account_name(username)
        db.session.add(user)
        db.session.commit()
        return "User added, try login again."

    app.logger.info("Starting minimal viable example")
    app.run(host="localhost", port=5000, debug=True)


if __name__ == "__main__":
    run_app()
