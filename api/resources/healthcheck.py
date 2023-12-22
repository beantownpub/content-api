import json, os

from flask import Response, request
from flask_restful import Resource
from api.libs.logging import init_logger

LOG = init_logger(os.environ.get("LOG_LEVEL"))


def requestData(request):
    request_data = {
        "host": request.host,
        "origin": request.origin,
        "path": request.path,
        "referrer": request.referrer,
        "remote_addr": request.remote_addr
    }
    return request_data

class HealthCheckAPI(Resource):
    def get(self):
        #LOG.info(json.dumps(requestData(request)))
        return Response(status=200)
