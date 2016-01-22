#!/usr/bin/env python

import os
import sys
import json
import hashlib
import hmac
import logging
import socket

from bottle import route, request, response, error, default_app, view, static_file, HTTPError
from tinydb import TinyDB, where

def mailgunVerify(mailToken, mailTimestamp, mailSignature):
	return mailSignature == hmac.new(
		key=mailgunToken,
		msg='{}{}'.format(mailTimestamp, mailToken),
		digestmod=hashlib.sha256).hexdigest()

@route('/favicon.ico')
@route('/import/mailgun', method='GET')
@error(404)
def error404():
	response.status = 404
	return 'Not Found'

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

	emailAddress = request.forms.get('sender')
	emailRecipient = request.forms.get('recipient')
	emailSubject = request.forms.get('subject')
	
	emailToken = request.forms.get('token')
	emailTimestamp = request.forms.get('timestamp')
	emailSignature = request.forms.get('signature')
	
	if not mailgunVerify(emailToken, emailTimestamp, emailSignature):
		log.info("Discarding e-mail from " + emailAddress, " , signature verification failed")
		raise HTTPError(403)
	else:
		log.info("Accepted e-mail from " + emailAddress + ", (recipient: " + emailRecipient + ")")
		return "Accepted"

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

	if mailgunToken == '':
		log.error('Failed to connect to the Mailgun API.')
		exit(1)

	# Now we're ready, so start the server
	try:
		log.info("Successfully started application server on " + socket.gethostname())
		app.run(host=serverHost, port=serverPort)
	except:
		log.error("Failed to start application server on " + socket.gethostname())
