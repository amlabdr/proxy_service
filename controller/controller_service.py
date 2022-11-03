import time
from request.request import Request
class Controller:
    def __init__(self,config):
        self.cfg = config

    def controllerAuthentication(self, authentication_period:int):
        """Method to authenticate to the controller
        Args:
            authentication_periode(int) : period of refreshing the authentification Token
        return:
            Token(str)
        """
        global TOKEN
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
                TOKEN = response.json()['token']
            except:    
                print("An exception  during Authentification")
            
            time.sleep(authentication_period)

    
    def jsonSend():
        filename = 'data.json'
        # uploading JSON file to controller
        current_request = Request()
        current_request.postRequest(cfg.controller_url, filename)