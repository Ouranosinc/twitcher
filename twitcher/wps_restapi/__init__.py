from pyramid.settings import asbool
from twitcher.wps_restapi.frontpage import frontpage
from twitcher.wps_restapi import swagger_definitions as sd
from pyramid.httpexceptions import *
from twitcher.wps_restapi.api import api_swagger_json, api_swagger_ui, api_versions
from twitcher.db import MongoDB
import logging
from twitcher.owsexceptions import *
from twitcher.exceptions import ServiceNotFound
logger = logging.getLogger(__name__)


def includeme(config):
    settings = config.registry.settings

    if asbool(settings.get('twitcher.wps_restapi', True)):
        logger.info('Adding WPS REST API ...')
        config.include('cornice')
        config.include('cornice_swagger')
        config.include('twitcher.wps_restapi.providers')
        config.include('twitcher.wps_restapi.processes')
        config.include('twitcher.wps_restapi.jobs')
        config.include('pyramid_mako')
        config.add_route(**sd.service_api_route_info(sd.api_frontpage_service, settings))
        config.add_route(**sd.service_api_route_info(sd.api_swagger_json_service, settings))
        config.add_route(**sd.service_api_route_info(sd.api_swagger_ui_service, settings))
        config.add_route(**sd.service_api_route_info(sd.api_versions_service, settings))
        config.add_view(frontpage, route_name=sd.api_frontpage_service.name,
                        request_method='GET', renderer='json')
        config.add_view(api_swagger_json, route_name=sd.api_swagger_json_service.name,
                        request_method='GET', renderer='json')
        config.add_view(api_swagger_ui, route_name=sd.api_swagger_ui_service.name,
                        request_method='GET', renderer='templates/swagger_ui.mako')
        config.add_view(api_versions, route_name=sd.api_versions_service.name,
                        request_method='GET', renderer='json')
        config.registry.celerydb = MongoDB.get(config.registry)
