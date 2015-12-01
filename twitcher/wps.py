"""
pywps wrapper
"""
import os

from pyramid.httpexceptions import HTTPBadRequest
from pyramid.settings import asbool

import pywps
from pywps.Exceptions import WPSException
from twitcher.owsexceptions import OWSNoApplicableCode

import logging
logger = logging.getLogger(__name__)

wps_environ_keys = ['PYWPS_CFG', 'PYWPS_PROCESSES', 'PYWPS_TEMPLATES']

def pywps_view(request):
    """
    * TODO: add xml response renderer
    * TODO: fix exceptions ... use OWSException (raise ...)
    * TODO: config of pywps is missing
    """
    response = request.response
    response.status = "200 OK"
    response.content_type = "text/xml"

    inputQuery = None
    if request.method == "GET":
        inputQuery = request.query_string
    elif request.method == "POST":
        inputQuery = request.body_file_raw
    else:
        return HTTPBadRequest()

    if not inputQuery:
        return OWSNoApplicableCode("No query string found.")

    # set the environ for wps from request environ
    for key in wps_environ_keys:
        if key in request.environ:
            os.environ[key] = request.environ[key]

    # create the WPS object
    try:
        wps = pywps.Pywps(request.method)
        if wps.parseRequest(inputQuery):
            pywps.debug(wps.inputs)
            return wps.performRequest()
    except WPSException,e:
        return e
    except Exception, e:
        return OWSNoApplicableCode(e.message)

def includeme(config):
    settings = config.registry.settings

    if asbool(settings.get('twitcher.wps', True)):
        logger.info('Add twitcher wps application')
        config.add_route('wps', '/ows/wps')
        config.add_route('wps_secured', '/ows/wps/{access_token}')
        config.add_view(pywps_view, route_name='wps', renderer='string')
        config.add_view(pywps_view, route_name='wps_secured', renderer='string')



