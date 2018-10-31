# MongoDB
# http://docs.pylonsproject.org/projects/pyramid-cookbook/en/latest/database/mongodb.html
# maybe use event to register mongodb

import pymongo

import logging
logger = logging.getLogger(__name__)


class MongoDB:
    __db = None

    @classmethod
    def get(cls, registry):
        if not cls.__db:
            settings = registry.settings
            client = pymongo.MongoClient(settings['mongodb.host'], int(settings['mongodb.port']))
            cls.__db = client[settings['mongodb.db_name']]
        return cls.__db


def mongodb(registry):
    db = MongoDB.get(registry)
    db.services.create_index("name", unique=True)
    db.services.create_index("url", unique=True)
    return db


def includeme(config):
    factory = config.registry.settings.get('twitcher.db_factory')
    if factory == 'mongodb':
        config.registry.db = mongodb(config.registry)

        def _add_db(request):
            db = request.registry.db
            # if db_url.username and db_url.password:
            #     db.authenticate(db_url.username, db_url.password)
            return db
        config.add_request_method(_add_db, 'db', reify=True)
