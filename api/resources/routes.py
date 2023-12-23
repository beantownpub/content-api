from .healthcheck import HealthCheckAPI
from .blog import BlogPostsAPI, BlogPostAPI

def init_routes(api):
    api.add_resource(HealthCheckAPI, "/v1/content/healthz")
    api.add_resource(BlogPostsAPI, "/v1/content/blog")
    api.add_resource(BlogPostAPI, "/v1/content/blog/<slug>")
