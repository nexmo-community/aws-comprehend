#!/usr/bin/env python
from __future__ import absolute_import, print_function
import wave
import datetime
import argparse
import io
import logging
import os
import sys
import time
from logging import debug, info
import uuid
import cgi
import audioop
import asyncio
import aiofile
from pprint import pprint
from threading import Thread
from threading import Timer
import threading
from queue import Queue
import time
import logging

from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent

import boto3

import requests
import tornado.ioloop
import tornado.websocket
import tornado.httpserver
import tornado.template
import tornado.web
import webrtcvad
from requests_aws4auth import AWS4Auth
from tornado.web import url
import json
from base64 import b64decode
from requests.packages.urllib3.exceptions import InsecurePlatformWarning
from requests.packages.urllib3.exceptions import SNIMissingWarning
from dotenv import load_dotenv
load_dotenv()

#-------------------------

# Environment variables (local deployment: .env file)
PORT = os.getenv("PORT") # Do not set as Config Vars for Heroku deployment
REGION = os.getenv("REGION", default = "us-east-1")
TRANSCRIBE_LANGUAGE_CODE = os.getenv("TRANSCRIBE_LANGUAGE_CODE", default = "en-US")

# Derivate sentiment language from transcribe language
SENTIMENT_LANGUAGE = TRANSCRIBE_LANGUAGE_CODE[:2]   # e.g. "en" 

#---------------------- Comprehend main ---------------------------------------

comprehend = boto3.client(service_name='comprehend', region_name=REGION)

#------------------------ Web server basic service check ----------------------        

class PingHandler(tornado.web.RequestHandler):
    async def get(self):
        self.write('ok')
        self.set_header("Content-Type", 'text/plain')
        self.finish()

#-------------------- Receive text to be sentiment analyzed ------------------       

MAX_STREAMED_SIZE = 2880000 

@tornado.web.stream_request_body
class SentimentHandler(tornado.web.RequestHandler):     

    def initialize(self):
        self.bytes_read = 0
        self.data = b''

    async def prepare(self):
        self.request.connection.set_max_body_size(MAX_STREAMED_SIZE)
        self.query_params = self.request.query_arguments

    async def data_received(self, chunck):
        self.bytes_read += len(chunck)
        self.data += chunck

    async def post(self):
        self.write('ok')
        self.set_header("Content-Type", 'text/plain')
        self.finish()

        # Retrieve all query paramaters
        for k,v in self.query_params.items():
            self.query_params[k] = v[0].decode("utf-8")

        self.payload = str(json.dumps(self.query_params))

        self.webhook_url = self.get_argument("webhook_url")
        self.language = self.get_argument("language")

        self.rec_json = self.data.decode('utf-8')
        # print('self.rec_json:', self.rec_json) 

        self.values = json.loads(self.rec_json)
        self.text = self.values["text"]
        print('text:', self.text)

        #-----------------

        if self.text != '' :
            self.sentiment = comprehend.detect_sentiment(Text=self.text, LanguageCode=self.language)

        print("sentiment:", json.dumps(self.sentiment))

        #------------------

        self.payload = '{"sentiment": ' + json.dumps(self.sentiment) + ', "text": "' + self.text + '", ' + self.payload[1:]

        self.payload =  self.payload[:-1] + ', "service": "AWS Comprehend"}'

        info('payload')
        info(self.payload)

        # Posting results back via webhook
        if (self.webhook_url):
            a = requests.post(self.webhook_url, data=self.payload, headers={'Content-Type': 'application/json'})

#------------------------- Main thread -----------------------------------------        

def main(argv=sys.argv[1:]):
    try:
        ap = argparse.ArgumentParser()
        ap.add_argument("-v", "--verbose", action="count")
        args = ap.parse_args(argv)
        logging.basicConfig(
            level=logging.DEBUG if args.verbose != None else logging.INFO,
            format="%(levelname)7s %(message)s",
        )
        print("Logging level is {}".format(logging.getLevelName(logging.getLogger().level)))
        application = tornado.web.Application([
            url(r"/ping", PingHandler),
            url(r"/sentiment", SentimentHandler)
        ])
        http_server = tornado.httpserver.HTTPServer(application)
        http_server.listen(PORT)
        info("Running on port %s", PORT)
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        pass  # Suppress the stack-trace on quit

#----------------------- Start main thread --------------------------------------        

if __name__ == "__main__":
    main()
