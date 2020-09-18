#!/usr/bin/env python

import os, datetime, hashlib, hmac, logging, socket, argparse
import ujson, redis
from bottle import route, request, response, redirect, error, default_app, view, static_file, template, HTTPError
from bottle.ext.websocket import GeventWebSocketServer
from bottle.ext.websocket import websocket

def set_content_type(fn):
	def _return_type(*args, **kwargs):
		if request.headers.get('Accept') == "application/json":
			response.headers['Content-Type'] = 'application/json'
		if request.headers.get('Accept') == "text/plain":
			response.headers['Content-Type'] = 'text/plain'
		if request.method != 'OPTIONS':
			return fn(*args, **kwargs)
	return _return_type

def enable_cors(fn):
	def _enable_cors(*args, **kwargs):
		response.headers['Access-Control-Allow-Origin'] = '*'
		response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
		response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

		if request.method != 'OPTIONS':
			return fn(*args, **kwargs)
	return _enable_cors

def returnError(code, msg, contentType="text/plain"):
	response.status = int(code)
	response.content_type = contentType
	return msg

@route('/favicon.ico')
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
		f = open(os.getenv('VERSION_PATH', '{}/.git/refs/heads/master'.format(dirname)), 'r')
		content = f.read()
		response.content_type = 'text/plain'
		return content
	except:
		return "Unable to open version file."

@route('/<id>', method='GET')
@route('/count/<id>', method='GET')
@set_content_type
@enable_cors
def counter_get(id):
	if not r.get(id):
		return returnError(404, "Counter not found")

	counter = ujson.loads(r.get(id))

	# And return our success message
	content = {
		"id": id,
		"name": counter["name"],
		"buttonText": counter["buttonText"],
		"value": counter["value"]
	}

	if response.content_type == "application/json":
		return returnError(200, ujson.dumps(content), "application/json")
	else:
		return template('counter', content)

@route('/<id>', method='POST')
@route('/count/<id>', method='POST')
def counter_create(id):
	if id == "create":
		# We're going to create a new counter, and return a JSON blob of the URL
		counter_id = hashlib.sha224(os.urandom(9)).hexdigest()[:9]
		counter_name = request.forms.get('counterName')
		counter_buttonText = request.forms.get('counterButton')

		# Deal with empty submissions by providing example data
		if counter_name in ["", None]:
			counter_name = "Untitled"
		if counter_buttonText in ["", None]:
			counter_buttonText = "Click Here"

		
		r.set(counter_id, ujson.dumps({
			'name': counter_name,
			'buttonText': counter_buttonText,
			'value': 0
		}))

		if request.query.method == 'web':
			return redirect("/" + counter_id)
		else:
			content = {
				"id": counter_id,
				"url": "https://count.re/{}".format(counter_id),
			}
			return returnError(200, ujson.dumps(content), "application/json")
	else:
		try:
			if not r.get(id):
				log.info("{} is not currently active, and therefore will not be incremented".format(id))
				raise KeyError

			counter = ujson.loads(r.get(id))

			# We found the key, so now we can increment it
			counter['value'] = counter['value'] + 1
			r.set(id, ujson.dumps(counter))

			global visitors
			for visitor in visitors:
				visitor.send(r.get(id))

		except KeyError:
			return returnError(404, "Counter not found")
			
		if request.query.method == 'web':
			return redirect("/{}".format(id))
		else:
			return returnError(200, "Successfully updated value for {}".format(id))

@route('/websocket', apply=[websocket])
def websocket(ws):
	global visitors
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

	parser = argparse.ArgumentParser()

	# Server settings
	parser.add_argument("-i", "--host", default=os.getenv('HOST', '127.0.0.1'), help="server ip")
	parser.add_argument("-p", "--port", default=os.getenv('PORT', 5000), help="server port")

	# Redis settings
	parser.add_argument("--redis", default=os.getenv('REDIS', 'redis://localhost:6379'), help="redis connection string")

	# Application settings
	parser.add_argument("--secret", default=os.getenv('SECRET', ''), help="seed for secrets generation")
	
	# Verbose mode
	parser.add_argument("--verbose", "-v", help="increase output verbosity", action="store_true")
	args = parser.parse_args()

	if args.verbose:
		logging.basicConfig(level=logging.DEBUG)
	else:
		logging.basicConfig(level=logging.INFO)
	log = logging.getLogger(__name__)

	try:
		if args.redis:
			r = redis.from_url(args.redis)
	except:
		log.fatal("Unable to connect to redis: {}".format(args.redis))

	if args.secret == '':
		log.error(
			'Secure tokens disabled, using empty secret. Set APP_SECRET to secure seed and restart.'
		)

	try:
		global visitors
		visitors = set()
		app = default_app()
		app.run(host=args.host, port=args.port, server=GeventWebSocketServer)
	except:
		log.error("Unable to start server on {}:{}".format(args.host, args.port))
