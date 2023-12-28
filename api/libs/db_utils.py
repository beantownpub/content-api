import os
import sqlalchemy

from api.database.models import Post
from api.database.db import DB

from .logging import init_logger

class DBException(Exception):
    """Base class for database exceptions"""

LOG_LEVEL = os.environ.get('LOG_LEVEL')
LOG = init_logger(LOG_LEVEL)
LOG.info('Log Level %s', LOG_LEVEL)

TABLES = {
    "posts": Post
}


def get_all_items(table_name, query):
    table = TABLES.get(table_name)
    try:
        items = table.query.filter_by(**query).all()
    except sqlalchemy.exc.OperationalError:
        LOG.error('DB OperationalError')
        raise
    return items


def get_item(table_name, query):
    table = TABLES.get(table_name)
    try:
        items = table.query.filter_by(**query).first()
    except sqlalchemy.exc.OperationalError:
        LOG.error('DB OperationalError')
        raise
    return items


def get_item_by_slug(table_name, slug):
    LOG.debug('Table: %s | Slug: %s', table_name, slug)
    table = TABLES.get(table_name)
    item = table.query.filter_by(slug=slug).first()
    LOG.debug('ITEM: %s', item)
    return item


def _db_update(item, table_name, body):
    LOG.debug('DB UPDATE %s | Table: %s | Body: %s', item, table_name, body)
    item.title = body['title']
    item.author = body['author']
    item.is_active = body['is_active']
    item.summary = body['summary']
    item.slug = body['slug']
    item.body = body['body']
    DB.session.add(item)


def _db_write(table_name, body):
    LOG.debug('DB WRITE | Table: %s | Body: %s ', table_name, body)
    table = TABLES.get(table_name)
    item = table(**body)
    LOG.debug('DB WRITE | ITEM %s', item)
    DB.session.add(item)


def get_post_from_db(table_name, slug):
    table = TABLES.get(table_name)
    if not table:
        raise DBException(f"DB Table {table_name} not found")
    item = table.query.filter_by(slug=slug).first()
    return item


def run_db_action(action, item=None, body=None, table=None, location=None):
    #LOG.debug('%s | Table: %s | Item: %s | Body: %s', action, table, item, body)
    if action == "create":
        _db_write(body=body, table_name=table)
    elif action == "update":
        _db_update(item=item, table_name=table, body=body)
    elif action == "delete":
        DB.session.delete(item)
    else:
        raise DBException(f"DB action {action} not found")
    DB.session.commit()
