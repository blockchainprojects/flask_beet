# Flask-Beet Extension

[![build status](https://secure.travis-ci.org/blockchainprojects/flask_beet.png?branch=master)](https://travis-ci.org/#!/blockchainprojects/flask_beet)

Flask-beet is a Flask extension for allow login (flask-security/flask-login)
via signed messages and the [Beet app](http://get-beet.io).

The login requires a unique string to be signed and submitted. The signature is
created with the memo key of an account on the BitShares Blockchain,

## Installation

Install the extension with one of the following commands:

    $ pip install flask_beet

## Usage

Using SeaSurf is fairly straightforward. Begin by importing the extension and
then passing your application object back to the extension, like this:

    from flask import Flask
    from flask_beet import Beet
    app = Flask(__name__)
    beet = Beet(app)

## Documentation

The Sphinx-compiled documentation is available here: [flask-beet.rtfd.io](http://flask-beet.rtfd.io/)
