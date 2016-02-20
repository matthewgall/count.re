#!/usr/bin/env python

import os
import hashlib
import hmac
import logging
import socket

import ujson

from bottle import route, request, response, redirect, hook, error, default_app, view, static_file, template, HTTPError
from bottle.ext.websocket import GeventWebSocketServer
from bottle.ext.websocket import websocket

from tinydb import TinyDB, Query
from tinydb.operations import increment

from pprint import pprint

class StripPathMiddleware(object):
    def __init__(self, app):
        self.app = app
    def __call__(self, e, h):
        e['PATH_INFO'] = e['PATH_INFO'].rstrip('/')
        return self.app(e,h)

def buildTelegramURI(path):
    return "https://api.telegram.org/file/" + telegramToken + path

def mailgunVerify(mail_token, mail_timestamp, mail_signature):
    return mail_signature == hmac.new(
        key=mailgunToken,
        msg='{}{}'.format(mail_timestamp, mail_token),
        digestmod=hashlib.sha256).hexdigest()

def returnError(code, msg, contentType="text/plain"):
    response.status = int(code)
    response.content_type = contentType
    return msg

@hook('before_request')
def determine_content_type():
    if request.headers.get('Accept') == "application/json":
        response.content_type = 'application/json'    
    elif request.headers.get('Accept') == "application/xml":
        response.content_type = 'application/xml'

@route('/favicon.ico')
@route('/import/mailgun', method='GET')
@error(404)
def error404():
    return returnError(404, "Not Found")

@error(403)
def error403(error):
    return returnError(403, "Access forbidden")

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

@route('/import/telegram', method="POST")
def telegram():

    if telegramToken == '':
        log.error('TELEGRAM_TOKEN not set. Telegram interface disabled.')
        return returnError(404, "TELEGRAM_TOKEN not set. Telegram interface disabled.")

    try:
        telegramObj = ujson.loads(request.body.read())
    except:
        return returnError(200, "JSON object provided by Telegram was invalid")

    try:
        telegramUser = telegramObj['message']['from']['username']
        telegramChatID = telegramObj['message']['chat']['id']
        telegramMessage = telegramObj['message']['text']
        telegramMessageArray = telegramMessage.replace('/', '').split(' ')
    except:
        return returnError(200, "JSON object provided by Telegram was invalid")

    log.info("Received message from " + telegramUser + ": " + telegramMessage)

    if telegramMessageArray[0] == "create":
        response = {
            "method": "sendMessage",
            "chat_id": telegramChatID,
            "text": "We're not ready yet, but if this had worked, I'd have made a counter"
        }
        return returnError(200, ujson.dumps(response), "application/json")
    else:
        log.info("Encountered an unknown command: " + telegramMessageArray[0])

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

@route('/<id>', method='GET')
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
        "value": count_info[0]["value"]
    }

    if response.content_type == "application/json":
        return returnError(200, ujson.dumps(content), "application/json")
    else:
        return template('counter', content)

@route('/<id>', method='POST')
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
            return redirect("/" + counter_id)
        else:
            content = {
                "id": counter_id,
                "url": "https://count.re/" + counter_id,
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
        
        # And inform the connected visitors
        count_info = db.search(counter.id == id)
        for visitor in visitors:
            visitor.send(ujson.dumps(count_info))
            
        if request.query.method == 'web':
            return redirect("/" + id)
        else:
            return returnError(200, "Successfully updated value for " + id)

@route('/websocket', apply=[websocket])
def websocket(ws):
    visitors.add(ws)
    while True:
        msg = ws.receive()
        if msg is not None:
            pass
        else: break
    visitors.remove(ws)

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
    telegramToken = os.getenv('TELEGRAM_TOKEN', '')
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

    # And an in memory database of connected users
    visitors = set()
    
    # Now we're ready, so start the server
    try:
        log.info("Successfully started application server on " + socket.gethostname())
        app.run(host=serverHost, port=serverPort, reloader=bool(appReload), server=GeventWebSocketServer)
    except:
        log.error("Failed to start application server on " + socket.gethostname())