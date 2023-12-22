from .healthcheck import HealthCheckAPI
from .blog import BlogAPI

def init_routes(api):
    api.add_resource(HealthCheckAPI, "/v1/content/healthz")
    api.add_resource(BlogAPI, "/v1/content/blog")
