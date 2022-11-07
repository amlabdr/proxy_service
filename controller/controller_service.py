import time, logging, datetime
from .request.request import Request
from .http_server.server import HTTPServer, httpHandller
from datetime import datetime
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

from network.network import Network
class Controller_service:
    def __init__(self,config):
        self.cfg = config
        self.request = Request()
        self.url = self.cfg.controller_url
        self.request.url = self.url
        self.http_server_class = HTTPServer()
        self.http_handller = httpHandller()
        self.token = ""

    

    def controllerAuthentication(self, authentication_period:int):
        """Method to authenticate to the controller
        Args:
            authentication_periode(int) : period of refreshing the authentification Token
        return:
            Token(str)
        """
        while True:
            #update TOKEN EVERY PERIODE
            current_request = Request()
            data = {
                'username': self.cfg.conf_file_contents['CONTROLLER_AUTH']['username'],
                'password': self.cfg.conf_file_contents['CONTROLLER_AUTH']['password']
            }
            url = self.cfg.controller_url + "/api/login/user"
            try:
                response = current_request.postRequestJson(url,data)
                print(response.json())
                self.token = response.json()['token']
                #self.token = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-2]
            except:    
                logging.exception("An exception  during Authentification")
            time.sleep(authentication_period)

    def post(self,filename):
        """Method to post a file to the controller
        Args:
            filename : name of the file to post
        return:
            response
        """
        net = Network()
        response = self.request.postRequest(filename = filename, token = self.token)
        logging.info("post response to {} is : {}".format(self.request.url,response))
        return response

    def run_http_server(self):
        logging.basicConfig(level=logging.INFO)
        server = self.url.split(":")[0]
        port = self.url.split(":")[1]
        server_address = (server, port)
        httpd = self.http_server_class(server_address, self.http_handller)
        logging.info('Starting http server...\n')
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        httpd.server_close()
        logging.info('Stopping httpd...\n')

    


    
    def jsonSend(self):
        filename = 'data.json'
        # uploading JSON file to controller
        current_request = Request()
        current_request.postRequest(self.cfg.controller_url, filename)