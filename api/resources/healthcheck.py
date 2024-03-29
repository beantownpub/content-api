import os

from flask import Response, request
from flask_restful import Resource
from api.libs.logging import init_logger

LOG = init_logger(os.environ.get("LOG_LEVEL"))

class HealthCheckAPI(Resource):
  def get(self):
    return Response(status=200)
