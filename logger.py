import requests


def _log_dict(d):
    for key, elem in d.items():
        print(key, ' ', elem)


def log_response(response, method='GET', detail=True):
    if detail:
        print('[-]', method, response.url, response.status_code)
        print('[-] cookies:')
        _log_dict(requests.utils.dict_from_cookiejar(response.cookies))
        print('[-] headers:')
        _log_dict(response.headers)
        print('[-] reqest:')
        _log_dict(response.request.headers)
        print('[-] data:')
        print(response.request.body)

