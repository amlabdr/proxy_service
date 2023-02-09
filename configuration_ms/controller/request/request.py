import requests

class Request:
    def __init__(self):
        self.url = ""
        self.filename = ""

    def postRequest(self, filename,token=""):
        filedata = {'filedata': (filename, open(filename, 'rb'))}
        hed = {'Authorization': 'Bearer ' + token}
        response = requests.post(self.url, files=filedata,headers=hed)
        return response.text

    def postRequestJson(self,url,data):
        response = requests.post(url, json=data)
        return response