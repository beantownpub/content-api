import json
import os

from datetime import datetime
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

class BlogException(Exception):
  """Base class for blog exceptions"""


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
  post_dict = {
    "creation_date": datetime.strftime(post.creation_date, "%Y-%m-%d"),
    "id": post.id,
    "is_active": post.is_active,
    "title": post.title,
    "slug": post.slug,
    "summary": post.summary,
    "uuid": post.uuid,
    "author": post.author,
    "body": post.body,
    "tags": post.tags
  }
  return post_dict


def get_post_by_title(title):
  posts = Post.query.filter_by(title=title).all()
  return posts


def get_post_by_slug(slug):
  post = Post.query.filter_by(slug=slug).first()
  return post


def get_all_posts():
  LOG.info("Getting all posts")
  return Post.query.all()


def get_slug(args):
  slug = args.get('slug')
  return slug

class BlogPostAPI(Resource):
  @AUTH.login_required
  def post(self, slug=None):
    body = request.json
    LOG.info('Creating post: %s', body["title"])
    post = get_post_by_title(body["title"])
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
  def get(self, slug):
      post = get_post_by_slug(slug)
      posts_list = []
      if post:
        posts_list.append(post_to_dict(post))
      return Response(json.dumps(posts_list), mimetype='application/json', status=200)

  @AUTH.login_required
  def delete(self, slug):
      LOG.info("[DELETE] %s", slug)
      post = get_post_by_slug(slug)
      if not post:
          LOG.info('404 DELETE Item Post %s not found', slug)
          resp = {"status": 404, "response": "Post not found"}
      else:
          run_db_action(action='delete', item=post)
          resp = {"status": 204, "response": "Post deleted"}
      return Response(**resp)

  def create_item(self, body):
      LOG.debug('Adding %s to DB', body['slug'])
      run_db_action(action='create', body=body, table=TABLE)


class BlogPostsAPI(Resource):
  @AUTH.login_required
  def get(self):
    LOG.info("WTF")
    args = ParamArgs(request.args)
    posts = get_all_posts()
    posts_list = []
    if posts:
      if args.active_only:
        for post in posts:
          if post.is_active:
            posts_list.append(post_to_dict(post))
      else:
        for post in posts:
          posts_list.append(post_to_dict(post))
    return Response(json.dumps(posts_list), mimetype='application/json', status=200)
