import uuid
from datetime import datetime


def add_creation_date(message_body):
  created = datetime.strftime(datetime.today(), "%m-%d-%Y %H:%M")
  message_body["created"] = created
  return message_body


def make_slug(title):
  slug = title.lower().replace(' ', '-').replace('.', '').replace('&', 'and').strip('*')
  return slug


def make_uuid():
  return str(uuid.uuid4())


class ParamArgs:
    def __init__(self, args):
      self.args = args
      self.active_only = self._convert_to_bool(args.get('active_only'))
      self.author = args.get('author')
      self.inactive_only = self._convert_to_bool(args.get('inactive_only'))
      self.title = args.get('title')
      self.slug = args.get('slug')
      self.uuid = args.get('uuid')
      self.render_markdown = self._convert_to_bool(args.get('render_markdown'))

    def __repr__(self):
      return repr(self.map)

    @property
    def map(self):
      args_dict = {
        "active_only": self.active_only,
        "author": self.author,
        "title": self.title,
        "slug": self.slug,
        "uuid": self.uuid,
        "render_markdown": self.render_markdown
      }
      return args_dict

    def _convert_to_bool(self, value):
      if not isinstance(value, bool):
        if value == 'true':
          value = True
        elif value == 'false' or not value:
          value = False
      return value
