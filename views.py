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
from flask_security import url_for_security, login_user
from werkzeug.local import LocalProxy

from . import forms, signals

bp = Blueprint("beet", __name__, template_folder="templates")

# Convenient references
_security = LocalProxy(lambda: app.extensions["security"])
_datastore = LocalProxy(lambda: _security.datastore)
_db = LocalProxy(lambda: _datastore.db)
_user = LocalProxy(lambda: _datastore.user_model)


def _user_loader(account_name):
    return _security.datastore.find_user(account_name=account_name)


@bp.route("/login/beet/", methods=["POST", "GET"])
def login():
    loginForm = forms.SignedMessageLoginForm()
    if request.method == "POST" and loginForm.validate_on_submit():
        if (
            loginForm.message.signedMessage.plain_message
            != session[app.config.get("BEET_UNIQUE_MESSAGE_SESSION_KEY")]
        ):
            flash(app.config.get("BEET_INVALID_PAYLOAD_MESSAGE"), "error")
            return redirect(url_for(".login"))

        account_name = loginForm.message.signedMessage.signed_by_name
        user = _user.find_beet_account_name(account_name)
        if user:
            login_user(user, remember=True)
            signals.beet_logged_in.send(
                app._get_current_object(), user=user, message=loginForm.message.data
            )
            return redirect(
                request.args.get("next") or app.config.get("SECURITY_POST_LOGIN_VIEW")
            )
        else:
            session[
                app.config.get("BEET_ONBOARDING_MESSAGE_KEY")
            ] = loginForm.message.data
            session[app.config.get("BEET_ONBOARDING_ACCOUNT_NAME_KEY")] = account_name
            session["_next"] = request.args.get("next") or app.config.get(
                "SECURITY_POST_LOGIN_VIEW"
            )
            signals.beet_onboarding.send(
                app._get_current_object(), user=user, message=loginForm.message.data
            )
            return redirect(app.config.get("BEET_ONBOARDING_VIEW"))

    return render_template("beet/login.html", **locals())


@bp.route("/login/beet/img/beet.png")
def beet_logo():
    path = os.path.join(os.path.dirname(__file__), "img", "beet.png")
    return send_file(path)
