Changes
*******

Current
=======

New Features:

* Feature #36: make protected path configurable.

0.3.7 (2018-03-13)
==================

Fixes:

* fixed exclude filter in MANIFEST.in.

New Features:

* Feature #28: use request upstream when not using wps (e.g download file through thredds).

0.3.6 (2018-03-08)
==================

* pep8
* removed unused ``c4i`` option.
* added ``auth`` option to set authentication method.
* updated docs for usage of x509 certificates.

New Features:

* Feature #25: using x509 certificates for service authentication.

0.3.5 (2018-03-01)
==================

* pep8
* updated makefile
* updated buildout recipes
* fixed nginx dependency
* updated mongodb 3.4
* configured csrf in xmlrpc
* fixed tutorial example
* added readthedocs, licence and chat badges

0.3.4 (2017-05-05)
==================

* updated logging.
* fixed: creates workdir if it does not exist.

0.3.3 (2017-04-27)
==================

* fixed fetching of access token when service is public.

0.3.2 (2017-01-31)
==================

* set header X-X509-User-Proxy.


0.3.1 (2017-01-26)
==================

* pep8.
* set permission of certfile.
* added option ows-proxy-delegate.

0.3.0 (2017-01-11)
==================

* pep8.
* changed rpc interface.
* added twitcher.client module.
* using esgf scls service to get credentials.
* updated internal pywps to version 4.0.0.
* using default port 5000.
* added ipython notebook examples.
* moved namesgenerator to top-level.
* added _compat module for python 3.x/2.x compatibility.
* added twitcher.api and cleaned up rpcinterface.
* added twitcher.store with mongodb and memory implementation.
* added twitcher.datatype with AccessToken and Service.
* using https port only.
* using OWSExceptions on errors in owsproxy.

0.2.4 (2016-12-23)
==================

* pep8.
* using replace_caps_url in owsproxy.
* pinned mongodb=2.6*|3.3.9.
* replaced service_url by proxy_url.
* added wms_130 and renamed wms_111.

0.2.3 (2016-11-18)
==================

* pep8
* using doc2dict, renamed get_service_by_name().
* added support for c4i tokens.
* updated deps: pytest, mongodb.
* updated buildout recipes.
* fixed functional tests.

0.2.2 (2016-08-18)
==================

* pep8
* don't allow dupliate service names.

0.2.1 (2016-08-05)
==================

* register service with public access.
* WMS services can be registered.

0.2.0 (2016-07-18)
==================

* updated to new buildout with seperated conda environment.
* replaced nose by pytest.
* updated installation docs.

0.1.7 (2016-06-09)
==================

Bugfixes:

* update of service failed (#17).

0.1.6 (2016-06-01)
==================

* updated docs.
* renamed python package to pyramid_twitcher.
* conda envionment.yml added.
* using get_sane_name().
* replaced httplib2 by requests.

Bugfixes:

* don't check token for allowed requests (#14).
* ignore decoding errors of response content (#13).
* fixed twitcher app config: wrong egg name.

0.1.5 (2016-04-22)
==================

* fixed docs links

0.1.4 (2016-04-19)
==================

* Fixed MANIFEST.in
* Fixed service database index.
* Updated makefile.
* Added more links to appendix.

0.1.0 (2015-12-07)
==================

Initial Release.
