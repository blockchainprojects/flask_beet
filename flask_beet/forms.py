# -*- coding: utf-8 -*-
from flask import current_app as app
from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError
from bitshares.message import Message
from flask_security.confirmable import requires_confirmation
from flask_security.utils import get_message
from werkzeug.local import LocalProxy

# Convenient references
_security = LocalProxy(lambda: app.extensions["security"])
_datastore = LocalProxy(lambda: _security.datastore)
_user = LocalProxy(lambda: _datastore.user_model)


class ValidSignedMessage:
    """ This Validator is used to check the signed message

        It will return (unless exception is raised) an object that has
        additional attributes:

            * field.signed_by_account
            * field.signed_by_name
            * field.plain_message

    """

    def __init__(self, message="Message invalid!"):
        self.message = message

    def __call__(self, FlaskForm, field):
        try:
            field.signedMessage = Message(field.data)
            ret = field.signedMessage.verify()
        except Exception as e:
            raise ValidationError(str(e))
        if not ret:  # pragma: no cover
            raise ValidationError(self.message)
        field.signed_by_account = field.signedMessage.signed_by_account
        field.signed_by_name = field.signedMessage.signed_by_name
        field.plain_message = field.signedMessage.plain_message


class SignedMessageLoginForm(FlaskForm):
    """ The login form only requires a TextArea and a submit button
    """

    message = TextAreaField(
        "Signed Message", [DataRequired(), ValidSignedMessage()], id="signedMessage"
    )
    submit = SubmitField("Login")

    def validate(self):
        if not super(SignedMessageLoginForm, self).validate():
            return False
        self.user = _user.find_beet_account_name(self.message.signed_by_name)
        if self.user and requires_confirmation(self.user):
            self.message.errors.append(get_message("CONFIRMATION_REQUIRED")[0])
            return False
        if self.user and not self.user.is_active:
            self.message.errors.append(get_message("DISABLED_ACCOUNT")[0])
            return False
        return True
