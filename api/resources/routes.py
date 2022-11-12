from .content import NFLContent
from .healthcheck import HealthCheckAPI
from .slack import SlackAPI


def init_routes(api):
    api.add_resource(EventContactAPI, "/v1/nfl/<team>")
    api.add_resource(HealthCheckAPI, "/v1/contact/healthz")
    api.add_resource(SlackAPI, "/v1/contact/slack")
