import json
import urllib.request
import urllib.parse
import config_loader as config


class DataPoster:
    def __init__(self):
        pass

    def post(self, data):
        #newConditions = {"con1": 40, "con2": 20, "con3": 99, "con4": 40, "password": "1234"}
        params_json = json.dumps(data).encode('utf8')
        params = urllib.parse.urlencode({"payload": params_json}).encode('utf-8')
        req = urllib.request.Request(
            config.API_TARGET + "?push=" + config.API_KEY,
            data=params,
            #headers={'content-type': 'application/json'},
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            method='POST'
        )
        response = urllib.request.urlopen(req)
        body = response.read()
        character_set = response.headers.get_content_charset()
        response.close()
        content = body.decode(character_set)
        print(content)
