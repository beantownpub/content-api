import json, os
from flask import Flask, request
from flask_restful import Api
from flask_cors import CORS

from api.database.db import init_database
from api.libs.logging import init_logger
from api.resources.routes import init_routes
from api.libs.aws import get_secret


class ContentAPIException(Exception):
    """Base class for content API exceptions"""

SECRET = get_secret()
ORIGINS = [
    "https://jalgraves.com",
    "http://localhost:5033",
    "http://localhost",
    "https://www.jalgraves.com",
    "https://beantown.dev.jalgraves.com",
]

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
APP = Flask(__name__.split(".")[0], instance_path="/opt/app/api")
API = Api(APP)

PSQL = {
    'user': SECRET["db_user"],
    'password': SECRET["db_pass"],
    'host': SECRET["db_host"],
    'db': SECRET["db_name"],
    'port': SECRET["db_port"]
}

for k, v in PSQL.items():
    if not v:
        msg = f"Env variable not set for database {k}"
        raise ContentAPIException(msg)

database = f"postgresql://{PSQL['user']}:{PSQL['password']}@{PSQL['host']}:{PSQL['port']}/{PSQL['db']}"

APP.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"pool_pre_ping": True}
APP.config['SQLALCHEMY_POOL_SIZE'] = 10
APP.config['SQLALCHEMY_MAX_OVERFLOW'] = 20
APP.config['SQLALCHEMY_POOL_RECYCLE'] = 1800
APP.config['SQLALCHEMY_DATABASE_URI'] = database
APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
APP.config["CORS_ALLOW_HEADERS"] = True
APP.config["CORS_EXPOSE_HEADERS"] = True

cors = CORS(
    APP, resources={r"/v1/content/*": {"origins": ORIGINS}}, supports_credentials=True
)

LOG = init_logger(LOG_LEVEL)
LOG.info("Logging initialized")
init_database(APP)
LOG.info("DB initialized")
init_routes(API)
LOG.info("Routes initialized")

def requestData(request):
    request_data = {
        "host": request.host,
        "origin": request.origin,
        "path": request.path,
        "referrer": request.referrer,
        "remote_addr": request.remote_addr,
        "http_origin": request.environ.get("HTTP_ORIGIN"),
        "http_type": "request"
    }
    return request_data


@APP.after_request
def after_request(response):
    # http_data = {
    #     "http_type": "response",
    #     "status_code": response.status_code
    # }
    request_data = requestData(request)
    if "healthz" not in request.path:
        LOG.info(json.dumps(request_data))
    origin = request.environ.get("HTTP_ORIGIN")
    #LOG.info(json.dumps(http_data))
    if origin and origin in ORIGINS:
        response.headers.add("Access-Control-Allow-Origin", origin)
    response.headers.add(
        "Access-Control-Allow-Headers", "Content-Type,Authorization,X-JAL-Comp"
    )
    response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    return response
