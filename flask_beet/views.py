# -*- coding: utf-8 -*-
import os
from flask import (
    Blueprint,
    session,
    request,
    redirect,
    url_for,
    flash,
    current_app as app,
    render_template,
    send_file,
)
from flask_security import login_user

from . import forms, signals

bp = Blueprint("beet", __name__, template_folder="templates", url_prefix="/beet")


@bp.route("/login", methods=["POST", "GET"])
def login():
    """ This is the main endpoint. It presents a login
        form from /beet/login.html and deals with loggin in a user
    """
    beet_login_form = forms.SignedMessageLoginForm()
    if request.method == "POST" and beet_login_form.validate_on_submit():
        if beet_login_form.message.signedMessage.plain_message != session.get(
            app.config.get("BEET_UNIQUE_MESSAGE_SESSION_KEY")
        ):
            flash(
                app.config.get("BEET_INVALID_PAYLOAD_MESSAGE", "ERRORORORORO"), "error"
            )
            return redirect(url_for(".login"))

        account_name = beet_login_form.message.signedMessage.signed_by_name
        user = beet_login_form.user
        if user:
            login_user(user, remember=app.config.get("BEET_REMEMBER"))
            signals.beet_logged_in.send(
                app._get_current_object(),
                user=user,
                message=beet_login_form.message.data,
            )
            return redirect(
                request.args.get("next") or app.config.get("BEET_POST_LOGIN_VIEW")
            )
        else:
            session[
                app.config.get("BEET_ONBOARDING_MESSAGE_KEY")
            ] = beet_login_form.message.data
            session[app.config.get("BEET_ONBOARDING_ACCOUNT_NAME_KEY")] = account_name
            session["_next"] = request.args.get("next") or app.config.get(
                "BEET_POST_LOGIN_VIEW"
            )
            signals.beet_onboarding.send(
                app._get_current_object(),
                user=user,
                message=beet_login_form.message.data,
            )
            return redirect(app.config.get("BEET_ONBOARDING_VIEW"))

    return render_template(app.config.get("BEET_LOGIN_TEMPLATE"), **locals(), app=app)


@bp.route("/img/beet.png")
def beet_logo():
    """ Return the BEET logo
    """
    path = os.path.join(os.path.dirname(__file__), "static", "img", "beet.png")
    return send_file(path)


@bp.route("/js/beet.js")
def beet_js():
    """ Return the BEET logo
    """
    path = os.path.join(os.path.dirname(__file__), "static", "js", "beet-js.js")
    return send_file(path)
