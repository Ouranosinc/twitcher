import functools

from pyramid.view import view_defaults
from pyramid_rpc.xmlrpc import xmlrpc_method
from pyramid.settings import asbool

from twitcher.api import service_api_factory

import logging
logger = logging.getLogger(__name__)


# shortcut for xmlrpc_method
# api_xmlrpc = functools.partial(xmlrpc_method, endpoint="api")


@view_defaults(permission='view')
class RPCInterface(object):
    def __init__(self, request):
        self.request = request
        self.api = service_api_factory(self.request.registry)

    # token management
    # ----------------

    def generate_token(self, valid_in_hours=1, environ=None):
        return self.api.generate_token(valid_in_hours, environ)

    def revoke_token(self, token):
        return self.api.revoke_token(token)

    def revoke_all_tokens(self):
        return self.api.revoke_all_tokens()

    # service registry
    # ----------------

    def register_service(self, url, name, service_type, public, c4i, overwrite):
        return self.api.register_service(url, name, service_type, public, c4i, overwrite)

    def unregister_service(self, name):
        return self.api.unregister_service(name)

    def get_service_name(self, url):
        return self.api.get_service_name(url)

    def get_service_by_name(self, name):
        return self.api.get_service_name(name)

    def get_service_by_url(self, url):
        return self.api.get_service_by_url(url)

    def is_public(self, name):
        return self.api.is_public(name)

    def list_services(self):
        return self.api.list_services()

    def clear_services(self):
        return self.api.clear_services()


def includeme(config):
    """ The callable makes it possible to include rpcinterface
    in a Pyramid application.

    Calling ``config.include(twitcher.rpcinterface)`` will result in this
    callable being called.

    Arguments:

    * ``config``: the ``pyramid.config.Configurator`` object.
    """
    settings = config.registry.settings

    if asbool(settings.get('twitcher.rpcinterface', True)):
        logger.debug('Add twitcher rpcinterface')

        # using basic auth
        config.include('twitcher.basicauth')

        # pyramid xml-rpc
        # http://docs.pylonsproject.org/projects/pyramid-rpc/en/latest/xmlrpc.html
        config.include('pyramid_rpc.xmlrpc')
        config.include('twitcher.db')
        config.add_xmlrpc_endpoint('api', '/RPC2')

        # register xmlrpc methods
        config.add_xmlrpc_method(RPCInterface, attr='generate_token', endpoint='api', method='generate_token')
        config.add_xmlrpc_method(RPCInterface, attr='revoke_token', endpoint='api', method='revoke_token')
        config.add_xmlrpc_method(RPCInterface, attr='revoke_all_tokens', endpoint='api', method='revoke_all_tokens')
        config.add_xmlrpc_method(RPCInterface, attr='register_service', endpoint='api', method='register_service')
        config.add_xmlrpc_method(RPCInterface, attr='unregister_service', endpoint='api', method='unregister_service')
        config.add_xmlrpc_method(RPCInterface, attr='is_public', endpoint='api', method='is_public')
        config.add_xmlrpc_method(RPCInterface, attr='get_service_name', endpoint='api', method='get_service_name')
        config.add_xmlrpc_method(RPCInterface, attr='get_service_by_name', endpoint='api', method='get_service_by_name')
        config.add_xmlrpc_method(RPCInterface, attr='get_service_by_url', endpoint='api', method='get_service_by_url')
        config.add_xmlrpc_method(RPCInterface, attr='clear_services', endpoint='api', method='clear_services')
        config.add_xmlrpc_method(RPCInterface, attr='list_services', endpoint='api', method='list_services')
