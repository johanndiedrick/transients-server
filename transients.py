import tornado.ioloop
import tornado.web
import os.path
import tornado.httpserver
import tornado.ioloop
from tornado.options import define, options
import tornado.gen
import tornado.web
import motor
from transients_globals import aws_public_key, aws_secret_key, mongodb_uri, transients_aws_base_url

from bson import json_util
import json

import boto
from boto.s3.connection import S3Connection
from boto.s3.key import Key

port = 9000

define("port", default=port, help="run on the given port", type=int)

class Application(tornado.web.Application):
        def __init__(self):
                handlers =      [

                                (r"/", MainHandler),
				(r"/geosounds", GeosoundsHandler),
				(r"/inserttest", InsertTestHandler),
				(r"/uploadaudio", UploadAudioHandler)
                                ]

                settings = dict(
                                template_path=os.path.join(os.path.dirname(__file__), "templates"),
                                static_path=os.path.join(os.path.dirname(__file__), "static"),
                                debug = True
                                )

                tornado.web.Application.__init__(self, handlers, **settings)
		print 'running on port ' + str(port)
		client = motor.MotorClient(mongodb_uri)
		self.db =  client["transients-sandbox"]


class MainHandler(tornado.web.RequestHandler):
	def get(self):
		self.write("Hello, world")

class GeosoundsHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def get(self):
		geosounds = {}
		all_geosounds = []
		cursor = self.application.db.geosounds.find({})
		while (yield cursor.fetch_next):
			geosound = cursor.next_object()
			all_geosounds.append(geosound)
		geosounds = { "geosounds" : all_geosounds }
		self.write(json.dumps(geosounds, default=json_util.default)) #write json
		self.finish

class InsertTestHandler(tornado.web.RequestHandler):
	def get(self):
		document = {"lat" : 40.5, "lng" : 70.3}
		self.application.db.geosounds.insert(document)

class UploadAudioHandler(tornado.web.RequestHandler):
	#this class post action receives a wav file and uploads the file to amazon s3
	def post(self):
			wav = self.request.files['wav'][0] #wav post data from form

			wavbody = wav['body'] #body of wav file
			wavname = wav['filename'] #wav name and path

			conn = S3Connection(aws_public_key, aws_secret_key)
			bucket = conn.get_bucket('transients-devel') #bucket for wavs

			k = Key(bucket) #key associated with wav bucket

			k.key = wavname #sets key to file name

			k.set_metadata("Content-Type", "audio/mp3") #sets metadata for audio/wav

			# k.set_contents_from_file()
			k.set_contents_from_string( wav )#, cb=self.mycb(), num_cb=1000)

			print('made it this far')
			k.set_acl('public-read') #makes wav public

			self.write("uploaded!")


	def get(self):
		self.render('uploadwav.html')


if __name__ == "__main__":
        tornado.options.parse_command_line()
        http_server = tornado.httpserver.HTTPServer(Application())
        http_server.listen(options.port)
        tornado.ioloop.IOLoop.instance().start()
