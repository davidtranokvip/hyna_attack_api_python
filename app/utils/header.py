from flask import request

def get_header():
    headers = dict(request.headers)
    headers.pop('Host', None)
    headers.pop('Content-Length', None)
    headers.pop('Content-Type', None)
    headers.pop('User-Agent', None)
    headers.pop('Accept', None)
    headers.pop('Accept-Encoding', None)
    headers.pop('Connection', None)
    headers.pop('Authorization', None)

    return headers