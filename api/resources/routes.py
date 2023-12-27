from .healthcheck import HealthCheckAPI
from .blog import BlogPostsAPI, BlogPostAPI

BLOG_POST_ROUTES = [
    "/v1/content/posts/<slug>",
    "/v1/content/posts"
]

def init_routes(api):
    api.add_resource(HealthCheckAPI, "/v1/content/healthz")
    api.add_resource(BlogPostsAPI, "/v1/content/blog")
    api.add_resource(BlogPostAPI, *BLOG_POST_ROUTES)
