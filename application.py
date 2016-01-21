#!/usr/bin/env python

import os
import sys
import json
import hashlib
import hmac
import logging
import socket

from bottle import route, request, response, error, default_app, view, static_file
from tinydb import TinyDB, where

def mailgunVerify(os.getenv('MAILGUN_TOKEN'), token, timestamp, signature):
	return signature == hmac.new(
		key=api_key,
		msg='{}{}'.format(timestamp, token),
		digestmod=hashlib.sha256).hexdigest()

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
		
@route('/import/mailgun')
def incrementCountMail():
	return True

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
	
	# Now we're ready, so start the server
	# Instantiate the logger
	log = logging.getLogger('log')
	console = logging.StreamHandler()
	log.setLevel(logging.INFO)
	log.addHandler(console)

	if os.getenv('LOGENTRIES_TOKEN', '') != '':
		log.addHandler(LogentriesHandler(os.getenv('LOGENTRIES_TOKEN', '')))

	if os.getenv('MAILGUN_TOKEN', '') == '':
		log.error('Failed to connect to the Mailgun API.')
		exit(1)

	# Now we're ready, so start the server
	try:
		log.info("Successfully started application server on " + socket.gethostname())
		app.run(host=serverHost, port=serverPort)
	except:
		log.error("Failed to start application server on " + socket.gethostname())
