import requests
class Logger:
    
    def __init__(self):
        pass
    
    def log_response(self, response, method='GET', detail=True):
        if detail:
            print( '[-]',method, response.url, response.status_code)
            print( '[-] cookies:' )
            self.__log_dict(requests.utils.dict_from_cookiejar(response.cookies))
            print( '[-] headers:' )
            self.__log_dict(response.headers)
            print( '[-] reqest:')
            self.__log_dict(response.request.headers)
            print( '[-] data:')
            print(response.request.body)


    def __log_dict(self, d):
        for key, elem in d.items():
            print (key,' ', elem)


