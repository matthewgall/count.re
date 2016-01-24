#!/usr/bin/env python

import os
import hashlib
import hmac
import logging
import socket

import ujson
from bottle import route, request, response, redirect, error, default_app, view, static_file, template, HTTPError
from tinydb import TinyDB, Query
from tinydb.operations import increment

def mailgunVerify(mail_token, mail_timestamp, mail_signature):
    return mail_signature == hmac.new(
        key=mailgunToken,
        msg='{}{}'.format(mail_timestamp, mail_token),
        digestmod=hashlib.sha256).hexdigest()

def returnError(code, msg, contentType="text/plain"):
    response.status = int(code)
    response.content_type = contentType
    return msg

@route('/favicon.ico')
@route('/import/mailgun', method='GET')
@error(404)
def error404():
    response.status = 404
    return "Not Found"

@error(403)
def error403(error):
    response.status = 403
    return 'Access forbidden'

@route('/static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root='views/static')

@route('/version')
def return_version():
    try:
        dirname, filename = os.path.split(os.path.abspath(__file__))
        del filename
        f = open(os.getenv('VERSION_PATH', dirname + '/.git/refs/heads/master'), 'r')
        content = f.read()
        response.content_type = 'text/plain'
        return content
    except:
        return "Unable to open version file."

@route('/import/mailgun', method="POST")
def incrementCountMail():

    if mailgunToken == '':
        log.error('MAILGUN_TOKEN not set. E-mail processing disabled.')
        return returnError(404, "MAILGUN_TOKEN not set. E-mail processing disabled.")

    try:
        email_address = request.forms.get('sender')
        email_recipient = request.forms.get('recipient')
        email_subject = request.forms.get('subject')

        email_token = request.forms.get('token')
        email_timestamp = request.forms.get('timestamp')
        email_signature = request.forms.get('signature')

        counter_id = email_recipient.split('@')[0]
    except AttributeError:
        return returnError(200, "Bad request, data received was in an unexpected format")

    if not mailgunVerify(email_token, email_timestamp, email_signature):
        log.info("Discarding e-mail from " + email_address, " , signature verification failed")
        return returnError(200, "Signature verification failed")
    else:
        log.info("Accepted e-mail from " + email_address + ", (recipient: " + email_recipient + ")")

    # Now, we are going to determine if the counter is active
    if len(db.search(counter.id == counter_id)) < 1:
        log.info(counter_id + " is not currently active, and therefore will not be incremented")
        return returnError(200, "Counter not found")

    # We found the key, so now we can increment it
    db.update(increment('value'), counter.id == counter_id)

    # And return our success message
    log.info("Successfully incremented counter: " + counter_id)
    return returnError(200, "Successfully updated value for " + counter_id)

@route('/count/<id>', method='GET')
def getCounter(id):

    # Find the counter
    count_info = db.search(counter.id == id)

    if len(count_info) < 1:
        return returnError(404, "Counter not found")

    # And return our success message
    content = {
        "id": id,
        "name": count_info[0]["name"],
        "buttonText": count_info[0]["buttonText"],
        "value": count_info[0]["value"],
        "logs": []
    }

    return template('counter',
        id = id,
        name = count_info[0]["name"],
        buttonText = count_info[0]["buttonText"],
        value = count_info[0]["value"]
    )
    # return returnError(200, ujson.dumps(content), "application/json")

@route('/count/<id>', method='POST')
def incrementCounter(id):
    if id == "create":
        # We're going to create a new counter, and return a JSON blob of the URL
        counter_id = hashlib.sha224(os.urandom(9)).hexdigest()[:9]
        counter_name = request.forms.get('counterName')
        counter_buttonText = request.forms.get('counterButton')

        # Deal with empty submissions by providing example data
        if counter_name == "" or counter_name == None:
            counter_name = "Untitled"
        if counter_buttonText == "" or counter_buttonText == None:
            counter_buttonText = "Click Here"

        # Now, we create the counter using the information we have
        db.insert({
            'id': counter_id,
            'name': counter_name,
            'buttonText': counter_buttonText,
            'value': 0
        })

        # And now that is done, we'll return a success message, or a redirect
        log.info("Successfully created counter: " + counter_id)

        if request.query.method == 'web':
            return redirect("/count/" + counter_id)
        else:
            content = {
                "id": counter_id,
                "url": "https://count.re/count/" + counter_id,
            }
            return returnError(200, ujson.dumps(content), "application/json")
    else:
        # We are going to determine if the counter is active
        if len(db.search(counter.id == id)) < 1:
            log.info(id + " is not currently active, and therefore will not be incremented")
            return returnError(404, "Counter not found")

        # We found the key, so now we can increment it
        db.update(increment('value'), counter.id == id)

        # And return our success message
        log.info("Successfully incremented counter: " + id)
        
        if request.query.method == 'web':
            return redirect("/count/" + id)
        else:
            return returnError(200, "Successfully updated value for " + id)

@route('/')
def index():
    return template('home')

if __name__ == '__main__':

    app = default_app()

    appReload = bool(os.getenv('APP_RELOAD', False))
    appSecret = os.getenv('APP_SECRET', '')

    serverHost = os.getenv('SERVER_HOST', 'localhost')
    serverPort = os.getenv('SERVER_PORT', '5000')

    mailgunToken = os.getenv('MAILGUN_TOKEN', '')
    logentriesToken = os.getenv('LOGENTRIES_TOKEN', '')

    # Now we're ready, so start the server
    # Instantiate the logger
    log = logging.getLogger('log')
    console = logging.StreamHandler()
    log.setLevel(logging.INFO)
    log.addHandler(console)

    if logentriesToken != '':
        log.addHandler(LogentriesHandler(logentriesToken))

    if appSecret == '':
        log.error(
            'Secure tokens disabled, using empty secret. Set APP_SECRET to secure seed and restart.'
        )

    if mailgunToken == '':
        log.error(
            'Unable to connect to mailgun API. Incrementing counters via e-mail will be disabled.'
        )

    # Instantiate a connection to the database
    db = TinyDB(os.getenv('APP_DATABASE', 'db/app.json'))
    counter = Query()

    # Now we're ready, so start the server
    try:
        log.info("Successfully started application server on " + socket.gethostname())
        app.run(host=serverHost, port=serverPort, reloader=bool(appReload))
    except:
        log.error("Failed to start application server on " + socket.gethostname())
