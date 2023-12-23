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
        self.inactive_only = args.get('inactive_only')
        self.is_active = args.get('is_active')
        self.title = args.get('title')
        self.slug = args.get('slug')
        self.status = self.get_status()
        self.uuid = args.get('uuid')

    def __repr__(self):
        return repr(self.map)

    @property
    def map(self):
        args_dict = {
            "active_only": self.active_only,
            "author": self.author,
            "title": self.title,
            "is_active": self.is_active,
            "slug": self.slug,
            "status": self.status,
            "uuid": self.uuid
        }
        return args_dict

    def get_status(self):
        if not self.args.get('status'):
            status = self._convert_to_bool(self.is_active)
        else:
            status = self.args.get('status')
        return status

    def _convert_to_bool(self, value):
        if not isinstance(value, bool):
            if value == 'true':
                value = True
            elif value == 'false':
                value = False
        return value