#!/usr/bin/env python

import os
import json
import hashlib
import hmac
import logging
import socket

from bottle import route, request, response, error, default_app, view, static_file, HTTPError
from tinydb import TinyDB, Query
from tinydb.operations import increment

def mailgunVerify(mailToken, mailTimestamp, mailSignature):
    return mailSignature == hmac.new(
        key=mailgunToken,
        msg='{}{}'.format(mailTimestamp, mailToken),
        digestmod=hashlib.sha256).hexdigest()

def returnError(code, msg):
    response.status = int(code)
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
        log.error('Received call to /import/mailgun with MAILGUN_TOKEN not set. E-mail processing disabled.')
        return returnError(404, "MAILGUN_TOKEN not set. E-mail processing disabled.")
    
    try:
        emailAddress = request.forms.get('sender')
        emailRecipient = request.forms.get('recipient')
        emailSubject = request.forms.get('subject')
        
        emailToken = request.forms.get('token')
        emailTimestamp = request.forms.get('timestamp')
        emailSignature = request.forms.get('signature')
        
        counterID = emailRecipient.split('@')[0]
    except AttributeError:
        return returnError(400, "Bad request, data received was in an unexpected format")
        
    if not mailgunVerify(emailToken, emailTimestamp, emailSignature):
        log.info("Discarding e-mail from " + emailAddress, " , signature verification failed")
        return returnError(401, "Signature verification failed")
    else:
        log.info("Accepted e-mail from " + emailAddress + ", (recipient: " + emailRecipient + ")")

    # Now, we are going to determine if the counter is active
    if len(db.search(counter.id == counterID)) < 1:
        log.info(counterID + " is not currently active, and therefore will not be incremented")
        return returnError(404, "Counter not found")
    
    # We found the key, so now we can increment it
    db.update(increment('value'), counter.id == counterID)
    
    # And return our success message
    log.info("Successfully incremented counter: " + counterID)
    return returnError(200, "Successfully updated value for " + counterID)
    
@route('/count/<id>', method='GET')
def getCounter(id):
    return getCounter
    
@route('/count/<id>', method='POST')
def incrementCounter(id):
    return getCounter

@route('/')
def index():
    return "Hello, world!"

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
        log.addHandler(LogentriesHandler(os.getenv('LOGENTRIES_TOKEN', '')))

    if appSecret == '':
        log.error('Secure tokens disabled, using empty secret. Cookies will not be encrypted. Set APP_SECRET to secure seed and restart.')
    
    if mailgunToken == '':
        log.error('Unable to connect to mailgun API. Incrementing counters via e-mail will be disabled. Set MAILGUN_TOKEN to your domain API key and restart.')

    # Instantiate a connection to the database
    db = TinyDB(os.getenv('APP_DATABASE', 'db/app.json'))
    counter = Query()
    
    # Now we're ready, so start the server
    try:
        log.info("Successfully started application server on " + socket.gethostname())
        app.run(host=serverHost, port=serverPort, reloader=bool(appReload))
    except:
        log.error("Failed to start application server on " + socket.gethostname())