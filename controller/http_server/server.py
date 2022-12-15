#!/usr/bin/env python3
"""
Very simple HTTP server in python for logging requests
Usage::
    ./server.py [<port>]
"""
from http.server import BaseHTTPRequestHandler
import logging, json, traceback


class httpHandller(BaseHTTPRequestHandler):
    def init_network(self, network, cfg):
        self.network = network
        self.cfg = cfg
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        self._set_response()
        self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # to get the size of data
        post_data = self.rfile.read(content_length) # to get the data
        logging.info("post_data: {}".format(post_data))
        
        if self.path == '/api/dt/config':
            logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                    str(self.path), str(self.headers), post_data.decode('utf-8'))
                

            network_config = {}
            try:
                network_config = json.loads(post_data)
            except:
                logging.error("Reading Json file Failed {}")
                traceback.print_exc()
            self._set_response()
            self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))

            logging.info("now will call config in network")
            self.network.config_network(network_config, self.cfg)
            
        else:
            logging.info("POST request a not available path,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                    str(self.path), str(self.headers), post_data.decode('utf-8'))

