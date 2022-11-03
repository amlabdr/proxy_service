import requests

class Request:
    def __init__(self):
        pass

    def postRequest(self, url, filename):
        filedata = {'filedata': (filename, open(filename, 'rb'))}
        response = requests.post(url, files=filedata)
        return response.text
