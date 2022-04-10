from werkzeug.exceptions import HTTPException
from flask import make_response
import json

class BussinessValidationError(HTTPException):
    def __init__(self, status_code,error_code, error_message):
        message = {"error_code":error_code,"error_message":error_message}
        self.response = make_response(json.dumps(message),status_code)

class FourZeroNineError(HTTPException):
    def __init__(self):
        self.response = make_response('',409)

class AllOkError(HTTPException):
    def __init__(self):
        self.response = make_response('',200)

class NotFoundError(HTTPException):
    def __init__(self):
        self.response = make_response('',404)