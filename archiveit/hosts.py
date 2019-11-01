import requests
from requests.exceptions import RequestException

class Host():
    def __init__(self):
        pass

    def upload(self, file: bytes):
        '''
        Uploads data to the hosting provider, returns a URL.
        :param file: The data to send, as bytes.
        :return: A string, the URL.
        '''
        raise NotImplementedError()

class ZeroXZero(Host):
    def __init__(self):
        super(ZeroXZero).__init__()

    def upload(self, file):
        data = {'file': file}
        try:
            r = requests.post("https://0x0.st", files=data)
        except RequestException:
            pass
        if str(r) != "<Response [200]>":
            pass

        return r.text

hosts = {"0x0": ZeroXZero}
