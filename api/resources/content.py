import json
import os

from flask import Response, request
from flask_httpauth import HTTPBasicAuth
from flask_restful import Resource
from api.libs.sports.nfl import NFLScrape
from api.libs.logging import init_logger

AUTH = HTTPBasicAuth()
LOG = init_logger(os.environ.get("LOG_LEVEL"))


class ContentException(Exception):
    """Base  class for order content exceptions"""


@AUTH.verify_password
def verify_password(username, password):
    api_username = os.environ.get("API_USERNAME")
    api_password = os.environ.get("API_PASSWORD")
    if username.strip() == api_username and password.strip() == api_password:
        verified = True
    else:
        verified = False
    return verified


class NFLContent(Resource):

    @AUTH.login_required
    def get(self, team):
        team_info = NFLScrape(team)
        return Response(json.dumps(team_info.stats), mimetype="application/json", status=200)

    def options(self, location):
        LOG.info("ContactAPI | OPTIONS | %s", location)
        return "", 200
