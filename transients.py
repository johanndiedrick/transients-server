import tornado.ioloop
import tornado.web
import os.path
import tornado.httpserver
import tornado.ioloop
from tornado.options import define, options
import tornado.gen
import tornado.web
import motor
import tornado.websocket
from transients_globals import aws_public_key, aws_secret_key, mongodb_uri, transients_aws_base_url, transients_s3_base_url, mapbox_public_key, mapbox_secret_key

from bson import json_util
import json

import boto
from boto.s3.connection import S3Connection
from boto.s3.key import Key

import datetime

port = 9000

# connected clients
cl = []


define("port", default=port, help="run on the given port", type=int)

class Application(tornado.web.Application):
        def __init__(self):
                handlers =      [

                                # (r"/", MainHandler),
                                (r"/", MapBHandler),
				(r"/geosounds", GeosoundsHandler),
				(r"/inserttest", InsertTestHandler),
				(r"/uploadaudio", UploadAudioHandler),
				(r"/uploadjson", UploadJSONHandler),
				(r"/map", MapHandler),
				(r"/newmap", NewMapHandler),
				(r"/mapb", MapBHandler),
				(r"/websocket", EchoWebSocketHandler)


                                ]

                settings = dict(
                                template_path=os.path.join(os.path.dirname(__file__), "templates"),
                                static_path=os.path.join(os.path.dirname(__file__), "static"),
                                debug = True,
				static_hash_cache=False
                                )


                tornado.web.Application.__init__(self, handlers, **settings)
		print 'running on port ' + str(port)
		client = motor.MotorClient(mongodb_uri)
		self.db =  client["transients-sandbox"]


class MainHandler(tornado.web.RequestHandler):
	def get(self):
		self.set_header("Access-Control-Allow-Origin", "*")
		self.write("Hello, world")

class GeosoundsHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def get(self):
		self.set_header("Access-Control-Allow-Origin", "*")
		geosounds = {}
		all_geosounds = []
		cursor = self.application.db.geosounds.find({})
		while (yield cursor.fetch_next):
			geosound = cursor.next_object()
			all_geosounds.append(geosound)
		geosounds = { "geosounds" : all_geosounds }
		self.write(json.dumps(geosounds, default=json_util.default)) #write json

		# tornado.websocket.WebSocketHandler.write_message(tornado.websocket.WebSocketHandler, "what is happening")
		for c in cl:
			c.write_message(json.dumps({'newSounds': geosounds}, default=json_util.default))

		self.finish

class InsertTestHandler(tornado.web.RequestHandler):
	def get(self):
		document = {"lat" : 40.5, "lng" : 70.3}
		self.application.db.geosounds.insert(document)

class MapHandler(tornado.web.RequestHandler):
	def get(self):
		self.set_header("Access-Control-Allow-Origin", "*")
		self.render("map.html")

class NewMapHandler(tornado.web.RequestHandler):
	def get(self):
		self.set_header("Access-Control-Allow-Origin", "*")
		self.render("maplet.html", mapbox_public_key=mapbox_public_key)

class MapBHandler(tornado.web.RequestHandler):
	def get(self):
		self.set_header("Access-Control-Allow-Origin", "*")
		self.render("mapb.html", mapbox_public_key=mapbox_public_key)

class UploadAudioHandler(tornado.web.RequestHandler):
	#this class post action receives a wav file and uploads the file to amazon s3
	def post(self):
			mp3 = self.request.files['mp3'][0] #wav post data from form

			mp3body = mp3['body'] #body of wav file
			mp3name = mp3['filename'] #wav name and path

			conn = S3Connection(aws_public_key, aws_secret_key)
			bucket = conn.get_bucket('transients-mp3') #bucket for wavs

			k = Key(bucket) #key associated with wav bucket

			filename = datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S") + ".mp3"

			k.key = filename #sets key to file name

			k.set_metadata("Content-Type", "audio/mp3") #sets metadata for audio/wav

			# k.set_contents_from_file()
			k.set_contents_from_string( mp3body )#, cb=self.mycb(), num_cb=1000)

			k.set_acl('public-read') #makes wav public

			print('uploaded')

			# return
			self.write({"success": True, "filename": filename })

	def get(self):
		self.render('uploadmp3.html')

class UploadJSONHandler(tornado.web.RequestHandler):
	def post(self):
		data_json = tornado.escape.json_decode(self.request.body)

		# collection
		coll = self.application.db.geosounds

		sound = dict()
		sound['latitude'] = data_json['latitude']
		sound['longitude'] = data_json['longitude']
		sound['sound_url_mp3'] = transients_s3_base_url + data_json['filename']
		sound['date'] = datetime.utcnow
		# sound['time'] = data_json['time']
		sound['description'] = data_json['description']
		sound['tags'] = data_json['tags']
		sound['isDrifting'] = data_json['isDrifting']
		sound['thrownLatitude'] = data_json['thrownLatitude']
		sound['thrownLongitude'] = data_json['thrownLongitude']


		# send the new sound to all connected clients
		for c in cl:
			c.write_message(json.dumps({'newSound': sound}, default=json_util.default))

		print sound

		coll.insert(sound)

	def get(self):
		self.write("Ready to upload JSON")

# websocket handler
class EchoWebSocketHandler(tornado.websocket.WebSocketHandler):
	def open(self):
		if self not in cl:
			cl.append(self)
		print("WebSocket opened")

	def on_message(self, message):
		self.write_message(json.dumps({'msg': u"You said: " + message}))

	def on_close(self):
		if self in cl:
			cl.remove(self)
		print("WebSocket closed")


if __name__ == "__main__":
        tornado.options.parse_command_line()
        http_server = tornado.httpserver.HTTPServer(Application())
        http_server.listen(options.port)
        tornado.ioloop.IOLoop.instance().start()
