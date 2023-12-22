import json
import os

from flask import Response, request
from flask_httpauth import HTTPBasicAuth
from flask_restful import Resource

from api.database.models import Post
from api.libs.db_utils import run_db_action
from api.libs.logging import init_logger
from api.libs.utils import make_uuid, make_slug, ParamArgs
from api.libs.aws import get_secret

SECRET = get_secret()
AUTH = HTTPBasicAuth()
TABLE = 'posts'

class MenuDBException(Exception):
    """Base class for menu database exceptions"""

LOG_LEVEL = os.environ.get('LOG_LEVEL')
LOG = init_logger(LOG_LEVEL)
LOG.info('blog.py logging level %s', LOG_LEVEL)


@AUTH.verify_password
def verify_password(username, password):
    api_username = SECRET["api_username"].strip()
    api_password = SECRET["api_password"].strip()
    if username.strip() == api_username and password.strip() == api_password:
        verified = True
    else:
        verified = False
    return verified


@AUTH.error_handler
def unauthorized():
    LOG.info("Unauthorized request")
    resp = {
        "status": 401,
        "response": "Unauthorized",
        "mimetype": "application/json",
    }
    return Response(**resp)


def post_to_dict(post):
    LOG.info('Convert to dict %s', post.creation_date)
    post_dict = {
        #'creation_date': post.creation_date,
        'title': post.title,
        'slug': post.slug,
        'uuid': post.uuid,
        'author': post.author,
        'body': post.body
    }
    return post_dict

def get_post(title):
    posts = Post.query.filter_by(title=title).all()
    return posts

def get_posts():
    LOG.debug('CHECK | %s | Location: %s')
    return Post.query.all()

def get_slug(args):
    slug = args.get('slug')
    return slug

class BlogAPI(Resource):
    @AUTH.login_required
    def post(self):
        body = request.json
        post = get_post(body['title'])
        LOG.debug('[POST] Post: %s', body)
        if not post:
            body['slug'] = make_slug(body['title'])
            if not body.get('uuid'):
                body['uuid'] = make_uuid()
            LOG.debug("PATH %s | Slug: %s", request.path, body['slug'])
            self.create_item(body)
            resp = {"status": 201}
        else:
            LOG.debug("[POST] 400 | Post %s already exists", post[0].slug)
            resp = {"status": 400, "response": f"post {post[0].slug} already exists"}
        return Response(**resp)

    @AUTH.login_required
    def get(self):
        args = ParamArgs(request.args)
        slug = args.slug
        LOG.info('[GET] Slug: %s | Args: %s', slug, args)
        posts = get_posts()
        posts_list = []
        if posts:
            for post in posts:
                LOG.info('postsAPI | post: %s', post)
                posts_list.append(post_to_dict(post))
        return Response(json.dumps(posts_list), mimetype='application/json', status=200)

    def create_item(self, body):
        LOG.debug('Adding %s to DB', body['slug'])
        run_db_action(action='create', body=body, table=TABLE)